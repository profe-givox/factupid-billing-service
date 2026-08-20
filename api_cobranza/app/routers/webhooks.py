import logging
import time
import stripe
import httpx
from datetime import datetime, timezone
from fastapi import APIRouter, Request, HTTPException, status
from sqlmodel import Session, select

from app.core.config import settings
from app.db.session import get_session, engine
from app.models.subscription import Subscription
from app.models.payment import WebhookNotificationQueue
from app.services.stripe_service import release_stripe_schedule_if_possible
from app.services.main_app_overage import trigger_main_app_overage_reporting

router = APIRouter(prefix="/webhooks", tags=["webhooks"])

stripe.api_key = settings.STRIPE_SECRET_KEY

logger = logging.getLogger(__name__)

def _resolve_billing_code_for_subscription(db, subscription, fallback_billing_code=None):
    """
    Resuelve el billing_code que se enviará a Django.

    Prioridad:
    1. Código recibido desde metadata/evento, si existe.
    2. Código del plan asociado a subscription.plan_id.
    3. Cadena vacía si no se pudo resolver.
    """
    if fallback_billing_code:
        value = str(fallback_billing_code).strip()
        if value:
            return value

    if not subscription or not getattr(subscription, "plan_id", None):
        return ""

    from app.models.plan import Plan

    plan = db.get(Plan, subscription.plan_id)
    if not plan:
        return ""

    return (
        getattr(plan, "code", None)
        or getattr(plan, "billing_code", None)
        or ""
    )

@router.post("/stripe")
async def stripe_webhook(
    request: Request,
):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    if not sig_header:
        raise HTTPException(status_code=400, detail="Missing Stripe signature")

    try:
        event = stripe.Webhook.construct_event(
            payload=payload,
            sig_header=sig_header,
            secret=settings.STRIPE_ENDPOINT_SECRET,
        )
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid payload")

    # Evento principal
    if event["type"] == "checkout.session.completed":
        handle_checkout_completed(event["data"]["object"])

    #Pago único
    elif event["type"] == "payment_intent.succeeded":
        handle_one_time_payment(event["data"]["object"], event)
    # Pago suscripción exitoso
    elif event["type"] == "invoice.payment_succeeded":
        handle_subscription_payment(event["data"]["object"], event)
    # Cancelación
    elif event["type"] == "customer.subscription.deleted":
        handle_subscription_deleted(event["data"]["object"])
    # FALLO DE PAGO (renovación)
    elif event["type"] == "invoice.payment_failed":
        handle_invoice_payment_failed(event["data"]["object"], event)
    # Cambio de estado de suscripción
    elif event["type"] == "customer.subscription.updated":
        handle_subscription_updated(event["data"]["object"])
    # Fase 7C.4: Último sync de excedentes antes del cobro
    elif event["type"] == "invoice.created":
        handle_invoice_created(event["data"]["object"])

    return {"status": "ok"}

def _save_failed_notification(
    user_id: int,
    billing_code: str,
    subscription_id: int,
    plan_id: int | None = None,
    service_id: int | None = None,
    date_cutoff=None,
    last_error: str | None = None,
    event_type: str = "checkout_completed",
    full_payload: dict | None = None,
    period_start=None,
    period_end=None,
    stripe_subscription_id: str | None = None,
) -> None:
    """Guarda una notificacion fallida en la cola de reintentos."""
    try:
        with Session(engine) as db:
            payload = full_payload or {
                "user_id": user_id,
                "billing_code": billing_code,
                "plan_code": billing_code,
                "subscription_id": subscription_id,
            }
            if plan_id is not None:
                payload.setdefault("plan_id", plan_id)
            if service_id is not None:
                payload.setdefault("service_id", service_id)
            if date_cutoff:
                payload.setdefault(
                    "date_cutoff",
                    date_cutoff.isoformat() if hasattr(date_cutoff, "isoformat") else str(date_cutoff),
                )
            # Guardar period_start/period_end/stripe_subscription_id
            # para que se repliquen correctamente desde la cola
            if period_start:
                payload.setdefault(
                    "period_start",
                    period_start.isoformat() if hasattr(period_start, "isoformat") else str(period_start),
                )
            if period_end:
                payload.setdefault(
                    "period_end",
                    period_end.isoformat() if hasattr(period_end, "isoformat") else str(period_end),
                )
            if stripe_subscription_id:
                payload.setdefault("stripe_subscription_id", stripe_subscription_id)

            queue_item = WebhookNotificationQueue(
                event_type=event_type,
                subscription_id=subscription_id,
                user_id=user_id,
                billing_code=billing_code,
                plan_id=plan_id,
                service_id=service_id,
                date_cutoff=str(date_cutoff) if date_cutoff else None,
                payload=payload,
                status="pending",
                next_retry_at=datetime.now(timezone.utc),
                last_error=last_error,
            )
            db.add(queue_item)
            db.commit()
    except Exception as exc:
        logger.error("Error guardando notificacion fallida en cola: %s", exc)


