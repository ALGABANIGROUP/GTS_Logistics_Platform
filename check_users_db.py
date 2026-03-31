import asyncio
from backend.database.connection import get_async_engine_from_env
from sqlalchemy import text

async def check_users():
    engine = get_async_engine_from_env()
    async with engine.begin() as conn:
        try:
            result = await conn.execute(text('SELECT COUNT(*) as count FROM users'))
            count = result.scalar()
            print(f'Users table exists. User count: {count}')

            if count > 0:
                result = await conn.execute(text('SELECT id, email, username, role, is_active FROM users LIMIT 5'))
                rows = result.mappings().all()
                print('Sample users:')
                for row in rows:
                    print(f'  ID: {row["id"]}, Email: {row["email"]}, Username: {row["username"]}, Role: {row["role"]}, Active: {row["is_active"]}')
        except Exception as e:
            print(f'Error checking users table: {e}')
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(check_users())