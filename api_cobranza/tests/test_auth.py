"""Tests de autenticacion JWT para endpoints protegidos."""

from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

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


def test_payments_init_sin_jwt_rechazado(client: TestClient):
    """POST /payments/init sin JWT debe retornar 403."""
    app.dependency_overrides.pop(get_current_user, None)
    response = client.post(
        "/api/pagos/payments/init",
        json={"user_id": 1, "plan_code": "CFDI_PRUEBA_PAYMENT"},
    )
    assert response.status_code == 403


def test_payments_init_con_jwt_aceptado(client: TestClient):
    """POST /payments/init con JWT valido debe funcionar."""
    app.dependency_overrides[get_current_user] = lambda: MOCK_USER
    response = client.post(
        "/api/pagos/payments/init",
        json={"user_id": 1, "plan_code": "CFDI_PRUEBA_PAYMENT"},
        headers={"Authorization": "Bearer test-token"},
    )
    assert response.status_code in (201, 200, 404)
    # 404 si no existe el plan en test DB


def test_cancel_subscription_sin_jwt_rechazado(client: TestClient):
    """POST /payments/subscriptions/{id}/cancel sin JWT debe retornar 403."""
    app.dependency_overrides.pop(get_current_user, None)
    response = client.post(
        "/api/pagos/payments/subscriptions/1/cancel",
        json={"at_period_end": True},
    )
    assert response.status_code == 403


def test_change_plan_sin_jwt_rechazado(client: TestClient):
    """POST /subscriptions/change-plan sin JWT debe retornar 403."""
    app.dependency_overrides.pop(get_current_user, None)
    response = client.post(
        "/api/pagos/subscriptions/change-plan",
        params={"user_id": 1, "new_plan_code": "CFDI_PRO"},
    )
    assert response.status_code == 403


def test_preview_plan_change_sin_jwt_rechazado(client: TestClient):
    """POST /subscriptions/preview-plan-change sin JWT debe retornar 403."""
    app.dependency_overrides.pop(get_current_user, None)
    response = client.post(
        "/api/pagos/subscriptions/preview-plan-change",
        params={"user_id": 1, "new_plan_code": "CFDI_PRO"},
    )
    assert response.status_code == 403


def test_plans_create_stripe_sin_jwt_rechazado(client: TestClient):
    """POST /plans/create-stripe sin JWT debe retornar 403."""
    app.dependency_overrides.pop(get_current_user, None)
    response = client.post(
        "/api/pagos/plans/create-stripe",
        json={
            "code": "TEST_PLAN",
            "name": "Test",
            "price": 100,
            "currency": "MXN",
            "billing_type": "one_time",
        },
    )
    assert response.status_code == 403


def test_plans_register_sin_jwt_rechazado(client: TestClient):
    """POST /plans/register sin JWT debe retornar 403."""
    app.dependency_overrides.pop(get_current_user, None)
    response = client.post(
        "/api/pagos/plans/register",
        json={
            "code": "TEST_REGISTER",
            "name": "Test",
            "price": 100,
            "currency": "MXN",
            "billing_type": "one_time",
            "stripe_product_id": "prod_test",
            "stripe_price_id": "price_test",
        },
    )
    assert response.status_code == 403


def test_plans_update_sin_jwt_rechazado(client: TestClient):
    """PATCH /plans/{code} sin JWT debe retornar 403."""
    app.dependency_overrides.pop(get_current_user, None)
    response = client.patch(
        "/api/pagos/plans/CFDI_FREE",
        json={"name": "Updated"},
    )
    assert response.status_code == 403


def test_webhook_stripe_no_requiere_jwt(client: TestClient):
    """POST /webhooks/stripe NO debe requerir JWT (usa Stripe signature)."""
    app.dependency_overrides.pop(get_current_user, None)
    response = client.post(
        "/api/pagos/webhooks/stripe",
        json={},
    )
    # Sin firma Stripe da 400, no 403
    assert response.status_code == 400
    assert "Missing Stripe signature" in response.text
