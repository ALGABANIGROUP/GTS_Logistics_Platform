"""Integration tests using the local test harness."""

import pytest


@pytest.mark.asyncio
async def test_health_endpoint(async_client):
    response = await async_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data.get("status") == "healthy"


@pytest.mark.asyncio
async def test_api_v1_health(async_client):
    response = await async_client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json().get("status") == "healthy"


@pytest.mark.asyncio
async def test_auth_endpoint(async_client):
    response = await async_client.post("/api/v1/auth/login")
    assert response.status_code in [401, 422]


@pytest.mark.asyncio
async def test_admin_health(async_client):
    response = await async_client.get("/api/v1/admin/health")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_finance_health(async_client):
    response = await async_client.get("/api/v1/finance/health")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_root_endpoint(async_client):
    response = await async_client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data


@pytest.mark.asyncio
async def test_bots_available(async_client, dev_token):
    headers = {"Authorization": f"Bearer {dev_token}"}
    response = await async_client.get("/api/v1/bots/available", headers=headers)
    assert response.status_code in [200, 401]


@pytest.mark.asyncio
async def test_docs_endpoint(async_client):
    response = await async_client.get("/docs")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_openapi_json(async_client):
    response = await async_client.get("/openapi.json")
    assert response.status_code == 200
    data = response.json()
    assert "info" in data
    assert "paths" in data
