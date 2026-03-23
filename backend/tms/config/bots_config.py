from __future__ import annotations

"""
TMS Bots configuration without introducing new bots. English-only per repo conventions.

Provides mappings for customer-facing bots, internal/admin-only bots, permission levels,
subscription plans, and system access profiles.
"""

# Customer-facing bots (align with existing bot names)
CUSTOMER_BOTS = {
    "freight_broker": {
        "key": "fb",
        "name": "AI Freight Broker",
        "description": "Pricing, carrier selection, trip coordination",
        "icon": "🚚",
        "default_permission": "quick_run",
    },
    "finance_bot": {
        "key": "fin",
        "name": "AI Finance Bot",
        "description": "Invoices, cost analysis, collections",
        "icon": "💰",
        "default_permission": "control_panel",
    },
    "documents_manager": {
        "key": "doc",
        "name": "AI Documents Manager",
        "description": "Documents, BOL, RateCon, archiving",
        "icon": "📄",
        "default_permission": "control_panel",
    },
    "customer_service": {
        "key": "cs",
        "name": "AI Customer Service",
        "description": "Support, tracking, tickets",
        "icon": "👥",
        "default_permission": "control_panel",
    },
    "sales_team": {
        "key": "sales",
        "name": "AI Sales Team",
        "description": "CRM, customers, quotes",
        "icon": "📈",
        "default_permission": "control_panel",
    },
    "mapleload_canada": {
        "key": "mlc",
        "name": "MapleLoad Canada",
        "description": "Canadian sourcing",
        "icon": "🍁",
        "default_permission": "quick_run",
    },
}

# Internal bots (admin-only)
INTERNAL_BOTS = {
    "general_manager": {
        "key": "gm",
        "name": "AI General Manager",
        "description": "Executive reports and strategy",
        "visible_to": ["admin", "super_admin"],
    },
    "operations_manager": {
        "key": "om",
        "name": "AI Operations Manager",
        "description": "Orchestrates bot operations",
        "visible_to": ["admin", "super_admin"],
    },
    "system_admin": {
        "key": "sa",
        "name": "AI System Admin",
        "description": "System and users management",
        "visible_to": ["admin", "super_admin"],
    },
    "security_manager": {
        "key": "sec",
        "name": "AI Security Manager",
        "description": "Platform security",
        "visible_to": ["admin", "super_admin"],
    },
    "dev_maintenance": {
        "key": "dev",
        "name": "AI Dev Maintenance",
        "description": "Engineering maintenance and improvements",
        "visible_to": ["admin", "super_admin"],
    },
    "information_coordinator": {
        "key": "ic",
        "name": "AI Information Coordinator",
        "description": "Data coordination and dashboards",
        "visible_to": ["admin", "super_admin"],
    },
    "strategy_advisor": {
        "key": "strat",
        "name": "AI Strategy Advisor",
        "description": "Market analysis and recommendations",
        "visible_to": ["admin", "super_admin"],
    },
}

PERMISSION_LEVELS = {
    "view": {
        "level": 1,
        "name": "View Only",
        "description": "Read reports and dashboards",
        "icon": "👁️",
    },
    "quick_run": {
        "level": 2,
        "name": "Quick Run",
        "description": "Use prebuilt templates",
        "icon": "⚡",
    },
    "control_panel": {
        "level": 3,
        "name": "Control Panel",
        "description": "Full operational control",
        "icon": "🎮",
    },
    "configure": {
        "level": 4,
        "name": "Configure",
        "description": "Integrations and advanced settings",
        "icon": "⚙️",
    },
}

SUBSCRIPTION_PLANS = {
    "starter": {
        "name": "Starter",
        "code": "starter",
        "monthly_price": 99,
        "bots": {"cs": "quick_run", "doc": "quick_run", "fb": "quick_run", "mlc": "quick_run"},
        "max_users": 3,
        "max_shipments": 100,
        "features": ["Basic run log", "Limited users (3)", "Basic support"],
    },
    "professional": {
        "name": "Professional",
        "code": "professional",
        "monthly_price": 299,
        "bots": {
            "cs": "control_panel",
            "doc": "control_panel",
            "fb": "control_panel",
            "fin": "control_panel",
            "sales": "control_panel",
            "mlc": "quick_run",
        },
        "max_users": 10,
        "max_shipments": 500,
        "features": ["Dashboards", "Some custom settings", "Priority support", "Advanced reports"],
    },
    "enterprise": {
        "name": "Enterprise",
        "code": "enterprise",
        "monthly_price": 799,
        "bots": {
            "cs": "configure",
            "doc": "configure",
            "fb": "configure",
            "fin": "configure",
            "sales": "configure",
            "mlc": "control_panel",
        },
        "max_users": 9999,
        "max_shipments": 99999,
        "features": [
            "Full integrations",
            "Scheduled automation",
            "Audit logs",
            "Dedicated support",
            "API and Webhooks",
        ],
    },
}

SYSTEM_ACCESS = {
    "gts_main": {
        "name": "GTS Main Platform",
        "description": "Primary partners and customers portal",
        "bots": ["cs", "sales"],
        "permissions": ["view", "quick_run"],
    },
    "tms": {
        "name": "TMS System",
        "description": "Integrated transport management system",
        "bots": list(CUSTOMER_BOTS.keys()),
        "permissions": ["view", "quick_run", "control_panel", "configure"],
    },
    "both": {
        "name": "Both Systems",
        "description": "Access to both systems",
        "bots": list(CUSTOMER_BOTS.keys()) + list(INTERNAL_BOTS.keys()),
        "permissions": ["view", "quick_run", "control_panel", "configure"],
    },
}
