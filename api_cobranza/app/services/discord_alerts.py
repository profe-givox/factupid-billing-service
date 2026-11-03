"""Servicio de alertas Discord para observabilidad del Outbox.

REUTILIZA lógica segura: solo lectura, try/except, nunca afecta el flujo principal.
No envía secretos. Soporta deduplicación por clave lógica.
"""

import json
import logging
from datetime import datetime, timedelta, timezone
from typing import Any

import httpx

from app.core.config import settings

log = logging.getLogger(__name__)

_MAX_CONTENT_LENGTH = 1800
# Evitar spam entre workers: se persiste en memoria por proceso; la deduplicación
# "at-least-once" sigue estando protegida por la política (solo WARNING>=umbral y FAILED).
_LAST_ALERT_AT: dict[str, datetime] = {}


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _enabled() -> bool:
    if not getattr(settings, "DISCORD_ALERTS_ENABLED", False):
        return False
    if not getattr(settings, "DISCORD_WEBHOOK_URL", None):
        return False
    return True


def _mask_sensitive(text: Any) -> str:
    if text is None:
        return ""
    s = str(text)
    # No exponer headers/tokens/claves
    for key in ("COBRANZA_WEBHOOK_SECRET", "STRIPE_SECRET_KEY", "DISCORD_WEBHOOK_URL", "X-Webhook-Token", "Authorization"):
        if key in s:
            s = s.replace(key, "[REDACTED]")
    return s[:500]


def _should_send(key: str, cooldown_seconds: int) -> bool:
    now = _utcnow()
    last = _LAST_ALERT_AT.get(key)
    if last and (now - last) < timedelta(seconds=cooldown_seconds):
        return False
    _LAST_ALERT_AT[key] = now
    return True


def _send_discord(title: str, description: str, fields: list[dict[str, Any]]) -> bool:
    """Envía alerta. Nunca lanza excepción."""
    try:
        if not _enabled():
            return False
        url = settings.DISCORD_WEBHOOK_URL
        if not url:
            return False

        safe_fields = []
        for f in fields:
            safe_fields.append(
                {
                    "name": _mask_sensitive(f.get("name", ""))[:256],
                    "value": _mask_sensitive(f.get("value", ""))[:1024],
                    "inline": bool(f.get("inline", True)),
                }
            )

        embed = {
            "title": title[:256],
            "description": description[:_MAX_CONTENT_LENGTH],
            "color": 0xFFA500,
            "fields": safe_fields,
            "timestamp": _utcnow().isoformat().replace("+00:00", "Z"),
        }
        payload = {"embeds": [embed]}

        with httpx.Client(timeout=3.0) as client:
            resp = client.post(url, json=payload)
        if resp.status_code >= 400:
            log.warning("Discord webhook respondió %s", resp.status_code)
            return False
        return True
    except Exception as exc:  # noqa: BLE001
        log.debug("Discord alert falló (ignorado): %s", exc)
        return False


def alert_outbox_warning(
    *,
    queue_item,
    reason: str = "retry_threshold",
) -> bool:
    """WARNING cuando retry_count alcanza umbral significativo y aún puede reintentarse."""
    try:
        if not _enabled():
            return False
        threshold = int(getattr(settings, "DISCORD_ALERT_WARNING_RETRY_COUNT", 3))
        retry_count = int(getattr(queue_item, "retry_count", 0))
        if retry_count < threshold:
            return False
        if getattr(queue_item, "status", None) == "failed":
            return False

        key = f"warning:{getattr(queue_item,'id')}:{threshold}"
        cooldown = int(getattr(settings, "DISCORD_ALERTS_COOLDOWN_SECONDS", 900))
        if not _should_send(key, cooldown):
            return False

        fields = [
            {"name": "Notification ID", "value": getattr(queue_item, "id")},
            {"name": "notification_key", "value": getattr(queue_item, "notification_key") or "NULL"},
            {"name": "event_type", "value": getattr(queue_item, "event_type")},
            {"name": "user_id", "value": getattr(queue_item, "user_id")},
            {"name": "billing_subscription_id", "value": getattr(queue_item, "subscription_id")},
            {"name": "retry_count", "value": retry_count},
            {"name": "max_retries", "value": getattr(queue_item, "max_retries")},
            {"name": "status", "value": getattr(queue_item, "status")},
            {"name": "source_event_id", "value": getattr(queue_item, "source_event_id") or "NULL"},
            {"name": "last_error", "value": _mask_sensitive(getattr(queue_item, "last_error"))},
            {"name": "next_retry_at", "value": getattr(queue_item, "next_retry_at")},
        ]
        return _send_discord(
            title="Billing Outbox - WARNING: reintentos elevados",
            description=f"notificación con reintentos >= {threshold}. reason={reason}. No se toma acción sobre BD/Stripe.",
            fields=fields,
        )
    except Exception as exc:  # noqa: BLE001
        log.debug("alert_outbox_warning ignorado: %s", exc)
        return False


