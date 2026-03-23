
from __future__ import annotations
from typing import Optional, Dict

import secrets
import string

from fastapi import APIRouter, HTTPException, Body, Depends, status
from backend.auth.rbac_middleware import require_permission
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.services.portal_requests_store import (
    list_portal_requests,
    get_portal_request_by_id,
    update_portal_request_status,
    delete_portal_request,
    list_admin_notifications,
    get_request_audit_log,
    log_audit_action,
)
from backend.services.tms_access_store import grant_tms_access
from backend.utils.email_utils import send_bot_email, send_admin_notification
from backend.models.user import User
from backend.security.hashing import get_password_hash
from backend.config import settings

# --- DB dependency: get_db_async ---
try:
    from backend.database.config import get_db_async  # type: ignore
except Exception:
    try:
        from backend.core.db_config import get_db_async  # type: ignore
    except Exception:
        async def get_db_async() -> AsyncSession:  # type: ignore
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database dependency not available",
            )

portal_router = APIRouter(prefix="/admin/portal", tags=["admin", "portal"], include_in_schema=True)
portal_router_v1 = APIRouter(prefix="/api/v1/admin/portal", tags=["admin", "portal"], include_in_schema=True)
router = portal_router


def _generate_password(length: int = 14) -> str:
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return "".join(secrets.choice(alphabet) for _ in range(length))


def _login_url() -> str:
    base = (getattr(settings, "FRONTEND_URL", "") or "").rstrip("/")
    return f"{base}/login" if base else "http://127.0.0.1:5173/login"


@router.get("/requests")
async def admin_list_requests(limit: int = 100, status: Optional[str] = None):
    return await list_portal_requests(limit=limit, status=status)


