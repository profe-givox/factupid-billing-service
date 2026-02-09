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


#Pago de suscripción
def handle_subscription_payment(invoice: dict, event: dict):
    """
    Este handler se ejecuta AUTOMÁTICAMENTE cuando Stripe envía
    el evento `invoice.payment_succeeded`.

    Sirve para:
    - Primer pago de suscripción
    - Renovaciones automáticas
    - Último pago antes de cancelación al final del período
    """
    from app.db.session import engine
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
    from app.db.session import engine
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


        db.add(subscription)
        db.commit()



def notify_main_app(*, user_id: int, plan_code: str, subscription_id: int) -> None:
    # Notifica a Django para crear/actualizar el User_Service al completar el cobro.
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
