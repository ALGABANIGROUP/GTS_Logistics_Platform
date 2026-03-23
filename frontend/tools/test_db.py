import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Retrieve DATABASE_URL
database_url = os.getenv("DATABASE_URL", "")

if database_url.startswith("postgresql://") and "+asyncpg" not in database_url:
    database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)

# Create async database engine
engine = create_async_engine(database_url, echo=True, future=True)

async def test_db_connection():
    """Test connection to the PostgreSQL database"""
    try:
        async with engine.connect() as conn:
            result = await conn.execute("SELECT datname, datcollate, encoding FROM pg_database;")
            databases = result.fetchall()
            print("\n✅ Connection successful! Databases available:")
            for db in databases:
                print(f"🔹 Name: {db[0]}, Collation: {db[1]}, Encoding: {db[2]}")
    except Exception as e:
        print(f"\n❌ Connection failed: {str(e)}")
    finally:
        await engine.dispose()

# Run the test
asyncio.run(test_db_connection())
