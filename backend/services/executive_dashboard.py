from __future__ import annotations

from datetime import datetime, timedelta
from enum import Enum
from typing import Any


class DashboardWidget(str, Enum):
    UNIFIED_KPI = "unified_kpi"
    OPERATIONAL_METRICS = "operational_metrics"
    FINANCIAL_SUMMARY = "financial_summary"
    SAFETY_STATUS = "safety_status"
    ACTIVE_ALERTS = "active_alerts"
    PERFORMANCE_TRENDS = "performance_trends"
    BOT_HEALTH = "bot_health"
    RECOMMENDATIONS = "recommendations"


class ExecutiveDashboard:
    """Build a backend dashboard payload from report and alert engines."""

    def __init__(self, report_engine: Any, alert_engine: Any) -> None:
        self.report_engine = report_engine
        self.alert_engine = alert_engine
        self.widget_configs = self._load_widget_configs()

    def _load_widget_configs(self) -> dict[DashboardWidget, dict[str, Any]]:
        return {
            DashboardWidget.UNIFIED_KPI: {
                "title": "Unified KPI",
                "refresh_rate": 300,
                "priority": 1,
                "visualization": "gauge",
            },
            DashboardWidget.OPERATIONAL_METRICS: {
                "title": "Operational Overview",
                "refresh_rate": 60,
                "priority": 1,
                "visualization": "metrics_grid",
            },
            DashboardWidget.FINANCIAL_SUMMARY: {
                "title": "Financial Health",
                "refresh_rate": 3600,
                "priority": 2,
                "visualization": "charts",
            },
            DashboardWidget.ACTIVE_ALERTS: {
                "title": "Active Alerts",
                "refresh_rate": 30,
                "priority": 1,
                "visualization": "alert_list",
            },
            DashboardWidget.RECOMMENDATIONS: {
                "title": "Strategic Recommendations",
                "refresh_rate": 3600,
                "priority": 3,
                "visualization": "card_list",
            },
        }

    async def render_dashboard(self, executive_level: str = "general_manager") -> dict[str, Any]:
        report = await self.report_engine.generate_unified_report()
        active_alerts = await self.alert_engine.get_active_alerts()
        widgets: dict[str, Any] = {}
        for widget_type, config in self.widget_configs.items():
            widgets[widget_type.value] = {
                "config": config,
                "data": await self._generate_widget_data(widget_type, report),
            }
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "executive_level": executive_level,
            "widgets": widgets,
            "summary": self._generate_executive_summary(report, active_alerts),
            "alerts_summary": await self._get_alerts_summary(),
            "unified_report": report,
            "active_alerts": active_alerts,
        }

    async def _generate_widget_data(self, widget_type: DashboardWidget, report: dict[str, Any]) -> dict[str, Any]:
        if widget_type == DashboardWidget.UNIFIED_KPI:
            kpi = report.get("unified_kpi", {})
            return {
                "current": kpi.get("overall_score", 0),
                "target": 85,
                "trend": kpi.get("trends", {}),
                "breakdown": {
                    "operational": kpi.get("operational_efficiency", 0),
                    "financial": kpi.get("financial_health", 0),
                    "safety": kpi.get("safety_index", 0),
                    "customer": kpi.get("customer_happiness", 0),
                    "system": kpi.get("system_stability", 0),
                },
            }
        if widget_type == DashboardWidget.OPERATIONAL_METRICS:
            shipments = report.get("raw_data_summary", {}).get("shipments", {})
            return {
                "total_shipments": shipments.get("total_shipments", 0),
                "on_time_delivery": shipments.get("on_time_delivery", 0),
                "delayed_shipments": shipments.get("delayed_shipments", 0),
                "active_drivers": shipments.get("active_drivers", 0),
                "average_delivery_time": shipments.get("average_delivery_time", 0),
            }
        if widget_type == DashboardWidget.FINANCIAL_SUMMARY:
            financial = report.get("raw_data_summary", {}).get("financial", {})
            return {
                "revenue": financial.get("revenue", 0),
                "profit_margin": financial.get("profit_margin", 0),
                "pending_payments": financial.get("pending_payments", 0),
                "monthly_growth": financial.get("revenue_growth", 0),
            }
        if widget_type == DashboardWidget.ACTIVE_ALERTS:
            alerts = await self.alert_engine.get_active_alerts()
            return {
                "total": len(alerts),
                "critical": len([alert for alert in alerts if alert.get("severity") == "critical"]),
                "high": len([alert for alert in alerts if alert.get("severity") == "high"]),
                "by_category": self._count_by_category(alerts),
            }
        if widget_type == DashboardWidget.RECOMMENDATIONS:
            return {
                "recommendations": report.get("recommendations", []),
                "insights": report.get("insights", []),
            }
        return {}

    def _count_by_category(self, alerts: list[dict[str, Any]]) -> dict[str, int]:
        counts: dict[str, int] = {}
        for alert in alerts:
            category = str(alert.get("category", "unknown"))
            counts[category] = counts.get(category, 0) + 1
        return counts

    def _generate_executive_summary(self, report: dict[str, Any], alerts: list[dict[str, Any]]) -> dict[str, Any]:
        kpi = report.get("unified_kpi", {})
        overall_score = float(kpi.get("overall_score", 0))
        if overall_score >= 85:
            status, color = "Excellent", "green"
        elif overall_score >= 70:
            status, color = "Good", "yellow"
        elif overall_score >= 50:
            status, color = "Fair", "orange"
        else:
            status, color = "Critical", "red"
        critical_alerts = len([alert for alert in alerts if alert.get("severity") == "critical"])
        return {
            "status": status,
            "color": color,
            "unified_score": overall_score,
            "critical_issues": critical_alerts,
            "top_priority": self._get_top_priority(report, alerts),
            "quick_wins": report.get("recommendations", [])[:3],
        }

    def _get_top_priority(self, report: dict[str, Any], alerts: list[dict[str, Any]]) -> str:
        critical = [alert for alert in alerts if alert.get("severity") == "critical"]
        if critical:
            return f"Resolve {len(critical)} critical alerts."
        recommendations = report.get("recommendations", [])
        if recommendations:
            return str(recommendations[0])
        return "Monitor system performance."

    async def get_drilldown_data(self, entity: str, entity_id: str) -> dict[str, Any]:
        if entity == "shipment":
            return {
                "shipment_id": entity_id,
                "status": "in_transit",
                "location": "Toronto",
                "estimated_delivery": (datetime.utcnow() + timedelta(hours=5)).isoformat(),
                "driver": "Example Driver",
                "history": [],
            }
        if entity == "partner":
            return {
                "partner_id": entity_id,
                "name": "Example Partner",
                "tier": "Gold",
                "total_deals": 45,
                "total_commission": 12500,
                "recent_transactions": [],
            }
        if entity == "alert":
            alerts = await self.alert_engine.get_active_alerts()
            for alert in alerts:
                if alert.get("alert_id") == entity_id:
                    return alert
            return {"error": "Alert not found."}
        return {"error": "Unknown entity."}

    async def get_alerts_summary(self) -> dict[str, Any]:
        return await self._get_alerts_summary()

    async def _get_alerts_summary(self) -> dict[str, Any]:
        active = await self.alert_engine.get_active_alerts()
        return {
            "total_active": len(active),
            "by_severity": {
                "critical": len([alert for alert in active if alert.get("severity") == "critical"]),
                "high": len([alert for alert in active if alert.get("severity") == "high"]),
                "warning": len([alert for alert in active if alert.get("severity") == "warning"]),
                "info": len([alert for alert in active if alert.get("severity") == "info"]),
            },
            "oldest_alert": min(active, key=lambda alert: alert.get("timestamp")) if active else None,
            "most_recent": max(active, key=lambda alert: alert.get("timestamp")) if active else None,
        }
