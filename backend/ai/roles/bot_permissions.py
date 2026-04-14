from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Set, Dict, Any, List


@dataclass(frozen=True)
class BotPolicySpec:
    visible_to_roles: Set[str]
    required_features: Set[str] = field(default_factory=set)
    hidden: bool = False


BOT_POLICIES: Dict[str, BotPolicySpec] = {
    # Core Business Bots
    "customer_service": BotPolicySpec(
        visible_to_roles={"admin", "subscription_user", "super_admin"},
        required_features={"cs_access"},
    ),
    "documents_manager": BotPolicySpec(
        visible_to_roles={"admin", "subscription_user", "super_admin"},
        required_features={"documents_access"},
    ),
    "freight_bot": BotPolicySpec(
        visible_to_roles={"admin", "subscription_user", "super_admin"},
        required_features={"freight_access"},
    ),
    "freight_broker": BotPolicySpec(
        visible_to_roles={"admin", "subscription_user", "super_admin", "system_admin"},
    ),
    "general_manager": BotPolicySpec(visible_to_roles={"admin", "system_admin", "super_admin"}),
    "information_coordinator": BotPolicySpec(visible_to_roles={"admin", "system_admin", "super_admin"}),
    "intelligence_bot": BotPolicySpec(visible_to_roles={"admin", "system_admin", "super_admin"}),
    "legal_bot": BotPolicySpec(visible_to_roles={"admin", "system_admin", "super_admin"}),
    "legal_consultant": BotPolicySpec(visible_to_roles={"admin", "system_admin", "super_admin"}),
    "legal_counsel": BotPolicySpec(visible_to_roles={"admin", "system_admin", "super_admin"}),
    "maintenance_dev": BotPolicySpec(visible_to_roles={"admin", "system_admin", "super_admin"}),
    "dev_maintenance": BotPolicySpec(visible_to_roles={"admin", "system_admin", "super_admin"}),
    "maintenance_dev_bot": BotPolicySpec(visible_to_roles={"admin", "system_admin", "super_admin"}),
    "marketing_manager": BotPolicySpec(visible_to_roles={"admin", "system_admin", "super_admin", "subscription_user"}, required_features={"sales_access"}),
    "marketing_manager_bot": BotPolicySpec(visible_to_roles={"admin", "system_admin", "super_admin", "subscription_user"}, required_features={"sales_access"}),
    "marketing_bot": BotPolicySpec(visible_to_roles={"admin", "system_admin", "super_admin", "subscription_user"}, required_features={"sales_access"}),
    "mapleload_bot": BotPolicySpec(
        visible_to_roles={"admin", "subscription_user", "super_admin"},
        required_features={"mapleload_access"},
    ),
    "mapleload_canada": BotPolicySpec(
        visible_to_roles={"admin", "subscription_user", "super_admin"},
        required_features={"mapleload_access"},
    ),
    "operations_bot": BotPolicySpec(visible_to_roles={"admin", "system_admin", "super_admin"}),
    "operations_manager": BotPolicySpec(visible_to_roles={"admin", "system_admin", "super_admin"}),
    "operations_manager_bot": BotPolicySpec(visible_to_roles={"admin", "system_admin", "super_admin"}),
    "partner_bot": BotPolicySpec(visible_to_roles={"admin", "partner", "system_admin", "super_admin"}),
    "partner_manager": BotPolicySpec(visible_to_roles={"admin", "system_admin", "super_admin"}),
    "safety_bot": BotPolicySpec(
        visible_to_roles={"admin", "subscription_user", "super_admin"},
        required_features={"safety_access"},
    ),
    "sales_bot": BotPolicySpec(
        visible_to_roles={"admin", "subscription_user", "super_admin"},
        required_features={"sales_access"},
    ),
    "security_bot": BotPolicySpec(visible_to_roles={"admin", "system_admin", "super_admin"}),
    "security_manager": BotPolicySpec(visible_to_roles={"admin", "system_admin", "super_admin"}),
    "security_manager_bot": BotPolicySpec(visible_to_roles={"admin", "system_admin", "super_admin"}),
    "system_bot": BotPolicySpec(visible_to_roles={"admin", "system_admin", "super_admin"}),
    "system_manager": BotPolicySpec(visible_to_roles={"admin", "system_admin", "super_admin"}),
    "system_manager_bot": BotPolicySpec(visible_to_roles={"admin", "system_admin", "super_admin"}),
    "system_admin": BotPolicySpec(visible_to_roles={"admin", "system_admin", "super_admin"}),
    "trainer_bot": BotPolicySpec(visible_to_roles={"admin", "system_admin", "super_admin"}),
    "trainer": BotPolicySpec(visible_to_roles={"admin", "system_admin", "super_admin"}),
    "training_bot": BotPolicySpec(visible_to_roles={"admin", "system_admin", "super_admin"}),
    "ai_dispatcher": BotPolicySpec(visible_to_roles={"admin", "system_admin", "super_admin"}),
    "finance_bot": BotPolicySpec(visible_to_roles={"admin", "system_admin", "super_admin", "subscription_user"}, required_features={"finance_access"}),
}

