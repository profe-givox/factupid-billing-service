"""Tests Billing: Fase 7C.3/7C.4 — Servicio main_app_overage, scheduler e invoice.created.

Cubre:
1. trigger_main_app_overage_reporting llama a Django con token correcto.
2. scheduler ejecuta trigger_main_app_overage_reporting.
3. scheduler respeta ENABLE_OVERAGE_REPORTING_SCHEDULER=false.
4. invoice.created de suscripción dispara trigger con mode=invoice_created.
5. invoice.created sin subscription no dispara trigger.
6. Si Django falla, invoice.created no rompe el webhook.
"""

from datetime import date
from unittest.mock import patch, MagicMock

import pytest

from sqlmodel import Session

from tests.conftest import test_engine
from app.models.plan import Plan
from app.models.subscription import Subscription

WEBHOOK_URL = "/api/pagos/webhooks/stripe"
WEBHOOK_HEADERS = {
    "stripe-signature": "t=123,v1=valida",
    "Content-Type": "application/json",
}


def _seed_subscription_for_invoice_created(
    user_id=42,
    stripe_subscription_id="sub_stripe_inv_created_1",
):
    """Crea plan + subscription para tests de invoice.created."""
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
            status="active",
            provider="stripe",
            stripe_subscription_id=stripe_subscription_id,
            stripe_customer_id="cus_inv_created_1",
            start_date=date(2026, 8, 1),
            end_date=date(2026, 8, 31),
        )
        db.add(sub)
        db.commit()
        db.refresh(sub)
        return sub.id


def _make_invoice_created_event(
    invoice_id="in_draft_123",
    stripe_sub_id="sub_stripe_inv_created_1",
    billing_reason="subscription_cycle",
):
    """Crea un evento invoice.created para una suscripción."""
    return {
        "id": f"evt_{invoice_id}",
        "type": "invoice.created",
        "data": {
            "object": {
                "id": invoice_id,
                "status": "draft",
                "subscription": stripe_sub_id,
                "billing_reason": billing_reason,
                "amount_due": 5000,
                "currency": "mxn",
            }
        },
    }


# ---------------------------------------------------------------------------
# 1. trigger_main_app_overage_reporting llama a Django con token correcto
# ---------------------------------------------------------------------------


class TestTriggerMainAppOverage:
    """Tests del servicio trigger_main_app_overage_reporting."""

    def test_llama_a_django_con_token_y_payload(self):
        """Verifica URL, headers y payload enviados a Django."""
        from app.services.main_app_overage import trigger_main_app_overage_reporting

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "application/json"}
        mock_response.json.return_value = {
            "success": True, "reported": 2, "failed": 0,
        }

        with patch("app.services.main_app_overage.settings") as mock_settings, \
             patch("app.services.main_app_overage.httpx.Client") as mock_client_cls:
            mock_settings.MAIN_APP_BASE = "http://django:8000"
            mock_settings.COBRANZA_WEBHOOK_SECRET = "test_secret_7c3"

            mock_client = MagicMock()
            mock_client.__enter__ = MagicMock(return_value=mock_client)
            mock_client.__exit__ = MagicMock(return_value=False)
            mock_client.post.return_value = mock_response
            mock_client_cls.return_value = mock_client

            result = trigger_main_app_overage_reporting(
                mode="invoice_created",
                billing_subscription_id=42,
                stripe_subscription_id="sub_xyz",
            )

        assert result is True
        call_args = mock_client.post.call_args
        assert "/subscription/report-overages/" in call_args.args[0]
        assert call_args.kwargs["headers"]["X-Webhook-Token"] == "test_secret_7c3"
        payload = call_args.kwargs["json"]
        assert payload["mode"] == "invoice_created"
        assert payload["billing_subscription_id"] == 42
        assert payload["stripe_subscription_id"] == "sub_xyz"

    def test_falla_django_retorna_false(self):
        """Si Django falla, retorna False sin excepción."""
        from app.services.main_app_overage import trigger_main_app_overage_reporting

        with patch("app.services.main_app_overage.settings") as mock_settings, \
             patch("app.services.main_app_overage.httpx.Client") as mock_client_cls:
            mock_settings.MAIN_APP_BASE = "http://django:8000"
            mock_settings.COBRANZA_WEBHOOK_SECRET = "tok"

            mock_client = MagicMock()
            mock_client.__enter__ = MagicMock(return_value=mock_client)
            mock_client.__exit__ = MagicMock(return_value=False)
            mock_client.post.side_effect = Exception("Connection refused")
            mock_client_cls.return_value = mock_client

            result = trigger_main_app_overage_reporting(mode="periodic")

        assert result is False

    def test_main_app_base_no_configurado(self):
        """Si MAIN_APP_BASE no está, retorna False."""
        from app.services.main_app_overage import trigger_main_app_overage_reporting

        with patch("app.services.main_app_overage.settings") as mock_settings:
            mock_settings.MAIN_APP_BASE = None

            result = trigger_main_app_overage_reporting(mode="periodic")

        assert result is False


# ---------------------------------------------------------------------------
# 2-3. Scheduler jobs
# ---------------------------------------------------------------------------


