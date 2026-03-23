#!/usr/bin/env python3
"""
Test script for production-grade health checks
"""
import asyncio
import aiohttp
import json
import sys
from typing import Dict, Any

async def test_health_endpoint(url: str, name: str) -> Dict[str, Any]:
    """Test a health endpoint and return structured results."""
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=15)) as session:
            async with session.get(url) as response:
                result = await response.json()
                return {
                    "endpoint": name,
                    "url": url,
                    "status_code": response.status,
                    "ok": result.get("ok", False),
                    "response": result
                }
    except Exception as e:
        return {
            "endpoint": name,
            "url": url,
            "status_code": None,
            "ok": False,
            "error": str(e)
        }

async def main():
    """Test all health endpoints."""
    base_url = "http://localhost:8000/health"

    endpoints = [
        ("ping", f"{base_url}/ping"),
        ("db", f"{base_url}/db"),
        ("redis", f"{base_url}/redis"),
        ("external", f"{base_url}/external"),
        ("full", f"{base_url}/full"),
    ]

    print("🩺 Testing Production-Grade Health Checks")
    print("=" * 50)

    results = []
    for name, url in endpoints:
        print(f"Testing {name}... ", end="", flush=True)
        result = await test_health_endpoint(url, name)
        results.append(result)

        if result["ok"]:
            print("✅ PASS")
        else:
            print("❌ FAIL")

        # Show details for failed endpoints
        if not result["ok"]:
            if result.get("status_code"):
                print(f"   Status: {result['status_code']}")
            if result.get("error"):
                print(f"   Error: {result['error']}")
            elif result.get("response", {}).get("error"):
                print(f"   Error: {result['response']['error']}")

    print("\n📊 Summary:")
    print("-" * 30)
    passed = sum(1 for r in results if r["ok"])
    total = len(results)
    print(f"Passed: {passed}/{total}")

    # Show detailed results for database and external checks
    for result in results:
        if result["endpoint"] in ["db", "external"] and result["ok"]:
            print(f"\n🔍 {result['endpoint'].upper()} Details:")
            if result["endpoint"] == "db":
                resp = result["response"]
                print(f"   Query Time: {resp.get('query_time', 'N/A')}")
                print(f"   Current Time: {resp.get('current_time', 'N/A')}")
                print(f"   DB Version: {resp.get('db_version', 'N/A')[:50]}")
            elif result["endpoint"] == "external":
                services = result["response"].get("services", {})
                for service_name, service_info in services.items():
                    status = "✅" if service_info.get("ok") else "❌"
                    print(f"   {service_name}: {status}")

    return passed == total

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\nTest interrupted")
        sys.exit(1)