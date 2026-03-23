import asyncio
from backend.database.connection import _async_engine
from sqlalchemy import inspect, text

async def check_roles_table():
    # Query the table structure directly
    async with _async_engine.connect() as conn:
        result = await conn.execute(text("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'roles'
            ORDER BY ordinal_position
        """))
        print("Roles table columns:")
        for row in result:
            print(f"- {row[0]} ({row[1]})")

if __name__ == "__main__":
    asyncio.run(check_roles_table())
