"""
System Admin Bot service for immediate user-management execution.

This service centralizes admin user mutations so the admin UI, future bot flows,
and API routes all use the same logic path without delayed schedulers.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.user import User
from backend.security.passwords import hash_password

logger = logging.getLogger(__name__)


class SystemAdminBot:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.bot_name = "system_admin_bot"
        self.bot_version = "1.0.0"

    async def create_user(
        self,
        user_data: Dict[str, Any],
        *,
        created_by: Optional[int] = None,
    ) -> Tuple[bool, Optional[User], str]:
        try:
            email = str(user_data.get("email") or "").strip().lower()
            if not email:
                return False, None, "Email is required"

            existing = (
                await self.db.execute(select(User).where(func.lower(User.email) == email))
            ).scalars().first()
            if existing:
                return False, None, f"User with email {email} already exists"

            password = str(user_data.get("password") or "").strip()
            if not password:
                return False, None, "Password is required"

            user = User(
                email=email,
                full_name=user_data.get("full_name"),
                username=user_data.get("username"),
                phone_number=user_data.get("phone_number") or user_data.get("phone"),
                company=user_data.get("company"),
                country=user_data.get("country"),
                user_type=user_data.get("user_type"),
                manager_id=user_data.get("manager_id"),
                role=str(user_data.get("role") or "user").strip().lower(),
                assigned_bots=user_data.get("assigned_bots"),
                features=user_data.get("features"),
                is_active=bool(user_data.get("is_active", True)),
                is_banned=bool(user_data.get("is_banned", False)),
                ban_reason=user_data.get("ban_reason"),
                banned_until=user_data.get("banned_until"),
                hashed_password=hash_password(password),
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            self.db.add(user)
            await self.db.commit()
            await self.db.refresh(user)
            logger.info(
                "[%s] created user id=%s email=%s actor=%s",
                self.bot_name,
                user.id,
                user.email,
                created_by,
            )
            return True, user, f"User {user.email} created successfully"
        except Exception as exc:
            await self.db.rollback()
            logger.exception("[%s] create_user failed: %s", self.bot_name, exc)
            return False, None, f"Failed to create user: {exc}"

    async def get_user(self, user_id: int) -> Optional[User]:
        return await self.db.get(User, user_id)

    async def list_users(
        self,
        *,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[User]:
        stmt = select(User)
        conditions = []
        filters = filters or {}

        role = filters.get("role")
        if isinstance(role, str) and role:
            conditions.append(func.lower(User.role) == role.strip().lower())

        if filters.get("tenant_id"):
            conditions.append(User.tenant_id == filters["tenant_id"])

        is_active = filters.get("is_active")
        if isinstance(is_active, bool):
            conditions.append(User.is_active == is_active)

        search = filters.get("search")
        if isinstance(search, str) and search.strip():
            needle = f"%{search.strip()}%"
            conditions.append(
                or_(
                    User.email.ilike(needle),
                    User.full_name.ilike(needle),
                    User.username.ilike(needle),
                    User.phone_number.ilike(needle),
                )
            )

        if conditions:
            stmt = stmt.where(and_(*conditions))

        stmt = stmt.order_by(User.created_at.desc()).offset(offset).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def update_user(
        self,
        user_id: int,
        updates: Dict[str, Any],
        *,
        updated_by: Optional[int] = None,
    ) -> Tuple[bool, Optional[User], str]:
        try:
            user = await self.db.get(User, user_id)
            if not user:
                return False, None, f"User with ID {user_id} not found"

            for key, value in (updates or {}).items():
                if key == "password":
                    if value:
                        user.hashed_password = hash_password(str(value))
                    continue
                if key == "phone":
                    key = "phone_number"
                if key == "role_key":
                    key = "role"
                if key in {"assigned_bots", "features"} and value is not None and not isinstance(value, list):
                    value = list(value) if isinstance(value, (set, tuple)) else [value]
                if hasattr(user, key) and value is not None:
                    if key == "email":
                        value = str(value).strip().lower()
                    if key == "role":
                        value = str(value).strip().lower()
                    setattr(user, key, value)

            user.updated_at = datetime.now(timezone.utc)
            self.db.add(user)
            await self.db.commit()
            await self.db.refresh(user)
            logger.info(
                "[%s] updated user id=%s email=%s actor=%s",
                self.bot_name,
                user.id,
                user.email,
                updated_by,
            )
            return True, user, f"User {user.email} updated successfully"
        except Exception as exc:
            await self.db.rollback()
            logger.exception("[%s] update_user failed: %s", self.bot_name, exc)
            return False, None, f"Failed to update user: {exc}"

    async def delete_user(
        self,
        user_id: int,
        *,
        deleted_by: Optional[int] = None,
    ) -> Tuple[bool, str]:
        try:
            user = await self.db.get(User, user_id)
            if not user:
                return False, f"User with ID {user_id} not found"

            user.is_active = False
            user.is_deleted = True
            user.deleted_at = datetime.now(timezone.utc)
            user.updated_at = datetime.now(timezone.utc)
            self.db.add(user)
            await self.db.commit()
            logger.info(
                "[%s] deactivated user id=%s email=%s actor=%s",
                self.bot_name,
                user.id,
                user.email,
                deleted_by,
            )
            return True, f"User {user.email} deactivated successfully"
        except Exception as exc:
            await self.db.rollback()
            logger.exception("[%s] delete_user failed: %s", self.bot_name, exc)
            return False, f"Failed to deactivate user: {exc}"

    async def toggle_user_status(
        self,
        user_id: int,
        activate: bool,
        *,
        updated_by: Optional[int] = None,
    ) -> Tuple[bool, Optional[User], str]:
        return await self.update_user(
            user_id,
            {
                "is_active": activate,
                "is_deleted": False if activate else None,
                "deleted_at": None if activate else datetime.now(timezone.utc),
            },
            updated_by=updated_by,
        )

    async def bulk_create_users(self, users_data: List[Dict[str, Any]]) -> Tuple[int, List[str]]:
        success_count = 0
        errors: List[str] = []
        for payload in users_data:
            success, _user, message = await self.create_user(payload)
            if success:
                success_count += 1
            else:
                errors.append(f"{payload.get('email')}: {message}")
        return success_count, errors

    async def get_user_stats(self) -> Dict[str, Any]:
        total = await self.db.scalar(select(func.count(User.id))) or 0
        active = await self.db.scalar(select(func.count(User.id)).where(User.is_active.is_(True))) or 0
        admins = (
            await self.db.scalar(
                select(func.count(User.id)).where(func.lower(User.role).in_(["admin", "super_admin", "owner"]))
            )
            or 0
        )
        return {
            "total": int(total),
            "active": int(active),
            "inactive": int(total) - int(active),
            "admins": int(admins),
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "managed_by": self.bot_name,
        }
