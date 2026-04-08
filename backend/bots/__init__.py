from __future__ import annotations
# backend/bots/__init__.py
"""
Bots module for GTS Logistics Platform
"""
import logging

from .base_bot import BaseBot
from .general_manager import GeneralManagerBot
from .freight_broker import FreightBrokerBot
from .operations_manager import OperationsManagerBot

logger = logging.getLogger(__name__)

__all__ = [
    'BaseBot',
    'GeneralManagerBot',
    'FreightBrokerBot',
    'OperationsManagerBot'
]
from .general_manager import GeneralManagerBot
from .freight_broker import FreightBrokerBot
from .operations_manager import OperationsManagerBot
from .information_coordinator import InformationCoordinatorBot
from .legal_bot import LegalBot
from .security_bot import SecurityBot
from .system_manager import SystemManagerBot
from .system_admin import SystemAdminBot
from .maintenance_dev import MaintenanceDevBot
from .sales_intelligence import SalesIntelligenceBot
from .marketing_manager import MarketingManagerBot
from .intelligence_bot import IntelligenceBot
from .trainer_bot import TrainerBotRuntime
from .safety_bot import SafetyBot
from .ai_dispatcher import AIDispatcherBot
from .mapleload_canada import MapleLoadCanadaBot
from .customer_service import CustomerServiceBot
from .os import get_bot_os, init_bot_os

# Advanced bots
try:
    from .documents_manager import DocumentsManagerBot
except ImportError:
    DocumentsManagerBot = None

try:
    from .executive_intelligence import ExecutiveIntelligenceBot
except ImportError:
    ExecutiveIntelligenceBot = None

try:
    from .finance_intelligence import FinanceIntelligenceBot
except ImportError:
    FinanceIntelligenceBot = None

try:
    from .partner_management import PartnerManagementBot
except ImportError:
    PartnerManagementBot = None

try:
    from .system_intelligence import SystemIntelligenceBot
except ImportError:
    SystemIntelligenceBot = None

# List of all available bots
__all__ = [
    "GeneralManagerBot",
    "FreightBrokerBot",
    "OperationsManagerBot",
    "InformationCoordinatorBot",
    "LegalBot",
    "SecurityBot",
    "SystemManagerBot",
    "SystemAdminBot",
    "MaintenanceDevBot",
    "SalesIntelligenceBot",
    "MarketingManagerBot",
    "IntelligenceBot",
    "TrainerBotRuntime",
    "SafetyBot",
    "AIDispatcherBot",
    "MapleLoadCanadaBot",
    "CustomerServiceBot",
    "get_bot_os",
    "init_bot_os",
]

# Add advanced bots if available
if DocumentsManagerBot:
    __all__.append("DocumentsManagerBot")
if ExecutiveIntelligenceBot:
    __all__.append("ExecutiveIntelligenceBot")
if FinanceIntelligenceBot:
    __all__.append("FinanceIntelligenceBot")
if PartnerManagementBot:
    __all__.append("PartnerManagementBot")
if SystemIntelligenceBot:
    __all__.append("SystemIntelligenceBot")

# Bots registry dictionary
BOTS_REGISTRY = {
    "general_manager": GeneralManagerBot,
    "freight_broker": FreightBrokerBot,
    "operations_manager": OperationsManagerBot,
    "information_coordinator": InformationCoordinatorBot,
    "legal_consultant": LegalBot,
    "security_manager": SecurityBot,
    "system_manager": SystemManagerBot,
    "system_admin": SystemAdminBot,
    "maintenance_dev": MaintenanceDevBot,
    "sales_intelligence": SalesIntelligenceBot,
    "marketing_manager": MarketingManagerBot,
    "intelligence_bot": IntelligenceBot,
    "trainer_bot": TrainerBotRuntime,
    "safety_manager": SafetyBot,
    "ai_dispatcher": AIDispatcherBot,
    "mapleload_canada": MapleLoadCanadaBot,
    "customer_service": CustomerServiceBot,
}

# Add advanced bots to registry
if DocumentsManagerBot:
    BOTS_REGISTRY["documents_manager"] = DocumentsManagerBot
if ExecutiveIntelligenceBot:
    BOTS_REGISTRY["executive_intelligence"] = ExecutiveIntelligenceBot
if FinanceIntelligenceBot:
    BOTS_REGISTRY["finance_intelligence"] = FinanceIntelligenceBot
if PartnerManagementBot:
    BOTS_REGISTRY["partner_management"] = PartnerManagementBot
if SystemIntelligenceBot:
    BOTS_REGISTRY["system_intelligence"] = SystemIntelligenceBot

# Add active bot tracking
ACTIVE_BOTS = []
INACTIVE_BOTS = []

def set_bot_status(bot_name: str, is_active: bool):
    """Set bot active/inactive status"""
    if is_active:
        if bot_name in INACTIVE_BOTS:
            INACTIVE_BOTS.remove(bot_name)
        if bot_name not in ACTIVE_BOTS:
            ACTIVE_BOTS.append(bot_name)
    else:
        if bot_name in ACTIVE_BOTS:
            ACTIVE_BOTS.remove(bot_name)
        if bot_name not in INACTIVE_BOTS:
            INACTIVE_BOTS.append(bot_name)

def is_bot_active(bot_name: str) -> bool:
    """Check if bot is active"""
    return bot_name in ACTIVE_BOTS

def get_active_bots() -> List[str]:
    """Get list of active bot names"""
    return ACTIVE_BOTS.copy()

def get_inactive_bots() -> List[str]:
    """Get list of inactive bot names"""
    return INACTIVE_BOTS.copy()

def activate_all_bots():
    """Activate all registered bots"""
    global ACTIVE_BOTS, INACTIVE_BOTS
    ACTIVE_BOTS = list(BOTS_REGISTRY.keys())
    INACTIVE_BOTS = []
    logger.info(f"Activated {len(ACTIVE_BOTS)} bots")

# Call this on startup
activate_all_bots()

