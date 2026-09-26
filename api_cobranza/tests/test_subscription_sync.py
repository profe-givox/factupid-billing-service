"""Tests para notificaciones de suscripciones CFDI a Django.

Cubre:
- notify_subscription_event (éxito, reintentos, cola)
- handle_subscription_payment → subscription_renewed
- handle_subscription_deleted → subscription_canceled
- handle_subscription_updated → cancel_scheduled y plan_changed
- handle_invoice_payment_failed → past_due
- queue_processor routing por event_type
"""

from datetime import datetime, timezone, timedelta, date
from unittest.mock import patch, MagicMock
import time

import pytest
from sqlmodel import Session, select

from tests.conftest import test_engine
from app.models.plan import Plan
from app.models.subscription import Subscription
from app.models.payment import Payment, WebhookNotificationQueue
from app.routers.webhooks import (
    notify_subscription_event,
    handle_subscription_payment,
    handle_subscription_deleted,
    handle_subscription_updated,
    handle_invoice_payment_failed,
    _save_failed_notification,
)
from app.services.queue_processor import process_pending_notifications


# ── Tests de notify_subscription_event ──


class TestNotifySubscriptionEventSuccess:
    """T1: notify_subscription_event retorna True cuando Django responde 200."""

    def test_exito_200(self):
        with patch("httpx.Client") as mock_httpx:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.text = '{"success": true}'
            mock_instance = MagicMock()
            mock_instance.post.return_value = mock_response
            mock_httpx.return_value.__enter__ = MagicMock(return_value=mock_instance)
            mock_httpx.return_value.__exit__ = MagicMock(return_value=False)

            result = notify_subscription_event(
                event_type="subscription_renewed",
                user_id=1,
                billing_code="CFDI_PRO",
                subscription_id=1,
                period_start=date(2026, 8, 1),
                period_end=date(2026, 8, 31),
                date_cutoff=date(2026, 8, 31),
            )
            assert result is True
            assert mock_instance.post.call_count == 1

            # Verificar que la URL es /subscription/sync/
            call_args = mock_instance.post.call_args
            assert "/subscription/sync/" in call_args[0][0]

            # Verificar payload contiene event_type
            payload = call_args[1]["json"]
            assert payload["event_type"] == "subscription_renewed"
            assert "period_start" in payload
            assert "period_end" in payload


class TestNotifySubscriptionEventRetryOnFailure:
    """T2: notify_subscription_event reintenta 3 veces si Django falla."""

    def test_reintenta_3_veces(self):
        with patch("httpx.Client") as mock_httpx:
            mock_response = MagicMock()
            mock_response.status_code = 500
            mock_response.text = "Internal Server Error"
            mock_instance = MagicMock()
            mock_instance.post.return_value = mock_response
            mock_httpx.return_value.__enter__ = MagicMock(return_value=mock_instance)
            mock_httpx.return_value.__exit__ = MagicMock(return_value=False)

            with patch("app.routers.webhooks._save_failed_notification") as mock_save:
                with patch("app.routers.webhooks.time.sleep"):
                    result = notify_subscription_event(
                        event_type="subscription_canceled",
                        user_id=1,
                        billing_code="CFDI_PRO",
                        subscription_id=1,
                    )

                    assert result is False
                    assert mock_instance.post.call_count == 3
                    mock_save.assert_called_once()

                    # Verificar que se guardó con event_type correcto
                    call_kwargs = mock_save.call_args[1]
                    assert call_kwargs["event_type"] == "subscription_canceled"


class TestNotifySubscriptionEventSavesToQueue:
    """T3: notify_subscription_event guarda en cola con event_type al fallar."""

    def test_guarda_en_cola_con_event_type(self):
        with patch("httpx.Client") as mock_httpx:
            mock_response = MagicMock()
            mock_response.status_code = 503
            mock_response.text = "Service Unavailable"
            mock_instance = MagicMock()
            mock_instance.post.return_value = mock_response
            mock_httpx.return_value.__enter__ = MagicMock(return_value=mock_instance)
            mock_httpx.return_value.__exit__ = MagicMock(return_value=False)

            with patch("app.routers.webhooks.time.sleep"):
                with patch("app.routers.webhooks.engine", test_engine):
                    result = notify_subscription_event(
                        event_type="subscription_past_due",
                        user_id=42,
                        billing_code="CFDI_PRO",
                        subscription_id=7,
                    )

                    assert result is False

        with Session(test_engine) as db:
            item = db.exec(
                select(WebhookNotificationQueue).where(
                    WebhookNotificationQueue.subscription_id == 7
                )
            ).first()
            assert item is not None
            assert item.event_type == "subscription_past_due"
            assert item.user_id == 42
            assert item.status == "pending"


# ── Tests de handlers ──


