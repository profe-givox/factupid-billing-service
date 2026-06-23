"""Fixtures compartidos para tests de la API de pagos Factupid."""

from typing import Generator
from unittest.mock import patch, MagicMock

import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine

from app.main import app
from app.db.session import get_session
from app.core.config import settings
from app.core.security import get_current_user, verify_token
from app.schemas.user import CurrentUser

# Base de datos en memoria para tests
TEST_DATABASE_URL = "sqlite:///./test_billing.db"
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    SQLModel.metadata.create_all(test_engine)
    yield
    SQLModel.metadata.drop_all(test_engine)


def override_get_session():
    with Session(test_engine) as session:
        yield session


app.dependency_overrides[get_session] = override_get_session


@pytest.fixture
def client() -> Generator:
    with TestClient(app) as c:
        yield c


MOCK_USER_PAYLOAD = {
    "sub": "test-user-1",
    "user_id": 1,
    "username": "testuser",
    "email": "test@factupid.com",
    "is_staff": False,
    "is_superuser": False,
    "groups": ["billing"],
    "perms": [
        "billing.create_checkout",
        "billing.cancel_subscription",
        "billing.change_subscription_plan",
        "billing.view_subscription",
        "billing.view_payments",
        "billing.register_subscription",
    ],
    "tenant": 1,
    "token_type": "access",
    "aud": "billing-api",
    "iss": "https://app.factupid.com",
}


def mock_get_current_user_all_perms():
    return CurrentUser(**MOCK_USER_PAYLOAD)


@pytest.fixture
def auth_headers() -> dict:
    """Headers con token JWT simulado (no se valida crypto, solo se usa override)."""
    return {"Authorization": "Bearer mock-token"}


@pytest.fixture(autouse=True)
def override_auth():
    """
    Por defecto, todos los endpoints autenticados usan un usuario con todos los permisos.
    Tests individuales pueden overridear esto.
    """
    app.dependency_overrides[get_current_user] = mock_get_current_user_all_perms
    yield
    # Restaurar el get_current_user original
    app.dependency_overrides.pop(get_current_user, None)


# Mock de Stripe
@pytest.fixture(autouse=True)
def mock_stripe():
    with patch("stripe.checkout.Session.create") as mock_session_create:
        mock_session = MagicMock()
        mock_session.url = "https://checkout.stripe.com/test_session_123"
        mock_session.id = "cs_test_123"
        mock_session.metadata = {"subscription_id": "1", "user_id": "1"}
        mock_session.configure_mock(**{
            "get.side_effect": lambda key, default=None: {
                "id": "cs_test_123",
                "metadata": {"subscription_id": "1", "user_id": "1"},
                "payment_status": "paid",
                "status": "complete",
                "mode": "subscription",
                "subscription": "sub_test_123",
                "customer_details": {"email": "test@factupid.com"},
                "amount_total": 5000,
                "currency": "mxn",
            }.get(key, default)
        })
        mock_session_create.return_value = mock_session

        with patch("stripe.checkout.Session.retrieve") as mock_retrieve:
            mock_retrieve.return_value = mock_session

            with patch("stripe.Subscription.retrieve") as mock_sub_retrieve:
                mock_sub = MagicMock()
                mock_sub.configure_mock(**{
                    "get.side_effect": lambda key, default=None: {
                        "id": "sub_test_123",
                        "status": "active",
                        "current_period_start": 1000000,
                        "current_period_end": 2000000,
                    }.get(key, default)
                })
                mock_sub_retrieve.return_value = mock_sub

                with patch("stripe.Webhook.construct_event") as mock_construct:
                    mock_event = MagicMock()
                    mock_event.__getitem__.side_effect = lambda key: {
                        "type": "checkout.session.completed",
                        "data": {
                            "object": {
                                "id": "cs_test_123",
                                "metadata": {
                                    "subscription_id": "1",
                                    "user_id": "1",
                                    "billing_code": "CFDI_PRO",
                                },
                                "payment_status": "paid",
                                "status": "complete",
                                "mode": "subscription",
                                "subscription": "sub_test_123",
                                "customer_details": {"email": "test@factupid.com"},
                                "amount_total": 5000,
                                "currency": "mxn",
                            }
                        },
                    }[key]
                    mock_construct.return_value = mock_event

                    yield
