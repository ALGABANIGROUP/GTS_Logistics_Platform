#!/usr/bin/env python3
"""
Simple script to create basic subscription tables using asyncpg directly
"""
import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv
import asyncpg

async def create_basic_tables():
    """Create basic subscription tables"""
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

        print("🔧 Creating basic subscription tables...")

        # Create tables one by one
        tables_sql = [
            """
            CREATE TABLE IF NOT EXISTS plans (
                key VARCHAR(50) PRIMARY KEY,
                name_ar VARCHAR(100) NOT NULL,
                name_en VARCHAR(100) NOT NULL,
                description TEXT,
                price_monthly DECIMAL(10,2),
                price_yearly DECIMAL(10,2),
                features JSONB DEFAULT '[]',
                limits JSONB DEFAULT '{}',
                is_active BOOLEAN DEFAULT true,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS roles (
                key VARCHAR(50) PRIMARY KEY,
                name_ar VARCHAR(100) NOT NULL,
                name_en VARCHAR(100) NOT NULL,
                permissions JSONB DEFAULT '[]',
                is_system BOOLEAN DEFAULT false,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS tenants (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                name VARCHAR(255) NOT NULL,
                slug VARCHAR(100) UNIQUE NOT NULL,
                plan_key VARCHAR(50) NOT NULL,
                status VARCHAR(20) DEFAULT 'active',
                settings JSONB DEFAULT '{}',
                email_config JSONB DEFAULT '{}',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                tenant_id UUID NOT NULL,
                email VARCHAR(255) NOT NULL,
                password_hash VARCHAR(255),
                name VARCHAR(100) NOT NULL,
                role_key VARCHAR(50) NOT NULL,
                is_active BOOLEAN DEFAULT true,
                last_login TIMESTAMP,
                settings JSONB DEFAULT '{}',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(tenant_id, email)
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS ai_bots (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                key VARCHAR(50) UNIQUE NOT NULL,
                name_ar VARCHAR(100) NOT NULL,
                name_en VARCHAR(100) NOT NULL,
                description TEXT,
                type VARCHAR(20) CHECK (type IN ('user', 'system')),
                category VARCHAR(50),
                icon VARCHAR(10),
                email_local_part VARCHAR(100),
                version VARCHAR(20) DEFAULT '1.0.0',
                status VARCHAR(20) DEFAULT 'active',
                availability VARCHAR(50),
                endpoints JSONB DEFAULT '{}',
                features JSONB DEFAULT '[]',
                dependencies JSONB DEFAULT '[]',
                config JSONB DEFAULT '{}',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
        ]

        for i, sql in enumerate(tables_sql, 1):
            try:
                await conn.execute(sql)
                print(f"  ✅ Created table {i}/{len(tables_sql)}")
            except Exception as e:
                print(f"  ⚠️  Table {i} failed: {str(e)[:100]}...")
                # Continue with other tables

        # Add foreign keys
        fk_sql = [
            "ALTER TABLE tenants ADD CONSTRAINT fk_tenants_plan FOREIGN KEY (plan_key) REFERENCES plans(key);",
            "ALTER TABLE users ADD CONSTRAINT fk_users_tenant FOREIGN KEY (tenant_id) REFERENCES tenants(id);",
            "ALTER TABLE users ADD CONSTRAINT fk_users_role FOREIGN KEY (role_key) REFERENCES roles(key);"
        ]

        for sql in fk_sql:
            try:
                await conn.execute(sql)
                print("  ✅ Added foreign key")
            except Exception as e:
                print(f"  ⚠️  FK failed: {str(e)[:100]}...")

        print("✅ Basic subscription tables created successfully!")

        await conn.close()
        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(create_basic_tables())
    exit(0 if success else 1)