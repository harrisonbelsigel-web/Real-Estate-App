import asyncio
import logging
from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from backend.database import SessionLocal
from backend.app.models import Area
from backend.app.services.scraper import PropertyScraper
from backend.app.services.cache import cache

logger = logging.getLogger(__name__)

# Cron triggers per frequency: daily 2am, weekly Sunday 2am, monthly 1st 2am.
FREQUENCY_TRIGGERS = {
    "daily": CronTrigger(hour=2, minute=0),
    "weekly": CronTrigger(day_of_week="sun", hour=2, minute=0),
    "monthly": CronTrigger(day=1, hour=2, minute=0),
}

scheduler = AsyncIOScheduler()


async def run_scheduled_scrape(area_id: int) -> None:
    """Scrape one area on its schedule, then clear cached query results."""
    db = SessionLocal()
    try:
        area = db.query(Area).filter(Area.id == area_id).first()
        if not area:
            logger.warning(f"Scheduled scrape skipped: area {area_id} no longer exists")
            return

        logger.info(f"Running scheduled scrape for {area.name}")
        await PropertyScraper.scrape_area(db, area)

        area.last_scraped_at = datetime.utcnow()
        db.add(area)
        db.commit()
        cache.clear()
    except Exception as e:
        logger.error(f"Scheduled scrape failed for area {area_id}: {e}")
    finally:
        db.close()


def sync_area_schedules() -> None:
    """
    Reconcile scheduler jobs with the areas table. Called on startup and
    whenever an area's scrape_frequency changes.
    """
    db = SessionLocal()
    try:
        areas = db.query(Area).all()
        active_job_ids = set()

        for area in areas:
            job_id = f"scrape-area-{area.id}"
            trigger = FREQUENCY_TRIGGERS.get(area.scrape_frequency or "")

            if trigger is None:
                # Frequency "manual" (or unset): no scheduled job.
                continue

            active_job_ids.add(job_id)
            existing = scheduler.get_job(job_id)
            if existing:
                scheduler.reschedule_job(job_id, trigger=trigger)
            else:
                scheduler.add_job(
                    run_scheduled_scrape,
                    trigger=trigger,
                    id=job_id,
                    args=[area.id],
                    replace_existing=True,
                )
            logger.info(f"Scheduled {area.name}: {area.scrape_frequency}")

        # Remove jobs for deleted areas or areas switched back to manual.
        for job in scheduler.get_jobs():
            if job.id.startswith("scrape-area-") and job.id not in active_job_ids:
                scheduler.remove_job(job.id)
    finally:
        db.close()


def start_scheduler() -> None:
    if not scheduler.running:
        scheduler.start()
    sync_area_schedules()


def shutdown_scheduler() -> None:
    if scheduler.running:
        scheduler.shutdown(wait=False)
