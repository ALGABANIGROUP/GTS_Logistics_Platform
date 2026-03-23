from __future__ import annotations

import asyncio
import logging
import os
import shutil
import uuid
from pathlib import Path
from typing import Any, Dict
from datetime import datetime

from fastapi import APIRouter, Body, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

from backend.services.platform_settings_store import (
    get_platform_settings,
    update_platform_settings,
    _get_platform_settings_raw,
)
from backend.services.platform_webhook_dispatcher import dispatch_platform_webhook
from backend.security.auth import get_current_user
from backend.utils.email_utils import send_email

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

try:
    from backend.services.portal_requests_store import log_audit_action  # type: ignore
except Exception:
    log_audit_action = None  # type: ignore

# Create router with /api/v1 prefix (matching frontend expectations)
router = APIRouter(prefix="/api/v1/admin/platform-settings", tags=["admin", "platform-settings"])
public_router = APIRouter(prefix="/api/v1/platform-settings", tags=["platform-settings"])
UPLOAD_BASE_DIR = Path("uploads")
MAX_FILE_SIZE = 5 * 1024 * 1024
ALLOWED_UPLOAD_EXTENSIONS = {".png", ".jpg", ".jpeg", ".svg", ".webp"}


def _resolve_platform_tenant(current_user: Dict[str, Any] | None) -> tuple[str | None, str | None]:
    if not current_user:
        return None, None
    tenant_id = current_user.get("tenant_id") or current_user.get("id")
    tenant_type = current_user.get("user_type") or current_user.get("system_type") or "company"
    return (str(tenant_id), str(tenant_type)) if tenant_id is not None else (None, str(tenant_type))


def _get_tenant_upload_dir(tenant_id: str, subdir: str) -> Path:
    target = UPLOAD_BASE_DIR / str(tenant_id) / subdir
    target.mkdir(parents=True, exist_ok=True)
    return target


def _validate_upload_file(file: UploadFile) -> tuple[bool, str]:
    ext = Path(file.filename or "").suffix.lower()
    if ext not in ALLOWED_UPLOAD_EXTENSIONS:
        allowed = ", ".join(sorted(ALLOWED_UPLOAD_EXTENSIONS))
        return False, f"Invalid file type. Allowed: {allowed}"

    try:
        file.file.seek(0, os.SEEK_END)
        size = file.file.tell()
        file.file.seek(0)
    except Exception:
        size = 0

    if size > MAX_FILE_SIZE:
        return False, f"File too large. Max size: {MAX_FILE_SIZE // 1024 // 1024}MB"

    return True, ""


async def _delete_old_upload(relative_url: str | None) -> None:
    if not relative_url or not str(relative_url).startswith("/uploads/"):
        return
    try:
        relative_path = str(relative_url).replace("/uploads/", "", 1)
        file_path = UPLOAD_BASE_DIR / relative_path
        if file_path.exists() and file_path.is_file():
            file_path.unlink()
    except Exception as exc:
        logger.warning("Failed to delete old upload %s: %s", relative_url, exc)


@public_router.get("/branding")
async def get_public_branding(
    db: AsyncSession = Depends(get_db_async),
    tenant_id: str | None = Query(default=None),
):
    """Get public platform branding (name and logo) - no auth required"""
    try:
        settings = await get_platform_settings(db, tenant_id=tenant_id)
        general = settings.get("general", {})
        branding = settings.get("branding", {})
        
        return {
            "platformName": general.get("platformName") or branding.get("platformName") or "Gabani Transport Solutions",
            "platformLogo": general.get("platformLogo") or branding.get("logoUrl") or "",
            "tenantId": tenant_id,
        }
    except Exception as e:
        # Return defaults on error
        return {
            "platformName": "Gabani Transport Solutions",
            "platformLogo": "",
            "tenantId": tenant_id,
        }


