"""
Create all users needed for Locust load testing
Creates: tester@gts.com, admin@gts.com, operator1-5@gts.com
"""
import asyncio
from sqlalchemy import text
from backend.database.config import init_engines, get_sessionmaker
from backend.security.auth import get_password_hash

async def create_load_test_users():
    init_engines()
    maker = get_sessionmaker()

    async with maker() as session:
        users_to_create = [
            # Regular user for load testing
            {
                "email": "tester@gts.com",
                "password": "123456",
                "full_name": "Load Test User",
                "role": "user"
            },
            # Admin user
            {
                "email": "admin@gts.com",
                "password": "admin123",
                "full_name": "Admin User",
                "role": "admin"
            },
            # Operator users (5)
            {
                "email": "operator1@gts.com",
                "password": "operator123",
                "full_name": "Operator 1",
                "role": "operator"
            },
            {
                "email": "operator2@gts.com",
                "password": "operator123",
                "full_name": "Operator 2",
                "role": "operator"
            },
            {
                "email": "operator3@gts.com",
                "password": "operator123",
                "full_name": "Operator 3",
                "role": "operator"
            },
            {
                "email": "operator4@gts.com",
                "password": "operator123",
                "full_name": "Operator 4",
                "role": "operator"
            },
            {
                "email": "operator5@gts.com",
                "password": "operator123",
                "full_name": "Operator 5",
                "role": "operator"
            }
        ]

        for user in users_to_create:
            # Delete existing user if exists
            await session.execute(
                text("DELETE FROM users WHERE email = :email"),
                {"email": user["email"]}
            )

            # Create user with hashed password
            hashed_password = get_password_hash(user["password"])
            await session.execute(text("""
                INSERT INTO users (email, full_name, role, is_active, hashed_password, token_version, created_at)
                VALUES (:email, :full_name, :role, true, :hashed_password, 0, NOW())
            """), {
                "email": user["email"],
                "full_name": user["full_name"],
                "role": user["role"],
                "hashed_password": hashed_password
            })

            print(f'✅ Created user: {user["email"]} / {user["password"]} (role: {user["role"]})')

        await session.commit()
        print('\n🎉 All load test users created successfully!')
        print('\n📋 User credentials:')
        print('   tester@gts.com / 123456 (user)')
        print('   admin@gts.com / admin123 (admin)')
        print('   operator1-5@gts.com / operator123 (operator)')

if __name__ == "__main__":
    asyncio.run(create_load_test_users())
