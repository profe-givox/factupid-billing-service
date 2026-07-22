from datetime import datetime, timezone
from sqlmodel import Session, select
from app.db.session import engine
from app.models.payment import WebhookNotificationQueue
from app.routers.webhooks import notify_main_app


def process_pending_notifications(max_items: int = 10) -> dict:
    """Procesa notificaciones pendientes en la cola. Retorna estadísticas."""
    stats = {"processed": 0, "succeeded": 0, "failed": 0, "expired": 0}

    with Session(engine) as db:
        pending = db.exec(
            select(WebhookNotificationQueue)
            .where(
                WebhookNotificationQueue.status == "pending",
                WebhookNotificationQueue.next_retry_at <= datetime.now(timezone.utc),
            )
            .limit(max_items)
        ).all()

        for item in pending:
            stats["processed"] += 1
            try:
                success = notify_main_app(
                    user_id=item.user_id,
                    billing_code=item.billing_code,
                    subscription_id=item.subscription_id,
                    plan_id=item.plan_id,
                    service_id=item.service_id,
                    date_cutoff=item.date_cutoff,
                )

                if success:
                    item.status = "completed"
                    stats["succeeded"] += 1
                else:
                    item.retry_count += 1
                    item.last_attempt_at = datetime.now(timezone.utc)
                    if item.retry_count >= item.max_retries:
                        item.status = "failed"
                        stats["expired"] += 1
                    else:
                        # Backoff: 2^retry_count minutos
                        import datetime as dt
                        item.next_retry_at = datetime.now(timezone.utc) + dt.timedelta(
                            minutes=2 ** item.retry_count
                        )
                        stats["failed"] += 1

            except Exception as exc:
                item.retry_count += 1
                item.last_error = str(exc)
                item.last_attempt_at = datetime.now(timezone.utc)
                if item.retry_count >= item.max_retries:
                    item.status = "failed"
                stats["failed"] += 1

            db.add(item)

        db.commit()

    return stats