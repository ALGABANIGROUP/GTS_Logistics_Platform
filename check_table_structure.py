#!/usr/bin/env python3
"""
Check ai_bots table structure
"""
import os
import asyncio
import asyncpg

async def check_table_structure():
    conn = await asyncpg.connect(os.getenv('DATABASE_URL'))

    # Get table structure
    columns = await conn.fetch('''
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns
        WHERE table_name = 'ai_bots'
        ORDER BY ordinal_position
    ''')

    print('📋 EN ai_bots EN:')
    print('=' * 60)
    for col in columns:
        nullable = 'NULL' if col['is_nullable'] == 'YES' else 'NOT NULL'
        default = f' DEFAULT {col["column_default"]}' if col['column_default'] else ''
        print(f'{col["column_name"]:20} {col["data_type"]:15} {nullable}{default}')

    await conn.close()

if __name__ == "__main__":
    asyncio.run(check_table_structure())