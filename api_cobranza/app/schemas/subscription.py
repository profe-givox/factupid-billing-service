from typing import Optional
from datetime import date, datetime

from pydantic import BaseModel

class SubscriptionBase(BaseModel):
    """
    Campos comunes de una suscripcion.
    """
    user_id: int
    plan_code: str


class SubscriptionCreate(SubscriptionBase):
    """
    Schema usado cuando se crea una suscripcion (antes del pago).
    """
    pass


class SubscriptionRead(BaseModel):
    """
    Schema de salida para exponer el estado de una suscripcion.
    """
    id: int
    user_id: int
    plan_code: str
    status: str
    start_date: Optional[date]
    end_date: Optional[date]
    provider: str
    created_at: datetime
    
class SubscriptionCancel(BaseModel):
    at_period_end: bool = True


class RegularizePaymentRequest(BaseModel):
    """
    Petición para crear una sesión del portal de cliente de Stripe y
    regularizar el pago de una suscripción past_due/unpaid.
    """
    subscription_id: int
    user_id: int
    return_url: str


class SubscriptionIdRequest(BaseModel):
    """
    Petición genérica con solo el ID interno de una suscripción.
    """
    subscription_id: int


class ReportOverageRequest(BaseModel):
    """
    Petición para reportar excedentes de timbres CFDI a Stripe como un
    invoice item (Fase 7C delta).

    quantity es el delta pendiente (overage_quantity - reported_quantity),
    NO el total del periodo. Billing lo trata como un lote independiente.

    idempotency_key es una cadena determinística generada por Django para
    evitar invoice items duplicados en Stripe.
    """
    subscription_id: int
    user_id: int
    overage_period_id: int
    period_start: str
    period_end: str
    quantity: int
    unit_price: float
    total_amount: float
    currency: str = "mxn"
    description: Optional[str] = None
    report_sequence: Optional[int] = None
    idempotency_key: Optional[str] = None
