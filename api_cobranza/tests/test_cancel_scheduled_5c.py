"""Tests para la fase UI 5C: revertir cancelación programada y manejo de
SubscriptionSchedule de downgrade.

Cubre:
- POST /subscriptions/reactivate-cancel-scheduled
- POST /subscriptions/cancel-scheduled-plan-change
- fix en POST /payments/subscriptions/{id}/cancel con schedule pendiente
"""

from unittest.mock import patch, MagicMock
from datetime import datetime, timezone, date

import pytest
from sqlmodel import Session

from tests.conftest import test_engine
from app.models.plan import Plan
from app.models.subscription import Subscription
from app.core.security import get_current_user
from app.schemas.user import CurrentUser

REACTIVATE_URL = "/api/pagos/subscriptions/reactivate-cancel-scheduled"
CANCEL_PLAN_URL = "/api/pagos/subscriptions/cancel-scheduled-plan-change"
CANCEL_URL = "/api/pagos/payments/subscriptions"


def _seed_subscription(
    status="cancel_scheduled",
    user_id=1,
    cancel_at_period_end=True,
    stripe_schedule_id=None,
    stripe_subscription_id="sub_stripe_1",
    canceled_at=None,
):
    """Crea un plan PRO y una suscripción en la BD de test."""
    with Session(test_engine) as db:
        plan = Plan(
            code="CFDI_PRO", name="PRO", price=50, currency="MXN",
            interval="month", billing_type="subscription",
            stripe_price_id="price_pro_test", stripe_product_id="prod_pro_test",
            is_active=True,
        )
        db.add(plan)
        db.commit()
        db.refresh(plan)

        sub = Subscription(
            user_id=user_id,
            plan_id=plan.id,
            status=status,
            provider="stripe",
            stripe_subscription_id=stripe_subscription_id,
            stripe_schedule_id=stripe_schedule_id,
            cancel_at_period_end=cancel_at_period_end,
            canceled_at=canceled_at,
            end_date=date(2026, 9, 1),
        )
        db.add(sub)
        db.commit()
        db.refresh(sub)
        return sub.id


def _seed_plan_only():
    with Session(test_engine) as db:
        plan = Plan(
            code="CFDI_PRO", name="PRO", price=50, currency="MXN",
            interval="month", billing_type="subscription",
            stripe_price_id="price_pro_test", stripe_product_id="prod_pro_test",
            is_active=True,
        )
        db.add(plan)
        db.commit()
        db.refresh(plan)
        return plan


def _patch_engine():
    return patch("app.routers.subscriptions.engine", test_engine)


