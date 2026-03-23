#!/usr/bin/env python
"""Test signup endpoint and other HTTP endpoints"""

import asyncio
import httpx
import json

async def test_endpoints():
    print("=" * 70)
    print("ENDPOINT TESTING")
    print("=" * 70)
    
    base_url = "http://localhost:8000"
    
    async with httpx.AsyncClient(base_url=base_url, timeout=5.0) as client:
        # Test 1: Health check
        print("\n✅ TEST 1: Health Check")
        try:
            response = await client.get("/health")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.json() if response.status_code == 200 else response.text}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Test 2: Check subdomain availability
        print("\n✅ TEST 2: Subdomain Availability Check")
        try:
            response = await client.get("/api/v1/signup/status/mycompany")
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   Response: {json.dumps(data, indent=2)}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Test 3: Invalid subdomain
        print("\n✅ TEST 3: Invalid Subdomain Check")
        try:
            response = await client.get("/api/v1/signup/status/www")  # Reserved word
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   Available: {data.get('available')} (should be False for reserved words)")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Test 4: Attempt signup (will fail due to email verification but tests the endpoint)
        print("\n✅ TEST 4: Signup Endpoint Test")
        try:
            signup_data = {
                "company_name": "Test Company",
                "subdomain": "testcompany123",
                "owner_email": "test@testcompany.com",
                "owner_name": "Test Owner",
                "owner_password": "password123"
            }
            response = await client.post(
                "/api/v1/signup/register",
                json=signup_data
            )
            print(f"   Status: {response.status_code}")
            if response.status_code in [200, 201]:
                data = response.json()
                print(f"   ✅ Response: {json.dumps(data, indent=2)}")
            else:
                print(f"   Response: {response.text[:200]}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Test 5: Rate limiting on signup
        print("\n✅ TEST 5: Rate Limiting Test")
        try:
            # Make 4 requests to same endpoint from same IP
            for i in range(1, 5):
                signup_data = {
                    "company_name": f"Test Company {i}",
                    "subdomain": f"testco{i}",
                    "owner_email": f"test{i}@test.com",
                    "owner_name": "Test",
                    "owner_password": "password123"
                }
                response = await client.post(
                    "/api/v1/signup/register",
                    json=signup_data,
                    headers={"x-forwarded-for": "192.168.1.1"}  # Same IP
                )
                if i <= 3:
                    status_ok = response.status_code in [200, 201, 400, 422]  # OK or validation error
                    print(f"   Request {i}: {response.status_code} {'✅' if status_ok else '❌'}")
                else:
                    # 4th request should be rate limited
                    is_rate_limited = response.status_code == 429
                    print(f"   Request {i} (4th): {response.status_code} {'✅ Rate Limited' if is_rate_limited else '❌'}")
        except Exception as e:
            print(f"   ❌ Error: {e}")

print("Starting endpoint tests...")
asyncio.run(test_endpoints())

print("\n" + "=" * 70)
print("✅ ENDPOINT TESTING COMPLETE")
print("=" * 70)
