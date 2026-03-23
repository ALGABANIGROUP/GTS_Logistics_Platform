#!/usr/bin/env python3
"""
Verify all bot names are English only
"""
import os
import asyncio
import asyncpg

async def verify_english_only():
    conn = await asyncpg.connect(os.getenv('DATABASE_URL'))

    # Check that all name_ar equals name_en
    bots = await conn.fetch('SELECT key, name_ar, name_en, status FROM ai_bots ORDER BY key')

    print('🔍 Verifying all bots are English only:')
    print('=' * 70)

    all_english = True
    for bot in bots:
        status_icon = '✅' if bot['status'] == 'active' else '❌'
        match = '✓' if bot['name_ar'] == bot['name_en'] else '✗'
        if bot['name_ar'] != bot['name_en']:
            all_english = False
        print(f'{status_icon} {match} {bot["key"]:20} | AR: {bot["name_ar"]:30} | EN: {bot["name_en"]}')

    print(f'\n📊 Result: {"✅ All bots are English" if all_english else "❌ Some bots are still mixed"}')
    print(f'📈 Total count: {len(bots)} bots')

    await conn.close()

if __name__ == "__main__":
    asyncio.run(verify_english_only())