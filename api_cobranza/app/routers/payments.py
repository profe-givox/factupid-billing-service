from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.db.session import get_session
from app.models.plan import Plan
from app.models.subscription import Subscription
from app.schemas.subscription import SubscriptionCreate, SubscriptionRead

from app.services.stripe_service import create_checkout_session
from app.schemas.payment import CheckoutSessionResponse

router = APIRouter(prefix="/payments", tags=["payments"])


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
