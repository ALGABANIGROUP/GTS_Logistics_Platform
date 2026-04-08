"""
Shippers Management API Routes
Manage shippers, verification, and shipper-related operations
"""

from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_, or_, func, desc
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

from backend.security.auth import get_current_user
from backend.database.session import get_async_session
from backend.models.shipper import Shipper
from backend.models.shipper_models import (
    ShipperCreate, ShipperUpdate, ShipperResponse,
    ShipperListResponse, ShipperVerification, ShipperVerificationResponse
)

router = APIRouter(prefix="/api/v1/shippers", tags=["Shippers"])


# ============================================================================
# Helper Functions
# ============================================================================

async def get_shipper_by_id(db: AsyncSession, shipper_id: int) -> Optional[Shipper]:
    """Get shipper by ID"""
    result = await db.execute(select(Shipper).where(Shipper.id == shipper_id))
    return result.scalar_one_or_none()

async def get_shipper_by_tax_id(db: AsyncSession, tax_id: str) -> Optional[Shipper]:
    """Get shipper by tax ID"""
    result = await db.execute(select(Shipper).where(Shipper.tax_id == tax_id))
    return result.scalar_one_or_none()


# ============================================================================
# Shipper Verification
# ============================================================================

@router.post("/verify", response_model=ShipperVerificationResponse)
async def verify_shipper_tax_id(
    verification: ShipperVerification,
    db: AsyncSession = Depends(get_async_session)
):
    """
    Verify shipper by tax ID
    """
    try:
        shipper = await get_shipper_by_tax_id(db, verification.tax_id)

        if shipper:
            return ShipperVerificationResponse(
                is_valid=True,
                shipper_info={
                    "id": shipper.id,
                    "name": shipper.name,
                    "is_active": shipper.is_active,
                    "is_verified": shipper.is_verified,
                    "rating": float(shipper.rating) if shipper.rating else None
                },
                message="Shipper found and verified"
            )
        else:
            return ShipperVerificationResponse(
                is_valid=False,
                shipper_info=None,
                message="Shipper not found in our database"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Verification failed: {str(e)}"
        )


# ============================================================================
# Shipper CRUD Operations
# ============================================================================

@router.post("/", response_model=ShipperResponse)
async def create_shipper(
    shipper_data: ShipperCreate,
    db: AsyncSession = Depends(get_async_session),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Create a new shipper
    """
    try:
        # Check if tax ID already exists
        if shipper_data.tax_id:
            existing = await get_shipper_by_tax_id(db, shipper_data.tax_id)
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Shipper with this tax ID already exists"
                )

        # Create new shipper
        shipper_dict = shipper_data.model_dump()
        shipper_dict["created_at"] = datetime.now(timezone.utc)
        shipper_dict["updated_at"] = datetime.now(timezone.utc)

        db_shipper = Shipper(**shipper_dict)
        db.add(db_shipper)
        await db.commit()
        await db.refresh(db_shipper)

        return ShipperResponse.model_validate(db_shipper)
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create shipper: {str(e)}"
        )


@router.get("/", response_model=ShipperListResponse)
async def list_shippers(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    search: Optional[str] = None,
    is_active: Optional[bool] = None,
    is_verified: Optional[bool] = None,
    industry_type: Optional[str] = None,
    business_type: Optional[str] = None,
    state: Optional[str] = None,
    min_rating: Optional[float] = Query(None, ge=1.0, le=5.0),
    db: AsyncSession = Depends(get_async_session)
):
    """
    List shippers with filtering and pagination
    """
    try:
        # Build query
        query = select(Shipper)

        # Apply filters
        if search:
            search_filter = f"%{search}%"
            query = query.where(
                or_(
                    Shipper.name.ilike(search_filter),
                    Shipper.tax_id.ilike(search_filter),
                    Shipper.email.ilike(search_filter),
                    Shipper.city.ilike(search_filter)
                )
            )

        if is_active is not None:
            query = query.where(Shipper.is_active == is_active)

        if is_verified is not None:
            query = query.where(Shipper.is_verified == is_verified)

        if industry_type:
            query = query.where(Shipper.industry_type == industry_type)

        if business_type:
            query = query.where(Shipper.business_type == business_type)

        if state:
            query = query.where(Shipper.state == state)

        if min_rating:
            query = query.where(Shipper.rating >= min_rating)

        # Get total count
        count_query = query.with_only_columns(func.count(Shipper.id))
        total_result = await db.execute(count_query)
        total = total_result.scalar()

        # Apply pagination and ordering
        query = query.order_by(desc(Shipper.created_at))
        query = query.offset((page - 1) * per_page).limit(per_page)

        # Execute query
        result = await db.execute(query)
        shippers = result.scalars().all()

        return ShipperListResponse(
            shippers=[ShipperResponse.model_validate(shipper) for shipper in shippers],
            total=total,
            page=page,
            per_page=per_page
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list shippers: {str(e)}"
        )


@router.get("/recent")
async def get_recent_shippers(
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Get recently added shippers
    """
    try:
        result = await db.execute(
            select(Shipper)
            .where(Shipper.is_active == True)
            .order_by(desc(Shipper.created_at))
            .limit(limit)
        )
        shippers = result.scalars().all()

        return {
            "items": [ShipperResponse.model_validate(shipper) for shipper in shippers],
            "total": len(shippers)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get recent shippers: {str(e)}"
        )


@router.get("/{shipper_id}", response_model=ShipperResponse)
async def get_shipper(
    shipper_id: int,
    db: AsyncSession = Depends(get_async_session)
):
    """
    Get shipper by ID
    """
    shipper = await get_shipper_by_id(db, shipper_id)
    if not shipper:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shipper not found"
        )

    return ShipperResponse.model_validate(shipper)


