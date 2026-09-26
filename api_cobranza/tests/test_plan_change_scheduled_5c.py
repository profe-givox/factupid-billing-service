"""Tests del ajuste UI 5C: notificación de downgrade programado.

Cubre:
  I1. El downgrade crea schedule, guarda stripe_schedule_id y notifica
      subscription_plan_change_scheduled con plan destino y fecha efectiva.
  I2. El payload incluye billing_code actual, subscription_id y plan_id actual.
  I3. Si no se resuelve billing_code no se notifica (no rompe el flujo).
  I4. Webhook downgrade aplicado: libera el schedule, limpia local y notifica
      subscription_plan_changed con el billing_code del nuevo plan.
  I5. Webhook con cambio aún no aplicado: mantiene plan y schedule, no notifica
      plan_changed.
"""

from unittest.mock import patch, MagicMock
from datetime import datetime, timezone, date

import pytest
from sqlmodel import Session

from tests.conftest import test_engine
from app.models.plan import Plan
from app.models.subscription import Subscription
from app.routers.webhooks import handle_subscription_updated

CHANGE_PLAN_URL = "/api/pagos/subscriptions/change-plan"


def _seed_two_plans():
    """Crea planes ENTERPRISE (actual) y PRO (destino) con suscripción activa."""
    with Session(test_engine) as db:
        pro = Plan(
            code="CFDI_PRO", name="PRO", price=50, currency="MXN",
            interval="month", billing_type="subscription",
            stripe_price_id="price_pro_test", stripe_product_id="prod_pro_test",
            is_active=True,
        )
        ent = Plan(
            code="CFDI_ENTERPRISE", name="ENTERPRISE", price=500, currency="MXN",
            interval="month", billing_type="subscription",
            stripe_price_id="price_ent_test", stripe_product_id="prod_ent_test",
            is_active=True,
        )
        db.add(pro)
        db.add(ent)
        db.commit()
        db.refresh(pro)
        db.refresh(ent)

        sub = Subscription(
            user_id=1, plan_id=ent.id, status="active", provider="stripe",
            stripe_subscription_id="sub_stripe_1",
            stripe_schedule_id=None, cancel_at_period_end=False,
            end_date=date(2026, 9, 1),
        )
        db.add(sub)
        db.commit()
        db.refresh(sub)
        return {"sub_id": sub.id, "pro_id": pro.id, "ent_id": ent.id}


class TestChangePlanDowngradeNotificaScheduled:
    """I1-I3: change_plan (downgrade) notifica el cambio programado."""

    def _stripe_sub_dict(self, current_period_end):
        return {
            "id": "sub_stripe_1",
            "status": "active",
            "items": {
                "data": [{
                    "id": "si_1",
                    "current_period_start": 1767225600,
                    "current_period_end": current_period_end,
                }],
            },
        }

    def _downgrade(self, client, auth_headers, current_period_end=None):
        if current_period_end is None:
            current_period_end = int(
                datetime(2026, 9, 1, tzinfo=timezone.utc).timestamp()
            )
        schedule = MagicMock()
        schedule.configure_mock(id="sub_sched_1")

        with patch("app.routers.subscriptions.engine", test_engine), \
                patch("stripe.Subscription.retrieve") as mock_retrieve, \
                patch("stripe.SubscriptionSchedule.create") as mock_create, \
                patch("stripe.SubscriptionSchedule.modify") as mock_modify, \
                patch("app.routers.subscriptions.notify_subscription_event") as mock_notify:
            mock_retrieve.return_value = self._stripe_sub_dict(current_period_end)
            mock_create.return_value = schedule

            response = self._call(client, auth_headers)
            return response, mock_notify

    def _call(self, client, auth_headers):
        return client.post(
            CHANGE_PLAN_URL,
            params={"user_id": 1, "new_plan_code": "CFDI_PRO"},
            headers=auth_headers,
        )

    def test_downgrade_guarda_schedule_y_notifica_destino(self, client, auth_headers):
        ids = _seed_two_plans()
        current_period_end = int(datetime(2026, 9, 1, tzinfo=timezone.utc).timestamp())

        response, mock_notify = self._downgrade(client, auth_headers, current_period_end)

        assert response.status_code == 200
        body = response.json()
        assert body["type"] == "downgrade"
        assert body["effective_date"] == current_period_end

        # Schedule guardado localmente; el plan actual NO cambia todavía
        with Session(test_engine) as db:
            sub = db.get(Subscription, ids["sub_id"])
            assert sub.stripe_schedule_id == "sub_sched_1"
            assert sub.plan_id == ids["ent_id"]

        mock_notify.assert_called_once()
        kwargs = mock_notify.call_args[1]
        assert kwargs["event_type"] == "subscription_plan_change_scheduled"

        payload = kwargs["full_payload"]
        assert payload["scheduled_billing_code"] == "CFDI_PRO"
        assert payload["scheduled_plan_id"] == ids["pro_id"]
        assert payload["effective_date"] == "2026-09-01"
        assert payload["change_type"] == "downgrade"

    def test_payload_incluye_suscripcion_y_plan_actual(self, client, auth_headers):
        ids = _seed_two_plans()

        response, mock_notify = self._downgrade(client, auth_headers)

        assert response.status_code == 200
        kwargs = mock_notify.call_args[1]
        assert kwargs["billing_code"] == "CFDI_ENTERPRISE"
        assert kwargs["subscription_id"] == ids["sub_id"]
        assert kwargs["plan_id"] == ids["ent_id"]
        assert kwargs["user_id"] == 1
        assert kwargs["stripe_subscription_id"] == "sub_stripe_1"

    def test_sin_billing_code_no_notifica_pero_no_falla(self, client, auth_headers):
        ids = _seed_two_plans()
        # Plan sin code: no se resuelve billing_code
        with Session(test_engine) as db:
            sin_code = Plan(
                code="", name="SIN_CODE", price=500, currency="MXN",
                interval="month", billing_type="subscription",
                stripe_price_id="price_sin_code", stripe_product_id="prod_sin_code",
                is_active=True,
            )
            db.add(sin_code)
            db.commit()
            db.refresh(sin_code)

            sub = db.get(Subscription, ids["sub_id"])
            sub.plan_id = sin_code.id
            db.add(sub)
            db.commit()

        response, mock_notify = self._downgrade(client, auth_headers)

        assert response.status_code == 200
        assert response.json()["type"] == "downgrade"
        mock_notify.assert_not_called()


