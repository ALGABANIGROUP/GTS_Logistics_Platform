from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.ai.bot_subscription_manager import (
    check_bot_access,
    get_available_bots,
    get_available_bots_with_services,
    get_bot_categories,
    get_subscription_summary,
)
from backend.core.db_config import get_async_db
from backend.models.user import User
from backend.security.auth import get_current_user

router = APIRouter(prefix="/api/v1/ai/bots", tags=["AI Bots Subscription"])


def _extract_user_email(current_user: Any) -> Optional[str]:
    if hasattr(current_user, "email"):
        return getattr(current_user, "email")
    if isinstance(current_user, dict):
        return current_user.get("email") or current_user.get("sub")
    return None


def _extract_current_role(current_user: Any) -> Optional[str]:
    if hasattr(current_user, "effective_role"):
        return getattr(current_user, "effective_role")
    if hasattr(current_user, "role"):
        return getattr(current_user, "role")
    if isinstance(current_user, dict):
        return (
            current_user.get("effective_role")
            or current_user.get("db_role")
            or current_user.get("role")
            or current_user.get("token_role")
        )
    return None


def _normalize_bot_role(role: Optional[str]) -> str:
    normalized = (role or "").strip().lower()
    if normalized in {"super_admin", "owner", "system_admin"}:
        return "super_admin"
    if normalized == "admin":
        return "admin"
    return normalized


async def _resolve_user_access_context(db: AsyncSession, current_user: Any) -> Tuple[str, str, str]:
    subscription_tier = "demo"
    user_role = "shipper"
    system_type = "tms"

    current_role = _normalize_bot_role(_extract_current_role(current_user))
    if current_role in {"super_admin", "owner", "system_admin", "admin"}:
        return "enterprise", current_role, system_type

    email = _extract_user_email(current_user)
    if not email:
        return subscription_tier, user_role, system_type

    result = await db.execute(select(User).where(func.lower(User.email) == email.lower()))
    user = result.scalar_one_or_none()
    if not user:
        return subscription_tier, user_role, system_type

    subscription_tier = getattr(user, "subscription_tier", None) or subscription_tier
    user_role = getattr(user, "role", None) or user_role
    system_type = getattr(user, "system_type", None) or system_type

    normalized_role = _normalize_bot_role(str(user_role))
    if normalized_role in {"super_admin", "admin"}:
        return "enterprise", normalized_role, system_type

    return subscription_tier, user_role, system_type


async def _resolve_requested_access_context(
    db: AsyncSession,
    current_user: Any,
    subscription_tier: Optional[str],
    user_role: Optional[str],
    system_type: Optional[str],
) -> Tuple[str, str, str]:
    if subscription_tier or user_role or system_type:
        return (
            (subscription_tier or "demo").strip().lower(),
            (user_role or "shipper").strip().lower(),
            (system_type or "tms").strip().lower(),
        )
    return await _resolve_user_access_context(db, current_user)


class BotInfo(BaseModel):
    id: str
    name: str
    description: str = ""
    color: str = ""
    icon: str = ""
    category: str = ""
    status: str = "active"
    tier_required: str = "basic"
    is_internal: Optional[bool] = None
    bot_key: Optional[str] = None
    display_name: Optional[str] = None
    has_backend: bool = True


class AvailableBotsResponse(BaseModel):
    bots: List[BotInfo]
    services: List[BotInfo] = []
    total_count: int
    subscription_tier: str
    user_role: str
    system_type: str
    aliases: List[Dict[str, Any]] = []
    data: Dict[str, Any]


class BotAccessCheck(BaseModel):
    bot_id: str
    has_access: bool
    subscription_tier: str
    tier_required: Optional[str] = None
    message_ar: Optional[str] = None
    message_en: Optional[str] = None


def _normalize_bot_item(bot: Dict[str, Any]) -> BotInfo:
    item = dict(bot)
    bot_id = str(item.get("id") or item.get("bot_key") or item.get("name") or "").strip()
    name = str(item.get("name") or item.get("display_name") or bot_id).strip()
    return BotInfo(
        id=bot_id,
        bot_key=str(item.get("bot_key") or bot_id),
        display_name=str(item.get("display_name") or name),
        name=name,
        description=str(item.get("description") or ""),
        color=str(item.get("color") or ""),
        icon=str(item.get("icon") or ""),
        category=str(item.get("category") or ""),
        status=str(item.get("status") or "active"),
        tier_required=str(item.get("tier_required") or item.get("subscription_required") or "basic"),
        is_internal=item.get("is_internal"),
        has_backend=bool(item.get("has_backend", True)),
    )


