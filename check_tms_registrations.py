import asyncio
import asyncpg

async def main():
    conn = await asyncpg.connect(user='gabani_transport_solutions_user', password='__SET_IN_SECRET_MANAGER__', database='gabani_transport_solutions', host='dpg-cuicq2qj1k6c73asm5c0-a.oregon-postgres.render.com')
    rows = await conn.fetch('SELECT * FROM tms_registration_requests ORDER BY created_at DESC LIMIT 10')
    for row in rows:
        print(dict(row))
    await conn.close()

if __name__ == "__main__":
    asyncio.run(main())
