from __future__ import annotations

from fastapi import APIRouter, HTTPException, Depends
from backend.auth.rbac_middleware import require_permission

from backend.services.tms_access_store import (
    grant_tms_access,
    revoke_tms_access,
    check_tms_access,
    list_tms_access,
)

router = APIRouter(prefix="/admin/tms", tags=["admin", "tms"], include_in_schema=True)


@router.get("/access")
async def admin_list_tms_access(limit: int = 100, _=Depends(require_permission("tms.access_read"))):
    """List all users with TMS access."""
    return await list_tms_access(limit=limit)


@router.post("/access/{email}/grant")
async def admin_grant_tms_access(email: str, granted_by: str = "admin", notes: str = None, _=Depends(require_permission("tms.access_grant"))):
    """Grant TMS access to a user by email."""
    rec = await grant_tms_access(email=email, granted_by=granted_by, notes=notes)
    return {"ok": True, "record": rec}


@router.post("/access/{email}/revoke")
async def admin_revoke_tms_access(email: str, _=Depends(require_permission("tms.access_revoke"))):
    """Revoke TMS access from a user by email."""
    await revoke_tms_access(email)
    return {"ok": True}


@router.get("/access/{email}/check")
async def admin_check_tms_access(email: str, _=Depends(require_permission("tms.access_read"))):
    """Check if a user has TMS access."""
    has_access = await check_tms_access(email)
    return {"email": email, "has_tms_access": has_access}