def _dump_models(items: List[BotInfo]) -> List[Dict[str, Any]]:
    dumped: List[Dict[str, Any]] = []
    for item in items:
        if hasattr(item, "model_dump"):
            dumped.append(item.model_dump())
        else:  # pragma: no cover
            dumped.append(item.dict())
    return dumped


def _build_available_response(
    bots: List[Dict[str, Any]],
    services: List[Dict[str, Any]],
    subscription_tier: str,
    user_role: str,
    system_type: str,
) -> AvailableBotsResponse:
    bot_models = [_normalize_bot_item(bot) for bot in bots]
    service_models = [_normalize_bot_item(bot) for bot in services]
    return AvailableBotsResponse(
        bots=bot_models,
        services=service_models,
        total_count=len(bot_models),
        subscription_tier=subscription_tier,
        user_role=user_role,
        system_type=system_type,
        aliases=[],
        data={"bots": _dump_models(bot_models)},
    )


@router.get("/available", response_model=AvailableBotsResponse)
async def list_available_bots_endpoint(
    language: str = Query(default="en", description="Language (ar, en)"),
    subscription_tier: Optional[str] = Query(default=None),
    user_role: Optional[str] = Query(default=None),
    system_type: Optional[str] = Query(default=None),
    db: AsyncSession = Depends(get_async_db),
    current_user: Any = Depends(get_current_user),
):
    try:
        resolved_subscription_tier, resolved_user_role, resolved_system_type = await _resolve_requested_access_context(
            db,
            current_user,
            subscription_tier,
            user_role,
            system_type,
        )
        bots = get_available_bots(
            subscription_tier=resolved_subscription_tier,
            user_role=resolved_user_role,
            system_type=resolved_system_type,
            language=language,
        )
        return _build_available_response(
            bots=bots,
            services=[],
            subscription_tier=resolved_subscription_tier,
            user_role=resolved_user_role,
            system_type=resolved_system_type,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch bots: {str(e)}")


@router.get("/check-access/{bot_id}", response_model=BotAccessCheck)
async def check_access(
    bot_id: str,
    db: AsyncSession = Depends(get_async_db),
    current_user: Any = Depends(get_current_user),
):
    from backend.ai.bot_subscription_manager import BOT_DEFINITIONS

    subscription_tier, user_role, system_type = await _resolve_user_access_context(db, current_user)
    has_access = check_bot_access(
        bot_id=bot_id,
        subscription_tier=subscription_tier,
        user_role=user_role,
        system_type=system_type,
    )

    response = BotAccessCheck(
        bot_id=bot_id,
        has_access=has_access,
        subscription_tier=subscription_tier,
    )

    if not has_access:
        if bot_id in BOT_DEFINITIONS:
            bot_config = BOT_DEFINITIONS[bot_id]
            tier_required = bot_config["min_tier"].value
            response.tier_required = tier_required
            response.message_ar = f"This bot requires '{tier_required}' subscription or higher"
            response.message_en = f"This bot requires '{tier_required}' subscription or higher"
        else:
            response.message_ar = "Bot not found"
            response.message_en = "Bot not found"

    return response


@router.get("/categories")
async def list_categories(current_user: Dict[str, Any] = Depends(get_current_user)):
    return get_bot_categories()


@router.get("/current-user/available", response_model=AvailableBotsResponse)
async def list_current_user_available_bots(
    language: str = Query(default="en", description="Language (ar, en)"),
    db: AsyncSession = Depends(get_async_db),
    current_user: Any = Depends(get_current_user),
):
    try:
        subscription_tier, user_role, system_type = await _resolve_user_access_context(db, current_user)
        result = get_available_bots_with_services(
            subscription_tier=subscription_tier,
            user_role=user_role,
            system_type=system_type,
            language=language,
        )
        return _build_available_response(
            bots=result.get("bots", []),
            services=result.get("services", []),
            subscription_tier=subscription_tier,
            user_role=user_role,
            system_type=system_type,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching available bots: {str(e)}")


@router.get("/subscription-summary")
async def subscription_info(
    db: AsyncSession = Depends(get_async_db),
    current_user: Any = Depends(get_current_user),
):
    subscription_tier, _, _ = await _resolve_user_access_context(db, current_user)
    return get_subscription_summary(subscription_tier)


@router.post("/upgrade-required")
async def suggest_upgrade(
    bot_id: str,
    db: AsyncSession = Depends(get_async_db),
    current_user: Any = Depends(get_current_user),
):
    raise HTTPException(
        status_code=410,
        detail="Upgrade API is disabled in internal-only mode. Contact platform administrator for access policy changes.",
    )
