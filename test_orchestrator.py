#!/usr/bin/env python3
"""
Test Database Orchestrator Bot
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime

class OrchestratorTester:
    def __init__(self, base_url="http://localhost:8080"):
        self.base_url = base_url
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def test_operation(self, operation_data):
        """Test specific operation"""
        try:
            async with self.session.post(
                f"{self.base_url}/api/v1/operation",
                json=operation_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                result = await response.json()
                return {
                    "status": response.status,
                    "data": result,
                    "success": result.get("success", False)
                }
        except Exception as e:
            return {
                "status": 0,
                "error": str(e),
                "success": False
            }

    async def get_metrics(self):
        """Get system metrics"""
        try:
            async with self.session.get(f"{self.base_url}/api/v1/metrics") as response:
                return await response.json()
        except Exception as e:
            return {"error": str(e)}

    async def flush_batches(self):
        """Flush batches"""
        try:
            async with self.session.post(f"{self.base_url}/api/v1/flush") as response:
                return await response.json()
        except Exception as e:
            return {"error": str(e)}

    async def clear_cache(self, table=None):
        """Clear cache"""
        try:
            url = f"{self.base_url}/api/v1/clear-cache"
            if table:
                url += f"?table={table}"
            async with self.session.post(url) as response:
                return await response.json()
        except Exception as e:
            return {"error": str(e)}

async def run_tests():
    """Run all tests"""

    print("🧪 Starting Database Orchestrator Bot test")
    print("=" * 50)

    async with OrchestratorTester() as tester:

        # Wait for bot initialization
        print("⏳ Waiting for bot initialization...")
        await asyncio.sleep(5)

        # Test 1: Read data
        print("\n1️⃣ Testing data reading")
        read_op = {
            "operation_type": "read",
            "table": "users",
            "filters": {"is_active": True},
            "cache_ttl": 300
        }

        result = await tester.test_operation(read_op)
        if result["success"]:
            print("✅ Read test passed")
            print(f"   📊 Retrieved {result['data'].get('rows_count', 0)} rows")
        else:
            print("❌ Read test failed")
            print(f"   Error: {result.get('error', 'Unknown')}")

        # Test 2: Write data (batch)
        print("\n2️⃣ Testing data writing (batch)")
        write_op = {
            "operation_type": "write",
            "table": "test_orders",
            "data": {
                "user_id": 1,
                "amount": 99.99,
                "status": "pending",
                "created_at": datetime.now().isoformat()
            },
            "priority": 3  # batch
        }

        result = await tester.test_operation(write_op)
        if result["success"]:
            print("✅ Batch write test passed")
            print(f"   📝 Operation added to batch: {result['data'].get('operation_id', 'N/A')}")
        else:
            print("❌ Batch write test failed")
            print(f"   Error: {result.get('error', 'Unknown')}")

        # Test 3: Write data (immediate)
        print("\n3️⃣ Testing data writing (immediate)")
        urgent_write_op = {
            "operation_type": "write",
            "table": "test_payments",
            "data": {
                "order_id": 1,
                "amount": 99.99,
                "status": "completed",
                "processed_at": datetime.now().isoformat()
            },
            "priority": 9  # immediate
        }

        result = await tester.test_operation(urgent_write_op)
        if result["success"]:
            print("✅ Immediate write test passed")
            print(f"   🆔 Inserted ID: {result['data'].get('inserted_id', 'N/A')}")
        else:
            print("❌ Immediate write test failed")
            print(f"   Error: {result.get('error', 'Unknown')}")

        # Test 4: Display metrics
        print("\n4️⃣ Testing metrics display")
        metrics = await tester.get_metrics()
        if "error" not in metrics:
            print("✅ Metrics display successful")
            print(f"   📊 Requests served: {metrics.get('requests_served', 0)}")
            print(".3f"            print(f"   🔄 Batch operations: {metrics.get('batch_operations', 0)}")
            print(f"   ❌ Errors: {metrics.get('errors', 0)}")
        else:
            print("❌ Metrics display failed")
            print(f"   Error: {metrics['error']}")

        # Test 5: Flush batches
        print("\n5️⃣ Testing batch flush")
        flush_result = await tester.flush_batches()
        if flush_result.get("success"):
            print("✅ Batch flush successful")
        else:
            print("❌ Batch flush failed")
            print(f"   Error: {flush_result.get('error', 'Unknown')}")

        # Test 6: Clear cache
        print("\n6️⃣ Testing cache clear")
        cache_result = await tester.clear_cache()
        if cache_result.get("success"):
            print("✅ Cache clear successful")
        else:
            print("❌ Cache clear failed")
            print(f"   Error: {cache_result.get('error', 'Unknown')}")

        # Test 7: Performance test
        print("\n7️⃣ Performance test (repeated reads)")
        start_time = time.time()

        # Read same data 10 times
        for i in range(10):
            result = await tester.test_operation(read_op)
            if not result["success"]:
                print(f"❌ Failed at iteration {i+1}")
                break
        else:
            end_time = time.time()
            total_time = end_time - start_time
            avg_time = total_time / 10
            print("✅ Performance test passed")
            print(".3f"            print(".3f"
        # Test 8: Read from cache
        print("\n8️⃣ Testing cache read")
        result = await tester.test_operation(read_op)
        if result["success"] and result["data"].get("from_cache"):
            print("✅ Cache read successful")
            print(f"   🗝️ Cache key: {result['data'].get('cache_key', 'N/A')}")
        else:
            print("⚠️ Cache not used (data may not exist)")

    print("\n" + "=" * 50)
    print("🎉 Test completed!")

if __name__ == "__main__":
    asyncio.run(run_tests())