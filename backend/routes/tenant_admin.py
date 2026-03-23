from __future__ import annotations

from datetime import date
from typing import Any, Dict

from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database.session import get_async_session
from backend.models.tenant import Tenant
from backend.security.auth import require_roles
from backend.services.tenant_admin_store import (
    create_admin_tenant,
    delete_admin_tenant,
    get_admin_tenant,
    list_admin_tenants,
    update_admin_tenant,
)


def _first_value(payload: Dict[str, Any], *keys: str, default: Any = None) -> Any:
    for key in keys:
        if key in payload and payload[key] is not None:
            return payload[key]
    return default


def _normalize_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "company_name": _first_value(payload, "companyName", "company_name", "name", default=""),
        "domain": _first_value(payload, "domain", "domain_name", default=""),
        "status": _first_value(payload, "status", default="active"),
        "users_count": int(_first_value(payload, "usersCount", "users_count", default=0) or 0),
        "max_users": int(_first_value(payload, "maxUsers", "max_users", default=0) or 0),
        "plan": _first_value(payload, "plan", default="basic"),
        "subscription_end": _first_value(payload, "subscriptionEnd", "subscription_end"),
        "created_date": _first_value(payload, "createdDate", "created_date"),
        "contact_email": _first_value(payload, "contactEmail", "contact_email", "email"),
        "contact_phone": _first_value(payload, "contactPhone", "contact_phone", "phone"),
        "storage_used": _first_value(payload, "storageUsed", "storage_used"),
        "total_storage": _first_value(payload, "totalStorage", "total_storage"),
        "subdomain": _first_value(payload, "subdomain"),
    }


def _derive_tenant_id(payload: Dict[str, Any]) -> str:
    tenant_id = (
        _first_value(payload, "id", "tenant_id", "subdomain", default="") or ""
    ).strip()
    domain = str(_first_value(payload, "domain", "domain_name", default="") or "").strip()
    if not tenant_id and domain:
        tenant_id = domain.split(".", 1)[0]
    return tenant_id


router = APIRouter(
    prefix="/api/admin/tenants",
    tags=["Tenants"],
    dependencies=[Depends(require_roles(["admin", "system_admin", "super_admin", "owner"]))],
)
router_v1 = APIRouter(
    prefix="/api/v1/admin/tenants",
    tags=["Tenants"],
    dependencies=[Depends(require_roles(["admin", "system_admin", "super_admin", "owner"]))],
)


@router.get("")
async def list_tenants(db: AsyncSession = Depends(get_async_session)) -> Dict[str, Any]:
    tenants = await list_admin_tenants(db)
    return {"tenants": tenants}


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_tenant(
    payload: Dict[str, Any] = Body(default={}),
    db: AsyncSession = Depends(get_async_session),
) -> Dict[str, Any]:
    normalized = _normalize_payload(payload)
    tenant_id = _derive_tenant_id(payload)
    if not tenant_id:
        raise HTTPException(status_code=400, detail="id or subdomain is required")

    if not normalized.get("company_name") or not normalized.get("domain"):
        raise HTTPException(status_code=400, detail="companyName and domain are required")

    existing = await get_admin_tenant(db, tenant_id)
    if existing:
        raise HTTPException(status_code=409, detail="Tenant already exists")

    if not normalized.get("created_date"):
        normalized["created_date"] = date.today().isoformat()

    result = await db.execute(select(Tenant).where(Tenant.id == tenant_id))
    tenant = result.scalar_one_or_none()
    if not tenant:
        tenant = Tenant(
            id=tenant_id,
            subdomain=normalized.get("subdomain") or tenant_id,
            name=normalized.get("company_name"),
            is_default=False,
        )
        db.add(tenant)
    else:
        tenant.subdomain = normalized.get("subdomain") or tenant.subdomain
        tenant.name = normalized.get("company_name") or tenant.name
    await db.commit()

    created = await create_admin_tenant(db, tenant_id, normalized)
    return created


@router.put("/{tenant_id}")
async def update_tenant(
    tenant_id: str,
    payload: Dict[str, Any] = Body(default={}),
    db: AsyncSession = Depends(get_async_session),
) -> Dict[str, Any]:
    existing = await get_admin_tenant(db, tenant_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Tenant not found")

    normalized = _normalize_payload({**existing, **payload})
    updated = await update_admin_tenant(db, tenant_id, normalized)

    result = await db.execute(select(Tenant).where(Tenant.id == tenant_id))
    tenant = result.scalar_one_or_none()
    if tenant:
        tenant.subdomain = normalized.get("subdomain") or tenant.subdomain
        tenant.name = normalized.get("company_name") or tenant.name
        await db.commit()

    return updated


@router.delete("/{tenant_id}", status_code=status.HTTP_200_OK)
async def delete_tenant(
    tenant_id: str,
    db: AsyncSession = Depends(get_async_session),
) -> Dict[str, Any]:
    existing = await get_admin_tenant(db, tenant_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Tenant not found")
    await delete_admin_tenant(db, tenant_id)
    return {"ok": True}


@router_v1.get("")
async def list_tenants_v1(db: AsyncSession = Depends(get_async_session)) -> Dict[str, Any]:
    return await list_tenants(db)


@router_v1.post("", status_code=status.HTTP_201_CREATED)
async def create_tenant_v1(
    payload: Dict[str, Any] = Body(default={}),
    db: AsyncSession = Depends(get_async_session),
) -> Dict[str, Any]:
    return await create_tenant(payload, db)


@router_v1.put("/{tenant_id}")
async def update_tenant_v1(
    tenant_id: str,
    payload: Dict[str, Any] = Body(default={}),
    db: AsyncSession = Depends(get_async_session),
) -> Dict[str, Any]:
    return await update_tenant(tenant_id, payload, db)


@router_v1.delete("/{tenant_id}", status_code=status.HTTP_200_OK)
async def delete_tenant_v1(
    tenant_id: str,
    db: AsyncSession = Depends(get_async_session),
) -> Dict[str, Any]:
    return await delete_tenant(tenant_id, db)


combined_router = APIRouter()
combined_router.include_router(router)
combined_router.include_router(router_v1)

router = combined_router

__all__ = ["router", "combined_router"]

