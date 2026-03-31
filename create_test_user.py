import asyncio
from datetime import datetime
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
            INSERT INTO users (
                email, username, full_name, role, is_active, hashed_password, 
                token_version, failed_login_attempts, two_factor_enabled, 
                is_banned, is_deleted, created_at, updated_at
            )
            VALUES (
                'test@gts.com', 'testuser', 'Test User', 'super_admin', 1, :hashed_password, 
                0, 0, 0, 
                0, 0, :created_at, :updated_at
            )
        """), {
            "hashed_password": hashed_password, 
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        })

        await session.commit()
        print('Test user created: test@gts.com / test123')

if __name__ == "__main__":
    asyncio.run(create_test_user())