class TestReactivateCancelScheduled:
    """POST /subscriptions/reactivate-cancel-scheduled."""

    def _post(self, client, subscription_id):
        return client.post(
            REACTIVATE_URL,
            json={"subscription_id": subscription_id},
        )

    def test_revierte_cancelacion_programada(self, client, auth_headers):
        sub_id = _seed_subscription(
            status="cancel_scheduled", cancel_at_period_end=True,
            canceled_at=datetime(2026, 8, 1, tzinfo=timezone.utc),
        )

        with _patch_engine(), \
                patch("stripe.Subscription.modify") as mock_modify, \
                patch("app.routers.subscriptions.notify_subscription_event") as mock_notify:
            response = self._post(client, sub_id)

        assert response.status_code == 200
        body = response.json()
        assert body["subscription_status"] == "active"
        assert body["cancel_at_period_end"] is False

        mock_modify.assert_called_once_with(
            "sub_stripe_1", cancel_at_period_end=False,
        )

        # BD local actualizada: activa, sin cancelación programada, sin fecha de cancelación
        with Session(test_engine) as db:
            sub = db.get(Subscription, sub_id)
            assert sub.status == "active"
            assert sub.cancel_at_period_end is False
            assert sub.canceled_at is None

        # Notifica a Django subscription_reactivated
        mock_notify.assert_called_once()
        kwargs = mock_notify.call_args[1]
        assert kwargs["event_type"] == "subscription_reactivated"
        assert kwargs["cancel_at_period_end"] is False

    def test_revierte_con_cancel_at_period_end_solo(self, client, auth_headers):
        # Status activo pero con cancel_at_period_end=True es suficiente
        sub_id = _seed_subscription(
            status="active", cancel_at_period_end=True,
        )

        with _patch_engine(), \
                patch("stripe.Subscription.modify"), \
                patch("app.routers.subscriptions.notify_subscription_event"):
            response = self._post(client, sub_id)

        assert response.status_code == 200

    def test_sin_cancelacion_programada_rechaza(self, client, auth_headers):
        sub_id = _seed_subscription(
            status="active", cancel_at_period_end=False,
        )

        with _patch_engine(), \
                patch("stripe.Subscription.modify") as mock_modify, \
                patch("app.routers.subscriptions.notify_subscription_event") as mock_notify:
            response = self._post(client, sub_id)

        assert response.status_code == 400
        assert response.json()["detail"]["code"] == "NO_CANCEL_SCHEDULED"
        mock_modify.assert_not_called()
        mock_notify.assert_not_called()

    def test_subscription_no_encontrada(self, client, auth_headers):
        with _patch_engine():
            response = self._post(client, 999999)

        assert response.status_code == 404

    def test_sin_stripe_subscription_id_rechaza(self, client, auth_headers):
        sub_id = _seed_subscription(
            status="cancel_scheduled", stripe_subscription_id=None,
        )

        with _patch_engine(), \
                patch("stripe.Subscription.modify") as mock_modify, \
                patch("app.routers.subscriptions.notify_subscription_event") as mock_notify:
            response = self._post(client, sub_id)

        assert response.status_code == 400
        mock_modify.assert_not_called()
        mock_notify.assert_not_called()

    def test_error_stripe_devuelve_502(self, client, auth_headers):
        import stripe as stripe_lib

        sub_id = _seed_subscription(status="cancel_scheduled")

        with _patch_engine(), \
                patch("stripe.Subscription.modify") as mock_modify, \
                patch("app.routers.subscriptions.notify_subscription_event") as mock_notify:
            mock_modify.side_effect = stripe_lib.error.StripeError("boom")
            response = self._post(client, sub_id)

        assert response.status_code == 502
        # No modifica la BD local si Stripe falló
        with Session(test_engine) as db:
            sub = db.get(Subscription, sub_id)
            assert sub.status == "cancel_scheduled"
            assert sub.cancel_at_period_end is True
        mock_notify.assert_not_called()

    def test_sin_permiso_rechaza(self, client, auth_headers):
        sub_id = _seed_subscription(status="cancel_scheduled")

        def mock_user_sin_permisos():
            return CurrentUser(
                sub="test-user-1", user_id=1, username="testuser",
                email="test@factupid.com", is_staff=False, is_superuser=False,
                groups=[], perms=[], tenant=1, token_type="access",
                aud="billing-api", iss="https://app.factupid.com",
            )

        from app.main import app as fastapi_app

        fastapi_app.dependency_overrides[get_current_user] = mock_user_sin_permisos
        try:
            with _patch_engine(), \
                    patch("stripe.Subscription.modify") as mock_modify:
                response = self._post(client, sub_id)

            assert response.status_code == 403
            mock_modify.assert_not_called()
        finally:
            fastapi_app.dependency_overrides.pop(get_current_user, None)


