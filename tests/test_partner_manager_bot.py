# tests/test_partner_manager_bot.py
# NOTE: ASCII only.
import asyncio

from backend.ai.policy import bot_access_policy
from backend.ai.roles.partner_manager import PartnerManagerBot


class _StubOperationsManager:
    def __init__(self) -> None:
        self.calls = []

    async def run(self, payload):
        self.calls.append(payload)
        return {"ok": True, "data": {"mock": True}}


class _StubRegistry:
    def __init__(self, ops):
        self._ops = ops

    def get(self, name):
        if name == "operations_manager":
            return self._ops
        return None


def test_partner_manager_listed_for_admin():
    data = bot_access_policy.list_available_bots("admin", set())
    keys = {bot["bot_key"] for bot in data.get("bots", [])}
    assert "partner_manager" in keys


def test_partner_manager_run_returns_normalized_response(monkeypatch):
    bot = PartnerManagerBot()
    ops = _StubOperationsManager()
    registry = _StubRegistry(ops)
    monkeypatch.setattr(bot, "_get_registry", lambda: registry)

    payload = {"action": "create_agreement", "partner_id": "p-001", "inputs": {"term": "net30"}}
    result = asyncio.run(bot.run(payload))

    assert result["ok"] is True
    assert result["action"] == "create_agreement"
    assert result["partner_id"] == "p-001"
    assert "data" in result
    assert "workflow" in result["data"]
    assert ops.calls


def test_partner_manager_orchestration_calls_operations_manager(monkeypatch):
    bot = PartnerManagerBot()
    ops = _StubOperationsManager()
    registry = _StubRegistry(ops)
    monkeypatch.setattr(bot, "_get_registry", lambda: registry)

    payload = {"action": "risk_report", "partner_id": "p-002", "inputs": {}}
    result = asyncio.run(bot.run(payload))

    assert result["ok"] is True
    assert len(ops.calls) == 1
    assert ops.calls[0]["workflow_name"] == "partner_risk_report"


def test_partner_manager_rbac_denies_customer():
    decision = bot_access_policy.can_see_bot("customer", set(), "partner_manager")
    assert decision["allowed"] is False
