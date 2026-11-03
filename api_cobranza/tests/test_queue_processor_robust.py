"""Tests del queue processor robusto (claim, lease, backoff, routing).

Los tests de este archivo corren sobre SQLite y validan la lógica de claim
lógico, lease y políticas. El locking real de PostgreSQL (SKIP LOCKED) se
prueba aparte en tests/integration/test_queue_processor_postgres_skip_locked.py.
"""

from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

import httpx
import pytest
from sqlmodel import Session, select

from tests.conftest import test_engine
from app.models.payment import Payment, WebhookNotificationQueue
from app.models.subscription import Subscription
from app.routers.webhooks import _mark_notification_completed, enqueue_notification
from app.services import queue_processor
from app.services.queue_processor import (
    _deliver_claimed,
    _post_persisted_payload,
    claim_pending_notifications,
    delivery_endpoint,
    next_retry_delay_seconds,
    process_pending_notifications,
)


class FakeResponse:
    def __init__(self, status_code: int, body=None):
        self.status_code = status_code
        self._body = body

    def json(self):
        if isinstance(self._body, Exception):
            raise self._body
        return self._body


def _now():
    return datetime.now(timezone.utc)


def make_queue_item(**overrides) -> int:
    payload = {
        "event_type": "checkout_completed",
        "user_id": 1,
        "billing_code": "CFDI_PRO",
        "subscription_id": 1,
        "plan_id": 1,
        "event_created": 1700000000,
    }
    payload.update(overrides.pop("payload", {}))

    values = {
        "event_type": "checkout_completed",
        "subscription_id": 1,
        "user_id": 1,
        "billing_code": "CFDI_PRO",
        "plan_id": 1,
        "payload": payload,
        "status": "pending",
        "next_retry_at": _now() - timedelta(seconds=5),
        "source_event_id": "evt_test_1",
        "event_created": datetime.fromtimestamp(1700000000, tz=timezone.utc),
        "notification_key": "evt_test_1:checkout_completed",
    }
    values.update(overrides)

    with Session(test_engine) as db:
        item = WebhookNotificationQueue(**values)
        db.add(item)
        db.commit()
        db.refresh(item)
        return item.id


def get_item(item_id: int) -> WebhookNotificationQueue:
    with Session(test_engine) as db:
        return db.get(WebhookNotificationQueue, item_id)


def run_processor(max_items: int = 10):
    with patch("app.services.queue_processor.engine", test_engine):
        with patch("app.services.queue_processor.settings.MAIN_APP_BASE", "http://django.test"):
            return process_pending_notifications(max_items=max_items)


def patch_http(status_code: int = 200, body=None, side_effect=None):
    client_cls = MagicMock()
    client = client_cls.return_value.__enter__.return_value
    if side_effect is not None:
        client.post.side_effect = side_effect
    else:
        client.post.return_value = FakeResponse(status_code, body or {"success": True})
    return patch("app.services.queue_processor.httpx.Client", client_cls), client


# Q1
def test_q1_pending_success_marks_completed():
    item_id = make_queue_item()
    ctx, client = patch_http(200, {"success": True})
    with ctx:
        stats = run_processor()

    item = get_item(item_id)
    assert stats == {
        "processed": 1,
        "succeeded": 1,
        "failed": 0,
        "expired": 0,
        "skipped": 0,
    }
    assert item.status == "completed"
    assert item.completed_at is not None
    assert item.lease_expires_at is None
    assert client.post.call_args[0][0].endswith("/checkout/complete/")


# Q2
def test_q2_network_unreachable_stays_pending_with_future_retry():
    item_id = make_queue_item()
    ctx, _ = patch_http(side_effect=httpx.ConnectError("unreachable"))
    with ctx:
        run_processor()

    item = get_item(item_id)
    assert item.status == "pending"
    assert item.retry_count == 1
    assert item.last_error and "network" in item.last_error
    assert item.next_retry_at is not None
    assert item.next_retry_at.replace(tzinfo=timezone.utc) > _now()
    assert item.lease_expires_at is None


