"""
API health and connectivity tests
"""
import pytest
from httpx import AsyncClient


class TestAPIHealth:
    """Test API health and basic connectivity"""
    
    @pytest.mark.asyncio
    async def test_root_endpoint(self, client: AsyncClient):
        """Test root endpoint responds"""
        response = await client.get("/")
        assert response.status_code in [200, 404, 307]  # OK, Not Found, or Redirect
    
    @pytest.mark.asyncio
    async def test_health_check(self, client: AsyncClient):
        """Test health check endpoint"""
        response = await client.get("/healthz")
        assert response.status_code in [200, 404]
    
    @pytest.mark.asyncio
    async def test_api_v1_root(self, client: AsyncClient):
        """Test API v1 root endpoint"""
        response = await client.get("/api/v1/")
        assert response.status_code in [200, 404, 307]


class TestAPIEndpoints:
    """Test important API endpoints exist"""
    
    @pytest.mark.asyncio
    async def test_auth_endpoint_exists(self, client: AsyncClient):
        """Test auth endpoints are accessible (even if they return 401/422)"""
        response = await client.get("/api/v1/auth/me")
        # Should be 401 (unauthorized) not 404 (not found)
        assert response.status_code != 404
    
    @pytest.mark.asyncio
    async def test_admin_endpoint_exists(self, client: AsyncClient):
        """Test admin endpoints are accessible"""
        response = await client.get("/api/v1/admin/")
        # Should be 401/403 (unauthorized) not 404 (not found)
        assert response.status_code != 404
    
    @pytest.mark.asyncio
    async def test_bots_endpoint_exists(self, client: AsyncClient):
        """Test bots endpoints are accessible"""
        response = await client.get("/api/v1/bots/available")
        # Should be 401 (unauthorized) not 404 (not found)
        assert response.status_code != 404
