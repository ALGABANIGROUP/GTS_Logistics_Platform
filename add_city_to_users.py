#!/usr/bin/env python3
"""Add city column to users table"""
import asyncio
import os
from sqlalchemy import text
from backend.database.config import get_sessionmaker

async def add_city_column():
    sessionmaker = get_sessionmaker()
    async with sessionmaker() as session:
        async with session.begin():
            # Add column
            await session.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS city VARCHAR(100)"))
            print("✓ Added city column to users table")
            
            # Update your user
            result = await session.execute(
                text("UPDATE users SET city = 'Vancouver' WHERE email = 'enjoy983@hotmail.com' RETURNING id, email, city")
            )
            row = result.first()
            if row:
                print(f"✓ Updated user: {row.email} -> city: {row.city}")
            else:
                print("✗ User not found")

if __name__ == "__main__":
    asyncio.run(add_city_column())
