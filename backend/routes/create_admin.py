from __future__ import annotations

from datetime import datetime
import os

from fastapi import APIRouter, Depends, HTTPException
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from backend.database.config import get_db_async  # type: ignore[import]
from backend.models.user import User  # type: ignore[import]

router = APIRouter(prefix="/admin-bootstrap", tags=["Admin Setup"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ADMIN_EMAIL = os.getenv("BOOTSTRAP_ADMIN_EMAIL", "").strip().lower()
ADMIN_PASSWORD = os.getenv("BOOTSTRAP_ADMIN_PASSWORD", "")
BOOTSTRAP_ENABLED = os.getenv("ENABLE_ADMIN_BOOTSTRAP_ROUTE", "").lower() in ("1", "true", "yes")


@router.get("/setup-admin")
async def create_admin_user(
    db: AsyncSession = Depends(get_db_async),
):
    try:
        if not BOOTSTRAP_ENABLED:
            raise HTTPException(status_code=404, detail="Not found")
        if not ADMIN_EMAIL or not ADMIN_PASSWORD:
            raise HTTPException(
                status_code=500,
                detail="Set BOOTSTRAP_ADMIN_EMAIL and BOOTSTRAP_ADMIN_PASSWORD before using admin bootstrap.",
            )

        # Check if admin already exists
        result = await db.execute(
            select(User).where(User.email == ADMIN_EMAIL)
        )
        existing_user = result.scalars().first()

        if existing_user:
            return {
                "message": "Admin already exists",
                "email": existing_user.email,
                "role": existing_user.role,
            }

        hashed_password = pwd_context.hash(ADMIN_PASSWORD)

        new_user = User(
            email=ADMIN_EMAIL,
            full_name="Super Admin",
            role="admin",
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            hashed_password=hashed_password,  # field used by auth logic
        )

        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        return {
            "message": "Admin created successfully",
            "email": new_user.email,
            "password": "[redacted]",
            "role": new_user.role,
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create admin: {e}",
        )

