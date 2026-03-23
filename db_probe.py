import os, re, asyncio, asyncpg

raw = os.environ.get("ASYNC_DATABASE_URL", "")
print("RAW DSN:", raw)

# Convert SQLAlchemy format to asyncpg format
dsn = re.sub(r"^postgresql\+asyncpg://", "postgresql://", raw)
# Clean any ssl/sslmode from URL if mistakenly present
dsn = re.sub(r"([?&])(sslmode|ssl)=[^&]+&?", r"\1", dsn).rstrip("?&")
print("TEST DSN:", dsn)

async def main():
    try:
        conn = await asyncpg.connect(dsn, ssl=True)
        v = await conn.fetchval("SELECT 1")
        print("asyncpg.connect OK / SELECT 1 =", v)
        await conn.close()
    except Exception:
        import traceback; traceback.print_exc()

asyncio.run(main())