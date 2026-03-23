#!/usr/bin/env python3
"""
Simple test script to diagnose the 500 error in /api/v1/auth/token
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

print("🧪 Testing /api/v1/auth/token endpoint")
print("=" * 60)

# Test data
data = {
    "username": "enjoy983@hotmail.com",
    "password": "password123"
}

try:
    print(f"\n📤 Sending POST request to {BASE_URL}/api/v1/auth/token")
    print(f"   Credentials: {data}")
    
    response = requests.post(
        f"{BASE_URL}/api/v1/auth/token",
        data=data
    )
    
    print(f"\n📥 Response Status: {response.status_code}")
    print(f"   Content-Type: {response.headers.get('content-type')}")
    
    # Try to parse as JSON
    try:
        result = response.json()
        print(f"\n   Response Body:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except:
        print(f"\n   Response Body (raw):")
        print(response.text[:500])
    
    if response.status_code != 200:
        print(f"\n⚠️  ERROR: Expected 200, got {response.status_code}")
        if "detail" in response.json():
            print(f"   Detail: {response.json()['detail']}")
    else:
        print(f"\n✅ SUCCESS: Token received!")
    
except requests.exceptions.ConnectionError as e:
    print(f"\n❌ Connection Error: Cannot connect to {BASE_URL}")
    print(f"   Make sure backend is running on port 8000")
    print(f"   Error: {e}")
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
