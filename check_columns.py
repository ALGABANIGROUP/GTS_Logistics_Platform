import asyncio
from backend.database.session import async_session
from sqlalchemy import text

async def check_columns():
    async with async_session() as db:
        try:
            result = await db.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'carriers' ORDER BY column_name"))
            columns = result.scalars().all()
            print('Columns in carriers table:')
            for col in columns:
                print(f'  - {col}')
        except Exception as e:
            print(f'Error: {e}')

if __name__ == "__main__":
    asyncio.run(check_columns())