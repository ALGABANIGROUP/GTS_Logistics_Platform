"""
Bot Subscription & Role Manager

Access is controlled by:
- Subscription tier (demo, basic, tms_pro, unified, enterprise)
- User role (shipper, carrier, broker, admin, super_admin)
- System type (tms, loadboard)
"""
from typing import Dict, List, Optional, Set
from enum import Enum


class SubscriptionTier(str, Enum):
    """Supported subscription tiers."""
    DEMO = "demo"
    BASIC = "basic"
    TMS_PRO = "tms_pro"
    UNIFIED = "unified"
    ENTERPRISE = "enterprise"


class UserRole(str, Enum):
    """Supported user roles."""
    SHIPPER = "shipper"      # Shipper account
    CARRIER = "carrier"      # Carrier account
    BROKER = "broker"        # Broker account
    ADMIN = "admin"          # Platform admin
    SUPER_ADMIN = "super_admin"  # Super admin


class SystemType(str, Enum):
    """Supported system contexts."""
    TMS = "tms"
    LOADBOARD = "loadboard"


# Bot catalog and access policies
BOT_DEFINITIONS = {
    # ========== Basic Tier ==========
    "customer_service": {
        "name_ar": "AI Customer Service",
        "name_en": "AI Customer Service",
        "description_ar": "Automated customer support, notifications, and feedback analysis",
        "description_en": "Automated customer support, notifications, and feedback analysis",
        "min_tier": SubscriptionTier.BASIC,
        "allowed_roles": {UserRole.SHIPPER, UserRole.CARRIER, UserRole.BROKER, UserRole.ADMIN, UserRole.SUPER_ADMIN},
        "allowed_systems": {SystemType.TMS, SystemType.LOADBOARD},
        "color": "#06B6D4",
        "icon": "💬",
        "category": "Basic",
    },
    "documents_manager": {
        "name_ar": "AI Documents Manager",
        "name_en": "AI Documents Manager",
        "description_ar": "Document archiving, compliance workflows, and file control",
        "description_en": "Document archiving, compliance workflows, and file control",
        "min_tier": SubscriptionTier.BASIC,
        "allowed_roles": {UserRole.CARRIER, UserRole.BROKER, UserRole.ADMIN, UserRole.SUPER_ADMIN},
        "allowed_systems": {SystemType.TMS, SystemType.LOADBOARD},
        "color": "#F59E0B",
        "icon": "📄",
        "category": "Basic",
    },
    
    # ========== TMS Pro Tier ==========
    "ai_dispatcher": {
        "name_ar": "AI Dispatcher",
        "name_en": "AI Dispatcher",
        "description_ar": "Real-time dispatch management and task distribution",
        "description_en": "Real-time dispatch management and task distribution",
        "min_tier": SubscriptionTier.TMS_PRO,
        "allowed_roles": {UserRole.CARRIER, UserRole.BROKER, UserRole.ADMIN, UserRole.SUPER_ADMIN},
        "allowed_systems": {SystemType.TMS},
        "color": "#0EA5E9",
        "icon": "🚛",
        "category": "Advanced",
    },
    "operations_manager_bot": {
        "name_ar": "AI Operations Manager",
        "name_en": "AI Operations Manager",
        "description_ar": "Coordinates daily operations and workflow orchestration",
        "description_en": "Coordinates daily operations and workflow orchestration",
        "min_tier": SubscriptionTier.TMS_PRO,
        "allowed_roles": {UserRole.BROKER, UserRole.ADMIN, UserRole.SUPER_ADMIN},
        "allowed_systems": {SystemType.TMS, SystemType.LOADBOARD},
        "color": "#2563EB",
        "icon": "⚙️",
        "category": "Advanced",
    },
    "information_coordinator": {
        "name_ar": "AI Information Coordinator",
        "name_en": "AI Information Coordinator",
        "description_ar": "Routes intelligence and connects data to operations",
        "description_en": "Routes intelligence and connects data to operations",
        "min_tier": SubscriptionTier.TMS_PRO,
        "allowed_roles": {UserRole.BROKER, UserRole.ADMIN, UserRole.SUPER_ADMIN},
        "allowed_systems": {SystemType.TMS, SystemType.LOADBOARD},
        "color": "#6366F1",
        "icon": "🔄",
        "category": "Advanced",
    },
    "sales_bot": {
        "name_ar": "AI Sales Bot",
        "name_en": "AI Sales Bot",
        "description_ar": "CRM insights, lead management, and revenue analysis",
        "description_en": "CRM insights, lead management, and revenue analysis",
        "min_tier": SubscriptionTier.TMS_PRO,
        "allowed_roles": {UserRole.BROKER, UserRole.ADMIN, UserRole.SUPER_ADMIN},
        "allowed_systems": {SystemType.TMS, SystemType.LOADBOARD},
        "color": "#10B981",
        "icon": "💰",
        "category": "Advanced",
    },
    "freight_broker": {
        "name_ar": "AI Freight Broker",
        "name_en": "AI Freight Broker",
        "description_ar": "Handles freight brokerage, shipment creation, and dispatch workflows",
        "description_en": "Handles freight brokerage, shipment creation, and dispatch workflows",
        "min_tier": SubscriptionTier.TMS_PRO,
        "allowed_roles": {UserRole.BROKER, UserRole.ADMIN, UserRole.SUPER_ADMIN},
        "allowed_systems": {SystemType.TMS, SystemType.LOADBOARD},
        "color": "#14B8A6",
        "icon": "FRT",
        "category": "Advanced",
    },
    "finance_bot": {
        "name_ar": "AI Finance Bot",
        "name_en": "AI Finance Bot",
        "description_ar": "Manages invoices, payments, financial summaries, and revenue workflows",
        "description_en": "Manages invoices, payments, financial summaries, and revenue workflows",
        "min_tier": SubscriptionTier.TMS_PRO,
        "allowed_roles": {UserRole.SHIPPER, UserRole.CARRIER, UserRole.BROKER, UserRole.ADMIN, UserRole.SUPER_ADMIN},
        "allowed_systems": {SystemType.TMS, SystemType.LOADBOARD},
        "color": "#F59E0B",
        "icon": "FIN",
        "category": "Advanced",
    },
    "payment_bot": {
        "name_ar": "Payment Gateway Dashboard",
        "name_en": "Payment Gateway Dashboard",
        "description_ar": "Secure payment processing, invoice management, and finance bot integration",
        "description_en": "Secure payment processing, invoice management, and finance bot integration",
        "min_tier": SubscriptionTier.ENTERPRISE,
        "allowed_roles": {UserRole.SHIPPER, UserRole.CARRIER, UserRole.BROKER, UserRole.ADMIN, UserRole.SUPER_ADMIN},
        "allowed_systems": {SystemType.TMS, SystemType.LOADBOARD},
        "color": "#2563EB",
        "icon": "PAY",
        "category": "Enterprise",
    },

    # ========== Unified Tier ==========
    "safety_manager_bot": {
        "name_ar": "AI Safety Manager",
        "name_en": "AI Safety Manager",
        "description_ar": "Monitors safety data, incident reporting, and compliance checks",
        "description_en": "Monitors safety data, incident reporting, and compliance checks",
        "min_tier": SubscriptionTier.UNIFIED,
        "allowed_roles": {UserRole.CARRIER, UserRole.BROKER, UserRole.ADMIN, UserRole.SUPER_ADMIN},
        "allowed_systems": {SystemType.TMS},
        "color": "#F97316",
        "icon": "🛡️",
        "category": "Professional",
        "is_internal": True,
    },
    "intelligence_bot": {
        "name_ar": "AI Intelligence Bot",
        "name_en": "AI Intelligence Bot",
        "description_ar": "Strategic analysis, executive insights, and reporting",
        "description_en": "Strategic analysis, executive insights, and reporting",
        "min_tier": SubscriptionTier.UNIFIED,
        "allowed_roles": {UserRole.BROKER, UserRole.ADMIN, UserRole.SUPER_ADMIN},
        "allowed_systems": {SystemType.TMS, SystemType.LOADBOARD},
        "color": "#7C3AED",
        "icon": "🧠",
        "category": "Professional",
    },
    "mapleload_bot": {
        "name_ar": "AI MapleLoad Canada",
        "name_en": "AI MapleLoad Canada",
        "description_ar": "Canadian logistics intelligence and cross-border coordination",
        "description_en": "Canadian logistics intelligence and cross-border coordination",
        "min_tier": SubscriptionTier.UNIFIED,
        "allowed_roles": {UserRole.CARRIER, UserRole.BROKER, UserRole.ADMIN, UserRole.SUPER_ADMIN},
        "allowed_systems": {SystemType.TMS, SystemType.LOADBOARD},
        "color": "#F97316",
        "icon": "🍁",
        "category": "Professional",
    },
    
    # ========== Enterprise Tier ==========
    "general_manager": {
        "name_ar": "AI General Manager",
        "name_en": "AI General Manager",
        "description_ar": "Executive oversight and strategic reporting",
        "description_en": "Executive oversight and strategic reporting",
        "min_tier": SubscriptionTier.ENTERPRISE,
        "allowed_roles": {UserRole.ADMIN, UserRole.SUPER_ADMIN},
        "allowed_systems": {SystemType.TMS, SystemType.LOADBOARD},
        "color": "#4F46E5",
        "icon": "👔",
        "category": "Enterprise",
    },
    "legal_bot": {
        "name_ar": "AI Legal Consultant",
        "name_en": "AI Legal Consultant",
        "description_ar": "Reviews legal documents and ensures compliance",
        "description_en": "Reviews legal documents and ensures compliance",
        "min_tier": SubscriptionTier.ENTERPRISE,
        "allowed_roles": {UserRole.BROKER, UserRole.ADMIN, UserRole.SUPER_ADMIN},
        "allowed_systems": {SystemType.TMS, SystemType.LOADBOARD},
        "color": "#64748B",
        "icon": "⚖️",
        "category": "Enterprise",
    },
    "security_manager_bot": {
        "name_ar": "AI Security Manager",
        "name_en": "AI Security Manager",
        "description_ar": "Security monitoring, threat detection, and compliance auditing",
        "description_en": "Security monitoring, threat detection, and compliance auditing",
        "min_tier": SubscriptionTier.ENTERPRISE,
        "allowed_roles": {UserRole.ADMIN, UserRole.SUPER_ADMIN},
        "allowed_systems": {SystemType.TMS, SystemType.LOADBOARD},
        "color": "#EF4444",
        "icon": "🔒",
        "category": "Enterprise",
        "is_internal": True,
    },
    "system_manager_bot": {
        "name_ar": "AI System Manager",
        "name_en": "AI System Manager",
        "description_ar": "System performance, infrastructure health, and optimization",
        "description_en": "System performance, infrastructure health, and optimization",
        "min_tier": SubscriptionTier.ENTERPRISE,
        "allowed_roles": {UserRole.ADMIN, UserRole.SUPER_ADMIN},
        "allowed_systems": {SystemType.TMS, SystemType.LOADBOARD},
        "color": "#475569",
        "icon": "🖥️",
        "category": "Enterprise",
        "is_internal": True,
    },
    "maintenance_dev": {
        "name_ar": "AI Maintenance Dev",
        "name_en": "AI Maintenance Dev",
        "description_ar": "Monitors bot health, fixes bugs, and suggests system upgrades",
        "description_en": "Monitors bot health, fixes bugs, and suggests system upgrades",
        "min_tier": SubscriptionTier.ENTERPRISE,
        "allowed_roles": {UserRole.ADMIN, UserRole.SUPER_ADMIN},
        "allowed_systems": {SystemType.TMS, SystemType.LOADBOARD},
        "color": "#64748B",
        "icon": "🔧",
        "category": "Enterprise",
        "is_internal": True,
    },
    "partner_manager": {
        "name_ar": "AI Partner Manager",
        "name_en": "AI Partner Manager",
        "description_ar": "Partner operations, alliance workflows, and partner performance management",
        "description_en": "Partner operations, alliance workflows, and partner performance management",
        "min_tier": SubscriptionTier.ENTERPRISE,
        "allowed_roles": {UserRole.ADMIN, UserRole.SUPER_ADMIN},
        "allowed_systems": {SystemType.TMS, SystemType.LOADBOARD},
        "color": "#8B5CF6",
        "icon": "PRT",
        "category": "Management",
    },
    "weather_bot": {
        "name_ar": "AI Weather Bot",
        "name_en": "AI Weather Bot",
        "description_ar": "Weather monitoring and operational alerts",
        "description_en": "Weather monitoring and operational alerts",
        "min_tier": SubscriptionTier.TMS_PRO,
        "allowed_roles": {UserRole.SHIPPER, UserRole.CARRIER, UserRole.BROKER, UserRole.ADMIN, UserRole.SUPER_ADMIN},
        "allowed_systems": {SystemType.TMS, SystemType.LOADBOARD},
        "color": "#38BDF8",
        "icon": "🌦️",
        "category": "Advanced",
        "is_internal": True,
        "feature_only": True,
    },
}


