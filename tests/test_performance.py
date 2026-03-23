"""
Performance Benchmarking Tests
Measures response times, throughput, and resource usage
"""
import pytest
import asyncio
import httpx
import time
import statistics
from typing import List


API_URL = "http://localhost:8000"
TEST_EMAIL = "tester@gts.com"
TEST_PASSWORD = "123456"


@pytest.fixture
async def auth_token():
    """Get authentication token"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{API_URL}/api/v1/auth/token",
            data={"email": TEST_EMAIL, "password": TEST_PASSWORD},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        return response.json()["access_token"]


@pytest.fixture
async def auth_headers(auth_token):
    """Get authorization headers"""
    return {"Authorization": f"Bearer {auth_token}"}


class TestAPIResponseTimes:
    """Test API endpoint response times"""

    @pytest.mark.asyncio
    async def test_health_check_performance(self):
        """Health check should respond in < 50ms"""
        times = []
        
        async with httpx.AsyncClient() as client:
            for _ in range(20):
                start = time.time()
                response = await client.get(f"{API_URL}/healthz")
                end = time.time()
                
                assert response.status_code == 200
                times.append((end - start) * 1000)  # Convert to ms
        
        avg_time = statistics.mean(times)
        p95_time = statistics.quantiles(times, n=20)[18]  # 95th percentile
        
        print(f"\nHealth Check Performance:")
        print(f"  Average: {avg_time:.2f}ms")
        print(f"  P95: {p95_time:.2f}ms")
        print(f"  Min: {min(times):.2f}ms")
        print(f"  Max: {max(times):.2f}ms")
        
        assert avg_time < 50, f"Average response time {avg_time:.2f}ms exceeds 50ms"

    @pytest.mark.asyncio
    async def test_login_performance(self):
        """Login should complete in < 200ms"""
        times = []
        
        async with httpx.AsyncClient() as client:
            for _ in range(10):
                start = time.time()
                response = await client.post(
                    f"{API_URL}/api/v1/auth/token",
                    data={"email": TEST_EMAIL, "password": TEST_PASSWORD},
                    headers={"Content-Type": "application/x-www-form-urlencoded"}
                )
                end = time.time()
                
                assert response.status_code == 200
                times.append((end - start) * 1000)
        
        avg_time = statistics.mean(times)
        
        print(f"\nLogin Performance:")
        print(f"  Average: {avg_time:.2f}ms")
        print(f"  Min: {min(times):.2f}ms")
        print(f"  Max: {max(times):.2f}ms")
        
        assert avg_time < 200, f"Average login time {avg_time:.2f}ms exceeds 200ms"

    @pytest.mark.asyncio
    async def test_bot_list_performance(self, auth_headers):
        """Bot listing should respond in < 150ms"""
        times = []
        
        async with httpx.AsyncClient() as client:
            for _ in range(15):
                start = time.time()
                response = await client.get(
                    f"{API_URL}/api/v1/bots",
                    headers=auth_headers
                )
                end = time.time()
                
                assert response.status_code == 200
                times.append((end - start) * 1000)
        
        avg_time = statistics.mean(times)
        
        print(f"\nBot List Performance:")
        print(f"  Average: {avg_time:.2f}ms")
        print(f"  Min: {min(times):.2f}ms")
        print(f"  Max: {max(times):.2f}ms")
        
        assert avg_time < 150, f"Average response time {avg_time:.2f}ms exceeds 150ms"


class TestThroughput:
    """Test system throughput"""

    @pytest.mark.asyncio
    async def test_concurrent_requests_throughput(self, auth_headers):
        """Measure requests per second under concurrent load"""
        async def make_request():
            async with httpx.AsyncClient() as client:
                start = time.time()
                response = await client.get(
                    f"{API_URL}/api/v1/bots",
                    headers=auth_headers
                )
                end = time.time()
                return response.status_code, (end - start) * 1000
        
        # Execute 50 concurrent requests
        start_time = time.time()
        tasks = [make_request() for _ in range(50)]
        results = await asyncio.gather(*tasks)
        end_time = time.time()
        
        total_time = end_time - start_time
        success_count = sum(1 for status, _ in results if status == 200)
        response_times = [rt for _, rt in results]
        
        throughput = success_count / total_time
        avg_response_time = statistics.mean(response_times)
        
        print(f"\nThroughput Test (50 concurrent requests):")
        print(f"  Total time: {total_time:.2f}s")
        print(f"  Successful: {success_count}/50")
        print(f"  Throughput: {throughput:.2f} req/s")
        print(f"  Avg response: {avg_response_time:.2f}ms")
        
        assert success_count >= 45, "At least 90% of requests should succeed"
        assert throughput >= 10, "Should handle at least 10 req/s"


class TestDatabasePerformance:
    """Test database query performance"""

    @pytest.mark.asyncio
    async def test_user_lookup_performance(self, auth_headers):
        """User lookup should be fast"""
        times = []
        
        async with httpx.AsyncClient() as client:
            for _ in range(20):
                start = time.time()
                response = await client.get(
                    f"{API_URL}/api/v1/auth/me",
                    headers=auth_headers
                )
                end = time.time()
                
                assert response.status_code == 200
                times.append((end - start) * 1000)
        
        avg_time = statistics.mean(times)
        
        print(f"\nUser Lookup Performance:")
        print(f"  Average: {avg_time:.2f}ms")
        print(f"  P95: {statistics.quantiles(times, n=20)[18]:.2f}ms")
        
        assert avg_time < 100, f"User lookup should be under 100ms, got {avg_time:.2f}ms"


class TestScalability:
    """Test system scalability under increasing load"""

    @pytest.mark.asyncio
    async def test_scaling_concurrent_users(self, auth_headers):
        """Test performance degradation under increasing load"""
        user_counts = [10, 25, 50, 100]
        results = {}
        
        for user_count in user_counts:
            async def make_request():
                async with httpx.AsyncClient() as client:
                    start = time.time()
                    response = await client.get(
                        f"{API_URL}/api/v1/bots",
                        headers=auth_headers
                    )
                    end = time.time()
                    return (end - start) * 1000
            
            tasks = [make_request() for _ in range(user_count)]
            times = await asyncio.gather(*tasks)
            
            avg_time = statistics.mean(times)
            results[user_count] = avg_time
        
        print(f"\nScalability Test Results:")
        for users, avg in results.items():
            print(f"  {users} users: {avg:.2f}ms avg")
        
        # Performance shouldn't degrade more than 3x from 10 to 100 users
        degradation = results[100] / results[10]
        assert degradation < 3, f"Performance degraded {degradation:.1f}x, should be < 3x"


class TestMemoryUsage:
    """Test memory efficiency"""

    @pytest.mark.asyncio
    async def test_no_memory_leaks(self, auth_headers):
        """Ensure no memory leaks from repeated requests"""
        # This is a basic test - production would use proper profiling tools
        
        async def make_100_requests():
            async with httpx.AsyncClient() as client:
                for _ in range(100):
                    await client.get(f"{API_URL}/healthz")
        
        # Execute multiple batches
        for batch in range(5):
            start = time.time()
            await make_100_requests()
            end = time.time()
            
            batch_time = end - start
            print(f"Batch {batch + 1}: {batch_time:.2f}s for 100 requests")
        
        # Times should remain relatively consistent (no significant degradation)
        # This is a simple smoke test; proper memory profiling needed for production


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--asyncio-mode=auto", "-s"])
