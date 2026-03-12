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
def change_plan(
    user_id: int,
    new_plan_code: str,
):
    with Session(engine) as db:

        subscription = db.exec(
            select(Subscription).where(
                Subscription.user_id == user_id
            )
        ).first()

        if not subscription:
            raise HTTPException(
                status_code=400,
                detail="Subscription no encontrada"
            )

        if subscription.status not in ["active", "past_due"]:
            raise HTTPException(
                status_code=400,
                detail="Subscription not modifiable"
            )

        new_plan = db.exec(
            select(Plan).where(
                Plan.code == new_plan_code,
                Plan.is_active == True,
            )
        ).first()

        if not new_plan:
            raise HTTPException(
                status_code=400,
                detail="Plan no valido"
            )

        if not new_plan.stripe_price_id:
            raise HTTPException(
                status_code=400,
                detail="El plan no tiene stripe_price_id configurado"
            )

        if not subscription.stripe_subscription_id:
            raise HTTPException(
                status_code=400,
                detail="La suscripción no está vinculada a Stripe"
            )
    
        if subscription.plan_id == new_plan.id:
            raise HTTPException(
                status_code=400,
                detail="El usuario ya tiene ese plan"
            )
            
        current_plan = db.get(Plan, subscription.plan_id)

        # detectar upgrade o downgrade
        upgrade = new_plan.price > current_plan.price

        updated = change_subscription_plan(
            stripe_subscription_id=subscription.stripe_subscription_id,
            new_price_id=new_plan.stripe_price_id,
            upgrade=upgrade
        )

        subscription.plan_id = new_plan.id
        db.add(subscription)
        db.commit()

        return {
            "message": "Plan actualizado correctamente",
            "stripe_status": updated["status"]
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

        current_plan = db.get(Plan, subscription.plan_id)

        upgrade = new_plan.price > current_plan.price
        downgrade = new_plan.price < current_plan.price

        behavior = "always_invoice" if upgrade else "create_prorations"

        stripe_sub = stripe.Subscription.retrieve(
            subscription.stripe_subscription_id
        )

        item_id = stripe_sub["items"]["data"][0]["id"]

        preview = stripe.Invoice.create_preview(
            customer=stripe_sub.customer,
            subscription=subscription.stripe_subscription_id,
            subscription_details={
                "items": [{
                    "id": item_id,
                    "price": new_plan.stripe_price_id
                }],
                "proration_behavior": behavior
            }
        )

        details = []

        for line in preview.lines.data:
            details.append({
                "description": line.description,
                "amount": line.amount / 100,
                "proration": line.parent.subscription_item_details.proration,
            })

        return {
            "change_type": "upgrade" if upgrade else "downgrade",
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