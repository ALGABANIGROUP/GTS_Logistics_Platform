import asyncio
from sqlalchemy import select
from backend.database.config import init_engines, get_sessionmaker
from backend.models.user import User
from backend.models.unified_models import UserSystemsAccess

async def create_admin_user():
    init_engines()
    maker = get_sessionmaker()

    async with maker() as session:
        # Check if admin user exists
        result = await session.execute(select(User).where(User.email == 'admin@gts.com'))
        existing = result.scalar_one_or_none()

        if existing:
            print('Admin user already exists')
            return

        # Create admin user
        admin = User(
            email='admin@gts.com',
            full_name='GTS Administrator',
            role='super_admin',
            is_active=True,
            hashed_password='$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LeCt1uB0YgHvQ3S3e'  # password: admin123
        )
        session.add(admin)
        await session.commit()
        await session.refresh(admin)

        # Add system access
        system_access = UserSystemsAccess(
            user_id=admin.id,
            system_type='gts_main',
            access_level='super_admin',
            is_active=True
        )
        session.add(system_access)
        await session.commit()

        print(f'Created admin user: {admin.email} with ID: {admin.id}')

if __name__ == "__main__":
    asyncio.run(create_admin_user())