def get_available_bots(
    subscription_tier: str,
    user_role: str,
    system_type: str = "tms",
    language: str = "ar"
) -> List[Dict]:
    """
    Return all bots available for a user context.
    
    Args:
        subscription_tier: tier key (demo, basic, tms_pro, unified, enterprise)
        user_role: role key (shipper, carrier, broker, admin, super_admin)
        system_type: system key (tms, loadboard)
        language: language key (ar, en)
    
    Returns:
        List of available bot payloads
    """
    # Normalize and validate context
    try:
        tier = SubscriptionTier(subscription_tier.lower())
    except ValueError:
        tier = SubscriptionTier.DEMO
    
    try:
        role = UserRole(user_role.lower())
    except ValueError:
        role = UserRole.SHIPPER
    
    try:
        sys_type = SystemType(system_type.lower())
    except ValueError:
        sys_type = SystemType.TMS
    
    # Tier hierarchy for entitlement checks
    tier_order = {
        SubscriptionTier.DEMO: 0,
        SubscriptionTier.BASIC: 1,
        SubscriptionTier.TMS_PRO: 2,
        SubscriptionTier.UNIFIED: 3,
        SubscriptionTier.ENTERPRISE: 4,
    }
    
    user_tier_level = tier_order.get(tier, 0)
    available_bots = []
    
    is_admin = role in {UserRole.ADMIN, UserRole.SUPER_ADMIN}

    for bot_id, bot_config in BOT_DEFINITIONS.items():
        if bot_config.get("feature_only"):
            continue

        # Filter by minimum tier
        min_tier_level = tier_order.get(bot_config["min_tier"], 0)
        if user_tier_level < min_tier_level:
            continue
        
        # Filter by role
        if role not in bot_config["allowed_roles"]:
            continue
        
        # Filter by system context
        if sys_type not in bot_config["allowed_systems"]:
            continue
        
        # Restrict internal bots to admin users
        if bot_config.get("is_internal") and not is_admin:
            continue

        # Build response record
        bot_info = {
            "id": bot_id,
            "name": bot_config[f"name_{language}"] if f"name_{language}" in bot_config else bot_config["name_en"],
            "description": bot_config[f"description_{language}"] if f"description_{language}" in bot_config else bot_config["description_en"],
            "color": bot_config["color"],
            "icon": bot_config.get("icon", "🤖"),
            "category": bot_config.get("category", "General"),
            "status": "active",
            "tier_required": bot_config["min_tier"].value,
        }
        available_bots.append(bot_info)
    
    return available_bots


