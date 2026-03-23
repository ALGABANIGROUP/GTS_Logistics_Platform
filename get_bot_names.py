#!/usr/bin/env python3
"""
Get all AI bot names and details
"""
import os
import asyncio
import asyncpg

async def get_bot_names():
    """Get all AI bot names and details"""

    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        print("❌ No DATABASE_URL found")
        return

    try:
        conn = await asyncpg.connect(db_url)

        # Get all bots with their details
        bots = await conn.fetch('SELECT key, name_en, name_ar, status, category, icon FROM ai_bots ORDER BY key')

        print('🤖 EN Bots EN (24 EN):')
        print('=' * 80)

        active_count = 0
        for bot in bots:
            status_icon = '✅' if bot['status'] == 'active' else '❌'
            if bot['status'] == 'active':
                active_count += 1

            print(f'{status_icon} {bot["key"]}')
            print(f'   EN: {bot["name_en"]}')
            print(f'   EN: {bot["name_ar"]}')
            print(f'   EN: {bot["category"]} | EN: {bot["icon"]}')
            print()

        print(f'📊 EN: {len(bots)} EN')
        print(f'✅ Bots EN: {active_count}')
        print(f'❌ Bots EN: {len(bots) - active_count}')

        await conn.close()

    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(get_bot_names())