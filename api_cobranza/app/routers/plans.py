from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.db.session import get_session
from app.models.plan import Plan
from app.schemas.plan import PlanRead

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
