# backend/tools/open_web_leads/router.py

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


# No auth in development stage
router = APIRouter(
    prefix="/api/v1/open-web-leads",
    tags=["open-web-leads"],
)


@router.get("/", response_model=OpenWebLeadListResponse)
async def list_open_web_leads(
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
    List Open Web Leads with optional filters.
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


@router.patch("/{lead_id}/status", response_model=OpenWebLeadOut)
async def update_open_web_lead_status(
    lead_id: int,
    payload: OpenWebLeadUpdateStatus,
    db: AsyncSession = Depends(get_db),
):
    """
    Update status of a lead (new / contacted / closed / ignored).
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


@router.get("/{lead_id}", response_model=OpenWebLeadOut)
async def get_open_web_lead(
    lead_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieve a single lead by ID.
    """
    lead = await crud.get_lead_by_id(db, lead_id)
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found",
        )
    return lead

