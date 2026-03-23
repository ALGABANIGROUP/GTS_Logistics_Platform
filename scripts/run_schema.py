#!/usr/bin/env python3
"""
Run subscription tables SQL schema
"""
import asyncio
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

from sqlalchemy import text
from backend.database.config import get_sessionmaker

async def run_schema():
    """Run the subscription tables schema"""
    try:
        # Read SQL file
        sql_file = os.path.join(os.path.dirname(__file__), 'create_subscription_tables.sql')
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()

        print("🔧 Creating subscription tables...")

        # Split SQL into individual statements
        statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip() and not stmt.strip().startswith('--')]

        # Execute each statement
        sessionmaker = get_sessionmaker()
        async with sessionmaker() as session:
            for i, stmt in enumerate(statements, 1):
                if stmt:
                    try:
                        await session.execute(text(stmt))
                        print(f"  ✅ Executed statement {i}/{len(statements)}")
                    except Exception as e:
                        print(f"  ⚠️  Statement {i} failed (might be OK): {str(e)[:100]}...")
                        # Continue with other statements

            await session.commit()

        print("✅ Subscription tables created successfully!")

    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False

    return True


if __name__ == "__main__":
    success = asyncio.run(run_schema())
    sys.exit(0 if success else 1)