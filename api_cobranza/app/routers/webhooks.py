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

    #Pago único
    if event["type"] == "payment_intent.succeeded":
        handle_one_time_payment(event["data"]["object"], event)

    elif event["type"] == "invoice.payment_succeeded":
        handle_subscription_payment(event["data"]["object"], event)

    elif event["type"] == "customer.subscription.deleted":
        handle_subscription_deleted(event["data"]["object"])

    return {"status": "ok"}



def handle_checkout_completed(session_data: dict):
    from app.db.session import engine
    from app.models.subscription import Subscription
    from app.models.payment import Payment
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
        # Activar suscripción
        subscription.status = "active"
        subscription.stripe_subscription_id = stripe_subscription_id
        # subscription.start_date = subscription.created_at.date()
        # subscription.end_date = subscription.start_date.replace(
        #     month=(subscription.start_date.month % 12) + 1
        # )


        db.add(subscription)
        db.commit()


#Pago único
def handle_one_time_payment(payment_intent: dict, event: dict):
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

#Pago de suscripción
def handle_subscription_payment(invoice: dict, event: dict):
    from app.db.session import engine
    from app.models.payment import Payment
    from app.models.subscription import Subscription
    from sqlmodel import Session, select
    from datetime import datetime, timezone

    print("\n========== STRIPE SUBSCRIPTION PAYMENT ==========")

    invoice_id = invoice.get("id")

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

    # print("stripe_sub_id:", stripe_sub_id)
    # print("internal_subscription_id:", internal_subscription_id)
    # print("invoice_id:", invoice_id)

    if not invoice_id:
        print("EXIT: invoice_id es None")
        return

    with Session(engine) as db:

        # 1 Resolver subscription
        subscription = None

        if internal_subscription_id:
            subscription = db.get(Subscription, int(internal_subscription_id))

        if not subscription and stripe_sub_id:
            subscription = db.exec(
                select(Subscription).where(
                    Subscription.stripe_subscription_id == stripe_sub_id
                )
            ).first()

        if not subscription:
            print("EXIT: No se pudo resolver subscription")
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
        
        # 3 FECHAS REALES DESDE STRIPE (AQUÍ)
        period = invoice["lines"]["data"][0]["period"]

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

        db.add(subscription)
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
