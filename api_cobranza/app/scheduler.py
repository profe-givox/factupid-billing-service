import logging
from apscheduler.schedulers.background import BackgroundScheduler
from app.services.queue_processor import process_pending_notifications

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()


def _process_pending_notifications_job():
    """Job que se ejecuta periodicamente para reprocesar notificaciones fallidas."""
    try:
        stats = process_pending_notifications(max_items=20)
        if stats["processed"] > 0:
            logger.info(
                "Cola procesada: %d procesadas, %d exitosas, %d fallidas, %d expiradas",
                stats["processed"],
                stats["succeeded"],
                stats["failed"],
                stats["expired"],
            )
    except Exception as exc:
        logger.error("Error ejecutando job de cola de notificaciones: %s", exc)


def start_scheduler(interval_minutes: int = 5):
    """Inicia el scheduler con el job de procesamiento de cola."""
    scheduler.add_job(
        _process_pending_notifications_job,
        "interval",
        minutes=interval_minutes,
        id="process_pending_notifications",
        replace_existing=True,
    )
    scheduler.start()
    logger.info(
        "Scheduler iniciado: process_pending_notifications cada %d minutos",
        interval_minutes,
    )


def shutdown_scheduler():
    """Detiene el scheduler de forma segura."""
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("Scheduler detenido")
