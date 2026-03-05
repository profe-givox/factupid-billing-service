from typing import Optional
from pydantic import BaseModel


class PlanBase(BaseModel):
    id: str
    name: str
    price: int
    currency: str
    interval: Optional[str] = None

class PlanCreate(BaseModel):
    code: str
    name: str
    price: float
    currency: str = "MXN"
    interval: Optional[str] = None
    billing_type: str
    
class PlanRegister(BaseModel):
    code: str
    name: str
    price: int
    currency: str = "MXN"
    interval: Optional[str] = None
    billing_type: str

    stripe_product_id: str
    stripe_price_id: str

class PlanRead(PlanBase):
    """
    Schema de salida para exponer planes al frontend.
    """
    pass
