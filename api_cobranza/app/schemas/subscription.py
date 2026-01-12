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