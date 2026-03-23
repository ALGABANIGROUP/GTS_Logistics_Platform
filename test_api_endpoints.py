#!/usr/bin/env python3
import httpx
import asyncio

async def test_endpoints():
    async with httpx.AsyncClient() as client:
        endpoints = [
            'http://localhost:8000/healthz',
            'http://localhost:8000/api/v1/admin/api-connections/',
            'http://localhost:8000/api/v1/admin/api-connections/categories/list',
            'http://localhost:8000/api/v1/admin/api-connections/connection-types/list',
            'http://localhost:8000/api/v1/admin/api-connections/stats',
        ]
        
        for endpoint in endpoints:
            try:
                response = await client.get(endpoint, timeout=3.0)
                print(f'✅ {endpoint.split("/")[-1] or "healthz"}: {response.status_code}')
            except Exception as e:
                print(f'❌ {endpoint.split("/")[-1] or "healthz"}: {type(e).__name__}')

asyncio.run(test_endpoints())
