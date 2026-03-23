from __future__ import annotations

import logging
import os
import time
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, cast

import psutil
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.config import get_db_async
from backend.database.session import wrap_session_factory
from .models import AlertRule, HealthSnapshot, Incident, RemediationAction
from .knowledge_graph import ProjectKnowledgeGraph, HealthMonitoringSystem
from .auto_fix_engine import AutoFixEngine
from .recommendation_engine import RecommendationEngine
from .nlp_processor import NLPProcessor

logger = logging.getLogger("maintenance")

# -----------------------------
# Config (env overrides)
# -----------------------------
AUTO_REMEDIATE = os.getenv("MAINTENANCE_AUTO_REMEDIATE", "true").lower() in (
    "1",
    "true",
    "yes",
    "on",
)

INCIDENT_COOLDOWN_MINUTES = int(os.getenv("MAINTENANCE_INCIDENT_COOLDOWN_MINUTES", "30"))
REMEDIATION_COOLDOWN_MINUTES = int(os.getenv("MAINTENANCE_REMEDIATION_COOLDOWN_MINUTES", "20"))

DB_DEGRADED_MS = float(os.getenv("MAINTENANCE_DB_DEGRADED_MS", "2000"))
DB_CRITICAL_MS = float(os.getenv("MAINTENANCE_DB_CRITICAL_MS", "8000"))
MEM_DEGRADED = float(os.getenv("MAINTENANCE_MEM_DEGRADED", "80"))
MEM_CRITICAL = float(os.getenv("MAINTENANCE_MEM_CRITICAL", "90"))
DISK_DEGRADED = float(os.getenv("MAINTENANCE_DISK_DEGRADED", "80"))
DISK_CRITICAL = float(os.getenv("MAINTENANCE_DISK_CRITICAL", "90"))

DB_REMEDIATE_LOWER_CONCURRENCY_MS = float(os.getenv("MAINTENANCE_DB_LOWER_CONCURRENCY_MS", "3000"))
MEM_REMEDIATE_CLEAR_CACHE = float(os.getenv("MAINTENANCE_MEM_CLEAR_CACHE", "85"))
DISK_REMEDIATE_ROTATE_LOGS = float(os.getenv("MAINTENANCE_DISK_ROTATE_LOGS", "85"))


def _status_from_metrics(
    db_latency_ms: Optional[float],
    mem: Optional[float],
    disk: Optional[float],
) -> str:
    db_latency_ms = float(db_latency_ms or 0.0)
    mem = float(mem or 0.0)
    disk = float(disk or 0.0)

    if db_latency_ms >= DB_CRITICAL_MS or mem >= MEM_CRITICAL or disk >= DISK_CRITICAL:
        return "critical"
    if db_latency_ms >= DB_DEGRADED_MS or mem >= MEM_DEGRADED or disk >= DISK_DEGRADED:
        return "degraded"
    return "healthy"


class HealthCollector:
    @staticmethod
    async def collect_system_metrics() -> Dict[str, Any]:
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage("/")
            load_avg = psutil.getloadavg()[0] if hasattr(psutil, "getloadavg") else None

            return {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "disk_percent": disk.percent,
                "load_average": load_avg,
                "timestamp": datetime.utcnow().isoformat(),
            }
        except Exception as e:
            logger.error(f"Failed to collect system metrics: {e}")
            return {}

    @staticmethod
    async def collect_database_metrics(db: AsyncSession) -> Dict[str, Any]:
        try:
            start_time = time.time()
            await db.execute(select(func.count()).select_from(HealthSnapshot))
            latency_ms = (time.time() - start_time) * 1000.0
            return {"db_latency_ms": latency_ms, "timestamp": datetime.utcnow().isoformat()}
        except Exception as e:
            logger.error(f"Failed to collect DB metrics: {e}")
            return {"db_latency_ms": None}

    @staticmethod
    async def collect_bot_metrics() -> Dict[str, Any]:
        ops_latency = int(os.getenv("OPS_LATENCY", "150"))
        ops_errors = int(os.getenv("OPS_ERRORS", "0"))
        ops_health = os.getenv("OPS_HEALTH", "healthy")
        return {
            "finance_bot": {"latency": 150, "errors": 0, "status": "healthy"},
            "operations_manager": {"latency": ops_latency, "errors": ops_errors, "status": ops_health},
            "timestamp": datetime.utcnow().isoformat(),
        }


