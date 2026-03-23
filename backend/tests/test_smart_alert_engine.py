from __future__ import annotations

import pytest

from backend.core.alerts.smart_alert_engine import SmartAlertEngine
from backend.routes.bot_collaboration import MockBotConnector


@pytest.mark.asyncio
async def test_smart_alert_engine_creates_composite_and_resolves():
    engine = SmartAlertEngine()
    await engine.register_bot_connectors(
        {
            "freight_broker": MockBotConnector("freight_broker"),
            "dispatcher": MockBotConnector("dispatcher"),
        }
    )

    first = await engine.ingest_alert(
        {
            "bot_name": "freight_broker",
            "category": "operational",
            "severity": "high",
            "title": "Shipment delay detected",
            "description": "Shipment 1234 is delayed.",
            "affected_entity": "shipment_1234",
        }
    )
    second = await engine.ingest_alert(
        {
            "bot_name": "dispatcher",
            "category": "operational",
            "severity": "warning",
            "title": "Driver availability reduced",
            "description": "Multiple drivers are unavailable.",
            "affected_entity": "shipment_1234",
        }
    )

    active_alerts = await engine.get_active_alerts()
    assert len(active_alerts) == 2

    composites = await engine.get_composite_alerts()
    assert len(composites) == 1
    assert composites[0]["correlation_score"] > 0

    resolved = await engine.resolve_alert(first["alert_id"], "Handled by operations.")
    assert resolved is not None
    assert resolved["is_resolved"] is True

    await engine.resolve_alert(second["alert_id"], "Driver schedule adjusted.")
    resolved_composites = await engine.get_composite_alerts(status="resolved")
    assert resolved_composites
