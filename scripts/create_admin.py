# scripts/create_admin.py
import asyncio
import bcrypt
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.models.user import User
from backend.config import settings

async def create_admin():
    engine = create_async_engine(settings.ASYNC_DATABASE_URL, echo=True)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # التحقق من وجود المستخدم
        result = await session.execute(select(User).where(User.email == "superadmin@gts.com"))
        existing = result.scalar_one_or_none()

        if existing:
            print("Admin user already exists")
            return

        # إنشاء مستخدم super_admin
        hashed = bcrypt.hashpw("Admin@2026".encode(), bcrypt.gensalt()).decode()

        admin = User(
            email="superadmin@gts.com",
            full_name="Super Administrator",
            role="super_admin",
            is_active=True,
            hashed_password=hashed
        )

        session.add(admin)
        await session.commit()
        print("✅ Super Admin created: superadmin@gts.com / Admin@2026")

if __name__ == "__main__":
    asyncio.run(create_admin())