"""Add missing columns to roles table

This migration adds the 'features' and 'data_scope' columns to the roles table.
"""
import asyncio
from backend.database.connection import _async_engine
from sqlalchemy import text

async def add_missing_columns():
    async with _async_engine.begin() as conn:
        # Check if columns exist first
        result = await conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'roles'
        """))
        existing_cols = {row[0] for row in result}
        
        print(f"Existing columns: {existing_cols}")
        
        # Add features column if missing
        if 'features' not in existing_cols:
            print("Adding 'features' column...")
            await conn.execute(text("""
                ALTER TABLE roles 
                ADD COLUMN features JSONB DEFAULT '[]'::jsonb
            """))
            print("✓ Added 'features' column")
        else:
            print("✓ 'features' column already exists")
        
        # Add data_scope column if missing
        if 'data_scope' not in existing_cols:
            print("Adding 'data_scope' column...")
            await conn.execute(text("""
                ALTER TABLE roles 
                ADD COLUMN data_scope VARCHAR(20) DEFAULT 'tenant_only'
            """))
            print("✓ Added 'data_scope' column")
        else:
            print("✓ 'data_scope' column already exists")
        
        print("\n✅ Migration completed successfully!")

if __name__ == "__main__":
    asyncio.run(add_missing_columns())
