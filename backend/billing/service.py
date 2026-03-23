from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.billing.models import Plan
from backend.security.entitlements import resolve_region

FEATURE_LABELS = {
    "tms.core": "TMS Core",
    "pricing.engine": "Pricing Engine",
    "ai.dispatcher": "AI Dispatcher",
    "docs.compliance": "Documents Compliance",
    "finance.reports": "Finance Reports",
    "module.loadboard": "Load Board",
}

PLAN_ORDER = ["FREE", "STARTER", "GROWTH", "PROFESSIONAL", "ENTERPRISE"]
CATALOG_PATH = Path(__file__).resolve().parents[1] / "data" / "pricing_catalog.json"


def _build_default_plans(currency: str) -> List[Dict[str, Any]]:
    return [
        {
            "code": "FREE",
            "name": "Free",
            "description": "GPS tracking, invoicing, and a basic dashboard for a single operator.",
            "currency": currency,
            "price_amount": 0,
            "is_demo": False,
            "is_free": True,
            "suitable_for": ["Solo drivers", "Very small fleets"],
            "highlights": [
                "1 vehicle",
                "1 user",
                "GPS tracking",
                "Basic invoicing",
                "Basic dashboard",
            ],
            "addons": [],
            "entitlements": {
                "tms.core": True,
                "pricing.engine": True,
                "ai.dispatcher": False,
                "docs.compliance": False,
                "finance.reports": False,
                "module.loadboard": False,
                "limits.vehicles": 1,
                "limits.users": 1,
            },
        },
        {
            "code": "STARTER",
            "name": "Starter",
            "description": "Trip operations and live visibility for small transport teams.",
            "currency": currency,
            "price_amount": 9,
            "is_demo": False,
            "is_free": False,
            "suitable_for": ["Small transport companies"],
            "highlights": [
                "5 vehicles",
                "3 users",
                "Trip management",
                "Real-time tracking",
                "Invoicing",
                "Basic reports",
            ],
            "addons": [],
            "entitlements": {
                "tms.core": True,
                "pricing.engine": True,
                "ai.dispatcher": True,
                "docs.compliance": True,
                "finance.reports": False,
                "module.loadboard": False,
                "limits.vehicles": 5,
                "limits.users": 3,
            },
        },
        {
            "code": "GROWTH",
            "name": "Growth",
            "description": "Driver coordination, alerts, and finance visibility for growing fleets.",
            "currency": currency,
            "price_amount": 19,
            "is_demo": False,
            "is_free": False,
            "suitable_for": ["Mid-size transport companies"],
            "highlights": [
                "15 vehicles",
                "7 users",
                "Driver management",
                "Smart alerts",
                "Financial reports",
            ],
            "addons": [],
            "entitlements": {
                "tms.core": True,
                "pricing.engine": True,
                "ai.dispatcher": True,
                "docs.compliance": True,
                "finance.reports": True,
                "module.loadboard": True,
                "limits.vehicles": 15,
                "limits.users": 7,
            },
        },
        {
            "code": "PROFESSIONAL",
            "name": "Professional",
            "description": "Advanced analytics and document control for high-volume logistics teams.",
            "currency": currency,
            "price_amount": 39,
            "is_demo": False,
            "is_free": False,
            "suitable_for": ["Large transport companies"],
            "highlights": [
                "40 vehicles",
                "15 users",
                "Advanced analytics",
                "Document management",
                "API integration",
            ],
            "addons": [],
            "entitlements": {
                "tms.core": True,
                "pricing.engine": True,
                "ai.dispatcher": True,
                "docs.compliance": True,
                "finance.reports": True,
                "module.loadboard": True,
                "limits.vehicles": 40,
                "limits.users": 15,
            },
        },
        {
            "code": "ENTERPRISE",
            "name": "Enterprise",
            "description": "Full platform access with bots and marketplace support for enterprise logistics.",
            "currency": currency,
            "price_amount": 79,
            "is_demo": False,
            "is_free": False,
            "suitable_for": ["Large enterprises", "Brokerages", "Logistics companies"],
            "highlights": [
                "Unlimited vehicles",
                "Unlimited users",
                "All features",
                "Full Bots Package",
                "Freight Marketplace",
            ],
            "addons": [],
            "entitlements": {
                "tms.core": True,
                "pricing.engine": True,
                "ai.dispatcher": True,
                "docs.compliance": True,
                "finance.reports": True,
                "module.loadboard": True,
                "limits.vehicles": -1,
                "limits.users": -1,
            },
        },
    ]

DEFAULT_PLANS: Dict[str, List[Dict[str, Any]]] = {
    "GLOBAL": _build_default_plans("USD"),
    "US": _build_default_plans("USD"),
    "CA": _build_default_plans("CAD"),
}


