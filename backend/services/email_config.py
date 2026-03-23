from __future__ import annotations

import os

PRIMARY_DOMAIN = "gabanilogistics.com"
SECURITY_DOMAIN = "gabanistore.com"

BOT_CODE_ALIASES = {
    "maintenance_bot": "maintenance_dev",
    "safety_manager": "safety",
    "security_manager": "security",
}

EMAIL_DISABLED_BOTS = {
    "general_manager",
    "information_coordinator",
    "maintenance_dev",
    "maintenance_bot",
    "legal_consultant",
}

BOT_EMAIL_MAP = {
    "platform_expenses": f"accounts@{PRIMARY_DOMAIN}",
    "finance_bot": f"finance@{PRIMARY_DOMAIN}",
    "freight_broker": f"freight@{PRIMARY_DOMAIN}",
    "documents_manager": f"doccontrol@{PRIMARY_DOMAIN}",
    "customer_service": f"customers@{PRIMARY_DOMAIN}",
    "strategy_advisor": f"marketing@{PRIMARY_DOMAIN}",
    "partner_manager": f"investments@{PRIMARY_DOMAIN}",
    "operations_manager": f"operations@{PRIMARY_DOMAIN}",
    "safety_manager": f"safety@{PRIMARY_DOMAIN}",
    "security_manager": f"security@{SECURITY_DOMAIN}",
}

SYSTEM_ADMIN_EMAIL = f"admin@{PRIMARY_DOMAIN}"
NO_REPLY_EMAIL = (
    os.getenv("MAIL_FROM")
    or os.getenv("SMTP_FROM")
    or "no-reply@gabanilogistics.com"
)
