#!/usr/bin/env python3
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

# Test token
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6Im9wZXJhdGlvbnNAZ2FiYW5pbG9naXN0aWNzLmNvbSIsInJvbGUiOiJzdXBlcl9hZG1pbiIsImV4cCI6OTk5OTk5OTk5OX0.fake"

def test_token():
    """Test getting a real token first"""
    payload = {
        "grant_type": "password",
        "username": "operations@gabanilogistics.com",
        "password": "123456"
    }
    
    r = requests.post(
        f"{BASE_URL}/api/v1/auth/token",
        data=payload,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    if r.status_code == 200:
        data = r.json()
        token = data.get("access_token")
        print(f"✓ Got token: {token[:50]}...")
        return token
    else:
        print(f"✗ Failed to get token: {r.status_code}")
        print(f"  {r.text[:200]}")
        return None

def test_admin_users(token):
    """Test the /admin/users/management endpoint"""
    headers = {"Authorization": f"Bearer {token}"}
    
    r = requests.get(
        f"{BASE_URL}/api/v1/admin/users/management",
        headers=headers
    )
    
    print(f"\n/api/v1/admin/users/management:")
    print(f"  Status: {r.status_code}")
    
    if r.status_code == 200:
        data = r.json()
        print(f"  ✓ Success!")
        print(f"  Users: {data.get('total_users', 0)}")
    else:
        print(f"  ✗ Error: {r.text[:200]}")

if __name__ == "__main__":
    print("[Test] Testing /admin/users/management endpoint\n")
    
    token = test_token()
    if token:
        test_admin_users(token)
    else:
        print("Cannot test without a token")
