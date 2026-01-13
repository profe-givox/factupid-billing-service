from typing import Optional, List, TYPE_CHECKING
from datetime import datetime, date

from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.payment import Payment

class Subscription(SQLModel, table=True):
    """
    Representa una suscripcion de un usuario a un plan.
    """

    id: Optional[int] = Field(default=None, primary_key=True)

    user_id: int = Field(
        index=True,
        description="ID del usuario en el sistema principal"
    )

    plan_id: int = Field(
        foreign_key="plan.id",
        description="ID interno del plan"
    )

    status: str = Field(
        default="pending",
        description="Estado: pending, active, expired, canceled"
    )

    provider: str = Field(
        default="stripe",
        description="Proveedor de pago (stripe, manual, promo)"
    )

    stripe_subscription_id: Optional[str] = Field(
        default=None,
        index=True,
        description="ID de la suscripcion en Stripe"
    )

    start_date: Optional[date] = Field(
        default=None,
        description="Fecha de inicio de la suscripcion"
    )

    end_date: Optional[date] = Field(
        default=None,
        description="Fecha de fin de la suscripcion"
    )

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Fecha de creacion"
    )

    payments: List["Payment"] = Relationship(back_populates="subscription")