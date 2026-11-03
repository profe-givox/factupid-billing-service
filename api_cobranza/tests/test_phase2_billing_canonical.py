"""Fase 2: activación CFDI canónica desde invoice.payment_succeeded."""

from datetime import date, datetime, timezone
from unittest.mock import patch

from sqlmodel import Session, select

from app.models.payment import Payment, WebhookNotificationQueue
from app.models.plan import Plan
from app.models.subscription import Subscription
from app.routers.webhooks import (
    handle_checkout_completed,
    handle_subscription_payment,
)
from app.services.queue_processor import process_pending_notifications
from tests.conftest import (
    _make_checkout_event,
    _make_invoice_event,
    test_engine,
)


def _outbox_rows():
    with Session(test_engine) as db:
        return db.exec(select(WebhookNotificationQueue)).all()


def _sub(sub_id):
    with Session(test_engine) as db:
        return db.get(Subscription, sub_id)


def _payments(sub_id):
    with Session(test_engine) as db:
        return db.exec(
            select(Payment).where(Payment.subscription_id == sub_id)
        ).all()


def _checkout(event):
    with patch("app.routers.webhooks.engine", test_engine):
        with patch("app.routers.webhooks.notify_main_app") as notify:
            handle_checkout_completed(event["data"]["object"], event)
    return notify


def _invoice(event, notify_result=True):
    with patch("app.routers.webhooks.engine", test_engine):
        with patch(
            "app.routers.webhooks.notify_main_app",
            return_value=notify_result,
        ) as notify:
            handle_subscription_payment(event["data"]["object"], event)
    return notify


def test_checkout_paid_cfdi_does_not_emit_incomplete_or_partial_activation(
    seed_plans_and_sub,
):
    sub_id = seed_plans_and_sub["sub_id"]
    event = _make_checkout_event(sub_id)

    notify = _checkout(event)

    notify.assert_not_called()
    assert _outbox_rows() == []
    assert _sub(sub_id).status == "active"


def test_checkout_then_invoice_emits_exactly_one_complete_activation(
    seed_plans_and_sub,
):
    sub_id = seed_plans_and_sub["sub_id"]
    checkout = _make_checkout_event(sub_id)
    invoice = _make_invoice_event(sub_id)

    _checkout(checkout)
    assert _outbox_rows() == []

    notify = _invoice(invoice)

    notify.assert_called_once()
    rows = _outbox_rows()
    assert len(rows) == 1
    row = rows[0]
    assert row.event_type == "checkout_completed"
    assert row.status == "completed"
    assert row.payload["period_start"] is not None
    assert row.payload["period_end"] is not None
    assert row.payload["date_cutoff"] == row.payload["period_end"]
    assert row.payload["source_event_type"] == "invoice.payment_succeeded"
    assert row.payload["invoice_id"] == invoice["data"]["object"]["id"]
    assert _sub(sub_id).status == "active"
    assert len(_payments(sub_id)) == 1


def test_invoice_then_checkout_still_emits_exactly_one_activation(
    seed_plans_and_sub,
):
    sub_id = seed_plans_and_sub["sub_id"]
    invoice = _make_invoice_event(sub_id)
    checkout = _make_checkout_event(sub_id)

    _invoice(invoice)
    after_invoice = _outbox_rows()
    assert len(after_invoice) == 1

    notify = _checkout(checkout)

    notify.assert_not_called()
    assert len(_outbox_rows()) == 1
    assert _outbox_rows()[0].id == after_invoice[0].id
    assert _sub(sub_id).status == "active"


def test_invoice_replay_same_event_does_not_duplicate_or_redeliver(
    seed_plans_and_sub,
):
    sub_id = seed_plans_and_sub["sub_id"]
    event = _make_invoice_event(sub_id)

    first = _invoice(event)
    second = _invoice(event)

    assert first.call_count == 1
    assert second.call_count == 0
    assert len(_outbox_rows()) == 1
    assert len(_payments(sub_id)) == 1


def test_invoice_replay_different_event_id_keeps_one_business_row(
    seed_plans_and_sub,
):
    sub_id = seed_plans_and_sub["sub_id"]
    invoice_id = "in_business_key_1"
    first_event = _make_invoice_event(sub_id, invoice_id=invoice_id)
    second_event = _make_invoice_event(sub_id, invoice_id=invoice_id)
    first_event["id"] = "evt_business_key_1"
    second_event["id"] = "evt_business_key_2"

    _invoice(first_event)
    second = _invoice(second_event)

    assert second.call_count == 0
    rows = _outbox_rows()
    assert len(rows) == 1
    assert rows[0].notification_key.startswith(
        f"subscription:{sub_id}:checkout_completed:"
    )
    assert len(_payments(sub_id)) == 1


