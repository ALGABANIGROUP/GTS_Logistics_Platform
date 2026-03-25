# backend/tests/test_fincen_service.py
import pytest
import os
from httpx import Response

from backend.services.fincen_api import FincenService, get_fincen_service

# Sample transaction data
SAMPLE_TRANSACTION = {
    "amount": 12000.00,
    "currency": "USD",
    "customer_id": "CUST-123",
    "transaction_type": "wire_transfer"
}

@pytest.mark.asyncio
async def test_fincen_service_disabled_mode(monkeypatch):
    """Test that the service runs in mock mode when no API key is set."""
    monkeypatch.delenv("FINCEN_API_KEY", raising=False)
    
    # Use the factory to get a fresh instance
    service = FincenService()
    
    assert not service.enabled
    
    # Test submit report
    response = await service.submit_transaction_report(SAMPLE_TRANSACTION)
    assert response["status"] == "mock"
    assert "MOCK-" in response["report_id"]
    assert "mock mode" in response["detail"]
    
    # Test get status
    status_response = await service.get_report_status("MOCK-123")
    assert status_response["status"] == "mock"
    assert status_response["processing_status"] == "completed"

@pytest.mark.asyncio
async def test_fincen_service_enabled_mode_submit_success(monkeypatch, httpx_mock):
    """Test successful report submission in enabled mode."""
    monkeypatch.setenv("FINCEN_API_KEY", "test-api-key")
    
    # Mock the API endpoint
    httpx_mock.add_response(
        method="POST",
        url="https://api.fincen.gov/v1/reports/ctr",
        json={"report_id": "FINCEN-REPORT-XYZ", "status": "accepted"},
        status_code=200
    )
    
    service = FincenService()
    assert service.enabled
    
    response = await service.submit_transaction_report(SAMPLE_TRANSACTION, report_type="ctr")
    
    assert response["status"] == "success"
    assert response["report_id"] == "FINCEN-REPORT-XYZ"
    assert "acknowledgment" in response

@pytest.mark.asyncio
async def test_fincen_service_enabled_mode_submit_api_error(monkeypatch, httpx_mock):
    """Test API error during report submission."""
    monkeypatch.setenv("FINCEN_API_KEY", "test-api-key")
    
    # Mock the API endpoint to return an error
    httpx_mock.add_response(
        method="POST",
        url="https://api.fincen.gov/v1/reports/sar",
        text="Internal Server Error",
        status_code=500
    )
    
    service = FincenService()
    assert service.enabled
    
    response = await service.submit_transaction_report(SAMPLE_TRANSACTION, report_type="sar")
    
    assert response["status"] == "error"
    assert response["error_code"] == 500
    assert "Internal Server Error" in response["detail"]

@pytest.mark.asyncio
async def test_fincen_get_report_status_success(monkeypatch, httpx_mock):
    """Test successfully getting a report status."""
    monkeypatch.setenv("FINCEN_API_KEY", "test-api-key")
    
    report_id = "FINCEN-REPORT-XYZ"
    
    httpx_mock.add_response(
        method="GET",
        url=f"https://api.fincen.gov/v1/reports/{report_id}",
        json={"id": report_id, "status": "processed", "details": "Report processed successfully."},
        status_code=200
    )
    
    service = FincenService()
    response = await service.get_report_status(report_id)
    
    assert response["status"] == "success"
    assert response["report_id"] == report_id
    assert response["report_data"]["status"] == "processed"

@pytest.mark.asyncio
async def test_validate_transaction():
    """Test the local transaction validation logic."""
    service = FincenService() # API key not needed for validation
    
    # Test case 1: Valid transaction under threshold
    valid_under_10k = {"amount": 5000, "currency": "USD"}
    result1 = await service.validate_transaction(valid_under_10k)
    assert result1["valid"]
    assert not result1["errors"]
    assert not result1["warnings"]
    assert not result1["requires_reporting"]
    
    # Test case 2: Transaction over threshold
    valid_over_10k = {"amount": 15000, "currency": "USD"}
    result2 = await service.validate_transaction(valid_over_10k)
    assert result2["valid"]
    assert not result2["errors"]
    assert len(result2["warnings"]) == 1
    assert "exceeds $10,000" in result2["warnings"][0]
    assert result2["requires_reporting"]
    
    # Test case 3: Invalid transaction (missing amount)
    invalid_data = {"currency": "USD"}
    result3 = await service.validate_transaction(invalid_data)
    assert not result3["valid"]
    assert len(result3["errors"]) == 1
    assert "amount is required" in result3["errors"][0]