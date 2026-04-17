from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from backend.database.session import wrap_session_factory
from backend.crud.maintenance import create_maintenance_run, create_maintenance_issue
import asyncio
import logging

logger = logging.getLogger("maintenance.scheduler")

SCHEDULER_INTERVAL_MINUTES = 60  # Run every 60 minutes

scheduler = AsyncIOScheduler(timezone="UTC")

async def health_check_and_log():
    # Create a maintenance run entry (issue creation is optional)
    async with wrap_session_factory() as session:
        run = await create_maintenance_run(session, None)  # scaffold payload
        logger.info(f"Maintenance run created: {run}")
        # Example issue flow:
        # issue = await create_maintenance_issue(session, ...)
        # logger.info(f"Maintenance issue created: {issue}")

def start_maintenance_scheduler():
    if scheduler.get_job("maintenance_health_check") is None:
        scheduler.add_job(
            lambda: asyncio.create_task(health_check_and_log()),
            IntervalTrigger(minutes=SCHEDULER_INTERVAL_MINUTES),
            id="maintenance_health_check",
            replace_existing=True,
            max_instances=1,
        )
    if not scheduler.running:
        scheduler.start(paused=False)
        logger.info("Maintenance scheduler started (every %s min)", SCHEDULER_INTERVAL_MINUTES)

def stop_maintenance_scheduler():
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("Maintenance scheduler stopped")

