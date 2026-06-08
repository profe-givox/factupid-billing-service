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

class PlanUpdate(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None
    price: Optional[float] = None
    currency: Optional[str] = None
    interval: Optional[str] = None
    billing_type: Optional[str] = None
    stripe_product_id: Optional[str] = None
    stripe_price_id: Optional[str] = None
    is_active: Optional[bool] = None