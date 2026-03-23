import asyncio
import sys
sys.path.insert(0, '.')
from backend.database.config import get_sessionmaker
from backend.models.user import User
from sqlalchemy import select

async def check_user_pass():
    sessionmaker = get_sessionmaker()
    async with sessionmaker() as session:
        result = await session.execute(select(User).where(User.email == 'operations@gabanilogistics.com'))
        user = result.scalar_one_or_none()
        if user:
            print(f'User: {user.email}')
            print(f'Password hash exists: {bool(user.password_hash)}')
            if user.password_hash:
                print(f'Password hash: {user.password_hash[:80]}...')
        else:
            print('User not found')

asyncio.run(check_user_pass())
