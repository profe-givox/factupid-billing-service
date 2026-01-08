from typing import Optional
from pydantic import BaseModel


class PlanBase(BaseModel):
    id: str
    name: str
    price: int
    currency: str
    interval: Optional[str] = None


class PlanRead(PlanBase):
    """
    Schema de salida para exponer planes al frontend.
    """
    pass
