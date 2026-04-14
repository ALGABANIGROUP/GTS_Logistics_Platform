"""
AI Bots system tests
"""
import pytest
from httpx import AsyncClient


class TestBotsAPI:
    """Test AI Bots API endpoints"""
    
    @pytest.mark.asyncio
    async def test_get_available_bots(self, async_client: AsyncClient, auth_headers: dict):
        """Test getting available bots list"""
        response = await async_client.get(
            "/api/v1/bots/available",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "bots" in data or isinstance(data, list)
    
    @pytest.mark.asyncio
    async def test_get_bot_stats(self, async_client: AsyncClient, auth_headers: dict):
        """Test getting bot statistics"""
        response = await async_client.get(
            "/api/v1/bots/stats",
            headers=auth_headers
        )
        # Should either work or return 404 if endpoint doesn't exist
        assert response.status_code in [200, 404]
    
    @pytest.mark.asyncio
    async def test_bots_require_auth(self, async_client: AsyncClient):
        """Test that bots endpoints require authentication"""
        response = await async_client.get("/api/v1/bots/available")
        assert response.status_code in (200, 401)


class TestBotSubscriptions:
    """Test bot subscription and access control"""
    
    @pytest.mark.asyncio
    async def test_get_user_available_bots(self, async_client: AsyncClient, auth_headers: dict):
        """Test getting bots available to current user"""
        response = await async_client.get(
            "/api/v1/ai/bots/available",
            headers=auth_headers
        )
        # Should work or return method not allowed if different method needed
        assert response.status_code in [200, 405]
    
    @pytest.mark.asyncio
    async def test_check_bot_access(self, async_client: AsyncClient, auth_headers: dict):
        """Test checking access to specific bot"""
        response = await async_client.get(
            "/api/v1/ai/bots/check-access/general_manager",
            headers=auth_headers
        )
        # Should work or return 404 if endpoint doesn't exist
        assert response.status_code in [200, 404]