def get_available_bots_with_services(
    subscription_tier: str,
    user_role: str,
    system_type: str = "tms",
    language: str = "ar"
) -> Dict[str, List[Dict]]:
    """
    Return categorized bot access payload (bots + internal services).
    Returns bots list plus internal services for non-admin users.
    """
    # Normalize and validate context
    try:
        tier = SubscriptionTier(subscription_tier.lower())
    except ValueError:
        tier = SubscriptionTier.DEMO

    try:
        role = UserRole(user_role.lower())
    except ValueError:
        role = UserRole.SHIPPER

    try:
        sys_type = SystemType(system_type.lower())
    except ValueError:
        sys_type = SystemType.TMS

    tier_order = {
        SubscriptionTier.DEMO: 0,
        SubscriptionTier.BASIC: 1,
        SubscriptionTier.TMS_PRO: 2,
        SubscriptionTier.UNIFIED: 3,
        SubscriptionTier.ENTERPRISE: 4,
    }

    user_tier_level = tier_order.get(tier, 0)
    bots: List[Dict] = []
    services: List[Dict] = []

    is_admin = role in {UserRole.ADMIN, UserRole.SUPER_ADMIN}

    for bot_id, bot_config in BOT_DEFINITIONS.items():
        if bot_config.get("feature_only"):
            continue

        min_tier_level = tier_order.get(bot_config["min_tier"], 0)
        if user_tier_level < min_tier_level:
            continue

        if role not in bot_config["allowed_roles"]:
            continue

        if sys_type not in bot_config["allowed_systems"]:
            continue

        bot_info = {
            "id": bot_id,
            "name": bot_config.get(f"name_{language}", bot_config["name_en"]),
            "description": bot_config.get(f"description_{language}", bot_config["description_en"]),
            "color": bot_config["color"],
            "icon": bot_config.get("icon", "🤖"),
            "category": bot_config.get("category", "General"),
            "status": "active",
            "tier_required": bot_config["min_tier"].value,
            "is_internal": bool(bot_config.get("is_internal")),
        }

        if bot_info["is_internal"] and not is_admin:
            services.append(bot_info)
        else:
            bots.append(bot_info)

    return {"bots": bots, "services": services}


