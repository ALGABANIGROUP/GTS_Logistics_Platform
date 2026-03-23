#!/usr/bin/env python3
"""
Run the AI bots cleanup script
"""
import os
import asyncio
import asyncpg

async def run_cleanup():
    """Run the AI bots cleanup SQL script"""

    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        print("❌ No DATABASE_URL found")
        return False

    try:
        conn = await asyncpg.connect(db_url)
        print("✅ Connected to database")

        # Read SQL file
        sql_file = "clean_ai_bots.sql"
        if not os.path.exists(sql_file):
            print(f"❌ SQL file not found: {sql_file}")
            return False

        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()

        print("🔄 Executing cleanup script...")

        # Execute the entire script as one transaction
        await conn.execute(sql_content)

        print("✅ Cleanup script executed successfully")

        # Verify results
        bots = await conn.fetch('SELECT key, name_en, status, type FROM ai_bots ORDER BY type, key')

        print(f"\n🤖 Bots after cleanup ({len(bots)}):")
        print('=' * 50)

        user_bots = [b for b in bots if b['type'] == 'user']
        system_bots = [b for b in bots if b['type'] == 'system']

        print(f"👤 User bots ({len(user_bots)}):")
        for bot in user_bots:
            status_icon = '✅' if bot['status'] == 'active' else '❌'
            print(f"  {status_icon} {bot['key']}: {bot['name_en']}")

        print(f"\n🔧 System bots ({len(system_bots)}):")
        for bot in system_bots:
            status_icon = '✅' if bot['status'] == 'active' else '❌'
            print(f"  {status_icon} {bot['key']}: {bot['name_en']}")

        await conn.close()
        return True

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    success = asyncio.run(run_cleanup())
    if success:
        print("\n🎉 Bots cleanup completed!")
    else:
        print("\n❌ Failed to cleanup Bots!")