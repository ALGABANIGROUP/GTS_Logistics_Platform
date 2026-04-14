from __future__ import annotations

import sys
import pytest

from backend.main import app
from backend.database.config import get_db_async

portal_module = sys.modules.get("routes.portal_requests")
if portal_module is None:
    from backend.routes import portal_requests as portal_module


@pytest.fixture(autouse=True)
def _override_db_dependency():
    async def _fake_db():
        class DummySession:
            async def close(self):
                return None

        dummy = DummySession()
        try:
            yield dummy
        finally:
            await dummy.close()

    app.dependency_overrides[get_db_async] = _fake_db
    yield
    app.dependency_overrides.pop(get_db_async, None)


@pytest.mark.asyncio
async def test_public_portal_submission_returns_created_request(async_client, monkeypatch):
    async def fake_verify_hcaptcha(_token: str) -> bool:
        return True

    async def fake_check_ip_rate_limit(_ip: str, requests_per_hour: int = 5, session=None) -> bool:
        return False

    async def fake_get_portal_request_by_email(_email: str, tenant_id=None, session=None):
        return None

    async def fake_create_portal_request(**kwargs):
        return {"id": 77, "request_id": "REQ-77", "status": "pending"}

    async def fake_create_verification_token(*args, **kwargs):
        return True

    async def fake_create_admin_notification(*args, **kwargs):
        return True

    async def fake_log_audit_action(*args, **kwargs):
        return True

    async def fake_send_email(*args, **kwargs):
        return None

    async def fake_send_admin_notification(*args, **kwargs):
        return None

    monkeypatch.setattr(portal_module, "verify_hcaptcha", fake_verify_hcaptcha)
    monkeypatch.setattr(portal_module, "check_ip_rate_limit", fake_check_ip_rate_limit)
    monkeypatch.setattr(portal_module, "get_portal_request_by_email", fake_get_portal_request_by_email)
    monkeypatch.setattr(portal_module, "create_portal_request", fake_create_portal_request)
    monkeypatch.setattr(portal_module, "create_verification_token", fake_create_verification_token)
    monkeypatch.setattr(portal_module, "create_admin_notification", fake_create_admin_notification)
    monkeypatch.setattr(portal_module, "log_audit_action", fake_log_audit_action)
    monkeypatch.setattr(portal_module, "send_email", fake_send_email)
    monkeypatch.setattr(portal_module, "send_admin_notification", fake_send_admin_notification)

    response = await async_client.post(
        "/portal/requests",
        data={
            "full_name": "Test User",
            "company": "Acme Co",
            "email": "test@example.com",
            "mobile": "+1-555-1234",
            "country": "US",
            "user_type": "shipper",
            "comment": "Integration test",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == "REQ-77"
    assert body["status"] == "pending"
    assert body["success"] is True


@pytest.mark.asyncio
async def test_request_status_returns_normalized_payload(async_client, monkeypatch):
    async def fake_get_portal_request_by_request_id(request_id: str, session=None):
        return {
            "id": 77,
            "request_id": request_id,
            "status": "approved",
            "rejection_code": None,
            "rejection_message": None,
            "decided_at": None,
        }

    monkeypatch.setattr(portal_module, "get_portal_request_by_request_id", fake_get_portal_request_by_request_id)

    response = await async_client.get("/portal/requests/REQ-77/status")

    assert response.status_code == 200
    assert response.json()["status"] == "approved"


@pytest.mark.asyncio
async def test_verify_email_endpoint_success(async_client, monkeypatch):
    async def fake_verify_email(token: str, session=None):
        return "user@example.com" if token == "good-token" else None

    monkeypatch.setattr("backend.services.portal_requests_store.verify_email", fake_verify_email)

    response = await async_client.get("/portal/verify-email", params={"token": "good-token"})

    assert response.status_code == 200
    assert response.json()["success"] is True
