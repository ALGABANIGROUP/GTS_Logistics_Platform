from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from statistics import fmean
from typing import Any


logger = logging.getLogger(__name__)


class ReportType(str, Enum):
    OPERATIONAL_HEALTH = "operational_health"
    FINANCIAL_SUMMARY = "financial_summary"
    SAFETY_ANALYSIS = "safety_analysis"
    CUSTOMER_SATISFACTION = "customer_satisfaction"
    SYSTEM_PERFORMANCE = "system_performance"
    EXECUTIVE_OVERVIEW = "executive_overview"


class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class UnifiedKPI:
    overall_score: float
    operational_efficiency: float
    financial_health: float
    safety_index: float
    customer_happiness: float
    system_stability: float
    timestamp: datetime
    trends: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "overall_score": self.overall_score,
            "operational_efficiency": self.operational_efficiency,
            "financial_health": self.financial_health,
            "safety_index": self.safety_index,
            "customer_happiness": self.customer_happiness,
            "system_stability": self.system_stability,
            "timestamp": self.timestamp.isoformat(),
            "trends": self.trends,
        }


@dataclass
class SmartAlert:
    alert_id: str
    title: str
    description: str
    priority: Priority
    affected_bots: list[str]
    recommended_actions: list[str]
    source_bots: list[str]
    created_at: datetime

    def to_dict(self) -> dict[str, Any]:
        return {
            "alert_id": self.alert_id,
            "title": self.title,
            "description": self.description,
            "priority": self.priority.value,
            "affected_bots": self.affected_bots,
            "recommended_actions": self.recommended_actions,
            "source_bots": self.source_bots,
            "created_at": self.created_at.isoformat(),
        }


