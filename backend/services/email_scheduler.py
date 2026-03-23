from __future__ import annotations

import asyncio
import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from backend.database.config import AsyncSessionLocal
from backend.services.email_center_service import EmailCenterService

logger = logging.getLogger(__name__)

_polling_task: Optional[asyncio.Task[Any]] = None
_last_cycle_at: Optional[str] = None
_last_result: Dict[str, Any] = {}


def last_poll_cycle_at() -> Optional[str]:
    return _last_cycle_at


def last_poll_result() -> Dict[str, Any]:
    return dict(_last_result)


def is_polling_running() -> bool:
    return _polling_task is not None and not _polling_task.done()


async def run_poll_cycle() -> Dict[str, Any]:
    global _last_cycle_at, _last_result

    async with AsyncSessionLocal() as db:
        service = EmailCenterService(db)
        result = await service.poll_mailboxes()

    _last_cycle_at = datetime.now(timezone.utc).isoformat()
    _last_result = result
    logger.info(
        "[email_scheduler] poll cycle completed: checked=%s created=%s errors=%s",
        result.get("checked", 0),
        result.get("created", 0),
        len(result.get("errors", [])),
    )
    return result


async def email_polling_loop(interval_seconds: int = 300) -> None:
    while True:
        try:
            await run_poll_cycle()
        except Exception:
            logger.exception("[email_scheduler] poll cycle failed")
        await asyncio.sleep(interval_seconds)


def start_email_polling_task(interval_seconds: Optional[int] = None) -> asyncio.Task[Any]:
    global _polling_task
    if is_polling_running():
        return _polling_task  # type: ignore[return-value]

    resolved_interval = interval_seconds or int(os.getenv("EMAIL_POLL_INTERVAL_SECONDS", "300"))
    _polling_task = asyncio.create_task(email_polling_loop(interval_seconds=resolved_interval))
    logger.info("[email_scheduler] started (interval=%ss)", resolved_interval)
    return _polling_task


async def stop_email_polling_task() -> None:
    global _polling_task
    if _polling_task is None:
        return
    _polling_task.cancel()
    try:
        await _polling_task
    except asyncio.CancelledError:
        pass
    finally:
        _polling_task = None
        logger.info("[email_scheduler] stopped")
