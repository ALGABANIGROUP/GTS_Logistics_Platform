import asyncio

from backend.bots.maintenance_dev import MaintenanceDevBot


def test_dashboard_contains_maintenance_sections() -> None:
    bot = MaintenanceDevBot()
    result = asyncio.run(bot.run({"action": "dashboard"}))

    assert result["ok"] is True
    assert "active_errors" in result
    assert "pending_updates" in result
    assert "bot_health" in result


def test_process_message_routes_error_reporting() -> None:
    bot = MaintenanceDevBot()
    result = asyncio.run(
        bot.process_message(
            "Report an error",
            {"bot_name": "legal_bot", "error_message": "timeout after 30 seconds"},
        )
    )

    assert result["ok"] is True
    assert result["analysis"]["error_type"] == "timeout"
    assert result["auto_fix_applied"] is False or result["fix_result"] is not None


def test_error_resolution_and_fix_stats_work() -> None:
    bot = MaintenanceDevBot()
    reported = asyncio.run(
        bot.run(
            {
                "context": {
                    "action": "report_error",
                    "bot_name": "dispatcher",
                    "error_message": "database connection failed",
                    "severity": "critical",
                }
            }
        )
    )
    resolved = asyncio.run(
        bot.run(
            {
                "context": {
                    "action": "resolve_error",
                    "error_id": reported["error_id"],
                    "fix_applied": "docker compose restart dispatcher",
                }
            }
        )
    )
    stats = asyncio.run(bot.run({"context": {"action": "fix_stats"}}))

    assert reported["ok"] is True
    assert resolved["status"] == "resolved"
    assert stats["ok"] is True
    assert stats["total_attempts"] >= 1


def test_updates_and_performance_actions_work() -> None:
    bot = MaintenanceDevBot()
    updates = asyncio.run(
        bot.run(
            {
                "context": {
                    "action": "check_updates",
                    "bot_name": "security_manager",
                    "current_version": "1.0.0",
                }
            }
        )
    )
    performance = asyncio.run(
        bot.run(
            {
                "context": {
                    "action": "analyze_performance",
                    "bot_name": "dispatcher",
                    "hours": 24,
                }
            }
        )
    )
    prediction = asyncio.run(
        bot.run({"context": {"action": "predict_failures", "bot_name": "legal_bot"}})
    )

    assert updates["ok"] is True
    assert updates["update_available"] is True
    assert performance["ok"] is True
    assert "statistics" in performance
    assert prediction["ok"] is True
    assert prediction["failure_analysis"]["failure_probability"] > 0
