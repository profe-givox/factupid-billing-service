from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, JSON

if TYPE_CHECKING:
    from app.models.subscription import Subscription


class Payment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    subscription_id: int = Field(foreign_key="subscription.id")
    subscription: Optional["Subscription"] = Relationship(back_populates="payments")

    provider: str = Field(index=True)  # stripe
    provider_payment_id: str = Field(index=True, unique=True)

    amount: int
    currency: str

    status: str  # succeeded, failed, pending

    paid_at: datetime = Field(default_factory=datetime.utcnow)

    raw_event: Optional[dict] = Field(
        default=None,
        sa_column=Column(JSON)
    )
