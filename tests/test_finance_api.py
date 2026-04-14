# tests/test_finance_api.py
import pytest

@pytest.mark.asyncio
async def test_finance_health_ok(async_client, dev_token):
    headers = {"Authorization": f"Bearer {dev_token}"}
    response = await async_client.get("/api/v1/finance/health", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data.get("status") == "healthy"
    assert data.get("service") == "unified_finance"

@pytest.mark.asyncio
async def test_expense_crud_flow(async_client, dev_token):
    headers = {"Authorization": f"Bearer {dev_token}"}

    # Create
    body = {"category": "fuel", "amount": 25.75, "description": "pytest", "vendor": "cli", "status": "PENDING"}
    response = await async_client.post("/api/v1/finance/expenses", headers=headers, json=body)
    assert response.status_code in (200, 201)
    exp_id = response.json()["id"]

    # List
    response = await async_client.get("/api/v1/finance/expenses", headers=headers)
    assert response.status_code == 200
    assert response.json()["count"] >= 1

    # Toggle
    response = await async_client.put(f"/api/v1/finance/expenses/{exp_id}/status", headers=headers)
    assert response.status_code == 200
    assert response.json()["status"] in ("PENDING", "PAID")

    # Summary
    response = await async_client.get("/api/v1/finance/summary", headers=headers)
    assert response.status_code == 200

    # Delete
    response = await async_client.delete(f"/api/v1/finance/expenses/{exp_id}", headers=headers)
    assert response.status_code in (200, 202, 204)
