#!/usr/bin/env python3
"""
Simple test for Database Orchestrator Bot
"""

import asyncio
import aiohttp
import json

async def test_bot():
    async with aiohttp.ClientSession() as session:
        try:
            # Test metrics
            async with session.get('http://127.0.0.1:8081/api/v1/metrics') as response:
                if response.status == 200:
                    metrics = await response.json()
                    print('✅ Metrics retrieved successfully')
                    print(f'Requests served: {metrics.get("requests_served", 0)}')
                    print(f'Batch operations: {metrics.get("batch_operations", 0)}')
                    print(f'Average response time: {metrics.get("avg_response_time", 0):.3f}s')
                    print(f'Errors: {metrics.get("errors", 0)}')
                else:
                    print(f'❌ Failed to get metrics: {response.status}')

            # Test read operation
            print('\n🔍 Testing read operation...')
            read_data = {
                "operation_type": "read",
                "table": "users",
                "filters": {"is_active": True},
                "cache_ttl": 300
            }

            async with session.post(
                'http://127.0.0.1:8081/api/v1/operation',
                json=read_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    if result.get("success"):
                        print('✅ Read operation successful')
                        print(f'Retrieved {result.get("data", {}).get("rows_count", 0)} rows')
                    else:
                        print(f'❌ Read operation failed: {result.get("error", "Unknown")}')
                else:
                    print(f'❌ HTTP error: {response.status}')

        except Exception as e:
            print(f'❌ Connection error: {e}')

if __name__ == "__main__":
    asyncio.run(test_bot())