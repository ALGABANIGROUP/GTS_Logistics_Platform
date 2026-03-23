from __future__ import annotations

import os
from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.billing.models import Plan, PlanEntitlement, Subscription, SubscriptionAddon
from backend.database.config import get_db_async
from backend.models.user import User
from backend.security.auth import get_current_user


US_COUNTRIES = {"US", "USA", "UNITED_STATES"}
CA_COUNTRIES = {"CA", "CANADA"}
GCC_COUNTRIES = {"AE", "UAE", "KSA", "SA", "SAUDI", "SAUDI_ARABIA", "QA", "QATAR", "KW", "KUWAIT", "BH", "BAHRAIN", "OM", "OMAN"}
EGYPT_COUNTRIES = {"EG", "EGYPT"}

DEFAULT_DEMO_ENTITLEMENTS: Dict[str, Any] = {
    "tms.core": True,
    "pricing.engine": True,
    "ai.dispatcher": False,
    "docs.compliance": False,
    "finance.reports": False,
    "module.loadboard": False,
    "tms.dispatch": False,
    "limits.shipments_per_month": 50,
}


def _normalize_country(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    raw = str(value).strip().upper()
    if raw in ("US_CA", "NA", "NORTH_AMERICA"):
        return "US"
    if raw in US_COUNTRIES:
        return "US"
    if raw in CA_COUNTRIES:
        return "CA"
    if raw in GCC_COUNTRIES:
        return "GCC"
    if raw in EGYPT_COUNTRIES:
        return "EGYPT"
    if raw in ("GLOBAL", "WORLD"):
        return "GLOBAL"
    return raw


def resolve_region(
    *,
    header_country: Optional[str],
    user_country: Optional[str],
    override: Optional[str] = None,
) -> str:
    for candidate in (header_country, user_country, override):
        normalized = _normalize_country(candidate)
        if normalized:
            return normalized
    return "GLOBAL"


def currency_for_region(region: str) -> str:
    region = (region or "GLOBAL").upper()
    if region == "GCC":
        return "AED"
    if region == "EGYPT":
        return "EGP"
    if region == "US":
        return "USD"
    if region == "CA":
        return "CAD"
    return "USD"


def pricing_tier_for_region(region: str) -> str:
    region = (region or "GLOBAL").upper()
    if region == "GCC":
        return "gcc"
    if region == "EGYPT":
        return "egypt"
    if region in ("US", "CA"):
        return "us-ca"
    return "global"


async def resolve_user_from_claims(db: AsyncSession, claims: Dict[str, Any]) -> Optional[User]:
    if not claims:
        return None

    user_id = claims.get("user_id")
    sub = claims.get("sub")
    email = claims.get("email")

    if user_id is None and isinstance(sub, str) and sub.isdigit():
        user_id = int(sub)

    if user_id:
        return await db.scalar(select(User).where(User.id == int(user_id)))

    if isinstance(email, str) and email:
        return await db.scalar(select(User).where(User.email == email))

    if isinstance(sub, str) and "@" in sub:
        return await db.scalar(select(User).where(User.email == sub))

    return None


async def _get_active_subscription(db: AsyncSession, *, user_id: Optional[int], partner_id: Optional[int]) -> Optional[Subscription]:
    try:
        stmt = select(Subscription).where(Subscription.status == "active")
        if user_id is not None:
            stmt = stmt.where(Subscription.user_id == user_id)
        elif partner_id is not None:
            stmt = stmt.where(Subscription.partner_id == partner_id)
        else:
            return None

        stmt = stmt.order_by(Subscription.created_at.desc())
        result = await db.execute(stmt)
        return result.scalars().first()
    except Exception:
        # Fallback when billing tables are missing or unavailable
        return None


async def _get_plan_entitlements(db: AsyncSession, plan_id: str) -> Dict[str, Any]:
    try:
        result = await db.execute(select(PlanEntitlement).where(PlanEntitlement.plan_id == plan_id))
        entitlements: Dict[str, Any] = {}
        for row in result.scalars().all():
            entitlements[row.key] = row.value_json if row.value_json is not None else True
        return entitlements
    except Exception:
        # Fallback if table doesn't exist or query fails
        return dict(DEFAULT_DEMO_ENTITLEMENTS)


def _apply_addons(entitlements: Dict[str, Any], addons: list[SubscriptionAddon]) -> Dict[str, Any]:
    for addon in addons:
        if addon.addon_code == "LOADBOARD" and addon.enabled:
            entitlements["module.loadboard"] = True
    return entitlements


def _finalize_modules(entitlements: Dict[str, Any]) -> list[str]:
    modules = []
    if entitlements.get("tms.core"):
        modules.append("tms")
    if entitlements.get("ai.dispatcher"):
        modules.append("ai")
    if entitlements.get("docs.compliance"):
        modules.append("documents")
    if entitlements.get("finance.reports"):
        modules.append("finance")
    if entitlements.get("module.loadboard"):
        modules.append("loadboard")
    if entitlements.get("tms.dispatch"):
        modules.append("dispatch")
    return modules


async def resolve_entitlements(
    db: AsyncSession,
    user: Optional[User],
    *,
    region: str,
) -> Dict[str, Any]:
    region = (region or "GLOBAL").upper()
    subscription = None
    if user is not None:
        subscription = await _get_active_subscription(db, user_id=user.id, partner_id=None)

    if subscription is None:
        entitlements = dict(DEFAULT_DEMO_ENTITLEMENTS)
        plan_code = "DEMO"
        plan_id = None
        status = "demo"
    else:
        try:
            plan = await db.scalar(select(Plan).where(Plan.key == subscription.plan_id))
            if plan is None:
                entitlements = dict(DEFAULT_DEMO_ENTITLEMENTS)
                plan_code = "DEMO"
                plan_id = None
                status = "demo"
            else:
                entitlements = await _get_plan_entitlements(db, plan.key)
                entitlements = _apply_addons(entitlements, subscription.addons or [])
                plan_code = plan.key
                plan_id = plan.key
                status = subscription.status
        except Exception:
            # Fallback if Plan table doesn't exist or query fails
            entitlements = dict(DEFAULT_DEMO_ENTITLEMENTS)
            plan_code = "DEMO"
            plan_id = None
            status = "demo"

    if region not in ("US", "CA"):
        entitlements["module.loadboard"] = False

    enabled_modules = _finalize_modules(entitlements)

    return {
        "plan_code": plan_code,
        "plan_id": plan_id,
        "entitlements": entitlements,
        "enabled_modules": enabled_modules,
        "subscription_status": status,
        "resolved_at": datetime.utcnow().isoformat(),
    }


def require_entitlement(key: str):
    async def _dep(
        request: Request,
        db: AsyncSession = Depends(get_db_async),
        claims: Dict[str, Any] = Depends(get_current_user),
    ) -> Dict[str, Any]:
        user = await resolve_user_from_claims(db, claims)
        header_country = request.headers.get("X-GTS-COUNTRY")
        override = os.getenv("GTS_COUNTRY_OVERRIDE")
        region = resolve_region(
            header_country=header_country,
            user_country=getattr(user, "country", None),
            override=override,
        )
        resolved = await resolve_entitlements(db, user, region=region)
        if not resolved["entitlements"].get(key):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Entitlement required",
            )
        return resolved

    return _dep


def require_module(name: str):
    async def _dep(
        request: Request,
        db: AsyncSession = Depends(get_db_async),
        claims: Dict[str, Any] = Depends(get_current_user),
    ) -> Dict[str, Any]:
        user = await resolve_user_from_claims(db, claims)
        header_country = request.headers.get("X-GTS-COUNTRY")
        override = os.getenv("GTS_COUNTRY_OVERRIDE")
        region = resolve_region(
            header_country=header_country,
            user_country=getattr(user, "country", None),
            override=override,
        )
        resolved = await resolve_entitlements(db, user, region=region)
        if name not in resolved["enabled_modules"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Module not available",
            )
        return resolved

    return _dep

