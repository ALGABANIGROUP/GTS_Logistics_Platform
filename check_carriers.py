#!/usr/bin/env python3
import os
import asyncio
from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

load_dotenv()

async def check_carriers_table():
    db_url = os.getenv('ASYNC_DATABASE_URL').replace('?sslmode=require', '')
    engine = create_async_engine(db_url, echo=False, connect_args={'ssl': True})
    
    async with engine.begin() as conn:
        # Get columns
        result = await conn.execute(text("""
            SELECT column_name, data_type, is_nullable 
            FROM information_schema.columns 
            WHERE table_name='carriers' 
            ORDER BY ordinal_position
        """))
        
        print("✅ Carriers Table Structure:\n")
        for col in result.fetchall():
            name, dtype, nullable = col
            print(f"  • {name} ({dtype}) {'NULL' if nullable == 'YES' else 'NOT NULL'}")
        
        # Count existing records
        count_result = await conn.execute(text("SELECT COUNT(*) FROM carriers"))
        count = count_result.scalar()
        print(f"\n📊 Total Records: {count}")

asyncio.run(check_carriers_table())
