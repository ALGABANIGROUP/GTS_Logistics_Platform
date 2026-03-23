#!/usr/bin/env python3
"""
Show detailed information about cleaned AI bots
"""
import os
import asyncio
import asyncpg

async def show_clean_bots():
    conn = await asyncpg.connect(os.getenv('DATABASE_URL'))

    # Get all bots with full details
    bots = await conn.fetch('''
        SELECT key, name_ar, name_en, description, type, category, icon,
               status, availability, email_local_part
        FROM ai_bots
        ORDER BY type, category, key
    ''')

    print('🤖 Organized bots after cleanup:')
    print('=' * 80)

    user_bots = [b for b in bots if b['type'] == 'user']
    system_bots = [b for b in bots if b['type'] == 'system']

    print(f'👤 User bots ({len(user_bots)}):')
    print('-' * 50)
    for bot in user_bots:
        status_icon = '✅' if bot['status'] == 'active' else '❌'
        email = f' ({bot["email_local_part"]})' if bot['email_local_part'] else ''
        print(f'{status_icon} {bot["key"]:20} | {bot["name_en"]:25} | {bot["category"]:10} | {bot["availability"]:12}{email}')

    print(f'\n🔧 System bots ({len(system_bots)}):')
    print('-' * 50)
    for bot in system_bots:
        status_icon = '✅' if bot['status'] == 'active' else '❌'
        email = f' ({bot["email_local_part"]})' if bot['email_local_part'] else ''
        print(f'{status_icon} {bot["key"]:20} | {bot["name_en"]:25} | {bot["category"]:10} | {bot["availability"]:12}{email}')

    # Show deleted bots
    deleted_bots = ['endpoints', 'ui_config', 'maintenance_dev', 'sales', 'security', 'mapleload_canada']
    print(f'\n🗑️  Deleted bots ({len(deleted_bots)}):')
    print('-' * 30)
    for bot in deleted_bots:
        print(f'❌ {bot}')

    print(f'\n📊 Summary:')
    print(f'  Before cleanup: 24 bots')
    print(f'  After cleanup: {len(bots)} bots')
    print(f'  Deleted: {len(deleted_bots)} bots')
    print(f'  Active bots: {len([b for b in bots if b["status"] == "active"])}')
    print(f'  Inactive bots: {len([b for b in bots if b["status"] != "active"])}')

    await conn.close()

if __name__ == "__main__":
    asyncio.run(show_clean_bots())