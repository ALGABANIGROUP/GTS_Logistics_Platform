from __future__ import annotations

import asyncio
import os
import sys

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from backend.security.passwords import hash_password

sys.path.insert(0, os.path.dirname(__file__))

from backend.models.user import User


ADMIN_EMAIL = os.getenv("BOOTSTRAP_ADMIN_EMAIL", "").strip().lower()
ADMIN_PASSWORD = os.getenv("BOOTSTRAP_ADMIN_PASSWORD", "")
ADMIN_NAME = os.getenv("BOOTSTRAP_ADMIN_NAME", "System Administrator")
ADMIN_USERNAME = os.getenv("BOOTSTRAP_ADMIN_USERNAME", "admin")
ADMIN_ROLE = os.getenv("BOOTSTRAP_ADMIN_ROLE", "super_admin")
DATABASE_URL = os.getenv("ASYNC_DATABASE_URL") or "sqlite+aiosqlite:///./gts_database.db"


async def create_admin() -> None:
    if not ADMIN_EMAIL or not ADMIN_PASSWORD:
        raise RuntimeError("Set BOOTSTRAP_ADMIN_EMAIL and BOOTSTRAP_ADMIN_PASSWORD before running this script.")

    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        result = await session.execute(select(User).where(User.email == ADMIN_EMAIL))
        existing_user = result.scalar_one_or_none()

        if existing_user:
            existing_user.hashed_password = hash_password(ADMIN_PASSWORD)
            existing_user.role = ADMIN_ROLE
            existing_user.is_active = True
            existing_user.full_name = ADMIN_NAME
            session.add(existing_user)
            await session.commit()
            print(f"[create_admin] updated existing admin: {existing_user.email}")
        else:
            admin_user = User(
                email=ADMIN_EMAIL,
                full_name=ADMIN_NAME,
                username=ADMIN_USERNAME,
                hashed_password=hash_password(ADMIN_PASSWORD),
                role=ADMIN_ROLE,
                is_active=True,
                user_type="Admin",
                company="GTS",
            )
            session.add(admin_user)
            await session.commit()
            print(f"[create_admin] created admin: {ADMIN_EMAIL}")

        print("[create_admin] password source: environment (redacted)")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(create_admin())
