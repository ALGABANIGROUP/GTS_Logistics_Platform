from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.models.portal_access_request import PortalAccessRequest


async def create_portal_request(
    db: AsyncSession,
    *,
    full_name: str,
    company: str,
    email: str,
    mobile: str,
    comment: Optional[str],
    country: str,
    user_type: str,
    us_state: Optional[str],
    dot_number: Optional[str],
    mc_number: Optional[str],
    us_business_address: Optional[str],
    ca_province: Optional[str],
    ca_registered_address: Optional[str],
    ca_company_number: Optional[str],
    document_name: Optional[str],
) -> PortalAccessRequest:
    obj = PortalAccessRequest(
        full_name=full_name,
        company=company,
        email=email,
        mobile=mobile,
        comment=comment,
        country=country,
        user_type=user_type,
        us_state=us_state,
        dot_number=dot_number,
        mc_number=mc_number,
        us_business_address=us_business_address,
        ca_province=ca_province,
        ca_registered_address=ca_registered_address,
        ca_company_number=ca_company_number,
        document_name=document_name,
        status="pending",
    )
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


async def list_portal_requests(db: AsyncSession) -> List[PortalAccessRequest]:
    result = await db.execute(
        select(PortalAccessRequest).order_by(PortalAccessRequest.created_at.desc())
    )
    return list(result.scalars().all())


async def get_portal_request_by_id(
    db: AsyncSession, request_id: int
) -> Optional[PortalAccessRequest]:
    result = await db.execute(
        select(PortalAccessRequest).where(PortalAccessRequest.id == request_id)
    )
    return result.scalar_one_or_none()


async def approve_portal_request(
    db: AsyncSession,
    request_id: int,
    admin_email: str,
) -> PortalAccessRequest:
    req = await get_portal_request_by_id(db, request_id)
    if not req:
        raise ValueError("Request not found")

    req.status = "approved"  # type: ignore[assignment]
    req.approved_by = admin_email  # type: ignore[assignment]
    req.approved_at = datetime.now(timezone.utc)  # type: ignore[assignment]

    await db.commit()
    await db.refresh(req)
    return req


async def reject_portal_request(
    db: AsyncSession,
    request_id: int,
    admin_email: str,
    reason: Optional[str] = None,
) -> PortalAccessRequest:
    req = await get_portal_request_by_id(db, request_id)
    if not req:
        raise ValueError("Request not found")

    req.status = "rejected"  # type: ignore[assignment]
    req.rejected_by = admin_email  # type: ignore[assignment]
    req.rejected_at = datetime.now(timezone.utc)  # type: ignore[assignment]
    req.rejection_reason = reason  # type: ignore[assignment]

    await db.commit()
    await db.refresh(req)
    return req
# --- IGNORE ------------------------------------------------------------------------------------------------------------------------------
