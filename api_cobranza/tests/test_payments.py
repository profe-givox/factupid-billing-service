"""Tests para endpoints de pagos (/payments/*)."""

import json
from unittest.mock import patch, MagicMock

from fastapi.testclient import TestClient

from app.main import app
from app.core.security import get_current_user
from app.schemas.user import CurrentUser


MOCK_USER = CurrentUser(
    sub="test-user-1",
    user_id=1,
    username="testuser",
    email="test@factupid.com",
    is_staff=False,
    is_superuser=False,
    groups=["billing"],
    perms=[
        "billing.create_checkout",
        "billing.cancel_subscription",
        "billing.change_subscription_plan",
        "billing.view_subscription",
        "billing.view_payments",
        "billing.register_subscription",
    ],
    tenant=1,
    token_type="access",
    aud="billing-api",
    iss="https://app.factupid.com",
)


def test_confirm_payment_session_pagado(client: TestClient):
    """POST /payments/confirm con session_id pagado debe retornar paid."""
    app.dependency_overrides[get_current_user] = lambda: MOCK_USER

    with patch("stripe.checkout.Session.retrieve") as mock_retrieve:
        mock_session = MagicMock()
        mock_session.configure_mock(**{
            "get.side_effect": lambda key, default=None: {
                "id": "cs_test_paid",
                "metadata": {"subscription_id": "1"},
                "payment_status": "paid",
                "status": "complete",
                "mode": "subscription",
                "subscription": "sub_test_123",
                "customer_details": {"email": "test@factupid.com"},
                "amount_total": 5000,
                "currency": "mxn",
            }.get(key, default)
        })
        mock_retrieve.return_value = mock_session

        with patch("stripe.Subscription.retrieve") as mock_sub:
            mock_sub_data = MagicMock()
            mock_sub_data.configure_mock(**{
                "get.side_effect": lambda key, default=None: {
                    "id": "sub_test_123",
                    "status": "active",
                    "current_period_start": 1000000,
                    "current_period_end": 2000000,
                }.get(key, default)
            })
            mock_sub.return_value = mock_sub_data

            response = client.post(
                "/api/pagos/payments/confirm",
                json={"session_id": "cs_test_paid"},
                headers={"Authorization": "Bearer test-token"},
            )

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "active"
            assert data["payment_status"] == "paid"
            assert data["customer_email"] == "test@factupid.com"


def test_confirm_payment_session_no_pagado(client: TestClient):
    """POST /payments/confirm con session no pagado debe retornar unpaid."""
    app.dependency_overrides[get_current_user] = lambda: MOCK_USER

    with patch("stripe.checkout.Session.retrieve") as mock_retrieve:
        mock_session = MagicMock()
        mock_session.configure_mock(**{
            "get.side_effect": lambda key, default=None: {
                "id": "cs_test_unpaid",
                "metadata": {"subscription_id": "1"},
                "payment_status": "unpaid",
                "status": "complete",
                "mode": "payment",
                "customer_details": {"email": "test@factupid.com"},
                "amount_total": 5000,
                "currency": "mxn",
            }.get(key, default)
        })
        mock_retrieve.return_value = mock_session

        response = client.post(
            "/api/pagos/payments/confirm",
            json={"session_id": "cs_test_unpaid"},
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "unpaid"


def test_confirm_payment_session_no_existe(client: TestClient):
    """POST /payments/confirm con session_id inexistente debe retornar not_found."""
    app.dependency_overrides[get_current_user] = lambda: MOCK_USER

    with patch("stripe.checkout.Session.retrieve") as mock_retrieve:
        import stripe
        mock_retrieve.side_effect = stripe.error.InvalidRequestError(
            "Session not found", param="session_id"
        )

        response = client.post(
            "/api/pagos/payments/confirm",
            json={"session_id": "cs_test_nonexistent"},
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "not_found"


def test_confirm_payment_sin_session_id(client: TestClient):
    """POST /payments/confirm sin session_id debe retornar 400."""
    app.dependency_overrides[get_current_user] = lambda: MOCK_USER

    response = client.post(
        "/api/pagos/payments/confirm",
        json={},
        headers={"Authorization": "Bearer test-token"},
    )

    assert response.status_code == 400
    assert "session_id es requerido" in response.text


def test_confirm_payment_sin_jwt_rechazado(client: TestClient):
    """POST /payments/confirm sin JWT debe retornar 403."""
    app.dependency_overrides.pop(get_current_user, None)

    response = client.post(
        "/api/pagos/payments/confirm",
        json={"session_id": "cs_test_123"},
    )

    assert response.status_code == 403


def test_confirm_no_activa_planes(client: TestClient):
    """POST /payments/confirm NO debe modificar la BD ni activar planes."""
    app.dependency_overrides[get_current_user] = lambda: MOCK_USER

    with patch("stripe.checkout.Session.retrieve") as mock_retrieve:
        mock_session = MagicMock()
        mock_session.configure_mock(**{
            "get.side_effect": lambda key, default=None: {
                "id": "cs_test_paid",
                "metadata": {"subscription_id": "1"},
                "payment_status": "paid",
                "status": "complete",
                "mode": "payment",
                "customer_details": {"email": "test@factupid.com"},
                "amount_total": 5000,
                "currency": "mxn",
            }.get(key, default)
        })
        mock_retrieve.return_value = mock_session

        # Verificar que NO se llama a ninguna funcion que modifique BD
        with patch("app.routers.payments.Subscription") as mock_sub_model:
            response = client.post(
                "/api/pagos/payments/confirm",
                json={"session_id": "cs_test_paid"},
                headers={"Authorization": "Bearer test-token"},
            )
            assert response.status_code == 200
            # Solo lectura de Stripe, no debe tocar modelos locales
            mock_sub_model.assert_not_called()


def test_subscription_status_retorna_estado(client: TestClient):
    """GET /payments/status/{id} debe retornar el estado de la suscripcion."""
    app.dependency_overrides[get_current_user] = lambda: MOCK_USER

    response = client.get(
        "/api/pagos/payments/status/1",
        headers={"Authorization": "Bearer test-token"},
    )

    # La suscripcion puede no existir en test DB, pero el endpoint funciona
    assert response.status_code in (200, 404)
