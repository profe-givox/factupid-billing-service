"""Tests para el endpoint POST /subscriptions/regularize-payment.

Cubre:
- past_due/unpaid crean sesión del portal de cliente de Stripe
- estados no permitidos son rechazados
- validación de pertenencia de la suscripción
- recuperación de stripe_customer_id desde Stripe si falta
- errores de Stripe y de permisos
"""

from unittest.mock import patch, MagicMock

import pytest
from sqlmodel import Session

from tests.conftest import test_engine
from app.models.plan import Plan
from app.models.subscription import Subscription
from app.core.security import get_current_user
from app.schemas.user import CurrentUser


REGULARIZE_URL = "/api/pagos/subscriptions/regularize-payment"


def _seed_subscription(status="past_due", user_id=1, stripe_customer_id=None):
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


class TestRegularizePaymentPortal:
    """El endpoint crea una sesión del Billing Portal de Stripe."""

    @pytest.fixture(autouse=True)
    def _patch_engine(self):
        with patch("app.routers.subscriptions.engine", test_engine):
            yield

    def _post(self, client, subscription_id, user_id=1, return_url="https://app.factupid.com/console/subscription/"):
        return client.post(
            REGULARIZE_URL,
            json={
                "subscription_id": subscription_id,
                "user_id": user_id,
                "return_url": return_url,
            },
        )

    def test_past_due_crea_sesion_portal(self, client, auth_headers):
        sub_id = _seed_subscription(
            status="past_due", stripe_customer_id="cus_123",
        )

        with patch("stripe.billing_portal.Session.create") as mock_portal:
            mock_session = MagicMock()
            mock_session.url = "https://billing.stripe.com/p/session_abc"
            mock_portal.return_value = mock_session

            response = self._post(client, sub_id)

        assert response.status_code == 200
        body = response.json()
        assert body["url"] == "https://billing.stripe.com/p/session_abc"
        assert body["subscription_id"] == sub_id
        assert body["status"] == "past_due"

        mock_portal.assert_called_once_with(
            customer="cus_123",
            return_url="https://app.factupid.com/console/subscription/",
        )

        # No modifica el estado de la suscripción
        with Session(test_engine) as db:
            sub = db.get(Subscription, sub_id)
            assert sub.status == "past_due"

    def test_unpaid_crea_sesion_portal(self, client, auth_headers):
        sub_id = _seed_subscription(
            status="unpaid", stripe_customer_id="cus_123",
        )

        with patch("stripe.billing_portal.Session.create") as mock_portal:
            mock_session = MagicMock()
            mock_session.url = "https://billing.stripe.com/p/session_abc"
            mock_portal.return_value = mock_session

            response = self._post(client, sub_id)

        assert response.status_code == 200
        assert response.json()["url"] == "https://billing.stripe.com/p/session_abc"
        mock_portal.assert_called_once()

    def test_active_rechaza(self, client, auth_headers):
        sub_id = _seed_subscription(status="active", stripe_customer_id="cus_123")

        with patch("stripe.billing_portal.Session.create") as mock_portal:
            response = self._post(client, sub_id)

        assert response.status_code == 400
        body = response.json()["detail"]
        assert body["code"] == "SUBSCRIPTION_NOT_PENDING"
        mock_portal.assert_not_called()

    def test_canceled_rechaza(self, client, auth_headers):
        sub_id = _seed_subscription(status="canceled", stripe_customer_id="cus_123")

        with patch("stripe.billing_portal.Session.create") as mock_portal:
            response = self._post(client, sub_id)

        assert response.status_code == 400
        mock_portal.assert_not_called()

    def test_subscription_no_encontrada(self, client, auth_headers):
        response = self._post(client, 999999)

        assert response.status_code == 404
        assert "no encontrada" in response.json()["detail"].lower()

    def test_subscription_de_otro_usuario_rechaza(self, client, auth_headers):
        sub_id = _seed_subscription(
            status="past_due", user_id=42, stripe_customer_id="cus_123",
        )

        with patch("stripe.billing_portal.Session.create") as mock_portal:
            response = self._post(client, sub_id, user_id=1)

        assert response.status_code == 403
        mock_portal.assert_not_called()

    def test_recupera_customer_desde_stripe(self, client, auth_headers):
        # Sin stripe_customer_id local pero con stripe_subscription_id
        sub_id = _seed_subscription(status="past_due", stripe_customer_id=None)

        with patch("stripe.Subscription.retrieve") as mock_retrieve:
            mock_retrieve.return_value = {"id": "sub_stripe_1", "customer": "cus_789"}
            with patch("stripe.billing_portal.Session.create") as mock_portal:
                mock_session = MagicMock()
                mock_session.url = "https://billing.stripe.com/p/session_abc"
                mock_portal.return_value = mock_session

                response = self._post(client, sub_id)

        assert response.status_code == 200
        mock_retrieve.assert_called_once_with("sub_stripe_1")
        mock_portal.assert_called_once_with(
            customer="cus_789",
            return_url="https://app.factupid.com/console/subscription/",
        )

        # El customer queda persistido localmente
        with Session(test_engine) as db:
            sub = db.get(Subscription, sub_id)
            assert sub.stripe_customer_id == "cus_789"

    def test_sin_customer_rechaza(self, client, auth_headers):
        # Ni customer local ni stripe_subscription_id para recuperarlo
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
                user_id=1, plan_id=plan.id, status="past_due", provider="stripe",
                stripe_subscription_id=None, stripe_customer_id=None,
            )
            db.add(sub)
            db.commit()
            db.refresh(sub)
            sub_id = sub.id

        with patch("stripe.billing_portal.Session.create") as mock_portal:
            response = self._post(client, sub_id)

        assert response.status_code == 400
        assert "cliente de Stripe" in response.json()["detail"]
        mock_portal.assert_not_called()

    def test_stripe_error_devuelve_502(self, client, auth_headers):
        sub_id = _seed_subscription(
            status="past_due", stripe_customer_id="cus_123",
        )

        import stripe as stripe_lib

        with patch("stripe.billing_portal.Session.create") as mock_portal:
            mock_portal.side_effect = stripe_lib.error.StripeError("boom")

            response = self._post(client, sub_id)

        assert response.status_code == 502
        assert "Stripe" in response.json()["detail"]["message"]

    def test_error_recuperando_customer_devuelve_502(self, client, auth_headers):
        sub_id = _seed_subscription(status="past_due", stripe_customer_id=None)

        import stripe as stripe_lib

        with patch("stripe.Subscription.retrieve") as mock_retrieve:
            mock_retrieve.side_effect = stripe_lib.error.StripeError("boom")
            with patch("stripe.billing_portal.Session.create") as mock_portal:
                response = self._post(client, sub_id)

        assert response.status_code == 502
        mock_portal.assert_not_called()

    def test_sin_permiso_rechaza(self, client, auth_headers):
        sub_id = _seed_subscription(
            status="past_due", stripe_customer_id="cus_123",
        )

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
            with patch("stripe.billing_portal.Session.create") as mock_portal:
                response = self._post(client, sub_id)

            assert response.status_code == 403
            mock_portal.assert_not_called()
        finally:
            fastapi_app.dependency_overrides.pop(get_current_user, None)
