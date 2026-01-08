from typing import Optional
from datetime import datetime

from sqlmodel import SQLModel, Field


class Plan(SQLModel, table=True):
    """
    Modelo que representa un plan de pago en la base de datos.
    """

    id: Optional[int] = Field(default=None, primary_key=True)

    code: str = Field(
        index=True,
        unique=True,
        description="Codigo unico del plan (free, pro_mensual, etc.)",
    )

    name: str = Field(
        description="Nombre visible del plan"
    )

    price: int = Field(
        description="Precio del plan (en pesos por ahora)"
    )

    currency: str = Field(
        max_length=3,
        description="Moneda ISO (MXN)"
    )

    interval: Optional[str] = Field(
        default=None,
        description="Periodo del plan: month, year o null"
    )

    is_active: bool = Field(
        default=True,
        description="Indica si el plan esta activo"
    )

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Fecha de creacion del plan"
    )
