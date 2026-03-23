from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional, Tuple

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from backend.auth.rbac_middleware import require_permission
from backend.core.db_config import get_async_db
from backend.models.user import User
from backend.security.auth import get_current_user

router = APIRouter(prefix="/users", tags=["Users"])


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    company: Optional[str] = None
    country: Optional[str] = None
    user_type: Optional[str] = None
    phone_number: Optional[str] = None
    system_type: Optional[str] = None
    subscription_tier: Optional[str] = None
    role: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: Optional[str] = None
    username: Optional[str] = None
    company: Optional[str] = None
    country: Optional[str] = None
    user_type: Optional[str] = None
    phone_number: Optional[str] = None
    db_role: Optional[str] = None
    token_role: Optional[str] = None
    effective_role: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


def _extract_email_and_role(current_user: Any) -> Tuple[Optional[str], str]:
    if isinstance(current_user, dict):
        return current_user.get("email"), current_user.get("role", "user")
    return getattr(current_user, "email", None), getattr(current_user, "role", "user")


def _to_response_model(user: User, token_role: str) -> UserResponse:
    dto = UserResponse.model_validate(user)
    dto.db_role = getattr(user, "role", None)
    dto.token_role = token_role
    try:
        from backend.security.rbac import compute_effective_role  # type: ignore

        dto.effective_role = compute_effective_role(token_role, dto.db_role)
    except Exception:
        dto.effective_role = token_role
    return dto


async def ensure_user_exists(
    db: AsyncSession,
    email: str,
    role: str = "user",
) -> User:
    try:
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        if user:
            return user

        user = User(
            email=email,
            role=role,
            is_active=1,
            created_at=datetime.utcnow(),
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user
    except Exception as exc:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to ensure user exists: {exc}",
        )


@router.get("/vfme", response_model=UserResponse, summary="VF Debug: Get current user profile (no query)")
async def get_current_user_profile_vf(
    db: AsyncSession = Depends(get_async_db),
    current_user: Any = Depends(get_current_user),
) -> UserResponse:
    email, token_role = _extract_email_and_role(current_user)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email not found in token.",
        )

    try:
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        if user:
            return _to_response_model(user, token_role=token_role)
    except Exception:
        pass

    return UserResponse(
        id=-1,
        email=email,
        full_name=getattr(current_user, "full_name", None),
        username=getattr(current_user, "username", None),
        company=getattr(current_user, "company", None),
        country=getattr(current_user, "country", None),
        user_type=getattr(current_user, "user_type", None),
        phone_number=getattr(current_user, "phone_number", None),
        db_role=None,
        token_role=token_role,
        effective_role=token_role,
        is_active=True,
        created_at=None,
        updated_at=None,
    )


@router.get("/me", response_model=UserResponse, summary="Get current user profile")
async def get_current_user_profile(
    db: AsyncSession = Depends(get_async_db),
    current_user: Any = Depends(get_current_user),
) -> UserResponse:
    email, token_role = _extract_email_and_role(current_user)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email not found in token.",
        )

    try:
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        if user:
            return _to_response_model(user, token_role=token_role)
    except Exception:
        pass

    return UserResponse(
        id=-1,
        email=email,
        full_name=getattr(current_user, "full_name", None),
        username=getattr(current_user, "username", None),
        company=getattr(current_user, "company", None),
        country=getattr(current_user, "country", None),
        user_type=getattr(current_user, "user_type", None),
        phone_number=getattr(current_user, "phone_number", None),
        db_role=None,
        token_role=token_role,
        effective_role=token_role,
        is_active=True,
        created_at=None,
        updated_at=None,
    )


@router.put("/me", response_model=UserResponse, summary="Update current user profile")
async def update_current_user_profile(
    payload: UserUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user: Any = Depends(get_current_user),
    _=Depends(require_permission("users.update")),
) -> UserResponse:
    email, token_role = _extract_email_and_role(current_user)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email not found in token.",
        )

    try:
        user = await ensure_user_exists(db, email=email, role=token_role)
        update_data = payload.model_dump(exclude_unset=True)
        if update_data:
            update_data["updated_at"] = datetime.utcnow()
            stmt = (
                update(User)
                .where(User.id == user.id)
                .values(**update_data)
                .execution_options(synchronize_session="fetch")
            )
            await db.execute(stmt)
            await db.commit()
            await db.refresh(user)

        return _to_response_model(user, token_role=token_role)
    except HTTPException:
        raise
    except Exception as exc:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user profile: {exc}",
        )


@router.get("/test", summary="Simple users routes test")
async def test_users_endpoint() -> Dict[str, Any]:
    return {
        "ok": True,
        "message": "Users routes are working",
        "endpoints": [
            "GET /users/me",
            "PUT /users/me",
        ],
    }
