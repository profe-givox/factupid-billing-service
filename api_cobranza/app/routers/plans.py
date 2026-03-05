from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.db.session import get_session
from app.models.plan import Plan
from app.schemas.plan import PlanRead

from fastapi import APIRouter, HTTPException
from sqlmodel import Session, select
import stripe
from app.db.session import engine
from app.models.plan import Plan
from app.schemas.plan import PlanCreate, PlanRegister

router = APIRouter(prefix="/plans", tags=["plans"])


@router.get("/", response_model=list[PlanRead])
def list_plans(session: Session = Depends(get_session)):
    """
    Devuelve la lista de planes activos desde la base de datos.
    """
    statement = select(Plan).where(Plan.is_active == True)  # noqa: E712
    plans = session.exec(statement).all()

    # Mapeo: BD → Schema (exponemos code como id)
    return [
        PlanRead(
            id=plan.code,
            name=plan.name,
            price=plan.price,
            currency=plan.currency,
            interval=plan.interval,
        )
        for plan in plans
    ]

@router.post("/plans/create-stripe")
def create_plan_stripe(plan_data: PlanCreate):

    with Session(engine) as session:

        existing = session.exec(
            select(Plan).where(Plan.code == plan_data.code)
        ).first()

        if existing:
            raise HTTPException(400, "Plan code already exists")

        product = stripe.Product.create(
            name=plan_data.name,
        )

        price = stripe.Price.create(
            product=product.id,
            unit_amount=int(plan_data.price * 100),
            currency=plan_data.currency.lower(),
            recurring={"interval": plan_data.interval}
        )

        new_plan = Plan(
            code=plan_data.code,
            name=plan_data.name,
            price=plan_data.price,
            currency=plan_data.currency,
            interval=plan_data.interval,
            billing_type=plan_data.billing_type,
            stripe_product_id=product.id,
            stripe_price_id=price.id
        )

        session.add(new_plan)
        session.commit()
        session.refresh(new_plan)

        return new_plan
    
@router.post("/plans/register")
def register_plan(plan_data: PlanRegister):

    with Session(engine) as session:

        existing = session.exec(
            select(Plan).where(Plan.code == plan_data.code)
        ).first()

        if existing:
            raise HTTPException(400, "Plan code already exists")

        try:
            stripe.Product.retrieve(plan_data.stripe_product_id)
            stripe.Price.retrieve(plan_data.stripe_price_id)
        except Exception:
            raise HTTPException(400, "Invalid Stripe IDs")

        new_plan = Plan(
            code=plan_data.code,
            name=plan_data.name,
            price=plan_data.price,
            currency=plan_data.currency,
            interval=plan_data.interval,
            billing_type=plan_data.billing_type,
            stripe_product_id=plan_data.stripe_product_id,
            stripe_price_id=plan_data.stripe_price_id
        )

        session.add(new_plan)
        session.commit()
        session.refresh(new_plan)

        return new_plan