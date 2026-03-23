import secrets
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database.session import get_async_session
from backend.models.user import User
from backend.security.auth import get_password_hash
from backend.utils.email_utils import send_email

api_router = APIRouter()

import os

MAIL_USERNAME = os.getenv("MAIL_USERNAME", "") or os.getenv("SMTP_USER", "")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "") or os.getenv("SMTP_PASSWORD", "")
MAIL_FROM = os.getenv("MAIL_FROM") or os.getenv("SMTP_FROM") or "no-reply@gabanilogistics.com"
MAIL_ADMIN = os.getenv("MAIL_ADMIN", "") or os.getenv("ADMIN_EMAIL", "")
ACTIVATION_BASE_URL = os.getenv("ACTIVATION_BASE_URL", "")


class RegisterPayload(BaseModel):
    email: EmailStr
    password: str


def send_welcome_email(user_email: str, user_name: str = "", activation_token: str | None = None) -> None:
    """
    Send welcome email with HTML + plain fallback.
    If SMTP env vars are not set, log and skip.
    """
    if not (MAIL_USERNAME and MAIL_PASSWORD):
        print(f"[register] MAIL_USERNAME/MAIL_PASSWORD not set; skipping email to {user_email}")
        return

    activation_link = None
    if activation_token and ACTIVATION_BASE_URL:
        activation_link = f"{ACTIVATION_BASE_URL.rstrip('/')}/{activation_token}"

    display_name = user_name or user_email.split("@")[0]

    html_body = f"""
    <html>
      <body style="font-family: Arial, sans-serif; color: #0f172a;">
        <h2 style="color:#0f172a;">Welcome {display_name}!</h2>
        <p>Registration successful! Please wait up to 72 hours for security checks. Our team will contact you shortly.</p>
        {f'<p style="margin-top:16px;"><a href="{activation_link}" style="color:#2563eb;">Activate your account</a></p>' if activation_link else ''}
        <p style="margin-top:24px; color:#475569;">If you did not sign up, please ignore this email.</p>
      </body>
    </html>
    """

    text_body = (
        f"Welcome {display_name}!\n\n"
        "Registration successful! Please wait up to 72 hours for security checks. "
        "Our team will contact you shortly.\n"
        f"{'Activate: ' + activation_link + chr(10) if activation_link else ''}"
        "If you did not sign up, please ignore this email."
    )

    try:
        send_email(
            subject="Welcome to GTS Logistics",
            body=html_body,
            to=[user_email],
            html=True,
            plain_text=text_body,
            from_email=MAIL_FROM,
        )
        print(f"[register] welcome email sent to {user_email}")
    except Exception as e:
        print(f"[register] Error sending email to {user_email}: {e}")
        if MAIL_ADMIN:
            try:
                send_email(
                    subject="Welcome email failed",
                    body=f"Failed to send welcome email to {user_email}: {e}",
                    to=[MAIL_ADMIN],
                    from_email=MAIL_FROM,
                )
            except Exception as e2:
                print(f"[register] Failed to notify admin: {e2}")


def send_admin_notification(user_email: str, user_name: str = "", role: str = "user") -> None:
    """
    Notify admin about a new signup. Skips if MAIL_ADMIN or SMTP creds missing.
    """
    if not (MAIL_ADMIN and MAIL_USERNAME and MAIL_PASSWORD):
        return

    display_name = user_name or user_email.split("@")[0]
    body = (
        "New user registration received:\n\n"
        f"Name: {display_name}\n"
        f"Email: {user_email}\n"
        f"Role: {role}\n\n"
        "Review this request at: http://localhost:5173/admin/portal-requests"
    )
    html = f"""
    <html>
      <body style="font-family: Arial, sans-serif; color: #0f172a;">
        <h3>New User Registration</h3>
        <ul>
          <li><strong>Name:</strong> {display_name}</li>
          <li><strong>Email:</strong> {user_email}</li>
          <li><strong>Role:</strong> {role}</li>
        </ul>
        <p>Review this request at: <a href="http://localhost:5173/admin/portal-requests">Admin Portal Requests</a></p>
      </body>
    </html>
    """
    send_email(
        subject="New User Registration",
        body=html,
        to=[MAIL_ADMIN],
        html=True,
        plain_text=body,
        from_email=MAIL_FROM,
    )
    print(f"[register] admin notified about {user_email}")


@api_router.post("/register", tags=["public"], summary="Register new user (basic)")
async def register_user(payload: RegisterPayload, db: AsyncSession = Depends(get_async_session)):
    # 1) Check duplicate email
    existing = await db.execute(select(User).where(User.email == payload.email.lower()))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    activation_token = secrets.token_urlsafe(32)
    activation_expires_at = datetime.utcnow() + timedelta(days=3)

    # 2) Create user (minimal fields)
    user = User(
        email=payload.email.lower(),
        hashed_password=get_password_hash(payload.password),
        role="user",
        is_active=False,
        activation_token=activation_token,
        activation_expires_at=activation_expires_at,
    )
    db.add(user)
    await db.commit()

    # 3) Send welcome email (non-blocking best-effort)
    try:
        send_welcome_email(payload.email, activation_token=activation_token)
        send_admin_notification(payload.email, role="user")
    except Exception as e:
        print(f"[register] email send failed: {e}")

    return {
        "success": True,
        "message": "Registration successful! Please wait up to 72 hours for security checks.",
    }


@api_router.post("/verify/{token}", tags=["public"], summary="Activate account")
async def verify_account(token: str, db: AsyncSession = Depends(get_async_session)):
    stmt = select(User).where(User.activation_token == token)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    if user.activation_expires_at and datetime.utcnow() > user.activation_expires_at:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    user.is_active = True
    user.activation_token = None
    user.activation_expires_at = None
    await db.commit()

    return {"success": True, "message": "Account successfully activated."}
