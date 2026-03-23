#!/usr/bin/env python3
import asyncio
import httpx
from backend.security.auth import create_access_token_payload
from backend.database.session import get_sessionmaker
from backend.models.user import User
from sqlalchemy import select

async def test():
    # Get user from database
    maker = get_sessionmaker()
    async with maker() as session:
        result = await session.execute(
            select(User).where(User.email == "operations@gabanilogistics.com")
        )
        user = result.scalar_one_or_none()
        
        if not user:
            print("User not found!")
            return
        
        # Create token
        token_payload = await create_access_token_payload(user)
        token = token_payload["access_token"]
        
        print(f"Token: {token[:50]}...\n")
        
        # Test the endpoint
        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {token}"}
            
            # Test /auth/me first
            r = await client.get("http://127.0.0.1:8000/api/v1/auth/me", headers=headers)
            print(f"GET /api/v1/auth/me: {r.status_code}")
            if r.status_code == 200:
                data = r.json()
                print(f"  User role: {data.get('user', {}).get('role')}\n")
            else:
                print(f"  Error: {r.text[:100]}\n")
            
            # Test /admin/users/management
            r = await client.get("http://127.0.0.1:8000/api/v1/admin/users/management", headers=headers)
            print(f"GET /api/v1/admin/users/management: {r.status_code}")
            if r.status_code == 200:
                data = r.json()
                print(f"  Users: {data.get('total_users')}")
            else:
                print(f"  Error: {r.text[:200]}")

asyncio.run(test())
