import stripe
from fastapi import APIRouter, Request, HTTPException, status
from sqlmodel import Session, select

from app.core.config import settings
from app.db.session import get_session
from app.models.subscription import Subscription

router = APIRouter(prefix="/webhooks", tags=["webhooks"])

stripe.api_key = settings.STRIPE_SECRET_KEY


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

    subscription_id = session_data["metadata"].get("subscription_id")

    if not subscription_id:
        return

    with Session(engine) as db:
        statement = select(Subscription).where(
            Subscription.id == int(subscription_id)
        )
        subscription = db.exec(statement).first()

        if not subscription:
            return

        subscription.status = "active"
        subscription.start_date = subscription.start_date or subscription.created_at.date()

        # ejemplo simple: mensual
        subscription.end_date = subscription.start_date.replace(
            year=subscription.start_date.year + (1 if subscription.start_date.month == 12 else 0),
            month=(subscription.start_date.month % 12) + 1
        )

        db.add(subscription)
        db.commit()

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
