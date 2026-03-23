# backend/routes/admin_requests.py
import secrets
import string

from fastapi import APIRouter, HTTPException, Depends
from backend.auth.rbac_middleware import require_permission
from sqlalchemy.ext.asyncio import AsyncSession

from backend.utils.email_utils import send_bot_email
from backend.crud.portal_access_requests import get_portal_request_by_id, approve_portal_request
from backend.crud.users import create_user_from_portal_request  # Fix import path if needed
from backend.security.auth import require_roles
from backend.database.session import get_db_async  # Or use get_async_session if unavailable

router = APIRouter(prefix="/admin/requests", tags=["admin-requests"])


def generate_strong_password(length: int = 14) -> str:
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return "".join(secrets.choice(alphabet) for _ in range(length))


@router.post("/{request_id}/approve")
async def approve_request(
    request_id: int,
    db: AsyncSession = Depends(get_db_async),
    current_admin=Depends(require_roles(["admin", "system_admin", "super_admin"])),
    _=Depends(require_permission("requests.approve")),
):
    # 1) Read the request from the database
    portal_request = await get_portal_request_by_id(db, request_id)
    if not portal_request:
        raise HTTPException(status_code=404, detail="Request not found")
    if getattr(portal_request, "status", None) == "approved":
        raise HTTPException(status_code=400, detail="Already approved")

    # 2) Generate an automatic password
    raw_password = generate_strong_password()

    # 3) Create a new user (use your current user creation system)
    user = await create_user_from_portal_request(
        portal_request=portal_request,
        raw_password=raw_password,  # Password hashing is done inside create_user
    )

    # 4) Update the request status to "approved"
    await approve_portal_request(db, request_id, current_admin.email)

    # 5) Send an email to the user
    subject = "Your Gabani Transport Solutions (GTS) account has been approved"
    body = f"""
Hello {getattr(portal_request, 'full_name', '')},

Your enterprise access request has been approved.

Login URL: http://127.0.0.1:5173/login
Email: {getattr(portal_request, 'email', '')}
Temporary password: {raw_password}

For security reasons, please log in and change your password immediately
from the Account / Security settings.

Thank you,
Gabani Transport Solutions (GTS)
"""

    send_bot_email(
        bot_name="admin",
        subject=subject,
        body=body,
        to=[getattr(portal_request, 'email', '')],
    )

    return {"status": "approved", "user_id": getattr(user, 'id', None)}

