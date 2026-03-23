import asyncio

from backend.bots.general_manager import GeneralManagerBot


def test_dashboard_contains_executive_sections() -> None:
    bot = GeneralManagerBot()
    result = asyncio.run(bot.run({"action": "dashboard"}))

    assert result["ok"] is True
    assert "unified_kpi" in result
    assert "department_performance" in result
    assert "critical_alerts" in result
    assert result["team_status"]["active_bots"] >= 5


def test_process_message_dispatches_context_action() -> None:
    bot = GeneralManagerBot()
    result = asyncio.run(
        bot.process_message(
            "prepare leadership sync",
            {"action": "leadership_meeting", "meeting_type": "weekly"},
        )
    )

    assert result["ok"] is True
    assert result["meeting_type"] == "weekly"
    assert len(result["agenda"]) >= 3


def test_strategic_recommendations_return_roadmap() -> None:
    bot = GeneralManagerBot()
    result = asyncio.run(bot.run({"context": {"action": "strategic_recommendations"}}))

    assert result["ok"] is True
    assert len(result["top_recommendations"]) >= 2
    assert "short_term" in result["roadmap"]
