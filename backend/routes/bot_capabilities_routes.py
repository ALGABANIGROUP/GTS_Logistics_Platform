"""
Bot Capabilities Routes
Returns bot capabilities and available bots list
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.session import get_async_session
from backend.security.auth import get_current_user
from backend.config import settings

router = APIRouter(prefix="/ai/bots", tags=["AI Bots"])


# All available bots in the system (imported from bots_available_enhanced)
# This ensures consistency across both endpoints
try:
    from backend.routes.bots_available_enhanced import ALL_BOTS as BOTS_LIST
except ImportError:
    # Fallback if import fails
    BOTS_LIST = [
        {
            "id": "general_manager",
            "name": "AI General Manager",
            "description": "Manages daily operations and business strategy",
            "icon": "👔",
            "path": "/ai-bots/general-manager",
            "category": "Management",
            "enabled": True,
        },
        {
            "id": "freight_broker",
            "name": "Freight Broker Bot",
            "description": "Optimizes shipment loads and carrier negotiations",
            "icon": "🚚",
            "path": "/ai-bots/freight-broker",
            "category": "Operations",
            "enabled": True,
        },
        {
            "id": "operations_manager_bot",
            "name": "Operations Manager",
            "description": "Handles daily operations and task management",
            "icon": "⚙️",
            "path": "/ai-bots/operations",
            "category": "Operations",
            "enabled": True,
        },
        {
            "id": "ai_dispatcher",
            "name": "AI Dispatcher",
            "description": "Smart route planning and driver assignment",
            "icon": "🗺️",
            "path": "/ai-bots/aid-dispatcher",
            "category": "Operations",
            "enabled": True,
        },
        {
            "id": "information_coordinator",
            "name": "Information Coordinator",
            "description": "Manages company information and data",
            "icon": "📋",
            "path": "/ai-bots/information",
            "category": "Data",
            "enabled": True,
        },
        {
            "id": "intelligence_bot",
            "name": "Executive Intelligence",
            "description": "Generates business intelligence reports",
            "icon": "📊",
            "path": "/ai-bots/executive-intelligence",
            "category": "Analytics",
            "enabled": True,
        },
        {
            "id": "documents_manager",
            "name": "Documents Manager",
            "description": "Manages and processes documents",
            "icon": "📄",
            "path": "/ai-bots/documents",
            "category": "Documents",
            "enabled": True,
        },
        {
            "id": "customer_service",
            "name": "Customer Service Bot",
            "description": "Handles customer inquiries and support",
            "icon": "💬",
            "path": "/ai-bots/customer-service",
            "category": "Support",
            "enabled": True,
        },
        {
            "id": "legal_bot",
            "name": "Legal Consultant",
            "description": "Provides legal advice and contract review",
            "icon": "⚖️",
            "path": "/ai-bots/legal",
            "category": "Legal",
            "enabled": True,
        },
        {
            "id": "mapleload_bot",
            "name": "MapleLoad Canada Bot",
            "description": "Canadian freight and logistics management",
            "icon": "🍁",
            "path": "/ai-bots/mapleload-canada",
            "category": "Integration",
            "enabled": True,
        },
        {
            "id": "safety_manager_bot",
            "name": "Safety Manager",
            "description": "Safety and compliance management",
            "icon": "🛡️",
            "path": "/ai-bots/safety_manager",
            "category": "Safety",
            "enabled": True,
        },
        {
            "id": "sales_bot",
            "name": "Sales Bot",
            "description": "Sales support and lead management",
            "icon": "💼",
            "path": "/ai-bots/sales",
            "category": "Sales",
            "enabled": True,
        },
        {
            "id": "system_manager_bot",
            "name": "System Admin",
            "description": "System administration and monitoring",
            "icon": "🔧",
            "path": "/ai-bots/system-admin",
            "category": "System",
            "enabled": True,
        },
        {
            "id": "finance_bot",
            "name": "AI Finance Bot",
            "description": "Financial analysis and reporting",
            "icon": "💰",
            "path": "/ai-bots/finance",
            "category": "Finance",
            "enabled": True,
        },
        {
            "id": "trainer_bot",
            "name": "AI Trainer Bot",
            "description": "Training and simulation orchestration for bot readiness",
            "icon": "🎓",
            "path": "/ai-bots/control?bot=trainer_bot",
            "category": "Training",
            "enabled": True,
        },
        {
            "id": "partner_manager",
            "name": "AI Partner Manager",
            "description": "Manages partner relationships and collaborations",
            "icon": "🤝",
            "path": "/ai-bots/partner-management",
            "category": "Partners",
            "enabled": True,
        },
        {
            "id": "security_manager",
            "name": "Security Manager",
            "description": "Monitors and manages system security",
            "icon": "🔒",
            "path": "/ai-bots/security",
            "category": "Security",
            "enabled": True,
        },
        {
            "id": "strategy_advisor",
            "name": "Strategy Advisor",
            "description": "Provides strategic business recommendations",
            "icon": "📈",
            "path": "/ai-bots/strategy",
            "category": "Strategy",
            "enabled": True,
        },
        {
            "id": "maintenance_dev",
            "name": "Maintenance & Dev Bot",
            "description": "Handles system maintenance and development tasks",
            "icon": "🛠️",
            "path": "/ai-bots/maintenance",
            "category": "Development",
            "enabled": True,
        },
    ]


@router.get("/")
async def get_bots_list(
    session: AsyncSession = Depends(get_async_session),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Get list of all available AI bots
    Returns bot ID, name, description, icon, and path
    """
    # Filter enabled bots only
    enabled_bots = [bot for bot in BOTS_LIST if bot.get("enabled", True)]

    return {
        "bots": {
            bot["id"]: bot["name"]
            for bot in enabled_bots
        },
        "bot_details": {
            bot["id"]: {
                "name": bot["name"],
                "description": bot["description"],
                "icon": bot.get("icon", "🤖"),
                "path": bot.get("path", f"/ai-bots/{bot['id']}"),
                "category": bot.get("category", "General"),
            }
            for bot in enabled_bots
        },
        "total": len(enabled_bots),
    }


