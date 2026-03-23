from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Set

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database.config import get_db_async
from backend.security.auth import get_current_user
from backend.security.entitlements import (
    currency_for_region,
    resolve_entitlements,
    resolve_region,
    resolve_user_from_claims,
)
from backend.security.rbac import normalize_role


@dataclass(frozen=True)
class PlanDefinition:
    key: str
    name: str
    description: str
    modules: Dict[str, bool]
    features: Set[str]
    limits: Dict[str, Any]


PLAN_DEFINITIONS: Dict[str, PlanDefinition] = {
    "loadboard": PlanDefinition(
        key="loadboard",
        name="Loadboard",
        description="Loadboard-only access for listings and offers.",
        modules={"tms": False, "loadboard": True, "dispatcher": False, "ai": False},
        features={"loadboard.core", "loadboard.listings", "loadboard.offers"},
        limits={"monthly_listings": 250, "active_offers": 100},
    ),
    "tms": PlanDefinition(
        key="tms",
        name="TMS Core",
        description="Core TMS features for shipments and operations.",
        modules={"tms": True, "loadboard": False, "dispatcher": False, "ai": False},
        features={"tms.core", "tms.shipments", "tms.fleet"},
        limits={"shipments_per_month": 250, "drivers": 50},
    ),
    "dispatcher_plus": PlanDefinition(
        key="dispatcher_plus",
        name="Dispatcher Plus",
        description="Dispatcher tools with assignment workflows.",
        modules={"tms": True, "loadboard": False, "dispatcher": True, "ai": False},
        features={"tms.core", "tms.shipments", "tms.fleet", "dispatcher.core", "dispatch.assign", "ai.dispatcher"},
        limits={"shipments_per_month": 750, "drivers": 150},
    ),
    "unified_pro": PlanDefinition(
        key="unified_pro",
        name="Unified Pro",
        description="Unified platform with TMS, dispatcher, loadboard, and AI access.",
        modules={"tms": True, "loadboard": True, "dispatcher": True, "ai": True},
        features={
            "tms.core",
            "tms.shipments",
            "tms.fleet",
            "dispatcher.core",
            "dispatch.assign",
            "loadboard.core",
            "loadboard.listings",
            "loadboard.offers",
            "ai.core",
            "freight_access",
            "finance_access",
            "documents_access",
            "cs_access",
            "safety_access",
            "sales_access",
            "strategy_access",
            "legal_access",
            "mapleload_access",
        },
        limits={"shipments_per_month": 3000, "drivers": 500, "active_offers": 500},
    ),
}


PLAN_CODE_ALIASES = {
    "DEMO": "tms",
    "FREE": "tms",
    "STARTER": "tms",
    "PRO": "dispatcher_plus",
    "GROWTH": "dispatcher_plus",
    "PROFESSIONAL": "unified_pro",
    "ENTERPRISE": "unified_pro",
    "LOADBOARD": "loadboard",
    "TMS": "tms",
    "DISPATCHER_PLUS": "dispatcher_plus",
    "UNIFIED_PRO": "unified_pro",
}


ROLE_PERMISSIONS: Dict[str, Set[str]] = {
    "super_admin": {
        "shipments.view",
        "shipments.create",
        "shipments.update",
        "shipments.delete",
        "drivers.view",
        "drivers.manage",
        "dispatch.assign",
        "bots.run",
        "bots.configure",
    },
    "owner": {
        "shipments.view",
        "shipments.create",
        "shipments.update",
        "shipments.delete",
        "drivers.view",
        "drivers.manage",
        "dispatch.assign",
        "bots.run",
        "bots.configure",
    },
    "admin": {
        "shipments.view",
        "shipments.create",
        "shipments.update",
        "shipments.delete",
        "drivers.view",
        "drivers.manage",
        "dispatch.assign",
        "bots.run",
        "bots.configure",
    },
    "system_admin": {
        "shipments.view",
        "shipments.create",
        "shipments.update",
        "shipments.delete",
        "drivers.view",
        "drivers.manage",
        "dispatch.assign",
        "bots.run",
        "bots.configure",
    },
    "manager": {
        "shipments.view",
        "shipments.create",
        "shipments.update",
        "drivers.view",
        "dispatch.assign",
        "bots.run",
    },
    "ops": {
        "shipments.view",
        "shipments.create",
        "shipments.update",
        "drivers.view",
        "drivers.manage",
        "dispatch.assign",
        "bots.run",
    },
    "dispatcher": {"shipments.view", "drivers.view", "dispatch.assign"},
    "driver": {"shipments.view", "drivers.view", "drivers.manage"},
    "finance": {"shipments.view"},
    "support": {"shipments.view"},
    "partner": {"shipments.view"},
    "subscription_user": {"shipments.view"},
    "user": {"shipments.view"},
    "guest": set(),
}


