import logging

import stripe
from app.core.config import settings


stripe.api_key = settings.STRIPE_SECRET_KEY

logger = logging.getLogger(__name__)


def create_checkout_session(
    *,
    plan_name: str,
    amount: int,
    currency: str,
    subscription_id: int,
    user_id: int,
) -> stripe.checkout.Session:
    """
    Crea una Stripe Checkout Session asociada a una suscripcion pending.
    """

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        mode="payment",
        line_items=[
            {
                "price_data": {
                    "currency": currency.lower(),
                    "product_data": {
                        "name": plan_name,
                    },
                    "unit_amount": amount * 100,  # Stripe usa centavos
                },
                "quantity": 1,
            }
        ],
        metadata={
            "subscription_id": str(subscription_id),
            "user_id": str(user_id),
        },
        payment_intent_data={
        "metadata": {
            "subscription_id": str(subscription_id),
            "user_id": str(user_id),
            }
        },
        
        success_url=settings.STRIPE_SUCCESS_URL,
        cancel_url=settings.STRIPE_CANCEL_URL,
    )

    return session

# En Stripe:

# modify(cancel_at_period_end=True) → cancelación futura

# delete(subscription) → cancelación inmediata real
def cancel_stripe_subscription(
    *,
    stripe_subscription_id: str,
    at_period_end: bool = True,
):
    """
    Cancela una suscripción en Stripe.
    """
    # return stripe.Subscription.modify(
    #     stripe_subscription_id,
    #     cancel_at_period_end=at_period_end,
    # )
    if at_period_end:
        # Cancelación programada
        return stripe.Subscription.modify(
            stripe_subscription_id,
            cancel_at_period_end=True,
        )
    else:
        # Cancelación inmediata
        return stripe.Subscription.delete(
            stripe_subscription_id
        )


def create_subscription_checkout_session(
    *,
    stripe_price_id: str,
    subscription_id: int,
    user_id: int,
) -> stripe.checkout.Session:
    """
    Crea una Checkout Session para suscripción SaaS real.
    """

    session = stripe.checkout.Session.create(
        mode="subscription",
        payment_method_types=["card"],
        line_items=[
            {
                "price": stripe_price_id,
                "quantity": 1,
            }
        ],
        metadata={
            "subscription_id": str(subscription_id),
            "user_id": str(user_id),
        },
        subscription_data={  #
            "metadata": {
                "subscription_id": str(subscription_id),
                "user_id": str(user_id),
            }
        },
        success_url=settings.STRIPE_SUCCESS_URL,
        cancel_url=settings.STRIPE_CANCEL_URL,
    )

    return session

def change_subscription_plan(
    stripe_subscription_id: str,
    new_price_id: str,
    upgrade: bool
):

    behavior = "always_invoice" if upgrade else "create_prorations"

    subscription = stripe.Subscription.retrieve(
        stripe_subscription_id
    )

    item_id = subscription["items"]["data"][0]["id"]

    return stripe.Subscription.modify(
        stripe_subscription_id,
        items=[{
            "id": item_id,
            "price": new_price_id
        }],
        proration_behavior=behavior
    )


def create_billing_portal_session(
    *,
    customer_id: str,
    return_url: str,
) -> stripe.billing_portal.Session:
    """
    Crea una sesión del portal de cliente de Stripe para que el usuario
    pueda regularizar un pago pendiente o actualizar su método de pago.
    """
    session = stripe.billing_portal.Session.create(
        customer=customer_id,
        return_url=return_url,
    )
    return session


def reactivate_stripe_subscription(
    *,
    stripe_subscription_id: str,
) -> stripe.Subscription:
    """
    Revierte una cancelación programada en Stripe:
    pone cancel_at_period_end=False para conservar la suscripción.
    """
    return stripe.Subscription.modify(
        stripe_subscription_id,
        cancel_at_period_end=False,
    )


def get_schedule_id_for_stripe_subscription(
    *,
    stripe_subscription_id: str,
) -> str | None:
    """
    Identifica el SubscriptionSchedule que gestiona una suscripción en Stripe.
    Retorna el ID del schedule o None si no hay asociado.
    """
    if not stripe_subscription_id:
        return None

    try:
        subscription = stripe.Subscription.retrieve(stripe_subscription_id)
    except stripe.error.StripeError as exc:
        logger.warning(
            "No se pudo recuperar la suscripción %s para buscar schedule: %s",
            stripe_subscription_id, exc,
        )
        return None

    schedule_id = subscription.get("schedule")
    return schedule_id if schedule_id else None


def release_stripe_schedule_if_possible(
    *,
    stripe_schedule_id: str,
) -> tuple[bool, str | None, str | None]:
    """
    Libera un SubscriptionSchedule de Stripe si está activo o not_started.

    Regla de Stripe: para quitar un schedule de una suscripción sin cancelarla
    hay que llamar release. Si el schedule ya fue liberado, cancelado o
    completado, release fallaría; en ese caso no se intenta.

    Retorna (released, status, error):
      - released: True si se llamó release con éxito.
      - status: estado del schedule (active, not_started, released, completed,
        canceled) o None si no se pudo recuperar.
      - error: mensaje si ocurrió un error de Stripe, None en caso contrario.
    """
    if not stripe_schedule_id:
        return False, None, None

    try:
        schedule = stripe.SubscriptionSchedule.retrieve(stripe_schedule_id)
    except stripe.error.StripeError as exc:
        return False, None, str(exc)

    status_value = schedule.get("status")

    if status_value in ("active", "not_started"):
        try:
            stripe.SubscriptionSchedule.release(stripe_schedule_id)
            return True, status_value, None
        except stripe.error.StripeError as exc:
            return False, status_value, str(exc)

    return False, status_value, None