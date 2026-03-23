from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from backend.core.alerts.smart_alert_engine import AlertSeverity, SmartAlertEngine
from backend.core.reporting.smart_report_engine import ReportType, SmartReportEngine
from backend.services.executive_dashboard import ExecutiveDashboard


router = APIRouter(prefix="/api/v1/bot-collaboration", tags=["Bot Collaboration"])


class MockBotConnector:
    def __init__(self, bot_name: str) -> None:
        self.bot_name = bot_name
        self.received_composites: list[dict[str, Any]] = []

    async def get_status(self) -> dict[str, Any]:
        return {
            "total_shipments": 1247,
            "on_time_delivery": 94,
            "delayed_shipments": 8,
            "active_drivers": 42,
            "average_delivery_time": 3.5,
            "target_delivery_time": 4.0,
        }

    async def get_metrics(self) -> dict[str, Any]:
        if self.bot_name == "dispatcher":
            return {
                "total_shipments": 1247,
                "on_time_delivery": 91,
                "delayed_shipments": 12,
                "active_drivers": 37,
                "average_delivery_time": 4.1,
                "target_delivery_time": 4.0,
            }
        return {
            "revenue": 2400000,
            "profit_margin": 18,
            "revenue_growth": 12,
            "pending_payments": 450000,
        }

    async def get_incidents(self) -> dict[str, Any]:
        return {"incidents": 3, "accidents": 0, "safety_score": 92}

    async def get_satisfaction_metrics(self) -> dict[str, Any]:
        return {
            "satisfaction_score": 87,
            "open_tickets": 23,
            "resolved_tickets": 156,
            "average_response_time": 2.5,
            "target_response_time": 3.0,
        }

    async def get_health_status(self) -> dict[str, Any]:
        return {
            "uptime": 99.9,
            "response_time": 0.25,
            "threshold": 0.5,
            "error_rate": 0.01,
            "cpu_usage": 45,
            "memory_usage": 62,
        }

    async def get_performance_metrics(self) -> dict[str, Any]:
        return {
            "revenue": 2100000,
            "profit_margin": 21,
            "revenue_growth": 15,
            "pending_payments": 320000,
            "total_deals": 89,
            "conversion_rate": 23,
        }

    async def receive_composite_alert(self, alert_data: dict[str, Any]) -> None:
        self.received_composites.append(alert_data)


class AlertIngestRequest(BaseModel):
    bot_name: str = Field(..., min_length=1)
    category: str = "operational"
    severity: str = "info"
    title: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    affected_entity: str = "system"
    data: dict[str, Any] = Field(default_factory=dict)
    auto_resolve: bool = False
    auto_resolve_time: int = 300


class ResolveAlertRequest(BaseModel):
    resolution_note: str = ""


_report_engine = SmartReportEngine()
_alert_engine = SmartAlertEngine()
_dashboard = ExecutiveDashboard(_report_engine, _alert_engine)
_connectors_initialized = False


async def _ensure_default_connectors() -> None:
    global _connectors_initialized
    if _connectors_initialized:
        return
    connectors = {
        "freight_broker": MockBotConnector("freight_broker"),
        "dispatcher": MockBotConnector("dispatcher"),
        "safety_manager": MockBotConnector("safety_manager"),
        "finance_bot": MockBotConnector("finance_bot"),
        "customer_service": MockBotConnector("customer_service"),
        "system_manager": MockBotConnector("system_manager"),
        "sales_bot": MockBotConnector("sales_bot"),
    }
    await _report_engine.register_bot_connectors(connectors)
    await _alert_engine.register_bot_connectors(connectors)
    _connectors_initialized = True


@router.get("/connectors")
async def list_connectors():
    await _ensure_default_connectors()
    return {
        "success": True,
        "report_connectors": sorted(_report_engine.bot_connectors.keys()),
        "alert_connectors": sorted(_alert_engine.bot_connectors.keys()),
    }


@router.get("/report")
async def get_unified_report(
    report_type: ReportType = Query(default=ReportType.EXECUTIVE_OVERVIEW),
    force_refresh: bool = False,
):
    await _ensure_default_connectors()
    report = await _report_engine.generate_unified_report(report_type=report_type, force_refresh=force_refresh)
    return {"success": True, "report": report}


@router.get("/report/trends")
async def get_report_trends(days: int = 30):
    trends = await _report_engine.get_historical_trends(days=days)
    return {"success": "error" not in trends, "trends": trends}


@router.post("/alerts/ingest")
async def ingest_alert(request: AlertIngestRequest):
    await _ensure_default_connectors()
    alert = await _alert_engine.ingest_alert(request.model_dump())
    return {"success": True, "alert": alert}


@router.get("/alerts/active")
async def get_active_alerts(severity: str | None = Query(default=None)):
    await _ensure_default_connectors()
    severity_filter = AlertSeverity(severity) if severity else None
    alerts = await _alert_engine.get_active_alerts(severity=severity_filter)
    return {"success": True, "alerts": alerts}


@router.post("/alerts/{alert_id}/resolve")
async def resolve_alert(alert_id: str, request: ResolveAlertRequest):
    resolved = await _alert_engine.resolve_alert(alert_id, request.resolution_note)
    if not resolved:
        raise HTTPException(status_code=404, detail="Alert not found")
    return {"success": True, "alert": resolved}


@router.get("/alerts/composite")
async def get_composite_alerts(status: str = "active"):
    await _ensure_default_connectors()
    alerts = await _alert_engine.get_composite_alerts(status=status)
    return {"success": True, "alerts": alerts}


@router.get("/alerts/analysis")
async def get_alert_analysis(days: int = 7):
    analysis = await _alert_engine.analyze_alert_patterns(days=days)
    return {"success": "error" not in analysis, "analysis": analysis}


@router.get("/dashboard")
async def get_dashboard(executive_level: str = "general_manager"):
    await _ensure_default_connectors()
    dashboard = await _dashboard.render_dashboard(executive_level=executive_level)
    return {"success": True, "dashboard": dashboard}


@router.get("/dashboard/drilldown")
async def get_dashboard_drilldown(entity: str, entity_id: str):
    await _ensure_default_connectors()
    details = await _dashboard.get_drilldown_data(entity, entity_id)
    return {"success": "error" not in details, "details": details}
