"""Tests para el endpoint POST /subscriptions/report-overage (Fase 7B OnDemand).

Cubre:
- estados permitidos: active, cancel_scheduled, canceled
- estados rechazados: past_due, unpaid
- validación de quantity y total_amount
- creación del Stripe invoice item con amount en centavos y metadata
- uso / recuperación de stripe_customer_id
- no cambia subscription.status
"""

from unittest.mock import patch, MagicMock

import pytest
from sqlmodel import Session

from tests.conftest import test_engine
from app.models.plan import Plan
from app.models.subscription import Subscription


REPORT_OVERAGE_URL = "/api/pagos/subscriptions/report-overage"


def _seed_subscription(status="active", user_id=1, stripe_customer_id="cus_123"):
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
            stripe_subscription_id="sub_stripe_1",
            stripe_customer_id=stripe_customer_id,
        )
        db.add(sub)
        db.commit()
        db.refresh(sub)
        return sub.id


def _mock_invoice_item(item_id="ii_test_1"):
    item = MagicMock()
    item.id = item_id
    return item


def _overage_payload(
    subscription_id,
    user_id=1,
    quantity=3,
    unit_price=0.50,
    total_amount=1.50,
    **overrides,
):
    payload = {
        "subscription_id": subscription_id,
        "user_id": user_id,
        "overage_period_id": 77,
        "period_start": "2026-08-01",
        "period_end": "2026-08-31",
        "quantity": quantity,
        "unit_price": unit_price,
        "total_amount": total_amount,
        "currency": "mxn",
    }
    payload.update(overrides)
    return payload


