"""
Tests que verifican el comportamiento de los handlers de Stripe
cuando los eventos llegan en diferentes órdenes.

Escenario real del bug:
  Stripe envió invoice.payment_succeeded ANTES de checkout.session.completed,
  y Django respondió HTTP 500 AttributeError en /checkout/complete/.
"""

from unittest.mock import patch, MagicMock
from sqlmodel import Session, select
from fastapi.testclient import TestClient

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


class TestOrdenEventosCheckoutLuegoInvoice:
    """Orden feliz: checkout → invoice (el más común)."""

    def test_checkout_then_invoice(self, client, seed_plans_and_sub):
        data = seed_plans_and_sub
        sub_id = data["sub_id"]

        # 1) checkout.session.completed
        event = _make_checkout_event(sub_id, billing_code="CFDI_PRO")
        session_data = event["data"]["object"]

        with patch("app.routers.webhooks.engine", test_engine):
            with patch("app.routers.webhooks.notify_main_app") as mock_notify:
                handle_checkout_completed(session_data)
                mock_notify.assert_called_once()

        # Verificar que se activó
        with Session(test_engine) as db:
            sub = db.get(Subscription, sub_id)
            assert sub.status == "active"

        # 2) invoice.payment_succeeded
        event_inv = _make_invoice_event(sub_id)
        invoice = event_inv["data"]["object"]

        with patch("app.routers.webhooks.engine", test_engine):
            handle_subscription_payment(invoice, event_inv)

        # Verificar que se creó el pago y NO se rompió nada
        with Session(test_engine) as db:
            payments = db.exec(
                select(Payment).where(Payment.subscription_id == sub_id)
            ).all()
            assert len(payments) == 1
            sub = db.get(Subscription, sub_id)
            assert sub.status == "active"


class TestOrdenEventosInvoiceLuegoCheckout:
    """
    Orden del bug: invoice.payment_succeeded → checkout.session.completed.

    En este escenario, cuando llega checkout.session.completed,
    la suscripción ya podría tener datos parciales del invoice handler.
    El handler de checkout debe ser tolerante.
    """

    def test_invoice_then_checkout_no_crash(self, client, seed_plans_and_sub):
        data = seed_plans_and_sub
        sub_id = data["sub_id"]

        # 1) invoice.payment_succeeded PRIMERO
        event_inv = _make_invoice_event(sub_id)
        invoice = event_inv["data"]["object"]

        with patch("app.routers.webhooks.engine", test_engine):
            handle_subscription_payment(invoice, event_inv)

        # Verificar que el pago se registró
        with Session(test_engine) as db:
            payments = db.exec(
                select(Payment).where(Payment.subscription_id == sub_id)
            ).all()
            assert len(payments) == 1
            # La suscripción sigue pending (invoice no la activa)
            sub = db.get(Subscription, sub_id)
            assert sub.status == "pending"

        # 2) checkout.session.completed DESPUÉS
        event = _make_checkout_event(sub_id, billing_code="CFDI_PRO")
        session_data = event["data"]["object"]

        with patch("app.routers.webhooks.engine", test_engine):
            with patch("app.routers.webhooks.notify_main_app") as mock_notify:
                handle_checkout_completed(session_data)
                mock_notify.assert_called_once()

        # Verificar estado final
        with Session(test_engine) as db:
            sub = db.get(Subscription, sub_id)
            assert sub.status == "active"
            # Debe haber exactamente 1 pago (no duplicado)
            payments = db.exec(
                select(Payment).where(Payment.subscription_id == sub_id)
            ).all()
            assert len(payments) == 1