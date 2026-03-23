import asyncio
from backend.database.session import async_session
from sqlalchemy import text

async def check_table():
    async with async_session() as db:
        try:
            result = await db.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"))
            tables = result.scalars().all()
            print('Tables in database:')
            for table in tables:
                print(f'  - {table}')

            if 'carriers' in tables:
                result = await db.execute(text('SELECT COUNT(*) FROM carriers'))
                count = result.scalar()
                print(f'Carriers count: {count}')
            else:
                print('Carriers table does not exist!')
        except Exception as e:
            print(f'Error: {e}')

if __name__ == "__main__":
    asyncio.run(check_table())