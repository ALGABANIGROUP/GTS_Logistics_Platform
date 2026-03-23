from __future__ import annotations

import logging
from typing import Optional

# Optional APScheduler imports (ignored by type checker if missing)
try:
    from apscheduler.schedulers.asyncio import AsyncIOScheduler  # type: ignore[import]
    from apscheduler.triggers.cron import CronTrigger  # type: ignore[import]
except Exception:
    AsyncIOScheduler = None  # type: ignore[assignment]
    CronTrigger = None  # type: ignore[assignment]

logger = logging.getLogger(__name__)

# Global scheduler reference (we do not expose its concrete type here)
scheduler: Optional[object] = None


async def run_ai_report_job() -> None:
    """
    Daily scheduler job to trigger operations_manager automatically.
    """
    try:
        from backend.main import ai_registry  # local import to avoid circulars

        payload = {"message": "daily_auto_run", "source": "scheduler", "mode": "daily"}
        bot = ai_registry.get("operations_manager")
        result = await bot.run(payload)
        logger.info("AI report job executed operations_manager: ok=%s", bool(result.get("ok", True)))
    except Exception as exc:
        logger.exception("AI report job failed: %s", exc)


def get_scheduler() -> Optional[object]:
    """
    Return the global scheduler instance (if started), else None.
    """
    return scheduler


def start_ai_report_scheduler() -> None:
    """
    Initialize and start the APScheduler-based AI report scheduler.

    If APScheduler is not available (not installed) this becomes a no-op.
    """
    global scheduler

    if AsyncIOScheduler is None or CronTrigger is None:
        logger.info("APScheduler not available; AI report scheduler is disabled.")
        scheduler = None
        return

    if scheduler is not None:
        # Already started
        return

    # Use a local variable so type checker does not treat it as Optional
    local_scheduler = AsyncIOScheduler(timezone="UTC")  # type: ignore[call-arg]
    local_scheduler.add_job(
        run_ai_report_job,
        CronTrigger(hour=6, minute=0),  # type: ignore[call-arg]
        id="ai_report_heartbeat",
        replace_existing=True,
    )
    local_scheduler.start()
    scheduler = local_scheduler
    logger.info("AI report scheduler started (daily 06:00 UTC).")
