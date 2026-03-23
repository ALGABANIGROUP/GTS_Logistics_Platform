from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, EmailStr
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database.config import get_db_async
from backend.models.user import User
from backend.security.access_context import (
    require_any_feature,
    require_any_module,
    require_permission,
)
from backend.security.auth import get_password_hash

router = APIRouter(prefix="/api/v1/drivers", tags=["Drivers"])


class DriverCreate(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    password: Optional[str] = None
    company: Optional[str] = None
    country: Optional[str] = None
    user_type: Optional[str] = None
    manager_id: Optional[int] = None
    is_active: bool = True


class DriverUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    password: Optional[str] = None
    company: Optional[str] = None
    country: Optional[str] = None
    user_type: Optional[str] = None
    manager_id: Optional[int] = None
    is_active: Optional[bool] = None


def _driver_guard(view_only: bool = False):
    deps = [
        Depends(require_any_module(["tms", "dispatcher"])),
        Depends(require_any_feature(["tms.fleet", "dispatcher.core"])),
    ]
    if view_only:
        deps.append(Depends(require_permission("drivers.view")))
    else:
        deps.append(Depends(require_permission("drivers.manage")))
    return deps


def _user_payload(user: User) -> Dict[str, Any]:
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "phone_number": user.phone_number,
        "role": user.role,
        "is_active": user.is_active,
        "company": user.company,
        "country": user.country,
        "user_type": user.user_type,
        "manager_id": user.manager_id,
        "created_at": user.created_at.isoformat() if user.created_at else None,
    }


@router.get("/", dependencies=_driver_guard(view_only=True))
async def list_drivers(
    db: AsyncSession = Depends(get_db_async),
    search: Optional[str] = Query(None),
    active_only: bool = Query(False),
    limit: int = Query(200, ge=1, le=500),
) -> Dict[str, Any]:
    stmt = select(User).where(func.lower(User.role) == "driver")
    if hasattr(User, "is_deleted"):
        stmt = stmt.where(User.is_deleted.is_(False))
    if active_only:
        stmt = stmt.where(User.is_active.is_(True))
    if search:
        like_value = f"%{search.strip()}%"
        stmt = stmt.where(
            or_(
                User.email.ilike(like_value),
                User.full_name.ilike(like_value),
                User.username.ilike(like_value),
                User.phone_number.ilike(like_value),
            )
        )
    stmt = stmt.order_by(User.created_at.desc()).limit(limit)
    result = await db.execute(stmt)
    drivers = [_user_payload(user) for user in result.scalars().all()]
    return {"ok": True, "drivers": drivers}


@router.get("/{driver_id}", dependencies=_driver_guard(view_only=True))
async def get_driver(
    driver_id: int,
    db: AsyncSession = Depends(get_db_async),
) -> Dict[str, Any]:
    stmt = select(User).where(User.id == driver_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user or str(user.role or "").lower() != "driver":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Driver not found")
    return {"ok": True, "driver": _user_payload(user)}


@router.post("/", dependencies=_driver_guard(view_only=False))
async def create_driver(
    payload: DriverCreate,
    db: AsyncSession = Depends(get_db_async),
) -> Dict[str, Any]:
    email = payload.email.strip().lower()
    existing = await db.execute(select(User).where(func.lower(User.email) == email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already exists")

    user = User(
        email=email,
        full_name=payload.full_name,
        phone_number=payload.phone_number,
        company=payload.company,
        country=payload.country,
        user_type=payload.user_type,
        manager_id=payload.manager_id,
        is_active=payload.is_active,
        role="driver",
    )
    if payload.password:
        user.hashed_password = get_password_hash(payload.password)

    db.add(user)
    await db.commit()
    await db.refresh(user)
    return {"ok": True, "driver": _user_payload(user)}


@router.patch("/{driver_id}", dependencies=_driver_guard(view_only=False))
async def update_driver(
    driver_id: int,
    payload: DriverUpdate,
    db: AsyncSession = Depends(get_db_async),
) -> Dict[str, Any]:
    result = await db.execute(select(User).where(User.id == driver_id))
    user = result.scalar_one_or_none()
    if not user or str(user.role or "").lower() != "driver":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Driver not found")

    if payload.email:
        user.email = payload.email.strip().lower()
    if payload.full_name is not None:
        user.full_name = payload.full_name
    if payload.phone_number is not None:
        user.phone_number = payload.phone_number
    if payload.company is not None:
        user.company = payload.company
    if payload.country is not None:
        user.country = payload.country
    if payload.user_type is not None:
        user.user_type = payload.user_type
    if payload.manager_id is not None:
        user.manager_id = payload.manager_id
    if payload.is_active is not None:
        user.is_active = payload.is_active
    if payload.password:
        user.hashed_password = get_password_hash(payload.password)

    await db.commit()
    await db.refresh(user)
    return {"ok": True, "driver": _user_payload(user)}

