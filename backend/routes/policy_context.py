from __future__ import annotations

import os
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database.config import get_db_async  # type: ignore
from backend.security.auth import get_current_user
from backend.security.entitlements import (
    currency_for_region,
    pricing_tier_for_region,
    resolve_entitlements,
    resolve_region,
    resolve_user_from_claims,
)

router = APIRouter(prefix="/api/v1/policy", tags=["policy"])


async def get_optional_current_user(request: Request) -> Optional[Any]:
    """Allow anonymous callers to bootstrap pricing and regional policy context."""
    try:
        return await get_current_user(request)
    except HTTPException as exc:
        if exc.status_code == status.HTTP_401_UNAUTHORIZED:
            return None
        raise


@router.get("/context")
async def policy_context(
    db: AsyncSession = Depends(get_db_async),
    current_user: Optional[Any] = Depends(get_optional_current_user),
    x_gts_country: Optional[str] = Header(None, alias="X-GTS-COUNTRY"),
    region: Optional[str] = Query(None),
) -> Dict[str, Any]:
    user = None
    if isinstance(current_user, dict):
        user = await resolve_user_from_claims(db, current_user)

    env_override = os.getenv("GTS_COUNTRY_OVERRIDE")
    region_code = resolve_region(
        header_country=x_gts_country,
        user_country=getattr(user, "country", None),
        override=region or env_override,
    )
    mode = "HYBRID" if region_code in ("US", "CA") else "TMS"

    resolved = await resolve_entitlements(db, user, region=region_code)
    entitlements = resolved["entitlements"]
    enabled_modules = resolved["enabled_modules"]
    loadboard_enabled = bool(entitlements.get("module.loadboard"))

    currency = currency_for_region(region_code)
    pricing_tier = pricing_tier_for_region(region_code)

    return {
        "country": region_code,
        "region": region_code,
        "mode": mode,
        "loadboard_enabled": loadboard_enabled,
        "entitlements": entitlements,
        "enabled_modules": enabled_modules,
        "currency": currency,
        "pricing_tier": pricing_tier,
        "plan_code": resolved.get("plan_code"),
        "subscription_status": resolved.get("subscription_status"),
    }


__all__ = ["router"]
