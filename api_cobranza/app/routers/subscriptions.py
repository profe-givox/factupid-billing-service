from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select

import stripe

from app.db.session import engine
from app.models.plan import Plan
from app.models.subscription import Subscription
from app.services.stripe_service import create_subscription_checkout_session, change_subscription_plan

from app.services.subscription_service import obtener_subscription
from app.services.access_service import puede_acceder

from app.core.security import get_current_user, require_permission
from app.core.permissions import Permission
from app.schemas.user import CurrentUser
from app.schemas.subscription import (
    RegularizePaymentRequest,
    SubscriptionIdRequest,
    ReportOverageRequest,
)
from app.services.stripe_service import (
    create_subscription_checkout_session,
    change_subscription_plan,
    create_billing_portal_session,
    reactivate_stripe_subscription,
    release_stripe_schedule_if_possible,
)
from app.routers.webhooks import (
    _resolve_billing_code_for_subscription,
    notify_subscription_event,
)

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])

@router.post("/checkout")
def start_subscription(
    plan_code: str,
    user_id: int,
    current_user: CurrentUser = Depends(
        require_permission(Permission.CREATE_CHECKOUT)
    ),
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
            current_plan = db.get(Plan, active.plan_id)

            raise HTTPException(
                status_code=409,
                detail={
                    "code": "ACTIVE_SUBSCRIPTION_EXISTS",
                    "message": "El usuario ya tiene una suscripción activa",
                    "subscription": {
                        "id": active.id,
                        "status": active.status,
                        "plan_id": active.plan_id,
                        "plan_code": current_plan.code if current_plan else None,
                        "plan_name": current_plan.name if current_plan else None,
                    },
                    "suggested_action": "CHANGE_PLAN",
                },
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
        
        print("Creando nueva suscripción:", subscription)

        return {
            "checkout_url": session.url,
            "subscription_id": subscription.id,
            "reused": False,
        }


@router.post("/regularize-payment")
def regularize_payment(
    payload: RegularizePaymentRequest,
    current_user: CurrentUser = Depends(
        require_permission(Permission.CREATE_CHECKOUT)
    ),
):
    """
    Crea una sesión del portal de cliente de Stripe para que el usuario
    regularice el pago de una suscripción en estado past_due o unpaid.

    Reglas:
      - Solo se permite para estados past_due/unpaid.
      - La suscripción debe pertenecer al user_id indicado.
      - No modifica el estado de la suscripción: la actualización llega por
        webhook cuando Stripe procesa el pago.
    """
    with Session(engine) as db:
        subscription = db.get(Subscription, payload.subscription_id)

        if not subscription:
            raise HTTPException(status_code=404, detail="Suscripción no encontrada")

        if subscription.user_id != payload.user_id:
            raise HTTPException(
                status_code=403,
                detail="La suscripción no pertenece al usuario",
            )

        if subscription.status not in ("past_due", "unpaid"):
            raise HTTPException(
                status_code=400,
                detail={
                    "code": "SUBSCRIPTION_NOT_PENDING",
                    "message": (
                        "Solo se puede regularizar el pago de suscripciones "
                        "en estado past_due o unpaid"
                    ),
                    "status": subscription.status,
                },
            )

        # Obtener stripe_customer_id, recuperándolo de Stripe si hace falta
        customer_id = subscription.stripe_customer_id

        if not customer_id and subscription.stripe_subscription_id:
            try:
                stripe_sub = stripe.Subscription.retrieve(
                    subscription.stripe_subscription_id
                )
                customer_id = stripe_sub.get("customer")
            except stripe.error.StripeError as exc:
                raise HTTPException(
                    status_code=502,
                    detail={
                        "message": "Error comunicando con Stripe.",
                        "stripe_error": str(exc),
                    },
                )

        if not customer_id:
            raise HTTPException(
                status_code=400,
                detail="No se encontró el cliente de Stripe para esta suscripción",
            )

        if not subscription.stripe_customer_id:
            subscription.stripe_customer_id = customer_id
            db.add(subscription)
            db.commit()

        try:
            session = create_billing_portal_session(
                customer_id=customer_id,
                return_url=payload.return_url,
            )
        except stripe.error.StripeError as exc:
            raise HTTPException(
                status_code=502,
                detail={
                    "message": "Error comunicando con Stripe.",
                    "stripe_error": str(exc),
                },
            )

        return {
            "url": session.url,
            "subscription_id": subscription.id,
            "status": subscription.status,
        }


@router.post("/reactivate-cancel-scheduled")
def reactivate_cancel_scheduled(
    payload: SubscriptionIdRequest,
    current_user: CurrentUser = Depends(
        require_permission(Permission.CANCEL_SUBSCRIPTION)
    ),
):
    """
    Revierte una cancelación programada para conservar la suscripción.

    Solo se permite si la suscripción tiene cancel_at_period_end=True o
    estado cancel_scheduled. Llama a Stripe con cancel_at_period_end=False,
    actualiza la BD local y notifica a Django (subscription_reactivated).

    No borra información ni reinicia timbres.
    """
    with Session(engine) as db:
        subscription = db.get(Subscription, payload.subscription_id)

        if not subscription:
            raise HTTPException(status_code=404, detail="Suscripción no encontrada")

        if not (
            subscription.cancel_at_period_end
            or subscription.status == "cancel_scheduled"
        ):
            raise HTTPException(
                status_code=400,
                detail={
                    "code": "NO_CANCEL_SCHEDULED",
                    "message": (
                        "La suscripción no tiene una cancelación programada"
                    ),
                    "status": subscription.status,
                    "cancel_at_period_end": subscription.cancel_at_period_end,
                },
            )

        if not subscription.stripe_subscription_id:
            raise HTTPException(
                status_code=400,
                detail="Suscripción no vinculada a Stripe",
            )

        try:
            reactivate_stripe_subscription(
                stripe_subscription_id=subscription.stripe_subscription_id,
            )
        except stripe.error.StripeError as exc:
            raise HTTPException(
                status_code=502,
                detail={
                    "message": "Error comunicando con Stripe.",
                    "stripe_error": str(exc),
                },
            )

        # Actualizar BD local
        subscription.cancel_at_period_end = False
        subscription.status = "active"
        subscription.canceled_at = None

        db.add(subscription)
        db.commit()
        db.refresh(subscription)

        billing_code = _resolve_billing_code_for_subscription(db, subscription)

        if not billing_code:
            print(
                f"ERROR: No se pudo resolver billing_code para "
                f"subscription_id={subscription.id}"
            )
            return {"status": "ok"}

        notify_subscription_event(
            event_type="subscription_reactivated",
            user_id=subscription.user_id,
            billing_code=billing_code,
            subscription_id=subscription.id,
            plan_id=subscription.plan_id,
            date_cutoff=subscription.end_date,
            period_start=subscription.start_date,
            period_end=subscription.end_date,
            cancel_at_period_end=False,
            stripe_subscription_id=subscription.stripe_subscription_id,
        )

        return {
            "status": "ok",
            "subscription_id": subscription.id,
            "subscription_status": "active",
            "cancel_at_period_end": False,
        }


@router.post("/report-overage")
def report_overage(
    payload: ReportOverageRequest,
    current_user: CurrentUser = Depends(
        require_permission(Permission.REGISTER_SUBSCRIPTION)
    ),
):
    """
    Reporta excedentes de timbres CFDI (OnDemand) a Stripe como un invoice item.

    Fase 7B: Django calcula el excedente del periodo (CfdiOveragePeriod) y lo
    envía aquí; Billing lo convierte en un Stripe invoice item del cliente.
    NO se crea factura inmediata ni se cambia el estado de la suscripción.

    Reglas:
      - Solo se permite para estados active, cancel_scheduled o canceled.
      - Se rechaza si la suscripción está past_due o unpaid.
      - amount = total_amount * 100 (centavos), currency "mxn".
    """
    with Session(engine) as db:
        subscription = db.get(Subscription, payload.subscription_id)

        if not subscription:
            raise HTTPException(status_code=404, detail="Suscripción no encontrada")

        if subscription.user_id != payload.user_id:
            raise HTTPException(
                status_code=403,
                detail="La suscripción no pertenece al usuario",
            )

        if subscription.status in ("past_due", "unpaid"):
            raise HTTPException(
                status_code=400,
                detail={
                    "code": "SUBSCRIPTION_OVERDUE",
                    "message": (
                        "No se puede reportar excedentes con un pago pendiente. "
                        "Regulariza primero la suscripción."
                    ),
                    "status": subscription.status,
                },
            )

        if subscription.status not in ("active", "cancel_scheduled", "canceled"):
            raise HTTPException(
                status_code=400,
                detail={
                    "code": "SUBSCRIPTION_NOT_BILLABLE",
                    "message": (
                        "La suscripción no está en un estado facturable"
                    ),
                    "status": subscription.status,
                },
            )

        if payload.quantity <= 0:
            raise HTTPException(
                status_code=400,
                detail="quantity debe ser mayor a 0",
            )

        if payload.total_amount <= 0:
            raise HTTPException(
                status_code=400,
                detail="total_amount debe ser mayor a 0",
            )

        # Obtener stripe_customer_id, recuperándolo de Stripe si hace falta
        customer_id = subscription.stripe_customer_id

        if not customer_id and subscription.stripe_subscription_id:
            try:
                stripe_sub = stripe.Subscription.retrieve(
                    subscription.stripe_subscription_id
                )
                customer_id = stripe_sub.get("customer")
            except stripe.error.StripeError as exc:
                raise HTTPException(
                    status_code=502,
                    detail={
                        "message": "Error comunicando con Stripe.",
                        "stripe_error": str(exc),
                    },
                )

        if not customer_id:
            raise HTTPException(
                status_code=400,
                detail="No se encontró el cliente de Stripe para esta suscripción",
            )

        if not subscription.stripe_customer_id and customer_id:
            subscription.stripe_customer_id = customer_id
            db.add(subscription)
            db.commit()

        amount_cents = int(round(payload.total_amount * 100))
        currency = (payload.currency or "mxn").lower()

        period_start = str(payload.period_start)[:10]
        period_end = str(payload.period_end)[:10]
        report_sequence = payload.report_sequence or 0

        description = payload.description or (
            f"{payload.quantity} timbres CFDI excedentes - "
            f"lote {report_sequence} - periodo {period_start} a {period_end}"
        )

        try:
            invoice_item = stripe.InvoiceItem.create(
                customer=customer_id,
                amount=amount_cents,
                currency=currency,
                description=description,
                metadata={
                    "factupid_type": "cfdi_overage",
                    "user_id": str(payload.user_id),
                    "subscription_id": str(payload.subscription_id),
                    "overage_period_id": str(payload.overage_period_id),
                    "period_start": str(payload.period_start),
                    "period_end": str(payload.period_end),
                    "quantity": str(payload.quantity),
                    "unit_price": str(payload.unit_price),
                    "report_sequence": str(report_sequence),
                },
            )
        except stripe.error.StripeError as exc:
            raise HTTPException(
                status_code=502,
                detail={
                    "message": "Error comunicando con Stripe.",
                    "stripe_error": str(exc),
                },
            )

        return {
            "success": True,
            "stripe_invoice_item_id": invoice_item.id,
            "amount": amount_cents,
            "currency": currency,
        }


@router.post("/cancel-scheduled-plan-change")
def cancel_scheduled_plan_change(
    payload: SubscriptionIdRequest,
    current_user: CurrentUser = Depends(
        require_permission(Permission.CHANGE_SUBSCRIPTION_PLAN)
    ),
):
    """
    Cancela un cambio de plan programado (downgrade/upgrade futuro).

    Si existe stripe_schedule_id:
      - Se recupera el schedule en Stripe.
      - Si está activo/not_started se libera con release.
      - Si ya está released/completed/canceled no se falla.
      - Se limpia stripe_schedule_id local.
    No cambia el plan actual, no reinicia timbres y no borra información.
    """
    with Session(engine) as db:
        subscription = db.get(Subscription, payload.subscription_id)

        if not subscription:
            raise HTTPException(status_code=404, detail="Suscripción no encontrada")

        if not subscription.stripe_schedule_id:
            raise HTTPException(
                status_code=400,
                detail={
                    "code": "NO_SCHEDULED_PLAN_CHANGE",
                    "message": (
                        "No hay un cambio de plan programado para esta suscripción"
                    ),
                },
            )

        released, schedule_status, error = release_stripe_schedule_if_possible(
            stripe_schedule_id=subscription.stripe_schedule_id,
        )

        # Si Stripe no está disponible o el release falló, no limpiamos el ID
        # local: el schedule sigue existiendo y bloqueando. Solo se limpia si
        # se liberó con éxito o si el schedule ya está en estado terminal.
        if error:
            raise HTTPException(
                status_code=502,
                detail={
                    "message": "Error comunicando con Stripe.",
                    "stripe_error": error,
                },
            )

        if not released and schedule_status not in ("released", "completed", "canceled"):
            raise HTTPException(
                status_code=400,
                detail={
                    "code": "SCHEDULE_NOT_RELEASED",
                    "message": (
                        "No se pudo liberar el cambio de plan programado "
                        f"(estado: {schedule_status})"
                    ),
                    "schedule_status": schedule_status,
                },
            )

        subscription.stripe_schedule_id = None
        subscription.status = "active"

        db.add(subscription)
        db.commit()
        db.refresh(subscription)

        billing_code = _resolve_billing_code_for_subscription(db, subscription)

        if not billing_code:
            print(
                f"ERROR: No se pudo resolver billing_code para "
                f"subscription_id={subscription.id}"
            )
            return {"status": "ok"}

        notify_subscription_event(
            event_type="subscription_plan_change_canceled",
            user_id=subscription.user_id,
            billing_code=billing_code,
            subscription_id=subscription.id,
            plan_id=subscription.plan_id,
            date_cutoff=subscription.end_date,
            period_end=subscription.end_date,
            stripe_subscription_id=subscription.stripe_subscription_id,
        )

        return {
            "status": "ok",
            "subscription_id": subscription.id,
            "released": released,
            "schedule_status": schedule_status,
            "stripe_schedule_id": None,
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
    current_user: CurrentUser = Depends(
        require_permission(Permission.CHANGE_SUBSCRIPTION_PLAN)
    ),
):
    from app.models.subscription import Subscription
    from app.models.plan import Plan
    from sqlmodel import Session, select
    import stripe

    with Session(engine) as db:

        # Obtener suscripción actual
        subscription = db.exec(
            select(Subscription).where(
                Subscription.user_id == user_id, 
                Subscription.status == "active"
            )
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

            try:
                updated = stripe.Subscription.modify(
                    subscription.stripe_subscription_id,
                    items=[{
                        "id": item_id,
                        "price": new_plan.stripe_price_id,
                    }],
                    proration_behavior="always_invoice",
                    payment_behavior="pending_if_incomplete",
                    expand=["latest_invoice.payment_intent"],
                    metadata={
                        "subscription_id": str(subscription.id),
                        "user_id": str(subscription.user_id),
                        "change_type": "upgrade",
                        "old_plan_id": str(current_plan.id),
                        "new_plan_id": str(new_plan.id),
                        "new_plan_code": new_plan.code,
                    },
                )

            except stripe.error.CardError as exc:
                raise HTTPException(
                    status_code=402,
                    detail={
                        "message": "No se pudo cobrar el cambio de plan.",
                        "stripe_error": str(exc),
                    },
                )

            except stripe.error.StripeError as exc:
                raise HTTPException(
                    status_code=502,
                    detail={
                        "message": "Error comunicando con Stripe.",
                        "stripe_error": str(exc),
                    },
                )

            # No actualizar DB local todavía.
            # El cambio local debe aplicarse cuando llegue webhook de Stripe:
            # invoice.payment_succeeded / customer.subscription.updated
            # y el pago del prorrateo esté confirmado.

            latest_invoice = updated.get("latest_invoice")
            payment_intent = None

            if latest_invoice and isinstance(latest_invoice, dict):
                payment_intent = latest_invoice.get("payment_intent")

            return {
                "message": "Upgrade iniciado. Stripe intentará cobrar la diferencia inmediatamente.",
                "type": "upgrade",
                "stripe_subscription_id": updated["id"],
                "status": updated.get("status"),
                "latest_invoice": latest_invoice.get("id") if isinstance(latest_invoice, dict) else latest_invoice,
                "payment_intent_status": payment_intent.get("status") if isinstance(payment_intent, dict) else None,
                "requires_action": (
                    payment_intent.get("status") in ["requires_action", "requires_confirmation"]
                    if isinstance(payment_intent, dict)
                    else False
                ),
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
            db.refresh(subscription)

            # Notificar a Django el downgrade programado. Django guarda una
            # copia visual mínima (plan destino + fecha) para que el aviso no
            # dependa de que Billing esté disponible. El cambio real se
            # notifica después con subscription_plan_changed.
            effective_date = datetime.fromtimestamp(
                current_period_end, tz=timezone.utc,
            ).date().isoformat()

            billing_code = _resolve_billing_code_for_subscription(db, subscription)

            if billing_code:
                notify_subscription_event(
                    event_type="subscription_plan_change_scheduled",
                    user_id=subscription.user_id,
                    billing_code=billing_code,
                    subscription_id=subscription.id,
                    plan_id=subscription.plan_id,
                    date_cutoff=subscription.end_date,
                    period_end=subscription.end_date,
                    stripe_subscription_id=subscription.stripe_subscription_id,
                    full_payload={
                        "event_type": "subscription_plan_change_scheduled",
                        "user_id": subscription.user_id,
                        "billing_code": billing_code,
                        "subscription_id": subscription.id,
                        "plan_id": subscription.plan_id,
                        "scheduled_billing_code": new_plan.code,
                        "scheduled_plan_id": new_plan.id,
                        "effective_date": effective_date,
                        "change_type": "downgrade",
                    },
                )
            else:
                print(
                    f"ERROR: No se pudo resolver billing_code para "
                    f"subscription_id={subscription.id} al programar downgrade"
                )

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
    new_plan_code: str,
    current_user: CurrentUser = Depends(
        require_permission(Permission.CHANGE_SUBSCRIPTION_PLAN)
    ),
):
    with Session(engine) as db:

        subscription = db.exec(
            select(Subscription).where(
                Subscription.user_id == user_id,
                Subscription.status == "active"
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
def test_access(
    user_id: int,
    current_user: CurrentUser = Depends(
        require_permission(Permission.VIEW_SUBSCRIPTION)
    ),
):

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