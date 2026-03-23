from __future__ import annotations

import pytest

from backend.core.reporting.smart_report_engine import ReportType, SmartReportEngine
from backend.routes.bot_collaboration import MockBotConnector


@pytest.mark.asyncio
async def test_smart_report_engine_generates_kpi_and_trends():
    engine = SmartReportEngine()
    await engine.register_bot_connectors(
        {
            "freight_broker": MockBotConnector("freight_broker"),
            "dispatcher": MockBotConnector("dispatcher"),
            "safety_manager": MockBotConnector("safety_manager"),
            "finance_bot": MockBotConnector("finance_bot"),
            "customer_service": MockBotConnector("customer_service"),
            "system_manager": MockBotConnector("system_manager"),
            "sales_bot": MockBotConnector("sales_bot"),
        }
    )

    report_one = await engine.generate_unified_report(force_refresh=True)
    assert report_one["report_type"] == ReportType.EXECUTIVE_OVERVIEW.value
    assert report_one["unified_kpi"]["overall_score"] > 0
    assert "shipments" in report_one["raw_data_summary"]

    report_two = await engine.generate_unified_report(force_refresh=True)
    assert report_two["unified_kpi"]["trends"]["direction"] in {"stable", "improving", "declining"}

    trends = await engine.get_historical_trends(days=30)
    assert trends["data_points"] >= 2