def test_existing_payment_without_outbox_is_repaired_from_invoice_period(
    seed_plans_and_sub,
):
    sub_id = seed_plans_and_sub["sub_id"]
    event = _make_invoice_event(sub_id, invoice_id="in_repair_1")

    with Session(test_engine) as db:
        db.add(
            Payment(
                subscription_id=sub_id,
                provider="stripe",
                provider_payment_id="in_repair_1",
                amount=5000,
                currency="mxn",
                status="succeeded",
            )
        )
        db.commit()

    notify = _invoice(event)

    notify.assert_called_once()
    rows = _outbox_rows()
    assert len(rows) == 1
    assert rows[0].status == "completed"
    assert rows[0].payload["period_start"] is not None
    assert rows[0].payload["period_end"] is not None
    assert rows[0].payload["date_cutoff"] == rows[0].payload["period_end"]
    assert len(_payments(sub_id)) == 1
    assert _sub(sub_id).status == "active"


def test_existing_payment_with_completed_outbox_is_not_redelivered(
    seed_plans_and_sub,
):
    sub_id = seed_plans_and_sub["sub_id"]
    invoice_id = "in_repair_completed"
    event = _make_invoice_event(sub_id, invoice_id=invoice_id)

    _invoice(event)
    replay = _invoice(event)

    replay.assert_not_called()
    assert len(_outbox_rows()) == 1


def test_invoice_without_period_does_not_create_payment_or_activation(
    seed_plans_and_sub,
):
    sub_id = seed_plans_and_sub["sub_id"]
    event = _make_invoice_event(
        sub_id,
        lines={
            "data": [
                {
                    "parent": {
                        "subscription_item_details": {
                            "subscription": f"sub_stripe_{sub_id}",
                        }
                    }
                }
            ]
        },
    )

    notify = _invoice(event)

    notify.assert_not_called()
    assert _outbox_rows() == []
    assert _payments(sub_id) == []


def test_immediate_success_marks_outbox_completed_and_worker_skips_it(
    seed_plans_and_sub,
):
    sub_id = seed_plans_and_sub["sub_id"]
    event = _make_invoice_event(sub_id)

    _invoice(event, notify_result=True)
    assert _outbox_rows()[0].status == "completed"

    with patch("app.services.queue_processor.engine", test_engine):
        stats = process_pending_notifications()

    assert stats["processed"] == 0
    assert len(_outbox_rows()) == 1


def test_cfdi_free_checkout_keeps_legacy_non_subscription_activation():
    with Session(test_engine) as db:
        plan = Plan(
            code="CFDI_FREE",
            name="Free",
            price=0,
            currency="MXN",
            interval=None,
            billing_type="one_time",
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
            start_date=date(2026, 10, 1),
            end_date=date(2026, 10, 31),
        )
        db.add(sub)
        db.commit()
        db.refresh(sub)
        sub_id = sub.id

    event = _make_checkout_event(sub_id, billing_code="CFDI_FREE")
    notify = _checkout(event)

    notify.assert_called_once()
    assert _sub(sub_id).status == "active"
    rows = _outbox_rows()
    assert len(rows) == 1
    assert rows[0].status == "completed"


def test_recompra_after_cancel_emits_new_period_for_new_subscription(
    seed_plans_and_sub,
):
    old_sub_id = seed_plans_and_sub["sub_id"]

    with Session(test_engine) as db:
        old = db.get(Subscription, old_sub_id)
        old.status = "canceled"
        old.end_date = date(2026, 10, 15)
        db.add(old)

        pro = db.exec(select(Plan).where(Plan.code == "CFDI_PRO")).first()
        new = Subscription(
            user_id=1,
            plan_id=pro.id,
            status="pending",
            provider="stripe",
        )
        db.add(new)
        db.commit()
        db.refresh(new)
        new_sub_id = new.id

    future_ts = int(datetime(2026, 11, 1, tzinfo=timezone.utc).timestamp())
    event = _make_invoice_event(
        new_sub_id,
        invoice_id="in_recompra_1",
        lines={
            "data": [
                {
                    "period": {
                        "start": future_ts,
                        "end": future_ts + 30 * 86400,
                    },
                    "parent": {
                        "subscription_item_details": {
                            "subscription": f"sub_stripe_{new_sub_id}",
                        }
                    },
                }
            ]
        },
    )

    _invoice(event)

    rows = _outbox_rows()
    assert len(rows) == 1
    assert rows[0].subscription_id == new_sub_id
    assert rows[0].payload["period_start"] == "2026-11-01"
    assert rows[0].payload["date_cutoff"] == rows[0].payload["period_end"]
    assert _sub(new_sub_id).status == "active"
