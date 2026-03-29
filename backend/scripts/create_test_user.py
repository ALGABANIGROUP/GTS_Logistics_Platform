"""
Create test user for development
Run: python -m backend.scripts.create_test_user
"""

import asyncio
import bcrypt
from sqlalchemy import select

from backend.database.session import get_async_session
from backend.models.user import User


async def create_test_user():
    """Create a test user if not exists"""
    async for session in get_async_session():
        # Check if user exists
        result = await session.execute(
            select(User).where(User.email == "test@example.com")
        )
        user = result.scalar_one_or_none()

        if user:
            print("Test user already exists")
            return

        # Create test user
        hashed = bcrypt.hashpw("test123".encode('utf-8'), bcrypt.gensalt())

        test_user = User(
            email="test@example.com",
            username="testuser",
            hashed_password=hashed.decode('utf-8'),
            role="user",
            is_active=True
        )

        session.add(test_user)
        await session.commit()

        print("✅ Test user created:")
        print("   Email: test@example.com")
        print("   Password: test123")
        print("   Username: testuser")


if __name__ == "__main__":
    asyncio.run(create_test_user())