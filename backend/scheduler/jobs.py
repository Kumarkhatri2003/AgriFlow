

import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from django.conf import settings

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────
# Job definitions  (called every day at 04:00)
# ─────────────────────────────────────────────

def generate_crop_reminders_job():
    """Daily crop activity reminder generation job."""
    logger.info("[SCHEDULER] ▶ Running daily crop reminders job...")
    try:
        from crops.services.reminder_service import CropReminderService
        results = CropReminderService.generate_reminders_for_all_crops()
        logger.info(
            "[SCHEDULER] Crop reminders done — "
            "crops: %s, reminders: %s",
            results.get('total_crops', 0),
            results.get('total_reminders', 0),
        )
    except Exception as exc:
        logger.exception("[SCHEDULER] Crop reminder job failed: %s", exc)


def generate_livestock_alerts_job():
    """Daily livestock alert generation job."""
    logger.info("[SCHEDULER] ▶ Running daily livestock alerts job...")
    try:
        from livestock.alert_generator import LivestockAlertGenerator
        count = LivestockAlertGenerator.generate_all_alerts()
        logger.info(
            "[SCHEDULER]  Livestock alerts done — %s alerts generated", count
        )
    except Exception as exc:
        logger.exception("[SCHEDULER]  Livestock alert job failed: %s", exc)


# ─────────────────────────────────────────────
# Scheduler bootstrap
# ─────────────────────────────────────────────

def delete_old_job_executions(max_age=604_800):
    """
    Purge APScheduler execution records older than `max_age` seconds (default 7 days).
    Called once a week to keep the table tidy.
    """
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


def start_scheduler():
    """
    Configure and start the BackgroundScheduler.
    Jobs are stored in the Django database so they survive restarts
    and are guaranteed to run only once per trigger, even under Gunicorn.
    """
    timezone = getattr(settings, 'TIME_ZONE', 'Asia/Kathmandu')

    scheduler = BackgroundScheduler(timezone=timezone)
    scheduler.add_jobstore(DjangoJobStore(), 'default')

    # ── Daily 04:00 AM – Crop Reminders ──────────────────────────────────
    scheduler.add_job(
        generate_crop_reminders_job,
        trigger=CronTrigger(hour=4, minute=0, timezone=timezone),
        id='daily_crop_reminders',
        name='Daily Crop Activity Reminders @ 04:00',
        jobstore='default',
        replace_existing=True,     # update if already registered
        max_instances=1,           # never run two copies simultaneously
        misfire_grace_time=3600,   # run up to 1 hour late if server was down
    )
    logger.info("[SCHEDULER] Registered: daily_crop_reminders @ 04:00 %s", timezone)

    # ── Daily 04:00 AM – Livestock Alerts ────────────────────────────────
    scheduler.add_job(
        generate_livestock_alerts_job,
        trigger=CronTrigger(hour=4, minute=0, timezone=timezone),
        id='daily_livestock_alerts',
        name='Daily Livestock Alerts @ 04:00',
        jobstore='default',
        replace_existing=True,
        max_instances=1,
        misfire_grace_time=3600,
    )
    logger.info("[SCHEDULER] Registered: daily_livestock_alerts @ 04:00 %s", timezone)

    # ── Weekly cleanup of old APScheduler execution records ───────────────
    scheduler.add_job(
        delete_old_job_executions,
        trigger=CronTrigger(day_of_week='mon', hour=0, minute=0, timezone=timezone),
        id='weekly_apscheduler_cleanup',
        name='Weekly APScheduler execution log cleanup',
        jobstore='default',
        replace_existing=True,
        max_instances=1,
    )
    logger.info("[SCHEDULER] Registered: weekly_apscheduler_cleanup @ Mon 00:00 %s", timezone)

    try:
        logger.info("[SCHEDULER] Starting APScheduler...")
        scheduler.start()
        logger.info("[SCHEDULER] APScheduler started — jobs will fire daily at 04:00 %s", timezone)
    except Exception as exc:
        logger.exception("[SCHEDULER]  Failed to start APScheduler: %s", exc)
