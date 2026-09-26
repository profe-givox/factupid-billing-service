"""Tests de idempotencia: eventos duplicados no deben romper nada."""

from unittest.mock import patch, MagicMock
from sqlmodel import Session, select

from tests.conftest import test_engine
from app.models.subscription import Subscription
from app.models.payment import Payment
from app.routers.webhooks import (
    handle_checkout_completed,
    handle_subscription_payment,
)
from tests.conftest import (
    test_engine,
    _make_checkout_event,
    _make_invoice_event,
)


class TestCheckoutCompletedDuplicado:
    """checkout.session.completed enviado dos veces con mismo session_id."""

    def test_duplicado_no_duplica_estado(self, client, seed_plans_and_sub):
        data = seed_plans_and_sub
        sub_id = data["sub_id"]
        cs_id = "cs_duplicated_123"

        # Primer evento — checkout SOLO activa, NO notifica
        event1 = _make_checkout_event(
            sub_id, billing_code="CFDI_PRO",
        )
        event1["data"]["object"]["id"] = cs_id

        with patch("app.routers.webhooks.engine", test_engine):
            with patch("app.routers.webhooks.notify_main_app") as mock_notify:
                handle_checkout_completed(event1["data"]["object"])
                assert mock_notify.call_count == 0

        # Verificar que se activó y guardó stripe_subscription_id
        with Session(test_engine) as db:
            sub = db.get(Subscription, sub_id)
            assert sub.status == "active"
            assert sub.stripe_subscription_id is not None

        # Segundo evento (duplicado exacto) — no debe romper el estado ni notificar
        event2 = _make_checkout_event(
            sub_id, billing_code="CFDI_PRO",
        )
        event2["data"]["object"]["id"] = cs_id

        with patch("app.routers.webhooks.engine", test_engine):
            with patch("app.routers.webhooks.notify_main_app") as mock_notify2:
                handle_checkout_completed(event2["data"]["object"])
                assert mock_notify2.call_count == 0

        # Estado final: suscripción activa, sin duplicar
        with Session(test_engine) as db:
            sub = db.get(Subscription, sub_id)
            assert sub.status == "active"
            assert sub.stripe_subscription_id is not None


class TestInvoicePaymentSucceededDuplicado:
    """invoice.payment_succeeded enviado dos veces con mismo invoice_id."""

    def test_duplicado_no_duplica_pago(self, client, seed_plans_and_sub):
        data = seed_plans_and_sub
        sub_id = data["sub_id"]
        invoice_id = "in_dup_test_456"

        # Primer evento
        event1 = _make_invoice_event(sub_id, invoice_id=invoice_id)
        inv1 = event1["data"]["object"]

        with patch("app.routers.webhooks.engine", test_engine):
            handle_subscription_payment(inv1, event1)

        with Session(test_engine) as db:
            payments = db.exec(
                select(Payment).where(Payment.subscription_id == sub_id)
            ).all()
            assert len(payments) == 1

        # Segundo evento (duplicado exacto)
        event2 = _make_invoice_event(sub_id, invoice_id=invoice_id)
        inv2 = event2["data"]["object"]

        with patch("app.routers.webhooks.engine", test_engine):
            handle_subscription_payment(inv2, event2)

        # Idempotencia: sigue habiendo exactamente 1 pago
        with Session(test_engine) as db:
            payments = db.exec(
                select(Payment).where(Payment.subscription_id == sub_id)
            ).all()
            assert len(payments) == 1