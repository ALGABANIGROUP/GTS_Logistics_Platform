from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from backend.core.alerts.smart_alert_engine import AlertSeverity, SmartAlertEngine
from backend.core.reporting.smart_report_engine import ReportType, SmartReportEngine
from backend.services.real_bot_connector import RealBotConnector
from backend.services.executive_dashboard import ExecutiveDashboard


router = APIRouter(prefix="/api/v1/bot-collaboration", tags=["Bot Collaboration"])


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
        "freight_broker": RealBotConnector("freight_broker"),
        "dispatcher": RealBotConnector("dispatcher"),
        "safety_manager": RealBotConnector("safety_manager"),
        "finance_bot": RealBotConnector("finance_bot"),
        "customer_service": RealBotConnector("customer_service"),
        "system_manager": RealBotConnector("system_manager"),
        "sales_bot": RealBotConnector("sales_bot"),
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


@router.get("/bots/status")
async def get_bots_status():
    await _ensure_default_connectors()
    statuses = {}
    for bot_name, connector in _report_engine.bot_connectors.items():
        if hasattr(connector, "health_check"):
            statuses[bot_name] = await connector.health_check()
        else:
            statuses[bot_name] = {"status": "unknown"}

    available = [name for name, status in statuses.items() if status.get("status") != "unavailable"]
    if not available:
        return {
            "success": False,
            "status": 503,
            "error": "No bots available for collaboration",
            "data": {"available_bots": [], "bot_statuses": statuses},
        }

    return {
        "success": True,
        "available_bots": available,
        "bot_statuses": statuses,
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
