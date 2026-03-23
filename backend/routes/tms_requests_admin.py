"""
TMS Registration Requests API - Admin Panel for TMS Access Control
Handles approval/rejection of TMS registration requests
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func
from backend.database.session import wrap_session_factory
from backend.models.unified_models import TMSRegistrationRequest, UnifiedUser, UserSystemsAccess
from backend.auth.unified_auth import unified_auth
from backend.services.unified_email import UnifiedEmailSystem
from backend.security.geo_middleware import GeoRestrictionService
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
import logging
import uuid

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/admin/tms-requests", tags=["TMS Registration"])

# --- DB dependency: get_db_async ---
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


class TMSRegistrationRequestCreate(BaseModel):
    """Payload for creating a TMS registration request."""
    company_name: str
    contact_name: str
    contact_email: EmailStr
    contact_phone: Optional[str] = None
    company_website: Optional[str] = None
    industry_type: Optional[str] = 'freight_broker'  # 'freight_broker', 'carrier', '3pl'
    state_province: Optional[str] = None
    city: Optional[str] = None
    requested_plan: str = 'starter'  # 'starter', 'professional', 'enterprise'
    notes: Optional[str] = None


class TMSRequestApproval(BaseModel):
    """Payload used when approving a TMS request."""
    notes: Optional[str] = None


class TMSRequestRejection(BaseModel):
    """Payload used when rejecting a TMS request."""
    rejection_reason: str


async def verify_admin(request: Request) -> dict:
    """Verify that the requester has admin privileges."""
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token required"
        )
    
    payload = unified_auth.verify_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    # Check if user is admin
    is_admin = any(
        s.get("access_level") in ["admin", "super_admin"]
        for s in payload.get("systems", [])
    )
    
    if not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    return payload


@router.post("/submit", summary="Submit TMS Registration Request")
async def submit_tms_request(
    request: Request,
    data: TMSRegistrationRequestCreate,
    session: AsyncSession = Depends(get_db_async)
):
    """
    Submit a new TMS registration request (public endpoint)
    Anyone can submit, but needs admin approval
    """
    try:
        # Get client IP and country
        client_ip = GeoRestrictionService.get_client_ip(request)
        country_code = GeoRestrictionService.get_country_from_ip(client_ip)
        
        # Create request
        new_request = TMSRegistrationRequest(
            id=uuid.uuid4(),
            company_name=data.company_name,
            contact_name=data.contact_name,
            contact_email=data.contact_email,
            contact_phone=data.contact_phone,
            company_website=data.company_website,
            industry_type=data.industry_type,
            country_code=country_code,
            state_province=data.state_province,
            city=data.city,
            request_ip=client_ip,
            requested_plan=data.requested_plan,
            notes=data.notes,
            status='pending'
        )
        
        session.add(new_request)
        await session.commit()
        await session.refresh(new_request)
        
        # Notify admin
        UnifiedEmailSystem.notify_admin_new_tms_request(
            request_id=str(new_request.id),
            company_name=data.company_name,
            contact_email=data.contact_email
        )
        
        logger.info(f"New TMS request submitted: {data.company_name} from {country_code}")
        
        return {
            "success": True,
            "message": "Your TMS access request has been submitted successfully",
            "request_id": str(new_request.id),
            "status": "pending",
            "note": "Admin will review your request within 24-48 hours"
        }
        
    except Exception as e:
        logger.error(f"Error submitting TMS request: {e}")
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit request: {str(e)}"
        )


@router.get("/list", summary="Get All TMS Requests (Admin Only)")
async def list_tms_requests(
    request: Request,
    status_filter: Optional[str] = None,  # 'pending', 'approved', 'rejected'
    limit: int = 50,
    offset: int = 0,
    admin_payload: dict = Depends(verify_admin)
):
    """
    Get all TMS registration requests with filtering
    Admin only endpoint
    """
    async with wrap_session_factory(get_db_async) as session:
        try:
            query = select(TMSRegistrationRequest).order_by(TMSRegistrationRequest.created_at.desc())
            
            # Apply status filter
            if status_filter:
                query = query.where(TMSRegistrationRequest.status == status_filter)
            
            # Apply pagination
            query = query.limit(limit).offset(offset)
            
            result = await session.execute(query)
            requests = result.scalars().all()
            
            # Get total count
            count_query = select(func.count(TMSRegistrationRequest.id))
            if status_filter:
                count_query = count_query.where(TMSRegistrationRequest.status == status_filter)
            
            count_result = await session.execute(count_query)
            total_count = count_result.scalar()
            
            return {
                "success": True,
                "requests": [
                    {
                        "id": str(req.id),
                        "company_name": req.company_name,
                        "contact_name": req.contact_name,
                        "contact_email": req.contact_email,
                        "contact_phone": req.contact_phone,
                        "industry_type": req.industry_type,
                        "country_code": req.country_code,
                        "state_province": req.state_province,
                        "city": req.city,
                        "requested_plan": req.requested_plan,
                        "status": req.status,
                        "created_at": req.created_at.isoformat() if req.created_at else None,
                        "reviewed_at": req.reviewed_at.isoformat() if req.reviewed_at else None,
                        "rejection_reason": req.rejection_reason,
                        "notes": req.notes
                    }
                    for req in requests
                ],
                "total": total_count,
                "limit": limit,
                "offset": offset
            }
            
        except Exception as e:
            logger.error(f"Error listing TMS requests: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to list requests: {str(e)}"
            )


@router.post("/{request_id}/approve", summary="Approve TMS Request (Admin Only)")
async def approve_tms_request(
    request_id: str,
    request: Request,
    approval_data: TMSRequestApproval,
    admin_payload: dict = Depends(verify_admin)
):
    """
    Approve a TMS registration request and grant TMS access
    Admin only endpoint
    """
    async with wrap_session_factory(get_db_async) as session:
        try:
            # Get request
            result = await session.execute(
                select(TMSRegistrationRequest).where(TMSRegistrationRequest.id == uuid.UUID(request_id))
            )
            tms_request = result.scalar_one_or_none()
            
            if not tms_request:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Request not found"
                )
            
            if tms_request.status != 'pending':
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Request already {tms_request.status}"
                )
            
            # Check if user exists, if not create one
            user_result = await session.execute(
                select(UnifiedUser).where(UnifiedUser.email == tms_request.contact_email)
            )
            user = user_result.scalar_one_or_none()
            
            if not user:
                # Create new user
                user = UnifiedUser(
                    id=uuid.uuid4(),
                    email=tms_request.contact_email,
                    password_hash=unified_auth.hash_password("TempPassword123!"),  # Temp password
                    full_name=tms_request.contact_name,
                    phone=tms_request.contact_phone,
                    company_name=tms_request.company_name,
                    country=tms_request.country_code,
                    is_active=True,
                    email_verified=False
                )
                session.add(user)
                await session.flush()
            
            # Grant TMS access
            tms_access = UserSystemsAccess(
                id=uuid.uuid4(),
                user_id=user.id,
                system_type='tms',
                access_level='user',
                subscription_plan=tms_request.requested_plan,
                is_active=True
            )
            session.add(tms_access)
            
            # Update request status
            tms_request.status = 'approved'
            tms_request.reviewed_by = uuid.UUID(admin_payload['user_id'])
            tms_request.reviewed_at = datetime.utcnow()
            tms_request.user_id = user.id
            if approval_data.notes:
                tms_request.notes = approval_data.notes
            
            await session.commit()
            
            # Send approval email
            user_email = user.email if isinstance(user.email, str) else str(user.email)
            user_name = user.full_name if isinstance(user.full_name, str) else str(user.full_name)
            UnifiedEmailSystem.send_tms_approval_email(
                user_email=user_email,
                full_name=user_name,
                company_name=tms_request.company_name,
                plan=tms_request.requested_plan
            )
            
            logger.info(f"TMS request approved: {tms_request.company_name} -> {user.email}")
            
            return {
                "success": True,
                "message": "TMS access granted successfully",
                "user_id": str(user.id),
                "email": user.email,
                "plan": tms_request.requested_plan
            }
            
        except Exception as e:
            logger.error(f"Error approving TMS request: {e}")
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to approve request: {str(e)}"
            )


@router.post("/{request_id}/reject", summary="Reject TMS Request (Admin Only)")
async def reject_tms_request(
    request_id: str,
    request: Request,
    rejection_data: TMSRequestRejection,
    admin_payload: dict = Depends(verify_admin)
):
    """
    Reject a TMS registration request
    Admin only endpoint
    """
    async with wrap_session_factory(get_db_async) as session:
        try:
            # Get request
            result = await session.execute(
                select(TMSRegistrationRequest).where(TMSRegistrationRequest.id == uuid.UUID(request_id))
            )
            tms_request = result.scalar_one_or_none()
            
            if not tms_request:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Request not found"
                )
            
            if tms_request.status != 'pending':
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Request already {tms_request.status}"
                )
            
            # Update request status
            tms_request.status = 'rejected'
            tms_request.reviewed_by = uuid.UUID(admin_payload['user_id'])
            tms_request.reviewed_at = datetime.utcnow()
            tms_request.rejection_reason = rejection_data.rejection_reason
            
            await session.commit()
            
            # Send rejection email
            UnifiedEmailSystem.send_tms_rejection_email(
                user_email=tms_request.contact_email,
                full_name=tms_request.contact_name,
                reason=rejection_data.rejection_reason
            )
            
            logger.info(f"TMS request rejected: {tms_request.company_name}")
            
            return {
                "success": True,
                "message": "Request rejected",
                "reason": rejection_data.rejection_reason
            }
            
        except Exception as e:
            logger.error(f"Error rejecting TMS request: {e}")
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to reject request: {str(e)}"
            )


@router.get("/stats", summary="Get TMS Requests Statistics (Admin Only)")
async def get_tms_requests_stats(
    request: Request,
    admin_payload: dict = Depends(verify_admin)
):
    """Get statistics about TMS requests"""
    async with wrap_session_factory(get_db_async) as session:
        try:
            # Count by status
            pending_count = await session.execute(
                select(func.count(TMSRegistrationRequest.id)).where(
                    TMSRegistrationRequest.status == 'pending'
                )
            )
            approved_count = await session.execute(
                select(func.count(TMSRegistrationRequest.id)).where(
                    TMSRegistrationRequest.status == 'approved'
                )
            )
            rejected_count = await session.execute(
                select(func.count(TMSRegistrationRequest.id)).where(
                    TMSRegistrationRequest.status == 'rejected'
                )
            )
            
            return {
                "success": True,
                "stats": {
                    "pending": pending_count.scalar(),
                    "approved": approved_count.scalar(),
                    "rejected": rejected_count.scalar(),
                    "total": pending_count.scalar() + approved_count.scalar() + rejected_count.scalar()
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting TMS stats: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get stats: {str(e)}"
            )


