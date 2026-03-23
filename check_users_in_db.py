#!/usr/bin/env python3
"""
Check what users are available in the database
"""
import sys
sys.path.insert(0, r'c:\Users\enjoy\dev\GTS')

import asyncio
from backend.database.config import get_db_async, engine
from backend.models.user import User
from sqlalchemy import select

async def check_users():
    print("🔍 Checking users in database...\n")
    
    async with engine.begin() as conn:
        result = await conn.execute(select(User).limit(10))
        users = result.scalars().all()
        
        if not users:
            print("❌ No users found in database")
            return
        
        print(f"✅ Found {len(users)} users:\n")
        for user in users:
            print(f"  📧 Email: {user.email}")
            print(f"     ID: {user.id}")
            print(f"     Role: {getattr(user, 'role', 'N/A')}")
            print(f"     Is Active: {getattr(user, 'is_active', 'N/A')}")
            print(f"     Password Hash: {'Set' if getattr(user, 'password_hash', None) or getattr(user, 'hashed_password', None) else 'NOT SET'}")
            print()

try:
    asyncio.run(check_users())
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
