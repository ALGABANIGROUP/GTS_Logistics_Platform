# backend/routes/bots_available_enhanced.py
"""
Enhanced Bots Availability API
Returns available bots based on subscription and user role
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, List

from database.session import get_async_session
from security.auth import get_current_user
from config import settings
from backend.bots import get_active_bots, is_bot_active

router = APIRouter(prefix="/api/v1/ai/bots", tags=["AI Bots"])


# All available bots in the system
ALL_BOTS = [
    {
        "id": "general_manager",
        "name": "AI General Manager",
        "description": "Manages daily operations and business strategy",
        "icon": "👔",
        "path": "/ai-bots/general-manager",
        "category": "Management",
        "enabled": True,
        "subscription_required": "basic",
    },
    {
        "id": "freight_broker",
        "name": "Freight Broker Bot",
        "description": "Optimizes shipment loads and carrier negotiations",
        "icon": "🚚",
        "path": "/ai-bots/freight-broker",
        "category": "Operations",
        "enabled": True,
        "subscription_required": "basic",
    },
    {
        "id": "operations_manager_bot",
        "name": "Operations Manager",
        "description": "Handles daily operations and task management",
        "icon": "⚙️",
        "path": "/ai-bots/operations",
        "category": "Operations",
        "enabled": True,
        "subscription_required": "basic",
    },
    {
        "id": "information_coordinator",
        "name": "Information Coordinator",
        "description": "Manages company information and data",
        "icon": "📋",
        "path": "/ai-bots/information",
        "category": "Data",
        "enabled": True,
        "subscription_required": "basic",
    },
    {
        "id": "legal_consultant",
        "name": "Legal Consultant",
        "description": "Provides legal advice and contract review",
        "icon": "⚖️",
        "path": "/ai-bots/legal",
        "category": "Legal",
        "enabled": True,
        "subscription_required": "enterprise",
    },
    {
        "id": "security_manager",
        "name": "Security Manager",
        "description": "Monitors security threats and ensures system protection",
        "icon": "🛡️",
        "path": "/ai-bots/security",
        "category": "Security",
        "enabled": True,
        "subscription_required": "enterprise",
    },
    {
        "id": "system_manager",
        "name": "System Admin",
        "description": "System administration and monitoring",
        "icon": "🔧",
        "path": "/ai-bots/system-admin",
        "category": "System",
        "enabled": True,
        "subscription_required": "enterprise",
    },
    {
        "id": "maintenance_dev",
        "name": "AI Maintenance Dev",
        "description": "Error detection, auto-healing, and performance analysis",
        "icon": "🔧",
        "path": "/ai-bots/maintenance",
        "category": "System",
        "enabled": True,
        "subscription_required": "enterprise",
    },
    {
        "id": "sales_bot",
        "name": "AI Sales Bot",
        "description": "Sales analytics, lead management, and revenue tracking",
        "icon": "💰",
        "path": "/ai-bots/sales-team",
        "category": "Sales",
        "enabled": True,
        "subscription_required": "basic"
    },
    {
        "id": "marketing_manager",
        "name": "Marketing Manager",
        "description": "Manages marketing campaigns and strategies",
        "icon": "📢",
        "path": "/ai-bots/marketing",
        "category": "Marketing",
        "enabled": True,
        "subscription_required": "unified",
    },
    {
        "id": "intelligence_bot",
        "name": "Executive Intelligence",
        "description": "Generates business intelligence reports",
        "icon": "📊",
        "path": "/ai-bots/executive-intelligence",
        "category": "Analytics",
        "enabled": True,
        "subscription_required": "unified",
    },
    {
        "id": "trainer_bot",
        "name": "AI Trainer Bot",
        "description": "Training and simulation orchestration for bot readiness",
        "icon": "🎓",
        "path": "/ai-bots/trainer",
        "category": "Training",
        "enabled": True,
        "subscription_required": "enterprise",
    },
    {
        "id": "safety_manager",
        "name": "Safety Manager",
        "description": "Safety and compliance management",
        "icon": "🛡️",
        "path": "/ai-bots/safety",
        "category": "Safety",
        "enabled": True,
        "subscription_required": "unified",
    },
    {
        "id": "ai_dispatcher",
        "name": "AI Dispatcher",
        "description": "Smart route planning and driver assignment",
        "icon": "🗺️",
        "path": "/ai-bots/dispatcher",
        "category": "Operations",
        "enabled": True,
        "subscription_required": "tms_pro",
    },
    {
        "id": "mapleload_canada",
        "name": "MapleLoad Canada Bot",
        "description": "Canadian freight and logistics management",
        "icon": "🍁",
        "path": "/ai-bots/mapleload-canada",
        "category": "Integration",
        "enabled": True,
        "subscription_required": "tms_pro",
    },
    {
        "id": "customer_service",
        "name": "Customer Service Bot",
        "description": "Handles customer inquiries and support",
        "icon": "💬",
        "path": "/ai-bots/customer-service",
        "category": "Support",
        "enabled": True,
        "subscription_required": "basic",
    },
    {
        "id": "documents_manager",
        "name": "Documents Manager",
        "description": "Manages and processes documents",
        "icon": "📄",
        "path": "/ai-bots/documents",
        "category": "Documents",
        "enabled": True,
        "subscription_required": "basic",
    },
    {
        "id": "executive_intelligence",
        "name": "Executive Intelligence",
        "description": "Advanced business intelligence and analytics",
        "icon": "🎯",
        "path": "/ai-bots/executive-intelligence",
        "category": "Analytics",
        "enabled": True,
        "subscription_required": "enterprise",
    },
    {
        "id": "finance_intelligence",
        "name": "Finance Intelligence",
        "description": "Financial analysis and reporting",
        "icon": "💰",
        "path": "/ai-bots/finance",
        "category": "Finance",
        "enabled": True,
        "subscription_required": "unified",
    },
    {
        "id": "partner_management",
        "name": "Partner Management",
        "description": "Manages partnerships and vendor relationships",
        "icon": "🤝",
        "path": "/ai-bots/partners",
        "category": "Management",
        "enabled": True,
        "subscription_required": "unified",
    },
    {
        "id": "system_intelligence",
        "name": "System Intelligence",
        "description": "Advanced system monitoring and optimization",
        "icon": "🧠",
        "path": "/ai-bots/system-intelligence",
        "category": "System",
        "enabled": True,
        "subscription_required": "enterprise",
    },
]

SUBSCRIPTION_TIERS = {
    "demo": [bot["id"] for bot in ALL_BOTS if bot["subscription_required"] == "basic"],
    "basic": [bot["id"] for bot in ALL_BOTS if bot["subscription_required"] in ["basic"]],
    "tms_pro": [bot["id"] for bot in ALL_BOTS if bot["subscription_required"] in ["basic", "tms_pro"]],
    "unified": [bot["id"] for bot in ALL_BOTS if bot["subscription_required"] in ["basic", "tms_pro", "unified"]],
    "enterprise": [bot["id"] for bot in ALL_BOTS],  # All bots for enterprise
}


@router.get("/current-user/available-enhanced", response_model=Dict[str, Any])
async def get_current_user_available_bots(
    session: AsyncSession = Depends(get_async_session),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Get available bots for current user (returns all bots for super admin)"""
    # For now, return all bots - in production, check user subscription
    available_bot_ids = SUBSCRIPTION_TIERS["enterprise"]
    available_bots = [b for b in ALL_BOTS if b["id"] in available_bot_ids and b["enabled"]]

    return {
        "ok": True,
        "bots": available_bots,
        "services": [],
        "subscription_tier": "enterprise",
        "total_count": len(available_bots),
    }