class RemediationService:
    RUNBOOKS = {
        "restart_bot": {"params": ["bot_name"], "action": "restart_bot"},
        "clear_cache": {"params": [], "action": "clear_cache"},
        "rotate_logs": {"params": [], "action": "rotate_logs"},
        "lower_concurrency": {"params": ["target_concurrency"], "action": "lower_concurrency"},
    }

    @staticmethod
    async def execute_runbook(db: AsyncSession, runbook_id: str, params: Dict[str, Any]) -> bool:
        if runbook_id not in RemediationService.RUNBOOKS:
            logger.error(f"Unknown runbook: {runbook_id}")
            return False

        runbook = RemediationService.RUNBOOKS[runbook_id]

        action = RemediationAction(
            action_type=runbook["action"],
            action_params=params,
            runbook_id=runbook_id,
            status="running",
        )
        db.add(action)
        await db.commit()

        try:
            success = await RemediationService._execute_action(runbook["action"], params)

            a = cast(Any, action)
            a.status = "completed" if success else "failed"
            a.success = bool(success)
            a.completed_at = datetime.utcnow()
            await db.commit()
            return bool(success)

        except Exception as e:
            logger.error(f"Runbook execution failed: {e}")
            a = cast(Any, action)
            a.status = "failed"
            a.success = False
            a.error_message = str(e)
            a.completed_at = datetime.utcnow()
            await db.commit()
            return False

    @staticmethod
    async def _execute_action(action_type: str, params: Dict[str, Any]) -> bool:
        if action_type == "restart_bot":
            bot_name = params.get("bot_name")
            if bot_name:
                logger.info(f"Restarting bot: {bot_name} (placeholder)")
                return True
        if action_type == "clear_cache":
            logger.info("Clearing cache (placeholder)")
            return True
        if action_type == "rotate_logs":
            logger.info("Rotating logs (placeholder)")
            return True
        if action_type == "lower_concurrency":
            target = params.get("target_concurrency", 5)
            logger.info(f"Lowering concurrency to {target} (placeholder)")
            return True
        return False


class AlertAnalyzer:
    @staticmethod
    async def analyze_metrics(db: AsyncSession, metrics: Dict[str, Any]) -> None:
        try:
            res = await db.execute(select(AlertRule).where(AlertRule.enabled.is_(True)))
            rules = res.scalars().all()

            for rule in rules:
                metric_name = cast(str, rule.metric_name)
                val = AlertAnalyzer._get_metric_value(metrics, metric_name)
                if val is None:
                    continue

                threshold = float(cast(float, rule.threshold))
                op = cast(str, rule.operator)

                triggered = (
                    (op == ">" and val > threshold)
                    or (op == "<" and val < threshold)
                    or (op == ">=" and val >= threshold)
                    or (op == "<=" and val <= threshold)
                    or (op == "==" and val == threshold)
                )

                if triggered:
                    inc = Incident(
                        title=f"{rule.name}",
                        description=f"Alert rule triggered: {metric_name} {op} {threshold}",
                        severity=cast(str, rule.severity),
                        status="open",
                        component="system",
                        metrics_snapshot=metrics,
                    )
                    db.add(inc)

            await db.commit()
        except Exception as e:
            logger.error(f"Failed to analyze metrics: {e}")

    @staticmethod
    def _get_metric_value(metrics: Dict[str, Any], metric_name: str) -> Optional[float]:
        if metric_name in metrics:
            try:
                return float(metrics[metric_name])
            except Exception:
                return None

        parts = metric_name.split(".")
        cur: Any = metrics
        for p in parts:
            if isinstance(cur, dict) and p in cur:
                cur = cur[p]
            else:
                return None
        return float(cur) if isinstance(cur, (int, float)) else None