def notify_main_app(
    *,
    user_id: int,
    billing_code: str,
    subscription_id: int,
    plan_id: int | None = None,
    service_id: int | None = None,
    date_cutoff=None,
    period_start=None,
    period_end=None,
    stripe_subscription_id: str | None = None,
) -> bool:
    """
    Notifica a Django (MAIN_APP_BASE/checkout/complete/) del exito del pago.
    Reintenta hasta 3 veces con backoff exponencial (2s, 4s, 8s).
    Si todos los reintentos fallan, guarda en WebhookNotificationQueue.
    Retorna True si la notificacion fue exitosa, False en caso contrario.
    """
    import httpx

    base_url = settings.MAIN_APP_BASE
    if not base_url:
        logger.error("MAIN_APP_BASE no configurado, no se puede notificar a Django")
        return False

    base_url = base_url.rstrip("/")
    url = f"{base_url}/checkout/complete/"

    headers = {
        "Content-Type": "application/json",
    }

    if settings.COBRANZA_WEBHOOK_SECRET:
        headers["X-Webhook-Token"] = settings.COBRANZA_WEBHOOK_SECRET
    else:
        logger.warning("COBRANZA_WEBHOOK_SECRET no configurado, se envia sin token")

    payload = {
        "user_id": user_id,
        "billing_code": billing_code,
        "plan_code": billing_code,
        "subscription_id": subscription_id,
    }

    if plan_id is not None:
        payload["plan_id"] = plan_id

    if service_id is not None:
        payload["service_id"] = service_id

    # Enviar period_start/period_end para que Django cree UserTimbreCount
    # con las fechas reales de Billing/Stripe (no calculadas por mes calendario)
    if date_cutoff:
        payload["date_cutoff"] = (
            date_cutoff.isoformat() if hasattr(date_cutoff, "isoformat") else str(date_cutoff)
        )
    if period_start:
        payload["period_start"] = (
            period_start.isoformat() if hasattr(period_start, "isoformat") else str(period_start)
        )
    if period_end:
        payload["period_end"] = (
            period_end.isoformat() if hasattr(period_end, "isoformat") else str(period_end)
        )
    if stripe_subscription_id:
        payload["stripe_subscription_id"] = stripe_subscription_id

    max_retries = 3
    last_error = None
    
    print(f"Notificando a Django {url} con payload: {payload}")

    for attempt in range(max_retries):
        try:
            with httpx.Client(timeout=10) as client:
                response = client.post(url, json=payload, headers=headers)
                if response.status_code < 400:
                    logger.info(
                        "Notificacion a Django exitosa para subscription %s",
                        subscription_id,
                    )
                    return True

                last_error = f"HTTP {response.status_code}: {response.text[:200]}"
                logger.warning(
                    "Intento %d/%d - Main app webhook fallo: %s",
                    attempt + 1, max_retries, last_error,
                )

        except httpx.TimeoutException:
            last_error = "Timeout"
            logger.warning(
                "Intento %d/%d - Timeout notificando a Django",
                attempt + 1, max_retries,
            )
        except Exception as exc:
            last_error = str(exc)
            logger.warning(
                "Intento %d/%d - Error notificando a Django: %s",
                attempt + 1, max_retries, exc,
            )

        if attempt < max_retries - 1:
            time.sleep(2 ** attempt)

    logger.error(
        "Todos los reintentos fallaron para notificar subscription %s a Django. "
        "Guardando en cola de reintentos.",
        subscription_id,
    )

    _save_failed_notification(
        user_id=user_id,
        billing_code=billing_code,
        subscription_id=subscription_id,
        plan_id=plan_id,
        service_id=service_id,
        date_cutoff=date_cutoff,
        last_error=last_error,
        period_start=period_start,
        period_end=period_end,
        stripe_subscription_id=stripe_subscription_id,
    )

    return False


def notify_subscription_event(
    *,
    event_type: str,
    user_id: int,
    billing_code: str,
    subscription_id: int,
    plan_id: int | None = None,
    service_id: int | None = None,
    date_cutoff=None,
    period_start=None,
    period_end=None,
    canceled_at=None,
    cancel_at_period_end: bool | None = None,
    stripe_subscription_id: str | None = None,
    full_payload: dict | None = None,
) -> bool:
    """
    Notifica a Django (MAIN_APP_BASE/subscription/sync/) de eventos de ciclo
    de vida de suscripciones (renewed, canceled, past_due, plan_changed, etc.).
    Reintenta hasta 3 veces con backoff exponencial (2s, 4s, 8s).
    Si todos los reintentos fallan, guarda en WebhookNotificationQueue.
    Retorna True si la notificacion fue exitosa, False en caso contrario.
    """
    import httpx

    base_url = settings.MAIN_APP_BASE
    if not base_url:
        logger.error("MAIN_APP_BASE no configurado, no se puede notificar a Django")
        return False

    base_url = base_url.rstrip("/")
    url = f"{base_url}/subscription/sync/"

    headers = {"Content-Type": "application/json"}
    if settings.COBRANZA_WEBHOOK_SECRET:
        headers["X-Webhook-Token"] = settings.COBRANZA_WEBHOOK_SECRET
    else:
        logger.warning("COBRANZA_WEBHOOK_SECRET no configurado, se envia sin token")

    # Construir payload completo para Django
    payload = full_payload or {
        "event_type": event_type,
        "user_id": user_id,
        "billing_code": billing_code,
        "subscription_id": subscription_id,
    }

    # Asegurar campos obligatorios en el payload
    payload.setdefault("event_type", event_type)
    payload.setdefault("user_id", user_id)
    payload.setdefault("billing_code", billing_code)

    if plan_id is not None:
        payload["plan_id"] = plan_id
    if service_id is not None:
        payload["service_id"] = service_id
    if date_cutoff:
        payload["date_cutoff"] = (
            date_cutoff.isoformat() if hasattr(date_cutoff, "isoformat") else str(date_cutoff)
        )
    if period_start:
        payload["period_start"] = (
            period_start.isoformat() if hasattr(period_start, "isoformat") else str(period_start)
        )
    if period_end:
        payload["period_end"] = (
            period_end.isoformat() if hasattr(period_end, "isoformat") else str(period_end)
        )
    if canceled_at:
        payload["canceled_at"] = (
            canceled_at.isoformat() if hasattr(canceled_at, "isoformat") else str(canceled_at)
        )
    if cancel_at_period_end is not None:
        payload["cancel_at_period_end"] = cancel_at_period_end
    if stripe_subscription_id:
        payload["stripe_subscription_id"] = stripe_subscription_id

    max_retries = 3
    last_error = None

    for attempt in range(max_retries):
        try:
            with httpx.Client(timeout=10) as client:
                response = client.post(url, json=payload, headers=headers)
                if response.status_code < 400:
                    logger.info(
                        "Notificacion %s a Django exitosa para subscription %s",
                        event_type, subscription_id,
                    )
                    return True

                last_error = f"HTTP {response.status_code}: {response.text[:200]}"
                logger.warning(
                    "Intento %d/%d - subscription_sync fallo (%s): %s",
                    attempt + 1, max_retries, event_type, last_error,
                )

        except httpx.TimeoutException:
            last_error = "Timeout"
            logger.warning(
                "Intento %d/%d - Timeout notificando %s a Django",
                attempt + 1, max_retries, event_type,
            )
        except Exception as exc:
            last_error = str(exc)
            logger.warning(
                "Intento %d/%d - Error notificando %s a Django: %s",
                attempt + 1, max_retries, event_type, exc,
            )

        if attempt < max_retries - 1:
            time.sleep(2 ** attempt)

    logger.error(
        "Todos los reintentos fallaron para notificar %s (subscription %s) a Django. "
        "Guardando en cola de reintentos.",
        event_type, subscription_id,
    )

    _save_failed_notification(
        user_id=user_id,
        billing_code=billing_code,
        subscription_id=subscription_id,
        plan_id=plan_id,
        service_id=service_id,
        date_cutoff=date_cutoff,
        last_error=last_error,
        event_type=event_type,
        full_payload=payload,
    )

    return False


# Checkout activa la suscripción
# Invoice define el ciclo