# Q3
def test_q3_timeout_stays_pending():
    item_id = make_queue_item()
    ctx, _ = patch_http(side_effect=httpx.ReadTimeout("timeout"))
    with ctx:
        run_processor()

    item = get_item(item_id)
    assert item.status == "pending"
    assert item.retry_count == 1
    assert "timeout" in item.last_error


# Q4
def test_q4_http_500_stays_pending():
    item_id = make_queue_item()
    ctx, _ = patch_http(500, {"detail": "boom"})
    with ctx:
        run_processor()

    item = get_item(item_id)
    assert item.status == "pending"
    assert item.retry_count == 1
    assert "500" in item.last_error


# Q5
def test_q5_stale_event_marks_completed():
    item_id = make_queue_item()
    ctx, _ = patch_http(200, {"success": True, "skipped": "stale_event"})
    with ctx:
        run_processor()

    item = get_item(item_id)
    assert item.status == "completed"


# Q6
def test_q6_claim_excludes_row_already_claimed():
    item_id = make_queue_item()
    now = _now()
    with patch("app.services.queue_processor.engine", test_engine):
        first = claim_pending_notifications(max_items=10, lease_seconds=300, now=now)
        second = claim_pending_notifications(max_items=10, lease_seconds=300, now=now)

    assert first == [item_id]
    assert second == []
    assert get_item(item_id).retry_count == 1


# Q7
def test_q7_two_workers_claim_different_rows():
    first_id = make_queue_item(notification_key="evt_a:checkout_completed")
    second_id = make_queue_item(notification_key="evt_b:checkout_completed")
    now = _now()
    with patch("app.services.queue_processor.engine", test_engine):
        worker_a = claim_pending_notifications(max_items=1, now=now)
        worker_b = claim_pending_notifications(max_items=1, now=now)

    assert worker_a == [first_id]
    assert worker_b == [second_id]


# Q8
def test_q8_worker_dies_after_claim_row_recoverable():
    item_id = make_queue_item()
    now = _now()
    with patch("app.services.queue_processor.engine", test_engine):
        claimed = claim_pending_notifications(max_items=1, lease_seconds=60, now=now)
        recovered = claim_pending_notifications(
            max_items=1, lease_seconds=60, now=now + timedelta(seconds=61)
        )

    assert claimed == [item_id]
    assert recovered == [item_id]
    assert get_item(item_id).status == "processing"


# Q9
def test_q9_redelivery_after_django_processed_but_worker_died():
    item_id = make_queue_item()
    now = _now()
    calls = []

    def fake_post(event_type, payload):
        calls.append(payload)
        return True, False, None, 200

    with patch("app.services.queue_processor.engine", test_engine):
        claim_pending_notifications(max_items=1, lease_seconds=30, now=now)
    with patch("app.services.queue_processor._post_persisted_payload", side_effect=fake_post):
        # Django procesó, pero el worker "muere" antes de marcar completed.
        queue_processor._post_persisted_payload("checkout_completed", {"user_id": 1})
        with patch("app.services.queue_processor.engine", test_engine):
            reclaimed = claim_pending_notifications(
                max_items=1, lease_seconds=30, now=now + timedelta(seconds=31)
            )
            assert reclaimed == [item_id]
            outcome = _deliver_claimed(item_id)

    assert len(calls) == 2
    assert outcome == "succeeded"
    assert get_item(item_id).status == "completed"


# Q10
def test_q10_notification_key_is_single_logical_row():
    payload = {"user_id": 1, "billing_code": "CFDI_PRO", "subscription_id": 1}
    with Session(test_engine) as db:
        first = enqueue_notification(
            db,
            notification_key="evt_dup:checkout_completed",
            event_type="checkout_completed",
            payload=payload,
            source_event_id="evt_dup",
            event_created=1700000000,
            subscription_id=1,
            user_id=1,
            billing_code="CFDI_PRO",
        )
        second = enqueue_notification(
            db,
            notification_key="evt_dup:checkout_completed",
            event_type="checkout_completed",
            payload=payload,
            source_event_id="evt_dup",
            event_created=1700000000,
            subscription_id=1,
            user_id=1,
            billing_code="CFDI_PRO",
        )
        db.commit()
        rows = db.exec(select(WebhookNotificationQueue)).all()

    assert first.id == second.id
    assert len(rows) == 1


