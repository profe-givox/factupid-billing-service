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


class WebhookNotificationQueue(SQLModel, table=True):
    """
    Cola de reintentos para notificaciones fallidas hacia Django (MAIN_APP_BASE).
    Se crea una entrada cuando notify_main_app() agota sus reintentos.
    Un job externo (cron, scheduler) debe procesar los pendientes.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    subscription_id: int = Field(index=True)
    user_id: int
    billing_code: str
    plan_id: Optional[int] = None
    service_id: Optional[int] = None
    date_cutoff: Optional[str] = None
    payload: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    retry_count: int = Field(default=0)
    max_retries: int = Field(default=10)
    last_error: Optional[str] = None
    next_retry_at: Optional[datetime] = Field(default=None, index=True)
    status: str = Field(default="pending", description="pending, completed, failed")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_attempt_at: Optional[datetime] = None
