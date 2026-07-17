"""Weekly pipeline scheduler (APScheduler).

Why APScheduler and not Celery? One weekly job does not justify a broker,
a worker fleet and beat — see docs/DECISIONS.md. The job runs inside the
web process; DjangoJobStore persists state so restarts are safe.
"""
from __future__ import annotations

import logging

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from django.conf import settings
from django_apscheduler.jobstores import DjangoJobStore

logger = logging.getLogger(__name__)

_scheduler: BackgroundScheduler | None = None


def weekly_pipeline():
    """Thursday 06:00 Asia/Kathmandu: ingest fresh data, recompute SPI."""
    from ingestion.service import default_ingest_window, ingest_range
    from spi.service import compute_all

    frm, to = default_ingest_window(14)
    logger.info("Weekly pipeline: ingest %s..%s", frm, to)
    runs = ingest_range(frm, to)
    for run in runs:
        logger.info("  %s: %s (%s rows)", run.district.slug, run.status, run.rows_upserted)
    computed = compute_all()
    logger.info("Weekly pipeline: %s SPI snapshots computed", computed)


def start():
    global _scheduler
    if _scheduler is not None:
        return _scheduler
    scheduler = BackgroundScheduler(timezone=settings.TIME_ZONE)
    scheduler.add_jobstore(DjangoJobStore(), "default")
    scheduler.add_job(
        weekly_pipeline,
        trigger=CronTrigger(day_of_week="thu", hour=6, minute=0),
        id="weekly_spi_pipeline",
        max_instances=1,
        replace_existing=True,
    )
    scheduler.start()
    _scheduler = scheduler
    logger.info("APScheduler started: weekly_spi_pipeline (Thu 06:00 %s)", settings.TIME_ZONE)
    return scheduler
