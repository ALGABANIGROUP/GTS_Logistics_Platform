from __future__ import annotations

import asyncio
import logging
import os
from typing import Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from backend.database.session import async_session
from backend.models.external_data import BotExecution, ExternalRecord
from backend.services.sources import EXTERNAL_SOURCES_ENABLED, get_sources_manager, init_sources

logger = logging.getLogger("external.sync")

SYNC_JOB_ID = "external_sources_sync"
SYNC_INTERVAL_HOURS = max(int(os.getenv("EXTERNAL_SYNC_INTERVAL_HOURS", "6")), 1)
SYNC_RECORDS_PER_SOURCE = max(int(os.getenv("EXTERNAL_SYNC_RECORDS_PER_SOURCE", "5")), 1)
SCHEDULER_ENABLED = os.getenv("SCHEDULER_ENABLED", "1").strip().lower() in {
    "1",
    "true",
    "yes",
    "on",
}

_scheduler: Optional[AsyncIOScheduler] = None
_sync_lock = asyncio.Lock()


async def sync_external_sources(
    *,
    limit_per_source: Optional[int] = None,
    province: Optional[str] = None,
    force: bool = False,
) -> dict[str, int | str]:
    if not EXTERNAL_SOURCES_ENABLED:
        logger.info("External sources are disabled via EXTERNAL_SOURCES_ENABLED")
        return {"records": 0, "message": "external sources disabled", "sources": 0}

    if _sync_lock.locked() and not force:
        return {"records": 0, "message": "sync already running", "sources": 0}

    limit_per_source = max(1, min(limit_per_source or SYNC_RECORDS_PER_SOURCE, 50))
    try:
        manager = get_sources_manager()
    except RuntimeError:
        manager = init_sources()
    records = 0
    notes: list[str] = []
    sources_processed = 0

    async with _sync_lock:
        async with async_session() as session:
            for source_name in manager.list_sources():
                source = manager.get(source_name)
                if source is None:
                    continue
                try:
                    items = await source.search(limit=limit_per_source, province=province, query=None)
                except Exception as exc:  # pragma: no cover
                    logger.warning("source %s failed: %s", source_name, exc)
                    notes.append(f"{source_name}: {exc}")
                    continue

                for item in items:
                    record = ExternalRecord(
                        source=item.source,
                        entity_type=item.entity_type,
                        title=item.title,
                        location=item.location,
                        tags=item.tags,
                        raw=dict(item.raw),
                        fetched_at=item.fetched_at,
                        is_real=item.is_real,
                    )
                    session.add(record)
                records += len(items)
                sources_processed += 1

            execution = BotExecution(
                source="external_sources_sync",
                records_synced=records,
                succeeded=True,
                notes="; ".join(notes) if notes else None,
            )
            session.add(execution)

    return {
        "records": records,
        "sources": sources_processed,
        "notes": "; ".join(notes) if notes else "",
    }


async def _scheduled_sync() -> None:
    try:
        await sync_external_sources()
    except Exception as exc:  # pragma: no cover
        logger.exception("scheduled sync failed: %s", exc)


def _ensure_scheduler() -> AsyncIOScheduler:
    global _scheduler
    if _scheduler is None:
        _scheduler = AsyncIOScheduler(timezone="UTC")
    return _scheduler


def start_scheduler() -> None:
    if not (SCHEDULER_ENABLED and EXTERNAL_SOURCES_ENABLED):
        logger.info("Scheduler disabled (SCHEDULER_ENABLED=%s, sources=%s)", SCHEDULER_ENABLED, EXTERNAL_SOURCES_ENABLED)
        return

    init_sources()
    scheduler = _ensure_scheduler()
    if scheduler.get_job(SYNC_JOB_ID) is None:
        scheduler.add_job(
            _scheduled_sync,
            IntervalTrigger(hours=SYNC_INTERVAL_HOURS),
            id=SYNC_JOB_ID,
            replace_existing=True,
            max_instances=1,
        )
    if not scheduler.running:
        scheduler.start(paused=False)
        logger.info("External sources scheduler started (every %s hours)", SYNC_INTERVAL_HOURS)


def stop_scheduler() -> None:
    global _scheduler
    if _scheduler is None:
        return
    try:
        _scheduler.shutdown(wait=False)
        logger.info("External sources scheduler stopped")
    except Exception:
        pass
