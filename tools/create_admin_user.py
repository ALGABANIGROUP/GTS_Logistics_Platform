import os
import asyncio

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import select

# Import the User model
from backend.models.user import User
from backend.security.passwords import hash_password

# Load database URL
ASYNC_DSN = os.getenv("ASYNC_DATABASE_URL") or os.getenv("DATABASE_URL")

if not ASYNC_DSN:
    raise RuntimeError("ASYNC_DATABASE_URL or DATABASE_URL is not set in environment")

engine = create_async_engine(ASYNC_DSN, echo=False)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)

# Admin account data
ADMIN_EMAIL = os.getenv("BOOTSTRAP_ADMIN_EMAIL", "").strip().lower()
ADMIN_USERNAME = os.getenv("BOOTSTRAP_ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("BOOTSTRAP_ADMIN_PASSWORD", "")
ADMIN_NAME = os.getenv("BOOTSTRAP_ADMIN_NAME", "GTS Admin")
ADMIN_ROLE = os.getenv("BOOTSTRAP_ADMIN_ROLE", "admin")

async def main():
    if not ADMIN_EMAIL or not ADMIN_PASSWORD:
        raise RuntimeError("Set BOOTSTRAP_ADMIN_EMAIL and BOOTSTRAP_ADMIN_PASSWORD before running this tool.")

    async with SessionLocal() as session:
        # Check if user already exists
        result = await session.execute(
            select(User).where(User.email == ADMIN_EMAIL)
        )
        existing = result.scalar_one_or_none()

        if existing:
            print(f"[INFO] User with email {ADMIN_EMAIL} already exists (id={existing.id})")
            return

        # Create the admin user (model fields matched to your User model)
        user = User(
            username=ADMIN_USERNAME,
            email=ADMIN_EMAIL,
            full_name=ADMIN_NAME,
            role=ADMIN_ROLE,
            hashed_password=hash_password(ADMIN_PASSWORD),
            is_active=True
        )

        session.add(user)
        await session.commit()
        print(f"[OK] Created admin user:")
        print(f"  Email:    {ADMIN_EMAIL}")
        print(f"  Username: {ADMIN_USERNAME}")
        print(f"  Role:     {ADMIN_ROLE}")
        print("  Password: [redacted - supplied from environment]")

if __name__ == "__main__":
    asyncio.run(main())
