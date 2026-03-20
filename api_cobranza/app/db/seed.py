from sqlmodel import Session, select

from app.models.plan import Plan
from app.db.session import engine


def seed_plans():
    initial_plans = [
        {
            "code": "free",
            "name": "Plan Free",
            "price": 0,
            "currency": "MXN",
            "interval": None,
            "billing_type": "one_time",
            "stripe_price_id": None,
        },
        {
            "code": "pro_mensual",
            "name": "Plan Pro Mensual",
            "price": 299,
            "currency": "MXN",
            "interval": None,
            "billing_type": "one_time",
            "stripe_price_id": None,
        },
        {
            "code": "PRO",
            "name": "Plan Pro Mensual",
            "price": 50,
            "currency": "MXN",
            "interval": "month",
            "billing_type": "subscription",
            "stripe_price_id": "price_1SpxPwL5PT8hTeNFOHIRI88j",
            "stripe_product_id": "prod_TnYWxFv5DzAgln",
        },
        {
            "code": "ENT",
            "name": "Enterprise",
            "price": 290,
            "currency": "MXN",
            "interval": "month",
            "billing_type": "subscription",
            "stripe_price_id": "price_1SpxWfL5PT8hTeNFZg83bi74",
            "stripe_product_id": "prod_TnYdJmtcXdyENp",
        },
    ]

    with Session(engine) as session:
        for plan_data in initial_plans:
            plan = session.exec(
                select(Plan).where(Plan.code == plan_data["code"])
            ).first()

            if not plan:
                session.add(Plan(**plan_data))
            else:
                # 🔥 OPCIONAL PERO RECOMENDADO
                plan.stripe_price_id = plan_data.get("stripe_price_id")
                plan.billing_type = plan_data["billing_type"]

        session.commit()