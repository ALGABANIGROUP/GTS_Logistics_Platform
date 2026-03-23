"""
Carriers Management API Routes
Manage carriers, verification, and carrier-related operations
"""

from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_, or_, func, desc
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

from backend.security.auth import get_current_user
from backend.database.session import get_async_session
from backend.models.carrier import Carrier
from backend.models.carrier_models import (
    CarrierCreate, CarrierUpdate, CarrierResponse,
    CarrierListResponse, CarrierVerification, CarrierVerificationResponse
)

router = APIRouter(prefix="/api/v1/carriers", tags=["Carriers"])


# ============================================================================
# Helper Functions
# ============================================================================

async def get_carrier_by_id(db: AsyncSession, carrier_id: int) -> Optional[Carrier]:
    """Get carrier by ID"""
    result = await db.execute(select(Carrier).where(Carrier.id == carrier_id))
    return result.scalar_one_or_none()

async def get_carrier_by_mc_number(db: AsyncSession, mc_number: str) -> Optional[Carrier]:
    """Get carrier by MC number"""
    result = await db.execute(select(Carrier).where(Carrier.mc_number == mc_number))
    return result.scalar_one_or_none()


# ============================================================================
# Carrier Verification
# ============================================================================

@router.post("/verify", response_model=CarrierVerificationResponse)
async def verify_carrier_mc_number(
    verification: CarrierVerification,
    db: AsyncSession = Depends(get_async_session)
):
    """
    Verify carrier by MC number
    """
    try:
        carrier = await get_carrier_by_mc_number(db, verification.mc_number)

        if carrier:
            return CarrierVerificationResponse(
                is_valid=True,
                carrier_info={
                    "id": carrier.id,
                    "name": carrier.name,
                    "is_active": carrier.is_active,
                    "is_verified": carrier.is_verified,
                    "rating": float(carrier.rating) if carrier.rating else None
                },
                message="Carrier found and verified"
            )
        else:
            return CarrierVerificationResponse(
                is_valid=False,
                carrier_info=None,
                message="Carrier not found in our database"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Verification failed: {str(e)}"
        )


# ============================================================================
# Carrier CRUD Operations
# ============================================================================

