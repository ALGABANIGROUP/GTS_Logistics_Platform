"""
Add missing columns to production database
Run: python -m backend.scripts.add_missing_columns
"""

import asyncio
from sqlalchemy import text
from backend.database.session import get_async_session


async def add_missing_columns():
    """Add missing columns to users table"""
    async for session in get_async_session():
        try:
            # Add features column
            await session.execute(text("""
                DO $$ 
                BEGIN
                    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                   WHERE table_name='users' AND column_name='features') THEN
                        ALTER TABLE users ADD COLUMN features JSON DEFAULT '[]';
                    END IF;
                END $$;
            """))
            
            # Add data_scope column
            await session.execute(text("""
                DO $$ 
                BEGIN
                    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                   WHERE table_name='users' AND column_name='data_scope') THEN
                        ALTER TABLE users ADD COLUMN data_scope VARCHAR(50) DEFAULT 'personal';
                    END IF;
                END $$;
            """))
            
            # Add subscription_tier column if missing
            await session.execute(text("""
                DO $$ 
                BEGIN
                    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                   WHERE table_name='users' AND column_name='subscription_tier') THEN
                        ALTER TABLE users ADD COLUMN subscription_tier VARCHAR(50) DEFAULT 'basic';
                    END IF;
                END $$;
            """))
            
            # Add is_superuser column
            await session.execute(text("""
                DO $$ 
                BEGIN
                    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                   WHERE table_name='users' AND column_name='is_superuser') THEN
                        ALTER TABLE users ADD COLUMN is_superuser BOOLEAN DEFAULT FALSE;
                    END IF;
                END $$;
            """))
            
            # Add user_metadata column
            await session.execute(text("""
                DO $$ 
                BEGIN
                    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                   WHERE table_name='users' AND column_name='user_metadata') THEN
                        ALTER TABLE users ADD COLUMN user_metadata JSON DEFAULT '{}';
                    END IF;
                END $$;
            """))
            
            # Add tenant_id column
            await session.execute(text("""
                DO $$ 
                BEGIN
                    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                   WHERE table_name='users' AND column_name='tenant_id') THEN
                        ALTER TABLE users ADD COLUMN tenant_id INTEGER;
                    END IF;
                END $$;
            """))
            
            await session.commit()
            print("✅ Missing columns added successfully")
            
        except Exception as e:
            print(f"❌ Failed to add columns: {e}")
            await session.rollback()


async def main():
    await add_missing_columns()


if __name__ == "__main__":
    asyncio.run(main())