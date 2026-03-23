#!/usr/bin/env python3
"""
Verify database fixes were applied correctly
"""
import os
import asyncio
import asyncpg

async def verify_fixes():
    """Verify all database fixes"""

    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        print("❌ No DATABASE_URL found")
        return

    try:
        conn = await asyncpg.connect(db_url)
        print("✅ Connected to database")

        # Check roles
        roles = await conn.fetch('SELECT key, name, name_ar FROM roles ORDER BY key')
        print(f'\n📋 ROLES ({len(roles)} total):')
        for role in roles:
            print(f'  {role["key"]}: {role["name"]} ({role["name_ar"]})')

        # Check AI bots
        bots = await conn.fetch('SELECT key, name_en, status FROM ai_bots ORDER BY key')
        print(f'\n🤖 AI BOTS ({len(bots)} total):')
        for bot in bots[:5]:  # Show first 5
            print(f'  {bot["key"]}: {bot["name_en"]} ({bot["status"]})')
        if len(bots) > 5:
            print(f'  ... and {len(bots)-5} more bots')

        # Check plans
        plans = await conn.fetch('SELECT key, name_en, price_monthly FROM plans ORDER BY price_monthly')
        print(f'\n💰 PLANS ({len(plans)} total):')
        for plan in plans:
            print(f'  {plan["key"]}: {plan["name_en"]} - ${plan["price_monthly"]}/month')

        # Check subscriptions table
        subs_count = await conn.fetchval('SELECT COUNT(*) FROM subscriptions')
        print(f'\n📊 SUBSCRIPTIONS: {subs_count} records')

        # Check for null values in roles.name
        null_names = await conn.fetchval('SELECT COUNT(*) FROM roles WHERE name IS NULL OR name = \'\'')
        print(f'\n🔍 NULL role names: {null_names} (should be 0)')

        await conn.close()
        print("\n✅ Verification complete!")

    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(verify_fixes())