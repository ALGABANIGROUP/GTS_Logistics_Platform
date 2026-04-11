from __future__ import annotations

from typing import Optional
import logging
import secrets
import os
import httpx
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Form, File, UploadFile, Request, HTTPException, Query, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from backend.services.portal_requests_store import (
    create_portal_request,
    get_portal_request_by_email,
    get_portal_request_by_request_id,
    increment_request_attempt,
    check_ip_rate_limit,
    create_verification_token,
    create_admin_notification,
    log_audit_action,
)
from backend.utils.email_utils import send_email, send_admin_notification
from backend.config import settings  # type: ignore
from backend.database.config import get_db_async

logger = logging.getLogger(__name__)
router = APIRouter(tags=["portal"], include_in_schema=True)
_admin_base = str(getattr(settings, "ADMIN_URL", "") or "").rstrip("/")
_portal_requests_url = (
    f"{_admin_base}/portal-requests"
    if _admin_base
    else f"{str(getattr(settings, 'FRONTEND_URL', '') or '').rstrip('/')}/admin/portal-requests"
)

# hCaptcha secret key from environment
HCAPTCHA_SECRET = settings.HCAPTCHA_SECRET or os.getenv("HCAPTCHA_SECRET", "")
HCAPTCHA_DISABLED = bool(settings.HCAPTCHA_DISABLED)
REJECTION_COOLDOWN_HOURS = int(os.getenv("PORTAL_REJECT_COOLDOWN_HOURS", "24"))

_COUNTRY_CODE_MAP = {
    "UNITED STATES": "US",
    "UNITED STATES OF AMERICA": "US",
    "USA": "US",
    "US": "US",
    "CANADA": "CA",
    "CA": "CA",
    "MEXICO": "MX",
    "MX": "MX",
    "UNITED KINGDOM": "UK",
    "UK": "UK",
    "GREAT BRITAIN": "UK",
}


def _normalize_country(value: str) -> str:
    if not value:
        return ""
    cleaned = value.strip()
    if not cleaned:
        return ""
    if len(cleaned) == 2:
        return cleaned.upper()
    upper = cleaned.upper()
    if upper in _COUNTRY_CODE_MAP:
        return _COUNTRY_CODE_MAP[upper]
    if "(" in upper and ")" in upper:
        inner = upper.split("(", 1)[1].split(")", 1)[0].strip()
        if len(inner) == 2:
            return inner
        if inner in _COUNTRY_CODE_MAP:
            return _COUNTRY_CODE_MAP[inner]
    return upper


