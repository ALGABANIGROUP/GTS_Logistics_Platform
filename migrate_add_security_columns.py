#!/usr/bin/env python3
"""
Migration script to add security columns to users table
"""
import asyncio
import os
import sys
from pathlib import Path

# Load .env file first
env_file = Path(__file__).parent / ".env"
if env_file.exists():
    from dotenv import load_dotenv
    load_dotenv(env_file)

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

async def migrate():
    """Add security columns to users table"""
    
    # Get DATABASE_URL from env
    database_url = os.getenv("ASYNC_DATABASE_URL") or os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL not set! Please set ASYNC_DATABASE_URL env var")
        return
    
    # Convert sync URL to async if needed
    if "postgresql://" in database_url:
        database_url = database_url.replace("postgresql://", "postgresql+asyncpg://")
    
    # Remove sslmode parameter as asyncpg handles it differently
    database_url = database_url.replace("?sslmode=require", "")
    database_url = database_url.replace("&sslmode=require", "")
    
    print(f"🔗 Connecting to: {database_url.split('@')[1] if '@' in database_url else 'database'}")
    
    # Create async engine with proper SSL settings
    engine = create_async_engine(
        database_url, 
        echo=False,
        connect_args={"ssl": True}  # Enable SSL for asyncpg
    )
    
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        try:
            print("📊 Adding security columns to users table...")
            
            # SQL statements to add columns
            statements = [
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS failed_login_attempts INTEGER NOT NULL DEFAULT 0;",
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS lockout_until TIMESTAMP WITH TIME ZONE;",
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS password_changed_at TIMESTAMP WITH TIME ZONE;",
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS two_factor_enabled BOOLEAN NOT NULL DEFAULT FALSE;",
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS two_factor_secret VARCHAR(512);",
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS two_factor_backup_codes VARCHAR(2000);",
            ]
            
            for stmt in statements:
                col_name = stmt.split("ADD COLUMN IF NOT EXISTS")[1].strip().split()[0]
                print(f"  ➕ {col_name}...", end=" ")
                try:
                    await session.execute(text(stmt))
                    print("✅")
                except Exception as e:
                    if "already exists" in str(e):
                        print("⏭️ (already exists)")
                    else:
                        print(f"❌ {e}")
            
            await session.commit()
            print("\n✅ Migration complete!")
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            await session.rollback()
            raise
        finally:
            await engine.dispose()

if __name__ == "__main__":
    asyncio.run(migrate())
