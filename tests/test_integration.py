"""
Integration Tests for GTS Logistics System
Tests end-to-end workflows and component interactions
"""
import pytest
import asyncio
import httpx
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os
from datetime import datetime


# Test configuration
API_URL = os.getenv("API_URL", "http://localhost:8000")
TEST_EMAIL = "tester@gts.com"
TEST_PASSWORD = "123456"


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def auth_token():
    """Get authentication token for tests"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{API_URL}/api/v1/auth/token",
            data={"email": TEST_EMAIL, "password": TEST_PASSWORD},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert response.status_code == 200, "Login should succeed"
        data = response.json()
        return data["access_token"]


@pytest.fixture
async def auth_headers(auth_token):
    """Get authorization headers"""
    return {"Authorization": f"Bearer {auth_token}"}


class TestAuthenticationFlow:
    """Test complete authentication workflow"""

    @pytest.mark.asyncio
    async def test_login_success(self):
        """Test successful login"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{API_URL}/api/v1/auth/token",
                data={"email": TEST_EMAIL, "password": TEST_PASSWORD},
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "access_token" in data
            assert data["token_type"] == "bearer"
            assert "user" in data
            assert data["user"]["email"] == TEST_EMAIL

    @pytest.mark.asyncio
    async def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{API_URL}/api/v1/auth/token",
                data={"email": TEST_EMAIL, "password": "wrongpassword"},
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            assert response.status_code in [401, 403]

    @pytest.mark.asyncio
    async def test_get_current_user(self, auth_headers):
        """Test getting current user info"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{API_URL}/api/v1/auth/me",
                headers=auth_headers
            )
            
            assert response.status_code == 200
            user = response.json()
            assert user["email"] == TEST_EMAIL
            assert "role" in user
            assert "id" in user


class TestBotOperations:
    """Test bot system operations"""

    @pytest.mark.asyncio
    async def test_list_bots(self, auth_headers):
        """Test listing all bots"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{API_URL}/api/v1/bots",
                headers=auth_headers
            )
            
            assert response.status_code == 200
            bots = response.json()
            assert isinstance(bots, list)
            assert len(bots) > 0, "Should have at least one bot"
            
            # Verify bot structure
            bot = bots[0]
            assert "name" in bot
            assert "description" in bot
            assert "status" in bot

    @pytest.mark.asyncio
    async def test_get_bot_stats(self, auth_headers):
        """Test getting bot statistics"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{API_URL}/api/v1/bots/stats",
                headers=auth_headers
            )
            
            assert response.status_code == 200
            stats = response.json()
            assert "total_bots" in stats or "bots" in stats

    @pytest.mark.asyncio
    async def test_get_bot_history(self, auth_headers):
        """Test getting bot execution history"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{API_URL}/api/v1/bots/history",
                params={"limit": 5},
                headers=auth_headers
            )
            
            assert response.status_code == 200
            history = response.json()
            assert isinstance(history, list)

    @pytest.mark.asyncio
    async def test_execute_bot_command(self, auth_headers):
        """Test executing a bot command"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{API_URL}/api/v1/commands/human",
                json={"command": "What's my role?"},
                headers=auth_headers
            )
            
            # Should succeed or be rate limited
            assert response.status_code in [200, 201, 429]
            
            if response.status_code in [200, 201]:
                result = response.json()
                assert "result" in result or "response" in result or "message" in result


class TestHealthAndMonitoring:
    """Test health check and monitoring endpoints"""

    @pytest.mark.asyncio
    async def test_health_check(self):
        """Test health check endpoint"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{API_URL}/healthz")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "ok"

    @pytest.mark.asyncio
    async def test_api_docs_accessible(self):
        """Test API documentation is accessible"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{API_URL}/docs")
            
            assert response.status_code == 200
            assert "swagger" in response.text.lower() or "openapi" in response.text.lower()


class TestRateLimiting:
    """Test rate limiting functionality"""

    @pytest.mark.asyncio
    async def test_command_rate_limiting(self, auth_headers):
        """Test that commands are rate limited"""
        async with httpx.AsyncClient() as client:
            # Send multiple commands rapidly
            responses = []
            for i in range(10):
                response = await client.post(
                    f"{API_URL}/api/v1/commands/human",
                    json={"command": f"Test command {i}"},
                    headers=auth_headers
                )
                responses.append(response.status_code)
            
            # At least one should be rate limited
            assert 429 in responses, "Should hit rate limit"


class TestDatabaseOperations:
    """Test database integration"""

    @pytest.mark.asyncio
    async def test_user_persistence(self, auth_headers):
        """Test that user data persists correctly"""
        async with httpx.AsyncClient() as client:
            # Get user twice
            response1 = await client.get(f"{API_URL}/auth/me", headers=auth_headers)
            await asyncio.sleep(1)
            response2 = await client.get(f"{API_URL}/auth/me", headers=auth_headers)
            
            assert response1.status_code == 200
            assert response2.status_code == 200
            
            user1 = response1.json()
            user2 = response2.json()
            
            # Should be identical
            assert user1["id"] == user2["id"]
            assert user1["email"] == user2["email"]


class TestErrorHandling:
    """Test error handling and edge cases"""

    @pytest.mark.asyncio
    async def test_unauthorized_access(self):
        """Test accessing protected endpoint without auth"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{API_URL}/api/v1/bots")
            
            assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_invalid_endpoint(self, auth_headers):
        """Test accessing non-existent endpoint"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{API_URL}/api/v1/nonexistent",
                headers=auth_headers
            )
            
            assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_malformed_request(self, auth_headers):
        """Test malformed JSON request"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{API_URL}/api/v1/commands/human",
                content="not valid json",
                headers={**auth_headers, "Content-Type": "application/json"}
            )
            
            assert response.status_code in [400, 422]


class TestConcurrentOperations:
    """Test system behavior under concurrent load"""

    @pytest.mark.asyncio
    async def test_concurrent_logins(self):
        """Test multiple concurrent logins"""
        async def login():
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{API_URL}/api/v1/auth/token",
                    data={"email": TEST_EMAIL, "password": TEST_PASSWORD},
                    headers={"Content-Type": "application/x-www-form-urlencoded"}
                )
                return response.status_code
        
        # Execute 10 concurrent logins
        tasks = [login() for _ in range(10)]
        results = await asyncio.gather(*tasks)
        
        # All should succeed
        assert all(code == 200 for code in results)

    @pytest.mark.asyncio
    async def test_concurrent_api_calls(self, auth_headers):
        """Test concurrent API calls"""
        async def get_bots():
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{API_URL}/api/v1/bots",
                    headers=auth_headers
                )
                return response.status_code
        
        # Execute 20 concurrent requests
        tasks = [get_bots() for _ in range(20)]
        results = await asyncio.gather(*tasks)
        
        # Most should succeed (some might fail if rate limited)
        success_count = sum(1 for code in results if code == 200)
        assert success_count >= 15, "Most concurrent requests should succeed"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])
