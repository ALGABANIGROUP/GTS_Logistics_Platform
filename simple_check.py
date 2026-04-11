import asyncio
from backend.database.session import get_db

async def check_users():
    async for db in get_db():
        result = await db.execute('SELECT id, email FROM users LIMIT 5')
        users = result.fetchall()
        print('Users in database:')
        for user in users:
            print(f'ID: {user[0]}, Email: {user[1]}')
        break

if __name__ == "__main__":
    asyncio.run(check_users())