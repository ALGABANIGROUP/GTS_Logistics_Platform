#!/usr/bin/env python
import sys
import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from backend.database.config import _get_async_dsn

async def check_user():
    dsn = _get_async_dsn()
    engine = create_async_engine(dsn)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # List all users
        result = await session.execute(
            text("SELECT id, email, role, is_active FROM users LIMIT 10")
        )
        users = result.fetchall()
        print(f"Found {len(users)} users:")
        for user in users:
            print(f"  - ID: {user[0]}, Email: {user[1]}, Role: {user[2]}, Active: {user[3]}")
    
    await engine.dispose()

asyncio.run(check_user())