def handle_checkout_completed(session_data: dict):
    from app.models.subscription import Subscription
    from app.models.payment import Payment
    from app.models.plan import Plan
    from sqlmodel import Session, select
    from datetime import datetime

    subscription_id = session_data["metadata"]["subscription_id"]
    checkout_session_id = session_data["id"] 
    stripe_subscription_id = session_data.get("subscription")

    with Session(engine) as db:
        subscription = db.get(Subscription, int(subscription_id))
        if not subscription:
            return

        print("\n========== STRIPE CHECKOUT COMPLETED ==========")

        # =========================================================
        # Validacion CRITICA: solo activar si realmente pago
        # =========================================================
        payment_status = session_data.get("payment_status")
        session_status = session_data.get("status")

        if payment_status != "paid":
            logger.warning(
                "Checkout session %s NO esta pagada (payment_status=%s). "
                "No se activa subscription %s.",
                checkout_session_id, payment_status, subscription_id,
            )
            return

        if session_status != "complete":
            logger.warning(
                "Checkout session %s NO esta completa (status=%s). "
                "No se activa subscription %s.",
                checkout_session_id, session_status, subscription_id,
            )
            return

        existing_payment = db.exec(
            select(Payment).where(
                Payment.provider_payment_id == checkout_session_id
            )
        ).first()
        
        if existing_payment:
            logger.info("Checkout session %s ya procesada, ignorando duplicado", checkout_session_id)
            return
        # Activar suscripción
        subscription.status = "active"
        subscription.stripe_subscription_id = stripe_subscription_id

        # Guardar stripe_customer_id si viene en la sesión de checkout
        customer_id = session_data.get("customer")
        if customer_id:
            subscription.stripe_customer_id = customer_id


        db.add(subscription)
        db.commit()
        
        db.refresh(subscription)

        metadata = session_data.get("metadata", {}) or {}

        billing_code = (
            metadata.get("billing_code")
            or metadata.get("plan_code")
        )

        user_id = metadata.get("user_id") or subscription.user_id

        if not billing_code:
            plan = db.get(Plan, subscription.plan_id)
            billing_code = plan.code if plan else None
            
        # Protección parcial contra duplicados del mismo checkout.session.completed.
        # La activación final en Django se hace desde invoice.payment_succeeded
        # cuando ya existen fechas reales de Stripe.

        if billing_code and user_id and subscription.start_date and subscription.end_date:
            notify_main_app(
                user_id=int(user_id),
                billing_code=billing_code,
                subscription_id=subscription.id,
                plan_id=subscription.plan_id,
                date_cutoff=subscription.end_date,
                period_start=subscription.start_date,
                period_end=subscription.end_date,
                stripe_subscription_id=stripe_subscription_id,
            )
        else:
            logger.info(
                "checkout.session.completed no notifica a Django todavía porque faltan fechas. "
                "subscription_id=%s user_id=%s billing_code=%s start_date=%s end_date=%s. "
                "La activación final se hará en invoice.payment_succeeded subscription_create.",
                subscription.id,
                user_id,
                billing_code,
                subscription.start_date,
                subscription.end_date,
            )


#Pago único
def handle_one_time_payment(payment_intent: dict, event: dict):
    from app.models.payment import Payment
    from app.models.subscription import Subscription
    from sqlmodel import Session, select

    subscription_id = payment_intent["metadata"].get("subscription_id")

    if not subscription_id:
        return

    with Session(engine) as db:
        subscription = db.get(Subscription, int(subscription_id))
        if not subscription:
            return

        payment = Payment(
            subscription_id=subscription.id,
            provider="stripe",
            provider_payment_id=payment_intent["id"],
            amount=payment_intent["amount_received"],
            currency=payment_intent["currency"],
            status="succeeded",
            raw_event=event,
        )

        db.add(payment)
        db.commit()

#Pago de suscripción
# ---------------------------------------------------------------------------
# Helpers para detectar líneas de excedentes vs. líneas de suscripción
# en facturas de Stripe que pueden ser mixtas (renovación + excedentes).
# ---------------------------------------------------------------------------

def _is_cfdi_overage_line(line: dict) -> bool:
    """
    Detecta si una línea de factura de Stripe corresponde a un invoice
    item de excedentes CFDI (OnDemand).

    Busca metadata factupid_type=="cfdi_overage" en:
    - line.metadata
    - line.invoice_item_details.metadata
    - line.parent.invoice_item_details.metadata
    """
    if not isinstance(line, dict):
        return False

    # Buscar en metadata directa de la línea
    line_metadata = line.get("metadata") or {}
    if isinstance(line_metadata, dict) and (
        line_metadata.get("factupid_type") == "cfdi_overage"
    ):
        return True

    # Buscar en invoice_item_details de la línea
    item_details = line.get("invoice_item_details") or {}
    if isinstance(item_details, dict):
        item_metadata = item_details.get("metadata") or {}
        if isinstance(item_metadata, dict) and (
            item_metadata.get("factupid_type") == "cfdi_overage"
        ):
            return True

    # Buscar en parent.invoice_item_details
    parent = line.get("parent") or {}
    parent_item_details = parent.get("invoice_item_details") or {}
    if isinstance(parent_item_details, dict):
        parent_metadata = parent_item_details.get("metadata") or {}
        if isinstance(parent_metadata, dict) and (
            parent_metadata.get("factupid_type") == "cfdi_overage"
        ):
            return True

    return False


def _get_cfdi_overage_lines(invoice: dict) -> list:
    """
    Retorna la lista de líneas de excedentes CFDI en una factura.
    """
    if not isinstance(invoice, dict):
        return []

    lines = (invoice.get("lines") or {}).get("data") or []
    if not isinstance(lines, list):
        return []

    return [line for line in lines if _is_cfdi_overage_line(line)]


def _is_subscription_line(line: dict) -> bool:
    """
    Detecta si una línea de factura es una línea real de suscripción
    (NO es un invoice item de excedente).

    Una línea se considera de suscripción si:
    - Tiene parent.subscription_item_details.subscription (línea de suscripción Stripe)
    - O parent.type == "subscription_line_item"
    - Y NO es una línea de excedente CFDI.
    """
    if not isinstance(line, dict):
        return False

    # Si es línea de excedente, NO es línea de suscripción
    if _is_cfdi_overage_line(line):
        return False

    parent = line.get("parent") or {}

    # Línea con subscription_item_details es de suscripción
    if isinstance(parent, dict):
        sub_item_details = parent.get("subscription_item_details") or {}
        if isinstance(sub_item_details, dict) and sub_item_details.get("subscription"):
            return True

        # parent.type == "subscription_line_item" (formato Stripe legacy)
        if parent.get("type") == "subscription_line_item":
            return True

    return False


def _get_subscription_line(invoice: dict) -> dict | None:
    """
    Retorna la primera línea real de suscripción de la factura
    (excluyendo líneas de excedentes CFDI).
    """
    if not isinstance(invoice, dict):
        return None

    lines = (invoice.get("lines") or {}).get("data") or []
    if not isinstance(lines, list):
        return None

    for line in lines:
        if _is_subscription_line(line):
            return line

    return None


