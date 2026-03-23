#!/usr/bin/env python3
"""
Check existing subscriptions table
"""
import os
import asyncio
import asyncpg

async def check_existing_subscriptions():
    conn = await asyncpg.connect(os.getenv('DATABASE_URL'))

    # Check if subscriptions table exists and get its structure
    table_exists = await conn.fetchval('''
        SELECT EXISTS (
            SELECT 1 FROM information_schema.tables
            WHERE table_name = 'subscriptions'
        )
    ''')

    if table_exists:
        print('✅ EN subscriptions EN')

        # Get current structure
        columns = await conn.fetch('''
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name = 'subscriptions'
            ORDER BY ordinal_position
        ''')

        print('\n📋 EN:')
        print('=' * 60)
        for col in columns:
            nullable = 'NULL' if col['is_nullable'] == 'YES' else 'NOT NULL'
            default = f' DEFAULT {col["column_default"]}' if col['column_default'] else ''
            print(f'  {col["column_name"]:20} {col["data_type"]:15} {nullable}{default}')

        # Check current data
        count = await conn.fetchval('SELECT COUNT(*) FROM subscriptions')
        print(f'\n📊 EN: {count} EN')

        if count > 0:
            sample = await conn.fetchrow('SELECT * FROM subscriptions LIMIT 1')
            print('📝 EN:')
            for key, value in sample.items():
                print(f'  {key}: {value}')

    else:
        print('❌ EN subscriptions EN')

    await conn.close()

if __name__ == "__main__":
    asyncio.run(check_existing_subscriptions())