class SmartReportEngine:
    """Aggregate metrics across bot connectors into unified KPI reports."""

    def __init__(self) -> None:
        self.bot_connectors: dict[str, Any] = {}
        self.report_history: list[dict[str, Any]] = []
        self.cache: dict[str, dict[str, Any]] = {}

    async def register_bot_connector(self, bot_name: str, connector: Any) -> None:
        self.bot_connectors[bot_name] = connector
        logger.info("registered report connector for %s", bot_name)

    async def register_bot_connectors(self, connectors: dict[str, Any]) -> None:
        for bot_name, connector in connectors.items():
            await self.register_bot_connector(bot_name, connector)

    async def generate_unified_report(
        self,
        report_type: ReportType = ReportType.EXECUTIVE_OVERVIEW,
        force_refresh: bool = False,
    ) -> dict[str, Any]:
        cache_key = report_type.value
        if not force_refresh and cache_key in self.cache:
            cached = self.cache[cache_key]
            cached_age = datetime.utcnow() - datetime.fromisoformat(cached["generated_at"])
            if cached_age <= timedelta(minutes=5):
                return cached

        report_id = f"RPT_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}"
        collection_tasks: list[asyncio.Future[Any] | Any] = []

        if report_type in {ReportType.EXECUTIVE_OVERVIEW, ReportType.OPERATIONAL_HEALTH}:
            collection_tasks.extend(
                [
                    self._collect_freight_data(),
                    self._collect_dispatcher_data(),
                    self._collect_safety_data(),
                ]
            )
        if report_type in {ReportType.EXECUTIVE_OVERVIEW, ReportType.FINANCIAL_SUMMARY}:
            collection_tasks.extend([self._collect_finance_data(), self._collect_sales_data()])
        if report_type in {ReportType.EXECUTIVE_OVERVIEW, ReportType.CUSTOMER_SATISFACTION}:
            collection_tasks.append(self._collect_customer_service_data())
        if report_type in {ReportType.EXECUTIVE_OVERVIEW, ReportType.SYSTEM_PERFORMANCE}:
            collection_tasks.append(self._collect_system_data())

        collected_data = await asyncio.gather(*collection_tasks, return_exceptions=True)
        processed_data = self._process_collected_data(collected_data)
        unified_kpi = await self._calculate_unified_kpi(processed_data)
        insights = self._generate_insights(processed_data, unified_kpi)
        alerts = self._detect_critical_issues(processed_data)

        report = {
            "report_id": report_id,
            "report_type": report_type.value,
            "generated_at": datetime.utcnow().isoformat(),
            "time_period": self._get_report_period(),
            "unified_kpi": unified_kpi.to_dict(),
            "insights": insights,
            "alerts": [alert.to_dict() for alert in alerts],
            "recommendations": self._generate_recommendations(unified_kpi, insights),
            "data_sources": sorted(self.bot_connectors.keys()),
            "raw_data_summary": processed_data,
        }

        self.cache[cache_key] = report
        self.report_history.append(
            {
                "report_id": report_id,
                "timestamp": datetime.utcnow(),
                "report_type": report_type.value,
                "unified_kpi": unified_kpi.overall_score,
            }
        )
        return report

    async def _collect_freight_data(self) -> dict[str, Any]:
        return await self._collect_from_connector("freight_broker", "get_status")

    async def _collect_dispatcher_data(self) -> dict[str, Any]:
        return await self._collect_from_connector("dispatcher", "get_metrics")

    async def _collect_safety_data(self) -> dict[str, Any]:
        return await self._collect_from_connector("safety_manager", "get_incidents")

    async def _collect_finance_data(self) -> dict[str, Any]:
        return await self._collect_from_connector("finance_bot", "get_metrics")

    async def _collect_sales_data(self) -> dict[str, Any]:
        return await self._collect_from_connector("sales_bot", "get_performance_metrics")

    async def _collect_customer_service_data(self) -> dict[str, Any]:
        return await self._collect_from_connector("customer_service", "get_satisfaction_metrics")

    async def _collect_system_data(self) -> dict[str, Any]:
        return await self._collect_from_connector("system_manager", "get_health_status")

    async def _collect_from_connector(self, bot_name: str, method_name: str) -> dict[str, Any]:
        connector = self.bot_connectors.get(bot_name)
        if connector is None:
            return {"error": f"{bot_name} not connected", "bot_name": bot_name}
        try:
            method = getattr(connector, method_name)
            return await method()
        except Exception as exc:
            logger.error("failed to collect %s data: %s", bot_name, exc)
            return {"error": str(exc), "bot_name": bot_name}

    def _process_collected_data(self, raw_data: list[Any]) -> dict[str, dict[str, Any]]:
        processed: dict[str, dict[str, Any]] = {
            "shipments": {},
            "financial": {},
            "safety": {},
            "customer": {},
            "system": {},
        }
        for data in raw_data:
            if isinstance(data, Exception) or not isinstance(data, dict):
                continue
            if "total_shipments" in data or "on_time_delivery" in data:
                processed["shipments"].update(data)
            elif "revenue" in data or "profit_margin" in data:
                processed["financial"].update(data)
            elif "incidents" in data or "safety_score" in data:
                processed["safety"].update(data)
            elif "satisfaction_score" in data or "open_tickets" in data:
                processed["customer"].update(data)
            elif "cpu_usage" in data or "response_time" in data or "uptime" in data:
                processed["system"].update(data)
        return processed

    async def _calculate_unified_kpi(self, processed_data: dict[str, dict[str, Any]]) -> UnifiedKPI:
        operational = self._calculate_operational_kpi(processed_data.get("shipments", {}))
        financial_health = self._calculate_financial_kpi(processed_data.get("financial", {}))
        safety_index = self._calculate_safety_kpi(processed_data.get("safety", {}))
        customer_happiness = self._calculate_customer_kpi(processed_data.get("customer", {}))
        system_stability = self._calculate_system_kpi(processed_data.get("system", {}))
        overall = (
            (operational * 0.25)
            + (financial_health * 0.25)
            + (safety_index * 0.20)
            + (customer_happiness * 0.15)
            + (system_stability * 0.15)
        )
        trends = self._calculate_trends(
            operational,
            financial_health,
            safety_index,
            customer_happiness,
            system_stability,
        )
        return UnifiedKPI(
            overall_score=round(overall, 2),
            operational_efficiency=round(operational, 2),
            financial_health=round(financial_health, 2),
            safety_index=round(safety_index, 2),
            customer_happiness=round(customer_happiness, 2),
            system_stability=round(system_stability, 2),
            timestamp=datetime.utcnow(),
            trends=trends,
        )

    def _calculate_operational_kpi(self, data: dict[str, Any]) -> float:
        if not data:
            return 70.0
        metrics: list[float] = []
        if "on_time_delivery" in data:
            metrics.append(float(data["on_time_delivery"]))
        if data.get("total_shipments") and "delayed_shipments" in data:
            total = float(data["total_shipments"])
            metrics.append(((total - float(data["delayed_shipments"])) / total) * 100)
        if data.get("average_delivery_time") and data.get("target_delivery_time"):
            metrics.append(
                min(100.0, (float(data["target_delivery_time"]) / float(data["average_delivery_time"])) * 100)
            )
        return round(fmean(metrics), 2) if metrics else 70.0

    def _calculate_financial_kpi(self, data: dict[str, Any]) -> float:
        if not data:
            return 70.0
        metrics: list[float] = []
        if "profit_margin" in data:
            metrics.append(min(100.0, (float(data["profit_margin"]) / 50.0) * 100))
        if "revenue_growth" in data:
            normalized = ((float(data["revenue_growth"]) + 10.0) / 40.0) * 100.0
            metrics.append(max(0.0, min(100.0, normalized)))
        return round(fmean(metrics), 2) if metrics else 70.0

    def _calculate_safety_kpi(self, data: dict[str, Any]) -> float:
        if not data:
            return 85.0
        if "safety_score" in data:
            return max(0.0, min(100.0, float(data["safety_score"])))
        base_score = 100.0
        base_score -= int(data.get("incidents", 0)) * 5
        base_score -= int(data.get("accidents", 0)) * 15
        return max(0.0, min(100.0, base_score))

    def _calculate_customer_kpi(self, data: dict[str, Any]) -> float:
        if not data:
            return 75.0
        metrics: list[float] = []
        if "satisfaction_score" in data:
            metrics.append(float(data["satisfaction_score"]))
        if "open_tickets" in data and "resolved_tickets" in data:
            total = int(data["open_tickets"]) + int(data["resolved_tickets"])
            if total > 0:
                metrics.append((int(data["resolved_tickets"]) / total) * 100)
        if data.get("average_response_time") and data.get("target_response_time"):
            metrics.append(
                min(100.0, (float(data["target_response_time"]) / float(data["average_response_time"])) * 100)
            )
        return round(fmean(metrics), 2) if metrics else 75.0

    def _calculate_system_kpi(self, data: dict[str, Any]) -> float:
        if not data:
            return 90.0
        metrics: list[float] = []
        if "uptime" in data:
            metrics.append(float(data["uptime"]))
        if data.get("response_time") is not None and data.get("threshold"):
            performance = 100 - ((float(data["response_time"]) / float(data["threshold"])) * 100)
            metrics.append(max(0.0, min(100.0, performance)))
        if "error_rate" in data:
            metrics.append(100.0 - min(100.0, float(data["error_rate"]) * 100.0))
        return round(fmean(metrics), 2) if metrics else 90.0

    def _calculate_trends(self, *current_values: float) -> dict[str, Any]:
        if len(self.report_history) < 1:
            return {"direction": "stable", "change": 0.0}
        last_kpi = float(self.report_history[-1]["unified_kpi"])
        current_avg = fmean(current_values)
        if current_avg > last_kpi:
            return {"direction": "improving", "change": round(current_avg - last_kpi, 2)}
        if current_avg < last_kpi:
            return {"direction": "declining", "change": round(last_kpi - current_avg, 2)}
        return {"direction": "stable", "change": 0.0}

    def _generate_insights(self, data: dict[str, Any], kpi: UnifiedKPI) -> list[dict[str, Any]]:
        insights: list[dict[str, Any]] = []
        if kpi.operational_efficiency < 70:
            insights.append(
                {
                    "area": "operations",
                    "severity": "high",
                    "message": "Operational efficiency is below target.",
                    "suggestion": "Review dispatch rules and delayed route clusters.",
                }
            )
        if kpi.financial_health < 60:
            insights.append(
                {
                    "area": "finance",
                    "severity": "critical",
                    "message": "Financial health needs immediate review.",
                    "suggestion": "Inspect margin erosion and overdue receivables.",
                }
            )
        elif kpi.financial_health > 90:
            insights.append(
                {
                    "area": "finance",
                    "severity": "positive",
                    "message": "Financial performance is strong.",
                    "suggestion": "Evaluate expansion or reinvestment options.",
                }
            )
        if kpi.safety_index < 80:
            insights.append(
                {
                    "area": "safety",
                    "severity": "high",
                    "message": "Safety indicators are below the preferred range.",
                    "suggestion": "Run targeted coaching for high-risk routes and teams.",
                }
            )
        if not insights and data:
            insights.append(
                {
                    "area": "summary",
                    "severity": "stable",
                    "message": "Core operating signals remain within acceptable bounds.",
                    "suggestion": "Track trend direction and maintain current controls.",
                }
            )
        return insights

    def _detect_critical_issues(self, data: dict[str, Any]) -> list[SmartAlert]:
        alerts: list[SmartAlert] = []
        shipments = data.get("shipments", {})
        if int(shipments.get("delayed_shipments", 0)) > 10:
            alerts.append(
                SmartAlert(
                    alert_id=f"ALT_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_OPS",
                    title="Critical delivery delays",
                    description=f"{shipments['delayed_shipments']} shipments are currently delayed.",
                    priority=Priority.HIGH,
                    affected_bots=["dispatcher", "customer_service"],
                    recommended_actions=[
                        "Notify affected customers.",
                        "Rebalance available drivers.",
                        "Escalate to the operations manager.",
                    ],
                    source_bots=["freight_broker"],
                    created_at=datetime.utcnow(),
                )
            )
        safety = data.get("safety", {})
        if int(safety.get("incidents", 0)) > 5:
            alerts.append(
                SmartAlert(
                    alert_id=f"ALT_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_SAFE",
                    title="Safety incident spike",
                    description=f"{safety['incidents']} safety incidents were reported in the current period.",
                    priority=Priority.CRITICAL,
                    affected_bots=["safety_manager", "dispatcher"],
                    recommended_actions=[
                        "Investigate incident clusters.",
                        "Issue a safety bulletin.",
                        "Audit driver schedules for fatigue risk.",
                    ],
                    source_bots=["safety_manager"],
                    created_at=datetime.utcnow(),
                )
            )
        return alerts

    def _generate_recommendations(self, kpi: UnifiedKPI, insights: list[dict[str, Any]]) -> list[str]:
        recommendations: list[str] = []
        if kpi.overall_score < 60:
            recommendations.append("Schedule an emergency cross-functional review.")
        elif kpi.overall_score < 75:
            recommendations.append("Run weekly operating review meetings until the KPI recovers.")
        if kpi.operational_efficiency < kpi.financial_health:
            recommendations.append("Prioritize operations improvements to align execution with financial results.")
        if kpi.customer_happiness < 80:
            recommendations.append("Launch a customer feedback recovery program for delayed or unresolved cases.")
        if kpi.safety_index < kpi.overall_score:
            recommendations.append("Increase safety coaching and route-risk review frequency.")
        if not recommendations and insights:
            recommendations.append("Maintain current performance controls and track trend drift weekly.")
        recommendations.extend(
            [
                "Review resource allocation in low-performing areas.",
                "Tighten cross-department escalation playbooks.",
                "Set measurable targets for the next reporting cycle.",
            ]
        )
        return list(dict.fromkeys(recommendations))[:5]

    def _get_report_period(self) -> dict[str, Any]:
        end = datetime.utcnow()
        start = end - timedelta(days=7)
        return {"start": start.isoformat(), "end": end.isoformat(), "duration_days": 7}

    async def get_historical_trends(self, days: int = 30) -> dict[str, Any]:
        cutoff = datetime.utcnow() - timedelta(days=days)
        relevant_reports = [report for report in self.report_history if report["timestamp"] >= cutoff]
        if not relevant_reports:
            return {"error": "No historical data available."}
        scores = [float(report["unified_kpi"]) for report in relevant_reports]
        return {
            "period_days": days,
            "data_points": len(relevant_reports),
            "average_score": round(fmean(scores), 2),
            "min_score": min(scores),
            "max_score": max(scores),
            "trend": "up" if scores[-1] > scores[0] else "down" if scores[-1] < scores[0] else "stable",
            "improvement": round(scores[-1] - scores[0], 2),
        }
