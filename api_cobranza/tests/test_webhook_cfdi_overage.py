"""Tests BUG 2 Fase 7B: invoice de excedentes CFDI no se interpreta como renovación.

Cubre:
- _is_cfdi_overage_invoice detecta metadata en la línea y en invoice_item_details
- handle_subscription_payment corta el flujo para facturas de excedentes:
  NO renueva, NO toca start_date/end_date/status, NO notifica a Django.
- Los pagos normales (subscription_cycle / subscription_create) siguen
  notificando subscription_renewed / checkout_complete.
- report-overage crea el invoice item con metadata factupid_type=cfdi_overage.
"""

import time
from datetime import date, datetime, timezone

from unittest.mock import patch, MagicMock

import pytest

from sqlmodel import Session

from tests.conftest import test_engine, _make_invoice_event
from app.models.plan import Plan
from app.models.subscription import Subscription
from app.models.payment import Payment

WEBHOOK_URL = "/api/pagos/webhooks/stripe"
INVOICE_WEBHOOK_BODY = '{"type": "invoice.payment_succeeded"}'
WEBHOOK_HEADERS = {
    "stripe-signature": "t=123,v1=valida",
    "Content-Type": "application/json",
}
REPORT_OVERAGE_URL = "/api/pagos/subscriptions/report-overage"


def _seed_subscription(
    user_id=1,
    status="active",
    stripe_customer_id="cus_overage_1",
    start_date=None,
    end_date=None,
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
            stripe_subscription_id="sub_stripe_overage_1",
            stripe_customer_id=stripe_customer_id,
            start_date=start_date or date(2026, 8, 1),
            end_date=end_date or date(2026, 8, 31),
        )
        db.add(sub)
        db.commit()
        db.refresh(sub)
        return sub.id


def _make_overage_invoice(
    sub_id,
    *,
    invoice_id=None,
    stripe_sub_id="sub_stripe_overage_1",
    billing_reason="subscription_cycle",
    placement="line",
):
    """Factura de excedentes CFDI con metadata factupid_type=cfdi_overage.

    placement:
      - "line": metadata en invoice.lines.data[].metadata
      - "item_details": metadata dentro de invoice_item_details
    """
    now_ts = int(time.time())
    invoice_id = invoice_id or f"in_overage_{int(time.time() * 1000)}"

    line = {
        "period": {"start": now_ts, "end": now_ts + 30 * 86400},
        "parent": {
            "subscription_item_details": {"subscription": stripe_sub_id},
        },
    }

    if placement == "line":
        line["metadata"] = {"factupid_type": "cfdi_overage"}
    elif placement == "item_details":
        line["invoice_item_details"] = {
            "id": f"ii_overage_{int(time.time() * 1000)}",
            "metadata": {
                "factupid_type": "cfdi_overage",
                "overage_period_id": "77",
                "period_start": "2026-08-01",
                "period_end": "2026-08-31",
                "quantity": "3",
            },
        }

    obj = {
        "id": invoice_id,
        "billing_reason": billing_reason,
        "amount_paid": 150,
        "currency": "mxn",
        "status_transitions": {"paid_at": now_ts},
        "parent": {
            "subscription_details": {
                "subscription": stripe_sub_id,
                "metadata": {
                    "subscription_id": str(sub_id),
                    "user_id": "1",
                    "billing_code": "CFDI_PRO",
                },
            }
        },
        "lines": {"data": [line]},
    }

    return {
        "id": f"evt_{invoice_id}",
        "type": "invoice.payment_succeeded",
        "data": {"object": obj},
    }


def _post_invoice_webhook(client, event_dict):
    """Envía el evento invoice.payment_succeeded por el webhook real."""
    with patch("stripe.Webhook.construct_event", return_value=event_dict), \
            patch("app.routers.webhooks.engine", test_engine):
        return client.post(
            WEBHOOK_URL,
            content=INVOICE_WEBHOOK_BODY,
            headers=WEBHOOK_HEADERS,
        )


