from __future__ import annotations

import asyncio
import hashlib
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any


logger = logging.getLogger(__name__)


class AlertSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    HIGH = "high"
    CRITICAL = "critical"


class AlertCategory(str, Enum):
    OPERATIONAL = "operational"
    FINANCIAL = "financial"
    SAFETY = "safety"
    SECURITY = "security"
    SYSTEM = "system"
    CUSTOMER = "customer"


@dataclass
class BotAlert:
    alert_id: str
    bot_name: str
    category: AlertCategory
    severity: AlertSeverity
    title: str
    description: str
    affected_entity: str
    timestamp: datetime
    data: dict[str, Any]
    is_resolved: bool = False
    resolution_time: datetime | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "alert_id": self.alert_id,
            "bot_name": self.bot_name,
            "category": self.category.value,
            "severity": self.severity.value,
            "title": self.title,
            "description": self.description,
            "affected_entity": self.affected_entity,
            "timestamp": self.timestamp.isoformat(),
            "data": self.data,
            "is_resolved": self.is_resolved,
            "resolution_time": self.resolution_time.isoformat() if self.resolution_time else None,
        }


@dataclass
class CompositeAlert:
    composite_id: str
    primary_alert: BotAlert
    related_alerts: list[BotAlert]
    severity: AlertSeverity
    correlation_score: float
    recommended_actions: list[str]
    assigned_bots: list[str]
    created_at: datetime
    status: str = "active"

    def to_dict(self) -> dict[str, Any]:
        return {
            "composite_id": self.composite_id,
            "primary_alert": self.primary_alert.to_dict(),
            "related_alerts": [alert.to_dict() for alert in self.related_alerts],
            "severity": self.severity.value,
            "correlation_score": self.correlation_score,
            "recommended_actions": self.recommended_actions,
            "assigned_bots": self.assigned_bots,
            "created_at": self.created_at.isoformat(),
            "status": self.status,
        }