def _notify_cfdi_overage_billed(
    *,
    user_id: int,
    billing_code: str,
    subscription_id: int,
    overage_period_id: int,
    quantity: int,
    amount: int,
    stripe_invoice_item_id: str,
    stripe_invoice_id: str,
    report_sequence: int,
    paid_at,
):
    """
    Notifica a Django que un lote de excedentes CFDI fue cobrado (Fase 7C).
    Django marcará el CfdiOveragePeriod correspondiente como billed.
    """
    base_url = settings.MAIN_APP_BASE
    if not base_url:
        logger.error("MAIN_APP_BASE no configurado, no se puede notificar cfdi_overage_billed")
        return False

    base_url = base_url.rstrip("/")
    url = f"{base_url}/subscription/sync/"

    headers = {"Content-Type": "application/json"}
    if settings.COBRANZA_WEBHOOK_SECRET:
        headers["X-Webhook-Token"] = settings.COBRANZA_WEBHOOK_SECRET

    paid_at_str = (
        paid_at.isoformat() if hasattr(paid_at, "isoformat") else str(paid_at)
    )

    payload = {
        "event_type": "cfdi_overage_billed",
        "user_id": user_id,
        "billing_code": billing_code,
        "subscription_id": subscription_id,
        "overage_period_id": overage_period_id,
        "quantity": quantity,
        "amount": amount,
        "stripe_invoice_item_id": stripe_invoice_item_id,
        "stripe_invoice_id": stripe_invoice_id,
        "report_sequence": report_sequence,
        "paid_at": paid_at_str,
    }

    max_retries = 3
    last_error = None

    for attempt in range(max_retries):
        try:
            with httpx.Client(timeout=10) as client:
                response = client.post(url, json=payload, headers=headers)
                if response.status_code < 400:
                    logger.info(
                        "cfdi_overage_billed notificado a Django "
                        "overage_period_id=%s quantity=%s",
                        overage_period_id, quantity,
                    )
                    return True
                last_error = f"HTTP {response.status_code}: {response.text[:200]}"
        except httpx.TimeoutException:
            last_error = "Timeout"
        except Exception as exc:
            last_error = str(exc)

        if attempt < max_retries - 1:
            time.sleep(2 ** attempt)

    logger.error(
        "cfdi_overage_billed: todos los reintentos fallaron "
        "overage_period_id=%s last_error=%s",
        overage_period_id, last_error,
    )
    return False


def handle_invoice_created(invoice: dict):
    """
    Fase 7C.4: Cuando Stripe crea una invoice draft para una suscripción,
    dispara un último sync de excedentes CFDI a Django para que los
    invoice items pendientes se agreguen antes del cobro.

    Solo actúa sobre invoices de suscripción (con campo "subscription").
    No renueva suscripción, no crea Payment, no cambia estado.
    Si Django falla, responde OK a Stripe — la idempotencia y el
    scheduler periódico harán reintentos.
    """
    print("========== STRIPE INVOICE CREATED ==========")
    from app.models.subscription import Subscription
    from sqlmodel import Session, select

    invoice_id = invoice.get("id")
    subscription_id = invoice.get("subscription")

    # Solo procesar invoices de suscripción
    if not subscription_id:
        return

    # Ignorar invoices de un solo pago (payment_intent)
    billing_reason = invoice.get("billing_reason")
    if billing_reason in ("manual", "upcoming"):
        return

    logger.info(
        "invoice.created: invoice_id=%s subscription_stripe_id=%s "
        "billing_reason=%s",
        invoice_id, subscription_id, billing_reason,
    )

    # Resolver Subscription local por stripe_subscription_id
    with Session(engine) as db:
        subscription = db.exec(
            select(Subscription).where(
                Subscription.stripe_subscription_id == subscription_id
            )
        ).first()

    if not subscription:
        logger.warning(
            "invoice.created: subscription %s no encontrada en BD. "
            "Ignorando sync de excedentes.",
            subscription_id,
        )
        return

    # Disparar sync final de excedentes a Django
    ok = trigger_main_app_overage_reporting(
        mode="invoice_created",
        billing_subscription_id=subscription.id,
        stripe_subscription_id=subscription_id,
    )

    if not ok:
        logger.warning(
            "invoice.created: sync de excedentes a Django falló "
            "para subscription_id=%s. La idempotencia y el scheduler "
            "periódico harán reintentos.",
            subscription.id,
        )


