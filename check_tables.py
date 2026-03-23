#!/usr/bin/env python3
"""
Check if carriers and shippers tables exist
"""
import asyncio
import sys
import os
sys.path.append('backend')

from backend.database.session import async_session
from sqlalchemy import text

async def check_tables():
    async with async_session() as session:
        try:
            # Check if carriers table exists
            result = await session.execute(text("SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'carriers')"))
            carriers_exists = result.scalar()

            # Check if shippers table exists
            result = await session.execute(text("SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'shippers')"))
            shippers_exists = result.scalar()

            print(f'Carriers table exists: {carriers_exists}')
            print(f'Shippers table exists: {shippers_exists}')

        except Exception as e:
            print(f'Error checking tables: {e}')

if __name__ == "__main__":
    asyncio.run(check_tables())