from pydantic import BaseModel
from app.schemas.subscription import SubscriptionRead


class CheckoutSessionResponse(BaseModel):
    subscription: SubscriptionRead
    checkout_url: str