def _normalize_plan_key(raw: Optional[str]) -> Optional[str]:
    if not raw:
        return None
    key = str(raw).strip().lower()
    return key or None


def _infer_plan_key(
    entitlements: Dict[str, Any],
    *,
    plan_code: Optional[str],
    tenant_plan: Optional[str],
) -> str:
    for candidate in (tenant_plan, plan_code):
        if not candidate:
            continue
        alias = PLAN_CODE_ALIASES.get(str(candidate).strip().upper())
        if alias:
            return alias
        normalized = _normalize_plan_key(candidate)
        if normalized and normalized in PLAN_DEFINITIONS:
            return normalized

    if entitlements.get("module.loadboard") and not entitlements.get("tms.core"):
        return "loadboard"
    if entitlements.get("tms.core") and entitlements.get("ai.dispatcher"):
        if entitlements.get("module.loadboard"):
            return "unified_pro"
        return "dispatcher_plus"
    if entitlements.get("tms.core"):
        return "tms"
    return "tms"


def _derive_features(plan: PlanDefinition, entitlements: Dict[str, Any]) -> Set[str]:
    features = set(plan.features)
    for key, value in entitlements.items():
        if value is True:
            features.add(str(key))
    return features


def _derive_limits(plan: PlanDefinition, entitlements: Dict[str, Any]) -> Dict[str, Any]:
    limits = dict(plan.limits)
    for key, value in entitlements.items():
        if key.startswith("limits."):
            limits[key.replace("limits.", "", 1)] = value
    return limits


def _apply_role_feature_rules(role: str, features: Set[str]) -> Set[str]:
    if role == "guest":
        return set()
    return features


def _filter_permissions(perms: Iterable[str], *, features: Set[str], modules: Dict[str, bool]) -> Set[str]:
    filtered: Set[str] = set()
    has_shipments = ("tms.core" in features) or ("tms.shipments" in features) or modules.get("tms")
    has_drivers = ("tms.fleet" in features) or modules.get("dispatcher") or ("dispatcher.core" in features)
    has_dispatch = ("dispatch.assign" in features) or ("dispatcher.core" in features) or modules.get("dispatcher")

    for perm in perms:
        if perm.startswith("shipments.") and not has_shipments:
            continue
        if perm.startswith("drivers.") and not has_drivers:
            continue
        if perm == "dispatch.assign" and not has_dispatch:
            continue
        filtered.add(perm)
    return filtered


async def _try_resolve_tenant(request: Request, db: AsyncSession) -> Optional[Any]:
    try:
        from backend.security.tenant_resolver import TenantResolver  # type: ignore

        return await TenantResolver.resolve_tenant(request, db)
    except Exception:
        return None


async def build_auth_me_payload(
    request: Request,
    db: AsyncSession,
    claims: Dict[str, Any],
) -> Dict[str, Any]:
    user = await resolve_user_from_claims(db, claims)
    user_status = "active" if getattr(user, "is_active", True) else "pending"
    token_role = normalize_role(claims.get("token_role") or claims.get("role"))
    db_role = normalize_role(getattr(user, "role", None))
    effective_role = normalize_role(claims.get("effective_role") or db_role or claims.get("role"))
    role = effective_role or db_role or token_role or "user"

    header_country = request.headers.get("X-GTS-COUNTRY")
    region = resolve_region(
        header_country=header_country,
        user_country=getattr(user, "country", None),
        override=None,
    )
    entitlements_resolved = await resolve_entitlements(db, user, region=region)
    entitlements = entitlements_resolved.get("entitlements") or {}

    tenant = await _try_resolve_tenant(request, db)
    tenant_plan = _normalize_plan_key(getattr(tenant, "plan", None)) if tenant else None
    plan_key = _infer_plan_key(
        entitlements,
        plan_code=entitlements_resolved.get("plan_code"),
        tenant_plan=tenant_plan,
    )
    plan = PLAN_DEFINITIONS.get(plan_key, PLAN_DEFINITIONS["tms"])

    features = _derive_features(plan, entitlements)
    features = _apply_role_feature_rules(role, features)

    modules = dict(plan.modules)
    modules["tms"] = bool(entitlements.get("tms.core") or modules.get("tms") or ("tms.core" in features))
    modules["dispatcher"] = bool(
        entitlements.get("tms.dispatch")
        or entitlements.get("ai.dispatcher")
        or modules.get("dispatcher")
        or ("dispatcher.core" in features)
    )
    modules["loadboard"] = bool(entitlements.get("module.loadboard") or modules.get("loadboard"))
    has_ai_feature = any(str(feature).startswith("ai.") for feature in features)
    modules["ai"] = bool(
        entitlements.get("ai.dispatcher")
        or modules.get("ai")
        or ("ai.core" in features)
        or has_ai_feature
    )

    base_permissions = ROLE_PERMISSIONS.get(role, ROLE_PERMISSIONS["user"])
    permissions = _filter_permissions(base_permissions, features=features, modules=modules)

    try:
        from backend.ai.access_engine import any_visible_bots  # type: ignore

        if any_visible_bots(
            role=role,
            features=features,
            permissions=permissions,
            plan_key=plan.key,
            modules=modules,
        ):
            modules["ai"] = True
    except Exception:
        pass

    is_super_admin = role in {"super_admin", "owner"}
    if is_super_admin:
        for key in list(modules.keys()):
            modules[key] = True
        modules["admin"] = True
        features.update({"ai.core", "ai.botos", "ai.dispatcher"})

    limits = _derive_limits(plan, entitlements)

    # Get visible bots
    visible_bots = []
    try:
        from backend.ai.access_engine import get_visible_bots  # type: ignore
        visible_bots = get_visible_bots(
            role=role,
            features=features,
            permissions=permissions,
            plan_key=plan.key,
            modules=modules,
        )
    except Exception:
        # Fallback: some default bots
        visible_bots = ["finance_bot", "freight_broker", "dev_maintenance"]

    return {
        "user": {
            "id": getattr(user, "id", None),
            "email": getattr(user, "email", None),
            "name": getattr(user, "full_name", None) or getattr(user, "email", None),
            "full_name": getattr(user, "full_name", None),
            "username": getattr(user, "username", None),
            "role": role,
            "effective_role": effective_role,
            "db_role": db_role,
            "token_role": token_role,
            "is_active": getattr(user, "is_active", True),
            "user_status": user_status,
            "country": getattr(user, "country", None),
            "user_type": getattr(user, "user_type", None),
            "permissions": sorted(permissions),
        },
        "tenant": {
            "id": getattr(tenant, "id", None) if tenant else None,
            "name": getattr(tenant, "name", None) if tenant else None,
            "plan_key": plan.key,
            "status": getattr(tenant, "status", None) if tenant else None,
        },
        "entitlements": {
            "features": sorted(features),
            "modules": list(modules.keys()),
            "bots": visible_bots,
        },
        "plan": {
            "name": plan.name,
            "description": plan.description,
            "modules": plan.modules,
            "limits": limits,
        },
        "system": {
            "timezone": "UTC",
            "language": "en",
            "currency": currency_for_region(region),
        },
    }


