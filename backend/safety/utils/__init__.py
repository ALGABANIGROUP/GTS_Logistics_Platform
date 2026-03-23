"""
Utilities - Safety
Utility Functions
"""

import logging

logger = logging.getLogger(__name__)


def generate_report_id():
    """Generate a unique report identifier."""
    from datetime import datetime
    return f"RPT_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"


def format_alert_message(alert_type: str, severity: str, title: str) -> str:
    """Format a standardized alert message with severity icon."""
    severity_icons = {
        "critical": "🔴",
        "high": "🟠",
        "medium": "🟡",
        "low": "🟢",
    }
    icon = severity_icons.get(severity, "ℹ️")
    return f"{icon} [{alert_type.upper()}] {title}"


def calculate_risk_score(factors: dict) -> float:
    """Calculate weighted risk score from normalized factors."""
    weights = {
        "probability": 0.4,
        "severity": 0.4,
        "frequency": 0.2,
    }

    score = 0.0
    for factor, weight in weights.items():
        if factor in factors:
            score += factors[factor] * weight

    return min(score, 100.0)
