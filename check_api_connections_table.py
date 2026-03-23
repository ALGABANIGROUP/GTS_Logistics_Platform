#!/usr/bin/env python3
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()
db_url = os.getenv('DATABASE_URL')
engine = create_engine(db_url)

try:
    with engine.connect() as conn:
        # Check if api_connections table exists
        result = conn.execute(text('''
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'api_connections'
            )
        '''))
        exists = result.scalar()
        
        if exists:
            result = conn.execute(text('SELECT COUNT(*) FROM api_connections'))
            count = result.scalar()
            print(f'✅ api_connections table exists with {count} rows')
        else:
            print('❌ api_connections table does NOT exist')
            print('Creating table now...')
            
            # Create the table
            conn.execute(text('''
                CREATE TABLE IF NOT EXISTS api_connections (
                    id SERIAL PRIMARY KEY,
                    platform_name VARCHAR(255) NOT NULL,
                    platform_category VARCHAR(50) NOT NULL,
                    description TEXT,
                    api_url VARCHAR(500),
                    connection_type VARCHAR(50) NOT NULL,
                    api_key TEXT,
                    api_secret TEXT,
                    access_token TEXT,
                    refresh_token TEXT,
                    client_id VARCHAR(255),
                    client_secret TEXT,
                    oauth_callback_url VARCHAR(500),
                    headers JSONB DEFAULT '{}',
                    query_params JSONB DEFAULT '{}',
                    extra_config JSONB DEFAULT '{}',
                    is_active BOOLEAN DEFAULT true,
                    is_verified BOOLEAN DEFAULT false,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_tested_at TIMESTAMP,
                    last_used_at TIMESTAMP,
                    total_requests INTEGER DEFAULT 0,
                    successful_requests INTEGER DEFAULT 0,
                    failed_requests INTEGER DEFAULT 0,
                    tenant_id INTEGER,
                    created_by INTEGER,
                    updated_by INTEGER,
                    notes TEXT
                )
            '''))
            conn.commit()
            print('✅ Table created successfully!')
            
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()