BOT_LAYERS: Dict[str, str] = {
    "customer_service": "support",
    "documents_manager": "infrastructure",
    "freight_bot": "execution",
    "freight_broker": "execution",
    "general_manager": "governance",
    "information_coordinator": "intelligence",
    "intelligence_bot": "intelligence",
    "legal_bot": "governance",
    "legal_consultant": "governance",
    "legal_counsel": "governance",
    "maintenance_dev": "infrastructure",
    "dev_maintenance": "infrastructure",
    "maintenance_dev_bot": "infrastructure",
    "marketing_manager": "support",
    "marketing_manager_bot": "support",
    "marketing_bot": "support",
    "mapleload_bot": "execution",
    "mapleload_canada": "execution",
    "operations_bot": "execution",
    "operations_manager": "execution",
    "operations_manager_bot": "execution",
    "partner_bot": "support",
    "partner_manager": "governance",
    "safety_bot": "governance",
    "sales_bot": "support",
    "security_bot": "governance",
    "security_manager": "governance",
    "security_manager_bot": "governance",
    "system_bot": "infrastructure",
    "system_manager": "infrastructure",
    "system_manager_bot": "infrastructure",
    "system_admin": "infrastructure",
    "trainer_bot": "infrastructure",
    "trainer": "infrastructure",
    "training_bot": "infrastructure",
    "ai_dispatcher": "intelligence",
    "finance_bot": "execution",
}


