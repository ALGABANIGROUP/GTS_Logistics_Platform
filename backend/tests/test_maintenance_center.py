import pytest
from httpx import ASGITransport, AsyncClient

from backend.main import app
from backend.security.auth import get_current_user


@pytest.fixture
def admin_override():
    app.dependency_overrides[get_current_user] = lambda: {
        "email": "admin@test.local",
        "role": "admin",
        "effective_role": "admin",
    }
    yield
    app.dependency_overrides.pop(get_current_user, None)


@pytest.fixture
async def client(admin_override):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_maintenance_reports_access(client: AsyncClient):
    resp = await client.get("/api/v1/maintenance/reports")
    assert resp.status_code == 200
    body = resp.json()
    assert body["ok"] is True
    assert isinstance(body["reports"], list)


@pytest.mark.asyncio
async def test_maintenance_support_tickets_access(client: AsyncClient):
    resp = await client.get("/api/v1/maintenance/support-tickets")
    assert resp.status_code == 200
    body = resp.json()
    assert body["ok"] is True
    assert isinstance(body["tickets"], list)


@pytest.mark.asyncio
async def test_maintenance_suggestions_access(client: AsyncClient):
    resp = await client.get("/api/v1/maintenance/suggested-developments")
    assert resp.status_code == 200
    body = resp.json()
    assert body["ok"] is True
    assert "developments" in body


@pytest.mark.asyncio
async def test_maintenance_approve_action(client: AsyncClient):
    resp = await client.post("/api/v1/maintenance/approve/1")
    assert resp.status_code == 200
    body = resp.json()
    assert body["ok"] is True
    assert body["dev_id"] == 1
