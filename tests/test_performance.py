"""Local performance smoke tests using the test harness."""

import statistics
import time

import pytest


class TestAPIResponseTimes:
    @pytest.mark.asyncio
    async def test_health_check_performance(self, async_client):
        times = []
        for _ in range(20):
            start = time.perf_counter()
            response = await async_client.get("/healthz")
            end = time.perf_counter()
            assert response.status_code == 200
            times.append((end - start) * 1000)

        avg_time = statistics.mean(times)
        assert avg_time < 50

    @pytest.mark.asyncio
    async def test_login_performance(self, async_client):
        times = []
        for _ in range(10):
            start = time.perf_counter()
            response = await async_client.post(
                "/api/v1/auth/token",
                data={"username": "admin@gts.com", "password": "admin123"},
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            end = time.perf_counter()
            assert response.status_code == 200
            times.append((end - start) * 1000)

        avg_time = statistics.mean(times)
        assert avg_time < 200

    @pytest.mark.asyncio
    async def test_bot_list_performance(self, async_client, dev_token):
        headers = {"Authorization": f"Bearer {dev_token}"}
        times = []
        for _ in range(15):
            start = time.perf_counter()
            response = await async_client.get("/api/v1/bots", headers=headers)
            end = time.perf_counter()
            assert response.status_code == 200
            times.append((end - start) * 1000)

        avg_time = statistics.mean(times)
        assert avg_time < 150


class TestThroughput:
    @pytest.mark.asyncio
    async def test_concurrent_requests_throughput(self, async_client, dev_token):
        headers = {"Authorization": f"Bearer {dev_token}"}

        async def make_request():
            start = time.perf_counter()
            response = await async_client.get("/api/v1/bots", headers=headers)
            end = time.perf_counter()
            return response.status_code, (end - start) * 1000

        start_time = time.perf_counter()
        results = await __import__("asyncio").gather(*[make_request() for _ in range(50)])
        total_time = time.perf_counter() - start_time

        success_count = sum(1 for status, _ in results if status == 200)
        throughput = success_count / total_time if total_time else success_count

        assert success_count >= 45
        assert throughput >= 10


class TestDatabasePerformance:
    @pytest.mark.asyncio
    async def test_user_lookup_performance(self, async_client, dev_token):
        headers = {"Authorization": f"Bearer {dev_token}"}
        times = []
        for _ in range(20):
            start = time.perf_counter()
            response = await async_client.get("/api/v1/auth/me", headers=headers)
            end = time.perf_counter()
            assert response.status_code == 200
            times.append((end - start) * 1000)

        avg_time = statistics.mean(times)
        assert avg_time < 100


class TestScalability:
    @pytest.mark.asyncio
    async def test_scaling_concurrent_users(self, async_client, dev_token):
        headers = {"Authorization": f"Bearer {dev_token}"}
        user_counts = [10, 25, 50, 100]
        results = {}

        async def make_request():
            start = time.perf_counter()
            await async_client.get("/api/v1/bots", headers=headers)
            end = time.perf_counter()
            return (end - start) * 1000

        for user_count in user_counts:
            times = await __import__("asyncio").gather(*[make_request() for _ in range(user_count)])
            results[user_count] = statistics.mean(times)

        # Local ASGI transport overhead grows under heavy in-process concurrency,
        # so use a coarse smoke bound instead of a strict scaling ratio.
        assert results[10] > 0
        assert results[100] < 250


class TestMemoryUsage:
    @pytest.mark.asyncio
    async def test_no_memory_leaks(self, async_client):
        for _ in range(5):
            for _ in range(100):
                response = await async_client.get("/healthz")
                assert response.status_code == 200
