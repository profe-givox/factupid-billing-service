"""Procesador robusto de la cola de notificaciones (Outbox).

Garantías:
- claim corto con ``SELECT ... FOR UPDATE SKIP LOCKED`` en PostgreSQL;
- lease por fila para recuperar workers muertos;
- transporte HTTP fuera de la transacción/lock;
- backoff exponencial con tope;
- entrega at-least-once + idempotencia en Django.
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

import httpx
from sqlalchemy import and_, or_, update
from sqlmodel import Session, select

from app.core.config import settings
from app.db.session import engine
from app.models.payment import WebhookNotificationQueue
from app.routers.webhooks import notify_main_app, notify_subscription_event
from app.services import discord_alerts

logger = logging.getLogger(__name__)

DEFAULT_LEASE_SECONDS = 300
BASE_BACKOFF_SECONDS = 60
MAX_BACKOFF_SECONDS = 3600
HTTP_TIMEOUT_SECONDS = 10

# 4xx que sí pueden resolverse solos (auth rotada, rate limit, timeout de proxy).
RETRYABLE_4XX = {401, 403, 408, 425, 429}


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _as_aware(value: Optional[datetime]) -> Optional[datetime]:
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value


def next_retry_delay_seconds(retry_count: int) -> int:
    """1m, 2m, 4m, 8m, 16m, 32m, 60m (tope)."""
    exponent = max(int(retry_count), 1) - 1
    return min(BASE_BACKOFF_SECONDS * (2 ** exponent), MAX_BACKOFF_SECONDS)


def delivery_endpoint(event_type: str) -> str:
    """Destino Django existente. checkout va a /checkout/complete/, el resto a sync."""
    if event_type == "checkout_completed":
        return "/checkout/complete/"
    return "/subscription/sync/"


def _build_headers() -> dict:
    headers = {"Content-Type": "application/json"}
    if settings.COBRANZA_WEBHOOK_SECRET:
        headers["X-Webhook-Token"] = settings.COBRANZA_WEBHOOK_SECRET
    return headers


def _classify_response(resp) -> tuple[bool, bool, Optional[str], Optional[int]]:
    """Devuelve (success, retryable, error, status_code)."""
    status_code = getattr(resp, "status_code", None)
    if status_code is None:
        return False, True, "respuesta HTTP inválida", None

    if status_code < 400:
        try:
            body = resp.json()
        except Exception:
            body = None
        if isinstance(body, dict) and body.get("success") is False:
            return False, False, f"HTTP {status_code} success=false", status_code
        return True, False, None, status_code

    if status_code >= 500 or status_code in RETRYABLE_4XX:
        return False, True, f"HTTP {status_code}", status_code

    if 400 <= status_code < 500:
        return False, False, f"HTTP {status_code} no retriable", status_code

    return False, True, f"HTTP {status_code}", status_code


def _post_persisted_payload(
    event_type: str, payload: dict
) -> tuple[bool, bool, Optional[str], Optional[int]]:
    base_url = (settings.MAIN_APP_BASE or "").rstrip("/")
    if not base_url:
        return False, True, "MAIN_APP_BASE no configurado", None

    url = f"{base_url}{delivery_endpoint(event_type)}"
    try:
        with httpx.Client(timeout=HTTP_TIMEOUT_SECONDS) as client:
            resp = client.post(url, json=payload, headers=_build_headers())
        return _classify_response(resp)
    except httpx.TimeoutException as exc:
        return False, True, f"timeout: {exc}", None
    except httpx.TransportError as exc:
        return False, True, f"network: {exc}", None
    except Exception as exc:  # noqa: BLE001
        return False, True, f"error transporte: {exc}", None


def _payload_for_delivery(item: WebhookNotificationQueue) -> dict:
    """Envía el payload persistido. Solo rellena event_created si faltaba."""
    payload = dict(item.payload or {})
    if item.event_created and "event_created" not in payload:
        try:
            payload["event_created"] = int(_as_aware(item.event_created).timestamp())
        except Exception:
            pass
    return payload


def _is_legacy_incomplete_payload(payload: dict) -> bool:
    """Filas previas al outbox durable no guardaban payload completo."""
    return (
        not payload
        or "user_id" not in payload
        or "subscription_id" not in payload
    )


def _legacy_delivery(item: WebhookNotificationQueue, payload: dict) -> bool:
    event_created = payload.get("event_created")
    if event_created is None and item.event_created:
        try:
            event_created = int(_as_aware(item.event_created).timestamp())
        except Exception:
            event_created = None

    if item.event_type == "checkout_completed":
        return bool(
            notify_main_app(
                user_id=payload.get("user_id", item.user_id),
                billing_code=payload.get("billing_code", item.billing_code),
                subscription_id=payload.get("subscription_id", item.subscription_id),
                plan_id=payload.get("plan_id", item.plan_id),
                service_id=payload.get("service_id", item.service_id),
                date_cutoff=payload.get("date_cutoff", item.date_cutoff),
                period_start=payload.get("period_start"),
                period_end=payload.get("period_end"),
                stripe_subscription_id=payload.get("stripe_subscription_id"),
                event_created=event_created,
                stripe_event_id=item.source_event_id,
            )
        )

    return bool(
        notify_subscription_event(
            event_type=item.event_type,
            user_id=payload.get("user_id", item.user_id),
            billing_code=payload.get("billing_code", item.billing_code),
            subscription_id=payload.get("subscription_id", item.subscription_id),
            plan_id=payload.get("plan_id", item.plan_id),
            service_id=payload.get("service_id", item.service_id),
            date_cutoff=payload.get("date_cutoff", item.date_cutoff),
            period_start=payload.get("period_start"),
            period_end=payload.get("period_end"),
            canceled_at=payload.get("canceled_at"),
            cancel_at_period_end=payload.get("cancel_at_period_end"),
            stripe_subscription_id=payload.get("stripe_subscription_id"),
            full_payload=payload,
            stripe_event_id=item.source_event_id,
            event_created=event_created,
        )
    )


def claim_pending_notifications(
    max_items: int = 10,
    lease_seconds: int = DEFAULT_LEASE_SECONDS,
    now: Optional[datetime] = None,
) -> list[int]:
    """Selecciona y reclama filas de forma atómica y corta.

    PostgreSQL usa ``FOR UPDATE SKIP LOCKED``. En otros motores (tests SQLite)
    cae a un SELECT normal; el lease sigue evitando doble procesamiento lógico.
    """
    now = now or _utcnow()
    lease_until = now + timedelta(seconds=lease_seconds)
    claimed_ids: list[int] = []

    with Session(engine) as db:
        stmt = (
            select(WebhookNotificationQueue)
            .where(
                or_(
                    and_(
                        WebhookNotificationQueue.status == "pending",
                        or_(
                            WebhookNotificationQueue.next_retry_at.is_(None),
                            WebhookNotificationQueue.next_retry_at <= now,
                        ),
                    ),
                    and_(
                        WebhookNotificationQueue.status == "processing",
                        or_(
                            WebhookNotificationQueue.lease_expires_at.is_(None),
                            WebhookNotificationQueue.lease_expires_at <= now,
                        ),
                    ),
                )
            )
            .order_by(WebhookNotificationQueue.next_retry_at)
            .limit(max_items)
        )

        if db.get_bind().dialect.name == "postgresql":
            stmt = stmt.with_for_update(skip_locked=True)

        rows = db.exec(stmt).all()
        for item in rows:
            if item.retry_count >= item.max_retries:
                item.status = "failed"
                item.last_error = item.last_error or "max_retries alcanzado (lease recovery)"
                item.next_retry_at = None
                item.lease_expires_at = None
                db.add(item)
                continue

            item.status = "processing"
            item.retry_count += 1
            item.claimed_at = now
            item.last_attempt_at = now
            item.lease_expires_at = lease_until
            db.add(item)
            claimed_ids.append(item.id)

        db.commit()

    return claimed_ids


def _deliver_claimed(notification_id: int, now: Optional[datetime] = None) -> str:
    """Entrega una fila previamente reclamada. No mantiene locks durante HTTP."""
    now = now or _utcnow()

    with Session(engine) as db:
        item = db.get(WebhookNotificationQueue, notification_id)
        if not item or item.status != "processing":
            return "skipped"
        snapshot = {
            "id": item.id,
            "event_type": item.event_type,
            "payload": dict(item.payload or {}),
            "user_id": item.user_id,
            "billing_code": item.billing_code,
            "subscription_id": item.subscription_id,
            "plan_id": item.plan_id,
            "service_id": item.service_id,
            "date_cutoff": item.date_cutoff,
            "event_created": item.event_created,
            "source_event_id": item.source_event_id,
            "retry_count": item.retry_count,
            "max_retries": item.max_retries,
            "notification_key": item.notification_key,
            "status": item.status,
            "last_error": item.last_error,
            "next_retry_at": item.next_retry_at,
        }

    payload = dict(snapshot["payload"])
    if snapshot["event_created"] and "event_created" not in payload:
        try:
            payload["event_created"] = int(
                _as_aware(snapshot["event_created"]).timestamp()
            )
        except Exception:
            pass

    if _is_legacy_incomplete_payload(payload):
        legacy_item = WebhookNotificationQueue(
            id=snapshot["id"],
            event_type=snapshot["event_type"],
            subscription_id=snapshot["subscription_id"],
            user_id=snapshot["user_id"],
            billing_code=snapshot["billing_code"],
            plan_id=snapshot["plan_id"],
            service_id=snapshot["service_id"],
            date_cutoff=snapshot["date_cutoff"],
            event_created=snapshot["event_created"],
            source_event_id=snapshot["source_event_id"],
        )
        try:
            success = _legacy_delivery(legacy_item, payload)
            retryable = True
            error = None if success else "legacy delivery failed"
        except Exception as exc:  # noqa: BLE001
            success = False
            retryable = True
            error = f"legacy delivery error: {exc}"
    else:
        success, retryable, error, status_code = _post_persisted_payload(
            snapshot["event_type"], payload
        )
        if not success and error is None and status_code is not None:
            error = f"HTTP {status_code}"

    values: dict = {"last_attempt_at": now}
    if success:
        values.update(
            {
                "status": "completed",
                "completed_at": now,
                "lease_expires_at": None,
                "last_error": None,
            }
        )
        outcome = "succeeded"
    else:
        values.update(
            {
                "last_error": error,
                "lease_expires_at": None,
            }
        )
        if not retryable or snapshot["retry_count"] >= snapshot["max_retries"]:
            values.update(
                {
                    "status": "failed",
                    "next_retry_at": None,
                }
            )
            outcome = "expired"
        else:
            values.update(
                {
                    "status": "pending",
                    "next_retry_at": now
                    + timedelta(
                        seconds=next_retry_delay_seconds(snapshot["retry_count"])
                    ),
                }
            )
            outcome = "failed"

    with Session(engine) as db:
        result = db.execute(
            update(WebhookNotificationQueue)
            .where(
                WebhookNotificationQueue.id == notification_id,
                WebhookNotificationQueue.status == "processing",
            )
            .values(**values)
        )
        db.commit()
        if result.rowcount == 0:
            logger.warning(
                "Cola: fila %s ya no estaba en processing al terminar la entrega",
                notification_id,
            )
            return "skipped"

        # Alertas observabilidad (solo fuera de cambios DB/Stripe; nunca deben romper flujo)
        try:
            item_alert = db.get(WebhookNotificationQueue, notification_id)
            if item_alert:
                if outcome == "succeeded":
                    discord_alerts.alert_outbox_recovered(
                        queue_item=item_alert,
                        previous_failed_count=max(int(snapshot["retry_count"]) - 1, 0),
                    )
                elif outcome == "failed" and item_alert.status == "pending":
                    discord_alerts.alert_outbox_warning(queue_item=item_alert)
                elif outcome == "expired" and item_alert.status == "failed":
                    discord_alerts.alert_outbox_critical_failed(queue_item=item_alert)
        except Exception as exc:  # noqa: BLE001
            logger.debug("Alertas Discord ignoradas tras entrega: %s", exc)

    return outcome


def process_pending_notifications(max_items: int = 10) -> dict:
    """Reclama y procesa filas pendientes. Seguro con varios workers."""
    stats = {
        "processed": 0,
        "succeeded": 0,
        "failed": 0,
        "expired": 0,
        "skipped": 0,
    }

    claimed_ids = claim_pending_notifications(max_items=max_items)
    for notification_id in claimed_ids:
        stats["processed"] += 1
        try:
            outcome = _deliver_claimed(notification_id)
        except Exception as exc:  # noqa: BLE001
            logger.exception("Cola: error entregando fila %s", notification_id)
            with Session(engine) as db:
                result = db.execute(
                    update(WebhookNotificationQueue)
                    .where(
                        WebhookNotificationQueue.id == notification_id,
                        WebhookNotificationQueue.status == "processing",
                    )
                    .values(
                        status="pending",
                        last_error=str(exc),
                        lease_expires_at=None,
                        next_retry_at=_utcnow() + timedelta(seconds=BASE_BACKOFF_SECONDS),
                    )
                )
                db.commit()
            outcome = "failed" if result.rowcount else "skipped"

        if outcome == "succeeded":
            stats["succeeded"] += 1
        elif outcome == "expired":
            stats["expired"] += 1
        elif outcome == "failed":
            stats["failed"] += 1
        elif outcome == "skipped":
            stats["skipped"] += 1

    return stats
