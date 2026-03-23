from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.services.tenant_admin_store import (
    list_admin_tenants,
    get_admin_tenant,
    create_admin_tenant,
    update_admin_tenant,
    delete_admin_tenant,
)

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

router = APIRouter(prefix="/api/v1/admin/tenants", tags=["admin", "tenants"])


def _normalize_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "company_name": payload.get("companyName") or payload.get("company_name"),
        "domain": payload.get("domain"),
        "status": payload.get("status") or "active",
        "users_count": payload.get("usersCount") or payload.get("users_count") or 0,
        "max_users": payload.get("maxUsers") or payload.get("max_users") or 0,
        "plan": payload.get("plan") or "basic",
        "subscription_end": payload.get("subscriptionEnd") or payload.get("subscription_end"),
        "created_date": payload.get("createdDate") or payload.get("created_date"),
        "contact_email": payload.get("contactEmail") or payload.get("contact_email"),
        "contact_phone": payload.get("contactPhone") or payload.get("contact_phone"),
        "storage_used": payload.get("storageUsed") or payload.get("storage_used"),
        "total_storage": payload.get("totalStorage") or payload.get("total_storage"),
    }


@router.get("")
async def list_tenants(db: AsyncSession = Depends(get_db_async)):
    tenants = await list_admin_tenants(db)
    return {"tenants": tenants}


@router.get("/{tenant_id}")
async def read_tenant(tenant_id: str, db: AsyncSession = Depends(get_db_async)):
    tenant = await get_admin_tenant(db, tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return tenant


@router.post("")
async def create_tenant(payload: Dict[str, Any] = Body(...), db: AsyncSession = Depends(get_db_async)):
    tenant_id = payload.get("id") or payload.get("tenant_id")
    if not tenant_id:
        raise HTTPException(status_code=400, detail="Tenant id is required")
    data = _normalize_payload(payload)
    created = await create_admin_tenant(db, tenant_id, data)
    return created


@router.put("/{tenant_id}")
async def update_tenant(
    tenant_id: str, payload: Dict[str, Any] = Body(...), db: AsyncSession = Depends(get_db_async)
):
    data = _normalize_payload(payload)
    updated = await update_admin_tenant(db, tenant_id, data)
    return updated


@router.delete("/{tenant_id}")
async def remove_tenant(tenant_id: str, db: AsyncSession = Depends(get_db_async)):
    await delete_admin_tenant(db, tenant_id)
    return {"ok": True}
