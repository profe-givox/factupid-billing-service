"""Servicio para disparar reporte de excedentes CFDI a Django (Fase 7C.3).

Billing llama a Django POST /subscription/report-overages/ para que este
procese los CfdiOveragePeriod pendientes y cree invoice items en Stripe.

Django es la fuente de verdad. Billing solo dispara el proceso.
"""

import logging

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


def trigger_main_app_overage_reporting(
    mode="periodic",
    billing_subscription_id=None,
    stripe_subscription_id=None,
    stripe_invoice_id=None,
):
    """
    Llama a Django POST /subscription/report-overages/ para reportar
    excedentes CFDI pendientes.

    Args:
        mode: "periodic"|"invoice_created"|"manual"
        billing_subscription_id: int opcional — ID de Subscription en Billing
        stripe_subscription_id: str opcional — ID de suscripción en Stripe
        stripe_invoice_id: str opcional — ID de invoice draft en Stripe

    Returns:
        True si la llamada fue exitosa, False si falló.
        En caso de fallo, loggea el error pero NO lanza excepción.
    """
    base_url = settings.MAIN_APP_BASE
    if not base_url:
        logger.error(
            "trigger_main_app_overage_reporting: MAIN_APP_BASE no configurado"
        )
        return False

    base_url = base_url.rstrip("/")
    url = f"{base_url}/subscription/report-overages/"

    headers = {"Content-Type": "application/json"}
    if settings.COBRANZA_WEBHOOK_SECRET:
        headers["X-Webhook-Token"] = settings.COBRANZA_WEBHOOK_SECRET
    else:
        logger.warning(
            "trigger_main_app_overage_reporting: COBRANZA_WEBHOOK_SECRET "
            "no configurado, enviando sin token"
        )

    payload = {"mode": mode}
    if billing_subscription_id is not None:
        payload["billing_subscription_id"] = billing_subscription_id
    if stripe_subscription_id is not None:
        payload["stripe_subscription_id"] = stripe_subscription_id
    if stripe_invoice_id is not None:
        payload["stripe_invoice_id"] = stripe_invoice_id

    logger.info(
        "trigger_main_app_overage_reporting: mode=%s "
        "billing_subscription_id=%s stripe_subscription_id=%s "
        "stripe_invoice_id=%s",
        mode, billing_subscription_id, stripe_subscription_id,
        stripe_invoice_id,
    )

    try:
        with httpx.Client(timeout=30) as client:
            response = client.post(url, json=payload, headers=headers)

            if response.status_code < 400:
                data = response.json() if response.headers.get("content-type", "").startswith("application/json") else {}
                logger.info(
                    "trigger_main_app_overage_reporting: exito. "
                    "mode=%s status=%s reported=%s failed=%s",
                    mode,
                    response.status_code,
                    data.get("reported", "?"),
                    data.get("failed", "?"),
                )
                return True

            logger.warning(
                "trigger_main_app_overage_reporting: Django respondió %s. "
                "Body: %s",
                response.status_code,
                response.text[:500],
            )
            return False

    except httpx.TimeoutException:
        logger.warning(
            "trigger_main_app_overage_reporting: timeout "
            "(30s) llamando a Django. mode=%s", mode,
        )
        return False
    except httpx.ConnectError:
        logger.warning(
            "trigger_main_app_overage_reporting: error de conexión "
            "a Django. mode=%s", mode,
        )
        return False
    except Exception as exc:
        logger.error(
            "trigger_main_app_overage_reporting: error inesperado: %s",
            exc,
        )
        return False
