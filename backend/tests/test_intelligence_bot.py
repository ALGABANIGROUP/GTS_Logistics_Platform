import asyncio

from backend.bots.intelligence_bot import IntelligenceBot


def test_dashboard_contains_market_and_competitor_signals() -> None:
    bot = IntelligenceBot()
    dashboard = asyncio.run(bot.run({"action": "dashboard"}))

    assert dashboard["ok"] is True
    assert "overview" in dashboard
    assert "market" in dashboard
    assert "competitors" in dashboard
    assert dashboard["competitors"]["top_threat"]["market_share"] >= 18


def test_process_message_dispatches_context_action() -> None:
    bot = IntelligenceBot()

    result = asyncio.run(
        bot.process_message(
            "run a scenario",
            {
                "action": "scenario_analysis",
                "scenario": {"revenue": 3000000, "growth": 14, "market_share": 4.1},
                "variables": ["fuel_price", "competition"],
            },
        )
    )

    assert result["ok"] is True
    assert result["base_scenario"]["revenue"] == 3000000
    assert "optimistic" in result["scenarios"]


def test_competitor_analysis_action_returns_recommended_moves() -> None:
    bot = IntelligenceBot()
    result = asyncio.run(bot.run({"context": {"action": "competitor_analysis"}}))

    assert result["ok"] is True
    assert len(result["competitors"]) >= 3
    assert len(result["recommended_moves"]) >= 1


def test_ai_enhancement_dashboard_contains_new_sections() -> None:
    bot = IntelligenceBot()
    result = asyncio.run(bot.run({"context": {"action": "dashboard"}}))

    assert result["ok"] is True
    assert "ai_enhancements" in result
    assert "advanced_reports" in result
    assert "churn" in result["ai_enhancements"]
    assert "geo_analytics" in result["advanced_reports"]


def test_prediction_and_reporting_actions_return_expected_shapes() -> None:
    bot = IntelligenceBot()

    churn = asyncio.run(bot.run({"context": {"action": "churn_prediction"}}))
    demand = asyncio.run(bot.run({"context": {"action": "demand_forecast", "days": 28}}))
    anomalies = asyncio.run(bot.run({"context": {"action": "anomaly_detection"}}))
    report = asyncio.run(bot.run({"context": {"action": "executive_report", "report_type": "monthly"}}))

    assert churn["ok"] is True
    assert churn["at_risk_count"] >= 1
    assert len(churn["customers"]) >= 2

    assert demand["ok"] is True
    assert demand["trend"] == "increasing"
    assert len(demand["periods"]) >= 4

    assert anomalies["ok"] is True
    assert anomalies["count"] >= 1

    assert report["ok"] is True
    assert report["type"] == "monthly"
    assert "financial_highlights" in report
