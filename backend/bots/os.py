from __future__ import annotations

import asyncio
import json
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, AsyncIterator, Awaitable, Callable, Dict, Iterable, Optional
from contextlib import asynccontextmanager

from sqlalchemy import desc, func, select
from backend.models.bot_os import BotRegistry, BotRun, HumanCommand
from backend.bots.ws_manager import broadcast_event

try:
    from apscheduler.schedulers.asyncio import AsyncIOScheduler  # type: ignore
    from apscheduler.triggers.cron import CronTrigger  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    AsyncIOScheduler = None
    CronTrigger = None

logger = logging.getLogger("bots.os")

DEFAULT_SCHEDULES = {
    "finance_bot": "0 6 * * *",
    "maintenance_dev": "0 2 * * *",
    "mapleload": "0 */6 * * *",
    "freight_broker": "*/15 * * * *",
}

NON_AUTO_LEVELS = {"manual", "paused", "human"}
JOB_PREFIX = "bos:"


@dataclass
class BotRunResult:
    run_id: int
    bot_name: str
    status: str
    task_type: str
    result: Dict[str, Any] | None
    error: str | None


def _safe_json(value: Any) -> Any:
    try:
        return json.loads(json.dumps(value, default=str))
    except Exception:
        return None


def _config_path() -> Path:
    return Path(__file__).resolve().parents[2] / "config" / "bots.yaml"


def _load_config() -> Dict[str, Any]:
    path = _config_path()
    if not path.exists():
        return {}
    try:
        import yaml  # type: ignore
    except Exception:
        logger.warning("PyYAML not available; skipping %s", path)
        return {}
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception as exc:
        logger.warning("Failed to load %s: %s", path, exc)
        return {}
    if not isinstance(data, dict):
        return {}
    return data.get("bots") if isinstance(data.get("bots"), dict) else data


