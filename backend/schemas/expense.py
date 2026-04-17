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

from backend.config import settings  # type: ignore[import]
from backend.utils.email_utils import send_email

logger = logging.getLogger(__name__)

# Global scheduler reference (no concrete type to keep type checker happy)
scheduler: Optional[object] = None


async def run_load_board_job() -> None:
    """
    Simple scheduled job scaffold for the load board monitor.

    For now it just sends a heartbeat email to the admin to confirm that
    the load board scheduler is wired correctly. Later you can extend it
    to poll real load boards (123Loadboard, DAT, etc.).
    """
    subject = "[GTS AI] Load board monitor heartbeat"
    body = "The load board scheduler executed successfully. This is an automated message."

    try:
        # NOTE: send_email signature uses 'to', not 'to_email'
        to_email = settings.ADMIN_EMAIL or settings.SUPPORT_EMAIL
        if not to_email:
            logger.warning("Load board heartbeat skipped: no admin_email/support_email configured")
            return
        send_email(
            subject=subject,
            body=body,
            to=[to_email],
        )
        logger.info("Load board heartbeat email sent to %s", to_email)
    except Exception as exc:
        logger.exception("Load board job failed: %s", exc)


def get_scheduler() -> Optional[object]:
    """
    Return the global scheduler instance (if started), else None.
    """
    return scheduler


def start_load_board_scheduler() -> None:
    """
    Initialize and start the APScheduler-based load board scheduler.

    If APScheduler is not available (not installed) this becomes a no-op.
    """
    global scheduler

    if AsyncIOScheduler is None or CronTrigger is None:
        logger.info("APScheduler not available; load board scheduler is disabled.")
        scheduler = None
        return

    if scheduler is not None:
        # Already started
        return

    # Use a local variable so type checker does not treat it as Optional
    local_scheduler = AsyncIOScheduler(timezone="UTC")  # type: ignore[call-arg]
    # Example: run every 15 minutes
    local_scheduler.add_job(
        run_load_board_job,
        CronTrigger(minute="*/15"),  # type: ignore[call-arg]
        id="load_board_heartbeat",
        replace_existing=True,
    )
    local_scheduler.start()
    scheduler = local_scheduler
    logger.info("Load board scheduler started (every 15 minutes).")


__all__ = ["start_load_board_scheduler", "get_scheduler", "run_load_board_job"]
