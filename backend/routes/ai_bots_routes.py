from __future__ import annotations

import asyncio
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from backend.ai.errors import ai_forbidden
from backend.ai.policy import bot_access_policy, normalize_role
from backend.ai.roles.bot_permissions import BOT_CAPABILITIES, get_bot_policy
from backend.security.auth import get_current_user

router = APIRouter(tags=["AI"])


class BotRunPayload(BaseModel):
    message: str = ""
    context: Optional[Dict[str, Any]] = None
    meta: Optional[Dict[str, Any]] = None


def _registry():
    from backend import main as main_module

    return main_module.ai_registry


_BACKEND_ROOT = Path(__file__).resolve().parents[1]
_ACTIVE_HINTS = {
    "operations_manager",
    "operations_bot",
    "operations_manager_bot",
    "freight_bot",
    "freight_broker",
    "finance_bot",
    "documents_manager",
    "intelligence_bot",
    "intelligence",
    "executive_intelligence",
    "sales_bot",
    "sales_intelligence",
    "sales",
    "marketing_manager",
    "marketing_manager_bot",
    "marketing_bot",
    "mapleload",
    "mapleload_bot",
    "mapleload_canada",
    "maintenance_dev",
    "dev_maintenance",
    "maintenance_dev_bot",
    "system_admin",
    "partner_manager",
    "information_coordinator",
    "legal_bot",
    "legal_consultant",
    "legal_counsel",
    "security_bot",
    "security_manager",
    "security_manager_bot",
    "system_bot",
    "system_manager",
    "system_manager_bot",
    "system_admin",
    "trainer_bot",
    "trainer",
    "training_bot",
    "general_manager",
    "safety_bot",
    "safety_manager",
    "safety",
}
_SERVICE_ALIASES = {
    "system_admin": "ai_system_administrator.py",
    "strategy_advisor": "ai_marketing_specialist.py",
    "customer_service": "ai_customer_service.py",
    "marketing_manager": "ai_marketing_manager.py",
    "marketing_manager_bot": "ai_marketing_manager.py",
    "marketing_bot": "ai_marketing_manager.py",
    "maintenance_dev": "ai_maintenance_dev.py",
    "dev_maintenance": "ai_maintenance_dev.py",
    "maintenance_dev_bot": "ai_maintenance_dev.py",
    "information_coordinator": "ai_information_coordinator.py",
    "legal_bot": "ai_legal_consultant.py",
    "legal_consultant": "ai_legal_consultant.py",
    "legal_counsel": "ai_legal_consultant.py",
    "security_bot": "ai_security_manager.py",
    "security_manager": "ai_security_manager.py",
    "security_manager_bot": "ai_security_manager.py",
    "system_bot": "ai_system_manager.py",
    "system_manager": "ai_system_manager.py",
    "system_manager_bot": "ai_system_manager.py",
    "system_admin": "ai_system_manager.py",
    "trainer_bot": "trainer_bot.py",
    "trainer": "trainer_bot.py",
    "training_bot": "trainer_bot.py",
    "documents_manager": "ai_documents_manager.py",
}


def _has_backend(bot_key: str) -> bool:
    if bot_key in _ACTIVE_HINTS:
        return True

    alias = _SERVICE_ALIASES.get(bot_key)
    candidates = [
        _BACKEND_ROOT / "services" / (alias or f"ai_{bot_key}.py"),
        _BACKEND_ROOT / "ai" / f"ai_{bot_key}.py",
        _BACKEND_ROOT / "ai" / f"{bot_key}.py",
        _BACKEND_ROOT / "ai" / "bots" / f"{bot_key}.py",
        _BACKEND_ROOT / "ai" / "roles" / f"{bot_key}.py",
    ]

    return any(path.exists() for path in candidates)


def _policy_context(user: Dict[str, Any]) -> tuple[str, Set[str]]:
    role = str(user.get("effective_role") or user.get("role") or "user").strip().lower()
    features = set(user.get("features") or [])
    return role, features


def _assigned_bot_allows(user: Dict[str, Any], bot_key: str) -> bool:
    assigned = user.get("assigned_bots")
    if assigned is None:
        return True
    if not isinstance(assigned, list):
        return True
    normalized = {str(item).strip() for item in assigned if str(item).strip()}
    if not normalized:
        return False
    return "*" in normalized or bot_key in normalized


def _ensure_bot_exists(bot_key: str) -> None:
    registry = _registry()
    if bot_key not in registry.list():
        raise HTTPException(status_code=404, detail=f"Bot '{bot_key}' not found")


async def _safe_status(bot: Any) -> Dict[str, Any]:
    try:
        if hasattr(bot, "status") and callable(getattr(bot, "status")):
            return await bot.status()
    except Exception as exc:
        return {"status": "error", "error": str(exc)}
    return {"status": "unknown"}


