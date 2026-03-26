from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.routes import truckerpath_routes as truckerpath_routes_module


class _MissingCredentialsProvider:
    async def list_loads(self, *args, **kwargs):
        return {
            "ok": False,
            "status": 503,
            "error": "TruckerPath API credentials not configured",
            "message": "Service unavailable - missing API credentials.",
        }


def test_truckerpath_503_when_no_credentials(monkeypatch):
    app = FastAPI()
    app.include_router(truckerpath_routes_module.router)
    monkeypatch.setattr(
        truckerpath_routes_module,
        "get_provider",
        lambda name: _MissingCredentialsProvider,
    )

    client = TestClient(app)
    response = client.get("/truckerpath/loads")

    assert response.status_code == 503
    detail = response.json()["detail"]
    assert "missing api credentials" in str(detail).lower()