def handle_cfdi_overage_invoice_paid(invoice: dict, event: dict):
    """
    Procesa el pago de una factura SOLO de excedentes CFDI (sin línea de
    suscripción). NO renueva la suscripción.

    Fase 7C: notifica a Django con cfdi_overage_billed para cada línea de
    excedente, extrayendo la metadata del invoice item de Stripe.
    """
    from app.models.payment import Payment
    from app.models.subscription import Subscription
    from sqlmodel import Session, select
    from datetime import datetime, timezone

    invoice_id = invoice.get("id")
    if not invoice_id:
        logger.warning("handle_cfdi_overage_invoice_paid: invoice sin id")
        return

    # Resolver la suscripción igual que en pagos normales
    stripe_sub_id = (
        invoice.get("parent", {})
               .get("subscription_details", {})
               .get("subscription")
        or invoice.get("lines", {})
                  .get("data", [{}])[0]
                  .get("parent", {})
                  .get("subscription_item_details", {})
                  .get("subscription")
    )

    internal_subscription_id = (
        invoice.get("parent", {})
               .get("subscription_details", {})
               .get("metadata", {})
               .get("subscription_id")
    )

    with Session(engine) as db:
        subscription = None

        if stripe_sub_id:
            subscription = db.exec(
                select(Subscription).where(
                    Subscription.stripe_subscription_id == stripe_sub_id
                )
            ).first()

        if not subscription and internal_subscription_id:
            try:
                subscription = db.get(Subscription, int(internal_subscription_id))
            except (TypeError, ValueError):
                subscription = None

        if not subscription:
            logger.warning(
                "handle_cfdi_overage_invoice_paid: no se pudo resolver "
                "subscription invoice_id=%s stripe_sub_id=%s",
                invoice_id,
                stripe_sub_id,
            )
            return

        # Idempotencia por invoice_id
        existing = db.exec(
            select(Payment).where(
                Payment.provider_payment_id == invoice_id
            )
        ).first()

        if existing:
            logger.info(
                "handle_cfdi_overage_invoice_paid: payment ya registrado "
                "invoice_id=%s",
                invoice_id,
            )
            return

        paid_at_ts = invoice.get("status_transitions", {}).get("paid_at")
        paid_at = (
            datetime.fromtimestamp(paid_at_ts, tz=timezone.utc)
            if paid_at_ts else datetime.now(timezone.utc)
        )

        payment = Payment(
            subscription_id=subscription.id,
            provider="stripe",
            provider_payment_id=invoice_id,
            amount=invoice.get("amount_paid", 0),
            currency=invoice.get("currency", "mxn"),
            status="succeeded",
            paid_at=paid_at,
            raw_event=event,
        )
        db.add(payment)
        db.commit()

        # Fase 7C: notificar a Django por cada línea de excedente
        billing_code = _resolve_billing_code_for_subscription(db, subscription)
        overage_lines = _get_cfdi_overage_lines(invoice)

        for line in overage_lines:
            line_metadata = line.get("metadata") or {}
            item_details = line.get("invoice_item_details") or {}
            item_metadata = item_details.get("metadata") or {}
            parent = line.get("parent") or {}
            parent_item_details = parent.get("invoice_item_details") or {}
            parent_metadata = parent_item_details.get("metadata") or {}

            # Fusionar metadata de todas las fuentes posibles
            merged = {}
            merged.update(parent_metadata)
            merged.update(item_metadata)
            merged.update(line_metadata)

            overage_period_id = int(merged.get("overage_period_id", 0))
            line_quantity = int(merged.get("quantity", 0))
            line_amount = int(line.get("amount", 0))
            line_stripe_invoice_item_id = (
                merged.get("stripe_invoice_item_id")
                or item_details.get("id")
                or parent_item_details.get("id")
                or ""
            )
            line_report_sequence = int(merged.get("report_sequence", 0))

            if overage_period_id and billing_code:
                _notify_cfdi_overage_billed(
                    user_id=subscription.user_id,
                    billing_code=billing_code,
                    subscription_id=subscription.id,
                    overage_period_id=overage_period_id,
                    quantity=line_quantity,
                    amount=line_amount,
                    stripe_invoice_item_id=line_stripe_invoice_item_id,
                    stripe_invoice_id=invoice_id,
                    report_sequence=line_report_sequence,
                    paid_at=paid_at,
                )

        logger.info(
            "handle_cfdi_overage_invoice_paid: pago de excedentes CFDI "
            "registrado invoice_id=%s subscription_id=%s amount=%s "
            "overage_lines=%d",
            invoice_id,
            subscription.id,
            invoice.get("amount_paid", 0),
            len(overage_lines),
        )


