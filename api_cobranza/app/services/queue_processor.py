from datetime import datetime, timezone
from sqlmodel import Session, select
from app.db.session import engine
from app.models.payment import WebhookNotificationQueue
from app.routers.webhooks import notify_main_app, notify_subscription_event


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
                # Routing por event_type:
                # - checkout_completed → notify_main_app() (endpoint legacy /checkout/complete/)
                # - cualquier otro → notify_subscription_event() (endpoint /subscription/sync/)
                if item.event_type == "checkout_completed":
                    # Reconstruir desde payload completo guardado en la cola.
                    # Esto preserva period_start, period_end, stripe_subscription_id
                    # y otros campos que se agreguen en el futuro.
                    payload = item.payload or {}
                    success = notify_main_app(
                        user_id=payload.get("user_id", item.user_id),
                        billing_code=payload.get("billing_code", item.billing_code),
                        subscription_id=payload.get("subscription_id", item.subscription_id),
                        plan_id=payload.get("plan_id", item.plan_id),
                        service_id=payload.get("service_id", item.service_id),
                        date_cutoff=payload.get("date_cutoff", item.date_cutoff),
                        period_start=payload.get("period_start"),
                        period_end=payload.get("period_end"),
                        stripe_subscription_id=payload.get("stripe_subscription_id"),
                    )
                else:
                    # Reconstruir payload desde los campos de la cola si no hay payload guardado
                    payload = item.payload or {}
                    success = notify_subscription_event(
                        event_type=item.event_type,
                        user_id=item.user_id,
                        billing_code=item.billing_code,
                        subscription_id=item.subscription_id,
                        plan_id=item.plan_id,
                        service_id=item.service_id,
                        date_cutoff=item.date_cutoff,
                        full_payload=payload,
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