@router.delete("/requests/{request_id}", status_code=204)
async def admin_delete_portal_request(request_id: int, _=Depends(require_permission("requests.delete"))):
    deleted = await delete_portal_request(id=request_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Request not found")
    return None


@portal_router_v1.get("/requests")
async def admin_list_requests_v1(limit: int = 100, status: Optional[str] = None):
    return await admin_list_requests(limit=limit, status=status)


@router.post("/requests/{req_id}/approve")
async def admin_approve_request(req_id: int, db: AsyncSession = Depends(get_db_async), _=Depends(require_permission("requests.approve"))):
    rec = await get_portal_request_by_id(req_id)
    if not rec:
        raise HTTPException(status_code=404, detail={"error": "not_found"})

    if rec.get("status") == "approved":
        return {"ok": True, "status": "approved", "message": "Already approved"}

    email_raw = (rec.get("email") or "").strip()
    if not email_raw:
        raise HTTPException(status_code=400, detail="Request email is missing")

    email = email_raw.lower()
    raw_password = None

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user:
        raw_password = _generate_password()
        user = User(
            email=email,
            full_name=rec.get("full_name") or email_raw,
            company=rec.get("company"),
            country=rec.get("country"),
            user_type=rec.get("user_type"),
            phone_number=rec.get("mobile"),
            role="user",
            is_active=True,
            hashed_password=get_password_hash(raw_password),
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

    await update_portal_request_status(req_id, "approved", decided_by="admin")

    # Grant TMS access if requested
    if rec.get("system") in ("tms", "both"):
        await grant_tms_access(email=rec["email"], granted_by="admin", notes=f"Auto-granted on portal approval (req {req_id})")

    # Notify user
    if email_raw:
        system_label = str(rec.get("system") or "standard").upper()
        login_url = _login_url()
        onboarding_link = "https://your-domain.com/tms-onboarding"  # Adjust as needed
        if raw_password:
            body = f"""<!DOCTYPE html>
<html>
  <body style="margin:0;padding:24px;font-family:Arial,sans-serif;background-color:#0b1220;color:#e2e8f0;">
    <h2 style="margin:0 0 12px;color:#ffffff;">Access Approved</h2>
    <p style="margin:0 0 12px;">Your portal access request has been approved.</p>
    <p style="margin:0 0 12px;">Login URL: {login_url}</p>
    <p style="margin:0 0 12px;">Email: {email_raw}</p>
    <p style="margin:0 0 12px;">Temporary password: {raw_password}</p>
    <p style="margin:0 0 12px;">System Access: {system_label}</p>
    <p style="margin:0 0 16px;">If you requested TMS access, start here: {onboarding_link}</p>
    <p style="margin:0;color:#cbd5e1;">Please change your password after logging in.</p>
  </body>
</html>"""
        else:
            body = f"""<!DOCTYPE html>
<html>
  <body style="margin:0;padding:24px;font-family:Arial,sans-serif;background-color:#0b1220;color:#e2e8f0;">
    <h2 style="margin:0 0 12px;color:#ffffff;">Access Approved</h2>
    <p style="margin:0 0 12px;">Your portal access request has been approved.</p>
    <p style="margin:0 0 12px;">Login URL: {login_url}</p>
    <p style="margin:0 0 12px;">System Access: {system_label}</p>
    <p style="margin:0;color:#cbd5e1;">An account already exists for this email. If you forgot your password, use the reset link on the login page.</p>
  </body>
</html>"""
        send_bot_email(
            bot_name="admin",
            subject="GTS Portal Access Approved",
            body=body,
            to=[email_raw],
            html=True,
        )

    # Notify admin
    send_admin_notification(
        subject=f"[GTS Portal] Request approved: {rec.get('full_name')} ({rec.get('company')})",
        body=f"Request ID {req_id} has been approved for {rec.get('system', 'standard')} access.",
        bot_name="admin",
    )

    await log_audit_action(
        request_id=req_id,
        action="request_approved",
        actor="admin",
        details={"system": rec.get("system")},
    )

    return {"ok": True, "status": "approved", "user_id": getattr(user, "id", None)}


@portal_router_v1.post("/requests/{req_id}/approve")
async def admin_approve_request_v1(req_id: int, db: AsyncSession = Depends(get_db_async)):
    return await admin_approve_request(req_id, db=db)


@router.post("/requests/{req_id}/deny")
async def admin_deny_request(
    req_id: int,
    payload: Dict[str, Optional[str]] = Body(default={}),
    _=Depends(require_permission("requests.deny")),
):
    rec = await get_portal_request_by_id(req_id)
    if not rec:
        raise HTTPException(status_code=404, detail={"error": "not_found"})

    rejection_code = (payload or {}).get("rejection_code")
    rejection_message = (payload or {}).get("rejection_message") or (payload or {}).get("reason")
    await update_portal_request_status(
        req_id,
        "rejected",
        reason=rejection_message,
        rejection_code=rejection_code,
        decided_by="admin",
    )

    # Notify user
    if rec.get("email"):
        try:
            body = f"""<!DOCTYPE html>
<html>
  <body style="margin:0;padding:24px;font-family:Arial,sans-serif;background-color:#0b1220;color:#e2e8f0;">
    <h2 style="margin:0 0 12px;color:#ffffff;">Request Update</h2>
    <p style="margin:0 0 12px;">Your portal access request was not approved at this time.</p>
    <p style="margin:0 0 12px;">Reason: {rejection_message or 'N/A'}</p>
    <p style="margin:0;color:#cbd5e1;">You may re-apply after the cooldown period.</p>
  </body>
</html>"""
            send_bot_email(
                bot_name="admin",
                subject="GTS Portal Access Request Update",
                body=body,
                to=[rec["email"]],
                html=True,
            )
        except Exception:
            pass

    # Notify admin
    send_admin_notification(
        subject=f"[GTS Portal] Request rejected: {rec.get('full_name')} ({rec.get('company')})",
        body=f"Request ID {req_id} was rejected. Reason: {rejection_message or 'N/A'}",
        bot_name="admin",
    )

    await log_audit_action(
        request_id=req_id,
        action="request_rejected",
        actor="admin",
        details={"rejection_code": rejection_code, "rejection_message": rejection_message},
    )

    return {"ok": True}


@portal_router_v1.post("/requests/{req_id}/deny")
async def admin_deny_request_v1(
    req_id: int,
    payload: Dict[str, Optional[str]] = Body(default={}),
):
    return await admin_deny_request(req_id, payload=payload)
# backend/routes/admin_portal_requests.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Any, Optional
import os

# --- DB dependency: get_db_async ---
try:
    from backend.database.config import get_db_async  # type: ignore
except Exception:
    try:
        from backend.core.db_config import get_db_async  # type: ignore
    except Exception:
        async def get_db_async() -> AsyncSession:  # type: ignore
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database dependency not available",
            )

# --- Settings (with safe type for Pylance) ---
try:
    from backend.config import settings as _settings  # type: ignore
    settings: Any = _settings
except Exception:
    class _FallbackSettings:
        APP_NAME: str = os.getenv("APP_NAME", "Gabani Transport Solutions (GTS)")
        APP_ENV: str = os.getenv("APP_ENV", "development")
        ADMIN_EMAIL: str = os.getenv("ADMIN_EMAIL", "admin@example.com")

        CORS_ORIGINS: list[str] = [
            o.strip()
            for o in os.getenv("CORS_ORIGINS", "").split(",")
            if o.strip()
        ]

        RATE_LIMIT_ENABLED: bool = os.getenv(
            "RATE_LIMIT_ENABLED", "true"
        ).lower() in ("1", "true", "yes")
        RATE_LIMIT_REQUESTS: int = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
        RATE_LIMIT_WINDOW: int = int(os.getenv("RATE_LIMIT_WINDOW", "60"))

        REGISTRATION_DISABLED: bool = os.getenv(
            "REGISTRATION_DISABLED", "false"
        ).lower() in ("1", "true", "yes")
        REGISTRATION_DISABLED_DETAIL: str = os.getenv(
            "REGISTRATION_DISABLED_DETAIL",
            "Registration is temporarily closed. Please contact the administrator.",
        ).strip()
        REGISTRATION_REOPEN_DATE: Optional[str] = os.getenv("REGISTRATION_REOPEN_DATE")
        REGISTRATION_CONTACT_EMAIL: str = os.getenv("REGISTRATION_CONTACT_EMAIL", "")
        REQUIRE_EMAIL_VERIFICATION: bool = os.getenv(
            "REQUIRE_EMAIL_VERIFICATION", "false"
        ).lower() in ("1", "true", "yes")
        GTS_DEV_MODE: bool = os.getenv(
            "GTS_DEV_MODE", "true"
        ).lower() in ("1", "true", "yes")

        DATABASE_POOL_SIZE: int = int(os.getenv("DATABASE_POOL_SIZE", "10"))
        DATABASE_MAX_OVERFLOW: int = int(os.getenv("DATABASE_MAX_OVERFLOW", "20"))

    settings: Any = _FallbackSettings()

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])


