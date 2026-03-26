from __future__ import annotations

import importlib
import pytest

from backend import main as main_module
from backend.main import app
from backend.database.config import get_db_async
from backend.security.auth import get_current_user
from backend.security import auth as backend_auth_module

try:
    import security.auth as runtime_auth_module
except Exception:  # pragma: no cover
    runtime_auth_module = None

runtime_integrations_module = importlib.import_module("routes.integrations_api")


class DummySession:
    def __init__(self):
        self.rows = []
        self.commits = 0

    async def execute(self, *args, **kwargs):
        class Result:
            def __init__(self, rows):
                self._rows = rows

            def fetchall(self):
                return self._rows

        return Result(self.rows)

    async def commit(self):
        self.commits += 1

    async def close(self):
        return None


@pytest.fixture
def fake_db():
    return DummySession()


@pytest.fixture(autouse=True)
def _overrides(fake_db):
    async def _fake_db():
        try:
            yield fake_db
        finally:
            await fake_db.close()

    async def _fake_user():
        return {"email": "admin@test.local", "role": "admin", "effective_role": "admin"}

    app.dependency_overrides[get_db_async] = _fake_db
    app.dependency_overrides[get_current_user] = _fake_user
    app.dependency_overrides[backend_auth_module.get_current_user] = _fake_user
    if runtime_auth_module is not None:
        app.dependency_overrides[runtime_auth_module.get_current_user] = _fake_user
    if getattr(main_module, "get_current_user", None) is not None:
        app.dependency_overrides[main_module.get_current_user] = _fake_user
    app.dependency_overrides[runtime_integrations_module.get_db_async] = _fake_db
    app.dependency_overrides[runtime_integrations_module.get_current_user] = _fake_user
    yield
    app.dependency_overrides.pop(get_db_async, None)
    app.dependency_overrides.pop(get_current_user, None)
    app.dependency_overrides.pop(backend_auth_module.get_current_user, None)
    if runtime_auth_module is not None:
        app.dependency_overrides.pop(runtime_auth_module.get_current_user, None)
    if getattr(main_module, "get_current_user", None) is not None:
        app.dependency_overrides.pop(main_module.get_current_user, None)
    app.dependency_overrides.pop(runtime_integrations_module.get_db_async, None)
    app.dependency_overrides.pop(runtime_integrations_module.get_current_user, None)


@pytest.mark.asyncio
async def test_integrations_list_endpoint(async_client):
    response = await async_client.get("/api/v1/integrations")
    assert response.status_code == 200
    body = response.json()
    assert "connected_systems" in body
    assert body["total_integrations"] >= 1


@pytest.mark.asyncio
async def test_integrations_connect_endpoint(async_client):
    response = await async_client.post(
        "/api/v1/integrations/slack/connect",
        json={"webhook_url": "https://hooks.slack.com/services/T000/B000/XYZ"},
    )
    assert response.status_code == 200
    assert response.json()["success"] is True


@pytest.mark.asyncio
async def test_integrations_disconnect_endpoint(async_client):
    response = await async_client.post("/api/v1/integrations/slack/disconnect")
    assert response.status_code == 200
    assert response.json()["status"] == "disconnected"
