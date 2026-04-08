# File: backend/routes/user.py

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from math import ceil
from typing import Optional, List, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, EmailStr
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database.connection import get_db
from backend.models.user import User
from backend.security import require_roles

router = APIRouter(
    prefix="/admin/users",
    tags=["Admin Users"],
)


class UserCreate(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    company: Optional[str] = None
    country: Optional[str] = None
    user_type: Optional[str] = None
    phone_number: Optional[str] = None
    role: Optional[str] = "USER"
    is_active: Optional[bool] = True


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    company: Optional[str] = None
    country: Optional[str] = None
    user_type: Optional[str] = None
    phone_number: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None


class UserOut(BaseModel):
    id: int
    email: EmailStr
    full_name: Optional[str]
    company: Optional[str]
    country: Optional[str]
    user_type: Optional[str]
    phone_number: Optional[str]
    role: str
    is_active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


def _normalize_str(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    v = str(value).strip()
    return v or None


def _user_to_dict(user: User) -> Dict[str, Any]:
    created_at = user.created_at.isoformat() if user.created_at else None
    updated_at = user.updated_at.isoformat() if user.updated_at else None
    role_value = (user.role or "").upper() if hasattr(user, "role") else ""

    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "company": user.company,
        "country": user.country,
        "user_type": user.user_type,
        "phone_number": user.phone_number,
        "role": role_value or user.role,
        "is_active": user.is_active,
        "created_at": created_at,
        "updated_at": updated_at,
    }


def _apply_user_filters(
    stmt,
    *,
    role: Optional[str],
    active_only: bool,
    search: Optional[str],
):
    if hasattr(User, "is_deleted"):
        stmt = stmt.where(User.is_deleted.is_(False))

    if role:
        role_value = role.strip().lower()
        if role_value:
            stmt = stmt.where(func.lower(User.role) == role_value)

    if active_only:
        stmt = stmt.where(User.is_active.is_(True))

    if search:
        search_value = search.strip()
        if search_value:
            like_value = f"%{search_value}%"
            stmt = stmt.where(
                or_(
                    User.email.ilike(like_value),
                    User.full_name.ilike(like_value),
                    User.username.ilike(like_value),
                    User.company.ilike(like_value),
                )
            )

    return stmt


@router.get("/", response_model=List[UserOut])
async def list_users(
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(require_roles(["admin"])),
):
    result = await db.execute(select(User).order_by(User.id))
    users = result.scalars().all()
    return users


@router.get("", response_model=List[UserOut], include_in_schema=False)
async def list_users_no_slash(
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(require_roles(["admin"])),
):
    return await list_users(db=db, admin=admin)


@router.get("/list")
async def list_users_paged(
    page: int = 1,
    limit: int = 20,
    role: Optional[str] = None,
    active_only: bool = True,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(require_roles(["admin"])),
):
    safe_page = max(int(page), 1)
    safe_limit = max(min(int(limit), 100), 1)

    base_stmt = select(User)
    base_stmt = _apply_user_filters(
        base_stmt,
        role=role,
        active_only=active_only,
        search=search,
    )

    count_stmt = select(func.count()).select_from(base_stmt.subquery())
    total = int((await db.execute(count_stmt)).scalar() or 0)
    total_pages = int(ceil(total / safe_limit)) if total else 0

    data_stmt = base_stmt.order_by(User.id).offset((safe_page - 1) * safe_limit).limit(safe_limit)
    result = await db.execute(data_stmt)
    users = result.scalars().all()

    return {
        "users": [_user_to_dict(user) for user in users],
        "total": total,
        "page": safe_page,
        "total_pages": total_pages,
    }


@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_user(
    payload: UserCreate,
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(require_roles(["admin"])),
):
    email = payload.email.lower().strip()

    # Check if user already exists
    result = await db.execute(select(User).where(User.email == email))
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )

    role_value = (payload.role or "user").strip().lower()

    user = User(
        email=email,
        full_name=_normalize_str(payload.full_name) or email,
        company=_normalize_str(payload.company),
        country=_normalize_str(payload.country),
        user_type=_normalize_str(payload.user_type) or "Freight Broker",
        phone_number=_normalize_str(payload.phone_number),
        role=role_value,
        is_active=True if payload.is_active is None else bool(payload.is_active),
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@router.post("/create", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_user_alias(
    payload: UserCreate,
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(require_roles(["admin"])),
):
    return await create_user(payload=payload, db=db, admin=admin)


@router.put("/{user_id}", response_model=UserOut)
async def update_user(
    user_id: int,
    payload: UserUpdate,
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(require_roles(["admin"])),
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if payload.full_name is not None:
        user.full_name = _normalize_str(payload.full_name) or user.full_name

    if payload.company is not None:
        user.company = _normalize_str(payload.company) or user.company

    if payload.country is not None:
        user.country = _normalize_str(payload.country) or user.country

    if payload.user_type is not None:
        user.user_type = _normalize_str(payload.user_type) or user.user_type

    if payload.phone_number is not None:
        user.phone_number = _normalize_str(payload.phone_number) or user.phone_number

    if payload.role is not None:
        user.role = payload.role.strip().lower()

    if payload.is_active is not None:
        user.is_active = bool(payload.is_active)

    await db.commit()
    await db.refresh(user)
    return user


@router.put("/update/{user_id}", response_model=UserOut)
async def update_user_alias(
    user_id: int,
    payload: UserUpdate,
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(require_roles(["admin"])),
):
    return await update_user(user_id=user_id, payload=payload, db=db, admin=admin)


@router.put("/disable/{user_id}", response_model=UserOut)
async def disable_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(require_roles(["admin"])),
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user.is_active = False
    await db.commit()
    await db.refresh(user)
    return user


@router.put("/enable/{user_id}", response_model=UserOut)
async def enable_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(require_roles(["admin"])),
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user.is_active = True
    await db.commit()
    await db.refresh(user)
    return user


@router.get("/statistics/summary")
async def user_statistics_summary(
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(require_roles(["admin"])),
):
    conditions = []
    if hasattr(User, "is_deleted"):
        conditions.append(User.is_deleted.is_(False))

    total_stmt = select(func.count(User.id))
    if conditions:
        total_stmt = total_stmt.where(*conditions)
    total_users = int((await db.execute(total_stmt)).scalar() or 0)

    active_stmt = select(func.count(User.id)).where(User.is_active.is_(True))
    if conditions:
        active_stmt = active_stmt.where(*conditions)
    active_users = int((await db.execute(active_stmt)).scalar() or 0)

    inactive_stmt = select(func.count(User.id)).where(User.is_active.is_(False))
    if conditions:
        inactive_stmt = inactive_stmt.where(*conditions)
    inactive_users = int((await db.execute(inactive_stmt)).scalar() or 0)

    cutoff = datetime.now(timezone.utc) - timedelta(days=7)
    new_stmt = select(func.count(User.id)).where(User.created_at >= cutoff)
    if conditions:
        new_stmt = new_stmt.where(*conditions)
    new_users_last_7_days = int((await db.execute(new_stmt)).scalar() or 0)

    role_stmt = select(User.role, func.count(User.id)).group_by(User.role)
    if conditions:
        role_stmt = role_stmt.where(*conditions)
    role_rows = (await db.execute(role_stmt)).all()
    by_role = {str(role or "unknown").upper(): int(count or 0) for role, count in role_rows}

    country_stmt = select(User.country, func.count(User.id)).group_by(User.country)
    if conditions:
        country_stmt = country_stmt.where(*conditions)
    country_rows = (await db.execute(country_stmt)).all()
    by_country = {str(country or "unknown"): int(count or 0) for country, count in country_rows}

    return {
        "summary": {
            "total_users": total_users,
            "active_users": active_users,
            "inactive_users": inactive_users,
            "new_users_last_7_days": new_users_last_7_days,
        },
        "distribution": {
            "by_role": by_role,
            "by_country": by_country,
        },
    }


@router.get("/{user_id}")
async def get_user_by_id(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(require_roles(["admin"])),
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    now = datetime.now(timezone.utc)
    created_at = user.created_at or now
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)

    account_age_days = max((now - created_at).days, 0)
    return {
        "user": _user_to_dict(user),
        "statistics": {
            "shipments_count": 0,
            "account_age_days": account_age_days,
        },
    }


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(require_roles(["admin"])),
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    await db.delete(user)
    await db.commit()
    return None
