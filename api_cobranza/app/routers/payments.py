from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
import stripe
from sqlmodel import Session, select

from app.db.session import get_session
from app.models.plan import Plan
from app.models.subscription import Subscription
from app.schemas.subscription import SubscriptionCreate, SubscriptionRead


from app.services.stripe_service import (
    create_checkout_session,
    create_subscription_checkout_session,
)
from app.core.config import settings
from app.routers.webhooks import handle_checkout_completed
from app.schemas.payment import CheckoutSessionResponse

from datetime import datetime, timedelta
from app.services.stripe_service import cancel_stripe_subscription
from app.schemas.subscription import SubscriptionCancel
from app.routers.webhooks import notify_main_app


router = APIRouter(prefix="/payments", tags=["payments"])


class CheckoutConfirmRequest(BaseModel):
    session_id: str


@router.post(
    "/init",
    response_model=CheckoutSessionResponse,
    status_code=status.HTTP_201_CREATED,
)
def init_subscription(
    data: SubscriptionCreate,
    session: Session = Depends(get_session),
):
    """
    Inicia una suscripcion en estado PENDING.
    """
    # Flujo general:
    # 1) Django/Hugo llama este endpoint con user_id y plan (code o id).
    # 2) Se crea Subscription interna en estado pending.
    # 3) Se crea Checkout Session de Stripe (payment/subscription).
    # 4) Stripe redirige al usuario; luego webhook/fallback confirma y activa.

    # 1) Resolver plan de cobro dentro de billing.
    # Nota: plan_code es la llave estable entre sistemas; plan_id es fallback local.
    if data.plan_code:
        plan_stmt = select(Plan).where(
            Plan.code == data.plan_code,
            Plan.is_active == True,  # noqa: E712
        )
    elif data.plan_id is not None:
        plan_stmt = select(Plan).where(
            Plan.id == data.plan_id,
            Plan.is_active == True,  # noqa: E712
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debes enviar plan_id o plan_code",
        )
    plan = session.exec(plan_stmt).first()

    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El plan no existe o no está activo",
        )

    # 2) Persistir Subscription pending para ligar el pago de Stripe a un registro interno.
    subscription = Subscription(
        user_id=data.user_id,
        plan_id=plan.id,
        status="pending",
        provider="stripe",
    )

    session.add(subscription)
    session.commit()
    session.refresh(subscription)


    # 3) Crear checkout en Stripe y enviar metadata de trazabilidad:
    # subscription_id, user_id, plan_code y opcionalmente plan_id/service_id de Django.
    if plan.billing_type == "subscription":
        if not plan.stripe_price_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El plan de suscripcion no tiene stripe_price_id",
            )

        checkout_session = create_subscription_checkout_session(
            stripe_price_id=plan.stripe_price_id,
            subscription_id=subscription.id,
            user_id=subscription.user_id,
            plan_code=plan.code,
            plan_id=data.plan_id,
            service_id=data.service_id,
        )
    else:
        checkout_session = create_checkout_session(
            plan_name=plan.name,
            amount=plan.price,
            currency=plan.currency,
            subscription_id=subscription.id,
            user_id=subscription.user_id,
            plan_code=plan.code,
            plan_id=data.plan_id,
            service_id=data.service_id,
        )

    # 4) Plan gratuito: no depende de webhook de Stripe; se activa inmediatamente
    # y se notifica a Django para crear/actualizar User_Service.
    if plan.billing_type == "one_time" and plan.price == 0:
        subscription.status = "active"
        subscription.start_date = subscription.start_date or subscription.created_at.date()
        subscription.end_date = subscription.start_date + timedelta(days=30)
        session.add(subscription)
        session.commit()
        notify_main_app(
            user_id=subscription.user_id,
            plan_code=plan.code,
            subscription_id=subscription.id,
            plan_id=data.plan_id,
            service_id=data.service_id,
        )

    return {
        "subscription": SubscriptionRead(
            id=subscription.id,
            user_id=subscription.user_id,
            plan_code=plan.code,
            status=subscription.status,
            start_date=subscription.start_date,
            end_date=subscription.end_date,
            provider=subscription.provider,
            created_at=subscription.created_at,
        ),
        "checkout_url": checkout_session.url,
    }


@router.post("/confirm")
def confirm_checkout(data: CheckoutConfirmRequest):
    """
    Fallback: confirma un Checkout Session desde Django /checkout/success.
    """
    # Este endpoint cubre escenarios donde el webhook de Stripe no llega a tiempo.
    # Django envia session_id al volver de Stripe y aqui forzamos la confirmacion.
    stripe.api_key = settings.STRIPE_SECRET_KEY
    try:
        session = stripe.checkout.Session.retrieve(data.session_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se pudo recuperar la sesión de Stripe",
        )

    payment_status = getattr(session, "payment_status", None)
    status_value = getattr(session, "status", None)

    if payment_status != "paid" and status_value != "complete":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Pago no confirmado todavía",
        )

    # Reutiliza la misma logica del webhook checkout.session.completed.
    handle_checkout_completed(session)
    return {"status": "ok"}


@router.post("/subscriptions/{subscription_id}/cancel")
def cancel_subscription(
    subscription_id: int,
    data: SubscriptionCancel,
    session: Session = Depends(get_session),
):
    stmt = select(Subscription).where(Subscription.id == subscription_id)
    subscription = session.exec(stmt).first()

    if not subscription:
        raise HTTPException(status_code=404, detail="Suscripción no encontrada")

    if subscription.status != "active":
        raise HTTPException(
            status_code=400,
            detail="Solo se pueden cancelar suscripciones activas"
        )

    if not subscription.stripe_subscription_id:
        raise HTTPException(
            status_code=400,
            detail="Suscripción no vinculada a Stripe"
        )

    # 1 Cancelar en Stripe
    cancel_stripe_subscription(
        stripe_subscription_id=subscription.stripe_subscription_id,
        at_period_end=data.at_period_end,
    )

    # 2 Actualizar BD
    subscription.cancel_at_period_end = data.at_period_end

    if not data.at_period_end:
        subscription.status = "canceled"
        subscription.canceled_at = datetime.utcnow()

    session.add(subscription)
    session.commit()

    return {
        "status": "ok",
        "subscription_id": subscription.id,
        "cancel_at_period_end": data.at_period_end,

    }

