import asyncio
from backend.database.session import get_sessionmaker
from backend.models.user import User
from sqlalchemy import select

async def test():
    maker = get_sessionmaker()
    async with maker() as session:
        result = await session.execute(
            select(User).where(User.email == 'operations@gabanilogistics.com')
        )
        user = result.scalar_one_or_none()
        if user:
            print(f'User email: {user.email}')
            print(f'User role: {user.role}')
            print(f'Role == super_admin: {user.role == "super_admin"}')
            allowed_roles = ['admin', 'super_admin', 'system_admin']
            print(f'Role in allowed: {user.role in allowed_roles}')
        else:
            print('User not found')

asyncio.run(test())