class TestHandleSubscriptionPaymentNotifiesRenewed:
    """T4: handle_subscription_payment notifica subscription_renewed en renovaciones."""

    def test_renovacion_notifica_renewed(self, seed_plans_and_sub):
        data = seed_plans_and_sub
        sub_id = data["sub_id"]
        now_ts = int(time.time())

        # Crear invoice de renovación (billing_reason=subscription_cycle)
        invoice = {
            "id": "in_renewal_test",
            "billing_reason": "subscription_cycle",
            "amount_paid": 5000,
            "currency": "mxn",
            "status_transitions": {"paid_at": now_ts},
            "parent": {
                "subscription_details": {
                    "subscription": f"sub_stripe_{sub_id}",
                    "metadata": {"subscription_id": str(sub_id), "user_id": "1"},
                }
            },
            "lines": {
                "data": [
                    {
                        "period": {"start": now_ts, "end": now_ts + 30 * 86400},
                        "parent": {
                            "subscription_item_details": {
                                "subscription": f"sub_stripe_{sub_id}",
                            }
                        },
                    }
                ]
            },
        }

        with patch("app.routers.webhooks.engine", test_engine):
            with patch("app.routers.webhooks.notify_subscription_event") as mock_notify:
                handle_subscription_payment(invoice, {})

                mock_notify.assert_called_once()
                call_kwargs = mock_notify.call_args[1]
                assert call_kwargs["event_type"] == "subscription_renewed"
                assert call_kwargs["user_id"] == 1

    def test_primer_pago_no_notifica_renewed(self, seed_plans_and_sub):
        """El primer pago (subscription_create) NO debe notificar renewed."""
        data = seed_plans_and_sub
        sub_id = data["sub_id"]
        now_ts = int(time.time())

        invoice = {
            "id": "in_first_payment_test",
            "billing_reason": "subscription_create",
            "amount_paid": 5000,
            "currency": "mxn",
            "status_transitions": {"paid_at": now_ts},
            "parent": {
                "subscription_details": {
                    "subscription": f"sub_stripe_{sub_id}",
                    "metadata": {"subscription_id": str(sub_id), "user_id": "1"},
                }
            },
            "lines": {
                "data": [
                    {
                        "period": {"start": now_ts, "end": now_ts + 30 * 86400},
                        "parent": {
                            "subscription_item_details": {
                                "subscription": f"sub_stripe_{sub_id}",
                            }
                        },
                    }
                ]
            },
        }

        with patch("app.routers.webhooks.engine", test_engine):
            with patch("app.routers.webhooks.notify_subscription_event") as mock_notify:
                handle_subscription_payment(invoice, {})
                mock_notify.assert_not_called()


class TestHandleSubscriptionDeletedNotifiesCanceled:
    """T5: handle_subscription_deleted notifica subscription_canceled."""

    def test_deleted_notifica_canceled(self, seed_plans_and_sub):
        data = seed_plans_and_sub
        sub_id = data["sub_id"]

        # Activar la suscripción primero
        with Session(test_engine) as db:
            sub = db.get(Subscription, sub_id)
            sub.status = "active"
            sub.stripe_subscription_id = f"sub_stripe_{sub_id}"
            db.add(sub)
            db.commit()

        now_ts = int(time.time())
        delete_data = {
            "id": f"sub_stripe_{sub_id}",
            "canceled_at": now_ts,
        }

        with patch("app.routers.webhooks.engine", test_engine):
            with patch("app.routers.webhooks.notify_subscription_event") as mock_notify:
                handle_subscription_deleted(delete_data)

                mock_notify.assert_called_once()
                call_kwargs = mock_notify.call_args[1]
                assert call_kwargs["event_type"] == "subscription_canceled"
                assert call_kwargs["user_id"] == 1


class TestHandleSubscriptionUpdatedCancelAtPeriodEnd:
    """T6: handle_subscription_updated notifica subscription_cancel_scheduled."""

    def test_cancel_at_period_end_notifica(self, seed_plans_and_sub):
        data = seed_plans_and_sub
        sub_id = data["sub_id"]

        # Activar la suscripción y asignar stripe_id
        with Session(test_engine) as db:
            sub = db.get(Subscription, sub_id)
            sub.status = "active"
            sub.stripe_subscription_id = f"sub_stripe_{sub_id}"
            db.add(sub)
            db.commit()

        update_data = {
            "id": f"sub_stripe_{sub_id}",
            "status": "active",
            "cancel_at_period_end": True,
            "items": {
                "data": [
                    {
                        "price": {"id": "price_pro_test"},
                    }
                ]
            },
        }

        with patch("app.routers.webhooks.engine", test_engine):
            with patch("app.routers.webhooks.notify_subscription_event") as mock_notify:
                handle_subscription_updated(update_data)

                mock_notify.assert_called_once()
                call_kwargs = mock_notify.call_args[1]
                assert call_kwargs["event_type"] == "subscription_cancel_scheduled"
                assert call_kwargs["cancel_at_period_end"] is True


