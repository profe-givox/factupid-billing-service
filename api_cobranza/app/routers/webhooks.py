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

    return {"status": "ok"}

# Checkout activa la suscripción
# Invoice define el ciclo

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

        print(
            f"OK: Subscription {subscription.id} marcada como CANCELADA "
            f"(user_id={subscription.user_id}, plan_id={subscription.plan_id})"
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
    from app.db.session import engine
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

        # Stripe enviará customer.subscription.updated con el estado real

        print(
            f"Intento de cobro fallido registrado para subscription {subscription.id}"
        )
        # Registrar un Payment fallido opcional


def handle_subscription_updated(data: dict):
    from app.db.session import engine
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

                # 👉 Si Stripe ya coincide con el nuevo plan
                if subscription.plan_id != new_plan.id:
                    print(f"Plan aplicado al final del ciclo: {subscription.plan_id} → {new_plan.id}")

                    subscription.plan_id = new_plan.id
                    subscription.stripe_schedule_id = None  # limpiar schedule

                else:
                    print("Cambio aún NO aplicado, se mantiene plan actual en DB")

        # -------- STATUS --------
        subscription.status = stripe_status
        subscription.cancel_at_period_end = cancel_at_period_end

        if canceled_at:
            subscription.canceled_at = datetime.fromtimestamp(
                canceled_at, timezone.utc
            )

        db.add(subscription)
        db.commit()

        print(f"Subscription {subscription.id} sincronizada correctamente")
