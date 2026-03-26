# backend/tests/test_fincen_service.py
from __future__ import annotations

import pytest

from backend.services.fincen_api import FincenService

SAMPLE_TRANSACTION = {
    "amount": 12000.00,
    "currency": "USD",
    "customer_id": "CUST-123",
    "transaction_type": "wire_transfer",
}


class _FakeResponse:
    def __init__(self, status_code, json_data=None, text=""):
        self.status_code = status_code
        self._json_data = json_data or {}
        self.text = text

    def json(self):
        return self._json_data


class _FakeAsyncClient:
    def __init__(self, post_response=None, get_response=None):
        self._post_response = post_response
        self._get_response = get_response

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def post(self, *args, **kwargs):
        return self._post_response

    async def get(self, *args, **kwargs):
        return self._get_response


@pytest.mark.asyncio
async def test_fincen_service_returns_503_when_credentials_missing(monkeypatch):
    monkeypatch.delenv("FINCEN_API_KEY", raising=False)
    monkeypatch.delenv("FINCEN_API_SECRET", raising=False)

    service = FincenService()

    assert not service.enabled

    response = await service.submit_transaction_report(SAMPLE_TRANSACTION)
    assert response["status"] == "error"
    assert response["error_code"] == 503
    assert "missing FinCEN API credentials" in response["detail"]

    status_response = await service.get_report_status("FIN-123")
    assert status_response["status"] == "error"
    assert status_response["error_code"] == 503
    assert status_response["report_id"] == "FIN-123"


@pytest.mark.asyncio
async def test_fincen_service_enabled_mode_submit_success(monkeypatch):
    monkeypatch.setenv("FINCEN_API_KEY", "test-api-key")
    monkeypatch.setenv("FINCEN_API_SECRET", "test-api-secret")

    fake_response = _FakeResponse(
        200,
        json_data={"report_id": "FINCEN-REPORT-XYZ", "status": "accepted"},
    )
    monkeypatch.setattr(
        "backend.services.fincen_api.httpx.AsyncClient",
        lambda *args, **kwargs: _FakeAsyncClient(post_response=fake_response),
    )

    service = FincenService()
    response = await service.submit_transaction_report(SAMPLE_TRANSACTION, report_type="ctr")

    assert response["status"] == "success"
    assert response["report_id"] == "FINCEN-REPORT-XYZ"
    assert "acknowledgment" in response


@pytest.mark.asyncio
async def test_fincen_service_enabled_mode_submit_api_error(monkeypatch):
    monkeypatch.setenv("FINCEN_API_KEY", "test-api-key")
    monkeypatch.setenv("FINCEN_API_SECRET", "test-api-secret")

    fake_response = _FakeResponse(500, text="Internal Server Error")
    monkeypatch.setattr(
        "backend.services.fincen_api.httpx.AsyncClient",
        lambda *args, **kwargs: _FakeAsyncClient(post_response=fake_response),
    )

    service = FincenService()
    response = await service.submit_transaction_report(SAMPLE_TRANSACTION, report_type="sar")

    assert response["status"] == "error"
    assert response["error_code"] == 500
    assert "Internal Server Error" in response["detail"]


@pytest.mark.asyncio
async def test_fincen_get_report_status_success(monkeypatch):
    monkeypatch.setenv("FINCEN_API_KEY", "test-api-key")
    monkeypatch.setenv("FINCEN_API_SECRET", "test-api-secret")

    report_id = "FINCEN-REPORT-XYZ"
    fake_response = _FakeResponse(
        200,
        json_data={"id": report_id, "status": "processed", "details": "Report processed successfully."},
    )
    monkeypatch.setattr(
        "backend.services.fincen_api.httpx.AsyncClient",
        lambda *args, **kwargs: _FakeAsyncClient(get_response=fake_response),
    )

    service = FincenService()
    response = await service.get_report_status(report_id)

    assert response["status"] == "success"
    assert response["report_id"] == report_id
    assert response["report_data"]["status"] == "processed"


@pytest.mark.asyncio
async def test_validate_transaction():
    service = FincenService()

    valid_under_10k = {"amount": 5000, "currency": "USD"}
    result1 = await service.validate_transaction(valid_under_10k)
    assert result1["valid"]
    assert not result1["errors"]
    assert not result1["warnings"]
    assert not result1["requires_reporting"]

    valid_over_10k = {"amount": 15000, "currency": "USD"}
    result2 = await service.validate_transaction(valid_over_10k)
    assert result2["valid"]
    assert not result2["errors"]
    assert len(result2["warnings"]) == 1
    assert "exceeds $10,000" in result2["warnings"][0]
    assert result2["requires_reporting"]

    invalid_data = {"currency": "USD"}
    result3 = await service.validate_transaction(invalid_data)
    assert not result3["valid"]
    assert len(result3["errors"]) == 1
    assert "amount is required" in result3["errors"][0]
