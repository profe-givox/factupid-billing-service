import logging
from datetime import datetime, timedelta, timezone

from apscheduler.schedulers.background import BackgroundScheduler

from app.services.queue_processor import process_pending_notifications
from app.services.main_app_overage import trigger_main_app_overage_reporting

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


def _trigger_overage_reporting_job():
    """Job periódico que dispara reporte de excedentes CFDI a Django."""
    try:
        logger.info("Job overage_reporting: iniciando sync periódico de excedentes")
        ok = trigger_main_app_overage_reporting(mode="periodic")
        if ok:
            logger.info("Job overage_reporting: sync periódico exitoso")
        else:
            logger.warning("Job overage_reporting: sync periódico falló")
    except Exception as exc:
        logger.error("Job overage_reporting: error inesperado: %s", exc)


def start_scheduler(
    interval_minutes: int = 5,
    overage_interval_minutes: int = 15,
    enable_overage_reporting: bool = True,
):
    """Inicia el scheduler con los jobs configurados."""
    # Job 1: procesamiento de cola de notificaciones
    scheduler.add_job(
        _process_pending_notifications_job,
        "interval",
        minutes=interval_minutes,
        id="process_pending_notifications",
        replace_existing=True,
    )
    logger.info(
        "Scheduler: process_pending_notifications cada %d minutos",
        interval_minutes,
    )

    # Job 2: reporte periódico de excedentes CFDI (Fase 7C.3)
    if enable_overage_reporting:
        scheduler.add_job(
            _trigger_overage_reporting_job,
            "interval",
            minutes=overage_interval_minutes,
            id="trigger_overage_reporting",
            replace_existing=True,
            max_instances=1,
            # Ejecutar una vez al startup (después de 5s) + intervalo
            next_run_time=datetime.now(timezone.utc) + timedelta(seconds=5),
        )
        logger.info(
            "Scheduler: trigger_overage_reporting cada %d minutos "
            "(startup en 5s)",
            overage_interval_minutes,
        )
    else:
        logger.info("Scheduler: overage_reporting DESHABILITADO")

    scheduler.start()
    logger.info("Scheduler iniciado")


def shutdown_scheduler():
    """Detiene el scheduler de forma segura."""
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("Scheduler detenido")
