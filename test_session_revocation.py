#!/usr/bin/env python3
"""
Test script for Session Revocation functionality.
Tests that old tokens are invalidated after password change.
"""

import asyncio
import httpx
import json
import sys

BASE_URL = "http://127.0.0.1:8000"

async def test_session_revocation():
    """Test that old tokens are invalidated after password change."""

    async with httpx.AsyncClient() as client:
        # Step 1: Login with current password
        print("Step 1: Logging in with current password...")
        login_data = {
            "username": "enjoy983@hotmail.com",  # Use your test user email
            "password": "password123"  # Use your test password
        }

        try:
            response = await client.post(f"{BASE_URL}/auth/token", data=login_data)
            if response.status_code != 200:
                print(f"Login failed: {response.status_code} - {response.text}")
                return False

            token_data = response.json()
            old_token = token_data["access_token"]
            print(f"✓ Got access token: {old_token[:50]}...")

        except Exception as e:
            print(f"Login request failed: {e}")
            return False

        # Step 2: Verify old token works
        print("\nStep 2: Verifying old token works...")
        headers = {"Authorization": f"Bearer {old_token}"}
        try:
            response = await client.get(f"{BASE_URL}/auth/me", headers=headers)
            if response.status_code != 200:
                print(f"Old token verification failed: {response.status_code} - {response.text}")
                return False
            print("✓ Old token is valid")
        except Exception as e:
            print(f"Old token verification request failed: {e}")
            return False

        # Step 3: Change password (this should increment token_version)
        print("\nStep 3: Changing password...")
        change_data = {
            "old_password": "password123",
            "new_password": "newpassword123"
        }
        try:
            response = await client.post(f"{BASE_URL}/auth/change-password",
                                       json=change_data, headers=headers)
            if response.status_code != 200:
                print(f"Password change failed: {response.status_code} - {response.text}")
                return False
            print("✓ Password changed successfully")
        except Exception as e:
            print(f"Password change request failed: {e}")
            return False

        # Step 4: Verify old token is now invalid
        print("\nStep 4: Verifying old token is now invalid...")
        try:
            response = await client.get(f"{BASE_URL}/auth/me", headers=headers)
            if response.status_code == 401:
                print("✓ Old token correctly invalidated (401 Unauthorized)")
            else:
                print(f"✗ Old token still works! Status: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"Old token invalidation check failed: {e}")
            return False

        # Step 5: Login with new password
        print("\nStep 5: Logging in with new password...")
        login_data["password"] = "newpassword123"
        try:
            response = await client.post(f"{BASE_URL}/auth/token", data=login_data)
            if response.status_code != 200:
                print(f"New login failed: {response.status_code} - {response.text}")
                return False

            new_token_data = response.json()
            new_token = new_token_data["access_token"]
            print(f"✓ Got new access token: {new_token[:50]}...")

        except Exception as e:
            print(f"New login request failed: {e}")
            return False

        # Step 6: Verify new token works
        print("\nStep 6: Verifying new token works...")
        headers = {"Authorization": f"Bearer {new_token}"}
        try:
            response = await client.get(f"{BASE_URL}/auth/me", headers=headers)
            if response.status_code != 200:
                print(f"New token verification failed: {response.status_code} - {response.text}")
                return False
            print("✓ New token is valid")
        except Exception as e:
            print(f"New token verification request failed: {e}")
            return False

        print("\n🎉 Session Revocation test PASSED!")
        return True

if __name__ == "__main__":
    print("Testing Session Revocation functionality...")
    print("=" * 50)

    try:
        success = asyncio.run(test_session_revocation())
        if success:
            print("\n✅ All tests passed!")
            sys.exit(0)
        else:
            print("\n❌ Tests failed!")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test script failed: {e}")
        sys.exit(1)