def get_pricing_extras(region: str) -> Dict[str, Any]:
    currency = "CAD" if region == "CA" else "USD"
    return {
        "vehicle_pricing": [
            {"code": "VEHICLE_UP_TO_5", "name": "Up to 5 vehicles", "price_amount": 3, "currency": currency, "unit": "vehicle / month"},
            {"code": "VEHICLE_6_TO_20", "name": "6 - 20 vehicles", "price_amount": 2, "currency": currency, "unit": "vehicle / month"},
            {"code": "VEHICLE_OVER_20", "name": "More than 20 vehicles", "price_amount": 1.5, "currency": currency, "unit": "vehicle / month"},
        ],
        "user_pricing": [
            {"code": "ADDITIONAL_USER", "name": "Additional User", "price_amount": 2, "currency": currency, "unit": "user / month"},
            {"code": "ADMIN_USER", "name": "Administrative User", "price_amount": 3, "currency": currency, "unit": "user / month"},
        ],
        "bot_pricing": [
            {"code": "FREIGHT_BOT", "name": "Freight Bot (Freight optimization)", "price_amount": 3, "currency": currency, "unit": "month"},
            {"code": "FINANCE_BOT", "name": "Finance Bot (Billing & payments)", "price_amount": 3, "currency": currency, "unit": "month"},
            {"code": "DISPATCHER_BOT", "name": "Dispatcher Bot (Load dispatching)", "price_amount": 3, "currency": currency, "unit": "month"},
            {"code": "DOCUMENTS_BOT", "name": "Documents Bot (Document management)", "price_amount": 2, "currency": currency, "unit": "month"},
            {"code": "CUSTOMER_SERVICE_BOT", "name": "Customer Service Bot", "price_amount": 2, "currency": currency, "unit": "month"},
            {"code": "SAFETY_BOT", "name": "Safety Bot", "price_amount": 2, "currency": currency, "unit": "month"},
            {"code": "SYSTEM_MONITOR_BOT", "name": "System Monitor Bot", "price_amount": 2, "currency": currency, "unit": "month"},
        ],
        "bot_bundle": {
            "code": "BOTS_FULL_BUNDLE",
            "name": "Full Bots Package",
            "price_amount": 12,
            "currency": currency,
            "unit": "month",
        },
        "extra_services": {
            "automation": [
                {"code": "AUTO_INVOICING", "name": "Automated Invoicing", "price_amount": 2, "currency": currency, "unit": "month"},
                {"code": "ADVANCED_FINANCIAL_REPORTS", "name": "Advanced Financial Reports", "price_amount": 2, "currency": currency, "unit": "month"},
            ],
            "analytics": [
                {"code": "ROUTE_ANALYTICS", "name": "Route Analytics", "price_amount": 2, "currency": currency, "unit": "month"},
                {"code": "FUEL_ANALYTICS", "name": "Fuel Analytics", "price_amount": 2, "currency": currency, "unit": "month"},
            ],
            "integrations": [
                {"code": "API_INTEGRATION", "name": "API Integration", "price_amount": 5, "currency": currency, "unit": "month"},
            ],
        },
        "transaction_fees": {
            "supported_gateways": ["Stripe"],
            "platform_fee_percent": 1.0,
            "notes": ["Payments can be processed through gateways such as Stripe."],
        },
    }


def _default_catalog(region: str) -> Dict[str, Any]:
    normalized = region if region in DEFAULT_PLANS else "GLOBAL"
    extras = get_pricing_extras(normalized)
    return {
        "country": normalized,
        "plans": deepcopy(_sort_plans(DEFAULT_PLANS.get(normalized, DEFAULT_PLANS["GLOBAL"]))),
        "addons": [],
        "vehicle_pricing": deepcopy(extras.get("vehicle_pricing", [])),
        "user_pricing": deepcopy(extras.get("user_pricing", [])),
        "bot_pricing": deepcopy(extras.get("bot_pricing", [])),
        "bot_bundle": deepcopy(extras.get("bot_bundle")),
        "extra_services": deepcopy(extras.get("extra_services", {})),
        "transaction_fees": deepcopy(extras.get("transaction_fees", {})),
    }


def _normalize_region(country: Optional[str]) -> str:
    region = resolve_region(header_country=country, user_country=None, override=None)
    return region if region in DEFAULT_PLANS else "GLOBAL"


def _load_catalog_store() -> Dict[str, Any]:
    if not CATALOG_PATH.exists():
        return {}
    try:
        raw = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
        return raw if isinstance(raw, dict) else {}
    except Exception:
        return {}


def _write_catalog_store(data: Dict[str, Any]) -> None:
    CATALOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CATALOG_PATH.write_text(json.dumps(data, ensure_ascii=True, indent=2), encoding="utf-8")