class SmartAlertEngine:
    """Correlate and manage alerts across multiple bot domains."""

    def __init__(self) -> None:
        self.active_alerts: dict[str, BotAlert] = {}
        self.alert_history: list[BotAlert] = []
        self.composite_alerts: dict[str, CompositeAlert] = {}
        self.correlation_rules = self._load_correlation_rules()
        self.bot_connectors: dict[str, Any] = {}

    def _load_correlation_rules(self) -> list[dict[str, Any]]:
        return [
            {"name": "shipment_delay_chain", "trigger_bots": ["freight_broker", "dispatcher"], "time_window": 30},
            {"name": "financial_safety_correlation", "trigger_bots": ["finance_bot", "safety_manager"], "time_window": 60},
            {
                "name": "customer_service_cascade",
                "trigger_bots": ["customer_service", "dispatcher", "freight_broker"],
                "time_window": 15,
            },
            {"name": "system_security_breach", "trigger_bots": ["system_manager", "security_manager"], "time_window": 5},
        ]

    async def register_bot_connector(self, bot_name: str, connector: Any) -> None:
        self.bot_connectors[bot_name] = connector
        logger.info("registered alert connector for %s", bot_name)

    async def register_bot_connectors(self, connectors: dict[str, Any]) -> None:
        for bot_name, connector in connectors.items():
            await self.register_bot_connector(bot_name, connector)

    async def ingest_alert(self, alert_data: dict[str, Any]) -> dict[str, Any]:
        alert = BotAlert(
            alert_id=self._make_alert_id(str(alert_data["bot_name"])),
            bot_name=str(alert_data["bot_name"]),
            category=AlertCategory(alert_data.get("category", AlertCategory.OPERATIONAL.value)),
            severity=AlertSeverity(alert_data.get("severity", AlertSeverity.INFO.value)),
            title=str(alert_data["title"]),
            description=str(alert_data["description"]),
            affected_entity=str(alert_data.get("affected_entity", "system")),
            timestamp=datetime.utcnow(),
            data=dict(alert_data.get("data", {})),
        )
        self.active_alerts[alert.alert_id] = alert
        await self._check_correlations(alert)
        if alert_data.get("auto_resolve"):
            asyncio.create_task(self._auto_resolve_alert(alert.alert_id, int(alert_data.get("auto_resolve_time", 300))))
        return alert.to_dict()

    async def _check_correlations(self, new_alert: BotAlert) -> None:
        related_alerts: list[BotAlert] = []
        for alert in self.active_alerts.values():
            if alert.alert_id == new_alert.alert_id:
                continue
            for rule in self.correlation_rules:
                if alert.bot_name not in rule["trigger_bots"] or new_alert.bot_name not in rule["trigger_bots"]:
                    continue
                delta_seconds = abs((alert.timestamp - new_alert.timestamp).total_seconds())
                if delta_seconds <= int(rule["time_window"]) * 60:
                    related_alerts.append(alert)
                    break
        if related_alerts:
            await self._create_composite_alert(new_alert, related_alerts)

    async def _create_composite_alert(self, primary: BotAlert, related: list[BotAlert]) -> None:
        composite = CompositeAlert(
            composite_id=self._make_composite_id(primary.alert_id),
            primary_alert=primary,
            related_alerts=related,
            severity=self._max_severity([primary, *related]),
            correlation_score=self._calculate_correlation_score(primary, related),
            recommended_actions=self._generate_composite_actions(primary, related),
            assigned_bots=sorted({primary.bot_name, *(alert.bot_name for alert in related)}),
            created_at=datetime.utcnow(),
        )
        self.composite_alerts[composite.composite_id] = composite
        await self._notify_bots(composite)

    def _max_severity(self, alerts: list[BotAlert]) -> AlertSeverity:
        ranking = {
            AlertSeverity.INFO: 1,
            AlertSeverity.WARNING: 2,
            AlertSeverity.HIGH: 3,
            AlertSeverity.CRITICAL: 4,
        }
        return max((alert.severity for alert in alerts), key=lambda severity: ranking[severity])

    def _calculate_correlation_score(self, primary: BotAlert, related: list[BotAlert]) -> float:
        if not related:
            return 0.0
        time_diffs = [abs((primary.timestamp - alert.timestamp).total_seconds()) for alert in related]
        avg_time_diff = sum(time_diffs) / len(time_diffs)
        time_factor = max(0.0, 1.0 - (avg_time_diff / 1800.0))
        entity_match = sum(1 for alert in related if alert.affected_entity == primary.affected_entity) / len(related)
        category_match = sum(1 for alert in related if alert.category == primary.category) / len(related)
        return round(min(1.0, (time_factor * 0.4) + (entity_match * 0.4) + (category_match * 0.2)), 2)

    def _generate_composite_actions(self, primary: BotAlert, related: list[BotAlert]) -> list[str]:
        actions: list[str] = []
        categories = {primary.category, *(alert.category for alert in related)}
        if AlertCategory.OPERATIONAL in categories and AlertCategory.CUSTOMER in categories:
            actions.extend(
                [
                    "Notify affected customers immediately.",
                    "Prepare updated delivery estimates.",
                    "Coordinate dispatch and support follow-up.",
                ]
            )
        if AlertCategory.SAFETY in categories and AlertCategory.FINANCIAL in categories:
            actions.extend(
                [
                    "Estimate the financial impact of the safety issue.",
                    "Review insurance exposure and route controls.",
                    "Schedule a targeted safety audit.",
                ]
            )
        if AlertCategory.SECURITY in categories and AlertCategory.SYSTEM in categories:
            actions.extend(
                [
                    "Isolate affected systems.",
                    "Rotate exposed credentials.",
                    "Start the incident response playbook.",
                ]
            )
        if not actions:
            related_bots = sorted({alert.bot_name for alert in related})
            actions = [
                f"Investigate the relationship between {primary.bot_name} and {', '.join(related_bots)}.",
                "Review logs for the shared time window.",
                "Run a cross-team incident review.",
            ]
        return actions

    async def _notify_bots(self, composite: CompositeAlert) -> None:
        for bot_name in composite.assigned_bots:
            connector = self.bot_connectors.get(bot_name)
            if connector is None or not hasattr(connector, "receive_composite_alert"):
                continue
            try:
                await connector.receive_composite_alert(composite.to_dict())
            except Exception as exc:
                logger.error("failed to notify %s about composite alert: %s", bot_name, exc)

    async def resolve_alert(self, alert_id: str, resolution_note: str = "") -> dict[str, Any] | None:
        alert = self.active_alerts.get(alert_id)
        if alert is None:
            return None
        alert.is_resolved = True
        alert.resolution_time = datetime.utcnow()
        if resolution_note:
            alert.data["resolution_note"] = resolution_note
        self.alert_history.append(alert)
        del self.active_alerts[alert_id]
        await self._check_composite_resolution(alert_id)
        return alert.to_dict()

    async def _check_composite_resolution(self, resolved_alert_id: str) -> None:
        for composite in self.composite_alerts.values():
            if composite.status != "active":
                continue
            if composite.primary_alert.alert_id == resolved_alert_id:
                composite.primary_alert.is_resolved = True
            for alert in composite.related_alerts:
                if alert.alert_id == resolved_alert_id:
                    alert.is_resolved = True
            if composite.primary_alert.is_resolved and all(alert.is_resolved for alert in composite.related_alerts):
                composite.status = "resolved"

    async def _auto_resolve_alert(self, alert_id: str, timeout_seconds: int) -> None:
        await asyncio.sleep(timeout_seconds)
        await self.resolve_alert(alert_id, "Auto-resolved after timeout.")

    async def get_active_alerts(self, severity: AlertSeverity | None = None) -> list[dict[str, Any]]:
        alerts = [
            alert.to_dict()
            for alert in self.active_alerts.values()
            if severity is None or alert.severity == severity
        ]
        return sorted(alerts, key=lambda item: item["timestamp"], reverse=True)

    async def get_composite_alerts(self, status: str = "active") -> list[dict[str, Any]]:
        return [alert.to_dict() for alert in self.composite_alerts.values() if alert.status == status]

    async def analyze_alert_patterns(self, days: int = 7) -> dict[str, Any]:
        cutoff = datetime.utcnow() - timedelta(days=days)
        relevant = [alert for alert in self.alert_history if alert.timestamp >= cutoff]
        if not relevant:
            return {"error": "No historical data."}
        by_category: dict[str, int] = {}
        by_severity: dict[str, int] = {}
        by_bot: dict[str, int] = {}
        for alert in relevant:
            by_category[alert.category.value] = by_category.get(alert.category.value, 0) + 1
            by_severity[alert.severity.value] = by_severity.get(alert.severity.value, 0) + 1
            by_bot[alert.bot_name] = by_bot.get(alert.bot_name, 0) + 1
        resolved = [alert for alert in relevant if alert.is_resolved and alert.resolution_time]
        avg_resolution = 0.0
        if resolved:
            avg_resolution = sum(
                (alert.resolution_time - alert.timestamp).total_seconds() / 60.0 for alert in resolved if alert.resolution_time
            ) / len(resolved)
        return {
            "period_days": days,
            "total_alerts": len(relevant),
            "active_alerts": len([alert for alert in relevant if not alert.is_resolved]),
            "by_category": by_category,
            "by_severity": by_severity,
            "top_alert_bots": sorted(by_bot.items(), key=lambda item: item[1], reverse=True)[:5],
            "avg_resolution_time_minutes": round(avg_resolution, 2),
            "peak_hours": self._find_peak_hours(relevant),
        }

    def _find_peak_hours(self, alerts: list[BotAlert]) -> list[dict[str, int]]:
        counts: dict[int, int] = {}
        for alert in alerts:
            counts[alert.timestamp.hour] = counts.get(alert.timestamp.hour, 0) + 1
        return [{"hour": hour, "count": count} for hour, count in sorted(counts.items(), key=lambda item: item[1], reverse=True)[:3]]

    @staticmethod
    def _make_alert_id(bot_name: str) -> str:
        digest = hashlib.md5(f"{bot_name}_{datetime.utcnow().timestamp()}".encode("utf-8")).hexdigest()[:10]
        return f"ALT_{digest.upper()}"

    @staticmethod
    def _make_composite_id(alert_id: str) -> str:
        digest = hashlib.sha1(f"{alert_id}_{datetime.utcnow().timestamp()}".encode("utf-8")).hexdigest()[:10]
        return f"CMP_{digest.upper()}"
