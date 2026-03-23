from __future__ import annotations

from typing import Any, Dict, List, Set

from fastapi import APIRouter, Depends, HTTPException, status

from backend.ai.policy import bot_access_policy
from backend.ai.roles.bot_permissions import BOT_CAPABILITIES, get_bot_policy, VALID_REPORT_FLOWS
from backend.security.auth import get_current_user

router = APIRouter(prefix="/ai/bots", tags=["AI"])


def _registry():
    from backend import main as main_module

    return main_module.ai_registry


def _policy_context(user: Dict[str, Any]) -> tuple[str, Set[str]]:
    role = str(user.get("effective_role") or user.get("role") or "user").strip().lower()
    features = set(user.get("features") or [])
    return role, features


def _ensure_bot_exists(bot_key: str) -> None:
    registry = _registry()
    if bot_key not in registry.list():
        raise HTTPException(status_code=404, detail=f"Bot '{bot_key}' not found")


def _require_admin_role(role: str) -> None:
    normalized = str(role or "").strip().lower()
    if normalized not in {"admin", "system_admin", "super_admin", "owner"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required for reporting flows",
        )


@router.get("/capabilities")
async def list_bot_capabilities(
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    role, features = _policy_context(current_user)
    registry = _registry()
    bot_keys = list(registry.list().keys())

    bots: List[Dict[str, Any]] = []
    for bot_key in bot_keys:
        decision = bot_access_policy.can_see_bot(role, features, bot_key)
        if not decision.get("allowed"):
            continue
        caps = BOT_CAPABILITIES.get(bot_key) or {}
        policy = get_bot_policy(bot_key)
        bots.append(
            {
                "bot_key": bot_key,
                "capabilities": caps,
                "policy": {
                    "visible_to_roles": list(getattr(policy, "visible_to_roles", [])) if policy else [],
                    "required_features": list(getattr(policy, "required_features", [])) if policy else [],
                    "hidden": bool(getattr(policy, "hidden", False)) if policy else False,
                },
            }
        )

    return {"ok": True, "bots": bots, "count": len(bots)}


@router.get("/capabilities/{bot_key}")
async def get_bot_capability(
    bot_key: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    _ensure_bot_exists(bot_key)
    role, features = _policy_context(current_user)
    decision = bot_access_policy.can_see_bot(role, features, bot_key)
    if not decision.get("allowed"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=decision.get("message", "Access denied"))

    caps = BOT_CAPABILITIES.get(bot_key) or {}
    policy = get_bot_policy(bot_key)
    return {
        "ok": True,
        "bot_key": bot_key,
        "capabilities": caps,
        "policy": {
            "visible_to_roles": list(getattr(policy, "visible_to_roles", [])) if policy else [],
            "required_features": list(getattr(policy, "required_features", [])) if policy else [],
            "hidden": bool(getattr(policy, "hidden", False)) if policy else False,
        },
    }


@router.get("/reporting/flow")
async def list_reporting_flows(
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    role, _ = _policy_context(current_user)
    _require_admin_role(role)
    return {"ok": True, "flows": VALID_REPORT_FLOWS}


@router.get("/reporting/flow/{sender}")
async def get_reporting_flow(
    sender: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    role, _ = _policy_context(current_user)
    _require_admin_role(role)
    receivers = VALID_REPORT_FLOWS.get(sender)
    if receivers is None:
        raise HTTPException(status_code=404, detail="Sender not found")
    return {"ok": True, "sender": sender, "receivers": receivers}
