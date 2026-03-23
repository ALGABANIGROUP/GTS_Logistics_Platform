#!/usr/bin/env python3
import os
import asyncio
from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

load_dotenv()

async def list_tables():
    db_url = os.getenv('ASYNC_DATABASE_URL').replace('?sslmode=require', '')
    engine = create_async_engine(db_url, echo=False, connect_args={'ssl': True})
    
    async with engine.begin() as conn:
        result = await conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema='public' ORDER BY table_name"))
        tables = [row[0] for row in result.fetchall()]
    
    print("📊 Database Tables:\n")
    for t in sorted(tables):
        if any(keyword in t.lower() for keyword in ['supplier', 'load', 'source', 'freight', 'carrier']):
            print(f"✅ {t}")

asyncio.run(list_tables())