# Q11
def test_q11_delayed_event_keeps_original_event_created():
    item_id = make_queue_item(
        payload={"event_created": 1699999999},
        event_created=datetime.fromtimestamp(1699999999, tz=timezone.utc),
    )
    ctx, client = patch_http(200, {"success": True})
    with ctx:
        run_processor()

    sent_payload = client.post.call_args[1]["json"]
    assert sent_payload["event_created"] == 1699999999
    assert get_item(item_id).status == "completed"


# Q12
def test_q12_source_event_id_is_preserved():
    item_id = make_queue_item(source_event_id="evt_preserved_123")
    ctx, _ = patch_http(200, {"success": True})
    with ctx:
        run_processor()

    assert get_item(item_id).source_event_id == "evt_preserved_123"


# Q13
def test_q13_checkout_routes_to_checkout_complete():
    assert delivery_endpoint("checkout_completed") == "/checkout/complete/"


# Q14
@pytest.mark.parametrize(
    "event_type",
    ["subscription_renewed", "subscription_canceled", "subscription_past_due", "cfdi_overage_billed"],
)
def test_q14_subscription_events_route_to_sync(event_type):
    assert delivery_endpoint(event_type) == "/subscription/sync/"


# Q15
@pytest.mark.parametrize(
    "status_code,expected_status",
    [
        (400, "failed"),
        (401, "pending"),
        (403, "pending"),
        (404, "failed"),
        (409, "failed"),
        (422, "failed"),
        (429, "pending"),
    ],
)
def test_q15_http_4xx_policy(status_code, expected_status):
    item_id = make_queue_item()
    ctx, _ = patch_http(status_code, {"detail": "error"})
    with ctx:
        run_processor()

    item = get_item(item_id)
    assert item.status == expected_status
    if expected_status == "failed":
        assert item.next_retry_at is None
    else:
        assert item.next_retry_at is not None


# Q16
def test_q16_two_schedulers_do_not_duplicate_delivery():
    make_queue_item()
    ctx, client = patch_http(200, {"success": True})
    with ctx:
        first = run_processor()
        second = run_processor()

    assert first["succeeded"] == 1
    assert second["processed"] == 0
    assert client.post.call_count == 1


# Q17 - R2: una identidad ORM stale no debe dejar lease en una fila completed.
def test_q17_immediate_completion_clears_lease_with_stale_identity():
    item_id = make_queue_item()

    with Session(test_engine) as stale_db:
        stale_item = stale_db.get(WebhookNotificationQueue, item_id)
        assert stale_item.lease_expires_at is None

        with patch("app.services.queue_processor.engine", test_engine):
            claimed = claim_pending_notifications(max_items=1, lease_seconds=300)

        assert claimed == [item_id]
        _mark_notification_completed(stale_db, stale_item.notification_key)
        stale_db.commit()

    item = get_item(item_id)
    assert item.status == "completed"
    assert item.lease_expires_at is None


# Q18 - R2/R3: si la entrega inmediata completa durante el POST, el worker
# pierde la carrera y debe contabilizarse como skipped, no como succeeded/failed.
def test_q18_race_completed_by_immediate_delivery_counts_skipped():
    item_id = make_queue_item()
    item_key = get_item(item_id).notification_key

    def complete_immediately(event_type, payload):
        with Session(test_engine) as db:
            _mark_notification_completed(db, item_key)
            db.commit()
        return True, False, None, 200

    with (
        patch("app.services.queue_processor.engine", test_engine),
        patch(
            "app.services.queue_processor.settings.MAIN_APP_BASE",
            "http://django.test",
        ),
        patch(
            "app.services.queue_processor._post_persisted_payload",
            side_effect=complete_immediately,
        ),
    ):
        stats = process_pending_notifications(max_items=1)

    item = get_item(item_id)
    assert stats == {
        "processed": 1,
        "succeeded": 0,
        "failed": 0,
        "expired": 0,
        "skipped": 1,
    }
    assert item.status == "completed"
    assert item.lease_expires_at is None