class TestWebhookDowngradeAplicado:
    """I4-I5: customer.subscription.updated con schedule (CASO 2)."""

    @pytest.fixture(autouse=True)
    def _patch_engine(self):
        with patch("app.routers.webhooks.engine", test_engine):
            yield

    def _update_data(self, price_id="price_ent_test", status="active"):
        return {
            "id": "sub_stripe_1",
            "status": status,
            "customer": "cus_123",
            "cancel_at_period_end": False,
            "items": {"data": [{"price": {"id": price_id}}]},
        }

    def test_downgrade_aplicado_libera_y_notifica_plan_changed(self):
        ids = _seed_two_plans()
        with Session(test_engine) as db:
            sub = db.get(Subscription, ids["sub_id"])
            sub.stripe_schedule_id = "sub_sched_1"
            db.add(sub)
            db.commit()

        with patch("app.routers.webhooks.notify_subscription_event") as mock_notify, \
                patch("app.routers.webhooks.release_stripe_schedule_if_possible") as mock_release:
            mock_release.return_value = (True, "released", None)
            handle_subscription_updated(self._update_data(price_id="price_pro_test"))

        with Session(test_engine) as db:
            sub = db.get(Subscription, ids["sub_id"])
            assert sub.plan_id == ids["pro_id"]
            assert sub.stripe_schedule_id is None
            assert sub.status == "active"

        mock_release.assert_called_once_with(stripe_schedule_id="sub_sched_1")
        mock_notify.assert_called_once()
        kwargs = mock_notify.call_args[1]
        assert kwargs["event_type"] == "subscription_plan_changed"
        assert kwargs["billing_code"] == "CFDI_PRO"
        assert kwargs["plan_id"] == ids["pro_id"]

    def test_cambio_no_aplicado_mantiene_plan_y_schedule(self):
        ids = _seed_two_plans()
        with Session(test_engine) as db:
            sub = db.get(Subscription, ids["sub_id"])
            sub.stripe_schedule_id = "sub_sched_1"
            db.add(sub)
            db.commit()

        # Stripe sigue reportando el plan ENTERPRISE (fase actual del schedule)
        with patch("app.routers.webhooks.notify_subscription_event") as mock_notify:
            handle_subscription_updated(self._update_data(price_id="price_ent_test"))

        with Session(test_engine) as db:
            sub = db.get(Subscription, ids["sub_id"])
            assert sub.plan_id == ids["ent_id"]
            assert sub.stripe_schedule_id == "sub_sched_1"

        mock_notify.assert_not_called()