@router.get("/dashboard")
async def get_admin_dashboard(db: AsyncSession = Depends(get_db_async)):
    """
    Admin dashboard statistics and quick DB connectivity test.
    """
    try:
        result = await db.execute(text("SELECT 1 AS test"))
        test_result = result.scalar()

        return {
            "status": "success",
            "data": {
                "database": "connected" if test_result == 1 else "disconnected",
                "test_result": test_result,
                "message": "Admin dashboard is operational",
                "endpoints": {
                    "health": "/api/v1/admin/health",
                    "test_db": "/api/v1/admin/test-db",
                    "config": "/api/v1/admin/config",
                },
            },
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}",
        ) from e


@router.get("/health")
async def admin_health_check(db: AsyncSession = Depends(get_db_async)):
    """
    Admin-specific health check.
    """
    try:
        await db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "service": "admin-api",
            "database": "connected",
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "admin-api",
            "database": "disconnected",
            "error": str(e),
        }


@router.get("/test-db")
async def test_database_connection(db: AsyncSession = Depends(get_db_async)):
    """
    Explicit database connectivity test with DB/server timestamps.
    """
    try:
        import datetime

        result = await db.execute(text("SELECT NOW() AS current_time"))
        db_time = result.scalar()

        return {
            "success": True,
            "message": "Database connection successful",
            "database_time": str(db_time),
            "server_time": str(datetime.datetime.utcnow()),
            "timezone": "UTC",
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Database connection failed: {str(e)}",
            "troubleshooting": [
                "Check DATABASE_URL / ASYNC_DATABASE_URL in .env file",
                "Verify database server is running",
                "Check firewall settings",
                "Verify credentials (user/password/db/host/port)",
            ],
        }