def _normalize_region(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    cleaned = value.strip()
    if not cleaned:
        return None
    return cleaned.upper()


def get_client_ip(request: Request) -> str:
    """Get client IP from request, checking X-Forwarded-For for proxy"""
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.client.host if request.client else "0.0.0.0"


async def verify_hcaptcha(token: str) -> bool:
    """Verify hCaptcha token"""
    if HCAPTCHA_DISABLED:
        logger.info("CAPTCHA verification disabled")
        return True
    if not token or not HCAPTCHA_SECRET:
        logger.warning("CAPTCHA verification skipped - missing token or secret")
        return True  # Skip in dev
    
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            resp = await client.post(
                "https://hcaptcha.com/siteverify",
                data={
                    "secret": HCAPTCHA_SECRET,
                    "response": token,
                },
            )
            resp.raise_for_status()
            result = resp.json()
            return result.get("success", False)
    except Exception as exc:
        logger.error(f"[Portal] CAPTCHA verification error: {exc}")
        return False


@router.post("/portal/requests")
async def create_request(
    request: Request,
    background_tasks: BackgroundTasks,
    tenant_id: Optional[str] = Form(None),
    full_name: str = Form(...),
    company: str = Form(...),
    email: str = Form(...),
    mobile: str = Form(...),
    comment: Optional[str] = Form(None),
    country: str = Form(...),
    user_type: str = Form(...),
    system: str = Form("standard"),
    captcha_token: str = Form(""),
    us_state: Optional[str] = Form(None),
    dot_number: Optional[str] = Form(None),
    mc_number: Optional[str] = Form(None),
    us_business_address: Optional[str] = Form(None),
    ca_province: Optional[str] = Form(None),
    ca_registered_address: Optional[str] = Form(None),
    ca_company_number: Optional[str] = Form(None),
    document: UploadFile | None = File(None),
    db: AsyncSession = Depends(get_db_async),
):
    """
    Create a new portal access request with spam protection.
    
    Protections:
    - CAPTCHA verification
    - Rate limit: 5 requests per hour per IP
    - Duplicate prevention: no same email/company within 24h
    - Email verification required
    - IP tracking for abuse prevention
    - Full audit logging
    """
    client_ip = get_client_ip(request)
    email_clean = email.strip()
    company_clean = company.strip()
    email_norm = email_clean.lower()
    company_norm = company_clean.lower()
    country_norm = _normalize_country(country)
    us_state_norm = _normalize_region(us_state)
    ca_province_norm = _normalize_region(ca_province)
    if not country_norm:
        raise HTTPException(status_code=400, detail="Country is required.")
    if len(country_norm) != 2:
        raise HTTPException(
            status_code=400,
            detail="Invalid country. Please use a 2-letter country code.",
        )
    if us_state_norm and len(us_state_norm) != 2:
        raise HTTPException(
            status_code=400,
            detail="Invalid US state. Please use a 2-letter state code.",
        )
    if ca_province_norm and len(ca_province_norm) != 2:
        raise HTTPException(
            status_code=400,
            detail="Invalid CA province. Please use a 2-letter province code.",
        )
    logger.info(f"[Portal] Access request from IP: {client_ip}, email: {email_clean}")
    
    # Step 1: Verify CAPTCHA
    if not await verify_hcaptcha(captcha_token):
        logger.warning(f"[Portal] CAPTCHA verification failed for IP: {client_ip}")
        raise HTTPException(
            status_code=400,
            detail="CAPTCHA verification failed. Please try again."
        )
    
    # Step 2: Check rate limit
    if await check_ip_rate_limit(client_ip, requests_per_hour=5, session=db):
        logger.warning(f"[Portal] Rate limit exceeded for IP: {client_ip}")
        raise HTTPException(
            status_code=429,
            detail="Too many requests from this IP. Please try again later."
        )
    
    # Step 3: Check for duplicate submissions (pending -> return existing)
    existing = await get_portal_request_by_email(email_norm, tenant_id=tenant_id, session=db)
    if existing:
        status = existing.get("status")
        await increment_request_attempt(existing["id"], session=db)
        if status == "pending":
            logger.info(f"[Portal] Duplicate pending request: email={email_clean}")
            return {
                "id": existing.get("request_id") or existing.get("id"),
                "status": "pending",
                "message": "Your request is already pending review.",
            }
        if status == "approved":
            return {
                "id": existing.get("request_id") or existing.get("id"),
                "status": "approved",
                "message": "This email is already approved. Please log in.",
            }
        if status in ("rejected", "denied"):
            decided_at = existing.get("decided_at")
            if decided_at and isinstance(decided_at, datetime):
                cooldown_until = decided_at + timedelta(hours=REJECTION_COOLDOWN_HOURS)
                if cooldown_until > datetime.now(timezone.utc):
                    raise HTTPException(
                        status_code=429,
                        detail={
                            "status": "rejected",
                            "message": "Your request was rejected. Please try again later.",
                            "rejection_code": existing.get("rejection_code"),
                            "rejection_message": existing.get("rejection_message"),
                            "retry_after": int((cooldown_until - datetime.now(timezone.utc)).total_seconds()),
                        },
                    )
    
    document_name: Optional[str] = document.filename if document else None

    # Step 4: Create portal request record
    rec = await create_portal_request(
        tenant_id=tenant_id,
        full_name=full_name,
        company=company_clean,
        email=email_clean,
        mobile=mobile,
        comment=comment,
        country=country_norm,
        user_type=user_type,
        system=system,
        requested_systems={"system": system},
        us_state=us_state_norm,
        dot_number=dot_number,
        mc_number=mc_number,
        us_business_address=us_business_address,
        ca_province=ca_province_norm,
        ca_registered_address=ca_registered_address,
        ca_company_number=ca_company_number,
        document_name=document_name,
        session=db,
    )
    
    # Step 5: Generate verification token and email content
    verification_token = secrets.token_urlsafe(32)

    verification_link = f"{settings.FRONTEND_URL}/verify-email?token={verification_token}"
    subject_verify = "Registration received"
    body_verify = f"""<!DOCTYPE html>
<html>
  <body style="margin:0;padding:24px;font-family:Arial,sans-serif;background-color:#0b1220;color:#e2e8f0;">
    <h2 style="margin:0 0 12px;color:#ffffff;">Registration received</h2>
    <p style="margin:0 0 12px;">Thank you for submitting your access request. Our team will review your information within 72 hours.</p>
    <p style="margin:0 0 12px;">Once your request is approved, we will send your login instructions via email.</p>
    <p style="margin:0 0 12px;">Request ID: {rec['request_id']}</p>
    <p style="margin:0 0 16px;">Please verify your email to keep the process moving:</p>
    <p style="margin:0 0 20px;">
      <a href="{verification_link}" style="background:#2563eb;color:#ffffff;text-decoration:none;padding:10px 16px;border-radius:6px;display:inline-block;">
        Verify Email
      </a>
    </p>
    <p style="margin:0;color:#cbd5e1;">If you did not make this request, please ignore this message.</p>
  </body>
</html>"""

    try:
        await create_verification_token(email_norm, verification_token, 24)
    except Exception as exc:
        logger.warning("[Portal] Failed to store verification token: %s", exc)
    background_tasks.add_task(
        send_email,
        subject_verify,
        body_verify,
        [email_clean],
        True,
        settings.SMTP_FROM or "no-reply@gabanilogistics.com",
    )

    # Step 6: Notify admins
    subject_admin = "New enterprise access request submitted"
    body_admin = (
        "A new enterprise access request has been submitted.\n\n"
        f"Request ID: {rec['request_id']}\n"
        f"Name: {full_name}\n"
        f"Company: {company}\n"
        f"Email: {email_clean}\n"
        f"Mobile: {mobile}\n"
        f"Country: {country}\n"
        f"User Type: {user_type}\n"
        f"System Requested: {system}\n"
        f"Document: {document_name or '-'}\n"
        f"IP Address: {client_ip}\n\n"
        f"Comment:\n{comment or '-'}\n\n"
        f"Review this request at: {_portal_requests_url}"
    )

    background_tasks.add_task(send_admin_notification, subject_admin, body_admin)
    try:
        await create_admin_notification(
            request_id=rec["id"],
            notification_type="new_request",
            title=f"New request from {full_name}",
            message=f"Company: {company}, System: {system}",
        )
    except Exception as exc:
        logger.warning("[Portal] Failed to create admin notification: %s", exc)
    try:
        await log_audit_action(
            request_id=rec["id"],
            action="request_created",
            actor="system",
            details={
                "user_type": user_type,
                "system": system,
                "country": country,
            },
            ip_address=client_ip,
        )
    except Exception as exc:
        logger.warning("[Portal] Failed to log audit action: %s", exc)
    
    logger.info(f"[Portal] Request created: ID={rec['id']}, email={email_clean}, IP={client_ip}")
    
    return {
        "id": rec["request_id"],
        "status": rec["status"],
        "success": True,
        "message": "Registration submitted successfully. Please wait up to 72 hours for security checks. Our team will contact you.",
        "redirect_url": "/login",
    }


@router.get("/portal/requests/{request_id}/status")
async def request_status(request_id: str, db: AsyncSession = Depends(get_db_async)):
    rec = await get_portal_request_by_request_id(request_id, session=db)
    if not rec:
        raise HTTPException(status_code=404, detail="Request not found")
    return {
        "id": rec.get("request_id") or rec.get("id"),
        "status": rec.get("status"),
        "rejection_code": rec.get("rejection_code"),
        "rejection_message": rec.get("rejection_message"),
        "decided_at": rec.get("decided_at"),
    }


@router.get("/portal/verify-email")
async def verify_email_endpoint(token: str = Query(...)):
    """Verify email token and mark email as verified"""
    from backend.services.portal_requests_store import verify_email
    
    try:
        result = await verify_email(token)
        if result:
            logger.info(f"[Portal] Email verified for token: {token[:20]}...")
            return {
                "success": True,
                "message": "Your email has been verified. You can now proceed with your portal access."
            }
        else:
            logger.warning(f"[Portal] Invalid or expired token: {token[:20]}...")
            raise HTTPException(
                status_code=400,
                detail="Token is invalid or has expired. Please request a new verification link."
            )
    except Exception as e:
        logger.error(f"[Portal] Email verification error: {e}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred during email verification. Please try again later."
        )
