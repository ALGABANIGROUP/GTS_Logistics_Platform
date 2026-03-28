from __future__ import annotations

RACI_MATRIX: dict[str, dict[str, str]] = {
    "daily_operations_report": {
        "operations_manager": "R",
        "general_manager": "A",
        "system_admin": "C",
        "finance_bot": "I",
        "freight_broker": "I",
    },
    "strategic_report": {
        "general_manager": "R/A",
        "operations_manager": "C",
        "intelligence_bot": "I",
    },
    "financial_report": {
        "finance_bot": "R",
        "general_manager": "A",
        "operations_manager": "C",
        "system_admin": "I",
    },
    "security_audit_report": {
        "security_manager": "R",
        "system_admin": "A",
        "general_manager": "I",
    },
}


def get_report_role(report_type: str, bot_name: str) -> str | None:
    matrix = RACI_MATRIX.get(str(report_type or "").strip().lower(), {})
    return matrix.get(str(bot_name or "").strip().lower())


def can_send_report(report_type: str, bot_name: str) -> bool:
    return get_report_role(report_type, bot_name) in {"R", "R/A"}


def requires_approval(report_type: str, bot_name: str) -> bool:
    return get_report_role(report_type, bot_name) not in {"A", "R/A"}
