from __future__ import annotations

import asyncio

from backend.bots.general_manager import GeneralManagerBot
from backend.bots.information_coordinator import InformationCoordinatorBot
from backend.bots.legal_bot import LegalBot
from backend.bots.operations_manager import OperationsManagerBot
from backend.bots.security_manager import SecurityManagerBot
from backend.bots.system_manager import SystemManagerBot
from backend.bots.trainer_bot import TrainerBotRuntime
from backend.main import ai_registry, app
from fastapi.testclient import TestClient


EXPECTED_CORE_BOTS = {
    "partner_bot",
    "customer_service",
    "ai_dispatcher",
    "documents_manager",
    "sales_bot",
    "safety_bot",
    "intelligence_bot",
    "mapleload_bot",
    "general_manager",
    "operations_manager",
    "freight_broker",
    "information_coordinator",
    "legal_bot",
    "security_bot",
    "system_bot",
    "maintenance_dev",
    "marketing_manager",
    "trainer_bot",
}


def test_ai_registry_contains_expected_core_bots() -> None:
    from backend.ai.registry_fill import ensure_all_bots_registered

    ensure_all_bots_registered(ai_registry)
    registered = set(ai_registry.list().keys())
    missing = EXPECTED_CORE_BOTS - registered

    assert not missing, f"Missing core bot registrations: {sorted(missing)}"


def test_public_backend_smoke_routes_respond() -> None:
    client = TestClient(app)

    root = client.get("/")
    healthz = client.get("/healthz")
    ping = client.get("/health/ping")
    roles = client.get("/test/roles")

    assert root.status_code == 200
    assert root.json()["ok"] is True

    assert healthz.status_code == 200
    assert healthz.json()["status"] == "ok"

    assert ping.status_code == 200
    assert ping.json()["ok"] is True

    assert roles.status_code == 200
    assert roles.json()["status"] in {"success", "error"}


def test_operations_to_dispatch_flow_runs_in_process() -> None:
    bot = OperationsManagerBot()
    result = asyncio.run(
        bot.run(
            {
                "context": {
                    "action": "receive_report",
                    "report": {
                        "bot_name": "freight_broker",
                        "type": "shipment_delay",
                        "severity": "high",
                        "summary": "Lane congestion requires dispatch intervention.",
                        "data": {"shipment_id": "SH-1234", "delay_hours": 3},
                        "requires_action": True,
                    },
                }
            }
        )
    )

    assert result["ok"] is True
    assert result["actions_dispatched"] >= 2
    assert any(command["target_bot"] == "dispatcher" for command in result["commands"])


def test_general_manager_dashboard_exposes_executive_summary() -> None:
    bot = GeneralManagerBot()
    result = asyncio.run(bot.run({"action": "dashboard"}))

    assert result["ok"] is True
    assert "unified_kpi" in result
    assert "department_performance" in result
    assert "critical_alerts" in result


def test_system_manager_dashboard_exposes_system_summary() -> None:
    bot = SystemManagerBot()
    result = asyncio.run(bot.run({"action": "dashboard"}))

    assert result["ok"] is True
    assert "bot_health" in result
    assert "system_metrics" in result
    assert "cache_hit_rate" in result


def test_information_coordinator_dashboard_exposes_data_quality_summary() -> None:
    bot = InformationCoordinatorBot()
    result = asyncio.run(bot.run({"action": "dashboard"}))

    assert result["ok"] is True
    assert "overview" in result
    assert "source_health" in result
    assert "conflicts" in result


def test_legal_dashboard_exposes_library_and_coverage_summary() -> None:
    bot = LegalBot()
    result = asyncio.run(bot.run({"action": "dashboard"}))

    assert result["ok"] is True
    assert result["stats"]["total_laws"] >= 5
    assert result["coverage"]["international"] >= 1


def test_security_dashboard_exposes_security_summary() -> None:
    bot = SecurityManagerBot()
    result = asyncio.run(bot.run({"action": "dashboard"}))

    assert result["ok"] is True
    assert "quick_stats" in result
    assert "compliance" in result


def test_trainer_runtime_smoke_actions_work() -> None:
    bot = TrainerBotRuntime()

    status = asyncio.run(bot.status())
    config = asyncio.run(bot.config())
    registration = asyncio.run(bot.register_bot("customer_service", "beginner", "1.0"))
    assessment = asyncio.run(bot.assess_bot("customer_service"))

    assert status["ok"] is True
    assert config["name"] == "trainer_bot"
    assert registration["ok"] is True
    assert assessment["ok"] is True
