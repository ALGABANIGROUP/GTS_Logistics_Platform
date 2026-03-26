import importlib
import pytest
from httpx import ASGITransport, AsyncClient

from backend import main as main_module
from backend.main import app
from backend.security.auth import get_current_user
from backend.security import auth as backend_auth_module

try:
    import security.auth as runtime_auth_module
except Exception:  # pragma: no cover
    runtime_auth_module = None

runtime_maintenance_module = importlib.import_module("routes.maintenance_ai")


@pytest.fixture
def admin_override():
    async def _fake_admin_user():
        return {
        "email": "admin@test.local",
        "role": "admin",
        "effective_role": "admin",
        }

    app.dependency_overrides[get_current_user] = _fake_admin_user
    app.dependency_overrides[runtime_maintenance_module.get_current_user] = _fake_admin_user
    app.dependency_overrides[backend_auth_module.get_current_user] = _fake_admin_user
    if runtime_auth_module is not None:
        app.dependency_overrides[runtime_auth_module.get_current_user] = _fake_admin_user
    if getattr(main_module, "get_current_user", None) is not None:
        app.dependency_overrides[main_module.get_current_user] = _fake_admin_user
    yield
    app.dependency_overrides.pop(get_current_user, None)
    app.dependency_overrides.pop(runtime_maintenance_module.get_current_user, None)
    app.dependency_overrides.pop(backend_auth_module.get_current_user, None)
    if runtime_auth_module is not None:
        app.dependency_overrides.pop(runtime_auth_module.get_current_user, None)
    if getattr(main_module, "get_current_user", None) is not None:
        app.dependency_overrides.pop(main_module.get_current_user, None)


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
