from __future__ import annotations

from typing import Optional

from fastapi import Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.ext.asyncio import AsyncSession

try:
    import jwt  # type: ignore
except Exception:  # pragma: no cover
    from jose import jwt  # type: ignore
from backend.database.session import get_async_session
from backend.models.tenant import Tenant
from backend.security.auth import JWT_SECRET_KEY, JWT_ALGORITHM


DEFAULT_EXCLUDED_SUBS = {"www", "app", "api", "admin"}


class TenantResolver:
    _table_missing: bool = False  # short-circuit if tenants table is absent

    @staticmethod
    async def resolve_tenant(
        request: Request,
        db: AsyncSession,
    ) -> Optional[Tenant]:
        """
        FAIL CLOSED resolver: No default tenant fallback.
        Tenant must be explicitly identified via subdomain, header, or JWT.
        """
        if TenantResolver._table_missing:
            return None

        tenant_sources = []  # Track which sources identified a tenant
        resolved_tenants = set()  # Track which tenants were resolved

        try:
            # 1) Subdomain (most secure and explicit)
            host = (request.headers.get("host") or "").split(":")[0].strip().lower()
            if host:
                parts = host.split(".")
                subdomain = parts[0] if len(parts) >= 3 else None
                if subdomain and subdomain not in DEFAULT_EXCLUDED_SUBS:
                    res = await db.execute(select(Tenant).where(Tenant.subdomain == subdomain))
                    tenant = res.scalar_one_or_none()
                    if tenant:
                        tenant_sources.append(("subdomain", tenant.id))
                        resolved_tenants.add(tenant.id)

            # 2) Header `X-Tenant-ID`
            tenant_id = (request.headers.get("X-Tenant-ID") or request.headers.get("x-tenant-id") or "").strip()
            if tenant_id:
                res = await db.execute(select(Tenant).where(Tenant.id == tenant_id))
                tenant = res.scalar_one_or_none()
                if tenant:
                    tenant_sources.append(("header", tenant.id))
                    resolved_tenants.add(tenant.id)

            # 3) JWT claim `tenant_id`
            auth = request.headers.get("authorization") or ""
            if auth.lower().startswith("bearer "):
                token = auth.split()[1]
                try:
                    payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
                    claim_tid = str(payload.get("tenant_id") or "").strip()
                    if claim_tid:
                        res = await db.execute(select(Tenant).where(Tenant.id == claim_tid))
                        tenant = res.scalar_one_or_none()
                        if tenant:
                            tenant_sources.append(("jwt", tenant.id))
                            resolved_tenants.add(tenant.id)
                except Exception:
                    # Ignore token errors for resolver fallback
                    pass

        except ProgrammingError as exc:
            # Suppress noisy warnings when the tenants table is not yet migrated
            msg = str(exc).lower()
            if "relation" in msg and "tenants" in msg and "does not exist" in msg:
                TenantResolver._table_missing = True
                return None
            raise

        # Conflict detection: multiple sources disagree
        if len(resolved_tenants) > 1:
            raise HTTPException(
                status_code=400,
                detail="Conflicting tenant identification (subdomain, header, JWT disagree)"
            )

        # FAIL CLOSED: No default tenant allowed
        if len(resolved_tenants) == 0:
            return None  # Will raise 400 in get_tenant()
        
        # Return the unique tenant
        tenant_id_to_fetch = resolved_tenants.pop()
        res = await db.execute(select(Tenant).where(Tenant.id == tenant_id_to_fetch))
        return res.scalar_one_or_none()


async def get_tenant(
    request: Request,
    db: AsyncSession = Depends(get_async_session),
) -> Tenant:
    tenant = await TenantResolver.resolve_tenant(request, db)
    if not tenant:
        raise HTTPException(status_code=400, detail="Tenant not found")
    return tenant


async def get_tenant_id(
    request: Request,
    db: AsyncSession = Depends(get_async_session),
) -> str:
    tenant = await get_tenant(request, db)
    return tenant.id

