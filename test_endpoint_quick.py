#!/usr/bin/env python3
import requests

BASE_URL = "http://127.0.0.1:8000"

# Try to get a token
r = requests.post(
    f"{BASE_URL}/api/v1/auth/token",
    data={"username": "operations@gabanilogistics.com", "password": "123456"},
    headers={"Content-Type": "application/x-www-form-urlencoded"}
)

print(f"Login response: {r.status_code}")
print(f"Response: {r.text[:200]}")

if r.status_code == 200:
    data = r.json()
    token = data.get("access_token")
    print(f"\n✓ Got token: {token[:50]}...")
    
    # Now test the admin endpoint
    headers = {"Authorization": f"Bearer {token}"}
    
    r2 = requests.get(f"{BASE_URL}/api/v1/admin/users/management", headers=headers)
    print(f"\nAdmin endpoint response: {r2.status_code}")
    if r2.status_code == 200:
        data = r2.json()
        print(f"✓ Success! Got {data.get('total_users', 0)} users")
    else:
        print(f"Error: {r2.text[:300]}")
else:
    print("Failed to get token")