BOT_CAPABILITIES: Dict[str, Dict[str, Any]] = {
    "customer_service": {
        "name": "CS - Customer Service",
        "description": "Handles customer inquiries, support tickets, and service requests.",
        "category": "Support",
        "icon": "CS",
        "color": "violet",
        "tasks": [
            "Respond to customer inquiries",
            "Resolve issues and complaints",
            "Manage support tickets",
            "Analyze customer feedback",
            "Improve customer experience metrics",
        ],
        "reporting": {
            "frequency": "daily",
            "receives_from": [],
            "sends_to": ["operations_bot"],
        },
    },
    "documents_manager": {
        "name": "DOC - Documents Manager",
        "description": "Handles document OCR, classification, and management.",
        "category": "Infrastructure",
        "icon": "DOC",
        "color": "indigo",
        "tasks": [
            "Process documents with OCR",
            "Classify and organize documents",
            "Extract structured data",
            "Manage document access",
            "Track document lifecycle",
        ],
        "reporting": {
            "frequency": "daily",
            "receives_from": [],
            "sends_to": ["operations_bot"],
        },
    },
    "freight_bot": {
        "name": "FRT - Freight Bot",
        "description": "Manages freight booking, carrier matching, and load analysis.",
        "category": "Execution",
        "icon": "FRT",
        "color": "blue",
        "tasks": [
            "Analyze freight lanes and rates",
            "Match loads with carriers",
            "Book and track shipments",
            "Optimize routing and capacity",
            "Monitor freight performance",
        ],
        "reporting": {
            "frequency": "hourly",
            "receives_from": [],
            "sends_to": ["operations_bot"],
        },
    },
    "freight_broker": {
        "name": "FRT - Freight Broker",
        "description": "Freight booking, carrier matching, and load analysis.",
        "category": "Execution",
        "icon": "FRT",
        "color": "blue",
        "tasks": [
            "Analyze freight lanes and rates",
            "Match loads with carriers",
            "Book and track shipments",
            "Optimize routing and capacity",
            "Monitor freight performance",
        ],
    },
    "general_manager": {
        "name": "GM - General Manager",
        "description": "Executive strategy, reporting, and high-level decision support.",
        "category": "Governance",
        "icon": "GM",
        "color": "slate",
        "tasks": [
            "Guide company strategy",
            "Consolidate executive reporting",
            "Make strategic decisions",
            "Align goals across organization",
            "Evaluate system performance",
        ],
        "reporting": {
            "frequency": "weekly",
            "receives_from": ["operations_bot", "intelligence_bot"],
            "sends_to": ["human_executive"],
        },
    },
    "information_coordinator": {
        "name": "IC - Information Coordinator",
        "description": "Coordinates information flow and intelligence across the system.",
        "category": "Intelligence",
        "icon": "IC",
        "color": "sky",
        "tasks": [
            "Coordinate data collection",
            "Harmonize intelligence sources",
            "Build reporting dashboards",
            "Provide predictive insights",
            "Ensure data quality",
        ],
        "reporting": {
            "frequency": "daily",
            "receives_from": [],
            "sends_to": ["intelligence_bot"],
        },
    },
    "intelligence_bot": {
        "name": "GIT - Global Intelligence & Trends",
        "description": "Strategic analysis and executive insights.",
        "category": "Intelligence",
        "icon": "GIT",
        "color": "cyan",
        "tasks": [
            "Analyze market trends",
            "Evaluate strategic opportunities",
            "Provide executive insights",
            "Monitor competitive landscape",
            "Develop strategic recommendations",
        ],
        "reporting": {
            "frequency": "weekly",
            "receives_from": ["information_coordinator"],
            "sends_to": ["general_manager"],
        },
    },
    "legal_bot": {
        "name": "LG - Legal Bot",
        "description": "Legal document review and compliance management.",
        "category": "Governance",
        "icon": "LG",
        "color": "rose",
        "tasks": [
            "Review contracts and agreements",
            "Track regulatory changes",
            "Provide legal guidance",
            "Manage compliance risk",
            "Draft legal documentation",
        ],
        "reporting": {
            "frequency": "monthly",
            "receives_from": [],
            "sends_to": ["general_manager"],
        },
    },
    "legal_consultant": {
        "name": "LG - Legal Consultant",
        "description": "Alias for the legal consultant bot runtime.",
        "category": "Governance",
        "icon": "LG",
        "color": "rose",
    },
    "legal_counsel": {
        "name": "LG - Legal Counsel",
        "description": "Alias for the legal consultant bot runtime.",
        "category": "Governance",
        "icon": "LG",
        "color": "rose",
    },
    "maintenance_dev": {
        "name": "MA - Maintenance & Dev",
        "description": "System maintenance, health checks, and development support.",
        "category": "Infrastructure",
        "icon": "MA",
        "color": "slate",
        "tasks": [
            "Monitor system health",
            "Perform maintenance tasks",
            "Check system dependencies",
            "Backup data",
            "Optimize performance",
        ],
        "reporting": {
            "frequency": "daily",
            "receives_from": [],
            "sends_to": ["system_bot"],
        },
    },
    "mapleload_bot": {
        "name": "MLP - MapleLoad Bot",
        "description": "Canadian market intelligence and load matching.",
        "category": "Execution",
        "icon": "MLP",
        "color": "green",
        "tasks": [
            "Source Canadian freight",
            "Analyze Canadian market trends",
            "Match loads in Canada",
            "Manage Canadian partnerships",
            "Track Canadian performance",
        ],
        "reporting": {
            "frequency": "daily",
            "receives_from": [],
            "sends_to": ["freight_bot"],
        },
    },
    "mapleload_canada": {
        "name": "MLC - MapleLoad Canada",
        "description": "Real-time Canadian freight market monitoring and rate analysis.",
        "category": "Execution",
        "icon": "MLC",
        "color": "emerald",
        "tasks": [
            "Monitor Canadian market rates",
            "Daily freight rate reports (6 AM BC)",
            "Hourly rate change detection",
            "Weekly trend analysis",
            "Send rate alerts and notifications",
            "Track 8 major Canadian routes",
        ],
        "reporting": {
            "frequency": "hourly",
            "receives_from": [],
            "sends_to": ["freight_bot", "mapleload_bot"],
        },
    },
    "operations_bot": {
        "name": "OPS - Operations Bot",
        "description": "Operational workflow management and coordination.",
        "category": "Execution",
        "icon": "OPS",
        "color": "blue",
        "tasks": [
            "Coordinate operational workflows",
            "Manage daily execution",
            "Monitor operational performance",
            "Resolve bottlenecks",
            "Generate performance reports",
        ],
        "reporting": {
            "frequency": "daily",
            "receives_from": ["freight_bot", "sales_bot", "customer_service"],
            "sends_to": ["general_manager"],
        },
    },
    "operations_manager": {
        "name": "OPS - Operations Manager",
        "description": "Operational workflow management and coordination.",
        "category": "Execution",
        "icon": "OPS",
        "color": "blue",
        "tasks": [
            "Coordinate operational workflows",
            "Manage daily execution",
            "Monitor operational performance",
            "Resolve bottlenecks",
            "Generate performance reports",
        ],
    },
    "operations_manager_bot": {
        "name": "OPS - Operations Manager",
        "description": "Operational workflow management and coordination.",
        "category": "Execution",
        "icon": "OPS",
        "color": "blue",
        "tasks": [
            "Coordinate operational workflows",
            "Manage daily execution",
            "Monitor operational performance",
            "Resolve bottlenecks",
            "Generate performance reports",
        ],
    },
    "finance_bot": {
        "name": "FIN - Finance Bot",
        "description": "Financial insights, expenses, and revenue analysis.",
        "category": "Execution",
        "icon": "FIN",
        "color": "amber",
        "tasks": [
            "Summarize expenses and revenue",
            "Track profitability",
            "Surface financial anomalies",
        ],
    },
    "partner_bot": {
        "name": "PART - Partner Bot",
        "description": "Partner relationship management and collaboration.",
        "category": "Support",
        "icon": "PART",
        "color": "emerald",
        "tasks": [
            "Manage partner relationships",
            "Track partner performance",
            "Develop partnership opportunities",
            "Coordinate partner communications",
            "Analyze partnership ROI",
        ],
        "reporting": {
            "frequency": "weekly",
            "receives_from": [],
            "sends_to": ["operations_bot"],
        },
    },
    "safety_bot": {
        "name": "SAFE - Safety Bot",
        "description": "Safety incident tracking and compliance management.",
        "category": "Governance",
        "icon": "SAFE",
        "color": "amber",
        "tasks": [
            "Track safety incidents",
            "Monitor compliance",
            "Analyze risk factors",
            "Generate safety reports",
            "Recommend safety improvements",
        ],
        "reporting": {
            "frequency": "weekly",
            "receives_from": [],
            "sends_to": ["operations_bot"],
        },
    },
    "sales_bot": {
        "name": "SALE - Sales Bot",
        "description": "Sales analytics, forecasting, and revenue optimization.",
        "category": "Support",
        "icon": "SALE",
        "color": "green",
        "tasks": [
            "Analyze sales performance",
            "Generate sales forecasts",
            "Track customer relationships",
            "Identify sales opportunities",
            "Optimize pricing strategies",
        ],
        "reporting": {
            "frequency": "weekly",
            "receives_from": [],
            "sends_to": ["operations_bot"],
        },
    },
    "security_bot": {
        "name": "SEC - Security Bot",
        "description": "Security monitoring and threat detection.",
        "category": "Governance",
        "icon": "SEC",
        "color": "red",
        "tasks": [
            "Monitor security threats",
            "Detect intrusions",
            "Scan vulnerabilities",
            "Manage access controls",
            "Audit security events",
        ],
        "reporting": {
            "frequency": "realtime",
            "receives_from": [],
            "sends_to": ["system_bot"],
        },
    },
    "dev_maintenance": {
        "name": "MA - Maintenance Dev",
        "description": "Alias for the shared maintenance runtime.",
        "category": "Infrastructure",
        "icon": "MA",
        "color": "slate",
    },
    "maintenance_dev_bot": {
        "name": "MA - Maintenance Dev",
        "description": "Alias for the shared maintenance runtime.",
        "category": "Infrastructure",
        "icon": "MA",
        "color": "slate",
    },
    "marketing_manager": {
        "name": "MKT - Marketing Manager",
        "description": "Campaign management, lead generation, ROI analysis, promotions, and market growth workflows.",
        "category": "Support",
        "icon": "MKT",
        "color": "pink",
        "tasks": [
            "Create and optimize marketing campaigns",
            "Score and qualify inbound leads",
            "Analyze ROI by campaign and channel",
            "Segment customers for retention and growth",
            "Launch promotions tied to revenue goals",
        ],
        "reporting": {
            "frequency": "daily",
            "receives_from": ["intelligence_bot"],
            "sends_to": ["sales_bot"],
        },
    },
    "marketing_manager_bot": {
        "name": "MKT - Marketing Manager",
        "description": "Alias for the shared marketing manager runtime.",
        "category": "Support",
        "icon": "MKT",
        "color": "pink",
    },
    "marketing_bot": {
        "name": "MKT - Marketing Manager",
        "description": "Alias for the shared marketing manager runtime.",
        "category": "Support",
        "icon": "MKT",
        "color": "pink",
    },
    "security_manager": {
        "name": "SEC - Security Manager",
        "description": "Alias for the shared security manager runtime.",
        "category": "Governance",
        "icon": "SEC",
        "color": "red",
    },
    "security_manager_bot": {
        "name": "SEC - Security Manager",
        "description": "Alias for the shared security manager runtime.",
        "category": "Governance",
        "icon": "SEC",
        "color": "red",
    },
    "system_bot": {
        "name": "SYS - System Bot",
        "description": "System health monitoring and optimization.",
        "category": "Infrastructure",
        "icon": "SYS",
        "color": "gray",
        "tasks": [
            "Monitor system performance",
            "Track system metrics",
            "Optimize resource usage",
            "Detect system issues",
            "Generate system reports",
        ],
        "reporting": {
            "frequency": "hourly",
            "receives_from": ["maintenance_dev"],
            "sends_to": ["operations_bot"],
        },
    },
    "system_manager": {
        "name": "SYS - System Manager",
        "description": "Alias for the shared system manager runtime.",
        "category": "Infrastructure",
        "icon": "SYS",
        "color": "gray",
    },
    "system_manager_bot": {
        "name": "SYS - System Manager",
        "description": "Alias for the shared system manager runtime.",
        "category": "Infrastructure",
        "icon": "SYS",
        "color": "gray",
    },
    "system_admin": {
        "name": "SYS - System Manager",
        "description": "Alias for the shared system manager runtime.",
        "category": "Infrastructure",
        "icon": "SYS",
        "color": "gray",
    },
    "trainer_bot": {
        "name": "TRN - AI Trainer Bot",
        "description": "Training and simulation orchestration, readiness assessment, plan generation, and certification workflows.",
        "category": "Infrastructure",
        "icon": "TRN",
        "color": "teal",
        "tasks": [
            "Register trainable bots",
            "Assess readiness and weak points",
            "Generate structured training plans",
            "Run training sessions and simulations",
            "Publish reports and certificates",
        ],
        "reporting": {
            "frequency": "daily",
            "receives_from": ["general_manager", "maintenance_dev", "system_bot"],
            "sends_to": ["general_manager"],
        },
    },
    "trainer": {
        "name": "TRN - AI Trainer Bot",
        "description": "Alias for the trainer runtime.",
        "category": "Infrastructure",
        "icon": "TRN",
        "color": "teal",
    },
    "training_bot": {
        "name": "TRN - AI Trainer Bot",
        "description": "Alias for the trainer runtime.",
        "category": "Infrastructure",
        "icon": "TRN",
        "color": "teal",
    },
    "ai_dispatcher": {
        "name": "AID - AI Dispatcher",
        "description": "Intelligent task distribution and workflow orchestration.",
        "category": "Intelligence",
        "icon": "AID",
        "color": "purple",
        "tasks": [
            "Distribute tasks to bots",
            "Orchestrate workflows",
            "Monitor task completion",
            "Optimize resource allocation",
            "Handle task prioritization",
        ],
        "reporting": {
            "frequency": "realtime",
            "receives_from": [],
            "sends_to": ["operations_bot"],
        },
    },
}


