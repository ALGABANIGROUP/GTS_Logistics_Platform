from __future__ import annotations

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from backend.core.alerts.smart_alert_engine import SmartAlertEngine
from backend.core.reporting.smart_report_engine import SmartReportEngine
from backend.routes import bot_collaboration as bot_collaboration_module
from backend.services.executive_dashboard import ExecutiveDashboard


@pytest.fixture
def collaboration_app():
    app = FastAPI()
    bot_collaboration_module._report_engine = SmartReportEngine()
    bot_collaboration_module._alert_engine = SmartAlertEngine()
    bot_collaboration_module._dashboard = ExecutiveDashboard(
        bot_collaboration_module._report_engine,
        bot_collaboration_module._alert_engine,
    )
    bot_collaboration_module._connectors_initialized = False
    app.include_router(bot_collaboration_module.router)
    return app


@pytest.fixture
async def collaboration_client(collaboration_app):
    transport = ASGITransport(app=collaboration_app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client


@pytest.mark.asyncio
async def test_bot_collaboration_route_flow(collaboration_client: AsyncClient):
    connectors_response = await collaboration_client.get("/api/v1/bot-collaboration/connectors")
    assert connectors_response.status_code == 200
    assert "dispatcher" in connectors_response.json()["report_connectors"]

    report_response = await collaboration_client.get("/api/v1/bot-collaboration/report")
    assert report_response.status_code == 200
    assert report_response.json()["report"]["unified_kpi"]["overall_score"] > 0

    first_alert = await collaboration_client.post(
        "/api/v1/bot-collaboration/alerts/ingest",
        json={
            "bot_name": "freight_broker",
            "category": "operational",
            "severity": "high",
            "title": "Shipment delay detected",
            "description": "Shipment 1234 is delayed.",
            "affected_entity": "shipment_1234",
        },
    )
    assert first_alert.status_code == 200
    first_id = first_alert.json()["alert"]["alert_id"]

    second_alert = await collaboration_client.post(
        "/api/v1/bot-collaboration/alerts/ingest",
        json={
            "bot_name": "dispatcher",
            "category": "customer",
            "severity": "warning",
            "title": "Customer escalation",
            "description": "The delayed shipment triggered a complaint.",
            "affected_entity": "shipment_1234",
        },
    )
    assert second_alert.status_code == 200

    active_response = await collaboration_client.get("/api/v1/bot-collaboration/alerts/active")
    assert active_response.status_code == 200
    assert len(active_response.json()["alerts"]) == 2

    composite_response = await collaboration_client.get("/api/v1/bot-collaboration/alerts/composite")
    assert composite_response.status_code == 200
    assert composite_response.json()["alerts"]

    dashboard_response = await collaboration_client.get("/api/v1/bot-collaboration/dashboard")
    assert dashboard_response.status_code == 200
    assert dashboard_response.json()["dashboard"]["summary"]["status"] in {"Excellent", "Good", "Fair", "Critical"}

    resolve_response = await collaboration_client.post(
        f"/api/v1/bot-collaboration/alerts/{first_id}/resolve",
        json={"resolution_note": "Closed for route test."},
    )
    assert resolve_response.status_code == 200

    drilldown_response = await collaboration_client.get(
        "/api/v1/bot-collaboration/dashboard/drilldown",
        params={"entity": "shipment", "entity_id": "shipment_1234"},
    )
    assert drilldown_response.status_code == 200
    assert drilldown_response.json()["details"]["shipment_id"] == "shipment_1234"
