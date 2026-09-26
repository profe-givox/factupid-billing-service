"""Tests para WebhookNotificationQueue."""

from datetime import datetime, timezone
from sqlmodel import Session, select

from tests.conftest import test_engine
from app.models.payment import WebhookNotificationQueue
from app.routers.webhooks import _save_failed_notification
from unittest.mock import patch


class TestSaveFailedNotification:
    """T8: _save_failed_notification guarda en la cola correctamente."""

    def test_guarda_en_cola(self, client):
        with patch("app.routers.webhooks.engine", test_engine):
            _save_failed_notification(
                user_id=42,
                billing_code="CFDI_PRO",
                subscription_id=7,
                plan_id=3,
                last_error="HTTP 500: Server Error",
            )

        with Session(test_engine) as db:
            items = db.exec(
                select(WebhookNotificationQueue).where(
                    WebhookNotificationQueue.subscription_id == 7
                )
            ).all()
            assert len(items) == 1
            item = items[0]
            assert item.user_id == 42
            assert item.billing_code == "CFDI_PRO"
            assert item.status == "pending"
            assert item.retry_count == 0
            assert item.max_retries == 10
            assert item.last_error == "HTTP 500: Server Error"
            assert item.payload["user_id"] == 42
            assert item.next_retry_at is not None

    def test_guarda_con_date_cutoff(self, client):
        cutoff = datetime(2026, 8, 15, tzinfo=timezone.utc)

        with patch("app.routers.webhooks.engine", test_engine):
            _save_failed_notification(
                user_id=99,
                billing_code="CFDI_ENTERPRISE",
                subscription_id=15,
                date_cutoff=cutoff,
                last_error="Timeout",
            )

        with Session(test_engine) as db:
            item = db.exec(
                select(WebhookNotificationQueue).where(
                    WebhookNotificationQueue.subscription_id == 15
                )
            ).first()
            assert item is not None
            assert item.billing_code == "CFDI_ENTERPRISE"
            assert "2026-08-15" in item.date_cutoff
