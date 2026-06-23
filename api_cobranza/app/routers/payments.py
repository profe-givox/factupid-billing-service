import stripe
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.db.session import get_session
from app.models.plan import Plan
from app.models.subscription import Subscription
from app.models.payment import Payment
from app.schemas.subscription import SubscriptionCreate, SubscriptionRead

from app.services.stripe_service import create_checkout_session
from app.schemas.payment import CheckoutSessionResponse

from datetime import datetime
from app.services.stripe_service import cancel_stripe_subscription
from app.schemas.subscription import SubscriptionCancel

from app.core.security import get_current_user, require_permission
from app.core.permissions import Permission
from app.schemas.user import CurrentUser

router = APIRouter(prefix="/payments", tags=["payments"])


@router.post(
    "/init",
    response_model=CheckoutSessionResponse,
    status_code=status.HTTP_201_CREATED,
)
def init_subscription(
    data: SubscriptionCreate,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(
        require_permission(Permission.CREATE_CHECKOUT)
    ),
):
    """
    Inicia una suscripcion en estado PENDING.
    Requiere JWT con permiso billing.create_checkout.
    """

    # 1 Validar que el plan exista y esté activo
    plan_stmt = select(Plan).where(
        Plan.code == data.plan_code,
        Plan.is_active == True,  # noqa: E712
    )
    plan = session.exec(plan_stmt).first()

    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El plan no existe o no está activo",
        )

    # 2 Crear suscripcion en estado pending
    subscription = Subscription(
        user_id=data.user_id,
        plan_id=plan.id,
        status="pending",
        provider="stripe",
    )

    session.add(subscription)
    session.commit()
    session.refresh(subscription)

    # 3 Crear Stripe Checkout Session
    checkout_session = create_checkout_session(
        plan_name=plan.name,
        amount=plan.price,
        currency=plan.currency,
        subscription_id=subscription.id,
        user_id=subscription.user_id,
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


@router.post("/subscriptions/{subscription_id}/cancel")
def cancel_subscription(
    subscription_id: int,
    data: SubscriptionCancel,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(
        require_permission(Permission.CANCEL_SUBSCRIPTION)
    ),
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


@router.post("/confirm")
def confirm_payment(
    data: dict,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(
        require_permission(Permission.VIEW_PAYMENTS)
    ),
):
    """
    Consulta el estado real de una sesion de checkout en Stripe.
    NO activa planes ni modifica la BD. Solo lectura.
    Endpoint de respaldo para cuando Django necesita verificar
    el estado post-redireccion desde success_url.
    """
    session_id = data.get("session_id")
    if not session_id:
        raise HTTPException(status_code=400, detail="session_id es requerido")

    try:
        checkout_session = stripe.checkout.Session.retrieve(session_id)
    except stripe.error.StripeError as e:
        return {
            "status": "not_found",
            "detail": str(e),
            "session_id": session_id,
        }

    subscription_info = None
    stripe_sub_id = checkout_session.get("subscription")
    if checkout_session.get("mode") == "subscription" and stripe_sub_id:
        try:
            stripe_sub = stripe.Subscription.retrieve(stripe_sub_id)
            subscription_info = {
                "stripe_status": stripe_sub.get("status"),
                "current_period_start": stripe_sub.get("current_period_start"),
                "current_period_end": stripe_sub.get("current_period_end"),
            }
        except stripe.error.StripeError:
            pass

    checkout_status = checkout_session.get("status")
    payment_status = checkout_session.get("payment_status")
    metadata = checkout_session.get("metadata", {}) or {}

    if checkout_status == "expired":
        our_status = "expired"
    elif payment_status == "paid":
        our_status = "paid"
        if subscription_info:
            our_status = subscription_info["stripe_status"]
    elif payment_status == "unpaid":
        our_status = "unpaid"
    else:
        our_status = "pending"

    customer_details = checkout_session.get("customer_details") or {}
    amount_total = checkout_session.get("amount_total", 0)

    return {
        "status": our_status,
        "payment_status": payment_status,
        "checkout_status": checkout_status,
        "mode": checkout_session.get("mode"),
        "subscription_id": metadata.get("subscription_id"),
        "customer_email": customer_details.get("email"),
        "amount_total": amount_total / 100 if amount_total else 0,
        "currency": checkout_session.get("currency", "mxn"),
    }


@router.get("/status/{subscription_id}")
def subscription_status(
    subscription_id: int,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(
        require_permission(Permission.VIEW_SUBSCRIPTION)
    ),
):
    """
    Consulta el estado local de una suscripcion.
    No consulta Stripe. Solo lectura.
    """
    subscription = session.get(Subscription, subscription_id)
    if not subscription:
        raise HTTPException(status_code=404, detail="Suscripcion no encontrada")

    plan = session.get(Plan, subscription.plan_id)

    return {
        "id": subscription.id,
        "user_id": subscription.user_id,
        "plan_code": plan.code if plan else None,
        "status": subscription.status,
        "provider": subscription.provider,
        "stripe_subscription_id": subscription.stripe_subscription_id,
        "start_date": str(subscription.start_date) if subscription.start_date else None,
        "end_date": str(subscription.end_date) if subscription.end_date else None,
        "cancel_at_period_end": subscription.cancel_at_period_end,
        "canceled_at": str(subscription.canceled_at) if subscription.canceled_at else None,
    }