# backend/tools/open_web_leads/dev_router.py

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from . import crud
from .schemas import (
    OpenWebLeadListResponse,
    OpenWebLeadOut,
    OpenWebLeadUpdateStatus,
)
from backend.database.config import get_db

# Separate Dev route, outside /api/v1, with no Auth
router = APIRouter(
    prefix="/dev/open-web-leads",
    tags=["dev-open-web-leads"],
)


@router.get("/", response_model=OpenWebLeadListResponse)
async def dev_list_open_web_leads(
    status: Optional[str] = Query(
        None,
        description="Filter by lead status",
    ),
    origin: Optional[str] = Query(
        None,
        description="Filter by origin (text contains)",
    ),
    destination: Optional[str] = Query(
        None,
        description="Filter by destination (text contains)",
    ),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """
    DEV: List Open Web Leads without authentication.
    """
    total, items = await crud.list_leads(
        db,
        status=status,
        origin=origin,
        destination=destination,
        limit=limit,
        offset=offset,
    )
    return OpenWebLeadListResponse(total=total, items=[OpenWebLeadOut.from_orm(item) for item in items])


@router.get("/{lead_id}", response_model=OpenWebLeadOut)
async def dev_get_open_web_lead(
    lead_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    DEV: Get a single lead by ID (no auth).
    """
    lead = await crud.get_lead_by_id(db, lead_id)
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found",
        )
    return lead


@router.patch("/{lead_id}/status", response_model=OpenWebLeadOut)
async def dev_update_open_web_lead_status(
    lead_id: int,
    payload: OpenWebLeadUpdateStatus,
    db: AsyncSession = Depends(get_db),
):
    """
    DEV: Update lead status without authentication.
    """
    lead = await crud.update_lead_status(
        db,
        lead_id=lead_id,
        status=payload.status,
    )
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found",
        )
    return lead