@router.get("/{bot_id}")
async def get_bot_capabilities(
    bot_id: str,
    session: AsyncSession = Depends(get_async_session),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Get capabilities and details for a specific bot
    """
    # Find the bot
    bot = next((b for b in BOTS_LIST if b["id"] == bot_id), None)

    if not bot:
        raise HTTPException(status_code=404, detail=f"Bot '{bot_id}' not found")

    if not bot.get("enabled", True):
        raise HTTPException(status_code=403, detail=f"Bot '{bot_id}' is disabled")

    # Define capabilities for each bot (can be expanded)
    capabilities_map = {
        "general_manager": ["generate_report", "analyze_performance", "strategic_advice"],
        "freight_broker": ["match_loads", "negotiate_rates", "find_carriers"],
        "operations_manager": ["assign_tasks", "track_shipments", "optimize_routes"],
        "ai_dispatcher": ["dispatch_vehicles", "schedule_drivers", "route_optimization"],
        "information_coordinator": ["organize_data", "generate_insights", "data_analysis"],
        "intelligence_bot": ["market_analysis", "competitive_intel", "trend_forecasting"],
        "documents_manager": ["ocr_extraction", "document_validation", "template_generation"],
        "customer_service": ["answer_queries", "create_tickets", "escalate_issues"],
        "legal_bot": ["review_contracts", "compliance_check", "legal_advice"],
        "mapleload_bot": ["load_matching", "carrier_discovery", "rate_analysis"],
        "safety_manager_bot": ["incident_reporting", "compliance_monitoring", "risk_assessment"],
        "sales_bot": ["lead_scoring", "quote_generation", "follow_up_reminders"],
        "system_manager_bot": ["user_management", "system_monitoring", "backup_restore"],
        "finance_bot": ["invoice_processing", "expense_tracking", "financial_forecasting"],
        "trainer_bot": ["create_courses", "assess_skills", "simulation_run"],
        "partner_manager": ["evaluate_partners", "manage_collaborations", "revenue_sharing"],
        "security_manager": ["threat_detection", "access_control", "audit_logging"],
        "strategy_advisor": ["market_research", "competitive_analysis", "growth_strategy"],
        "maintenance_dev": ["health_check", "auto_repair", "system_upgrade"],
    }

    return {
        "id": bot["id"],
        "name": bot["name"],
        "description": bot["description"],
        "icon": bot.get("icon", "🤖"),
        "path": bot.get("path", f"/ai-bots/{bot['id']}"),
        "category": bot.get("category", "General"),
        "capabilities": capabilities_map.get(bot["id"], ["general_assistance"]),
        "status": "active" if bot.get("enabled", True) else "disabled",
    }


__all__ = ["router"]