class TestCancelScheduledPlanChange:
    """POST /subscriptions/cancel-scheduled-plan-change."""

    def _post(self, client, subscription_id):
        return client.post(
            CANCEL_PLAN_URL,
            json={"subscription_id": subscription_id},
        )

    def _mock_schedule(self, status="active"):
        schedule = MagicMock()
        schedule.configure_mock(**{
            "get.side_effect": lambda key, default=None: {
                "id": "sub_sched_1",
                "status": status,
            }.get(key, default)
        })
        return schedule

    def test_schedule_activo_se_libera(self, client, auth_headers):
        sub_id = _seed_subscription(
            status="active", cancel_at_period_end=False,
            stripe_schedule_id="sub_sched_1",
        )

        with _patch_engine(), \
                patch("stripe.SubscriptionSchedule.retrieve") as mock_retrieve, \
                patch("stripe.SubscriptionSchedule.release") as mock_release, \
                patch("app.routers.subscriptions.notify_subscription_event") as mock_notify:
            mock_retrieve.return_value = self._mock_schedule(status="active")

            response = self._post(client, sub_id)

        assert response.status_code == 200
        body = response.json()
        assert body["released"] is True
        assert body["stripe_schedule_id"] is None

        mock_retrieve.assert_called_once_with("sub_sched_1")
        mock_release.assert_called_once_with("sub_sched_1")

        # Se limpia el schedule local y se mantiene activa
        with Session(test_engine) as db:
            sub = db.get(Subscription, sub_id)
            assert sub.stripe_schedule_id is None
            assert sub.status == "active"

        mock_notify.assert_called_once()
        assert mock_notify.call_args[1]["event_type"] == "subscription_plan_change_canceled"

    def test_schedule_not_started_se_libera(self, client, auth_headers):
        sub_id = _seed_subscription(
            status="active", cancel_at_period_end=False,
            stripe_schedule_id="sub_sched_1",
        )

        with _patch_engine(), \
                patch("stripe.SubscriptionSchedule.retrieve") as mock_retrieve, \
                patch("stripe.SubscriptionSchedule.release") as mock_release, \
                patch("app.routers.subscriptions.notify_subscription_event") as mock_notify:
            mock_retrieve.return_value = self._mock_schedule(status="not_started")

            response = self._post(client, sub_id)

        assert response.status_code == 200
        assert response.json()["released"] is True
        mock_release.assert_called_once_with("sub_sched_1")

    def test_schedule_ya_released_no_falla(self, client, auth_headers):
        sub_id = _seed_subscription(
            status="active", cancel_at_period_end=False,
            stripe_schedule_id="sub_sched_1",
        )

        with _patch_engine(), \
                patch("stripe.SubscriptionSchedule.retrieve") as mock_retrieve, \
                patch("stripe.SubscriptionSchedule.release") as mock_release, \
                patch("app.routers.subscriptions.notify_subscription_event") as mock_notify:
            mock_retrieve.return_value = self._mock_schedule(status="released")

            response = self._post(client, sub_id)

        assert response.status_code == 200
        assert response.json()["released"] is False
        # No se llama release sobre un schedule ya terminal
        mock_release.assert_not_called()

        # Igualmente se limpia el ID local
        with Session(test_engine) as db:
            sub = db.get(Subscription, sub_id)
            assert sub.stripe_schedule_id is None

    def test_schedule_completado_no_falla(self, client, auth_headers):
        sub_id = _seed_subscription(
            status="active", cancel_at_period_end=False,
            stripe_schedule_id="sub_sched_1",
        )

        with _patch_engine(), \
                patch("stripe.SubscriptionSchedule.retrieve") as mock_retrieve, \
                patch("stripe.SubscriptionSchedule.release") as mock_release, \
                patch("app.routers.subscriptions.notify_subscription_event"):
            mock_retrieve.return_value = self._mock_schedule(status="completed")

            response = self._post(client, sub_id)

        assert response.status_code == 200
        mock_release.assert_not_called()

    def test_sin_schedule_rechaza(self, client, auth_headers):
        sub_id = _seed_subscription(
            status="active", cancel_at_period_end=False,
            stripe_schedule_id=None,
        )

        with _patch_engine(), \
                patch("stripe.SubscriptionSchedule.retrieve") as mock_retrieve, \
                patch("stripe.SubscriptionSchedule.release") as mock_release, \
                patch("app.routers.subscriptions.notify_subscription_event") as mock_notify:
            response = self._post(client, sub_id)

        assert response.status_code == 400
        assert response.json()["detail"]["code"] == "NO_SCHEDULED_PLAN_CHANGE"
        mock_retrieve.assert_not_called()
        mock_release.assert_not_called()
        mock_notify.assert_not_called()

    def test_subscription_no_encontrada(self, client, auth_headers):
        with _patch_engine():
            response = self._post(client, 999999)

        assert response.status_code == 404

    def test_error_stripe_no_limpia_local(self, client, auth_headers):
        import stripe as stripe_lib

        sub_id = _seed_subscription(
            status="active", cancel_at_period_end=False,
            stripe_schedule_id="sub_sched_1",
        )

        with _patch_engine(), \
                patch("stripe.SubscriptionSchedule.retrieve") as mock_retrieve, \
                patch("stripe.SubscriptionSchedule.release") as mock_release, \
                patch("app.routers.subscriptions.notify_subscription_event") as mock_notify:
            mock_retrieve.side_effect = stripe_lib.error.StripeError("boom")
            response = self._post(client, sub_id)

        assert response.status_code == 502
        mock_release.assert_not_called()
        mock_notify.assert_not_called()

        # No se toca el schedule local si Stripe falló
        with Session(test_engine) as db:
            sub = db.get(Subscription, sub_id)
            assert sub.stripe_schedule_id == "sub_sched_1"

    def test_release_falla_no_limpia_local(self, client, auth_headers):
        import stripe as stripe_lib

        sub_id = _seed_subscription(
            status="active", cancel_at_period_end=False,
            stripe_schedule_id="sub_sched_1",
        )

        with _patch_engine(), \
                patch("stripe.SubscriptionSchedule.retrieve") as mock_retrieve, \
                patch("stripe.SubscriptionSchedule.release") as mock_release, \
                patch("app.routers.subscriptions.notify_subscription_event") as mock_notify:
            mock_retrieve.return_value = self._mock_schedule(status="active")
            mock_release.side_effect = stripe_lib.error.StripeError("boom")
            response = self._post(client, sub_id)

        assert response.status_code == 502
        mock_notify.assert_not_called()

        with Session(test_engine) as db:
            sub = db.get(Subscription, sub_id)
            assert sub.stripe_schedule_id == "sub_sched_1"


