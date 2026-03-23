#!/usr/bin/env python3
"""
Check tenants table structure
"""
import os
import asyncio
import asyncpg

async def check_tenants_table():
    conn = await asyncpg.connect(os.getenv('DATABASE_URL'))

    # Get tenants table structure
    columns = await conn.fetch('''
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_name = 'tenants'
        ORDER BY ordinal_position
    ''')

    print('📋 EN tenants:')
    print('=' * 50)
    for col in columns:
        nullable = 'NULL' if col['is_nullable'] == 'YES' else 'NOT NULL'
        print(f'  {col["column_name"]:20} {col["data_type"]:15} {nullable}')

    # Check tenant count
    tenant_count = await conn.fetchval('SELECT COUNT(*) FROM tenants')
    print(f'\n📊 EN tenants: {tenant_count}')

    # Check if tenants have plan_key
    if tenant_count > 0:
        sample_tenant = await conn.fetchrow('SELECT id, plan_key FROM tenants LIMIT 1')
        if sample_tenant:
            print(f'  EN tenant: id={sample_tenant["id"]}, plan_key={sample_tenant["plan_key"]}')

    await conn.close()

if __name__ == "__main__":
    asyncio.run(check_tenants_table())