class BotOS:
    def __init__(
        self,
        *,
        bot_names_provider: Callable[[], Iterable[str]],
        bot_getter: Callable[[str], Any],
        session_factory: Callable[[], AsyncIterator[Any]],
    ) -> None:
        self._bot_names_provider = bot_names_provider
        self._bot_getter = bot_getter
        self._session_factory = session_factory
        self._paused: set[str] = set()
        self._lock = asyncio.Lock()
        self._started = False
        self._shutdown = False

        if AsyncIOScheduler is not None:
            self._scheduler = AsyncIOScheduler(timezone="UTC")
        else:  # pragma: no cover
            self._scheduler = None

    @property
    def session_factory(self) -> Callable[[], AsyncIterator[Any]]:
        return self._session_factory

    @asynccontextmanager
    async def _session_scope(self):
        provider = self._session_factory()
        if hasattr(provider, "__aenter__"):
            async with provider as session:
                yield session
            return
        async for session in provider:
            yield session
            break

    @asynccontextmanager
    async def session_scope(self):
        async with self._session_scope() as session:
            yield session

    def list_bot_names(self) -> list[str]:
        return list(self._bot_names_provider() or [])

    def has_bot(self, bot_name: str) -> bool:
        if not bot_name:
            return False
        try:
            self._bot_getter(bot_name)
            return True
        except Exception:
            return False

    async def start(self) -> None:
        if self._started:
            return
        await self.sync_registry()
        await self.refresh_schedule()
        self._started = True

    async def shutdown(self) -> None:
        self._shutdown = True
        if self._scheduler is None:
            return
        try:
            self._scheduler.shutdown(wait=False)
        except Exception:
            pass

    async def sync_registry(self) -> None:
        config = _load_config()
        bot_names = self.list_bot_names()
        async with self._session_scope() as session:
            rows = await session.execute(select(BotRegistry))
            existing = {row.bot_name: row for row in rows.scalars().all()}

            for bot_name in bot_names:
                cfg = config.get(bot_name, {})
                if not isinstance(cfg, dict):
                    cfg = {}

                if bot_name not in existing:
                    schedule_cron = cfg.get("schedule_cron") or DEFAULT_SCHEDULES.get(bot_name)
                    session.add(
                        BotRegistry(
                            bot_name=bot_name,
                            enabled=bool(cfg.get("enabled", True)),
                            automation_level=str(cfg.get("automation_level", "auto")),
                            schedule_cron=schedule_cron,
                            config_json=cfg.get("config") or {},
                        )
                    )
                    continue

                entry = existing[bot_name]
                if "enabled" in cfg:
                    entry.enabled = bool(cfg["enabled"])
                if "automation_level" in cfg:
                    entry.automation_level = str(cfg["automation_level"])
                if "schedule_cron" in cfg:
                    entry.schedule_cron = str(cfg["schedule_cron"]) if cfg["schedule_cron"] else None
                if "config" in cfg:
                    entry.config_json = cfg.get("config") or {}

            await session.commit()

    async def refresh_schedule(self) -> None:
        if self._scheduler is None or CronTrigger is None:
            logger.info("APScheduler not available; BotOS scheduler disabled.")
            return

        for job in list(self._scheduler.get_jobs()):
            if job.id.startswith(JOB_PREFIX):
                self._scheduler.remove_job(job.id)

        async with self._session_scope() as session:
            rows = await session.execute(
                select(BotRegistry).where(BotRegistry.enabled.is_(True))
            )
            for entry in rows.scalars().all():
                if not entry.schedule_cron:
                    continue
                if str(entry.automation_level or "").lower() in NON_AUTO_LEVELS:
                    continue
                job_id = f"{JOB_PREFIX}{entry.bot_name}"
                task_type = "scheduled"
                if isinstance(entry.config_json, dict) and entry.config_json.get("task_type"):
                    task_type = str(entry.config_json.get("task_type"))
                try:
                    trigger = CronTrigger.from_crontab(entry.schedule_cron)
                except Exception as exc:
                    logger.warning("Invalid cron for %s: %s (%s)", entry.bot_name, entry.schedule_cron, exc)
                    continue
                self._scheduler.add_job(
                    self._run_scheduled,
                    trigger,
                    id=job_id,
                    replace_existing=True,
                    args=[entry.bot_name, task_type],
                    max_instances=1,
                )

        if not self._scheduler.running:
            self._scheduler.start(paused=False)
            logger.info("BotOS scheduler started.")

    async def _run_scheduled(self, bot_name: str, task_type: str) -> None:
        if self._shutdown or bot_name in self._paused:
            return
        await self.execute_bot(bot_name, task_type=task_type, params={}, allow_paused=False)

    async def pause_bot(self, bot_name: str) -> bool:
        async with self._lock:
            if bot_name in self._paused:
                return False
            self._paused.add(bot_name)
        await broadcast_event(channel="bots.status", payload={"bot_name": bot_name, "status": "paused"})
        return True

    async def resume_bot(self, bot_name: str) -> bool:
        async with self._lock:
            if bot_name not in self._paused:
                return False
            self._paused.discard(bot_name)
        await broadcast_event(channel="bots.status", payload={"bot_name": bot_name, "status": "active"})
        return True

    async def execute_bot(
        self,
        bot_name: str,
        *,
        task_type: str,
        params: Dict[str, Any],
        allow_paused: bool = True,
    ) -> BotRunResult:
        if not bot_name:
            raise ValueError("bot_name is required")
        if not allow_paused and bot_name in self._paused:
            return BotRunResult(
                run_id=0,
                bot_name=bot_name,
                status="skipped",
                task_type=task_type,
                result=None,
                error="paused",
            )

        params_json = _safe_json(params or {})
        now = datetime.now(timezone.utc)
        async with self._session_scope() as session:
            run = BotRun(
                bot_name=bot_name,
                task_type=task_type or "run",
                params_json=params_json,
                status="running",
                started_at=now,
            )
            session.add(run)
            await session.commit()
            await session.refresh(run)

            status = "completed"
            error = None
            result_payload: Dict[str, Any] | None = None
            try:
                bot = self._bot_getter(bot_name)
                result = bot.run(params or {})
                if asyncio.iscoroutine(result):
                    result = await result
                result_payload = _safe_json(result)
            except Exception as exc:
                status = "failed"
                error = str(exc)

            run.status = status
            run.result_json = result_payload
            run.error = error
            run.finished_at = datetime.now(timezone.utc)
            await session.commit()

        await broadcast_event(
            channel="bots.run.completed",
            payload={
                "bot_name": bot_name,
                "run_id": run.id,
                "task_type": task_type,
                "status": status,
            },
        )

        return BotRunResult(
            run_id=run.id,
            bot_name=bot_name,
            status=status,
            task_type=task_type,
            result=result_payload,
            error=error,
        )

    async def list_bots(self) -> list[Dict[str, Any]]:
        async with self._session_scope() as session:
            rows = await session.execute(select(BotRegistry))
            bots = rows.scalars().all()

            runs = await session.execute(select(BotRun).order_by(desc(BotRun.started_at)))
            latest: Dict[str, BotRun] = {}
            for run in runs.scalars().all():
                if run.bot_name not in latest:
                    latest[run.bot_name] = run

        data: list[Dict[str, Any]] = []
        for bot in bots:
            job = self._scheduler.get_job(f"{JOB_PREFIX}{bot.bot_name}") if self._scheduler else None
            last_run = latest.get(bot.bot_name)
            status = "idle"
            if bot.bot_name in self._paused:
                status = "paused"
            elif last_run and last_run.status == "failed":
                status = "error"
            elif last_run and last_run.status == "running":
                status = "running"

            data.append(
                {
                    "bot_name": bot.bot_name,
                    "enabled": bot.enabled,
                    "automation_level": bot.automation_level,
                    "schedule_cron": bot.schedule_cron,
                    "next_run": job.next_run_time.isoformat() if job and job.next_run_time else None,
                    "status": status,
                    "last_run": {
                        "id": last_run.id,
                        "status": last_run.status,
                        "started_at": last_run.started_at.isoformat() if last_run and last_run.started_at else None,
                        "finished_at": last_run.finished_at.isoformat() if last_run and last_run.finished_at else None,
                    }
                    if last_run
                    else None,
                }
            )
        return data

    async def list_runs(self, limit: int = 50) -> list[Dict[str, Any]]:
        limit = max(1, min(int(limit or 50), 200))
        async with self._session_scope() as session:
            rows = await session.execute(
                select(BotRun).order_by(desc(BotRun.started_at)).limit(limit)
            )
            runs = rows.scalars().all()

        return [
            {
                "id": run.id,
                "bot_name": run.bot_name,
                "task_type": run.task_type,
                "status": run.status,
                "started_at": run.started_at.isoformat() if run.started_at else None,
                "finished_at": run.finished_at.isoformat() if run.finished_at else None,
                "error": run.error,
            }
            for run in runs
        ]

    async def stats(self) -> Dict[str, Any]:
        async with self._session_scope() as session:
            total_runs = await session.scalar(select(func.count()).select_from(BotRun))
            by_status_rows = await session.execute(
                select(BotRun.status, func.count()).group_by(BotRun.status)
            )
            by_bot_rows = await session.execute(
                select(BotRun.bot_name, func.count()).group_by(BotRun.bot_name)
            )
            commands_total = await session.scalar(select(func.count()).select_from(HumanCommand))

        return {
            "total_runs": int(total_runs or 0),
            "by_status": {str(k): int(v) for (k, v) in by_status_rows.all()},
            "by_bot": {str(k): int(v) for (k, v) in by_bot_rows.all()},
            "human_commands": int(commands_total or 0),
        }


_bot_os: Optional[BotOS] = None


def init_bot_os(
    *,
    bot_names_provider: Callable[[], Iterable[str]],
    bot_getter: Callable[[str], Any],
    session_factory: Callable[[], AsyncIterator[Any]],
) -> BotOS:
    global _bot_os
    if _bot_os is None:
        _bot_os = BotOS(
            bot_names_provider=bot_names_provider,
            bot_getter=bot_getter,
            session_factory=session_factory,
        )
    return _bot_os


def get_bot_os() -> BotOS:
    if _bot_os is None:
        raise RuntimeError("BotOS is not initialized")
    return _bot_os