class TestCancelConSchedulePendiente:
    """Fix Parte C: cancelar libera el schedule antes para no bloquear."""

    def _post(self, client, sub_id):
        return client.post(
            f"{CANCEL_URL}/{sub_id}/cancel",
            json={"at_period_end": True},
        )

    def test_cancel_libera_schedule_local_antes(self, client, auth_headers):
        sub_id = _seed_subscription(
            status="active", cancel_at_period_end=False,
            stripe_schedule_id="sub_sched_1",
        )

        with patch("stripe.SubscriptionSchedule.retrieve") as mock_retrieve, \
                patch("stripe.SubscriptionSchedule.release") as mock_release, \
                patch("stripe.Subscription.modify") as mock_modify:
            schedule = MagicMock()
            schedule.configure_mock(**{
                "get.side_effect": lambda key, default=None: {
                    "id": "sub_sched_1", "status": "active",
                }.get(key, default)
            })
            mock_retrieve.return_value = schedule

            response = self._post(client, sub_id)

        assert response.status_code == 200
        mock_release.assert_called_once_with("sub_sched_1")
        mock_modify.assert_called_once_with(
            "sub_stripe_1", cancel_at_period_end=True,
        )

        # El schedule local se limpia
        with Session(test_engine) as db:
            sub = db.get(Subscription, sub_id)
            assert sub.stripe_schedule_id is None
            assert sub.cancel_at_period_end is True

    def test_cancel_busca_schedule_en_stripe_si_no_hay_local(self, client, auth_headers):
        sub_id = _seed_subscription(
            status="active", cancel_at_period_end=False,
            stripe_schedule_id=None,
        )

        with patch("stripe.Subscription.retrieve") as mock_sub_retrieve, \
                patch("stripe.SubscriptionSchedule.retrieve") as mock_sched_retrieve, \
                patch("stripe.SubscriptionSchedule.release") as mock_release, \
                patch("stripe.Subscription.modify") as mock_modify:
            mock_sub_retrieve.return_value = {"id": "sub_stripe_1", "schedule": "sub_sched_9"}
            schedule = MagicMock()
            schedule.configure_mock(**{
                "get.side_effect": lambda key, default=None: {
                    "id": "sub_sched_9", "status": "active",
                }.get(key, default)
            })
            mock_sched_retrieve.return_value = schedule

            response = self._post(client, sub_id)

        assert response.status_code == 200
        mock_release.assert_called_once_with("sub_sched_9")
        mock_modify.assert_called_once_with(
            "sub_stripe_1", cancel_at_period_end=True,
        )

    def test_cancel_reintenta_si_stripe_rechaza_por_schedule(self, client, auth_headers):
        import stripe as stripe_lib

        sub_id = _seed_subscription(
            status="active", cancel_at_period_end=False,
            stripe_schedule_id="sub_sched_1",
        )

        with patch("stripe.SubscriptionSchedule.retrieve") as mock_retrieve, \
                patch("stripe.SubscriptionSchedule.release") as mock_release, \
                patch("stripe.Subscription.modify") as mock_modify:
            schedule = MagicMock()
            schedule.configure_mock(**{
                "get.side_effect": lambda key, default=None: {
                    "id": "sub_sched_1", "status": "active",
                }.get(key, default)
            })
            mock_retrieve.return_value = schedule
            # El primer modify falla con error de schedule (release previo falló),
            # el segundo reintento (tras release) funciona.
            mock_modify.side_effect = [
                stripe_lib.error.StripeError(
                    "Cannot cancel a subscription managed by a subscription schedule"
                ),
                {"id": "sub_stripe_1", "cancel_at_period_end": True},
            ]

            response = self._post(client, sub_id)

        assert response.status_code == 200
        assert mock_modify.call_count == 2
        assert mock_release.call_count == 2

        with Session(test_engine) as db:
            sub = db.get(Subscription, sub_id)
            assert sub.cancel_at_period_end is True