def test_backoff_formula_is_capped():
    assert next_retry_delay_seconds(1) == 60
    assert next_retry_delay_seconds(2) == 120
    assert next_retry_delay_seconds(3) == 240
    assert next_retry_delay_seconds(4) == 480
    assert next_retry_delay_seconds(7) == 3600
    assert next_retry_delay_seconds(20) == 3600


# Incidente original (integración conceptual con SQLite)
def test_original_incident_pending_survives_network_and_delivers_later(seed_plans_and_sub):
    sub_id = seed_plans_and_sub["sub_id"]
    with Session(test_engine) as db:
        plan_id = db.get(Subscription, sub_id).plan_id

    with Session(test_engine) as db:
        sub = db.get(Subscription, sub_id)
        sub.status = "active"
        sub.stripe_subscription_id = "sub_incident_1"
        db.add(sub)
        db.add(
            Payment(
                subscription_id=sub_id,
                provider="stripe",
                provider_payment_id="pi_incident_1",
                amount=5000,
                currency="MXN",
                status="succeeded",
            )
        )
        db.commit()

    item_id = make_queue_item(
        subscription_id=sub_id,
        plan_id=plan_id,
        payload={
            "event_type": "checkout_completed",
            "user_id": 1,
            "billing_code": "CFDI_PRO",
            "subscription_id": sub_id,
            "plan_id": plan_id,
            "event_created": 1700000000,
        },
        notification_key="evt_incident:checkout_completed",
        source_event_id="evt_incident",
    )

    # 3. Primer HTTP falla con network unreachable.
    ctx, _ = patch_http(side_effect=httpx.ConnectError("django down"))
    with ctx:
        first = run_processor()
    assert first["failed"] == 1
    assert get_item(item_id).status == "pending"

    # 4-5. El worker original desaparece; otro processor encuentra PENDING.
    with Session(test_engine) as db:
        item = db.get(WebhookNotificationQueue, item_id)
        item.next_retry_at = _now() - timedelta(seconds=1)
        db.add(item)
        db.commit()

    # 6-8. Django vuelve; el processor entrega el payload persistido.
    ctx, client = patch_http(200, {"success": True})
    with ctx:
        second = run_processor()

    assert second["succeeded"] == 1
    assert client.post.call_args[1]["json"]["subscription_id"] == sub_id

    # 9. Resultado final.
    item = get_item(item_id)
    assert item.status == "completed"
    with Session(test_engine) as db:
        assert db.get(Subscription, sub_id).status == "active"
        payment = db.exec(select(Payment).where(Payment.provider_payment_id == "pi_incident_1")).first()
        assert payment is not None and payment.status == "succeeded"


def test_recovery_alert_reports_previous_failed_attempts():
    """Recovery solo aplica tras >=2 intentos fallidos previos.

    `retry_count` se incrementa al reclamar, por lo que los intentos previos
    son `retry_count - 1` (no 1/0 como antes).
    """
    item_id = make_queue_item(retry_count=2, max_retries=5)

    with (
        patch("app.services.queue_processor.engine", test_engine),
        patch(
            "app.services.queue_processor._post_persisted_payload",
            return_value=(True, False, None, 200),
        ),
        patch("app.services.queue_processor.discord_alerts.alert_outbox_recovered") as recovered,
        patch("app.services.queue_processor.discord_alerts.alert_outbox_warning"),
        patch("app.services.queue_processor.discord_alerts.alert_outbox_critical_failed"),
    ):
        claimed = claim_pending_notifications(max_items=1)
        assert claimed == [item_id]
        outcome = _deliver_claimed(item_id)

    assert outcome == "succeeded"
    recovered.assert_called_once()
    assert recovered.call_args.kwargs["previous_failed_count"] == 2
