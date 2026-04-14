# backend/routes/tenants.py
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
from pydantic import BaseModel, EmailStr

from backend.database.session import get_async_session
from backend.security.auth import get_current_user
from backend.models.user import User
from backend.models.tenant import Tenant  # If it exists, or use temporary model

router = APIRouter(tags=["Tenants"])
logger = logging.getLogger(__name__)


# ==================== Models ====================
class TenantCreate(BaseModel):
    name: str
    domain: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    subscription_tier: str = "basic"
    is_active: bool = True


class TenantUpdate(BaseModel):
    name: Optional[str] = None
    domain: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    subscription_tier: Optional[str] = None
    is_active: Optional[bool] = None


class TenantResponse(BaseModel):
    id: int
    name: str
    domain: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    subscription_tier: str
    is_active: bool
    created_at: str
    updated_at: Optional[str] = None
    user_count: int = 0


# ==================== Mock Data (temporary until database exists) =====================
MOCK_TENANTS = [
    {
        "id": 1,
        "name": "GTS Logistics Inc.",
        "domain": "gtsdispatcher.com",
        "email": "info@gtsdispatcher.com",
        "phone": "+1-800-555-0123",
        "address": "123 Business Ave, New York, NY 10001",
        "subscription_tier": "enterprise",
        "is_active": True,
        "created_at": "2024-01-01T00:00:00",
        "updated_at": None,
        "user_count": 5
    },
    {
        "id": 2,
        "name": "Gabani Transport Solutions",
        "domain": "gabanilogistics.com",
        "email": "support@gabanilogistics.com",
        "phone": "+1-800-555-0456",
        "address": "456 Transport Blvd, Chicago, IL 60601",
        "subscription_tier": "enterprise",
        "is_active": True,
        "created_at": "2024-01-15T00:00:00",
        "updated_at": None,
        "user_count": 3
    },
    {
        "id": 3,
        "name": "Fast Freight Co.",
        "domain": "fastfreight.com",
        "email": "contact@fastfreight.com",
        "phone": "+1-800-555-0789",
        "address": "789 Speedway, Dallas, TX 75201",
        "subscription_tier": "professional",
        "is_active": True,
        "created_at": "2024-02-01T00:00:00",
        "updated_at": None,
        "user_count": 2
    },
    {
        "id": 4,
        "name": "Maple Load Canada",
        "domain": "mapleload.ca",
        "email": "info@mapleload.ca",
        "phone": "+1-800-555-1011",
        "address": "101 Maple Street, Toronto, ON M5V 2T6",
        "subscription_tier": "professional",
        "is_active": True,
        "created_at": "2024-02-15T00:00:00",
        "updated_at": None,
        "user_count": 2
    },
    {
        "id": 5,
        "name": "Demo Tenant",
        "domain": "demo.gtsdispatcher.com",
        "email": "demo@gtsdispatcher.com",
        "phone": "+1-800-555-1213",
        "address": "202 Demo Lane, San Francisco, CA 94105",
        "subscription_tier": "basic",
        "is_active": False,
        "created_at": "2024-03-01T00:00:00",
        "updated_at": "2024-03-15T00:00:00",
        "user_count": 1
    }
]


# ==================== Endpoints ====================

