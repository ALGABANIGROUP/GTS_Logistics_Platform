from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.routes.fincen_routes import router as fincen_router
from backend.security.auth import get_current_user
from backend.services.fincen_api import get_fincen_service


class StubFincenService:
    def __init__(self, result):
        self._result = result

    async def submit_transaction_report(self, payload, report_type="ctr"):
        return self._result

    async def get_report_status(self, report_id):
        return self._result | {"report_id": report_id}


def _build_client(service):
    app = FastAPI()
    app.include_router(fincen_router)
    app.dependency_overrides[get_current_user] = lambda: {"id": 1, "role": "admin"}
    app.dependency_overrides[get_fincen_service] = lambda: service
    return TestClient(app)


def test_submit_report_returns_503_when_credentials_missing():
    client = _build_client(
        StubFincenService(
            {
                "status": "error",
                "error_code": 503,
                "detail": "Service unavailable - missing FinCEN API credentials",
            }
        )
    )

    response = client.post("/api/v1/fincen/reports/ctr", json={"amount": 12000, "currency": "USD"})
    assert response.status_code == 503
    assert "missing FinCEN API credentials" in response.json()["detail"]


def test_get_report_status_returns_success_payload():
    client = _build_client(
        StubFincenService(
            {
                "status": "success",
                "report_data": {"status": "processed"},
            }
        )
    )

    response = client.get("/api/v1/fincen/reports/FIN-123")
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert response.json()["report_id"] == "FIN-123"
