from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any, Dict

from sqlalchemy import text

from backend.database.session import async_session

logger = logging.getLogger(__name__)


class RealBotConnector:
    """Production-safe connector for cross-bot reporting and alert fan-out."""

    def __init__(self, bot_name: str) -> None:
        self.bot_name = bot_name
        self.received_composites: list[dict[str, Any]] = []

    async def _fetch_scalar(self, sql: str, params: Dict[str, Any] | None = None) -> Any:
        async with async_session() as session:
            result = await session.execute(text(sql), params or {})
            return result.scalar()

    async def _fetch_counts(self) -> Dict[str, Any]:
        try:
            total_shipments = int(await self._fetch_scalar("SELECT COUNT(*) FROM shipments") or 0)
            delayed_shipments = int(
                await self._fetch_scalar(
                    """
                    SELECT COUNT(*)
                    FROM shipments
                    WHERE LOWER(COALESCE(status, '')) LIKE '%delay%'
                    """
                )
                or 0
            )
            active_drivers = int(
                await self._fetch_scalar(
                    """
                    SELECT COUNT(*)
                    FROM users
                    WHERE LOWER(COALESCE(role, '')) = 'driver'
                      AND COALESCE(is_deleted, FALSE) = FALSE
                      AND COALESCE(is_active, FALSE) = TRUE
                    """
                )
                or 0
            )
        except Exception as exc:
            logger.error("failed to collect shipment counts for %s: %s", self.bot_name, exc)
            return {"error": str(exc), "bot_name": self.bot_name}

        payload: Dict[str, Any] = {
            "total_shipments": total_shipments,
            "delayed_shipments": delayed_shipments,
            "active_drivers": active_drivers,
        }
        if total_shipments > 0:
            payload["on_time_delivery"] = round(
                ((total_shipments - delayed_shipments) / total_shipments) * 100,
                2,
            )
        return payload

    async def get_status(self) -> Dict[str, Any]:
        return await self._fetch_counts()

    async def get_metrics(self) -> Dict[str, Any]:
        if self.bot_name == "dispatcher":
            return await self._fetch_counts()

        now = datetime.utcnow()
        current_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        previous_month_end = current_month_start - timedelta(microseconds=1)
        previous_month_start = previous_month_end.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        try:
            revenue = float(
                await self._fetch_scalar(
                    """
                    SELECT COALESCE(SUM(amount), 0)
                    FROM payments
                    WHERE status::text = 'completed'
                    """
                )
                or 0
            )
            pending_payments = float(
                await self._fetch_scalar(
                    """
                    SELECT COALESCE(SUM(amount), 0)
                    FROM payments
                    WHERE status::text IN ('pending', 'processing')
                    """
                )
                or 0
            )
            current_revenue = float(
                await self._fetch_scalar(
                    """
                    SELECT COALESCE(SUM(amount), 0)
                    FROM payments
                    WHERE status::text = 'completed'
                      AND created_at >= :start
                      AND created_at <= :end
                    """,
                    {"start": current_month_start, "end": now},
                )
                or 0
            )
            previous_revenue = float(
                await self._fetch_scalar(
                    """
                    SELECT COALESCE(SUM(amount), 0)
                    FROM payments
                    WHERE status::text = 'completed'
                      AND created_at >= :start
                      AND created_at <= :end
                    """,
                    {"start": previous_month_start, "end": previous_month_end},
                )
                or 0
            )
        except Exception as exc:
            logger.error("failed to collect finance metrics for %s: %s", self.bot_name, exc)
            return {"error": str(exc), "bot_name": self.bot_name}

        growth = 0.0
        if previous_revenue > 0:
            growth = ((current_revenue - previous_revenue) / previous_revenue) * 100
        elif current_revenue > 0:
            growth = 100.0

        return {
            "revenue": revenue,
            "revenue_growth": round(growth, 2),
            "pending_payments": pending_payments,
        }

    async def get_incidents(self) -> Dict[str, Any]:
        incident_queries = [
            (
                "SELECT COUNT(*) FROM incidents",
                "SELECT COUNT(*) FROM incidents WHERE LOWER(COALESCE(type, '')) = 'accident'",
            ),
            (
                "SELECT COUNT(*) FROM fleet_live_alerts WHERE is_resolved = FALSE",
                "SELECT COUNT(*) FROM fleet_live_alerts WHERE is_resolved = FALSE AND LOWER(COALESCE(alert_type, '')) = 'accident'",
            ),
        ]
        for incidents_sql, accidents_sql in incident_queries:
            try:
                incidents = int(await self._fetch_scalar(incidents_sql) or 0)
                accidents = int(await self._fetch_scalar(accidents_sql) or 0)
                return {
                    "incidents": incidents,
                    "accidents": accidents,
                    "safety_score": max(0, 100 - (incidents * 5) - (accidents * 15)),
                }
            except Exception:
                continue
        return {"error": "incident_source_unavailable", "bot_name": self.bot_name}

    async def get_satisfaction_metrics(self) -> Dict[str, Any]:
        ticket_queries = [
            (
                "SELECT COUNT(*) FROM support_tickets WHERE LOWER(COALESCE(status, '')) IN ('open', 'pending', 'in_progress')",
                "SELECT COUNT(*) FROM support_tickets WHERE LOWER(COALESCE(status, '')) IN ('resolved', 'closed')",
            ),
            (
                "SELECT COUNT(*) FROM live_support_sessions WHERE LOWER(COALESCE(status, '')) IN ('open', 'pending', 'active')",
                "SELECT COUNT(*) FROM live_support_sessions WHERE LOWER(COALESCE(status, '')) IN ('resolved', 'closed', 'completed')",
            ),
        ]
        for open_sql, resolved_sql in ticket_queries:
            try:
                open_tickets = int(await self._fetch_scalar(open_sql) or 0)
                resolved_tickets = int(await self._fetch_scalar(resolved_sql) or 0)
                total = open_tickets + resolved_tickets
                satisfaction = round((resolved_tickets / total) * 100, 2) if total else 0.0
                return {
                    "satisfaction_score": satisfaction,
                    "open_tickets": open_tickets,
                    "resolved_tickets": resolved_tickets,
                }
            except Exception:
                continue
        return {"error": "support_metrics_unavailable", "bot_name": self.bot_name}

    async def get_health_status(self) -> Dict[str, Any]:
        try:
            start = datetime.utcnow()
            await self._fetch_scalar("SELECT 1")
            elapsed = max((datetime.utcnow() - start).total_seconds(), 0.001)
            return {
                "response_time": round(elapsed, 4),
                "threshold": 0.5,
                "error_rate": 0.0,
            }
        except Exception as exc:
            logger.error("failed to collect system health for %s: %s", self.bot_name, exc)
            return {"error": str(exc), "bot_name": self.bot_name}

    async def get_performance_metrics(self) -> Dict[str, Any]:
        return await self.get_metrics()

    async def receive_composite_alert(self, alert_data: dict[str, Any]) -> None:
        self.received_composites.append(alert_data)

    async def health_check(self) -> Dict[str, Any]:
        status = await self.get_health_status()
        if "error" in status:
            return {"status": "unavailable", "error": status["error"]}
        return {"status": "healthy", **status}