@router.get("/branding")
async def get_my_branding(
    db: AsyncSession = Depends(get_db_async),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    tenant_id, _tenant_type = _resolve_platform_tenant(current_user)
    settings = await get_platform_settings(db, tenant_id=tenant_id)
    general = settings.get("general", {})
    branding = settings.get("branding", {})
    return {
        "platformName": general.get("platformName") or branding.get("platformName") or "Gabani Transport Solutions",
        "platformLogo": general.get("platformLogo") or branding.get("logoUrl") or "",
        "tenantId": tenant_id,
    }


@router.get("")
async def read_platform_settings(
    db: AsyncSession = Depends(get_db_async),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Get platform settings"""
    tenant_id, _tenant_type = _resolve_platform_tenant(current_user)
    settings = await get_platform_settings(db, tenant_id=tenant_id)
    general = settings.get("general", {})
    branding = settings.get("branding", {})
    settings["tenant"] = {
        "tenantId": tenant_id,
        "tenantType": _tenant_type,
        "companyName": current_user.get("company") or general.get("platformName") or branding.get("platformName"),
    }
    return settings


@router.put("")
async def write_platform_settings(
    payload: Dict[str, Any] = Body(default={}),
    db: AsyncSession = Depends(get_db_async),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Update platform settings"""
    tenant_id, tenant_type = _resolve_platform_tenant(current_user)
    updated = await update_platform_settings(
        db,
        payload,
        updated_by=current_user.get("email") or "admin",
        tenant_id=tenant_id,
        tenant_type=tenant_type,
    )
    updated["tenant"] = {
        "tenantId": tenant_id,
        "tenantType": tenant_type,
        "companyName": current_user.get("company")
        or updated.get("general", {}).get("platformName")
        or updated.get("branding", {}).get("platformName"),
    }
    
    # Invalidate settings cache if technical or database settings were updated
    if "technical" in payload or "database" in payload:
        try:
            from backend.utils.technical_settings import invalidate_cache
            invalidate_cache()
            logger.info("Technical settings cache invalidated")
        except Exception:
            pass
    
    if log_audit_action:
        try:
            await log_audit_action(
                request_id=None,
                action="platform_settings_updated",
                actor="admin",
                details={"keys": list(payload.keys())},
                session=db,
            )
        except Exception:
            pass

    try:
        raw_settings = await _get_platform_settings_raw(db, tenant_id=tenant_id)
        integrations = raw_settings.get("integrations", {})
        webhook_url = str(integrations.get("webhookUrl") or "").strip()
        webhook_secret = str(integrations.get("webhookSecret") or "")
        if webhook_url:
            event_data = {
                "updated_keys": list(payload.keys()),
                "source": "platform-settings",
                "tenant_id": tenant_id,
                "tenant_type": tenant_type,
            }
            asyncio.create_task(
                dispatch_platform_webhook(
                    url=webhook_url,
                    secret=webhook_secret,
                    event_type="platform.settings.updated",
                    data=event_data,
                )
            )
    except Exception as exc:
        logger.warning("Webhook dispatch skipped: %s", exc)
    return updated


@router.post("/upload-logo")
async def upload_tenant_logo(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db_async),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    tenant_id, tenant_type = _resolve_platform_tenant(current_user)
    if not tenant_id:
        raise HTTPException(status_code=400, detail="Tenant ID not found")

    is_valid, error_message = _validate_upload_file(file)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_message)

    ext = Path(file.filename or "").suffix.lower()
    filename = f"logo_{uuid.uuid4().hex[:8]}{ext}"
    upload_dir = _get_tenant_upload_dir(tenant_id, "branding")
    file_path = upload_dir / filename

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    file_url = f"/uploads/{tenant_id}/branding/{filename}"
    settings = await get_platform_settings(db, tenant_id=tenant_id)
    old_logo = settings.get("branding", {}).get("logoUrl") or settings.get("general", {}).get("platformLogo")
    settings.setdefault("branding", {})
    settings.setdefault("general", {})
    settings["branding"]["logoUrl"] = file_url
    settings["general"]["platformLogo"] = file_url

    updated = await update_platform_settings(
        db,
        settings,
        updated_by=current_user.get("email") or "system",
        tenant_id=tenant_id,
        tenant_type=tenant_type,
    )
    await _delete_old_upload(old_logo)

    return {
        "success": True,
        "logoUrl": file_url,
        "tenantId": tenant_id,
        "message": "Logo uploaded successfully",
        "settings": updated,
    }


@router.delete("/logo")
async def delete_tenant_logo(
    db: AsyncSession = Depends(get_db_async),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    tenant_id, tenant_type = _resolve_platform_tenant(current_user)
    if not tenant_id:
        raise HTTPException(status_code=400, detail="Tenant ID not found")

    settings = await get_platform_settings(db, tenant_id=tenant_id)
    old_logo = settings.get("branding", {}).get("logoUrl") or settings.get("general", {}).get("platformLogo")
    settings.setdefault("branding", {})
    settings.setdefault("general", {})
    settings["branding"]["logoUrl"] = ""
    settings["general"]["platformLogo"] = ""

    updated = await update_platform_settings(
        db,
        settings,
        updated_by=current_user.get("email") or "system",
        tenant_id=tenant_id,
        tenant_type=tenant_type,
    )
    await _delete_old_upload(old_logo)

    return {
        "success": True,
        "tenantId": tenant_id,
        "message": "Logo deleted",
        "settings": updated,
    }


@router.post("/upload-background")
async def upload_tenant_background(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db_async),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    tenant_id, tenant_type = _resolve_platform_tenant(current_user)
    if not tenant_id:
        raise HTTPException(status_code=400, detail="Tenant ID not found")

    is_valid, error_message = _validate_upload_file(file)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_message)

    ext = Path(file.filename or "").suffix.lower()
    filename = f"background_{uuid.uuid4().hex[:8]}{ext}"
    upload_dir = _get_tenant_upload_dir(tenant_id, "backgrounds")
    file_path = upload_dir / filename

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    file_url = f"/uploads/{tenant_id}/backgrounds/{filename}"
    settings = await get_platform_settings(db, tenant_id=tenant_id)
    old_background = settings.get("branding", {}).get("backgroundImage")
    settings.setdefault("branding", {})
    settings["branding"]["backgroundImage"] = file_url

    updated = await update_platform_settings(
        db,
        settings,
        updated_by=current_user.get("email") or "system",
        tenant_id=tenant_id,
        tenant_type=tenant_type,
    )
    await _delete_old_upload(old_background)

    return {
        "success": True,
        "backgroundUrl": file_url,
        "tenantId": tenant_id,
        "message": "Background uploaded successfully",
        "settings": updated,
    }


@router.delete("/background")
async def delete_tenant_background(
    db: AsyncSession = Depends(get_db_async),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    tenant_id, tenant_type = _resolve_platform_tenant(current_user)
    if not tenant_id:
        raise HTTPException(status_code=400, detail="Tenant ID not found")

    settings = await get_platform_settings(db, tenant_id=tenant_id)
    old_background = settings.get("branding", {}).get("backgroundImage")
    settings.setdefault("branding", {})
    settings["branding"]["backgroundImage"] = ""

    updated = await update_platform_settings(
        db,
        settings,
        updated_by=current_user.get("email") or "system",
        tenant_id=tenant_id,
        tenant_type=tenant_type,
    )
    await _delete_old_upload(old_background)

    return {
        "success": True,
        "tenantId": tenant_id,
        "message": "Background deleted",
        "settings": updated,
    }


@router.post("/trigger-backup")
async def trigger_manual_backup():
    """Manually trigger database backup"""
    try:
        from backend.utils.backup_scheduler import trigger_manual_backup
        await trigger_manual_backup()
        return {
            "success": True,
            "message": "Backup triggered successfully",
            "note": "Check server logs for backup status"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to trigger backup: {str(e)}"
        )


@router.get("/cache-stats")
async def get_cache_statistics():
    """Get application cache statistics"""
    try:
        from backend.utils.cache_decorator import get_cache_stats
        stats = get_cache_stats()
        return {
            "success": True,
            "cache": stats
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@router.post("/clear-cache")
async def clear_application_cache():
    """Clear all application cache"""
    try:
        from backend.utils.cache_decorator import clear_cache
        clear_cache()
        return {
            "success": True,
            "message": "Application cache cleared successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear cache: {str(e)}"
        )


@router.post("/test-email")
async def test_email_configuration(
    test_email: str = Body(..., embed=True),
    db: AsyncSession = Depends(get_db_async),
):
    """Test email configuration by sending a test email"""
    try:
        from backend.services.email_settings_provider import get_email_settings, is_email_configured

        # Check if email is configured
        if not await is_email_configured(db):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is not configured. Please configure SMTP settings first."
            )
        
        # Get email settings
        email_config = await get_email_settings(db)
        
        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <h2>Email Configuration Test</h2>
            <p>This is a test email from GTS Logistics Platform.</p>
            <p><strong>Configuration Details:</strong></p>
            <ul>
                <li>SMTP Server: {email_config.get('smtpServer')}</li>
                <li>SMTP Port: {email_config.get('smtpPort')}</li>
                <li>From: {email_config.get('fromEmail')}</li>
                <li>SSL/TLS: {'Enabled' if email_config.get('useTLS') else 'Disabled'}</li>
            </ul>
            <p>If you received this email, your email configuration is working correctly!</p>
            <hr>
            <p style="color: #666; font-size: 12px;">
                GTS Logistics Platform<br>
                {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}
            </p>
        </body>
        </html>
        """

        smtp_password = email_config.get('smtpPassword') or os.getenv("EMAIL_SHARED_PASSWORD") or os.getenv("SMTP_PASSWORD")
        sent = send_email(
            subject="GTS Platform - Email Configuration Test",
            body=body,
            to=[test_email],
            html=True,
            from_email=email_config.get("fromEmail"),
            smtp_user=email_config.get("fromEmail"),
            smtp_password=smtp_password,
            smtp_host=email_config.get("smtpServer"),
            smtp_port=email_config.get("smtpPort"),
            smtp_secure=bool(email_config.get("useTLS")),
        )

        if not sent:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send test email with the configured SMTP settings."
            )

        logger.info(f"Test email sent successfully to {test_email}")
        return {
            "success": True,
            "message": f"Test email sent successfully to {test_email}",
            "config": {
                "smtpServer": email_config.get('smtpServer'),
                "smtpPort": email_config.get('smtpPort'),
                "fromEmail": email_config.get('fromEmail'),
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Test email failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to test email configuration: {str(e)}"
        )


@router.post("/test-webhook")
async def test_webhook_configuration(
    db: AsyncSession = Depends(get_db_async),
):
    """Send a test payload to the configured outbound webhook."""
    raw_settings = await _get_platform_settings_raw(db)
    integrations = raw_settings.get("integrations", {})
    webhook_url = str(integrations.get("webhookUrl") or "").strip()
    webhook_secret = str(integrations.get("webhookSecret") or "")

    if not webhook_url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Webhook URL is not configured",
        )

    ok, detail, status_code = await dispatch_platform_webhook(
        url=webhook_url,
        secret=webhook_secret,
        event_type="platform.webhook.test",
        data={"status": "test"},
    )

    if not ok:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Webhook test failed: {detail}",
        )

    return {
        "success": True,
        "message": "Webhook test delivered",
        "status_code": status_code,
    }


__all__ = ["router"]
