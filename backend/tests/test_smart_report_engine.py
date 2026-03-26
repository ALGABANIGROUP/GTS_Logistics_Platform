from __future__ import annotations

import pytest

from backend.core.reporting.smart_report_engine import ReportType, SmartReportEngine


class StubBotConnector:
    def __init__(self, bot_name: str) -> None:
        self.bot_name = bot_name

    async def get_status(self) -> dict[str, object]:
        return {"total_shipments": 10, "on_time_delivery": 90, "delayed_shipments": 1}

    async def get_metrics(self) -> dict[str, object]:
        if self.bot_name == "dispatcher":
            return {"total_shipments": 10, "on_time_delivery": 90, "delayed_shipments": 1}
        return {"revenue": 1000, "profit_margin": 20, "revenue_growth": 10, "pending_payments": 100}

    async def get_incidents(self) -> dict[str, object]:
        return {"incidents": 1, "accidents": 0, "safety_score": 95}

    async def get_satisfaction_metrics(self) -> dict[str, object]:
        return {"satisfaction_score": 88, "open_tickets": 2, "resolved_tickets": 8}

    async def get_health_status(self) -> dict[str, object]:
        return {"uptime": 99.0, "response_time": 0.1, "threshold": 0.5, "error_rate": 0.01}

    async def get_performance_metrics(self) -> dict[str, object]:
        return {"revenue": 1000, "profit_margin": 20, "revenue_growth": 10, "pending_payments": 100}


@pytest.mark.asyncio
async def test_smart_report_engine_generates_kpi_and_trends():
    engine = SmartReportEngine()
    await engine.register_bot_connectors(
        {
            "freight_broker": StubBotConnector("freight_broker"),
            "dispatcher": StubBotConnector("dispatcher"),
            "safety_manager": StubBotConnector("safety_manager"),
            "finance_bot": StubBotConnector("finance_bot"),
            "customer_service": StubBotConnector("customer_service"),
            "system_manager": StubBotConnector("system_manager"),
            "sales_bot": StubBotConnector("sales_bot"),
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