def require_module(module_key: str):
    async def _dep(
        request: Request,
        db: AsyncSession = Depends(get_db_async),
        claims: Dict[str, Any] = Depends(get_current_user),
    ) -> Dict[str, Any]:
        payload = await build_auth_me_payload(request, db, claims)
        entitlements = payload.get("entitlements") or {}
        enabled_modules = set(entitlements.get("modules") or [])
        plan_modules = payload.get("plan", {}).get("modules", {}) or {}
        if module_key not in enabled_modules and not plan_modules.get(module_key):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Module not available")
        return payload

    return _dep


def require_any_module(module_keys: Iterable[str]):
    module_keys = [str(key) for key in module_keys if key]

    async def _dep(
        request: Request,
        db: AsyncSession = Depends(get_db_async),
        claims: Dict[str, Any] = Depends(get_current_user),
    ) -> Dict[str, Any]:
        payload = await build_auth_me_payload(request, db, claims)
        entitlements = payload.get("entitlements") or {}
        enabled_modules = set(entitlements.get("modules") or [])
        plan_modules = payload.get("plan", {}).get("modules", {}) or {}
        if not any((key in enabled_modules) or plan_modules.get(key) for key in module_keys):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Module not available")
        return payload

    return _dep


def require_feature(feature_key: str):
    async def _dep(
        request: Request,
        db: AsyncSession = Depends(get_db_async),
        claims: Dict[str, Any] = Depends(get_current_user),
    ) -> Dict[str, Any]:
        payload = await build_auth_me_payload(request, db, claims)
        features = set((payload.get("entitlements") or {}).get("features") or [])
        if feature_key not in features:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Feature not available")
        return payload

    return _dep


def require_any_feature(feature_keys: Iterable[str]):
    feature_keys = [str(key) for key in feature_keys if key]

    async def _dep(
        request: Request,
        db: AsyncSession = Depends(get_db_async),
        claims: Dict[str, Any] = Depends(get_current_user),
    ) -> Dict[str, Any]:
        payload = await build_auth_me_payload(request, db, claims)
        features = set((payload.get("entitlements") or {}).get("features") or [])
        if not any(key in features for key in feature_keys):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Feature not available")
        return payload

    return _dep


def require_permission(permission_key: str):
    async def _dep(
        request: Request,
        db: AsyncSession = Depends(get_db_async),
        claims: Dict[str, Any] = Depends(get_current_user),
    ) -> Dict[str, Any]:
        payload = await build_auth_me_payload(request, db, claims)
        perms = set(payload.get("user", {}).get("permissions") or [])
        if permission_key not in perms:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission not granted")
        return payload

    return _dep