@router.get("/bots/catalog")
async def list_bots(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    role, features = _policy_context(current_user)
    registry = _registry()

    bots: List[Dict[str, Any]] = []
    for bot_key in registry.list().keys():
        if not _assigned_bot_allows(current_user, bot_key):
            continue
        decision = bot_access_policy.can_see_bot(role, features, bot_key)
        if not decision.get("allowed"):
            continue

        bot = registry.get(bot_key)
        status_data = await _safe_status(bot)
        meta = bot_permissions.BOT_CAPABILITIES.get(bot_key, {})
        has_backend = _has_backend(bot_key)
        allowed_actions: List[str] = []
        if has_backend:
            if bot_access_policy.can_run_bot(role, features, bot_key, action="run").get("allowed"):
                allowed_actions.append("run")
            if bot_access_policy.can_run_bot(role, features, bot_key, action="monitor").get("allowed"):
                allowed_actions.append("monitor")
            if bot_access_policy.can_run_bot(role, features, bot_key, action="configure").get("allowed"):
                allowed_actions.append("configure")
        bots.append(
            {
                "bot_code": bot_key,
                "bot_key": bot_key,
                "bot_class": bot.__class__.__name__,
                "status": status_data,
                "has_backend": has_backend,
                "allowed_actions": allowed_actions,
                "route_hint": f"/ai-bots/control?bot={bot_key}",
                "display_name": meta.get("name", bot_key),
                "description": meta.get("description", ""),
                "category": meta.get("category", ""),
                "icon": meta.get("icon", ""),
                "color": meta.get("color", ""),
                "tasks": meta.get("tasks", []),
                "reporting": meta.get("reporting", {}),
            }
        )

    return {
        "ok": True,
        "data": {"bots": bots, "count": len(bots)},
        "bots": bots,
        "count": len(bots),
        "error": None,
        "ts": datetime.now(timezone.utc).isoformat(),
    }


@router.post("/bots/{bot_code}/run")
async def run_bot(
    bot_code: str,
    payload: BotRunPayload,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    _ensure_bot_exists(bot_code)
    if not _assigned_bot_allows(current_user, bot_code):
        raise ai_forbidden("bot_assignment_missing", bot_code, message="User is not assigned to this bot.")
    if not _has_backend(bot_code):
        raise ai_forbidden("bot_preview", bot_code, message="Backend not active yet.")
    role, features = _policy_context(current_user)
    decision = bot_access_policy.can_run_bot(role, features, bot_code, action="run")
    if not decision.get("allowed"):
        details = {k: v for k, v in decision.items() if k != "allowed"}
        reason = details.pop("reason", "role_not_allowed")
        raise ai_forbidden(reason, bot_code, **details)

    registry = _registry()
    bot = registry.get(bot_code)
    trace_id = uuid.uuid4().hex
    ts = datetime.now(timezone.utc).isoformat()

    run_payload = {
        "message": payload.message,
        "context": payload.context or {},
        "meta": payload.meta or {},
        "trace_id": trace_id,
        "ts": ts,
    }

    if hasattr(bot, "process_message") and callable(getattr(bot, "process_message")):
        result = await bot.process_message(payload.message, payload.context or {})
    else:
        result = await bot.run(run_payload)

    return {
        "bot_code": bot_code,
        "bot_class": bot.__class__.__name__,
        "ok": True,
        "result": result,
        "data": result,
        "error": None,
        "trace_id": trace_id,
        "ts": ts,
    }


@router.get("/bots/{bot_code}/status")
async def bot_status(
    bot_code: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    _ensure_bot_exists(bot_code)
    if not _assigned_bot_allows(current_user, bot_code):
        raise ai_forbidden("bot_assignment_missing", bot_code, message="User is not assigned to this bot.")
    role, features = _policy_context(current_user)
    decision = bot_access_policy.can_see_bot(role, features, bot_code)
    if not decision.get("allowed"):
        details = {k: v for k, v in decision.items() if k != "allowed"}
        reason = details.pop("reason", "role_not_allowed")
        raise ai_forbidden(reason, bot_code, **details)

    registry = _registry()
    bot = registry.get(bot_code)
    status_data = await _safe_status(bot)
    return {
        "bot_code": bot_code,
        "bot_class": bot.__class__.__name__,
        "ok": True,
        "status": status_data,
        "data": status_data,
        "error": None,
        "ts": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/bots/{bot_code}/config")
async def bot_config(
    bot_code: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    _ensure_bot_exists(bot_code)
    if not _assigned_bot_allows(current_user, bot_code):
        raise ai_forbidden("bot_assignment_missing", bot_code, message="User is not assigned to this bot.")
    role, features = _policy_context(current_user)
    decision = bot_access_policy.can_see_bot(role, features, bot_code)
    if not decision.get("allowed"):
        details = {k: v for k, v in decision.items() if k != "allowed"}
        reason = details.pop("reason", "role_not_allowed")
        raise ai_forbidden(reason, bot_code, **details)

    registry = _registry()
    bot = registry.get(bot_code)
    config_data = {}
    if hasattr(bot, "config") and callable(getattr(bot, "config")):
        config_data = await bot.config()
    return {
        "bot_code": bot_code,
        "bot_class": bot.__class__.__name__,
        "ok": True,
        "config": config_data,
        "data": config_data,
        "error": None,
        "ts": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/bots/{bot_code}/health")
async def bot_health(
    bot_code: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    _ensure_bot_exists(bot_code)
    if not _assigned_bot_allows(current_user, bot_code):
        raise ai_forbidden("bot_assignment_missing", bot_code, message="User is not assigned to this bot.")
    role, features = _policy_context(current_user)
    decision = bot_access_policy.can_see_bot(role, features, bot_code)
    if not decision.get("allowed"):
        details = {k: v for k, v in decision.items() if k != "allowed"}
        reason = details.pop("reason", "role_not_allowed")
        raise ai_forbidden(reason, bot_code, **details)

    registry = _registry()
    bot = registry.get(bot_code)
    status_data = await _safe_status(bot)
    return {
        "bot_code": bot_code,
        "bot_class": bot.__class__.__name__,
        "ok": True,
        "status": status_data,
        "data": status_data,
        "error": None,
        "ts": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/bots/capabilities")
async def bot_capabilities(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    role, features = _policy_context(current_user)
    registry = _registry()

    items: List[Dict[str, Any]] = []
    for bot_key in registry.list().keys():
        if not _assigned_bot_allows(current_user, bot_key):
            continue
        decision = bot_access_policy.can_see_bot(role, features, bot_key)
        if not decision.get("allowed"):
            continue
        meta = bot_permissions.BOT_CAPABILITIES.get(bot_key, {})
        items.append(
            {
                "bot_key": bot_key,
                "display_name": meta.get("name", bot_key),
                "description": meta.get("description", ""),
                "category": meta.get("category", ""),
                "icon": meta.get("icon", ""),
                "color": meta.get("color", ""),
                "tasks": meta.get("tasks", []),
                "reporting": meta.get("reporting", {}),
                "has_backend": _has_backend(bot_key),
            }
        )

    return {
        "ok": True,
        "data": {"bots": items, "count": len(items)},
        "error": None,
        "ts": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/bots/capabilities/{bot_key}")
async def bot_capability(
    bot_key: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    if not _assigned_bot_allows(current_user, bot_key):
        raise ai_forbidden("bot_assignment_missing", bot_key, message="User is not assigned to this bot.")
    role, features = _policy_context(current_user)
    decision = bot_access_policy.can_see_bot(role, features, bot_key)
    if not decision.get("allowed"):
        details = {k: v for k, v in decision.items() if k != "allowed"}
        reason = details.pop("reason", "role_not_allowed")
        raise ai_forbidden(reason, bot_key, **details)

    meta = bot_permissions.BOT_CAPABILITIES.get(bot_key)
    if meta is None:
        raise HTTPException(status_code=404, detail=f"Capabilities not found for '{bot_key}'")

    payload = {
        "bot_key": bot_key,
        "display_name": meta.get("name", bot_key),
        "description": meta.get("description", ""),
        "category": meta.get("category", ""),
        "icon": meta.get("icon", ""),
        "color": meta.get("color", ""),
        "tasks": meta.get("tasks", []),
        "reporting": meta.get("reporting", {}),
        "has_backend": _has_backend(bot_key),
    }

    return {
        "ok": True,
        "data": payload,
        "error": None,
        "ts": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/bots/reporting/flow")
async def bot_reporting_flow(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    role, features = _policy_context(current_user)
    normalized_role = normalize_role(role)

    if normalized_role not in {"admin", "system_admin", "super_admin", "owner"}:
        raise ai_forbidden("role_not_allowed", "reporting_flow", message="Admin role required.")

    flows = bot_access_policy.get_report_flows_for_user(role, features)
    return {"ok": True, "data": flows, "error": None, "ts": datetime.now(timezone.utc).isoformat()}


@router.get("/information/news")
async def information_news(
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    if not _assigned_bot_allows(current_user, "information_coordinator"):
        raise ai_forbidden(
            "bot_assignment_missing",
            "information_coordinator",
            message="User is not assigned to this bot.",
        )
    role, features = _policy_context(current_user)
    decision = bot_access_policy.can_see_bot(role, features, "information_coordinator")
    if not decision.get("allowed"):
        details = {k: v for k, v in decision.items() if k != "allowed"}
        reason = details.pop("reason", "role_not_allowed")
        raise ai_forbidden(reason, "information_coordinator", **details)

    try:
        from backend.services import ai_information_coordinator as info_service
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Information service not available: {exc}")

    try:
        news = await asyncio.to_thread(info_service.get_comprehensive_canadian_logistics_news)
        source_count = len(info_service.get_canadian_scraper().sources)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to fetch news: {exc}")

    return {
        "ok": True,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source_count": source_count,
        "news": news,
    }
