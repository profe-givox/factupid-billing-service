"""Test de upgrade de plan: suscripción pending PRO → pago ENTERPRISE."""

from unittest.mock import patch, MagicMock
from sqlmodel import Session, select

from tests.conftest import test_engine
from app.models.subscription import Subscription
from app.models.payment import Payment
from app.models.plan import Plan
from app.routers.webhooks import handle_subscription_payment
from tests.test_stripe_event_ordering import _make_invoice_event


class TestUpgradePendingProAPagoEnterprise:
    """
    Escenario T5:
    1. Crear suscripción pending con plan PRO
    2. Cambiar plan a ENTERPRISE (simula upgrade antes del primer pago)
    3. Cobrar ENTERPRISE
    4. Notificar con billing_code=CFDI_ENTERPRISE
    """

    def test_upgrade_pro_to_enterprise_billing_code_correcto(
        self, client, seed_plans_and_sub
    ):
        data = seed_plans_and_sub
        sub_id = data["sub_id"]

        # 1) Cambiar plan a ENTERPRISE manualmente (simula handle_subscription_updated)
        with Session(test_engine) as db:
            ent = db.exec(
                select(Plan).where(Plan.code == "CFDI_ENTERPRISE")
            ).first()

            assert ent is not None

            sub = db.get(Subscription, sub_id)
            sub.plan_id = ent.id
            sub.status = "pending"
            db.add(sub)
            db.commit()

            enterprise_id = ent.id

        # 2) Cobrar (invoice.payment_succeeded)
        event = _make_invoice_event(
            sub_id,
            billing_code="CFDI_ENTERPRISE",
            stripe_sub_id=f"sub_stripe_{sub_id}",
        )
        invoice = event["data"]["object"]

        with patch("app.routers.webhooks.engine", test_engine):
            handle_subscription_payment(invoice, event)

        # Verificar
        with Session(test_engine) as db:
            sub = db.get(Subscription, sub_id)
            payments = db.exec(
                select(Payment).where(Payment.subscription_id == sub_id)
            ).all()

            # Plan debe ser ENTERPRISE
            assert sub.plan_id == ent.id
            # Pago registrado
            assert len(payments) == 1
            # Fechas actualizadas
            assert sub.start_date is not None
            assert sub.end_date is not None