class TestOvareportingSchedulerJob:
    """Tests del job periódico de overage reporting."""

    def test_job_llama_trigger(self):
        """El job llama trigger_main_app_overage_reporting con mode=periodic."""
        from app.scheduler import _trigger_overage_reporting_job

        with patch("app.scheduler.trigger_main_app_overage_reporting") as mock_trigger:
            mock_trigger.return_value = True
            _trigger_overage_reporting_job()
            mock_trigger.assert_called_once_with(mode="periodic")

    def test_job_handles_exception(self):
        """El job maneja excepciones sin crash."""
        from app.scheduler import _trigger_overage_reporting_job

        with patch("app.scheduler.trigger_main_app_overage_reporting") as mock_trigger:
            mock_trigger.side_effect = RuntimeError("DB error")
            # No debe lanzar excepción
            _trigger_overage_reporting_job()

    def test_scheduler_incluye_job_cuando_habilitado(self):
        """El scheduler incluye el job de overage reporting cuando está habilitado."""
        from app.scheduler import start_scheduler, shutdown_scheduler, scheduler

        start_scheduler(
            interval_minutes=5,
            overage_interval_minutes=15,
            enable_overage_reporting=True,
        )
        assert scheduler.running
        job_ids = [j.id for j in scheduler.get_jobs()]
        assert "trigger_overage_reporting" in job_ids
        assert "process_pending_notifications" in job_ids
        shutdown_scheduler()

    def test_scheduler_excluye_job_cuando_deshabilitado(self):
        """El scheduler NO incluye overage reporting cuando está deshabilitado."""
        from app.scheduler import start_scheduler, shutdown_scheduler, scheduler

        start_scheduler(
            interval_minutes=5,
            overage_interval_minutes=15,
            enable_overage_reporting=False,
        )
        assert scheduler.running
        job_ids = [j.id for j in scheduler.get_jobs()]
        assert "trigger_overage_reporting" not in job_ids
        assert "process_pending_notifications" in job_ids
        shutdown_scheduler()


# ---------------------------------------------------------------------------
# 4-6. invoice.created webhook handler
# ---------------------------------------------------------------------------


class TestInvoiceCreatedWebhook:
    """Tests del handler invoice.created en el webhook de Stripe."""

    def test_invoice_created_dispara_trigger_con_parametros_correctos(self):
        """Verifica mode, billing_subscription_id y stripe_subscription_id."""
        sub_id = _seed_subscription_for_invoice_created(
            stripe_subscription_id="sub_stripe_param_check",
        )

        event = _make_invoice_created_event(
            invoice_id="in_params_1",
            stripe_sub_id="sub_stripe_param_check",
            billing_reason="subscription_cycle",
        )

        with patch("app.routers.webhooks.trigger_main_app_overage_reporting") as mock_trigger, \
             patch("app.routers.webhooks.engine", test_engine):
            mock_trigger.return_value = True

            from fastapi.testclient import TestClient
            from app.main import app
            with TestClient(app) as client:
                with patch("stripe.Webhook.construct_event", return_value=event):
                    resp = client.post(
                        WEBHOOK_URL,
                        content='{"type": "invoice.created"}',
                        headers=WEBHOOK_HEADERS,
                    )

            assert resp.status_code == 200
            mock_trigger.assert_called_once()
            call_kwargs = mock_trigger.call_args.kwargs
            assert call_kwargs["mode"] == "invoice_created"
            assert call_kwargs["stripe_subscription_id"] == "sub_stripe_param_check"
            assert call_kwargs["billing_subscription_id"] == sub_id

    def test_invoice_created_sin_subscription_no_dispara(self):
        """invoice.created sin campo subscription no dispara trigger."""
        event = {
            "id": "evt_no_sub",
            "type": "invoice.created",
            "data": {
                "object": {
                    "id": "in_no_sub",
                    "status": "draft",
                    "subscription": None,
                    "billing_reason": "manual",
                }
            },
        }

        with patch("app.routers.webhooks.trigger_main_app_overage_reporting") as mock_trigger, \
             patch("app.routers.webhooks.engine", test_engine):
            mock_trigger.return_value = True

            from fastapi.testclient import TestClient
            from app.main import app
            with TestClient(app) as client:
                with patch("stripe.Webhook.construct_event", return_value=event):
                    resp = client.post(
                        WEBHOOK_URL,
                        content='{"type": "invoice.created"}',
                        headers=WEBHOOK_HEADERS,
                    )

            assert resp.status_code == 200
            mock_trigger.assert_not_called()

    def test_django_falla_no_rompe_webhook(self):
        """Si Django falla, invoice.created sigue respondiendo OK a Stripe."""
        sub_id = _seed_subscription_for_invoice_created(
            stripe_subscription_id="sub_stripe_fail_django",
        )

        event = _make_invoice_created_event(
            invoice_id="in_fail_django",
            stripe_sub_id="sub_stripe_fail_django",
            billing_reason="subscription_cycle",
        )

        with patch("app.routers.webhooks.trigger_main_app_overage_reporting") as mock_trigger, \
             patch("app.routers.webhooks.engine", test_engine):
            mock_trigger.return_value = False  # Django falló

            from fastapi.testclient import TestClient
            from app.main import app
            with TestClient(app) as client:
                with patch("stripe.Webhook.construct_event", return_value=event):
                    resp = client.post(
                        WEBHOOK_URL,
                        content='{"type": "invoice.created"}',
                        headers=WEBHOOK_HEADERS,
                    )

            # El webhook responde OK a Stripe aunque Django falle
            assert resp.status_code == 200
            assert resp.json()["status"] == "ok"