def get_pricing_catalog(country: Optional[str]) -> Dict[str, Any]:
    region = _normalize_region(country)
    store = _load_catalog_store()
    catalog = store.get(region)
    if isinstance(catalog, dict):
        merged = _default_catalog(region)
        merged.update(catalog)
        merged["country"] = region
        merged["plans"] = _sort_plans(list(merged.get("plans", [])))
        return merged
    return _default_catalog(region)


def save_pricing_catalog(country: Optional[str], catalog: Dict[str, Any]) -> Dict[str, Any]:
    region = _normalize_region(country)
    payload = _default_catalog(region)
    payload.update(catalog or {})
    payload["country"] = region
    payload["plans"] = _sort_plans(list(payload.get("plans", [])))

    store = _load_catalog_store()
    store[region] = payload
    _write_catalog_store(store)
    return payload


def _sort_plans(plans: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    order = {code: idx for idx, code in enumerate(PLAN_ORDER)}
    return sorted(plans, key=lambda p: order.get(p.get("code", ""), 999))


def _features_from_entitlements(entitlements: Dict[str, Any]) -> List[str]:
    features = []
    for key, label in FEATURE_LABELS.items():
        if entitlements.get(key):
            features.append(label)
    return features


def _limits_from_entitlements(entitlements: Dict[str, Any]) -> Dict[str, Any]:
    limits: Dict[str, Any] = {}
    for key, value in entitlements.items():
        if key.startswith("limits."):
            limits[key.replace("limits.", "", 1)] = value
    return limits


def _resolve_plan_code_value(plan: Plan) -> str:
    return str(getattr(plan, "code", None) or getattr(plan, "key", "")).upper()


def _resolve_plan_name_value(plan: Plan) -> str:
    return str(
        getattr(plan, "name", None)
        or getattr(plan, "name_en", None)
        or getattr(plan, "name_ar", None)
        or _resolve_plan_code_value(plan).title()
    )


def _resolve_plan_price_value(plan: Plan) -> float:
    raw_price = getattr(plan, "price_amount", None)
    if raw_price is None:
        raw_price = getattr(plan, "price_monthly", None)
    return float(raw_price) if raw_price is not None else 0.0


def _resolve_plan_features_value(plan: Plan, entitlements: Dict[str, Any]) -> List[str]:
    if entitlements:
        return _features_from_entitlements(entitlements)
    raw_features = getattr(plan, "features", None)
    if isinstance(raw_features, list):
        return [str(item) for item in raw_features]
    return []


def _resolve_plan_limits_value(plan: Plan, entitlements: Dict[str, Any]) -> Dict[str, Any]:
    if entitlements:
        return _limits_from_entitlements(entitlements)
    raw_limits = getattr(plan, "limits", None)
    if isinstance(raw_limits, dict):
        return raw_limits
    return {}


def _plan_dict(plan: Plan, entitlements: Dict[str, Any], region: str) -> Dict[str, Any]:
    price = _resolve_plan_price_value(plan)
    currency = getattr(plan, "currency", None) or ("CAD" if region == "CA" else "USD")
    features = _resolve_plan_features_value(plan, entitlements)
    limits = _resolve_plan_limits_value(plan, entitlements)
    return {
        "code": _resolve_plan_code_value(plan),
        "name": _resolve_plan_name_value(plan),
        "description": getattr(plan, "description", None),
        "currency": currency,
        "price_amount": price,
        "is_demo": bool(getattr(plan, "is_demo", False)),
        "is_free": price == 0,
        "entitlements": entitlements,
        "features": features,
        "highlights": features,
        "limits": limits,
        "suitable_for": [],
        "addons": [],
    }


def _fallback_plans(region: str) -> List[Dict[str, Any]]:
    return _sort_plans(DEFAULT_PLANS.get(region, DEFAULT_PLANS["GLOBAL"]))


async def get_plans_for_country(db: AsyncSession, country: Optional[str]) -> List[Dict[str, Any]]:
    return list(get_pricing_catalog(country).get("plans", []))


async def get_plan_by_code(
    db: AsyncSession,
    *,
    plan_code: str,
    country: Optional[str],
) -> Optional[Plan]:
    region = resolve_region(header_country=country, user_country=None, override=None)
    plan_field = Plan.code if hasattr(Plan, "code") else Plan.key
    stmt = select(Plan).where(plan_field == plan_code)
    if hasattr(Plan, "country"):
        stmt = stmt.where(Plan.country == region)
    plan = await db.scalar(stmt)
    if plan is None and region != "GLOBAL" and hasattr(Plan, "country"):
        plan = await db.scalar(select(Plan).where(plan_field == plan_code, Plan.country == "GLOBAL"))
    return plan
