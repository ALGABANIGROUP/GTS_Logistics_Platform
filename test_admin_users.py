#!/usr/bin/env python3
"""Test admin users endpoint"""
import asyncio
import aiohttp
import json

async def test_admin_users():
    async with aiohttp.ClientSession() as session:
        # Step 1: Get auth token
        auth_url = "http://127.0.0.1:8000/api/v1/auth/token"
        auth_data = aiohttp.FormData()
        auth_data.add_field('username', 'admin@gts.local')
        auth_data.add_field('password', 'admin123')
        
        async with session.post(auth_url, data=auth_data) as resp:
            if resp.status != 200:
                print(f"❌ Auth failed: {resp.status}")
                text = await resp.text()
                print(f"Response: {text[:200]}")
                return
            
            auth_json = await resp.json()
            token = auth_json.get('access_token')
            print(f"✅ Got token: {token[:30]}...")
        
        # Step 2: Get users list
        users_url = "http://127.0.0.1:8000/api/v1/admin/users/management"
        headers = {'Authorization': f'Bearer {token}'}
        
        async with session.get(users_url, headers=headers) as resp:
            if resp.status != 200:
                print(f"❌ Failed to get users: {resp.status}")
                text = await resp.text()
                print(f"Response: {text[:500]}")
                return
            
            users_json = await resp.json()
            users = users_json.get('users', [])
            print(f"✅ Got {len(users)} users")
            print("\nUsers:")
            for user in users:
                print(f"  - {user['email']}: {user['role']}")
            
            # Print raw JSON for inspection
            print("\n✅ Raw JSON (first user):")
            if users:
                print(json.dumps(users[0], indent=2))

if __name__ == "__main__":
    asyncio.run(test_admin_users())
