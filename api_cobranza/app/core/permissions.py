"""
Constantes de permisos para la API de billing.

Estos permisos deben coincidir exactamente con los creados en Django
en auth_permission y con los que viajan en el JWT.
"""

class Permission:
    # === CLIENTE BILLING ===
    REGISTER_SUBSCRIPTION   = "billing.register_subscription"
    VIEW_SUBSCRIPTION       = "billing.view_subscription"
    CANCEL_SUBSCRIPTION     = "billing.cancel_subscription"
    CHANGE_SUBSCRIPTION_PLAN = "billing.change_subscription_plan"
    CREATE_CHECKOUT         = "billing.create_checkout"
    VIEW_PAYMENTS           = "billing.view_payments"