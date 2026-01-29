import logging
import stripe
from fastapi import APIRouter, Request, HTTPException, status
from sqlmodel import Session, select

from app.core.config import settings
from app.db.session import get_session
from app.models.subscription import Subscription

router = APIRouter(prefix="/webhooks", tags=["webhooks"])

stripe.api_key = settings.STRIPE_SECRET_KEY
logger = logging.getLogger(__name__)


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
    logger.info("Stripe webhook recibido: %s", event.get("type"))
    if event["type"] == "checkout.session.completed":
        handle_checkout_completed(event["data"]["object"])
        
    if event["type"] == "payment_intent.succeeded":
        handle_payment_succeeded(event["data"]["object"], event)
    elif event["type"] == "customer.subscription.deleted":
        handle_subscription_deleted(event["data"]["object"])

    return {"status": "ok"}



def handle_checkout_completed(session_data: dict):
    """
    Activa la suscripcion cuando Stripe confirma el pago.
    """
    from app.db.session import engine  # import local para evitar ciclos
    from app.models.plan import Plan

    subscription_id = session_data.get("metadata", {}).get("subscription_id")

    if not subscription_id:
        return

    with Session(engine) as db:
        statement = select(Subscription).where(
            Subscription.id == int(subscription_id)
        )
        subscription = db.exec(statement).first()

        if not subscription:
            return

        subscription.stripe_subscription_id = session_data.get("subscription")
        subscription.status = "active"
        subscription.start_date = subscription.start_date or subscription.created_at.date()

        # ejemplo simple: mensual
        subscription.end_date = subscription.start_date.replace(
            year=subscription.start_date.year + (1 if subscription.start_date.month == 12 else 0),
            month=(subscription.start_date.month % 12) + 1
        )

        db.add(subscription)
        db.commit()

        plan_code = session_data.get("metadata", {}).get("plan_code")
        user_id = session_data.get("metadata", {}).get("user_id")

        if not plan_code or not user_id:
            plan = db.get(Plan, subscription.plan_id)
            plan_code = plan.code if plan else plan_code
            user_id = user_id or str(subscription.user_id)

        if plan_code and user_id:
            notify_main_app(
                user_id=int(user_id),
                plan_code=plan_code,
                subscription_id=subscription.id,
            )

def handle_payment_succeeded(payment_intent: dict, event: dict):
    from app.db.session import engine
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


def handle_subscription_deleted(data: dict):
    from app.db.session import engine
    from app.models.subscription import Subscription
    from sqlmodel import Session, select
    from datetime import datetime

    stripe_sub_id = data["id"]

    with Session(engine) as db:
        stmt = select(Subscription).where(
            Subscription.stripe_subscription_id == stripe_sub_id
        )
        subscription = db.exec(stmt).first()

        if not subscription:
            return

        subscription.status = "canceled"
        subscription.canceled_at = datetime.utcnow()

        db.add(subscription)
        db.commit()


def notify_main_app(*, user_id: int, plan_code: str, subscription_id: int) -> None:
    try:
        import httpx
    except ModuleNotFoundError:
        logger.warning("httpx no instalado: no se pudo notificar a Django.")
        return
    base_url = settings.MAIN_APP_BASE.rstrip("/")
    url = f"{base_url}/checkout/complete/"
    headers = {}

    if settings.MAIN_APP_WEBHOOK_SECRET:
        headers["X-Webhook-Token"] = settings.MAIN_APP_WEBHOOK_SECRET

    payload = {
        "user_id": user_id,
        "plan_code": plan_code,
        "subscription_id": subscription_id,
    }

    try:
        with httpx.Client(timeout=10) as client:
            response = client.post(url, json=payload, headers=headers)
            if response.status_code >= 400:
                logger.warning(
                    "Main app webhook failed: %s %s",
                    response.status_code,
                    response.text,
                )
    except Exception as exc:
        logger.warning("Main app webhook error: %s", exc)
