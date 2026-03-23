import asyncio
from backend.database.session import get_sessionmaker
from backend.models.user import User
from sqlalchemy import select

async def test():
    maker = get_sessionmaker()
    async with maker() as session:
        result = await session.execute(select(User).limit(1))
        user = result.scalar_one_or_none()
        if user:
            print(f"Email: {user.email}")
            print(f"Role: {user.role}")
            print(f"Has password_hash: {bool(user.password_hash)}")

asyncio.run(test())
