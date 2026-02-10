import stripe
from app.core.config import settings


stripe.api_key = settings.STRIPE_SECRET_KEY


def _ensure_session_id(success_url: str) -> str:
    if "{CHECKOUT_SESSION_ID}" in success_url:
        return success_url
    if "session_id=" in success_url:
        return success_url
    sep = "&" if "?" in success_url else "?"
    return f"{success_url}{sep}session_id={{CHECKOUT_SESSION_ID}}"


def create_checkout_session(
    *,
    plan_name: str,
    amount: int,
    currency: str,
    subscription_id: int,
    user_id: int,

    plan_code: str,

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

            "plan_code": plan_code,
        },
        payment_intent_data={
            "metadata": {
                "subscription_id": str(subscription_id),
                "user_id": str(user_id),
                "plan_code": plan_code,

            }
        },
        
        success_url=_ensure_session_id(settings.STRIPE_SUCCESS_URL),
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

    plan_code: str,

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

            "plan_code": plan_code,

        },
   
  
        success_url=_ensure_session_id(settings.STRIPE_SUCCESS_URL),
        cancel_url=settings.STRIPE_CANCEL_URL,
    )

    return session
