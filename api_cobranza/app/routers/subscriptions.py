from datetime import datetime

from fastapi import APIRouter, HTTPException
from sqlmodel import Session, select

import stripe

from app.db.session import engine
from app.models.plan import Plan
from app.models.subscription import Subscription
from app.services.stripe_service import create_subscription_checkout_session, change_subscription_plan

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
            raise HTTPException(status_code=400, detail="Plan no valido")
        
        # Verificar si ya tiene suscripción activa
        active = db.exec(
            select(Subscription).where(
                Subscription.user_id == user_id,
                Subscription.status == "active"
            )
        ).first()

        if active:
            raise HTTPException(
                400,
                "El usuario ya tiene una suscripción activa"
            )


        # Buscar suscripción pendiente reutilizable
        existing = db.exec(
            select(Subscription).where(
                Subscription.user_id == user_id,
                Subscription.status.in_(["pending", "incomplete", "past_due"])
            )
        ).first()

        if existing:
            print("Reutilizando suscripción existente:", existing)
            
            # Actualizar plan si cambió
            if existing.plan_id != plan.id:
                existing.plan_id = plan.id
                db.add(existing)
                db.commit()
                db.refresh(existing)
        
            # Reutilizar suscripción
            session = create_subscription_checkout_session(
                stripe_price_id=plan.stripe_price_id,
                subscription_id=existing.id,
                user_id=user_id,
            )

            return {
                "checkout_url": session.url,
                "subscription_id": existing.id,
                "reused": True,
            }

        # Si no existe → crear nueva
        subscription = Subscription(
            user_id=user_id,
            plan_id=plan.id,
            status="pending",
            provider="stripe",
        )

        db.add(subscription)
        db.commit()
        db.refresh(subscription)

        session = create_subscription_checkout_session(
            stripe_price_id=plan.stripe_price_id,
            subscription_id=subscription.id,
            user_id=user_id,
        )

        return {
            "checkout_url": session.url,
            "subscription_id": subscription.id,
            "reused": False,
        }

# @router.post("/checkout")
# def start_subscription(
#     plan_code: str,
#     user_id: int,
# ):
#     with Session(engine) as db:
#         plan = db.exec(
#             select(Plan).where(
#                 Plan.code == plan_code,
#                 Plan.is_active == True,
#                 Plan.billing_type == "subscription",
#             )
#         ).first()

#         if not plan or not plan.stripe_price_id:
#             raise HTTPException(status_code=400, detail="Plan no valido para suscripcion")

#         # Crear suscripcion interna (pending)
#         subscription = Subscription(
#             user_id=user_id,
#             plan_id=plan.id,
#             status="pending",
#             provider="stripe",
#         )

#         db.add(subscription)
#         db.commit()
#         db.refresh(subscription)

#         # Crear checkout SaaS
#         session = create_subscription_checkout_session(
#             stripe_price_id=plan.stripe_price_id,
#             subscription_id=subscription.id,
#             user_id=user_id,
#         )

#         return {
#             "checkout_url": session.url,
#             "subscription_id": subscription.id,
#         }


@router.post("/change-plan")
def change_plan(user_id: int, new_plan_code: str):
    from app.db.session import engine
    from app.models.subscription import Subscription
    from app.models.plan import Plan
    from sqlmodel import Session, select
    import stripe

    with Session(engine) as db:

        # Obtener suscripción actual
        subscription = db.exec(
            select(Subscription).where(Subscription.user_id == user_id)
        ).first()

        if not subscription:
            raise HTTPException(404, "Suscripción no encontrada")

        # Plan actual
        current_plan = db.get(Plan, subscription.plan_id)

        # Nuevo plan
        new_plan = db.exec(
            select(Plan).where(Plan.code == new_plan_code)
        ).first()

        if not new_plan:
            raise HTTPException(400, "Plan inválido")

        if current_plan.id == new_plan.id:
            return {"message": "Ya está en ese plan"}

        # Obtener suscripción de Stripe
        stripe_sub = stripe.Subscription.retrieve(
            subscription.stripe_subscription_id
        )

        item_id = stripe_sub["items"]["data"][0]["id"]

        # =========================
        # CASO 1: UPGRADE
        # =========================
        if new_plan.price > current_plan.price:

            updated = stripe.Subscription.modify(
                subscription.stripe_subscription_id,
                items=[{
                    "id": item_id,
                    "price": new_plan.stripe_price_id
                }],
                proration_behavior="create_prorations"
            )

            # actualizar DB inmediato
            subscription.plan_id = new_plan.id

            db.add(subscription)
            db.commit()

            return {
                "message": "Upgrade aplicado inmediatamente",
                "type": "upgrade"
            }

        # =========================
        # CASO 2: DOWNGRADE
        # =========================
        else:

            # Crear schedule desde suscripción actual
            schedule = stripe.SubscriptionSchedule.create(
                from_subscription=subscription.stripe_subscription_id
            )

            # print("Programando downgrade al final del ciclo actual", stripe_sub)
            
            item = stripe_sub["items"]["data"][0]

            current_period_start = item["current_period_start"]
            current_period_end = item["current_period_end"]

            # Configurar fases
            stripe.SubscriptionSchedule.modify(
                schedule.id,
                phases=[
                    {
                        "items": [{
                            "price": current_plan.stripe_price_id,
                            "quantity": 1
                        }],
                        "start_date": current_period_start,
                        "end_date": current_period_end
                    },
                    {
                        "items": [{
                            "price": new_plan.stripe_price_id,
                            "quantity": 1
                        }],
                        "start_date": current_period_end
                    }
                ]
            )

            # guardar referencia en DB
            subscription.stripe_schedule_id = schedule.id

            db.add(subscription)
            db.commit()

            return {
                "message": "Downgrade programado al final del ciclo",
                "type": "downgrade",
                "effective_date": current_period_end
            }


