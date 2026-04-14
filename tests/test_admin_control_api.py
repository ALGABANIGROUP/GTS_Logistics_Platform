import pytest


@pytest.mark.asyncio
async def test_admin_health(async_client):
    response = await async_client.get("/api/v1/admin/health")
    assert response.status_code == 200
    assert response.json().get("status") == "healthy"


@pytest.mark.asyncio
async def test_admin_users_endpoint(async_client):
    response = await async_client.get("/api/v1/admin/users")
    assert response.status_code in [200, 401]


@pytest.mark.asyncio
async def test_admin_system_health(async_client):
    response = await async_client.get("/api/v1/admin/system/health")
    assert response.status_code in [200, 401]
