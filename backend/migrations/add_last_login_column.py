"""
Add last_login column to users table
"""
from sqlalchemy import text
from backend.database.config import get_sessionmaker
import asyncio


async def add_last_login_column():
    """Add last_login timestamp to users table"""
    async_session = get_sessionmaker()
    
    async with async_session() as session:
        try:
            # Check if column exists
            check_query = text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'users' 
                AND column_name = 'last_login'
            """)
            
            result = await session.execute(check_query)
            exists = result.fetchone()
            
            if not exists:
                # Add last_login column
                alter_query = text("""
                    ALTER TABLE users 
                    ADD COLUMN last_login TIMESTAMP WITH TIME ZONE
                """)
                await session.execute(alter_query)
                await session.commit()
                print("✓ Added last_login column to users table")
            else:
                print("✓ last_login column already exists")
                
        except Exception as e:
            print(f"✗ Error adding last_login column: {e}")
            await session.rollback()


if __name__ == "__main__":
    asyncio.run(add_last_login_column())