def check_bot_access(
    bot_id: str,
    subscription_tier: str,
    user_role: str,
    system_type: str = "tms"
) -> bool:
    """
    Check access for a single bot in a given user context.
    
    Args:
        bot_id: bot identifier
        subscription_tier: tier key
        user_role: role key
        system_type: system key
    
    Returns:
        True if access is allowed
    """
    if bot_id not in BOT_DEFINITIONS:
        return False
    
    bot_config = BOT_DEFINITIONS[bot_id]
    
    try:
        tier = SubscriptionTier(subscription_tier.lower())
        role = UserRole(user_role.lower())
        sys_type = SystemType(system_type.lower())
    except ValueError:
        return False
    
    # Tier hierarchy for entitlement checks
    tier_order = {
        SubscriptionTier.DEMO: 0,
        SubscriptionTier.BASIC: 1,
        SubscriptionTier.TMS_PRO: 2,
        SubscriptionTier.UNIFIED: 3,
        SubscriptionTier.ENTERPRISE: 4,
    }
    
    user_tier_level = tier_order.get(tier, 0)
    min_tier_level = tier_order.get(bot_config["min_tier"], 0)
    
    return (
        user_tier_level >= min_tier_level and
        role in bot_config["allowed_roles"] and
        sys_type in bot_config["allowed_systems"]
    )


