"""Tests para el scheduler de cola de notificaciones y endpoint health/queue."""

from datetime import datetime, timezone, timedelta
from unittest.mock import patch, MagicMock

import pytest
from sqlmodel import Session, select

from tests.conftest import test_engine
from app.models.payment import WebhookNotificationQueue
from app.scheduler import (
    _process_pending_notifications_job,
    start_scheduler,
    shutdown_scheduler,
    scheduler,
)
from app.services.queue_processor import process_pending_notifications


class TestHealthQueueEndpoint:
    """Tests del endpoint GET /health/queue."""

    def _clean_queue(self):
        with Session(test_engine) as db:
            for item in db.exec(select(WebhookNotificationQueue)).all():
                db.delete(item)
            db.commit()

    def test_returns_queue_stats_empty(self, client):
        """Cola vacia retorna zeros."""
        self._clean_queue()
        with patch("app.main.engine", test_engine):
            resp = client.get("/health/queue")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert data["queue"]["total"] == 0
        assert data["queue"]["pending"] == 0
        assert data["queue"]["failed"] == 0
        assert data["queue"]["completed"] == 0

    def test_counts_pending_items(self, client):
        """Cuenta items pending en la cola."""
        with Session(test_engine) as db:
            for i in range(3):
                item = WebhookNotificationQueue(
                    event_type="subscription_renewed",
                    subscription_id=1,
                    user_id=1,
                    billing_code="CFDI_PRO",
                    payload={"event_type": "subscription_renewed"},
                    status="pending",
                    next_retry_at=datetime.now(timezone.utc) - timedelta(minutes=1),
                )
                db.add(item)
            db.commit()

        with patch("app.main.engine", test_engine):
            resp = client.get("/health/queue")
        assert resp.status_code == 200
        data = resp.json()
        assert data["queue"]["total"] == 3
        assert data["queue"]["pending"] == 3

    def test_counts_failed_items(self, client):
        """Cuenta items failed en la cola."""
        with Session(test_engine) as db:
            item = WebhookNotificationQueue(
                event_type="checkout_completed",
                subscription_id=1,
                user_id=1,
                billing_code="CFDI_PRO",
                payload={},
                status="failed",
                retry_count=3,
                last_error="Timeout",
            )
            db.add(item)
            db.commit()

        with patch("app.main.engine", test_engine):
            resp = client.get("/health/queue")
        assert resp.status_code == 200
        data = resp.json()
        assert data["queue"]["total"] == 1
        assert data["queue"]["failed"] == 1
        assert data["queue"]["pending"] == 0

    def test_counts_completed_items(self, client):
        """Cuenta items completed en la cola."""
        self._clean_queue()
        with Session(test_engine) as db:
            for i in range(2):
                db.add(WebhookNotificationQueue(
                    event_type="checkout_completed",
                    subscription_id=1,
                    user_id=1,
                    billing_code="CFDI_PRO",
                    payload={},
                    status="completed",
                ))
            db.add(WebhookNotificationQueue(
                event_type="subscription_renewed",
                subscription_id=1,
                user_id=1,
                billing_code="CFDI_PRO",
                payload={"event_type": "subscription_renewed"},
                status="pending",
                next_retry_at=datetime.now(timezone.utc) - timedelta(minutes=1),
            ))
            db.commit()

        with patch("app.main.engine", test_engine):
            resp = client.get("/health/queue")
        assert resp.status_code == 200
        data = resp.json()
        assert data["queue"]["total"] == 3
        assert data["queue"]["completed"] == 2
        assert data["queue"]["pending"] == 1

    def test_mixed_statuses(self, client):
        """Mezcla de statuses en la cola."""
        self._clean_queue()
        with Session(test_engine) as db:
            statuses = ["pending", "completed", "failed", "pending"]
            for s in statuses:
                db.add(WebhookNotificationQueue(
                    event_type="checkout_completed",
                    subscription_id=1,
                    user_id=1,
                    billing_code="CFDI_PRO",
                    payload={},
                    status=s,
                    next_retry_at=datetime.now(timezone.utc) - timedelta(minutes=1),
                ))
            db.commit()

        with patch("app.main.engine", test_engine):
            resp = client.get("/health/queue")
        assert resp.status_code == 200
        data = resp.json()
        assert data["queue"]["total"] == 4
        assert data["queue"]["pending"] == 2
        assert data["queue"]["completed"] == 1
        assert data["queue"]["failed"] == 1


class TestSchedulerJob:
    """Tests del job periodico _process_pending_notifications_job."""

    def test_job_calls_process_pending(self):
        """El job llama process_pending_notifications."""
        with patch("app.scheduler.process_pending_notifications") as mock_proc:
            mock_proc.return_value = {"processed": 0, "succeeded": 0, "failed": 0, "expired": 0}
            _process_pending_notifications_job()
            mock_proc.assert_called_once_with(max_items=20)

    def test_job_logs_when_items_processed(self):
        """El job loggea cuando procesa items."""
        with patch("app.scheduler.process_pending_notifications") as mock_proc:
            mock_proc.return_value = {"processed": 3, "succeeded": 2, "failed": 1, "expired": 0}
            with patch("app.scheduler.logger") as mock_logger:
                _process_pending_notifications_job()
                mock_logger.info.assert_called_once()
                assert mock_logger.info.call_args[0][1] == 3

    def test_job_no_log_when_nothing_processed(self):
        """El job NO loggea cuando no hay nada que procesar."""
        with patch("app.scheduler.process_pending_notifications") as mock_proc:
            mock_proc.return_value = {"processed": 0, "succeeded": 0, "failed": 0, "expired": 0}
            with patch("app.scheduler.logger") as mock_logger:
                _process_pending_notifications_job()
                mock_logger.info.assert_not_called()

    def test_job_handles_exception(self):
        """El job maneja excepciones sin crash."""
        with patch("app.scheduler.process_pending_notifications") as mock_proc:
            mock_proc.side_effect = RuntimeError("DB error")
            with patch("app.scheduler.logger") as mock_logger:
                _process_pending_notifications_job()
                mock_logger.error.assert_called_once()
                assert "DB error" in str(mock_logger.error.call_args[0][1])


class TestSchedulerLifecycle:
    """Tests de start/shutdown del scheduler."""

    def test_start_and_shutdown(self):
        """Iniciar y detener el scheduler funciona sin errores."""
        start_scheduler(interval_minutes=5)
        assert scheduler.running
        shutdown_scheduler()
        assert not scheduler.running

    def test_start_with_custom_interval(self):
        """El scheduler acepta intervalo personalizado."""
        start_scheduler(interval_minutes=10)
        assert scheduler.running
        jobs = scheduler.get_jobs()
        job_ids = [j.id for j in jobs]
        assert "process_pending_notifications" in job_ids
        shutdown_scheduler()

    def test_shutdown_is_safe_if_not_running(self):
        """Shutdown no falla si el scheduler no esta corriendo."""
        shutdown_scheduler()  # no debe lanzar excepcion
