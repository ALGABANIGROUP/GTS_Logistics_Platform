import asyncio

from backend.bots.operations_manager import OperationsManagerBot


def test_dashboard_contains_operational_sections() -> None:
    bot = OperationsManagerBot()
    result = asyncio.run(bot.run({"action": "dashboard"}))

    assert result["ok"] is True
    assert "quick_stats" in result
    assert "reports" in result
    assert "workflows" in result
    assert result["quick_stats"]["reports_today"] >= 3


def test_process_message_dispatches_context_action() -> None:
    bot = OperationsManagerBot()
    result = asyncio.run(
        bot.process_message(
            "execute workflow",
            {"action": "execute_workflow", "workflow_name": "incident_response", "data": {"incident_id": "INC-9"}},
        )
    )

    assert result["ok"] is True
    assert result["workflow_name"] == "incident_response"
    assert result["progress"] == 100


def test_receive_report_creates_commands_for_delay() -> None:
    bot = OperationsManagerBot()
    result = asyncio.run(
        bot.run(
            {
                "context": {
                    "action": "receive_report",
                    "report": {
                        "bot_name": "dispatcher",
                        "type": "shipment_delay",
                        "severity": "high",
                        "summary": "Lane congestion is causing delays",
                        "data": {"shipment_id": "SH-9"},
                        "requires_action": True,
                    },
                }
            }
        )
    )

    assert result["ok"] is True
    assert result["actions_dispatched"] >= 2
    assert any(command["target_bot"] == "dispatcher" for command in result["commands"])
