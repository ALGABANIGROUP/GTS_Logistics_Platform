"""
FastAPI dependencies for quota enforcement
"""

import logging
from typing import Optional
from fastapi import Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database.session import wrap_session_factory, get_async_session
from backend.security.tenant_resolver import get_tenant_id
from backend.security.quotas import QuotaChecker
from backend.models.tenant import Tenant

logger = logging.getLogger(__name__)


async def get_quota_checker(
    tenant_id: str = Depends(get_tenant_id),
    db: AsyncSession = Depends(get_async_session)
) -> QuotaChecker:
    """Get quota checker for current tenant"""
    
    async with wrap_session_factory(get_async_session) as session:
        # Fetch tenant from DB
        stmt = __import__("sqlalchemy").select(Tenant).filter(Tenant.id == tenant_id)
        result = await session.execute(stmt)
        tenant = result.scalar_one_or_none()
        
        if not tenant:
            raise HTTPException(status_code=404, detail="Tenant not found")
        
        # Create checker with tenant's plan and custom quotas
        checker = QuotaChecker(
            tenant_plan=tenant.plan or "free_trial",
            tenant_quotas=tenant.quotas
        )
        
        return checker


async def enforce_quota(
    request: Request,
    quota_type: str,
    increment: int = 1,
    quota_checker: QuotaChecker = Depends(get_quota_checker)
) -> bool:
    """
    Enforce quota limit for a specific resource
    
    Usage:
        @router.post("/tickets")
        async def create_ticket(
            data: TicketCreate,
            _: bool = Depends(lambda: enforce_quota(request, "max_tickets_per_day"))
        ):
            pass
    """
    
    # Note: In production, track actual usage from DB
    # For now, this is a scaffold that always passes
    # Real implementation would query usage count
    
    logger.debug(f"Quota check: {quota_type} (increment={increment}) for tenant")
    
    # Quota check passed
    return True


async def check_feature_access(
    request: Request,
    feature_name: str,
    quota_checker: QuotaChecker = Depends(get_quota_checker)
) -> bool:
    """
    Check if tenant has access to a feature based on quota
    
    Usage:
        @router.get("/advanced-analytics")
        async def get_analytics(
            _: bool = Depends(lambda: check_feature_access(request, "advanced_analytics"))
        ):
            pass
    """
    
    has_access, error_msg = quota_checker.check_feature_access(feature_name)
    
    if not has_access:
        logger.warning(f"Feature access denied for {feature_name}: {error_msg}")
        raise HTTPException(status_code=403, detail=error_msg)
    
    return True