class TestHandleSubscriptionUpdatedPlanChange:
    """T7: handle_subscription_updated notifica subscription_plan_changed."""

    def test_plan_change_notifica(self, seed_plans_and_sub):
        data = seed_plans_and_sub
        sub_id = data["sub_id"]

        # Activar la suscripción con plan PRO y stripe_id
        with Session(test_engine) as db:
            sub = db.get(Subscription, sub_id)
            sub.status = "active"
            sub.stripe_subscription_id = f"sub_stripe_{sub_id}"
            db.add(sub)
            db.commit()

        update_data = {
            "id": f"sub_stripe_{sub_id}",
            "status": "active",
            "cancel_at_period_end": False,
            "items": {
                "data": [
                    {
                        "price": {"id": "price_ent_test"},
                    }
                ]
            },
        }

        with patch("app.routers.webhooks.engine", test_engine):
            with patch("app.routers.webhooks.notify_subscription_event") as mock_notify:
                handle_subscription_updated(update_data)

                mock_notify.assert_called_once()
                call_kwargs = mock_notify.call_args[1]
                assert call_kwargs["event_type"] == "subscription_plan_changed"
                assert call_kwargs["user_id"] == 1


class TestHandleInvoicePaymentFailedPastDueAndNotifies:
    """T8: handle_invoice_payment_failed actualiza status y notifica subscription_past_due."""

    def test_past_due_status_y_notifica(self, seed_plans_and_sub):
        data = seed_plans_and_sub
        sub_id = data["sub_id"]

        # Activar la suscripción
        with Session(test_engine) as db:
            sub = db.get(Subscription, sub_id)
            sub.status = "active"
            sub.stripe_subscription_id = f"sub_stripe_{sub_id}"
            db.add(sub)
            db.commit()

        invoice = {
            "id": "in_failed_test",
            "billing_reason": "subscription_cycle",
            "subscription": f"sub_stripe_{sub_id}",
        }

        with patch("app.routers.webhooks.engine", test_engine):
            with patch("app.routers.webhooks.notify_subscription_event") as mock_notify:
                handle_invoice_payment_failed(invoice, {})

                # Verificar que la suscripción se actualizó a past_due
                with Session(test_engine) as db:
                    updated = db.get(Subscription, sub_id)
                    assert updated.status == "past_due"

                # Verificar notificación
                mock_notify.assert_called_once()
                call_kwargs = mock_notify.call_args[1]
                assert call_kwargs["event_type"] == "subscription_past_due"


# ── Tests de queue_processor routing ──


class TestQueueProcessorRoutesCheckoutCompleted:
    """T9: queue_processor envía checkout_completed a notify_main_app."""

    def test_checkout_completed_a_notify_main_app(self, seed_plans_and_sub):
        # Crear item en cola con event_type=checkout_completed
        with Session(test_engine) as db:
            item = WebhookNotificationQueue(
                event_type="checkout_completed",
                subscription_id=1,
                user_id=1,
                billing_code="CFDI_PRO",
                status="pending",
                next_retry_at=datetime.now(timezone.utc) - timedelta(minutes=1),
            )
            db.add(item)
            db.commit()

        with patch("app.services.queue_processor.notify_main_app") as mock_main:
            with patch("app.services.queue_processor.notify_subscription_event") as mock_sub:
                with patch("app.services.queue_processor.engine", test_engine):
                    mock_main.return_value = True
                    stats = process_pending_notifications(max_items=10)

                    assert stats["succeeded"] == 1
                    mock_main.assert_called_once()
                    mock_sub.assert_not_called()


class TestQueueProcessorRoutesSubscriptionEvent:
    """T10: queue_processor envía eventos de suscripción a notify_subscription_event."""

    def test_subscription_renewed_a_notify_subscription_event(self, seed_plans_and_sub):
        # Crear item en cola con event_type=subscription_renewed
        with Session(test_engine) as db:
            item = WebhookNotificationQueue(
                event_type="subscription_renewed",
                subscription_id=1,
                user_id=1,
                billing_code="CFDI_PRO",
                payload={
                    "event_type": "subscription_renewed",
                    "user_id": 1,
                    "billing_code": "CFDI_PRO",
                },
                status="pending",
                next_retry_at=datetime.now(timezone.utc) - timedelta(minutes=1),
            )
            db.add(item)
            db.commit()

        with patch("app.services.queue_processor.notify_main_app") as mock_main:
            with patch("app.services.queue_processor.notify_subscription_event") as mock_sub:
                with patch("app.services.queue_processor.engine", test_engine):
                    mock_sub.return_value = True
                    stats = process_pending_notifications(max_items=10)

                    assert stats["succeeded"] == 1
                    mock_sub.assert_called_once()
                    mock_main.assert_not_called()

                    # Verificar que se pasó el event_type correcto
                    call_kwargs = mock_sub.call_args[1]
                    assert call_kwargs["event_type"] == "subscription_renewed"
