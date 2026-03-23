from __future__ import annotations

from datetime import datetime, timezone

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from backend.models.email_center import BotMailboxRule, Mailbox
from backend.routes import email_center as email_center_module


class FakeEmailDb:
    def __init__(self):
        self.mailboxes = {
            1: Mailbox(
                id=1,
                email_address="ops@example.com",
                owner_user_id=7,
                assigned_bot_key="ops_bot",
                bot_config={"language": "en"},
            ),
            2: Mailbox(
                id=2,
                email_address="admin@example.com",
                owner_user_id=99,
                assigned_bot_key="admin_bot",
            ),
        }
        self.rules = {
            1: BotMailboxRule(
                id=1,
                mailbox_id=1,
                bot_key="finance_bot",
                condition_field="subject",
                condition_operator="contains",
                condition_value="invoice",
                action_type="process",
                priority=1,
                is_active=True,
                created_by=1,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
        }
        self.next_rule_id = 2

    async def get(self, model, identifier):
        if model is Mailbox:
            return self.mailboxes.get(identifier)
        if model is BotMailboxRule:
            return self.rules.get(identifier)
        return None

    def add(self, obj):
        if isinstance(obj, BotMailboxRule):
            if obj.id is None:
                obj.id = self.next_rule_id
                self.next_rule_id += 1
            now = datetime.now(timezone.utc)
            if not obj.created_at:
                obj.created_at = now
            if not obj.updated_at:
                obj.updated_at = now
            self.rules[obj.id] = obj

    async def commit(self):
        return None

    async def refresh(self, _obj):
        return None

    async def delete(self, obj):
        if isinstance(obj, BotMailboxRule):
            self.rules.pop(obj.id, None)


class FakeRoutingEngine:
    def __init__(self, db):
        self.db = db

    async def get_rules_for_mailbox(self, mailbox_id: int):
        rules = [rule for rule in self.db.rules.values() if rule.mailbox_id == mailbox_id]
        rules = sorted(rules, key=lambda rule: ((rule.priority or 0), rule.id or 0))
        return [email_center_module._rule_to_dict(rule) for rule in rules]

    async def apply_routing_to_message(self, message_id: int):
        return True, "finance_bot" if message_id == 123 else None


@pytest.fixture
def email_test_app(monkeypatch):
    db = FakeEmailDb()
    app = FastAPI()
    app.include_router(email_center_module.router)
    current_user = {"id": 1, "role": "super_admin", "effective_role": "super_admin"}

    async def fake_current_user():
        return current_user

    async def fake_db():
        yield db

    monkeypatch.setattr(email_center_module, "EmailRoutingEngine", FakeRoutingEngine)
    app.dependency_overrides[email_center_module.get_current_user] = fake_current_user
    app.dependency_overrides[email_center_module.get_async_session] = fake_db
    return app, db, current_user


@pytest.fixture
async def email_client(email_test_app):
    app, _, _ = email_test_app
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client


@pytest.mark.asyncio
async def test_assign_bot_to_mailbox_requires_admin_and_updates_state(email_client, email_test_app):
    _, db, current_user = email_test_app
    current_user.update({"id": 1, "role": "super_admin", "effective_role": "super_admin"})

    response = await email_client.patch(
        "/api/v1/email/mailboxes/1/assign-bot",
        json={"bot_key": "finance_bot", "config": {"language": "en"}},
    )

    assert response.status_code == 200
    assert response.json()["assigned_bot_key"] == "finance_bot"
    assert db.mailboxes[1].assigned_bot_key == "finance_bot"


@pytest.mark.asyncio
async def test_get_assigned_bot_allows_mailbox_owner(email_client, email_test_app):
    _, _, current_user = email_test_app
    current_user.update({"id": 7, "role": "user", "effective_role": "user"})

    response = await email_client.get("/api/v1/email/mailboxes/1/assigned-bot")

    assert response.status_code == 200
    assert response.json()["mailbox_id"] == 1
    assert response.json()["assigned_bot_key"] == "ops_bot"


@pytest.mark.asyncio
async def test_get_assigned_bot_rejects_non_owner_non_admin(email_client, email_test_app):
    _, _, current_user = email_test_app
    current_user.update({"id": 555, "role": "user", "effective_role": "user"})

    response = await email_client.get("/api/v1/email/mailboxes/1/assigned-bot")

    assert response.status_code == 403
    assert response.json()["detail"] == "Mailbox access denied"


@pytest.mark.asyncio
async def test_create_rule_validates_operator(email_client, email_test_app):
    _, _, current_user = email_test_app
    current_user.update({"id": 1, "role": "super_admin", "effective_role": "super_admin"})

    response = await email_client.post(
        "/api/v1/email/mailboxes/1/rules",
        json={
            "condition_field": "subject",
            "condition_operator": "bad_operator",
            "condition_value": "invoice",
            "action_type": "process",
        },
    )

    assert response.status_code == 400
    assert "Invalid condition operator" in response.json()["detail"]


@pytest.mark.asyncio
async def test_rule_crud_flow(email_client, email_test_app):
    _, db, current_user = email_test_app
    current_user.update({"id": 1, "role": "super_admin", "effective_role": "super_admin"})

    create_response = await email_client.post(
        "/api/v1/email/mailboxes/1/rules",
        json={
            "bot_key": "customer_service",
            "condition_field": "body",
            "condition_operator": "contains",
            "condition_value": "support",
            "action_type": "assign",
            "action_config": {"user_id": 42},
            "priority": 5,
            "is_active": True,
        },
    )
    assert create_response.status_code == 200
    rule_id = create_response.json()["id"]

    list_response = await email_client.get("/api/v1/email/mailboxes/1/rules")
    assert list_response.status_code == 200
    assert list_response.json()["count"] >= 2

    get_response = await email_client.get(f"/api/v1/email/rules/{rule_id}")
    assert get_response.status_code == 200
    assert get_response.json()["bot_key"] == "customer_service"

    update_response = await email_client.patch(
        f"/api/v1/email/rules/{rule_id}",
        json={"priority": 2, "is_active": False},
    )
    assert update_response.status_code == 200
    assert update_response.json()["priority"] == 2
    assert update_response.json()["is_active"] is False
    assert db.rules[rule_id].priority == 2

    delete_response = await email_client.delete(f"/api/v1/email/rules/{rule_id}")
    assert delete_response.status_code == 200
    assert delete_response.json()["ok"] is True
    assert rule_id not in db.rules


@pytest.mark.asyncio
async def test_manual_route_message_requires_admin(email_client, email_test_app):
    _, _, current_user = email_test_app
    current_user.update({"id": 1, "role": "user", "effective_role": "user"})

    response = await email_client.post("/api/v1/email/messages/123/route")

    assert response.status_code == 403
    assert response.json()["detail"] == "Email admin access required"


@pytest.mark.asyncio
async def test_manual_route_message_returns_result(email_client, email_test_app):
    _, _, current_user = email_test_app
    current_user.update({"id": 1, "role": "super_admin", "effective_role": "super_admin"})

    response = await email_client.post("/api/v1/email/messages/123/route")

    assert response.status_code == 200
    assert response.json() == {
        "message_id": 123,
        "routing_applied": True,
        "assigned_bot": "finance_bot",
    }