def get_bot_categories() -> Dict[str, List[str]]:
    """Get bot categories"""
    categories = {}
    for bot_id, bot_config in BOT_DEFINITIONS.items():
        category = bot_config.get("category", "General")
        if category not in categories:
            categories[category] = []
        categories[category].append(bot_id)
    return categories


def get_subscription_summary(subscription_tier: str) -> Dict:
    """
    Return summary metadata for the given subscription tier.
    
    Args:
        subscription_tier: tier key
    
    Returns:
        Tier summary payload
    """
    tier_info = {
        "demo": {
            "name_ar": "Trial",
            "name_en": "Trial",
            "total_bots": 2,
            "description_ar": "Trial access with limited capabilities",
        },
        "basic": {
            "name_ar": "Basic",
            "name_en": "Basic",
            "total_bots": 2,
            "description_ar": "Essential automation for core operations",
        },
        "tms_pro": {
            "name_ar": "TMS Pro",
            "name_en": "TMS Pro",
            "total_bots": 7,
            "description_ar": "Advanced dispatch and operations automation",
        },
        "unified": {
            "name_ar": "Unified",
            "name_en": "Unified",
            "total_bots": 10,
            "description_ar": "Cross-functional AI suite for logistics teams",
        },
        "enterprise": {
            "name_ar": "Enterprise",
            "name_en": "Enterprise",
            "total_bots": 15,
            "description_ar": "Full platform governance and strategic automation",
        },
    }
    
    return tier_info.get(subscription_tier.lower(), tier_info["demo"])