VALID_REPORT_FLOWS: Dict[str, List[str]] = {
    "customer_service": ["operations_bot"],
    "documents_manager": ["operations_bot"],
    "freight_bot": ["operations_bot"],
    "general_manager": ["human_executive"],
    "information_coordinator": ["intelligence_bot"],
    "intelligence_bot": ["general_manager"],
    "legal_bot": ["general_manager"],
    "legal_consultant": ["general_manager"],
    "legal_counsel": ["general_manager"],
    "maintenance_dev": ["system_bot"],
    "dev_maintenance": ["system_bot"],
    "maintenance_dev_bot": ["system_bot"],
    "marketing_manager": ["sales_bot"],
    "marketing_manager_bot": ["sales_bot"],
    "marketing_bot": ["sales_bot"],
    "mapleload_bot": ["freight_bot"],
    "mapleload_canada": ["freight_bot", "mapleload_bot"],
    "operations_bot": ["general_manager"],
    "operations_manager_bot": ["general_manager"],
    "partner_bot": ["operations_bot"],
    "safety_bot": ["operations_bot"],
    "sales_bot": ["operations_bot"],
    "security_bot": ["system_bot"],
    "security_manager": ["system_bot"],
    "security_manager_bot": ["system_bot"],
    "system_bot": ["operations_bot"],
    "system_manager": ["operations_bot"],
    "system_manager_bot": ["operations_bot"],
    "system_admin": ["operations_bot"],
    "trainer_bot": ["general_manager"],
    "trainer": ["general_manager"],
    "training_bot": ["general_manager"],
    "ai_dispatcher": ["operations_bot"],
}


def get_bot_policy(bot_key: str) -> Optional[BotPolicySpec]:
    return BOT_POLICIES.get(bot_key)


def get_bot_capabilities(bot_key: str) -> Optional[Dict[str, Any]]:
    return BOT_CAPABILITIES.get(bot_key)


def can_user_access_bot(user_role: str, user_features: Set[str], bot_key: str) -> bool:
    policy = get_bot_policy(bot_key)
    if not policy:
        return False
    if policy.hidden:
        return False
    if user_role not in policy.visible_to_roles:
        return False
    if not policy.required_features.issubset(user_features):
        return False
    return True


def get_accessible_bots(user_role: str, user_features: Set[str]) -> List[str]:
    return [k for k in BOT_POLICIES if can_user_access_bot(user_role, user_features, k)]


def validate_report_flow(sender: str, receiver: str) -> bool:
    return sender in VALID_REPORT_FLOWS and receiver in VALID_REPORT_FLOWS[sender]


def get_bot_layer(bot_key: str) -> Optional[str]:
    return BOT_LAYERS.get(bot_key)


def list_bot_layers() -> Dict[str, str]:
    return dict(BOT_LAYERS)
