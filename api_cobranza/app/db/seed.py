from sqlmodel import Session, select

from app.models.plan import Plan
from app.db.session import engine


def seed_plans():
    initial_plans = [
        {
            "code": "CFDI_FREE",
            "name": "Plan Free",
            "price": 0,
            "currency": "MXN",
            "interval": None,
            "billing_type": "one_time",
            "stripe_price_id": None,
        },
        {
            "code": "CFDI_PRUEBA_PAYMENT",
            "name": "Plan prueba pago unico",
            "price": 299,
            "currency": "MXN",
            "interval": None,
            "billing_type": "one_time",
            "stripe_price_id": None,
        },
        {
            "code": "CFDI_PRO",
            "name": "Plan PRO Mensual",
            "price": 50,
            "currency": "MXN",
            "interval": "month",
            "billing_type": "subscription",
            "stripe_price_id": "price_1SpxPwL5PT8hTeNFOHIRI88j",
            "stripe_product_id": "prod_TnYWxFv5DzAgln",
        },
        {
            "code": "CFDI_ENTERPRISE",
            "name": "Plan Enterprise Mensual",
            "price": 290,
            "currency": "MXN",
            "interval": "month",
            "billing_type": "subscription",
            "stripe_price_id": "price_1SpxWfL5PT8hTeNFZg83bi74",
            "stripe_product_id": "prod_TnYdJmtcXdyENp",
        },
        {
            "code": "CFDI_ONDEMAND",
            "name": "Plan OnDemand Mensual",
            "price": 110,
            "currency": "MXN",
            "interval": "month",
            "billing_type": "subscription",
            "stripe_price_id": "price_1SpxRAL5PT8hTeNF3UJYqrQq",
            "stripe_product_id": "prod_TnYYiQuRZb9BFj",
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
                plan.name = plan_data["name"]
                plan.price = plan_data["price"]
                plan.currency = plan_data["currency"]
                plan.interval = plan_data["interval"]
                plan.billing_type = plan_data["billing_type"]
                plan.stripe_price_id = plan_data.get("stripe_price_id")
                plan.stripe_product_id = plan_data.get("stripe_product_id")

        session.commit()