class MaintenanceService:
    @staticmethod
    async def _cooldown_ok(db: AsyncSession, runbook_id: str) -> bool:
        now = datetime.utcnow()
        window_start = now - timedelta(minutes=REMEDIATION_COOLDOWN_MINUTES)

        q = (
            select(RemediationAction)
            .where(
                and_(
                    RemediationAction.runbook_id == runbook_id,
                    RemediationAction.created_at >= window_start,
                    RemediationAction.status.in_(["running", "completed"]),
                )
            )
            .order_by(RemediationAction.created_at.desc())
        )
        res = await db.execute(q)
        return res.scalars().first() is None

    @staticmethod
    async def _maybe_open_incident(db: AsyncSession, status: str, metrics: Dict[str, Any]) -> None:
        if status not in ("degraded", "critical"):
            return

        now = datetime.utcnow()
        window_start = now - timedelta(minutes=INCIDENT_COOLDOWN_MINUTES)

        title = f"System health {status}"
        component = "system"
        severity = "critical" if status == "critical" else "warning"

        q_open = select(Incident).where(
            and_(
                Incident.title == title,
                Incident.component == component,
                Incident.status.in_(["open", "investigating"]),
            )
        )
        res_open = await db.execute(q_open)
        if res_open.scalars().first():
            return

        q_recent = select(Incident).where(
            and_(
                Incident.title == title,
                Incident.component == component,
                Incident.created_at >= window_start,
            )
        )
        res_recent = await db.execute(q_recent)
        if res_recent.scalars().first():
            return

        inc = Incident(
            title=title,
            description=f"Auto-detected. metrics={metrics}",
            severity=severity,
            status="open",
            component=component,
            metrics_snapshot=metrics,
        )
        db.add(inc)
        await db.commit()

    async def collect_and_analyze_health(self, db: AsyncSession) -> None:
        system_metrics = await HealthCollector.collect_system_metrics()
        db_metrics = await HealthCollector.collect_database_metrics(db)
        bot_metrics = await HealthCollector.collect_bot_metrics()

        metrics: Dict[str, Any] = {**system_metrics, **db_metrics, "bots": bot_metrics}

        db_latency_ms = metrics.get("db_latency_ms")
        memory_percent = metrics.get("memory_percent")
        disk_percent = metrics.get("disk_percent")
        cpu_percent = metrics.get("cpu_percent")

        overall_status = _status_from_metrics(db_latency_ms, memory_percent, disk_percent)

        snapshot = HealthSnapshot(
            cpu_percent=cpu_percent,
            memory_percent=memory_percent,
            disk_percent=disk_percent,
            load_average=metrics.get("load_average"),
            db_connections=metrics.get("db_connections"),
            db_latency_ms=db_latency_ms,
            bot_metrics=metrics.get("bots"),
            overall_status=overall_status,
        )
        db.add(snapshot)
        await db.commit()

        metrics_payload = {
            "db_latency_ms": db_latency_ms,
            "memory_percent": memory_percent,
            "disk_percent": disk_percent,
            "cpu_percent": cpu_percent,
        }
        await self._maybe_open_incident(db, overall_status, metrics_payload)

        if AUTO_REMEDIATE and overall_status in ("degraded", "critical"):
            if (db_latency_ms or 0) >= DB_REMEDIATE_LOWER_CONCURRENCY_MS and await self._cooldown_ok(
                db, "lower_concurrency"
            ):
                await RemediationService.execute_runbook(
                    db, "lower_concurrency", {"target_concurrency": 2, "executed_by": "auto"}
                )

            if (memory_percent or 0) >= MEM_REMEDIATE_CLEAR_CACHE and await self._cooldown_ok(db, "clear_cache"):
                await RemediationService.execute_runbook(db, "clear_cache", {"executed_by": "auto"})

            if (disk_percent or 0) >= DISK_REMEDIATE_ROTATE_LOGS and await self._cooldown_ok(db, "rotate_logs"):
                await RemediationService.execute_runbook(db, "rotate_logs", {"executed_by": "auto"})

        await AlertAnalyzer.analyze_metrics(db, metrics)


@wrap_session_factory(get_db_async)
async def trigger_health_collection(db: AsyncSession) -> Dict[str, Any]:
    svc = MaintenanceService()
    await svc.collect_and_analyze_health(db)
    return {"status": "success", "message": "Health collection triggered"}
