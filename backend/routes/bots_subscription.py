from backend.core.db_config import get_async_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from backend.models.user import User
from typing import Any
"""
Bots Subscription API Endpoints
"""
from typing import Dict, List, Optional, Tuple
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from backend.ai.bot_subscription_manager import (
    get_available_bots,
    get_available_bots_with_services,
    check_bot_access,
    get_bot_categories,
    get_subscription_summary,
)
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


async def _resolve_user_access_context(
    db: AsyncSession,
    current_user: Any,
) -> Tuple[str, str, str]:
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


class BotInfo(BaseModel):
    """Bot details."""
    id: str
    name: str
    description: str
    color: str
    icon: str
    category: str
    status: str
    tier_required: str
    is_internal: Optional[bool] = None


class AvailableBotsResponse(BaseModel):
    """Available bots response payload."""
    bots: List[BotInfo]
    services: List[BotInfo] = []
    total_count: int
    subscription_tier: str
    user_role: str
    system_type: str


class BotAccessCheck(BaseModel):
    """Bot access check response payload."""
    bot_id: str
    has_access: bool
    subscription_tier: str
    tier_required: Optional[str] = None
    message_ar: Optional[str] = None
    message_en: Optional[str] = None


@router.get("/available", response_model=AvailableBotsResponse)
async def list_available_bots(
    language: str = Query(default="en", description="Language (ar, en)"),
    db: AsyncSession = Depends(get_async_db),
    current_user: Any = Depends(get_current_user)
):
    """
    Return bots available to the authenticated user.

    **Parameters:**
    - language: preferred response language

    **Returns:**
    Available bots with access context metadata.
    """
    try:
        subscription_tier, user_role, system_type = await _resolve_user_access_context(db, current_user)

        bots = get_available_bots(
            subscription_tier=subscription_tier,
            user_role=user_role,
            system_type=system_type,
            language=language
        )
        
        return AvailableBotsResponse(
            bots=[BotInfo(**bot) for bot in bots],
            services=[],
            total_count=len(bots),
            subscription_tier=subscription_tier,
            user_role=user_role,
            system_type=system_type
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch bots: {str(e)}")


@router.get("/check-access/{bot_id}", response_model=BotAccessCheck)
async def check_access(
    bot_id: str,
    db: AsyncSession = Depends(get_async_db),
    current_user: Any = Depends(get_current_user)
):
    """
    Check whether the authenticated user can access a specific bot.

    **Parameters:**
    - bot_id: target bot ID

    **Returns:**
    Access status and contextual message.
    """
    from backend.ai.bot_subscription_manager import BOT_DEFINITIONS
    
    subscription_tier, user_role, system_type = await _resolve_user_access_context(db, current_user)

    has_access = check_bot_access(
        bot_id=bot_id,
        subscription_tier=subscription_tier,
        user_role=user_role,
        system_type=system_type
    )
    
    response = BotAccessCheck(
        bot_id=bot_id,
        has_access=has_access,
        subscription_tier=subscription_tier
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
async def list_categories(
    current_user: Dict = Depends(get_current_user)
):
    """
    Return available bot categories.

    **Returns:**
    Category map with associated bots.
    """
    return get_bot_categories()


@router.get("/current-user/available")
async def list_current_user_available_bots(
    language: str = Query(default="en", description="Language (ar, en)"),
    db: AsyncSession = Depends(get_async_db),
    current_user: Any = Depends(get_current_user)
):
    """
    Return bots available to the current authenticated user.

    **Returns:**
    Available bots and internal services with effective access context.
    """
    try:
        subscription_tier, user_role, system_type = await _resolve_user_access_context(db, current_user)
        
        result = get_available_bots_with_services(
            subscription_tier=subscription_tier,
            user_role=user_role,
            system_type=system_type,
            language=language
        )

        bots = result.get("bots", [])
        services = result.get("services", [])
        
        return AvailableBotsResponse(
            bots=[BotInfo(**bot) for bot in bots],
            services=[BotInfo(**bot) for bot in services],
            total_count=len(bots),
            subscription_tier=subscription_tier,
            user_role=user_role,
            system_type=system_type
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching available bots: {str(e)}")


@router.get("/subscription-summary")
async def subscription_info(
    db: AsyncSession = Depends(get_async_db),
    current_user: Any = Depends(get_current_user)
):
    """
    Return subscription capabilities summary for current user tier.
    """
    subscription_tier, _, _ = await _resolve_user_access_context(db, current_user)
    return get_subscription_summary(subscription_tier)


@router.post("/upgrade-required")
async def suggest_upgrade(
    bot_id: str,
    db: AsyncSession = Depends(get_async_db),
    current_user: Any = Depends(get_current_user)
):
    """
    Upgrade recommendation endpoint (disabled in internal-only mode).
    """
    raise HTTPException(
        status_code=410,
        detail="Upgrade API is disabled in internal-only mode. Contact platform administrator for access policy changes.",
    )