@router.get("/")
async def get_tenants(
    page: int = 1,
    limit: int = 25,
    search: Optional[str] = None,
    subscription_tier: Optional[str] = None,
    status: Optional[str] = None,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get all tenants (requires admin access)
    """

    # Check admin permissions
    user_role = current_user.get("role", "").lower()
    if user_role not in ["super_admin", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    # Filter data
    tenants = MOCK_TENANTS.copy()

    if search:
        tenants = [t for t in tenants if
                   search.lower() in t["name"].lower() or
                   (t.get("domain") and search.lower() in t["domain"].lower())]

    if subscription_tier:
        tenants = [t for t in tenants if t["subscription_tier"] == subscription_tier]

    if status == "active":
        tenants = [t for t in tenants if t["is_active"]]
    elif status == "inactive":
        tenants = [t for t in tenants if not t["is_active"]]

    total = len(tenants)

    # Pagination
    start = (page - 1) * limit
    end = start + limit
    tenants = tenants[start:end]

    return {
        "tenants": tenants,
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": (total + limit - 1) // limit if total else 0
    }


@router.get("/{tenant_id}")
async def get_tenant(
    tenant_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get single tenant by ID"""

    user_role = current_user.get("role", "").lower()
    if user_role not in ["super_admin", "admin"]:
        raise HTTPException(status_code=403, detail="Admin access required")

    tenant = next((t for t in MOCK_TENANTS if t["id"] == tenant_id), None)

    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    return tenant


@router.post("/")
async def create_tenant(
    tenant: TenantCreate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Create a new tenant"""

    user_role = current_user.get("role", "").lower()
    if user_role not in ["super_admin", "admin"]:
        raise HTTPException(status_code=403, detail="Admin access required")

    new_id = max([t["id"] for t in MOCK_TENANTS]) + 1 if MOCK_TENANTS else 1

    new_tenant = {
        "id": new_id,
        "name": tenant.name,
        "domain": tenant.domain,
        "email": tenant.email,
        "phone": tenant.phone,
        "address": tenant.address,
        "subscription_tier": tenant.subscription_tier,
        "is_active": tenant.is_active,
        "created_at": datetime.now().isoformat(),
        "updated_at": None,
        "user_count": 0
    }

    MOCK_TENANTS.append(new_tenant)

    return new_tenant


@router.patch("/{tenant_id}")
async def update_tenant(
    tenant_id: int,
    tenant_update: TenantUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Update a tenant"""

    user_role = current_user.get("role", "").lower()
    if user_role not in ["super_admin", "admin"]:
        raise HTTPException(status_code=403, detail="Admin access required")

    tenant = next((t for t in MOCK_TENANTS if t["id"] == tenant_id), None)

    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    # Update fields
    if tenant_update.name is not None:
        tenant["name"] = tenant_update.name
    if tenant_update.domain is not None:
        tenant["domain"] = tenant_update.domain
    if tenant_update.email is not None:
        tenant["email"] = tenant_update.email
    if tenant_update.phone is not None:
        tenant["phone"] = tenant_update.phone
    if tenant_update.address is not None:
        tenant["address"] = tenant_update.address
    if tenant_update.subscription_tier is not None:
        tenant["subscription_tier"] = tenant_update.subscription_tier
    if tenant_update.is_active is not None:
        tenant["is_active"] = tenant_update.is_active

    tenant["updated_at"] = datetime.now().isoformat()

    return tenant


@router.delete("/{tenant_id}")
async def delete_tenant(
    tenant_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Delete a tenant (soft delete)"""

    user_role = current_user.get("role", "").lower()
    if user_role not in ["super_admin", "admin"]:
        raise HTTPException(status_code=403, detail="Admin access required")

    tenant = next((t for t in MOCK_TENANTS if t["id"] == tenant_id), None)

    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    # Soft delete - set inactive
    tenant["is_active"] = False
    tenant["updated_at"] = datetime.now().isoformat()

    return {"message": "Tenant deactivated successfully"}


@router.get("/stats/summary")
async def get_tenants_stats(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get tenants statistics"""

    user_role = current_user.get("role", "").lower()
    if user_role not in ["super_admin", "admin"]:
        raise HTTPException(status_code=403, detail="Admin access required")

    total = len(MOCK_TENANTS)
    active = len([t for t in MOCK_TENANTS if t["is_active"]])
    inactive = total - active

    # Statistics by subscription plan
    by_tier = {}
    for tenant in MOCK_TENANTS:
        tier = tenant["subscription_tier"]
        by_tier[tier] = by_tier.get(tier, 0) + 1

    return {
        "total": total,
        "active": active,
        "inactive": inactive,
        "by_subscription_tier": by_tier
    }