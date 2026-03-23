import asyncio
from backend.database.connection import _async_engine
from sqlalchemy import text

async def check_roles_columns():
    async with _async_engine.connect() as conn:
        result = await conn.execute(text("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_name = 'roles'
            ORDER BY ordinal_position
        """))
        print("Actual roles table columns:")
        for row in result:
            print(f"  {row[0]} ({row[1]}) - Nullable: {row[2]}")

if __name__ == "__main__":
    asyncio.run(check_roles_columns())