# @router.post("/preview-plan-change")
# def preview_plan_change(
#     user_id: int,
#     new_plan_code: str
# ):
#     with Session(engine) as db:

#         subscription = db.exec(
#             select(Subscription).where(
#                 Subscription.user_id == user_id
#             )
#         ).first()

#         if not subscription:
#             raise HTTPException(400, "Subscription no encontrada")

#         new_plan = db.exec(
#             select(Plan).where(
#                 Plan.code == new_plan_code
#             )
#         ).first()

#         if not new_plan:
#             raise HTTPException(400, "Plan no valido")

#         stripe_sub = stripe.Subscription.retrieve(
#             subscription.stripe_subscription_id
#         )

#         item_id = stripe_sub["items"]["data"][0]["id"]

#         preview = stripe.Invoice.create_preview(
#             customer=stripe_sub.customer,
#             subscription=subscription.stripe_subscription_id,
#             subscription_details={
#                 "items": [{
#                     "id": item_id,
#                     "price": new_plan.stripe_price_id
#                 }],
#                 "proration_behavior": "always_invoice"
#             }
#         )
        
#         print("Preview:", preview)

#         return {
#             "amount_due": preview.amount_due / 100,
#             "currency": preview.currency,
#             "next_invoice_total": preview.total / 100
#         }
        
@router.post("/preview-plan-change")
def preview_plan_change(
    user_id: int,
    new_plan_code: str
):
    with Session(engine) as db:

        subscription = db.exec(
            select(Subscription).where(
                Subscription.user_id == user_id
            )
        ).first()

        if not subscription:
            raise HTTPException(400, "Subscription no encontrada")

        new_plan = db.exec(
            select(Plan).where(
                Plan.code == new_plan_code
            )
        ).first()

        if not new_plan:
            raise HTTPException(400, "Plan no valido")
        
        if subscription.plan_id == new_plan.id:
            raise HTTPException(
                status_code=400,
                detail="El usuario ya tiene ese plan"
            )

        current_plan = db.get(Plan, subscription.plan_id)

        upgrade = new_plan.price > current_plan.price
        downgrade = new_plan.price < current_plan.price
        
        if not upgrade and not downgrade:
            raise HTTPException(
                status_code=400,
                detail="El plan es equivalente"
            )

        behavior = "always_invoice" if upgrade else "create_prorations"

        stripe_sub = stripe.Subscription.retrieve(
            subscription.stripe_subscription_id
        )
        
        # print("Stripe Subscription:", stripe_sub)

        effective_date = datetime.fromtimestamp(
            stripe_sub["items"]["data"][0]["current_period_end"]
        ).date()

        # -------------------------
        # DOWNGRADE
        # -------------------------
        if downgrade:

            return {
                "change_type": "downgrade",
                "current_plan": current_plan.code,
                "new_plan": new_plan.code,
                "effective_date": effective_date,
                "amount_due_now": 0,
                "currency": stripe_sub["currency"],
                "message": f"Tu nuevo plan comenzará el {effective_date}"
            }

        # -------------------------
        # UPGRADE
        # -------------------------

        item_id = stripe_sub["items"]["data"][0]["id"]

        preview = stripe.Invoice.create_preview(
            customer=stripe_sub.customer,
            subscription=subscription.stripe_subscription_id,
            subscription_details={
                "items": [{
                    "id": item_id,
                    "price": new_plan.stripe_price_id
                }],
                "proration_behavior": "always_invoice"
            }
        )

        details = []

        for line in preview.lines.data:
            details.append({
                "description": line.description,
                "amount": line.amount / 100,
                "proration": line.parent.subscription_item_details.proration
            })

        return {
            "change_type": "upgrade",
            "current_plan": current_plan.code,
            "new_plan": new_plan.code,
            "amount_due_now": (preview.amount_due or 0) / 100,
            "next_invoice_total": (preview.total or 0) / 100,
            "currency": preview.currency,
            "details": details
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
        "canceled_at": subscription.canceled_at,
        "cancel_at_period_end": subscription.cancel_at_period_end,
        "puede_acceder": acceso
    }