@router.get("/config")
async def get_admin_config():
    """
    Non-sensitive backend configuration snapshot for admin UI.
    """
    return {
        "app_name": getattr(settings, "APP_NAME", "Gabani Transport Solutions (GTS)"),
        "environment": getattr(settings, "APP_ENV", "development"),
        "admin_email": getattr(settings, "ADMIN_EMAIL", "admin@example.com"),
        "cors_origins": getattr(settings, "CORS_ORIGINS", []),
        "rate_limiting": {
            "enabled": getattr(settings, "RATE_LIMIT_ENABLED", True),
            "requests": getattr(settings, "RATE_LIMIT_REQUESTS", 100),
            "window": getattr(settings, "RATE_LIMIT_WINDOW", 60),
        },
        "features": {
            "registration_enabled": not getattr(settings, "REGISTRATION_DISABLED", False),
            "registration_disabled": getattr(settings, "REGISTRATION_DISABLED", False),
            "registration_reopen_date": getattr(settings, "REGISTRATION_REOPEN_DATE", None),
            "registration_message": getattr(
                settings,
                "REGISTRATION_DISABLED_DETAIL",
                "Registration is temporarily closed.",
            ),
            "registration_contact_email": getattr(settings, "REGISTRATION_CONTACT_EMAIL", None),
            "email_verification": getattr(settings, "REQUIRE_EMAIL_VERIFICATION", False),
            "dev_mode": getattr(settings, "GTS_DEV_MODE", True),
        },
        "database": {
            "pool_size": getattr(settings, "DATABASE_POOL_SIZE", 10),
            "max_overflow": getattr(settings, "DATABASE_MAX_OVERFLOW", 20),
        },
    }


@router.get("/notifications")
async def get_admin_notifications(limit: int = 50, unread_only: bool = False):
    """Get admin notifications for portal requests"""
    notifications = await list_admin_notifications(limit=limit, unread_only=unread_only)
    return {
        "notifications": notifications,
        "total": len(notifications),
        "unread_count": sum(1 for n in notifications if not n.get("read"))
    }


@portal_router.get("/notifications")
async def get_admin_notifications_portal(limit: int = 50, unread_only: bool = False):
    return await get_admin_notifications(limit=limit, unread_only=unread_only)


@portal_router_v1.get("/notifications")
async def get_admin_notifications_portal_v1(limit: int = 50, unread_only: bool = False):
    return await get_admin_notifications(limit=limit, unread_only=unread_only)


@router.get("/requests/{req_id}/audit-log")
async def get_request_audit(req_id: int):
    """Get audit log for a specific portal request"""
    rec = await get_portal_request_by_id(req_id)
    if not rec:
        raise HTTPException(status_code=404, detail={"error": "not_found"})
    
    audit_log = await get_request_audit_log(req_id)
    
    return {
        "request_id": req_id,
        "request": rec,
        "audit_log": audit_log,
        "total_actions": len(audit_log)
    }


@portal_router.get("/requests/{req_id}/audit-log")
async def get_request_audit_portal(req_id: int):
    return await get_request_audit(req_id)


@portal_router_v1.get("/requests/{req_id}/audit-log")
async def get_request_audit_portal_v1(req_id: int):
    return await get_request_audit(req_id)


# Export a combined router that includes both portal and admin API routes.
admin_api_router = router
combined_router = APIRouter()
combined_router.include_router(portal_router)
combined_router.include_router(portal_router_v1)
combined_router.include_router(admin_api_router)
router = combined_router

__all__ = ["router"]
