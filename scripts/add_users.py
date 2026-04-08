# scripts/add_users.py
import asyncio
import bcrypt
from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.models.user import User
from backend.config import settings

async def add_users():
    """Add default users to the database if none exist"""
    try:
        # Create database connection
        engine = create_async_engine(settings.ASYNC_DATABASE_URL, echo=True)
        async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

        async with async_session() as session:
            # Check if users already exist
            result = await session.execute(select(User).limit(1))
            existing = result.scalar_one_or_none()

            if existing:
                print("✅ Users already exist in database")
                return

            print("🔄 Adding default users to database...")

            # Create hashed passwords
            admin_password = bcrypt.hashpw("Gabani@2026".encode(), bcrypt.gensalt()).decode()
            admin123 = bcrypt.hashpw("admin123".encode(), bcrypt.gensalt()).decode()
            manager123 = bcrypt.hashpw("manager123".encode(), bcrypt.gensalt()).decode()
            user123 = bcrypt.hashpw("user123".encode(), bcrypt.gensalt()).decode()

            # Create users
            users = [
                User(
                    email="enjoy983@hotmail.com",
                    full_name="Super Admin",
                    role="super_admin",
                    is_active=True,
                    hashed_password=admin_password,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                    token_version=1
                ),
                User(
                    email="admin@gts.com",
                    full_name="System Administrator",
                    role="admin",
                    is_active=True,
                    hashed_password=admin123,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                    token_version=1
                ),
                User(
                    email="manager@gts.com",
                    full_name="Operations Manager",
                    role="manager",
                    is_active=True,
                    hashed_password=manager123,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                    token_version=1
                ),
                User(
                    email="user@gts.com",
                    full_name="Regular User",
                    role="user",
                    is_active=True,
                    hashed_password=user123,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                    token_version=1
                )
            ]

            for user in users:
                session.add(user)

            await session.commit()
            print(f"✅ Successfully added {len(users)} users to database")
            print("\n📋 Users added:")
            for user in users:
                print(f"  - {user.email} ({user.role})")

    except Exception as e:
        print(f"❌ Error adding users: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(add_users())