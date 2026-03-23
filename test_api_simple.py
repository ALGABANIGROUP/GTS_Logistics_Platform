#!/usr/bin/env python3
"""
Simple test script for Safety API
"""
import httpx
import json

BASE_URL = "http://127.0.0.1:8000"
API_BASE = f"{BASE_URL}/api/v1"

def test_api():
    print("=" * 60)
    print("🛡️  SAFETY MANAGER BOT - API TEST")
    print("=" * 60)
    
    # Test 1: Backend Health
    print("\n🔍 Test 1: Backend Health")
    try:
        with httpx.Client() as client:
            response = client.get(f"{BASE_URL}/docs", timeout=5)
            print(f"✅ Backend Status: {response.status_code}")
    except Exception as e:
        print(f"❌ Backend Error: {e}")
        return
    
    # Test 2: Safety Status
    print("\n🔍 Test 2: Safety Status Endpoint")
    try:
        with httpx.Client() as client:
            response = client.get(f"{API_BASE}/safety/status", timeout=5)
            print(f"✅ Status Code: {response.status_code}")
            if response.status_code == 200:
                print(f"   Data: {response.json()}")
            elif response.status_code == 401:
                print("   ⚠️  Auth required (expected)")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Safety Dashboard
    print("\n🔍 Test 3: Safety Dashboard Endpoint")
    try:
        with httpx.Client() as client:
            response = client.get(f"{API_BASE}/safety/dashboard", timeout=5)
            print(f"✅ Status Code: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   Safety Score: {data.get('safety_score', 'N/A')}")
                print(f"   Risk Level: {data.get('risk_level', 'N/A')}")
            elif response.status_code == 401:
                print("   ⚠️  Auth required (expected)")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 4: All Endpoints
    print("\n🔍 Test 4: All Safety Endpoints")
    endpoints = [
        "/safety/status",
        "/safety/config",
        "/safety/dashboard",
        "/safety/incidents/statistics",
        "/safety/compliance/check",
        "/safety/risks/assess",
    ]
    
    with httpx.Client() as client:
        for endpoint in endpoints:
            try:
                response = client.get(f"{API_BASE}{endpoint}", timeout=5)
                status = "✅" if response.status_code in [200, 401] else "❌"
                print(f"   {status} GET {endpoint}: {response.status_code}")
            except Exception as e:
                print(f"   ❌ GET {endpoint}: {str(e)}")
    
    print("\n" + "=" * 60)
    print("✅ TEST COMPLETED")
    print("=" * 60)

if __name__ == "__main__":
    test_api()
