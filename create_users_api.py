#!/usr/bin/env python
"""Create test users via API endpoint"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

# Get auth token first
def get_token():
    response = requests.post(
        f"{BASE_URL}/api/v1/auth/token",
        data={"username": "admin@gts.local", "password": "admin123"}
    )
    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        print(f"Failed to get token: {response.text}")
        return None

# Create a user
def create_user(token, email, password, full_name, role):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "email": email,
        "password": password,
        "full_name": full_name,
        "role": role,
        "is_active": True
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/admin/users",
        headers=headers,
        json=payload
    )
    
    if response.status_code in (200, 201):
        print(f"✅ Created user: {email}")
        return response.json()
    else:
        print(f"⚠️  {email}: {response.status_code} - {response.text[:100]}")
        return None

# Main
token = get_token()
if not token:
    print("Cannot proceed without token")
    exit(1)

print(f"✅ Token obtained: {token[:20]}...")

users = [
    ("admin@test.local", "admin123", "Admin User", "admin"),
    ("manager@test.local", "manager123", "Manager User", "manager"),
    ("user@test.local", "user123", "Regular User", "user"),
]

for email, password, full_name, role in users:
    create_user(token, email, password, full_name, role)

print("\n✅ All users created!")
