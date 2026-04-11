from __future__ import annotations

from datetime import datetime
import logging
from typing import Any

from fastapi import APIRouter, Body, HTTPException, Query
from pydantic import BaseModel, Field

from backend.core.alerts.smart_alert_engine import AlertCategory, AlertSeverity, SmartAlertEngine
from backend.core.reporting.smart_report_engine import SmartReportEngine
from backend.services.executive_dashboard import ExecutiveDashboard


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/bot-collaboration", tags=["Bot Collaboration"])


class AlertIngestRequest(BaseModel):
    bot_name: str
    category: AlertCategory = AlertCategory.OPERATIONAL
    severity: AlertSeverity = AlertSeverity.INFO
    title: str
    description: str
    affected_entity: str = "system"
    data: dict[str, Any] = Field(default_factory=dict)
    auto_resolve: bool = False
    auto_resolve_time: int = 300


class AlertResolveRequest(BaseModel):
    resolution_note: str = ""


class _BaseConnector:
    def __init__(self, bot_name: str) -> None:
        self.bot_name = bot_name
        self.received_composites: list[dict[str, Any]] = []

    async def receive_composite_alert(self, payload: dict[str, Any]) -> None:
        self.received_composites.append(payload)


class _FreightBrokerConnector(_BaseConnector):
    async def get_status(self) -> dict[str, Any]:
        return {
            "bot_name": self.bot_name,
            "total_shipments": 128,
            "delayed_shipments": 7,
            "on_time_delivery": 94.5,
            "active_drivers": 38,
            "average_delivery_time": 18,
            "target_delivery_time": 20,
        }


class _DispatcherConnector(_BaseConnector):
    async def get_metrics(self) -> dict[str, Any]:
        return {
            "bot_name": self.bot_name,
            "total_shipments": 128,
            "delayed_shipments": 5,
            "on_time_delivery": 96.0,
            "active_drivers": 41,
            "average_delivery_time": 17,
            "target_delivery_time": 20,
        }


class _SafetyConnector(_BaseConnector):
    async def get_incidents(self) -> dict[str, Any]:
        return {
            "bot_name": self.bot_name,
            "incidents": 2,
            "accidents": 0,
            "safety_score": 92,
        }


class _FinanceConnector(_BaseConnector):
    async def get_metrics(self) -> dict[str, Any]:
        return {
            "bot_name": self.bot_name,
            "revenue": 245000,
            "profit_margin": 28,
            "revenue_growth": 12,
            "pending_payments": 6,
        }


class _SalesConnector(_BaseConnector):
    async def get_performance_metrics(self) -> dict[str, Any]:
        return {
            "bot_name": self.bot_name,
            "revenue": 245000,
            "profit_margin": 24,
            "revenue_growth": 15,
        }


class _CustomerServiceConnector(_BaseConnector):
    async def get_satisfaction_metrics(self) -> dict[str, Any]:
        return {
            "bot_name": self.bot_name,
            "satisfaction_score": 88,
            "open_tickets": 4,
            "resolved_tickets": 36,
            "average_response_time": 12,
            "target_response_time": 15,
        }


class _SystemManagerConnector(_BaseConnector):
    async def get_health_status(self) -> dict[str, Any]:
        return {
            "bot_name": self.bot_name,
            "cpu_usage": 41,
            "response_time": 110,
            "threshold": 250,
            "uptime": 99.93,
            "error_rate": 0.01,
        }


_report_engine: SmartReportEngine = SmartReportEngine()
_alert_engine: SmartAlertEngine = SmartAlertEngine()
_dashboard: ExecutiveDashboard = ExecutiveDashboard(_report_engine, _alert_engine)
_connectors_initialized = False

_REPORT_CONNECTORS: dict[str, _BaseConnector] = {
    "freight_broker": _FreightBrokerConnector("freight_broker"),
    "dispatcher": _DispatcherConnector("dispatcher"),
    "safety_manager": _SafetyConnector("safety_manager"),
    "finance_bot": _FinanceConnector("finance_bot"),
    "sales_bot": _SalesConnector("sales_bot"),
    "customer_service": _CustomerServiceConnector("customer_service"),
    "system_manager": _SystemManagerConnector("system_manager"),
}


async def _ensure_connectors_initialized() -> None:
    global _connectors_initialized
    if _connectors_initialized:
        return
    await _report_engine.register_bot_connectors(_REPORT_CONNECTORS)
    await _alert_engine.register_bot_connectors(_REPORT_CONNECTORS)
    _connectors_initialized = True


@router.get("/connectors")
async def get_connectors() -> dict[str, Any]:
    await _ensure_connectors_initialized()
    return {
        "report_connectors": sorted(_report_engine.bot_connectors.keys()),
        "alert_connectors": sorted(_alert_engine.bot_connectors.keys()),
        "initialized": _connectors_initialized,
    }


@router.get("/report")
async def get_unified_report(force_refresh: bool = False) -> dict[str, Any]:
    await _ensure_connectors_initialized()
    report = await _report_engine.generate_unified_report(force_refresh=force_refresh)
    return {"report": report}


@router.post("/alerts/ingest")
async def ingest_alert(payload: AlertIngestRequest) -> dict[str, Any]:
    await _ensure_connectors_initialized()
    alert = await _alert_engine.ingest_alert(payload.model_dump())
    return {"alert": alert}


@router.get("/alerts/active")
async def get_active_alerts(severity: AlertSeverity | None = None) -> dict[str, Any]:
    await _ensure_connectors_initialized()
    alerts = await _alert_engine.get_active_alerts(severity=severity)
    return {"alerts": alerts, "total": len(alerts)}


@router.get("/alerts/composite")
async def get_composite_alerts(status: str = "active") -> dict[str, Any]:
    await _ensure_connectors_initialized()
    alerts = await _alert_engine.get_composite_alerts(status=status)
    return {"alerts": alerts, "total": len(alerts)}


@router.post("/alerts/{alert_id}/resolve")
async def resolve_alert(alert_id: str, payload: AlertResolveRequest = Body(default_factory=AlertResolveRequest)) -> dict[str, Any]:
    await _ensure_connectors_initialized()
    resolved = await _alert_engine.resolve_alert(alert_id, payload.resolution_note)
    if resolved is None:
        raise HTTPException(status_code=404, detail="Alert not found")
    return {"alert": resolved}


@router.get("/dashboard")
async def get_dashboard(executive_level: str = "general_manager") -> dict[str, Any]:
    await _ensure_connectors_initialized()
    dashboard = await _dashboard.render_dashboard(executive_level=executive_level)
    return {"dashboard": dashboard}


@router.get("/dashboard/drilldown")
async def get_dashboard_drilldown(
    entity: str = Query(...),
    entity_id: str = Query(...),
) -> dict[str, Any]:
    await _ensure_connectors_initialized()
    details = await _dashboard.get_drilldown_data(entity=entity, entity_id=entity_id)
    if details.get("error"):
        raise HTTPException(status_code=404, detail=details["error"])
    return {"details": details}


@router.get("/health")
async def collaboration_health() -> dict[str, Any]:
    await _ensure_connectors_initialized()
    active_alerts = await _alert_engine.get_active_alerts()
    return {
        "status": "healthy",
        "report_connectors": len(_report_engine.bot_connectors),
        "alert_connectors": len(_alert_engine.bot_connectors),
        "active_alerts": len(active_alerts),
        "timestamp": datetime.utcnow().isoformat(),
    }
