#!/usr/bin/env python3
"""
Run tenant_id migration for users table
"""
import asyncio
import os
import asyncpg
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv(Path(__file__).parent / ".env")

async def run_migration():
    """Run the tenant_id migration"""
    # Get database URL from environment
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        print("❌ DATABASE_URL not found in environment")
        return

    print("📋 Connecting to database...")

    migration_file = Path(__file__).parent / "backend" / "database" / "migrations" / "013_add_tenant_id_to_users.sql"

    if not migration_file.exists():
        print(f"❌ Migration file not found: {migration_file}")
        return

    # Read migration SQL
    with open(migration_file, 'r', encoding='utf-8') as f:
        sql = f.read()

    print("📄 SQL content:")
    print(sql)

    try:
        conn = await asyncpg.connect(db_url)
        print("🔗 Connected to database")

        # Execute the SQL
        await conn.execute(sql)
        print("✅ Migration completed successfully!")

        await conn.close()

    except Exception as e:
        print(f"❌ Migration failed: {e}")

if __name__ == "__main__":
    asyncio.run(run_migration())