@router.post("/", response_model=CarrierResponse)
async def create_carrier(
    carrier_data: CarrierCreate,
    db: AsyncSession = Depends(get_async_session),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Create a new carrier
    """
    try:
        # Check if MC number already exists
        if carrier_data.mc_number:
            existing = await get_carrier_by_mc_number(db, carrier_data.mc_number)
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Carrier with this MC number already exists"
                )

        # Create new carrier
        carrier_dict = carrier_data.model_dump()
        carrier_dict["created_at"] = datetime.now(timezone.utc)
        carrier_dict["updated_at"] = datetime.now(timezone.utc)

        db_carrier = Carrier(**carrier_dict)
        db.add(db_carrier)
        await db.commit()
        await db.refresh(db_carrier)

        return CarrierResponse.model_validate(db_carrier)
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create carrier: {str(e)}"
        )


@router.get("/", response_model=CarrierListResponse)
async def list_carriers(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    search: Optional[str] = None,
    is_active: Optional[bool] = None,
    is_verified: Optional[bool] = None,
    carrier_type: Optional[str] = None,
    state: Optional[str] = None,
    min_rating: Optional[float] = Query(None, ge=1.0, le=5.0),
    db: AsyncSession = Depends(get_async_session)
):
    """
    List carriers with filtering and pagination
    """
    try:
        # Build query
        query = select(Carrier)

        # Apply filters
        if search:
            search_filter = f"%{search}%"
            query = query.where(
                or_(
                    Carrier.name.ilike(search_filter),
                    Carrier.mc_number.ilike(search_filter),
                    Carrier.email.ilike(search_filter),
                    Carrier.city.ilike(search_filter)
                )
            )

        if is_active is not None:
            query = query.where(Carrier.is_active == is_active)

        if is_verified is not None:
            query = query.where(Carrier.is_verified == is_verified)

        if carrier_type:
            query = query.where(Carrier.carrier_type == carrier_type)

        if state:
            query = query.where(Carrier.state == state)

        if min_rating:
            query = query.where(Carrier.rating >= min_rating)

        # Get total count
        count_query = query.with_only_columns(func.count(Carrier.id))
        total_result = await db.execute(count_query)
        total = total_result.scalar()

        # Apply pagination and ordering
        query = query.order_by(desc(Carrier.created_at))
        query = query.offset((page - 1) * per_page).limit(per_page)

        # Execute query
        result = await db.execute(query)
        carriers = result.scalars().all()

        return CarrierListResponse(
            carriers=[CarrierResponse.model_validate(carrier) for carrier in carriers],
            total=total,
            page=page,
            per_page=per_page
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list carriers: {str(e)}"
        )


@router.get("/{carrier_id}", response_model=CarrierResponse)
async def get_carrier(
    carrier_id: int,
    db: AsyncSession = Depends(get_async_session)
):
    """
    Get carrier by ID
    """
    carrier = await get_carrier_by_id(db, carrier_id)
    if not carrier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Carrier not found"
        )

    return CarrierResponse.model_validate(carrier)


@router.put("/{carrier_id}", response_model=CarrierResponse)
async def update_carrier(
    carrier_id: int,
    carrier_data: CarrierUpdate,
    db: AsyncSession = Depends(get_async_session),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Update carrier information
    """
    try:
        carrier = await get_carrier_by_id(db, carrier_id)
        if not carrier:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Carrier not found"
            )

        # Check MC number uniqueness if being updated
        if carrier_data.mc_number and carrier_data.mc_number != carrier.mc_number:
            existing = await get_carrier_by_mc_number(db, carrier_data.mc_number)
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Carrier with this MC number already exists"
                )

        # Update fields
        update_data = carrier_data.model_dump(exclude_unset=True)
        update_data["updated_at"] = datetime.now(timezone.utc)

        for field, value in update_data.items():
            setattr(carrier, field, value)

        await db.commit()
        await db.refresh(carrier)

        return CarrierResponse.model_validate(carrier)
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update carrier: {str(e)}"
        )


@router.delete("/{carrier_id}")
async def delete_carrier(
    carrier_id: int,
    db: AsyncSession = Depends(get_async_session),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Delete carrier (soft delete by setting is_active = false)
    """
    try:
        carrier = await get_carrier_by_id(db, carrier_id)
        if not carrier:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Carrier not found"
            )

        # Soft delete
        carrier.is_active = False
        carrier.updated_at = datetime.now(timezone.utc)

        await db.commit()

        return {"message": "Carrier deactivated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete carrier: {str(e)}"
        )


# ============================================================================
# Carrier Statistics
# ============================================================================

@router.get("/stats/summary")
async def get_carrier_stats(db: AsyncSession = Depends(get_async_session)):
    """
    Get carrier statistics summary
    """
    try:
        # Total carriers
        total_result = await db.execute(
            select(func.count(Carrier.id))
        )
        total_carriers = total_result.scalar()

        # Active carriers
        active_result = await db.execute(
            select(func.count(Carrier.id)).where(Carrier.is_active == True)
        )
        active_carriers = active_result.scalar()

        # Verified carriers
        verified_result = await db.execute(
            select(func.count(Carrier.id)).where(Carrier.is_verified == True)
        )
        verified_carriers = verified_result.scalar()

        # Average rating
        rating_result = await db.execute(
            select(func.avg(Carrier.rating)).where(Carrier.rating.isnot(None))
        )
        avg_rating = float(rating_result.scalar()) if rating_result.scalar() else None

        # Carrier types distribution
        types_result = await db.execute(
            select(Carrier.carrier_type, func.count(Carrier.id))
            .where(Carrier.carrier_type.isnot(None))
            .group_by(Carrier.carrier_type)
        )
        carrier_types = {row[0]: row[1] for row in types_result.all()}

        return {
            "total_carriers": total_carriers,
            "active_carriers": active_carriers,
            "verified_carriers": verified_carriers,
            "average_rating": avg_rating,
            "carrier_types": carrier_types
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get carrier stats: {str(e)}"
        )
