"""
Verify the current database and the currently registered user
"""
import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from backend.database.config import get_sessionmaker
from sqlalchemy import text
import os

async def main():
    print("=" * 70)
    print("🔍 Verifying current database")
    print("=" * 70)
    
    database_url = os.getenv("DATABASE_URL", "")
    print(f"\n📍 DATABASE_URL from .env:")
    print(f"  {database_url}")
    
    try:
        session_maker = get_sessionmaker()
        
        async with session_maker() as session:
            # Check database type
            result = await session.execute(text("SELECT 1"))
            result.close()
            
            # Get user with email
            query = text("""
                SELECT id, email, full_name, role, token_version, is_active
                FROM users 
                WHERE email = 'enjoy983@hotmail.com'
            """)
            result = await session.execute(query)
            user = result.fetchone()
            
            if user:
                print(f"\n✅ User found:")
                print(f"  ID: {user[0]}")
                print(f"  Email: {user[1]}")
                print(f"  Name: {user[2]}")
                print(f"  Role: {user[3]}")
                print(f"  Token Version: {user[4]}")
                print(f"  Active: {user[5]}")
                print()
                
                if user[0] == 344:
                    print("⚠️ This user is from the old PostgreSQL database!")
                    print("⚠️ token_version = 0 - needs update")
                elif user[0] == 1:
                    print("✅ This user is from the local SQLite database")
                    if user[4] == 1:
                        print("✅ token_version is updated correctly")
                    else:
                        print("⚠️ token_version needs update")
            else:
                print("\n❌ User not found!")
                
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(main())
