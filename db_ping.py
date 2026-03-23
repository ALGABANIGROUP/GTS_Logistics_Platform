import os, asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
dsn = os.getenv("ASYNC_DATABASE_URL"); print("DSN =", dsn)
async def main():
    engine = create_async_engine(dsn, future=True)
    async with engine.connect() as conn:
        v = (await conn.execute(text("SELECT 1"))).scalar_one()
        print("DB OK:", v == 1)
asyncio.run(main())
