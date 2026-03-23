import os, asyncio
from sqlalchemy.ext.asyncio import create_async_engine
dsn = (os.getenv("ASYNC_DATABASE_URL") or os.getenv("DATABASE_URL") 
       or os.getenv("DB_URL") or os.getenv("SQLALCHEMY_DATABASE_URI"))
print("DSN =", dsn)
async def main():
    if not dsn:
        raise SystemExit("No DSN env var set")
    engine = create_async_engine(dsn, future=True)
    async with engine.connect() as conn:
        res = await conn.execute("SELECT 1")
        print("DB OK:", res.scalar() == 1)
asyncio.run(main())
