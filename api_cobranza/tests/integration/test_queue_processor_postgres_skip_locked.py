"""Prueba de integración del locking real de PostgreSQL (SKIP LOCKED).

Requiere una base PostgreSQL dedicada de pruebas, por ejemplo:

    TEST_POSTGRES_URL=postgresql+psycopg://user:pass@localhost:5432/billing_test \
        pytest tests/integration/test_queue_processor_postgres_skip_locked.py -v

No se ejecuta por defecto. SQLite NO demuestra SKIP LOCKED.
"""

import os
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import create_engine, text
from sqlmodel import Session, SQLModel

from app.models.payment import WebhookNotificationQueue
from app.services import queue_processor

POSTGRES_URL = os.getenv("TEST_POSTGRES_URL")

pytestmark = pytest.mark.skipif(
    not POSTGRES_URL,
    reason="TEST_POSTGRES_URL no configurado (integración PostgreSQL)",
)


@pytest.fixture(scope="module")
def pg_engine():
    engine = create_engine(POSTGRES_URL, future=True)
    SQLModel.metadata.create_all(engine)
    yield engine
    engine.dispose()


def _make_item(engine, key: str) -> int:
    with Session(engine) as db:
        item = WebhookNotificationQueue(
            event_type="checkout_completed",
            subscription_id=1,
            user_id=1,
            billing_code="CFDI_PRO",
            payload={
                "event_type": "checkout_completed",
                "user_id": 1,
                "billing_code": "CFDI_PRO",
                "subscription_id": 1,
                "event_created": 1700000000,
            },
            status="pending",
            next_retry_at=datetime.now(timezone.utc) - timedelta(seconds=5),
            notification_key=key,
            source_event_id=key.split(":")[0],
        )
        db.add(item)
        db.commit()
        db.refresh(item)
        return item.id


def test_skip_locked_skips_row_locked_by_another_transaction(pg_engine):
    locked_id = _make_item(pg_engine, "evt_locked:checkout_completed")
    free_id = _make_item(pg_engine, "evt_free:checkout_completed")

    with Session(pg_engine) as blocker:
        blocker.execute(
            text("SELECT id FROM webhooknotificationqueue WHERE id = :id FOR UPDATE"),
            {"id": locked_id},
        )
        # La transacción sigue abierta: la fila está bloqueada.
        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(queue_processor, "engine", pg_engine)
            claimed = queue_processor.claim_pending_notifications(max_items=10)

        blocker.rollback()

    assert free_id in claimed
    assert locked_id not in claimed
