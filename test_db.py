import asyncio
from backend.database.connection import get_async_engine_from_env

async def test_db():
    try:
        engine = get_async_engine_from_env()
        async with engine.begin() as conn:
            await conn.run_sync(lambda sync_conn: print('Database connected successfully'))
        await engine.dispose()
        print("Database test completed")
    except Exception as e:
        print(f"Database error: {e}")

if __name__ == "__main__":
    asyncio.run(test_db())