from datetime import datetime, timezone
from sqlmodel import Session
from app.db.session import engine
from app.models.payment import WebhookNotificationQueue

ID = 36

with Session(engine) as db:
    q = db.get(WebhookNotificationQueue, ID)

    print("ANTES")
    print("status:", q.status)
    print("retry:", q.retry_count, "/", q.max_retries)
    print("next_retry_at:", q.next_retry_at)

    q.next_retry_at = datetime.now(timezone.utc)

    db.add(q)
    db.commit()
    db.refresh(q)

    print("\nDESPUÉS")
    print("status:", q.status)
    print("retry:", q.retry_count, "/", q.max_retries)
    print("next_retry_at:", q.next_retry_at)