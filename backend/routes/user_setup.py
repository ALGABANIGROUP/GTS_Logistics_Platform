from __future__ import annotations

from datetime import datetime
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.db_config import get_async_db
from backend.security.auth import get_current_user

router = APIRouter(prefix="/api/v1/user", tags=["User Setup"])


class UserSetupRequest(BaseModel):
    system_type: str
    subscription_tier: str
    role: str


def _extract_identity(current_user: Any) -> tuple[int | None, str | None]:
    if isinstance(current_user, dict):
        raw_id = current_user.get("id")
        email = current_user.get("email")
    else:
        raw_id = getattr(current_user, "id", None)
        email = getattr(current_user, "email", None)

    try:
        user_id = int(raw_id) if raw_id is not None else None
    except Exception:
        user_id = None
    return user_id, email


@router.post("/setup")
async def complete_user_setup(
    payload: UserSetupRequest,
    db: AsyncSession = Depends(get_async_db),
    current_user: Any = Depends(get_current_user),
) -> Dict[str, Any]:
    """Persist the initial system/plan/role selection for the current user."""
    user_id, email = _extract_identity(current_user)
    if user_id is None and not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to resolve the current user identity.",
        )

    where_clause = None
    params = {
        "system_type": payload.system_type,
        "subscription_tier": payload.subscription_tier,
        "role": payload.role,
        "updated_at": datetime.utcnow(),
    }
    if user_id is not None:
        where_clause = "id = :user_id"
        params["user_id"] = user_id
    elif email:
        where_clause = "lower(email) = lower(:email)"
        params["email"] = email

    if not where_clause:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to resolve the current user identity.",
        )

    stmt = text(
        f"""
        UPDATE users
        SET system_type = :system_type,
            subscription_tier = :subscription_tier,
            role = COALESCE(NULLIF(:role, ''), role),
            updated_at = :updated_at
        WHERE {where_clause}
        RETURNING id, email, full_name, role, system_type, subscription_tier, is_active
        """
    )

    try:
        result = await db.execute(
            stmt,
            params,
        )
        row = result.first()
        if not row:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        await db.commit()
    except HTTPException:
        raise
    except Exception as exc:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to complete setup: {exc}",
        ) from exc

    return {
        "success": True,
        "message": "Setup completed successfully",
        "redirect": "/dashboard",
        "user": {
            "id": row[0],
            "email": row[1],
            "full_name": row[2],
            "role": row[3],
            "system_type": row[4],
            "subscription_tier": row[5],
            "is_active": row[6],
        },
    }
