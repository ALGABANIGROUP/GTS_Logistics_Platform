#!/usr/bin/env python3
"""Add system_type and subscription_tier columns to users table"""

import asyncio
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

def add_columns():
    load_dotenv()
    
    # Get the sync database URL
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("❌ DATABASE_URL not configured")
        return
    
    # Convert async URL to sync if needed
    if db_url.startswith("postgresql+psycopg://"):
        db_url = db_url.replace("postgresql+psycopg://", "postgresql://")
    
    print(f"📚 Connecting to database...")
    engine = create_engine(db_url)
    
    with engine.begin() as conn:
        print("📦 Checking if columns exist...")
        
        # Check system_type column
        result = conn.execute(text("""
            SELECT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name='users' AND column_name='system_type'
            )
        """))
        system_type_exists = result.scalar()
        
        # Check subscription_tier column
        result = conn.execute(text("""
            SELECT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name='users' AND column_name='subscription_tier'
            )
        """))
        subscription_tier_exists = result.scalar()
        
        # Add system_type if needed
        if not system_type_exists:
            print("➕ Adding system_type column...")
            conn.execute(text("""
                ALTER TABLE users ADD COLUMN system_type VARCHAR(50) NULL
            """))
            print("✅ system_type column added")
        else:
            print("✓ system_type column already exists")
        
        # Add subscription_tier if needed
        if not subscription_tier_exists:
            print("➕ Adding subscription_tier column...")
            conn.execute(text("""
                ALTER TABLE users ADD COLUMN subscription_tier VARCHAR(50) NULL DEFAULT 'demo'
            """))
            print("✅ subscription_tier column added")
        else:
            print("✓ subscription_tier column already exists")
        
        # Create indexes
        print("📑 Creating indexes...")
        try:
            conn.execute(text("CREATE INDEX ix_users_system_type ON users(system_type)"))
        except:
            pass  # Index might already exist
        
        try:
            conn.execute(text("CREATE INDEX ix_users_subscription_tier ON users(subscription_tier)"))
        except:
            pass  # Index might already exist
        
        print("✅ Indexes created/verified")
    
    engine.dispose()
    print("\n✅ Database schema updated successfully!")

if __name__ == "__main__":
    add_columns()
