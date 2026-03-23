import asyncio

from backend.bots.system_manager import SystemManagerBot


def test_dashboard_contains_system_sections() -> None:
    bot = SystemManagerBot()
    result = asyncio.run(bot.run({"action": "dashboard"}))

    assert result["ok"] is True
    assert "bot_health" in result
    assert "system_metrics" in result
    assert "cache_hit_rate" in result


def test_process_message_routes_sql_analysis() -> None:
    bot = SystemManagerBot()
    result = asyncio.run(
        bot.process_message(
            "Analyze this SQL query",
            {"query": "SELECT * FROM shipments WHERE customer_id = 12345"},
        )
    )

    assert result["ok"] is True
    assert result["health_score"] < 100
    assert any(issue["type"] == "select_star" for issue in result["issues"])


def test_cache_and_alert_actions_work() -> None:
    bot = SystemManagerBot()
    cache_set = asyncio.run(
        bot.run(
            {"context": {"action": "cache_set", "key": "system:health", "value": {"ok": True}, "ttl": 300}}
        )
    )
    cache_get = asyncio.run(bot.run({"context": {"action": "cache_get", "key": "system:health"}}))
    alerts = asyncio.run(bot.run({"context": {"action": "get_active_alerts"}}))
    resolved = asyncio.run(
        bot.run({"context": {"action": "resolve_alert", "alert_id": "ALERT001"}})
    )

    assert cache_set["ok"] is True
    assert cache_get["value"]["ok"] is True
    assert alerts["count"] >= 1
    assert resolved["status"] == "resolved"


def test_bot_checks_and_resource_prediction_work() -> None:
    bot = SystemManagerBot()
    all_bots = asyncio.run(bot.run({"context": {"action": "check_all_bots"}}))
    prediction = asyncio.run(bot.run({"context": {"action": "predict_resources", "days": 30}}))

    assert all_bots["ok"] is True
    assert all_bots["count"] >= 10
    assert prediction["ok"] is True
    assert "predicted" in prediction
