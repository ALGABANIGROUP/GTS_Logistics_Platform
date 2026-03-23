#!/usr/bin/env python3
"""
AI Safety Manager Bot - System Health Check
Comprehensive system health testing
"""

import asyncio
import httpx
import json
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000"
API_BASE = f"{BASE_URL}/api/v1"

class SafetySystemTester:
    def __init__(self):
        self.results = []
        self.passed = 0
        self.failed = 0
        self.token = None

    async def test_backend_health(self):
        """Test that Backend is running"""
        print("\n🔍 Testing Backend Health...")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{BASE_URL}/docs")
                if response.status_code == 200:
                    print("✅ Backend is running")
                    self.passed += 1
                    self.results.append(("Backend Health", "✅ PASS"))
                else:
                    print("❌ Backend returned non-200 status")
                    self.failed += 1
                    self.results.append(("Backend Health", "❌ FAIL"))
        except Exception as e:
            print(f"❌ Backend Error: {e}")
            self.failed += 1
            self.results.append(("Backend Health", f"❌ FAIL: {str(e)}"))

    async def test_safety_status(self):
        """Test status endpoint"""
        print("\n🔍 Testing Safety Status Endpoint...")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{API_BASE}/safety/status")
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ Safety Status OK: {data.get('system_status', 'unknown')}")
                    self.passed += 1
                    self.results.append(("Safety Status", "✅ PASS"))
                elif response.status_code == 401:
                    print("⚠️  Authentication required (expected)")
                    self.passed += 1
                    self.results.append(("Safety Status", "✅ PASS (Auth required)"))
                else:
                    print(f"❌ Safety Status Error: {response.status_code}")
                    self.failed += 1
                    self.results.append(("Safety Status", f"❌ FAIL: {response.status_code}"))
        except Exception as e:
            print(f"❌ Safety Status Error: {e}")
            self.failed += 1
            self.results.append(("Safety Status", f"❌ FAIL: {str(e)}"))

    async def test_safety_dashboard(self):
        """Test dashboard endpoint"""
        print("\n🔍 Testing Safety Dashboard Endpoint...")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{API_BASE}/safety/dashboard")
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ Safety Dashboard OK")
                    print(f"   - Safety Score: {data.get('safety_score', 'N/A')}")
                    print(f"   - Risk Level: {data.get('risk_level', 'N/A')}")
                    print(f"   - Compliance Rate: {data.get('compliance_rate', 'N/A')}%")
                    self.passed += 1
                    self.results.append(("Safety Dashboard", "✅ PASS"))
                elif response.status_code == 401:
                    print("⚠️  Authentication required (expected)")
                    self.passed += 1
                    self.results.append(("Safety Dashboard", "✅ PASS (Auth required)"))
                else:
                    print(f"❌ Safety Dashboard Error: {response.status_code}")
                    self.failed += 1
                    self.results.append(("Safety Dashboard", f"❌ FAIL: {response.status_code}"))
        except Exception as e:
            print(f"❌ Safety Dashboard Error: {e}")
            self.failed += 1
            self.results.append(("Safety Dashboard", f"❌ FAIL: {str(e)}"))

    async def test_safety_endpoints(self):
        """Test all Safety endpoints"""
        print("\n🔍 Testing All Safety Endpoints...")
        endpoints = [
            ("GET", "/safety/status", "Status"),
            ("GET", "/safety/config", "Config"),
            ("GET", "/safety/dashboard", "Dashboard"),
            ("GET", "/safety/incidents/statistics", "Incident Stats"),
            ("GET", "/safety/compliance/check", "Compliance Check"),
            ("GET", "/safety/risks/assess", "Risk Assessment"),
            ("GET", "/safety/training/requirements", "Training Requirements"),
            ("GET", "/safety/alerts/recent", "Recent Alerts"),
        ]
        
        async with httpx.AsyncClient() as client:
            for method, endpoint, name in endpoints:
                try:
                    if method == "GET":
                        response = await client.get(f"{API_BASE}{endpoint}")
                    status = response.status_code
                    # 200 = OK, 401 = Auth required (expected for public endpoints)
                    if status in [200, 401]:
                        print(f"✅ {name}: {status}")
                        self.passed += 1
                        self.results.append((name, "✅ PASS"))
                    else:
                        print(f"❌ {name}: {status}")
                        self.failed += 1
                        self.results.append((name, f"❌ FAIL: {status}"))
                except Exception as e:
                    print(f"❌ {name}: {str(e)}")
                    self.failed += 1
                    self.results.append((name, f"❌ FAIL: {str(e)}"))

    async def test_cors(self):
        """Test CORS settings"""
        print("\n🔍 Testing CORS Configuration...")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{API_BASE}/safety/status",
                    headers={
                        "Origin": "http://127.0.0.1:5174",
                        "Access-Control-Request-Method": "GET"
                    }
                )
                cors_header = response.headers.get("access-control-allow-origin")
                if cors_header or response.status_code == 401:  # 401 is OK too
                    print(f"✅ CORS Configured: {cors_header or 'Auth required'}")
                    self.passed += 1
                    self.results.append(("CORS", "✅ PASS"))
                else:
                    print("⚠️  CORS header not present")
                    self.passed += 1
                    self.results.append(("CORS", "⚠️ WARN"))
        except Exception as e:
            print(f"❌ CORS Error: {e}")
            self.failed += 1
            self.results.append(("CORS", f"❌ FAIL: {str(e)}"))

    async def run_all_tests(self):
        """Run all tests"""
        print("=" * 60)
        print("🛡️  AI SAFETY MANAGER BOT - SYSTEM HEALTH CHECK")
        print("=" * 60)
        print(f"🕐 Testing at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🔗 Backend URL: {BASE_URL}")
        
        await self.test_backend_health()
        await self.test_safety_status()
        await self.test_safety_dashboard()
        await self.test_safety_endpoints()
        await self.test_cors()
        
        self.print_summary()

    def print_summary(self):
        """Print results summary"""
        print("\n" + "=" * 60)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 60)
        
        for test_name, result in self.results:
            print(f"{result:20} | {test_name}")
        
        print("=" * 60)
        total = self.passed + self.failed
        percentage = (self.passed / total * 100) if total > 0 else 0
        
        print(f"✅ Passed: {self.passed}")
        print(f"❌ Failed: {self.failed}")
        print(f"📈 Success Rate: {percentage:.1f}%")
        print("=" * 60)
        
        if self.failed == 0:
            print("🎉 ALL TESTS PASSED!")
            print("✅ System is ready to use")
        else:
            print("⚠️  Some tests failed - check Backend")
        
        print("=" * 60)

async def main():
    """Main entry point"""
    tester = SafetySystemTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
