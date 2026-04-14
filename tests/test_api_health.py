# tests/test_api_health.py
import pytest
from httpx import AsyncClient


class TestAPIHealth:
    """Test API health endpoints"""

    @pytest.mark.asyncio
    async def test_root_endpoint(self, async_client):
        """Test root endpoint"""
        response = await async_client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data

    @pytest.mark.asyncio
    async def test_health_check(self, async_client):
        """Test health check endpoint"""
        response = await async_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"

    @pytest.mark.asyncio
    async def test_api_v1_root(self, async_client):
        """Test API v1 root endpoint"""
        response = await async_client.get("/api/v1")
        assert response.status_code in [200, 404]


class TestAPIEndpoints:
    """Test API endpoints existence"""

    @pytest.mark.asyncio
    async def test_auth_endpoint_exists(self, async_client):
        """Test auth endpoint exists"""
        response = await async_client.post("/api/v1/auth/login")
        assert response.status_code in [200, 401, 422]

    @pytest.mark.asyncio
    async def test_admin_endpoint_exists(self, async_client):
        """Test admin endpoint exists"""
        response = await async_client.get("/api/v1/admin/health")
        assert response.status_code in [200, 401]

    @pytest.mark.asyncio
    async def test_bots_endpoint_exists(self, async_client):
        """Test bots endpoint exists"""
        response = await async_client.get("/api/v1/bots/available")
        assert response.status_code in [200, 401]


class TestAPIEndpoints:
    """Test important API endpoints exist"""
    
    @pytest.mark.asyncio
    async def test_auth_endpoint_exists(self, async_client: AsyncClient):
        """Test auth endpoints are accessible (even if they return 401/422)"""
        response = await async_client.get("/api/v1/auth/me")
        # Should be 401 (unauthorized) not 404 (not found)
        assert response.status_code != 404
    
    @pytest.mark.asyncio
    async def test_admin_endpoint_exists(self, async_client: AsyncClient):
        """Test admin endpoints are accessible"""
        response = await async_client.get("/api/v1/admin/")
        # Should be 401/403 (unauthorized) not 404 (not found)
        assert response.status_code != 404
    
    @pytest.mark.asyncio
    async def test_bots_endpoint_exists(self, async_client: AsyncClient):
        """Test bots endpoints are accessible"""
        response = await async_client.get("/api/v1/bots/available")
        # Should be 401 (unauthorized) not 404 (not found)
        assert response.status_code != 404
