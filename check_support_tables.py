#!/usr/bin/env python3
import asyncio
import sys
from pathlib import Path

repo_root = Path(__file__).resolve().parent
sys.path.insert(0, str(repo_root))

from backend.database.session import get_async_session
from sqlalchemy import text

async def check_tables():
    async for session in get_async_session():
        try:
            result = await session.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"))
            tables = result.fetchall()
            support_tables = [t[0] for t in tables if 'support' in t[0]]
            print(f'Support tables: {support_tables}')
            all_tables = [t[0] for t in tables]
            print(f'All tables: {all_tables[:10]}...')  # Show first 10
        except Exception as e:
            print(f'Error: {e}')

if __name__ == "__main__":
    asyncio.run(check_tables())