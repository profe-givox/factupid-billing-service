"""Tests Fase 7C: delta, report_sequence y cfdi_overage_billed en Billing.

Se agrega al final de test_webhook_cfdi_overage.py.
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


def _post_invoice_webhook(client, event_dict):
    with patch("stripe.Webhook.construct_event", return_value=event_dict), \
            patch("app.routers.webhooks.engine", test_engine):
        return client.post(
            WEBHOOK_URL,
            content=INVOICE_WEBHOOK_BODY,
            headers=WEBHOOK_HEADERS,
        )


# ---------------------------------------------------------------------------
# 6. report-overage crea invoice item con metadata report_sequence
# ---------------------------------------------------------------------------


class TestReportOverageReportSequence:
    """report-overage incluye report_sequence en metadata y description."""

    @pytest.fixture(autouse=True)
    def _patch_engine(self):
        with patch("app.routers.subscriptions.engine", test_engine):
            yield

    def test_report_sequence_en_metadata_y_description(self, client, auth_headers):
        sub_id = _seed_subscription()

        payload = {
            "subscription_id": sub_id,
            "user_id": 1,
            "overage_period_id": 77,
            "period_start": "2026-08-01",
            "period_end": "2026-08-31",
            "quantity": 30,
            "unit_price": 0.5,
            "total_amount": 15.0,
            "currency": "mxn",
            "report_sequence": 3,
        }

        item = MagicMock()
        item.id = "ii_seq_meta_1"

        with patch("stripe.InvoiceItem.create") as mock_invoice_item:
            mock_invoice_item.return_value = item

            response = client.post(REPORT_OVERAGE_URL, json=payload)

        assert response.status_code == 200
        metadata = mock_invoice_item.call_args.kwargs["metadata"]
        assert metadata["report_sequence"] == "3"
        description = mock_invoice_item.call_args.kwargs["description"]
        assert "lote 3" in description
        assert "30 timbres" in description


class TestReportOverageDeltaNotTotal:
    """report-overage trata quantity como delta, NO como total del periodo."""

    @pytest.fixture(autouse=True)
    def _patch_engine(self):
        with patch("app.routers.subscriptions.engine", test_engine):
            yield

    def test_quantity_es_delta(self, client, auth_headers):
        sub_id = _seed_subscription()

        payload = {
            "subscription_id": sub_id,
            "user_id": 1,
            "overage_period_id": 99,
            "period_start": "2026-08-01",
            "period_end": "2026-08-31",
            "quantity": 30,
            "unit_price": 0.5,
            "total_amount": 15.0,
            "currency": "mxn",
            "report_sequence": 2,
        }

        item = MagicMock()
        item.id = "ii_delta_val_1"

        with patch("stripe.InvoiceItem.create") as mock_invoice_item:
            mock_invoice_item.return_value = item

            response = client.post(REPORT_OVERAGE_URL, json=payload)

        assert response.status_code == 200
        amount_cents = mock_invoice_item.call_args.kwargs["amount"]
        assert amount_cents == 1500


# ---------------------------------------------------------------------------
# 7. Factura solo excedente notifica cfdi_overage_billed y NO renueva
# ---------------------------------------------------------------------------


class TestOverageInvoiceNotificaBilled:
    """Factura SOLO de excedentes notifica cfdi_overage_billed a Django."""

    def test_solo_excedente_notifica_billed(self, client):
        sub_id = _seed_subscription()

        now_ts = int(time.time())

        overage_line = {
            "amount": 500,
            "period": {"start": now_ts, "end": now_ts + 30 * 86400},
            "metadata": {
                "factupid_type": "cfdi_overage",
                "overage_period_id": "42",
                "quantity": "10",
                "unit_price": "0.5",
                "report_sequence": "1",
            },
            "parent": {
                "subscription_item_details": {"subscription": "sub_stripe_overage_1"},
            },
        }

        event = {
            "id": "evt_billed_only_1",
            "type": "invoice.payment_succeeded",
            "data": {
                "object": {
                    "id": "in_billed_only_1",
                    "billing_reason": "subscription_cycle",
                    "amount_paid": 500,
                    "currency": "mxn",
                    "status_transitions": {"paid_at": now_ts},
                    "parent": {
                        "subscription_details": {
                            "subscription": "sub_stripe_overage_1",
                            "metadata": {
                                "subscription_id": str(sub_id),
                                "user_id": "1",
                                "billing_code": "CFDI_PRO",
                            },
                        }
                    },
                    "lines": {"data": [overage_line]},
                }
            },
        }

        with patch("app.routers.webhooks.notify_subscription_event") as mock_notify_sub, \
                patch("app.routers.webhooks.notify_main_app") as mock_notify_main, \
                patch("app.routers.webhooks._notify_cfdi_overage_billed") as mock_billed:
            response = _post_invoice_webhook(client, event)

        assert response.status_code == 200
        mock_notify_sub.assert_not_called()
        mock_notify_main.assert_not_called()
        mock_billed.assert_called_once()
        assert mock_billed.call_args.kwargs["overage_period_id"] == 42
        assert mock_billed.call_args.kwargs["quantity"] == 10


# ---------------------------------------------------------------------------
# 8. Factura mixta notifica cfdi_overage_billed y SÍ renueva
# ---------------------------------------------------------------------------


class TestMixedInvoiceNotificaBilled:
    """Factura mixta notifica cfdi_overage_billed y SÍ renueva."""

    def test_mixta_notifica_billed_y_renovacion(self, client):
        sub_id = _seed_subscription()

        now_ts = int(time.time())

        sub_line = {
            "period": {"start": now_ts, "end": now_ts + 30 * 86400},
            "parent": {
                "subscription_item_details": {"subscription": "sub_stripe_overage_1"},
            },
        }
        overage_line = {
            "amount": 250,
            "period": {"start": now_ts, "end": now_ts + 30 * 86400},
            "metadata": {
                "factupid_type": "cfdi_overage",
                "overage_period_id": "55",
                "quantity": "5",
                "unit_price": "0.5",
                "report_sequence": "2",
            },
            "parent": {
                "subscription_item_details": {"subscription": "sub_stripe_overage_1"},
            },
        }

        event = {
            "id": "evt_billed_mixed_1",
            "type": "invoice.payment_succeeded",
            "data": {
                "object": {
                    "id": "in_billed_mixed_1",
                    "billing_reason": "subscription_cycle",
                    "amount_paid": 5250,
                    "currency": "mxn",
                    "status_transitions": {"paid_at": now_ts},
                    "parent": {
                        "subscription_details": {
                            "subscription": "sub_stripe_overage_1",
                            "metadata": {
                                "subscription_id": str(sub_id),
                                "user_id": "1",
                                "billing_code": "CFDI_PRO",
                            },
                        }
                    },
                    "lines": {"data": [sub_line, overage_line]},
                }
            },
        }

        with patch("app.routers.webhooks.notify_subscription_event") as mock_notify_sub, \
                patch("app.routers.webhooks._notify_cfdi_overage_billed") as mock_billed:
            response = _post_invoice_webhook(client, event)

        assert response.status_code == 200
        mock_notify_sub.assert_called_once()
        assert mock_notify_sub.call_args.kwargs["event_type"] == "subscription_renewed"
        mock_billed.assert_called_once()
        assert mock_billed.call_args.kwargs["overage_period_id"] == 55
        assert mock_billed.call_args.kwargs["quantity"] == 5


# ---------------------------------------------------------------------------
# 9. Invoice.payment_succeeded duplicado no duplica efectos
# ---------------------------------------------------------------------------


class TestDuplicateInvoiceNoDuplica:
    """Un evento duplicado no debe duplicar payments ni notificaciones."""

    def test_duplicado_no_duplica_payment(self, client):
        sub_id = _seed_subscription()

        event = _make_invoice_event(
            sub_id,
            billing_code="CFDI_PRO",
            stripe_sub_id="sub_stripe_overage_1",
            billing_reason="subscription_cycle",
            invoice_id="in_dup_1",
        )

        with patch("app.routers.webhooks.notify_subscription_event") as mock_notify_sub:
            resp1 = _post_invoice_webhook(client, event)
            assert resp1.status_code == 200
            assert mock_notify_sub.call_count == 1

            mock_notify_sub.reset_mock()
            resp2 = _post_invoice_webhook(client, event)
            assert resp2.status_code == 200
            mock_notify_sub.assert_not_called()

        with Session(test_engine) as db:
            payments = list(db.exec(
                Payment.__table__.select().where(
                    Payment.provider_payment_id == "in_dup_1"
                )
            ))
            assert len(payments) == 1


# ---------------------------------------------------------------------------
# 10. Metadata de líneas cfdi_overage se extrae correctamente
# ---------------------------------------------------------------------------


class TestOverageMetadataExtraction:
    """La metadata de líneas cfdi_overage se extrae correctamente."""

    def test_extrae_metadata_de_line_metadata(self, client):
        sub_id = _seed_subscription()

        now_ts = int(time.time())

        overage_line = {
            "amount": 300,
            "period": {"start": now_ts, "end": now_ts + 30 * 86400},
            "metadata": {
                "factupid_type": "cfdi_overage",
                "overage_period_id": "33",
                "quantity": "6",
                "unit_price": "0.5",
                "report_sequence": "1",
            },
            "parent": {
                "subscription_item_details": {"subscription": "sub_stripe_overage_1"},
            },
        }

        sub_line = {
            "period": {"start": now_ts, "end": now_ts + 30 * 86400},
            "parent": {
                "subscription_item_details": {"subscription": "sub_stripe_overage_1"},
            },
        }

        event = {
            "id": "evt_meta_extract_1",
            "type": "invoice.payment_succeeded",
            "data": {
                "object": {
                    "id": "in_meta_extract_1",
                    "billing_reason": "subscription_cycle",
                    "amount_paid": 5300,
                    "currency": "mxn",
                    "status_transitions": {"paid_at": now_ts},
                    "parent": {
                        "subscription_details": {
                            "subscription": "sub_stripe_overage_1",
                            "metadata": {
                                "subscription_id": str(sub_id),
                                "user_id": "1",
                                "billing_code": "CFDI_PRO",
                            },
                        }
                    },
                    "lines": {"data": [sub_line, overage_line]},
                }
            },
        }

        with patch("app.routers.webhooks._notify_cfdi_overage_billed") as mock_billed:
            response = _post_invoice_webhook(client, event)

        assert response.status_code == 200
        mock_billed.assert_called_once()
        assert mock_billed.call_args.kwargs["overage_period_id"] == 33
        assert mock_billed.call_args.kwargs["quantity"] == 6
        assert mock_billed.call_args.kwargs["report_sequence"] == 1


# ---------------------------------------------------------------------------
# 11. Idempotency key se envía a Stripe y aparece en metadata
# ---------------------------------------------------------------------------


class TestReportOverageIdempotencyKey:
    """report-overage pasa idempotency_key a stripe.InvoiceItem.create."""

    @pytest.fixture(autouse=True)
    def _patch_engine(self):
        with patch("app.routers.subscriptions.engine", test_engine):
            yield

    def test_idempotency_key_se_envia_a_stripe(self, client, auth_headers):
        sub_id = _seed_subscription()

        payload = {
            "subscription_id": sub_id,
            "user_id": 1,
            "overage_period_id": 88,
            "period_start": "2026-08-01",
            "period_end": "2026-08-31",
            "quantity": 50,
            "unit_price": 0.5,
            "total_amount": 25.0,
            "currency": "mxn",
            "report_sequence": 1,
            "idempotency_key": "cfdi-overage-88-0-50",
        }

        item = MagicMock()
        item.id = "ii_idempotent_stripe_1"

        with patch("stripe.InvoiceItem.create") as mock_invoice_item:
            mock_invoice_item.return_value = item
            response = client.post(REPORT_OVERAGE_URL, json=payload)

        assert response.status_code == 200
        call_kwargs = mock_invoice_item.call_args.kwargs
        assert call_kwargs["idempotency_key"] == "cfdi-overage-88-0-50"

    def test_idempotency_key_en_metadata(self, client, auth_headers):
        sub_id = _seed_subscription()

        payload = {
            "subscription_id": sub_id,
            "user_id": 1,
            "overage_period_id": 89,
            "period_start": "2026-08-01",
            "period_end": "2026-08-31",
            "quantity": 20,
            "unit_price": 0.5,
            "total_amount": 10.0,
            "currency": "mxn",
            "idempotency_key": "cfdi-overage-89-0-20",
        }

        item = MagicMock()
        item.id = "ii_idempotent_meta_1"

        with patch("stripe.InvoiceItem.create") as mock_invoice_item:
            mock_invoice_item.return_value = item
            response = client.post(REPORT_OVERAGE_URL, json=payload)

        assert response.status_code == 200
        metadata = mock_invoice_item.call_args.kwargs["metadata"]
        assert metadata["idempotency_key"] == "cfdi-overage-89-0-20"

    def test_respuesta_incluye_idempotency_key(self, client, auth_headers):
        sub_id = _seed_subscription()

        payload = {
            "subscription_id": sub_id,
            "user_id": 1,
            "overage_period_id": 90,
            "period_start": "2026-08-01",
            "period_end": "2026-08-31",
            "quantity": 10,
            "unit_price": 0.5,
            "total_amount": 5.0,
            "currency": "mxn",
            "idempotency_key": "cfdi-overage-90-0-10",
        }

        item = MagicMock()
        item.id = "ii_idempotent_resp_1"

        with patch("stripe.InvoiceItem.create") as mock_invoice_item:
            mock_invoice_item.return_value = item
            response = client.post(REPORT_OVERAGE_URL, json=payload)

        assert response.status_code == 200
        body = response.json()
        assert body["idempotency_key"] == "cfdi-overage-90-0-10"

    def test_sin_idempotency_key_no_rompe(self, client, auth_headers):
        """Si no se envía idempotency_key, funciona sin ella (retrocompat)."""
        sub_id = _seed_subscription()

        payload = {
            "subscription_id": sub_id,
            "user_id": 1,
            "overage_period_id": 91,
            "period_start": "2026-08-01",
            "period_end": "2026-08-31",
            "quantity": 5,
            "unit_price": 0.5,
            "total_amount": 2.5,
            "currency": "mxn",
        }

        item = MagicMock()
        item.id = "ii_no_idemp_1"

        with patch("stripe.InvoiceItem.create") as mock_invoice_item:
            mock_invoice_item.return_value = item
            response = client.post(REPORT_OVERAGE_URL, json=payload)

        assert response.status_code == 200
        call_kwargs = mock_invoice_item.call_args.kwargs
        assert "idempotency_key" not in call_kwargs

    def test_no_modifica_subscription_status(self, client, auth_headers):
        """report-overage no cambia subscription.status."""
        sub_id = _seed_subscription()

        payload = {
            "subscription_id": sub_id,
            "user_id": 1,
            "overage_period_id": 92,
            "period_start": "2026-08-01",
            "period_end": "2026-08-31",
            "quantity": 10,
            "unit_price": 0.5,
            "total_amount": 5.0,
            "currency": "mxn",
            "idempotency_key": "cfdi-overage-92-0-10",
        }

        item = MagicMock()
        item.id = "ii_status_check_1"

        with patch("stripe.InvoiceItem.create") as mock_invoice_item:
            mock_invoice_item.return_value = item
            response = client.post(REPORT_OVERAGE_URL, json=payload)

        assert response.status_code == 200
        with Session(test_engine) as db:
            sub = db.get(Subscription, sub_id)
            assert sub.status == "active"