class TestCfdiOverageInvoiceWebhook:
    """invoice.payment_succeeded de excedentes no renueva la suscripción."""

    def test_no_notifica_subscription_renewed(self, client):
        sub_id = _seed_subscription()
        event = _make_overage_invoice(sub_id)

        with patch("app.routers.webhooks.notify_subscription_event") as mock_notify_sub, \
                patch("app.routers.webhooks.notify_main_app") as mock_notify_main:
            response = _post_invoice_webhook(client, event)

        assert response.status_code == 200
        mock_notify_sub.assert_not_called()
        mock_notify_main.assert_not_called()

    def test_no_actualiza_start_date_ni_end_date(self, client):
        sub_id = _seed_subscription(
            start_date=date(2026, 8, 1),
            end_date=date(2026, 8, 31),
        )
        event = _make_overage_invoice(sub_id)

        _post_invoice_webhook(client, event)

        with Session(test_engine) as db:
            sub = db.get(Subscription, sub_id)
            assert sub.start_date == date(2026, 8, 1)
            assert sub.end_date == date(2026, 8, 31)

    def test_no_cambia_subscription_status(self, client):
        sub_id = _seed_subscription(status="active")
        event = _make_overage_invoice(sub_id)

        _post_invoice_webhook(client, event)

        with Session(test_engine) as db:
            sub = db.get(Subscription, sub_id)
            assert sub.status == "active"

    def test_no_notifica_main_app_y_registra_payment(self, client):
        sub_id = _seed_subscription()
        event = _make_overage_invoice(sub_id, invoice_id="in_overage_pay_1")

        with patch("app.routers.webhooks.notify_main_app") as mock_notify_main:
            _post_invoice_webhook(client, event)

        mock_notify_main.assert_not_called()

        # Se registra el pago (idempotente por invoice_id) sin renovación
        with Session(test_engine) as db:
            payment = db.exec(
                Payment.__table__.select().where(
                    Payment.provider_payment_id == "in_overage_pay_1"
                )
            ).first()
            assert payment is not None
            assert payment.subscription_id == sub_id
            assert payment.amount == 150
            assert payment.status == "succeeded"

    def test_detecta_metadata_en_invoice_item_details(self, client):
        sub_id = _seed_subscription()
        event = _make_overage_invoice(sub_id, placement="item_details")

        with patch("app.routers.webhooks.notify_subscription_event") as mock_notify_sub, \
                patch("app.routers.webhooks.notify_main_app") as mock_notify_main:
            response = _post_invoice_webhook(client, event)

        assert response.status_code == 200
        mock_notify_sub.assert_not_called()
        mock_notify_main.assert_not_called()

        with Session(test_engine) as db:
            sub = db.get(Subscription, sub_id)
            assert sub.status == "active"
            assert sub.start_date == date(2026, 8, 1)


class TestInvoiceNormalSigueNotificando:
    """Las facturas normales de suscripción siguen su flujo original."""

    def test_subscription_cycle_sigue_notificando_renewed(self, client):
        sub_id = _seed_subscription()

        event = _make_invoice_event(
            sub_id,
            billing_code="CFDI_PRO",
            stripe_sub_id="sub_stripe_overage_1",
            billing_reason="subscription_cycle",
            invoice_id="in_normal_cycle_1",
        )

        with patch("app.routers.webhooks.notify_subscription_event") as mock_notify_sub:
            response = _post_invoice_webhook(client, event)

        assert response.status_code == 200
        mock_notify_sub.assert_called_once()
        assert mock_notify_sub.call_args.kwargs["event_type"] == "subscription_renewed"

    def test_subscription_create_sigue_notificando_checkout_complete(self, client):
        sub_id = _seed_subscription()

        event = _make_invoice_event(
            sub_id,
            billing_code="CFDI_PRO",
            stripe_sub_id="sub_stripe_overage_1",
            billing_reason="subscription_create",
            invoice_id="in_normal_create_1",
        )

        with patch("app.routers.webhooks.notify_main_app") as mock_notify_main:
            response = _post_invoice_webhook(client, event)

        assert response.status_code == 200
        mock_notify_main.assert_called_once()
        assert mock_notify_main.call_args.kwargs["subscription_id"] == sub_id


class TestReportOverageMetadata:
    """report-overage crea el invoice item con metadata factupid_type."""

    @pytest.fixture(autouse=True)
    def _patch_engine(self):
        with patch("app.routers.subscriptions.engine", test_engine):
            yield

    def test_invoice_item_metadata_incluye_factupid_type(self, client, auth_headers):
        sub_id = _seed_subscription()

        payload = {
            "subscription_id": sub_id,
            "user_id": 1,
            "overage_period_id": 77,
            "period_start": "2026-08-01",
            "period_end": "2026-08-31",
            "quantity": 3,
            "unit_price": 0.5,
            "total_amount": 1.5,
            "currency": "mxn",
        }

        item = MagicMock()
        item.id = "ii_overage_meta_1"

        with patch("stripe.InvoiceItem.create") as mock_invoice_item:
            mock_invoice_item.return_value = item

            response = client.post(REPORT_OVERAGE_URL, json=payload)

        assert response.status_code == 200
        mock_invoice_item.assert_called_once()
        metadata = mock_invoice_item.call_args.kwargs["metadata"]
        assert metadata["factupid_type"] == "cfdi_overage"
        assert metadata["overage_period_id"] == "77"
        assert metadata["subscription_id"] == str(sub_id)
        assert metadata["quantity"] == "3"
