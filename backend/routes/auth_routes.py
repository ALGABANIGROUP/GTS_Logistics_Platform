from __future__ import annotations

from datetime import datetime
from typing import AsyncGenerator, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.models.user import User

# Use the same DB dependency as the rest of the app
try:
    from backend.core.db_config import get_async_db
except ImportError:
    try:
        from backend.core.db_config import get_async_db
    except ImportError:
        # Fallback for testing/development
        async def get_async_db():
            raise RuntimeError("Database configuration not available")

router = APIRouter(prefix="/users", tags=["users"])


class UserUpdate(BaseModel):
    email: str
    full_name: Optional[str] = None
    company: Optional[str] = None
    country: Optional[str] = None
    user_type: Optional[str] = None
    phone_number: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class UserResponse(BaseModel):
    email: str
    full_name: Optional[str]
    company: Optional[str]
    country: Optional[str]
    user_type: Optional[str]
    phone_number: Optional[str]
    role: str
    is_active: bool
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


@router.put("/me", response_model=UserResponse)
async def update_me(
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_async_db),
):
    # 1) Find user by email
    stmt = select(User).where(User.email == user_data.email)
    result = await db.execute(stmt)
    user: Optional[User] = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # 2) Apply updates to ORM object
    update_fields = user_data.model_dump(exclude={"email"}, exclude_none=True)
    for field, value in update_fields.items():
        setattr(user, field, value)

    user.updated_at = datetime.utcnow()

    # 3) Commit changes
    await db.commit()
    await db.refresh(user)

    return user


@router.get("/me", response_model=UserResponse)
async def get_me(
    email: str,
    db: AsyncSession = Depends(get_async_db),
):
    stmt = select(User).where(User.email == email)
    result = await db.execute(stmt)
    user: Optional[User] = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user

