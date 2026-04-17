from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional, Set

from backend.ai.roles.bot_permissions import (
    BOT_POLICIES,
    BOT_CAPABILITIES,
    get_bot_policy,
)


BOT_ACCESS_RULES: Dict[str, Dict[str, Any]] = {
    # Optional per-bot restrictions can be placed here.
    # Example:
    # "system_admin": {"allowed_plans": {"unified_pro"}, "required_permissions": {"admin.system"}},
}


BOT_ALIASES: Dict[str, str] = {
    "sales_team": "sales",
    "security_manager": "security",
    "maintenance_bot": "maintenance_dev",
    "support": "customer_service",
}


def _normalize_bot_key(value: str) -> str:
    return str(value or "").strip().lower().replace(" ", "_")


def _bot_status(registry: Any, bot_key: str) -> str:
    try:
        bot = registry.get(bot_key)
    except Exception:
        return "inactive"

    name = bot.__class__.__name__.lower()
    # Treat scaffold/alias registrations as available so UI can list them.
    if "scaffold" in name:
        return "active"
    if "alias" in name:
        return "active"
    return "active"


def evaluate_bot_access(
    bot_key: str,
    *,
    role: str,
    features: Set[str],
    permissions: Set[str],
    plan_key: str,
    status: str,
) -> Dict[str, Any]:
    normalized = _normalize_bot_key(bot_key)
    policy = get_bot_policy(normalized)

    reason_codes: List[str] = []

    if status != "active":
        reason_codes.append("BOT_INACTIVE")

    if policy is None:
        reason_codes.append("BOT_NOT_FOUND")
    else:
        if getattr(policy, "hidden", False):
            reason_codes.append("UI_HIDDEN")

        allowed_roles = set(getattr(policy, "visible_to_roles", set()))
        if role not in allowed_roles:
            reason_codes.append("ROLE_DENIED")

    required_features = set(getattr(policy, "required_features", set()))
    admin_roles = {"admin", "system_admin", "super_admin", "owner"}
    if role not in admin_roles:
        missing = required_features - features
        if missing:
            reason_codes.append("MISSING_FEATURE")

    rules = BOT_ACCESS_RULES.get(normalized, {})
    allowed_plans = set(rules.get("allowed_plans") or [])
    if allowed_plans and plan_key not in allowed_plans:
        reason_codes.append("PLAN_DENIED")

    required_permissions = set(rules.get("required_permissions") or [])
    if required_permissions and not required_permissions.issubset(permissions):
        reason_codes.append("PERMISSION_DENIED")

    can_see = len(reason_codes) == 0
    can_run = can_see

    return {
        "bot_key": normalized,
        "can_see": can_see,
        "can_run": can_run,
        "reason_codes": reason_codes,
        "policy": {
            "visible_to_roles": sorted(getattr(policy, "visible_to_roles", [])) if policy else [],
            "required_features": sorted(getattr(policy, "required_features", [])) if policy else [],
            "hidden": bool(getattr(policy, "hidden", False)) if policy else False,
        },
    }


def build_available_bots(
    *,
    registry: Any,
    role: str,
    features: Set[str],
    permissions: Set[str],
    plan_key: str,
    modules: Dict[str, bool],
) -> Dict[str, Any]:
    bots: List[Dict[str, Any]] = []
    aliases: List[Dict[str, Any]] = []

    for bot_key in sorted(BOT_POLICIES.keys()):
        status = _bot_status(registry, bot_key)
        decision = evaluate_bot_access(
            bot_key,
            role=role,
            features=features,
            permissions=permissions,
            plan_key=plan_key,
            status=status,
        )

        meta = BOT_CAPABILITIES.get(bot_key, {})
        bots.append(
            {
                "bot_key": bot_key,
                "display_name": meta.get("name", bot_key),
                "description": meta.get("description", ""),
                "category": meta.get("category", ""),
                "icon": meta.get("icon", ""),
                "color": meta.get("color", ""),
                "status": status,
                "can_see": decision["can_see"],
                "can_run": decision["can_run"],
                "reason_codes": decision["reason_codes"],
            }
        )

    for alias_key, target_key in BOT_ALIASES.items():
        target_key = _normalize_bot_key(target_key)
        alias_key = _normalize_bot_key(alias_key)
        if target_key == alias_key:
            continue
        decision = next((b for b in bots if b["bot_key"] == target_key), None)
        if not decision or not decision["can_see"]:
            continue
        aliases.append(
            {
                "alias_key": alias_key,
                "bot_key": target_key,
                "display_name": decision.get("display_name"),
                "can_see": decision.get("can_see"),
                "can_run": decision.get("can_run"),
                "reason_codes": decision.get("reason_codes"),
            }
        )

    visible_bots = [b for b in bots if b.get("can_see")]
    return {
        "bots": visible_bots,
        "aliases": aliases,
        "count": len(visible_bots),
    }


def any_visible_bots(
    *,
    role: str,
    features: Set[str],
    permissions: Set[str],
    plan_key: str,
    modules: Dict[str, bool],
) -> bool:
    class _RegistryStub:
        def get(self, _key: str):
            raise KeyError

    registry = _RegistryStub()
    for bot_key in BOT_POLICIES.keys():
        decision = evaluate_bot_access(
            bot_key,
            role=role,
            features=features,
            permissions=permissions,
            plan_key=plan_key,
            status="active",
        )
        if decision.get("can_see"):
            return True
    return False


def get_visible_bots(
    *,
    role: str,
    features: Set[str],
    permissions: Set[str],
    plan_key: str,
    modules: Dict[str, bool],
) -> List[str]:
    try:
        class _RegistryStub:
            def get(self, _key: str):
                raise KeyError

        registry = _RegistryStub()
        visible = []
        for bot_key in BOT_POLICIES.keys():
            decision = evaluate_bot_access(
                bot_key,
                role=role,
                features=features,
                permissions=permissions,
                plan_key=plan_key,
                status="active",
            )
            if decision.get("can_see"):
                visible.append(bot_key)
        return visible
    except Exception as e:
        print(f"Error in get_visible_bots: {e}")
        return []