def handle_subscription_payment(invoice: dict, event: dict):
    """
    Este handler se ejecuta AUTOMÁTICAMENTE cuando Stripe envía
    el evento `invoice.payment_succeeded`.

    Sirve para:
    - Primer pago de suscripción
    - Renovaciones automáticas
    - Último pago antes de cancelación al final del período
    - Facturas mixtas (renovación + excedentes CFDI)

    Regla para facturas mixtas (Fase 7B fix):
    - Si la factura tiene SOLO líneas de excedente (sin línea de suscripción):
      se procesa como excedente puro, NO se renueva la suscripción.
    - Si la factura tiene una línea de suscripción (con o sin excedentes):
      se procesa la renovación normalmente. El excedente se registra pero
      NO bloquea la renovación.
    """
    from app.models.payment import Payment
    from app.models.subscription import Subscription
    from sqlmodel import Session, select
    from datetime import datetime, timezone

    print("\n========== STRIPE SUBSCRIPTION PAYMENT ==========")

    invoice_id = invoice.get("id")
    
    """
    Motivo del cobro (MUY IMPORTANTE)
    subscription_create  -> primer pago
    subscription_cycle   -> renovación automática
    upcoming             -> preview (NO REAL)
    """
    
    billing_reason = invoice.get("billing_reason")
    print("billing_reason:", billing_reason)
    
    # Ignorar previews (NO son pagos reales)
    if billing_reason == "upcoming":
        print("Invoice preview ignorada")
        return

    # --- Detectar líneas de excedentes y de suscripción ---
    overage_lines = _get_cfdi_overage_lines(invoice)
    subscription_line = _get_subscription_line(invoice)

    # Resolver stripe_sub_id y internal_subscription_id desde la línea
    # correcta (la de suscripción, NO la de excedente).
    if subscription_line:
        stripe_sub_id = (
            subscription_line.get("parent", {})
                           .get("subscription_item_details", {})
                           .get("subscription")
        )
    else:
        stripe_sub_id = (
            invoice.get("parent", {})
                   .get("subscription_details", {})
                   .get("subscription")
            or (invoice.get("lines", {}).get("data") or [{}])[0]
                   .get("parent", {})
                   .get("subscription_item_details", {})
                   .get("subscription")
        )

    internal_subscription_id = (
        invoice.get("parent", {})
               .get("subscription_details", {})
               .get("metadata", {})
               .get("subscription_id")
    )

    if not invoice_id:
        print("EXIT: invoice_id es None")
        return

    # --- Factura SOLO de excedentes (sin línea de suscripción) ---
    # NO es una renovación. Se procesa como excedente puro.
    if overage_lines and not subscription_line:
        handle_cfdi_overage_invoice_paid(invoice, event)
        return

    with Session(engine) as db:

        # 1 Resolver subscription de forma segura
        subscription = None

        if stripe_sub_id:
            subscription = db.exec(
                select(Subscription).where(
                    Subscription.stripe_subscription_id == stripe_sub_id
                )
            ).first()

        if not subscription and internal_subscription_id:
            try:
                candidate = db.get(Subscription, int(internal_subscription_id))
            except (TypeError, ValueError):
                candidate = None

            if candidate:
                if candidate.stripe_subscription_id and stripe_sub_id:
                    if candidate.stripe_subscription_id != stripe_sub_id:
                        logger.warning(
                            "Evento Stripe ignorado por conflicto: "
                            "metadata.subscription_id=%s local_stripe_subscription_id=%s "
                            "stripe_sub_id=%s invoice_id=%s",
                            internal_subscription_id,
                            candidate.stripe_subscription_id,
                            stripe_sub_id,
                            invoice_id,
                        )
                        return

                subscription = candidate

        if not subscription:
            logger.warning(
                "EXIT: No se pudo resolver subscription invoice_id=%s stripe_sub_id=%s internal_subscription_id=%s",
                invoice_id,
                stripe_sub_id,
                internal_subscription_id,
            )
            return

        if stripe_sub_id and not subscription.stripe_subscription_id:
            subscription.stripe_subscription_id = stripe_sub_id

        # Guardar stripe_customer_id si viene en la factura
        customer_id = invoice.get("customer")
        if customer_id and not subscription.stripe_customer_id:
            subscription.stripe_customer_id = customer_id

        if stripe_sub_id and subscription.stripe_subscription_id != stripe_sub_id:
            logger.warning(
                "Evento Stripe ignorado: subscription local id=%s tiene stripe_subscription_id=%s "
                "pero invoice trae stripe_subscription_id=%s invoice_id=%s",
                subscription.id,
                subscription.stripe_subscription_id,
                stripe_sub_id,
                invoice_id,
            )
            return

        # 2 Idempotencia
        existing = db.exec(
            select(Payment).where(
                Payment.provider_payment_id == invoice_id
            )
        ).first()

        if existing:
            print("Payment ya existe")
            return
        
        # 3 FECHAS REALES DESDE STRIPE
        # Usar la línea de suscripción para extraer el periodo, NO la
        # primera línea (que puede ser un invoice item de excedente).
        if subscription_line:
            period = subscription_line.get("period")
        else:
            try:
                period = invoice["lines"]["data"][0]["period"]
            except (KeyError, IndexError) as exc:
                logger.warning("Invoice %s sin period data válida: %s", invoice_id, exc)
                return

        if not period:
            logger.warning("Invoice %s sin period en subscription_line", invoice_id)
            return

        subscription.start_date = datetime.fromtimestamp(
            period["start"], tz=timezone.utc
        ).date()

        subscription.end_date = datetime.fromtimestamp(
            period["end"], tz=timezone.utc
        ).date()
        

        paid_at_ts = invoice.get("status_transitions", {}).get("paid_at")
        paid_at = (
            datetime.fromtimestamp(paid_at_ts, tz=timezone.utc)
            if paid_at_ts else datetime.now(timezone.utc)
        )

        # Registrar el pago (SIEMPRE se crea uno nuevo)
        payment = Payment(
            subscription_id=subscription.id,
            provider="stripe",
            provider_payment_id=invoice_id,
            amount=invoice["amount_paid"],
            currency=invoice["currency"],
            status="succeeded",
            paid_at=paid_at,
            raw_event=event,
        )
        
        # Cancelación al final del período
        # Este pago puede ser el ÚLTIMO
        if invoice.get("subscription_cancel_at_period_end"):
            subscription.status = "canceled"
            subscription.canceled_at = datetime.fromtimestamp(
                period["end"], tz=timezone.utc
            )
            print("Suscripción cancelada al final del período")

        db.add(subscription)
        db.add(payment)
        db.commit()

        # Loggear si la factura es mixta (renovación + excedentes)
        if overage_lines and subscription_line:
            logger.info(
                "handle_subscription_payment: factura mixta invoice_id=%s "
                "tiene %d línea(s) de excedente y línea de suscripción. "
                "Se procesa la renovación normalmente.",
                invoice_id,
                len(overage_lines),
            )

        # Notificar a Django según el tipo de pago:
        # - subscription_create: activación inicial en /checkout/complete/ con fechas reales de Stripe
        # - subscription_cycle: renovación en /subscription/sync/
        metadata = (
            invoice.get("parent", {})
                   .get("subscription_details", {})
                   .get("metadata", {})
        )
        user_id_from_invoice = metadata.get("user_id") or subscription.user_id
        billing_code = _resolve_billing_code_for_subscription(db, subscription)

        if not billing_code:
            print(
                f"ERROR: No se pudo resolver billing_code para "
                f"subscription_id={subscription.id}, plan_id={subscription.plan_id}"
            )
            return
        # Primer pago: activa Django con fechas reales
        if billing_reason == "subscription_create":
            notify_main_app(
                user_id=int(user_id_from_invoice),
                billing_code=billing_code,
                subscription_id=subscription.id,
                plan_id=subscription.plan_id,
                date_cutoff=subscription.end_date,
                period_start=subscription.start_date,
                period_end=subscription.end_date,
                stripe_subscription_id=stripe_sub_id,
            )

        # Renovaciones: sincroniza nueva fecha y timbres
        elif billing_reason == "subscription_cycle":
            notify_subscription_event(
                event_type="subscription_renewed",
                user_id=int(user_id_from_invoice),
                billing_code=billing_code,
                subscription_id=subscription.id,
                plan_id=subscription.plan_id,
                date_cutoff=subscription.end_date,
                period_start=subscription.start_date,
                period_end=subscription.end_date,
                stripe_subscription_id=stripe_sub_id,
            )

        # Fase 7C: notificar cfdi_overage_billed por cada línea de excedente
        # en facturas mixtas (la de solo excedentes ya se procesa arriba).
        if overage_lines and billing_code:
            paid_at_ts_for_overage = invoice.get("status_transitions", {}).get("paid_at")
            paid_at_for_overage = (
                datetime.fromtimestamp(paid_at_ts_for_overage, tz=timezone.utc)
                if paid_at_ts_for_overage else datetime.now(timezone.utc)
            )

            for line in overage_lines:
                line_metadata = line.get("metadata") or {}
                item_details = line.get("invoice_item_details") or {}
                item_metadata = item_details.get("metadata") or {}
                parent = line.get("parent") or {}
                parent_item_details = parent.get("invoice_item_details") or {}
                parent_metadata = parent_item_details.get("metadata") or {}

                merged = {}
                merged.update(parent_metadata)
                merged.update(item_metadata)
                merged.update(line_metadata)

                overage_period_id = int(merged.get("overage_period_id", 0))
                line_quantity = int(merged.get("quantity", 0))
                line_amount = int(line.get("amount", 0))
                line_stripe_invoice_item_id = (
                    merged.get("stripe_invoice_item_id")
                    or item_details.get("id")
                    or parent_item_details.get("id")
                    or ""
                )
                line_report_sequence = int(merged.get("report_sequence", 0))

                if overage_period_id:
                    _notify_cfdi_overage_billed(
                        user_id=int(user_id_from_invoice),
                        billing_code=billing_code,
                        subscription_id=subscription.id,
                        overage_period_id=overage_period_id,
                        quantity=line_quantity,
                        amount=line_amount,
                        stripe_invoice_item_id=line_stripe_invoice_item_id,
                        stripe_invoice_id=invoice_id,
                        report_sequence=line_report_sequence,
                        paid_at=paid_at_for_overage,
                    )


# #Pago de suscripción version anterior sin distinción de billing_reason
# def handle_subscription_payment(invoice: dict, event: dict):
#     from app.db.session import engine
#     from app.models.payment import Payment
#     from app.models.subscription import Subscription
#     from sqlmodel import Session, select
#     from datetime import datetime, timezone

#     print("\n========== STRIPE SUBSCRIPTION PAYMENT ==========")

#     invoice_id = invoice.get("id")

