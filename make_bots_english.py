#!/usr/bin/env python3
"""
Make all bot names English only
"""
import os
import asyncio
import asyncpg

async def make_all_bots_english():
    conn = await asyncpg.connect(os.getenv('DATABASE_URL'))

    # Update all bots to use English names for both Arabic and English fields
    await conn.execute('''
        UPDATE ai_bots
        SET name_ar = name_en
        WHERE name_ar != name_en OR name_ar IS NULL
    ''')

    # Verify the changes
    bots = await conn.fetch('SELECT key, name_ar, name_en, status FROM ai_bots ORDER BY key')

    print('✅ All Bots updated to English:')
    print('=' * 60)

    for bot in bots:
        status_icon = '✅' if bot['status'] == 'active' else '❌'
        print(f'{status_icon} {bot["key"]:20} | {bot["name_ar"]}')

    print(f'\n📊 Updated {len(bots)} bots')

    await conn.close()

if __name__ == "__main__":
    asyncio.run(make_all_bots_english())