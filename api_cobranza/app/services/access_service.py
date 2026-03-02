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

    from datetime import date

def puede_acceder(subscription) -> bool:
    if not subscription:
        return False

    estado = subscription.status

    # Estados activos
    if estado in ["active", "trialing"]:
        return True

    # Stripe intentando cobrar
    if estado == "past_due":
        return True

    # Cancelada pero aún dentro del periodo pagado
    if estado == "canceled":
        if subscription.cancel_at_period_end:
            if subscription.end_date and subscription.end_date >= date.today():
                return True
        return False

    return False