#     stripe_sub_id = (
#         invoice.get("parent", {})
#                .get("subscription_details", {})
#                .get("subscription")
#         or invoice.get("lines", {})
#                   .get("data", [{}])[0]
#                   .get("parent", {})
#                   .get("subscription_item_details", {})
#                   .get("subscription")
#     )

#     internal_subscription_id = (
#         invoice.get("parent", {})
#                .get("subscription_details", {})
#                .get("metadata", {})
#                .get("subscription_id")
#     )

#     # print("stripe_sub_id:", stripe_sub_id)
#     # print("internal_subscription_id:", internal_subscription_id)
#     # print("invoice_id:", invoice_id)

#     if not invoice_id:
#         print("EXIT: invoice_id es None")
#         return

#     with Session(engine) as db:

#         # 1 Resolver subscription
#         subscription = None

#         if internal_subscription_id:
#             subscription = db.get(Subscription, int(internal_subscription_id))

#         if not subscription and stripe_sub_id:
#             subscription = db.exec(
#                 select(Subscription).where(
#                     Subscription.stripe_subscription_id == stripe_sub_id
#                 )
#             ).first()

#         if not subscription:
#             print("EXIT: No se pudo resolver subscription")
#             return

#         # 2 Idempotencia
#         existing = db.exec(
#             select(Payment).where(
#                 Payment.provider_payment_id == invoice_id
#             )
#         ).first()

#         if existing:
#             print("Payment ya existe")
#             return
        
#         # 3 FECHAS REALES DESDE STRIPE (AQUÍ)
#         period = invoice["lines"]["data"][0]["period"]

#         subscription.start_date = datetime.fromtimestamp(
#             period["start"], tz=timezone.utc
#         ).date()

#         subscription.end_date = datetime.fromtimestamp(
#             period["end"], tz=timezone.utc
#         ).date()
        

#         paid_at_ts = invoice.get("status_transitions", {}).get("paid_at")
#         paid_at = (
#             datetime.fromtimestamp(paid_at_ts, tz=timezone.utc)
#             if paid_at_ts else datetime.now(timezone.utc)
#         )

#         payment = Payment(
#             subscription_id=subscription.id,
#             provider="stripe",
#             provider_payment_id=invoice_id,
#             amount=invoice["amount_paid"],
#             currency=invoice["currency"],
#             status="succeeded",
#             paid_at=paid_at,
#             raw_event=event,
#         )

#         db.add(subscription)
#         db.add(payment)
#         db.commit()



def handle_subscription_deleted(data: dict):
    from app.models.subscription import Subscription
    from sqlmodel import Session, select
    from datetime import datetime, timezone

    print("\n========== STRIPE SUBSCRIPTION DELETED ==========")

    stripe_sub_id = data["id"]
    canceled_at_ts = data.get("canceled_at")

    print("stripe_subscription_id:", stripe_sub_id)

    with Session(engine) as db:
        subscription = db.exec(
            select(Subscription).where(
                Subscription.stripe_subscription_id == stripe_sub_id
            )
        ).first()

        if not subscription:
            print("Incidencia: Subscription no encontrada en BD para este stripe_subscription_id")
            return

        subscription.status = "canceled"
        subscription.canceled_at = (
            datetime.fromtimestamp(canceled_at_ts, tz=timezone.utc)
            if canceled_at_ts
            else datetime.now(timezone.utc)
        )

        # Guardar stripe_customer_id si viene en el evento
        customer_id = data.get("customer")
        if customer_id:
            subscription.stripe_customer_id = customer_id

        db.add(subscription)
        db.commit()
        db.refresh(subscription)

        print(
            f"OK: Subscription {subscription.id} marcada como CANCELADA "
            f"(user_id={subscription.user_id}, plan_id={subscription.plan_id})"
        )
        
        billing_code = _resolve_billing_code_for_subscription(db, subscription)

        if not billing_code:
            print(
                f"ERROR: No se pudo resolver billing_code para "
                f"subscription_id={subscription.id}, plan_id={subscription.plan_id}"
            )
            return

        # Notificar a Django subscription_canceled
        notify_subscription_event(
            event_type="subscription_canceled",
            user_id=subscription.user_id,
            billing_code=billing_code,
            subscription_id=subscription.id,
            plan_id=subscription.plan_id,
            canceled_at=subscription.canceled_at,
            date_cutoff=subscription.end_date,
        )

# def handle_subscription_deleted(data: dict):
#     from app.db.session import engine
#     from app.models.subscription import Subscription
#     from sqlmodel import Session, select
#     from datetime import datetime, timezone
#     print("\n========== STRIPE SUBSCRIPTION DELETED ==========")

#     stripe_sub_id = data["id"]

#     with Session(engine) as db:
#         stmt = select(Subscription).where(
#             Subscription.stripe_subscription_id == stripe_sub_id
#         )
#         subscription = db.exec(stmt).first()

#         if not subscription:
#             return

#         subscription.status = "canceled"
#         subscription.canceled_at = datetime.now(timezone.utc)

#         db.add(subscription)
#         db.commit()

def handle_invoice_payment_failed(invoice: dict, event: dict):
    from app.models.subscription import Subscription
    from sqlmodel import Session, select
    from datetime import datetime, timezone

    print("\n========== STRIPE PAYMENT FAILED ==========")

    stripe_sub_id = (
        invoice.get("subscription")
        or invoice.get("parent", {})
                .get("subscription_details", {})
                .get("subscription")
    )
    billing_reason = invoice.get("billing_reason")
    invoice_id = invoice.get("id")

    print("invoice_id:", invoice_id)
    print("billing_reason:", billing_reason)
    print("stripe_subscription_id:", stripe_sub_id)

    # Solo procesar renovaciones automáticas
    if billing_reason != "subscription_cycle":
        print("EXIT: no es renovación")
        return
    
    if not stripe_sub_id:
        print("EXIT: invoice sin subscription")
        return

    with Session(engine) as db:
        subscription = db.exec(
            select(Subscription).where(
                Subscription.stripe_subscription_id == stripe_sub_id
            )
        ).first()

        if not subscription:
            print("WARN: Subscription no encontrada en BD")
            return

        # Actualizar estado a past_due lo antes posible
        subscription.status = "past_due"
        db.add(subscription)
        db.commit()
        db.refresh(subscription)

        print(
            f"Subscription {subscription.id} marcada como PAST_DUE "
            f"(user_id={subscription.user_id})"
        )
        billing_code = _resolve_billing_code_for_subscription(db, subscription)

        if not billing_code:
            print(
                f"ERROR: No se pudo resolver billing_code para "
                f"subscription_id={subscription.id}, plan_id={subscription.plan_id}"
            )
            return

        # Notificar a Django subscription_past_due
        notify_subscription_event(
            event_type="subscription_past_due",
            user_id=subscription.user_id,
            billing_code=billing_code,
            subscription_id=subscription.id,
            plan_id=subscription.plan_id,
        )


