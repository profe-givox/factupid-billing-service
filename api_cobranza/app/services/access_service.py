from datetime import date

def puede_acceder(subscription) -> bool:
    """
    Determina si el usuario puede acceder al sistema
    según el estado actual de su suscripción.

    Política:
    - active → acceso completo
    - trialing → acceso completo
    - past_due → acceso permitido mientras Stripe intenta cobrar
    - unpaid → acceso bloqueado
    - canceled → acceso bloqueado
    - incomplete → acceso bloqueado
    - incomplete_expired → acceso bloqueado
    - paused → acceso bloqueado
    """

    if not subscription:
        return False

    estado = subscription.status

    if estado in ["active", "trialing", "past_due"]:
        return True

    if estado == "canceled":
        if subscription.end_date and subscription.end_date >= date.today():
            return True

    return False