@router.get("/all", response_model=Dict[str, Any])
async def get_all_bots(
    session: AsyncSession = Depends(get_async_session),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Get all available bots with real activation status"""
    active_bot_ids = get_active_bots()
    
    bots = []
    for bot in ALL_BOTS:
        bot_info = bot.copy()
        # Override status with real activation
        is_activated = bot["id"] in active_bot_ids and bot["enabled"]
        bot_info["is_activated"] = is_activated
        bot_info["status"] = "active" if is_activated else "inactive"
        bots.append(bot_info)
    
    active_count = len([b for b in bots if b["is_activated"]])
    
    return {
        "ok": True,
        "bots": bots,
        "active_count": active_count,
        "total_count": len(ALL_BOTS),
        "inactive_count": len(bots) - active_count
    }


@router.get("/available", response_model=Dict[str, Any])
async def get_available_bots(
    session: AsyncSession = Depends(get_async_session),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Get available bots for the dashboard"""
    # For now, return all bots - in production, check user subscription
    available_bot_ids = SUBSCRIPTION_TIERS["enterprise"]
    available_bots = [b for b in ALL_BOTS if b["id"] in available_bot_ids and b["enabled"]]
    
    # Format for dashboard compatibility
    formatted_bots = []
    for bot in available_bots:
        formatted_bots.append({
            "bot_key": bot["id"],
            "display_name": bot["name"],
            "name": bot["name"],
            "description": bot["description"],
            "has_backend": True,  # Assume all have backend for now
            "category": bot["category"],
            "subscription_required": bot["subscription_required"]
        })
    
    return {
        "data": {
            "bots": formatted_bots
        },
        "ok": True
    }


@router.get("/by-subscription/{subscription}", response_model=Dict[str, Any])
async def get_bots_by_subscription(
    subscription: str,
    session: AsyncSession = Depends(get_async_session),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Get available bots for a specific subscription tier"""
    if getattr(settings, "REGISTRATION_DISABLED", False):
        raise HTTPException(
            status_code=410,
            detail="Subscription-tier probing endpoint is disabled in internal-only mode.",
        )

    available_bot_ids = SUBSCRIPTION_TIERS.get(subscription, [])
    available_bots = [b for b in ALL_BOTS if b["id"] in available_bot_ids and b["enabled"]]

    return {
        "ok": True,
        "subscription": subscription,
        "bots": available_bots,
        "total": len(available_bots),
    }


__all__ = ["router"]
