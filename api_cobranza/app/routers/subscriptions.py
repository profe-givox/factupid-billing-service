from fastapi import APIRouter, HTTPException
from sqlmodel import Session, select

from app.db.session import engine
from app.models.plan import Plan
from app.models.subscription import Subscription
from app.services.stripe_service import create_subscription_checkout_session

from app.services.subscription_service import obtener_subscription
from app.services.access_service import puede_acceder

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])


@router.post("/checkout")
def start_subscription(
    plan_code: str,
    user_id: int,
):
    with Session(engine) as db:
        plan = db.exec(
            select(Plan).where(
                Plan.code == plan_code,
                Plan.is_active == True,
                Plan.billing_type == "subscription",
            )
        ).first()

        if not plan or not plan.stripe_price_id:
            raise HTTPException(status_code=400, detail="Plan no valido para suscripcion")

        # Crear suscripcion interna (pending)
        subscription = Subscription(
            user_id=user_id,
            plan_id=plan.id,
            status="pending",
            provider="stripe",
        )

        db.add(subscription)
        db.commit()
        db.refresh(subscription)

        # Crear checkout SaaS
        session = create_subscription_checkout_session(
            stripe_price_id=plan.stripe_price_id,
            subscription_id=subscription.id,
            user_id=user_id,
        )

        return {
            "checkout_url": session.url,
            "subscription_id": subscription.id,
        }

@router.get("/test-access/{user_id}")
def test_access(user_id: int):

    subscription = obtener_subscription(user_id)

    if not subscription:
        raise HTTPException(status_code=404, detail="No subscription")

    acceso = puede_acceder(subscription)

    return {
        "user_id": user_id,
        "status": subscription.status,
        "end_date": subscription.end_date,
        "puede_acceder": acceso
    }