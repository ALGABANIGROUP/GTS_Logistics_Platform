#!/usr/bin/env python3
"""
Run the subscriptions table creation migration
"""
import os
import asyncio
import asyncpg

async def run_subscriptions_migration():
    """Run the subscriptions table creation migration"""

    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        print("❌ No DATABASE_URL found")
        return False

    try:
        conn = await asyncpg.connect(db_url)
        print("✅ Connected to database")

        # Read SQL file
        sql_file = "create_subscriptions_table.sql"
        if not os.path.exists(sql_file):
            print(f"❌ SQL file not found: {sql_file}")
            return False

        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()

        print("🔄 Executing subscriptions migration...")

        # Execute the entire script as one transaction
        await conn.execute(sql_content)

        print("✅ Subscriptions migration completed successfully")

        # Verify results
        # Check if subscriptions table exists
        table_exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT 1 FROM information_schema.tables
                WHERE table_name = 'subscriptions'
            )
        """)

        if table_exists:
            # Get table structure
            columns = await conn.fetch("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = 'subscriptions'
                ORDER BY ordinal_position
            """)

            print(f"\n📋 subscriptions table structure ({len(columns)} columns):")
            print('=' * 50)
            for col in columns:
                nullable = 'NULL' if col['is_nullable'] == 'YES' else 'NOT NULL'
                print(f"  {col['column_name']:20} {col['data_type']:15} {nullable}")

            # Check subscription count
            sub_count = await conn.fetchval("SELECT COUNT(*) FROM subscriptions")
            print(f"\n📊 Number of subscriptions: {sub_count}")

            # Check active subscriptions
            active_count = await conn.fetchval("SELECT COUNT(*) FROM subscriptions WHERE status = 'active'")
            print(f"✅ Active subscriptions: {active_count}")

            # Check plans
            plan_count = await conn.fetchval("SELECT COUNT(*) FROM plans")
            print(f"💰 Number of plans: {plan_count}")

        else:
            print("❌ subscriptions table was not created!")

        await conn.close()
        return True

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    success = asyncio.run(run_subscriptions_migration())
    if success:
        print("\n🎉 subscriptions table created successfully!")
    else:
        print("\n❌ Failed to create subscriptions table!")