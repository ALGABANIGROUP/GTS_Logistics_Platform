#!/usr/bin/env python3
import os
import asyncio
from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

load_dotenv()

async def view_load_sources():
    db_url = os.getenv('ASYNC_DATABASE_URL').replace('?sslmode=require', '')
    engine = create_async_engine(db_url, echo=False, connect_args={'ssl': True})
    
    async with engine.begin() as conn:
        result = await conn.execute(text("""
            SELECT id, name, email, is_active, created_at 
            FROM carriers 
            ORDER BY created_at DESC
        """))
        
        print("🔗 Registered Load Sources:\n")
        print("=" * 70)
        for row in result.fetchall():
            id, name, email, is_active, created_at = row
            status = "✅ Active" if is_active else "❌ Inactive"
            print(f"🆔 {id}")
            print(f"📛 Name: {name}")
            print(f"📧 Email: {email}")
            print(f"📊 Status: {status}")
            print(f"📅 Date: {created_at}")
            print("=" * 70)

asyncio.run(view_load_sources())
