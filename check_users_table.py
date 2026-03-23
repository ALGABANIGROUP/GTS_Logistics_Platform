#!/usr/bin/env python3
"""
Check users table structure
"""
import os
import asyncio
import asyncpg

async def check_users_table():
    conn = await asyncpg.connect(os.getenv('DATABASE_URL'))

    # Check if users table exists
    users_exists = await conn.fetchval('''
        SELECT EXISTS (
            SELECT 1 FROM information_schema.tables
            WHERE table_name = 'users'
        )
    ''')

    if users_exists:
        # Get users table structure
        columns = await conn.fetch('''
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'users'
            ORDER BY ordinal_position
        ''')

        print('📋 EN users:')
        print('=' * 50)
        for col in columns:
            nullable = 'NULL' if col['is_nullable'] == 'YES' else 'NOT NULL'
            print(f'  {col["column_name"]:20} {col["data_type"]:15} {nullable}')

        # Check if tenants table exists
        tenants_exists = await conn.fetchval('''
            SELECT EXISTS (
                SELECT 1 FROM information_schema.tables
                WHERE table_name = 'tenants'
            )
        ''')

        print(f'\n📊 EN:')
        print(f'  users: {"✅" if users_exists else "❌"}')
        print(f'  tenants: {"✅" if tenants_exists else "❌"}')

        # Count users
        user_count = await conn.fetchval('SELECT COUNT(*) FROM users')
        print(f'  EN: {user_count}')

    else:
        print('❌ EN users EN')

    await conn.close()

if __name__ == "__main__":
    asyncio.run(check_users_table())