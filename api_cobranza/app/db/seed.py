from sqlmodel import Session, select

from app.models.plan import Plan
from app.db.session import engine


def seed_plans():
    """
    Inserta planes iniciales en la base de datos
    solo si no existen.
    """

    initial_plans = [
        {
            "code": "free",
            "name": "Plan Free",
            "price": 0,
            "currency": "MXN",
            "interval": None,
        },
        {
            "code": "pro_mensual",
            "name": "Plan Pro Mensual",
            "price": 299,
            "currency": "MXN",
            "interval": "month",
        },
    ]

    with Session(engine) as session:
        for plan_data in initial_plans:
            statement = select(Plan).where(Plan.code == plan_data["code"])
            existing_plan = session.exec(statement).first()

            if not existing_plan:
                plan = Plan(**plan_data)
                session.add(plan)

        session.commit()
