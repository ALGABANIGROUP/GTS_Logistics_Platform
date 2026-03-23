#!/usr/bin/env python
"""Setup script to create the api_connections table and indexes."""

from sqlalchemy import create_engine, text
import os

db_url = os.getenv(
    'DATABASE_URL',
    'postgresql://gabani_transport_solutions_user:__SET_IN_SECRET_MANAGER__@dpg-cuicq2qj1k6c73asm5c0-a.oregon-postgres.render.com:5432/gabani_transport_solutions?sslmode=require'
)

engine = create_engine(db_url)

sql_commands = [
    '''CREATE TABLE IF NOT EXISTS api_connections (
        id SERIAL PRIMARY KEY,
        platform_name VARCHAR(255) NOT NULL,
        platform_category VARCHAR(50) NOT NULL,
        description TEXT,
        api_url VARCHAR(500) NOT NULL,
        connection_type VARCHAR(50) NOT NULL,
        api_key TEXT,
        api_secret TEXT,
        access_token TEXT,
        refresh_token TEXT,
        client_id VARCHAR(255),
        client_secret TEXT,
        oauth_callback_url VARCHAR(500),
        headers JSONB,
        query_params JSONB,
        extra_config JSONB,
        is_active BOOLEAN DEFAULT TRUE,
        is_verified BOOLEAN DEFAULT FALSE,
        last_tested_at TIMESTAMP,
        last_test_status VARCHAR(50),
        last_test_message TEXT,
        total_requests INTEGER DEFAULT 0,
        successful_requests INTEGER DEFAULT 0,
        failed_requests INTEGER DEFAULT 0,
        last_used_at TIMESTAMP,
        created_by INTEGER,
        created_at TIMESTAMP DEFAULT NOW(),
        updated_at TIMESTAMP DEFAULT NOW()
    )''',
    'CREATE INDEX IF NOT EXISTS idx_api_connections_platform_name ON api_connections(platform_name)',
    'CREATE INDEX IF NOT EXISTS idx_api_connections_category ON api_connections(platform_category)',
    'CREATE INDEX IF NOT EXISTS idx_api_connections_active ON api_connections(is_active)',
    'CREATE INDEX IF NOT EXISTS idx_api_connections_verified ON api_connections(is_verified)',
]

try:
    with engine.begin() as conn:
        # Execute table creation and index creation
        for sql in sql_commands:
            conn.execute(text(sql))
        print('✅ API connections table created successfully')
        
        # Update migration version
        try:
            conn.execute(text('DELETE FROM alembic_version WHERE version_num = :version'), {'version': 'api_connections_001'})
        except Exception as e:
            print(f"ℹ️  Delete old version: {str(e)[:50]}")
        
        conn.execute(text('INSERT INTO alembic_version (version_num) VALUES (:version)'), {'version': 'api_connections_001'})
        print('✅ Migration version updated to api_connections_001')
        
        # Verify table exists
        result = conn.execute(text("SELECT EXISTS(SELECT 1 FROM information_schema.tables WHERE table_name='api_connections')"))
        if result.scalar():
            print('✅ Table verified in database')
            
            # Get row count
            result = conn.execute(text("SELECT COUNT(*) FROM api_connections"))
            count = result.scalar()
            print(f'✅ Table has {count} rows')
            
except Exception as e:
    print(f"❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()
    exit(1)

print('\n✅ Database setup complete!')
