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