@router.put("/{shipper_id}", response_model=ShipperResponse)
async def update_shipper(
    shipper_id: int,
    shipper_data: ShipperUpdate,
    db: AsyncSession = Depends(get_async_session),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Update shipper information
    """
    try:
        shipper = await get_shipper_by_id(db, shipper_id)
        if not shipper:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Shipper not found"
            )

        # Check tax ID uniqueness if being updated
        if shipper_data.tax_id and shipper_data.tax_id != shipper.tax_id:
            existing = await get_shipper_by_tax_id(db, shipper_data.tax_id)
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Shipper with this tax ID already exists"
                )

        # Update fields
        update_data = shipper_data.model_dump(exclude_unset=True)
        update_data["updated_at"] = datetime.now(timezone.utc)

        for field, value in update_data.items():
            setattr(shipper, field, value)

        await db.commit()
        await db.refresh(shipper)

        return ShipperResponse.model_validate(shipper)
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update shipper: {str(e)}"
        )


@router.delete("/{shipper_id}")
async def delete_shipper(
    shipper_id: int,
    db: AsyncSession = Depends(get_async_session),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Delete shipper (soft delete by setting is_active = false)
    """
    try:
        shipper = await get_shipper_by_id(db, shipper_id)
        if not shipper:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Shipper not found"
            )

        # Soft delete
        shipper.is_active = False
        shipper.updated_at = datetime.now(timezone.utc)

        await db.commit()

        return {"message": "Shipper deactivated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete shipper: {str(e)}"
        )


# ============================================================================
# Shipper Statistics
# ============================================================================

@router.get("/stats/summary")
async def get_shipper_stats(db: AsyncSession = Depends(get_async_session)):
    """
    Get shipper statistics summary
    """
    try:
        # Total shippers
        total_result = await db.execute(
            select(func.count(Shipper.id))
        )
        total_shippers = total_result.scalar()

        # Active shippers
        active_result = await db.execute(
            select(func.count(Shipper.id)).where(Shipper.is_active == True)
        )
        active_shippers = active_result.scalar()

        # Verified shippers
        verified_result = await db.execute(
            select(func.count(Shipper.id)).where(Shipper.is_verified == True)
        )
        verified_shippers = verified_result.scalar()

        # Average rating
        rating_result = await db.execute(
            select(func.avg(Shipper.rating)).where(Shipper.rating.isnot(None))
        )
        avg_rating = float(rating_result.scalar()) if rating_result.scalar() else None

        # Industry types distribution
        industry_result = await db.execute(
            select(Shipper.industry_type, func.count(Shipper.id))
            .where(Shipper.industry_type.isnot(None))
            .group_by(Shipper.industry_type)
        )
        industry_types = {row[0]: row[1] for row in industry_result.all()}

        return {
            "total_shippers": total_shippers,
            "active_shippers": active_shippers,
            "verified_shippers": verified_shippers,
            "average_rating": avg_rating,
            "industry_types": industry_types
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get shipper stats: {str(e)}"
        )