def alert_outbox_critical_failed(
    *,
    queue_item,
    reason: str = "max_retries_exceeded",
) -> bool:
    """CRITICAL cuando pasa a failed tras alcanzar max_retries."""
    try:
        if not _enabled():
            return False
        if not bool(getattr(settings, "DISCORD_ALERT_CRITICAL_ON_FAILED", True)):
            return False
        if getattr(queue_item, "status", None) != "failed":
            return False

        key = f"critical:{getattr(queue_item,'id')}:failed"
        cooldown = int(getattr(settings, "DISCORD_ALERTS_COOLDOWN_SECONDS", 900))
        if not _should_send(key, cooldown):
            return False

        fields = [
            {"name": "Notification ID", "value": getattr(queue_item, "id")},
            {"name": "notification_key", "value": getattr(queue_item, "notification_key") or "NULL"},
            {"name": "event_type", "value": getattr(queue_item, "event_type")},
            {"name": "user_id", "value": getattr(queue_item, "user_id")},
            {"name": "billing_subscription_id", "value": getattr(queue_item, "subscription_id")},
            {"name": "retry_count", "value": getattr(queue_item, "retry_count")},
            {"name": "max_retries", "value": getattr(queue_item, "max_retries")},
            {"name": "status", "value": "failed"},
            {"name": "source_event_id", "value": getattr(queue_item, "source_event_id") or "NULL"},
            {"name": "last_error", "value": _mask_sensitive(getattr(queue_item, "last_error"))},
            {"name": "completed_at", "value": getattr(queue_item, "completed_at")},
        ]
        return _send_discord(
            title="Billing Outbox - CRITICAL: marcado como FAILED",
            description="Se agotaron reintentos. Requiere revisión. Observabilidad únicamente.",
            fields=fields,
        )
    except Exception as exc:  # noqa: BLE001
        log.debug("alert_outbox_critical_failed ignorado: %s", exc)
        return False


def alert_outbox_recovered(
    *,
    queue_item,
    previous_failed_count: int = 0,
) -> bool:
    """Recuperación opcional para evitar ruido."""
    try:
        if not _enabled():
            return False
        if not bool(getattr(settings, "DISCORD_ALERT_ON_RECOVERY", True)):
            return False
        if getattr(queue_item, "status", None) != "completed":
            return False
        if previous_failed_count < 2:
            return False

        key = f"recovered:{getattr(queue_item,'id')}"
        cooldown = int(getattr(settings, "DISCORD_ALERTS_COOLDOWN_SECONDS", 900))
        if not _should_send(key, cooldown):
            return False

        fields = [
            {"name": "Notification ID", "value": getattr(queue_item, "id")},
            {"name": "notification_key", "value": getattr(queue_item, "notification_key") or "NULL"},
            {"name": "event_type", "value": getattr(queue_item, "event_type")},
            {"name": "billing_subscription_id", "value": getattr(queue_item, "subscription_id")},
            {"name": "retry_count", "value": getattr(queue_item, "retry_count")},
            {"name": "source_event_id", "value": getattr(queue_item, "source_event_id") or "NULL"},
            {"name": "completed_at", "value": getattr(queue_item, "completed_at")},
        ]
        return _send_discord(
            title="Billing Outbox - RECOVERY: notificación completada tras fallos",
            description="Observabilidad únicamente; sin impacto en BD/Stripe.",
            fields=fields,
        )
    except Exception as exc:  # noqa: BLE001
        log.debug("alert_outbox_recovered ignorado: %s", exc)
        return False
