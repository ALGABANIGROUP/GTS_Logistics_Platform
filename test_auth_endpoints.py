#!/usr/bin/env python3
"""
Quick authentication endpoint verification script
Tests all auth endpoints to ensure they're working correctly
"""

import asyncio
import httpx
import sys
from typing import Dict, Any

BASE_URL = "http://127.0.0.1:8000"
TEST_USER = {
    "username": "enjoy983@hotmail.com",
    "password": "password123",
}


async def test_login() -> Dict[str, Any]:
    """Test login endpoint"""
    print("\n🔐 TEST 1: Login Endpoint")
    print("=" * 50)
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{BASE_URL}/api/v1/auth/token",
                data={
                    "username": TEST_USER["username"],
                    "password": TEST_USER["password"],
                }
            )
            print(f"Status: {response.status_code}")
            result = response.json()
            print(f"Response: {result}")
            
            if response.status_code == 200 and result.get("access_token"):
                print("✅ Login successful")
                return result
            else:
                print("❌ Login failed")
                return None
        except Exception as e:
            print(f"❌ Error: {e}")
            return None


async def test_get_user(access_token: str) -> Dict[str, Any]:
    """Test get user endpoint"""
    print("\n👤 TEST 2: Get User Profile")
    print("=" * 50)
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{BASE_URL}/api/v1/auth/me",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            print(f"Status: {response.status_code}")
            result = response.json()
            print(f"Response: {result}")
            
            if response.status_code == 200:
                print("✅ User profile retrieved")
                return result
            else:
                print("❌ Failed to get user profile")
                return None
        except Exception as e:
            print(f"❌ Error: {e}")
            return None


async def test_quick_auth(access_token: str) -> Dict[str, Any]:
    """Test quick auth endpoint (no database)"""
    print("\n⚡ TEST 3: Quick Auth Check")
    print("=" * 50)
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{BASE_URL}/api/v1/auth/me/quick",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            print(f"Status: {response.status_code}")
            result = response.json()
            print(f"Response: {result}")
            
            if response.status_code == 200:
                print("✅ Quick auth check successful")
                return result
            else:
                print("❌ Quick auth check failed")
                return None
        except Exception as e:
            print(f"❌ Error: {e}")
            return None


async def test_refresh_token(access_token: str) -> Dict[str, Any]:
    """Test refresh token endpoint"""
    print("\n🔄 TEST 4: Refresh Token Endpoint")
    print("=" * 50)
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{BASE_URL}/api/v1/auth/refresh",
                json={"refresh_token": access_token}  # Using access token as test
            )
            print(f"Status: {response.status_code}")
            result = response.json()
            print(f"Response: {result}")
            
            if response.status_code == 200 and result.get("access_token"):
                print("✅ Token refresh successful")
                return result
            else:
                print("⚠️  Token refresh not working as expected (may need proper refresh token)")
                return result
        except Exception as e:
            print(f"❌ Error: {e}")
            return None


async def test_unauthorized() -> None:
    """Test unauthorized access"""
    print("\n🚫 TEST 5: Unauthorized Access (No Token)")
    print("=" * 50)
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}/api/v1/auth/me")
            print(f"Status: {response.status_code}")
            result = response.json()
            print(f"Response: {result}")
            
            if response.status_code == 401:
                print("✅ Correctly returned 401 for unauthorized access")
            else:
                print("❌ Should have returned 401")
        except Exception as e:
            print(f"❌ Error: {e}")


async def main():
    """Run all tests"""
    print("\n" + "=" * 50)
    print("🧪 GTS Authentication Endpoint Tests")
    print("=" * 50)
    
    # Test 1: Login
    login_result = await test_login()
    if not login_result:
        print("\n❌ Cannot proceed without valid login")
        sys.exit(1)
    
    access_token = login_result.get("access_token")
    
    # Test 2: Get user profile
    await test_get_user(access_token)
    
    # Test 3: Quick auth
    await test_quick_auth(access_token)
    
    # Test 4: Refresh token
    await test_refresh_token(access_token)
    
    # Test 5: Unauthorized
    await test_unauthorized()
    
    print("\n" + "=" * 50)
    print("🎉 All endpoint tests completed!")
    print("=" * 50 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
