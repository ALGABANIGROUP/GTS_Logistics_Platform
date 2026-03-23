import asyncio
from sqlalchemy import text
from backend.database.config import init_engines, get_sessionmaker
from backend.security.auth import get_password_hash

async def create_test_user():
    init_engines()
    maker = get_sessionmaker()

    async with maker() as session:
        # Delete existing test user if exists
        await session.execute(text("DELETE FROM users WHERE email = 'test@gts.com'"))

        # Create test user with hashed password
        hashed_password = get_password_hash('test123')
        await session.execute(text("""
            INSERT INTO users (email, full_name, role, is_active, hashed_password, token_version, created_at)
            VALUES ('test@gts.com', 'Test User', 'super_admin', true, :hashed_password, 0, NOW())
        """), {"hashed_password": hashed_password})

        await session.commit()
        print('Test user created: test@gts.com / test123')

if __name__ == "__main__":
    asyncio.run(create_test_user())