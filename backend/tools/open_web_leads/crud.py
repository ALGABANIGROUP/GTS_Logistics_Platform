# backend/tools/open_web_leads/crud.py

from typing import List, Optional, Tuple
from datetime import datetime

from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from .models import OpenWebLead, OpenWebLeadStatus
from .schemas import OpenWebLeadCreate


async def create_lead_if_not_exists(
    db: AsyncSession,
    lead_in: OpenWebLeadCreate,
) -> Tuple[OpenWebLead, bool]:
    """
    Returns: (lead, created_flag)
    created_flag = True if newly created, False if already exists.
    """
    stmt = select(OpenWebLead).where(
        OpenWebLead.raw_url == lead_in.raw_url,
        OpenWebLead.title == lead_in.title,
    )
    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()
    if existing:
        return existing, False

    db_obj = OpenWebLead(
        source=lead_in.source,
        title=lead_in.title,
        origin=lead_in.origin,
        destination=lead_in.destination,
        weight_lbs=lead_in.weight_lbs,
        equipment=lead_in.equipment,
        contact_email=lead_in.contact_email,
        contact_phone=lead_in.contact_phone,
        contact_name=lead_in.contact_name,
        raw_url=lead_in.raw_url,
        posted_at=lead_in.posted_at,
        score=lead_in.score,
        status=OpenWebLeadStatus.NEW.value,
    )
    db.add(db_obj)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        # A simple race condition occurred → return the existing record
        result = await db.execute(stmt)
        existing = result.scalar_one()
        return existing, False

    await db.refresh(db_obj)
    return db_obj, True


async def list_leads(
    db: AsyncSession,
    *,
    status: Optional[str] = None,
    origin: Optional[str] = None,
    destination: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
) -> Tuple[int, List[OpenWebLead]]:
    stmt = select(OpenWebLead)
    count_stmt = select(func.count(OpenWebLead.id))

    if status:
        stmt = stmt.where(OpenWebLead.status == status)
        count_stmt = count_stmt.where(OpenWebLead.status == status)

    if origin:
        stmt = stmt.where(OpenWebLead.origin.ilike(f"%{origin}%"))
        count_stmt = count_stmt.where(OpenWebLead.origin.ilike(f"%{origin}%"))

    if destination:
        stmt = stmt.where(OpenWebLead.destination.ilike(f"%{destination}%"))
        count_stmt = count_stmt.where(OpenWebLead.destination.ilike(f"%{destination}%"))

    stmt = stmt.order_by(OpenWebLead.created_at.desc()).limit(limit).offset(offset)

    total = (await db.execute(count_stmt)).scalar_one()
    items = (await db.execute(stmt)).scalars().all()
    return total, list(items)


async def update_lead_status(
    db: AsyncSession,
    lead_id: int,
    status: str,
) -> Optional[OpenWebLead]:
    stmt = select(OpenWebLead).where(OpenWebLead.id == lead_id)
    result = await db.execute(stmt)
    lead = result.scalar_one_or_none()
    if not lead:
        return None

    lead.status = status
    lead.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(lead)
    return lead


async def get_lead_by_id(
    db: AsyncSession,
    lead_id: int,
) -> Optional[OpenWebLead]:
    """
    Simple helper for GET /api/v1/open-web-leads/{id}
    """
    stmt = select(OpenWebLead).where(OpenWebLead.id == lead_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()
