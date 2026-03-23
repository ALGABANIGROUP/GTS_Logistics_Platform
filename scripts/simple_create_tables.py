#!/usr/bin/env python3
"""
Simple script to create subscription tables using asyncpg directly
"""
import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv
import asyncpg

async def create_tables():
    """Create subscription tables"""
    # Load environment
    env_path = Path(__file__).parent.parent / ".env"
    load_dotenv(env_path)

    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL not found")
        return False

    print("🔧 Connecting to database...")

    try:
        # Connect to database
        conn = await asyncpg.connect(database_url)

        # Read SQL file
        sql_file = Path(__file__).parent / 'create_subscription_tables.sql'
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()

        print("🔧 Creating subscription tables...")

        # Execute SQL
        await conn.execute(sql_content)

        print("✅ Subscription tables created successfully!")

        await conn.close()
        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(create_tables())
    exit(0 if success else 1)