class TestReportOverage:
    """El endpoint reporta excedentes como Stripe invoice item."""

    @pytest.fixture(autouse=True)
    def _patch_engine(self):
        with patch("app.routers.subscriptions.engine", test_engine):
            yield

    def _post(self, client, payload):
        return client.post(REPORT_OVERAGE_URL, json=payload)

    # ── Estados permitidos ──

    def test_permite_active(self, client, auth_headers):
        sub_id = _seed_subscription(status="active")

        with patch("stripe.InvoiceItem.create") as mock_invoice_item:
            mock_invoice_item.return_value = _mock_invoice_item()

            response = self._post(client, _overage_payload(sub_id))

        assert response.status_code == 200
        assert response.json()["success"] is True

    def test_permite_cancel_scheduled(self, client, auth_headers):
        sub_id = _seed_subscription(status="cancel_scheduled")

        with patch("stripe.InvoiceItem.create") as mock_invoice_item:
            mock_invoice_item.return_value = _mock_invoice_item()

            response = self._post(client, _overage_payload(sub_id))

        assert response.status_code == 200
        mock_invoice_item.assert_called_once()

    def test_permite_canceled(self, client, auth_headers):
        sub_id = _seed_subscription(status="canceled")

        with patch("stripe.InvoiceItem.create") as mock_invoice_item:
            mock_invoice_item.return_value = _mock_invoice_item()

            response = self._post(client, _overage_payload(sub_id))

        assert response.status_code == 200
        mock_invoice_item.assert_called_once()

    # ── Estados rechazados ──

    def test_rechaza_past_due(self, client, auth_headers):
        sub_id = _seed_subscription(status="past_due")

        with patch("stripe.InvoiceItem.create") as mock_invoice_item:
            response = self._post(client, _overage_payload(sub_id))

        assert response.status_code == 400
        assert response.json()["detail"]["code"] == "SUBSCRIPTION_OVERDUE"
        mock_invoice_item.assert_not_called()

    def test_rechaza_unpaid(self, client, auth_headers):
        sub_id = _seed_subscription(status="unpaid")

        with patch("stripe.InvoiceItem.create") as mock_invoice_item:
            response = self._post(client, _overage_payload(sub_id))

        assert response.status_code == 400
        assert response.json()["detail"]["code"] == "SUBSCRIPTION_OVERDUE"
        mock_invoice_item.assert_not_called()

    # ── Validaciones ──

    def test_rechaza_quantity_cero(self, client, auth_headers):
        sub_id = _seed_subscription(status="active")

        with patch("stripe.InvoiceItem.create") as mock_invoice_item:
            response = self._post(client, _overage_payload(sub_id, quantity=0))

        assert response.status_code == 400
        assert "quantity" in response.json()["detail"].lower()
        mock_invoice_item.assert_not_called()

    def test_rechaza_total_amount_cero(self, client, auth_headers):
        sub_id = _seed_subscription(status="active")

        with patch("stripe.InvoiceItem.create") as mock_invoice_item:
            response = self._post(client, _overage_payload(sub_id, total_amount=0))

        assert response.status_code == 400
        assert "total_amount" in response.json()["detail"].lower()
        mock_invoice_item.assert_not_called()

    # ── Creación del invoice item ──

    def test_crea_stripe_invoice_item(self, client, auth_headers):
        sub_id = _seed_subscription(status="active", stripe_customer_id="cus_123")

        with patch("stripe.InvoiceItem.create") as mock_invoice_item:
            mock_invoice_item.return_value = _mock_invoice_item("ii_test_77")

            response = self._post(client, _overage_payload(sub_id))

        assert response.status_code == 200
        body = response.json()
        assert body["stripe_invoice_item_id"] == "ii_test_77"
        assert body["amount"] == 150
        assert body["currency"] == "mxn"

        mock_invoice_item.assert_called_once_with(
            customer="cus_123",
            amount=150,
            currency="mxn",
            description="3 timbres CFDI excedentes - lote 0 - periodo 2026-08-01 a 2026-08-31",
            metadata={
                "factupid_type": "cfdi_overage",
                "user_id": "1",
                "subscription_id": str(sub_id),
                "overage_period_id": "77",
                "period_start": "2026-08-01",
                "period_end": "2026-08-31",
                "quantity": "3",
                "unit_price": "0.5",
                "report_sequence": "0",
            },
        )

    def test_usa_stripe_customer_id_existente(self, client, auth_headers):
        sub_id = _seed_subscription(
            status="active", stripe_customer_id="cus_existente",
        )

        with patch("stripe.Subscription.retrieve") as mock_retrieve, \
                patch("stripe.InvoiceItem.create") as mock_invoice_item:
            mock_invoice_item.return_value = _mock_invoice_item()

            response = self._post(client, _overage_payload(sub_id))

        assert response.status_code == 200
        # No se consulta Stripe si ya hay customer local
        mock_retrieve.assert_not_called()
        mock_invoice_item.assert_called_once_with(
            customer="cus_existente",
            amount=150,
            currency="mxn",
            description="3 timbres CFDI excedentes - lote 0 - periodo 2026-08-01 a 2026-08-31",
            metadata={
                "factupid_type": "cfdi_overage",
                "user_id": "1",
                "subscription_id": str(sub_id),
                "overage_period_id": "77",
                "period_start": "2026-08-01",
                "period_end": "2026-08-31",
                "quantity": "3",
                "unit_price": "0.5",
                "report_sequence": "0",
            },
        )

    def test_recupera_stripe_customer_id_si_falta(self, client, auth_headers):
        sub_id = _seed_subscription(status="active", stripe_customer_id=None)

        with patch("stripe.Subscription.retrieve") as mock_retrieve, \
                patch("stripe.InvoiceItem.create") as mock_invoice_item:
            mock_retrieve.return_value = {"id": "sub_stripe_1", "customer": "cus_recuperado"}
            mock_invoice_item.return_value = _mock_invoice_item()

            response = self._post(client, _overage_payload(sub_id))

        assert response.status_code == 200
        mock_retrieve.assert_called_once_with("sub_stripe_1")
        mock_invoice_item.assert_called_once()
        assert mock_invoice_item.call_args.kwargs["customer"] == "cus_recuperado"

        # El customer queda persistido localmente
        with Session(test_engine) as db:
            sub = db.get(Subscription, sub_id)
            assert sub.stripe_customer_id == "cus_recuperado"

    # ── No modifica estado ──

    def test_no_cambia_subscription_status(self, client, auth_headers):
        sub_id = _seed_subscription(status="cancel_scheduled")

        with patch("stripe.InvoiceItem.create") as mock_invoice_item:
            mock_invoice_item.return_value = _mock_invoice_item()

            response = self._post(client, _overage_payload(sub_id))

        assert response.status_code == 200

        with Session(test_engine) as db:
            sub = db.get(Subscription, sub_id)
            assert sub.status == "cancel_scheduled"

    # ── Robustez ──

    def test_subscription_no_encontrada(self, client, auth_headers):
        with patch("stripe.InvoiceItem.create") as mock_invoice_item:
            response = self._post(client, _overage_payload(999999))

        assert response.status_code == 404
        mock_invoice_item.assert_not_called()

    def test_subscription_de_otro_usuario_rechaza(self, client, auth_headers):
        sub_id = _seed_subscription(status="active", user_id=42)

        with patch("stripe.InvoiceItem.create") as mock_invoice_item:
            response = self._post(client, _overage_payload(sub_id, user_id=1))

        assert response.status_code == 403
        mock_invoice_item.assert_not_called()

    def test_stripe_error_devuelve_502(self, client, auth_headers):
        import stripe as stripe_lib

        sub_id = _seed_subscription(status="active")

        with patch("stripe.InvoiceItem.create") as mock_invoice_item:
            mock_invoice_item.side_effect = stripe_lib.error.StripeError("boom")

            response = self._post(client, _overage_payload(sub_id))

        assert response.status_code == 502
        assert "Stripe" in response.json()["detail"]["message"]
