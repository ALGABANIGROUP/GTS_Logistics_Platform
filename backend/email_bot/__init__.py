"""Email intelligence package for routing and processing inbound mail."""

from .intelligent_processor import IntelligentEmailProcessor
from .intelligent_router import IntelligentEmailRouter
from .monitoring import EmailBotMonitor
from .rules import PRIORITY_RULES, AUTO_RESPONSE_RULES

__all__ = [
    "IntelligentEmailProcessor",
    "IntelligentEmailRouter",
    "EmailBotMonitor",
    "PRIORITY_RULES",
    "AUTO_RESPONSE_RULES",
]