def handle_subscription_updated(data: dict):
    from app.models.subscription import Subscription
    from app.models.plan import Plan
    from sqlmodel import Session, select
    from datetime import datetime, timezone

    print("\n========== STRIPE SUBSCRIPTION UPDATED ==========")

    stripe_sub_id = data.get("id")
    stripe_status = data.get("status")

    cancel_at_period_end = data.get("cancel_at_period_end", False)
    canceled_at = data.get("canceled_at")

    print("stripe_subscription_id:", stripe_sub_id)
    print("stripe_status:", stripe_status)
    print("cancel_at_period_end:", cancel_at_period_end)
    
    # Obtener price actual (CLAVE)
    items = data.get("items", {}).get("data", [])
    if not items:
        print("No hay items en la suscripción")
        return

    current_price_id = items[0]["price"]["id"]
    print("current_price_id:", current_price_id)

    with Session(engine) as db:
        subscription = db.exec(
            select(Subscription).where(
                Subscription.stripe_subscription_id == stripe_sub_id
            )
        ).first()

        if not subscription:
            print("WARN: Subscription no encontrada")
            return

        # Guardar plan_id anterior para detectar cambios reales
        previous_plan_id = subscription.plan_id

        # Buscar plan en la BD
        new_plan = db.exec(
            select(Plan).where(
                Plan.stripe_price_id == current_price_id
            )
        ).first()

        if not new_plan:
            print("WARN: Plan no encontrado para price_id:", current_price_id)
        else:
            print(f"Stripe reporta plan_id={new_plan.id}")

            # =========================
            # CASO 1: NO hay schedule → update normal (upgrade)
            # =========================
            if not subscription.stripe_schedule_id:

                if subscription.plan_id != new_plan.id:
                    print(f"Plan cambiado (inmediato): {subscription.plan_id} → {new_plan.id}")
                    subscription.plan_id = new_plan.id

            # =========================
            # CASO 2: HAY schedule → downgrade pendiente
            # =========================
            else:
                print("Schedule activo, verificando si ya se aplicó...")

                if subscription.plan_id != new_plan.id:
                    print(f"Plan aplicado al final del ciclo: {subscription.plan_id} → {new_plan.id}")

                    # Liberar el schedule en Stripe: el cambio ya se aplicó y el
                    # schedule cumplió su función. Dejarlo activo bloquearía
                    # futuras cancelaciones/modificaciones de la suscripción.
                    if subscription.stripe_schedule_id:
                        released, schedule_status, release_error = (
                            release_stripe_schedule_if_possible(
                                stripe_schedule_id=subscription.stripe_schedule_id,
                            )
                        )
                        if released:
                            print(
                                f"Schedule {subscription.stripe_schedule_id} "
                                "liberado en Stripe"
                            )
                        elif release_error:
                            logger.warning(
                                "No se pudo liberar el schedule %s de la "
                                "suscripción %s: %s",
                                subscription.stripe_schedule_id,
                                subscription.id,
                                release_error,
                            )
                        else:
                            logger.warning(
                                "Schedule %s de la suscripción %s en estado %s "
                                "al aplicar el downgrade",
                                subscription.stripe_schedule_id,
                                subscription.id,
                                schedule_status,
                            )

                    subscription.plan_id = new_plan.id
                    subscription.stripe_schedule_id = None  # limpiar schedule

                else:
                    print("Cambio aún NO aplicado, se mantiene plan actual en DB")

        # -------- STATUS --------
        subscription.status = stripe_status
        subscription.cancel_at_period_end = cancel_at_period_end

        # Guardar stripe_customer_id si viene en el evento
        customer_id = data.get("customer")
        if customer_id and not subscription.stripe_customer_id:
            subscription.stripe_customer_id = customer_id

        if canceled_at:
            subscription.canceled_at = datetime.fromtimestamp(
                canceled_at, timezone.utc
            )

        db.add(subscription)
        db.commit()
        db.refresh(subscription)

        print(f"Subscription {subscription.id} sincronizada correctamente")

        # -------- NOTIFICACIONES A DJANGO --------

        # CASO UNPAID: Stripe agotó los reintentos de cobro. NO es una
        # cancelación: se notifica para que Django bloquee el timbrado y
        # muestre la opción de regularizar el pago. No se cancela nada.
        if stripe_status == "unpaid":
            print(f"Notificando subscription_unpaid: {subscription.id}")
            billing_code = _resolve_billing_code_for_subscription(db, subscription)

            if not billing_code:
                print(
                    f"ERROR: No se pudo resolver billing_code para "
                    f"subscription_id={subscription.id}, plan_id={subscription.plan_id}"
                )
                return

            notify_subscription_event(
                event_type="subscription_unpaid",
                user_id=subscription.user_id,
                billing_code=billing_code,
                subscription_id=subscription.id,
                plan_id=subscription.plan_id,
                date_cutoff=subscription.end_date,
                period_end=subscription.end_date,
                stripe_subscription_id=stripe_sub_id,
            )
            return

        # Detectar cambio real de plan (solo si el plan_id realmente cambió)
        plan_changed = previous_plan_id != subscription.plan_id
        if plan_changed and new_plan:
            print(f"Notificando subscription_plan_changed: {previous_plan_id} → {subscription.plan_id}")
            notify_subscription_event(
                event_type="subscription_plan_changed",
                user_id=subscription.user_id,
                billing_code=new_plan.code,
                subscription_id=subscription.id,
                plan_id=subscription.plan_id,
                service_id=None,
                date_cutoff=subscription.end_date,
                period_start=subscription.start_date,
                period_end=subscription.end_date,
                stripe_subscription_id=stripe_sub_id,
            )

        # Detectar cancelación programada (cancel_at_period_end se activó)
        elif cancel_at_period_end:
            print("Notificando subscription_cancel_scheduled")
            
            billing_code = _resolve_billing_code_for_subscription(db, subscription)

            if not billing_code:
                print(
                    f"ERROR: No se pudo resolver billing_code para "
                    f"subscription_id={subscription.id}, plan_id={subscription.plan_id}"
                )
                return
            
            notify_subscription_event(
                event_type="subscription_cancel_scheduled",
                user_id=subscription.user_id,
                billing_code=billing_code,
                subscription_id=subscription.id,
                plan_id=subscription.plan_id,
                date_cutoff=subscription.end_date,
                period_end=subscription.end_date,
                cancel_at_period_end=True,
                stripe_subscription_id=stripe_sub_id,
            )
