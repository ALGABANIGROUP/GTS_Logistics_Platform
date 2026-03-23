#!/usr/bin/env python3
"""
Simple database fix script - runs critical SQL fixes with per-statement commits
"""
import os
import sys
import asyncpg
from pathlib import Path

async def run_simple_fix():
    """Run the simple database fixes with individual commits"""

    # Get database URL from environment
    db_url = os.getenv('DATABASE_URL') or os.getenv('ASYNC_DATABASE_URL')
    if not db_url:
        print("❌ No DATABASE_URL found in environment")
        return False

    print(f"🔗 Connecting to database...")

    try:
        # Connect to database
        conn = await asyncpg.connect(db_url)
        print("✅ Connected successfully")

        # Read SQL file
        sql_file = Path(__file__).parent / "simple_db_fix.sql"
        if not sql_file.exists():
            print(f"❌ SQL file not found: {sql_file}")
            return False

        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()

        # Split SQL into individual statements
        statements = []
        current_statement = ""
        in_block_comment = False

        for line in sql_content.split('\n'):
            line = line.strip()

            # Skip empty lines and comments
            if not line or line.startswith('--'):
                continue

            # Handle block comments
            if '/*' in line:
                in_block_comment = True
            if '*/' in line:
                in_block_comment = False
                continue
            if in_block_comment:
                continue

            current_statement += line + " "

            # Check if statement is complete
            if line.endswith(';'):
                statements.append(current_statement.strip())
                current_statement = ""

        print(f"📄 Found {len(statements)} SQL statements to execute")

        # Execute each statement individually with commit
        success_count = 0
        for i, stmt in enumerate(statements, 1):
            try:
                print(f"🔄 Executing statement {i}/{len(statements)}...")
                await conn.execute(stmt)
                # asyncpg auto-commits individual statements
                success_count += 1
                print(f"✅ Statement {i} completed")
            except Exception as e:
                print(f"❌ Statement {i} failed: {str(e)}")
                # Continue with next statement instead of aborting

        # Run verification queries
        print("\n🔍 Running verification queries...")
        try:
            results = await conn.fetch("""
                SELECT 'Roles count:' as check_name, COUNT(*) as value FROM roles
                UNION ALL
                SELECT 'AI Bots count:', COUNT(*) FROM ai_bots
                UNION ALL
                SELECT 'Plans count:', COUNT(*) FROM plans
                UNION ALL
                SELECT 'Subscriptions exists:', CASE WHEN EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'subscriptions') THEN 1 ELSE 0 END
            """)

            print("\n📊 Verification Results:")
            for row in results:
                print(f"  {row['check_name']} {row['value']}")

        except Exception as e:
            print(f"❌ Verification failed: {str(e)}")

        await conn.close()
        print(f"\n🎉 Completed: {success_count}/{len(statements)} statements executed successfully")

        return success_count > 0

    except Exception as e:
        print(f"❌ Database error: {str(e)}")
        return False

if __name__ == "__main__":
    import asyncio
    success = asyncio.run(run_simple_fix())
    sys.exit(0 if success else 1)