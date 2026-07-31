"""Tests para webhooks de Stripe."""

from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from app.main import app


def test_webhook_stripe_sin_firma(client: TestClient):
    """Webhook sin firma Stripe debe ser rechazado con 400."""
    response = client.post("/api/pagos/webhooks/stripe", json={})
    assert response.status_code == 400
    assert "Missing Stripe signature" in response.text


def test_webhook_stripe_firma_invalida(client: TestClient):
    """Webhook con firma invalida debe ser rechazado con 400."""
    from unittest.mock import patch

    with patch("stripe.Webhook.construct_event") as mock_construct:
        import stripe
        mock_construct.side_effect = stripe.error.SignatureVerificationError(
            "Invalid signature", "sig_header"
        )

        response = client.post(
            "/api/pagos/webhooks/stripe",
            content='{"type": "checkout.session.completed"}',
            headers={
                "stripe-signature": "t=123,v1=firma_invalida",
                "Content-Type": "application/json",
            },
        )
        assert response.status_code == 400
        assert "Invalid signature" in response.text


def test_webhook_checkout_completed_no_pagado_no_activa(client: TestClient):
    """checkout.session.completed con payment_status != paid NO debe activar."""
    from unittest.mock import patch, MagicMock

    mock_event = MagicMock()
    mock_event.__getitem__.side_effect = lambda key: {
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "id": "cs_test_unpaid",
                "metadata": {"subscription_id": "999"},
                "payment_status": "unpaid",
                "status": "complete",
                "mode": "payment",
            }
        },
    }[key]

    with patch("stripe.Webhook.construct_event", return_value=mock_event):
        with patch("app.routers.webhooks.notify_main_app") as mock_notify:
            response = client.post(
                "/api/pagos/webhooks/stripe",
                content='{"type": "checkout.session.completed"}',
                headers={
                    "stripe-signature": "t=123,v1=valida",
                    "Content-Type": "application/json",
                },
            )
            assert response.status_code == 200
            mock_notify.assert_not_called()


def test_webhook_checkout_completed_pagado_sin_fechas_no_notifica(client: TestClient):
    """
    checkout.session.completed con payment_status=paid pero sin fechas
    en la suscripción NO debe notificar a Django.
    La activación final se hará desde invoice.payment_succeeded.
    """
    from unittest.mock import patch, MagicMock
    from app.routers import webhooks
    from tests.conftest import test_engine
    from app.models.plan import Plan
    from app.models.subscription import Subscription
    from sqlmodel import Session

    # Crear plan y suscripcion en test DB (sin start_date/end_date)
    with Session(test_engine) as db:
        plan = Plan(
            code="CFDI_PRO",
            name="Test PRO",
            price=5000,
            currency="MXN",
            interval="month",
            billing_type="subscription",
            stripe_price_id="price_test",
            stripe_product_id="prod_test",
            is_active=True,
        )
        db.add(plan)
        db.commit()
        db.refresh(plan)

        sub = Subscription(
            user_id=1,
            plan_id=plan.id,
            status="pending",
            provider="stripe",
        )
        db.add(sub)
        db.commit()
        sub_id = sub.id

    mock_event = MagicMock()
    mock_event.__getitem__.side_effect = lambda key: {
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "id": "cs_test_paid",
                "metadata": {
                    "subscription_id": str(sub_id),
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

    with patch("stripe.Webhook.construct_event", return_value=mock_event):
        with patch("app.routers.webhooks.notify_main_app") as mock_notify:
            with patch("app.routers.webhooks.engine", test_engine):
                response = client.post(
                    "/api/pagos/webhooks/stripe",
                    content='{"type": "checkout.session.completed"}',
                    headers={
                        "stripe-signature": "t=123,v1=valida",
                        "Content-Type": "application/json",
                    },
                )
                assert response.status_code == 200
                mock_notify.assert_not_called()

                # Verificar que la suscripcion local sí se activó
                with Session(test_engine) as db:
                    updated = db.get(Subscription, sub_id)
                    assert updated is not None
                    assert updated.status == "active"
                    assert updated.stripe_subscription_id == "sub_test_123"


def test_webhook_payload_malformado(client: TestClient):
    """Payload invalido debe ser rechazado."""
    from unittest.mock import patch

    with patch("stripe.Webhook.construct_event") as mock_construct:
        mock_construct.side_effect = ValueError("Invalid payload")

        response = client.post(
            "/api/pagos/webhooks/stripe",
            content="not-json",
            headers={
                "stripe-signature": "t=123,v1=valida",
            },
        )
        assert response.status_code == 400


def test_webhook_invoice_subscription_create_notifica_main_app(client: TestClient):
    """
    invoice.payment_succeeded con billing_reason=subscription_create
    debe notificar a Django /checkout/complete/ con period_start,
    period_end, date_cutoff y stripe_subscription_id.
    """
    from unittest.mock import patch, MagicMock
    from app.routers import webhooks
    from tests.conftest import test_engine, _make_invoice_event
    from app.models.plan import Plan
    from app.models.subscription import Subscription
    from sqlmodel import Session

    # Crear plan y suscripcion activa (checkout previo ya la activó)
    with Session(test_engine) as db:
        plan = Plan(
            code="CFDI_PRO", name="Test PRO", price=5000, currency="MXN",
            interval="month", billing_type="subscription",
            stripe_price_id="price_test", stripe_product_id="prod_test",
            is_active=True,
        )
        db.add(plan)
        db.commit()
        db.refresh(plan)

        sub = Subscription(
            user_id=1, plan_id=plan.id, status="active", provider="stripe",
            stripe_subscription_id="sub_test_inv",
        )
        db.add(sub)
        db.commit()
        sub_id = sub.id

    # Simular invoice.payment_succeeded con subscription_create
    event_dict = _make_invoice_event(
        sub_id,
        billing_code="CFDI_PRO",
        stripe_sub_id="sub_test_inv",
    )

    with patch("stripe.Webhook.construct_event", return_value=event_dict):
        with patch("app.routers.webhooks.notify_main_app") as mock_notify:
            with patch("app.routers.webhooks.engine", test_engine):
                response = client.post(
                    "/api/pagos/webhooks/stripe",
                    content='{"type": "invoice.payment_succeeded"}',
                    headers={
                        "stripe-signature": "t=123,v1=valida",
                        "Content-Type": "application/json",
                    },
                )
                assert response.status_code == 200
                mock_notify.assert_called_once()

                kwargs = mock_notify.call_args[1]
                assert kwargs.get("billing_code") == "CFDI_PRO"
                assert kwargs.get("subscription_id") == sub_id
                assert "period_start" in kwargs
                assert "period_end" in kwargs
                assert "date_cutoff" in kwargs
                assert kwargs.get("stripe_subscription_id") == "sub_test_inv"


def test_notify_main_app_reintenta_si_falla(client: TestClient):
    """notify_main_app debe reintentar si Django no responde."""
    from app.routers.webhooks import notify_main_app

    with patch("httpx.Client") as mock_client:
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Server Error"

        mock_instance = MagicMock()
        mock_instance.post.return_value = mock_response
        mock_client.return_value.__enter__.return_value = mock_instance

        result = notify_main_app(
            user_id=1,
            billing_code="CFDI_PRO",
            subscription_id=1,
        )

        assert result is False
        assert mock_instance.post.call_count == 3  # 3 reintentos
