import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlmodel import Session, select, func

from app.core.config import settings
from app.routers import plans, payments, webhooks, subscriptions, test_auth
from app.db.session import engine, get_session
from app.db.seed import seed_plans
from app.models.payment import WebhookNotificationQueue
from app.scheduler import start_scheduler, shutdown_scheduler

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    start_scheduler(
        interval_minutes=5,
        overage_interval_minutes=settings.OVERAGE_REPORTING_INTERVAL_MINUTES,
        enable_overage_reporting=settings.ENABLE_OVERAGE_REPORTING_SCHEDULER,
    )
    yield
    # Shutdown
    shutdown_scheduler()


app = FastAPI(
    title="Factupid Billing Service",
    version="0.1.0",
    root_path="/api/pagos",
    lifespan=lifespan,
)


app.include_router(plans.router)
app.include_router(payments.router)
app.include_router(webhooks.router)
app.include_router(subscriptions.router)
app.include_router(test_auth.router)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/health/queue")
def health_queue():
    """Stats de la cola de notificaciones pendientes."""
    with Session(engine) as db:
        total = db.exec(select(func.count(WebhookNotificationQueue.id))).one()
        pending = db.exec(
            select(func.count(WebhookNotificationQueue.id)).where(
                WebhookNotificationQueue.status == "pending"
            )
        ).one()
        failed = db.exec(
            select(func.count(WebhookNotificationQueue.id)).where(
                WebhookNotificationQueue.status == "failed"
            )
        ).one()
        completed = db.exec(
            select(func.count(WebhookNotificationQueue.id)).where(
                WebhookNotificationQueue.status == "completed"
            )
        ).one()

    return {
        "status": "ok",
        "queue": {
            "total": total,
            "pending": pending,
            "failed": failed,
            "completed": completed,
        },
    }


@app.get("/")
def read_root():
    return {"message": "Hola Mundo FastAPI está funcionando"}
