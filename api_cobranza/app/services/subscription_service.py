from sqlmodel import select
from app.db.session import engine
from app.models.subscription import Subscription
from sqlmodel import Session

def obtener_subscription(user_id: int):
    with Session(engine) as db:
        return db.exec(
            select(Subscription).where(
                Subscription.user_id == user_id
            )
        ).first()