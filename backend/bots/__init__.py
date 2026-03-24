"""
GTS Logistics AI Bots Package - Complete Registration
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# Core bots
from .general_manager import GeneralManagerBot
from .freight_broker import FreightBrokerBot
from .operations_manager import OperationsManagerBot
from .information_coordinator import InformationCoordinatorBot
from .legal_bot import LegalBot
from .security_bot import SecurityBot
from .system_manager import SystemManagerBot
from .maintenance_dev import MaintenanceDevBot
from .sales_intelligence import SalesIntelligenceBot
from .marketing_manager import MarketingManagerBot
from .intelligence_bot import IntelligenceBot
from .trainer_bot import TrainerBotRuntime
from .safety_bot import SafetyBot
from .ai_dispatcher import AIDispatcherBot
from .mapleload_canada import MapleLoadCanadaBot
from .customer_service import CustomerServiceBot

# Advanced bots
try:
    from .documents_manager import DocumentsManagerBot
except ImportError:
    DocumentsManagerBot = None
    logger.debug("DocumentsManagerBot not available")

try:
    from .executive_intelligence import ExecutiveIntelligenceBot
except ImportError:
    ExecutiveIntelligenceBot = None
    logger.debug("ExecutiveIntelligenceBot not available")

try:
    from .finance_intelligence import FinanceIntelligenceBot
except ImportError:
    FinanceIntelligenceBot = None
    logger.debug("FinanceIntelligenceBot not available")

try:
    from .partner_management import PartnerManagementBot
except ImportError:
    PartnerManagementBot = None
    logger.debug("PartnerManagementBot not available")

try:
    from .system_intelligence import SystemIntelligenceBot
except ImportError:
    SystemIntelligenceBot = None
    logger.debug("SystemIntelligenceBot not available")

# List of all available bots
__all__ = [
    "GeneralManagerBot",
    "FreightBrokerBot",
    "OperationsManagerBot",
    "InformationCoordinatorBot",
    "LegalBot",
    "SecurityBot",
    "SystemManagerBot",
    "MaintenanceDevBot",
    "SalesIntelligenceBot",
    "MarketingManagerBot",
    "IntelligenceBot",
    "TrainerBotRuntime",
    "SafetyBot",
    "AIDispatcherBot",
    "MapleLoadCanadaBot",
    "CustomerServiceBot",
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


def register_all_bots(ai_registry):
    """Register all available bots to the AI registry"""
    registered_count = 0
    failed_count = 0
    
    for bot_name, bot_class in BOTS_REGISTRY.items():
        try:
            if bot_class is not None:
                bot_instance = bot_class()
                # Set bot name if not already set
                if not hasattr(bot_instance, 'name'):
                    bot_instance.name = bot_name
                if not hasattr(bot_instance, 'display_name'):
                    bot_instance.display_name = bot_name.replace('_', ' ').title()
                
                ai_registry.register(bot_instance)
                registered_count += 1
                logger.info(f"Bot registered: {bot_name}")
            else:
                logger.warning(f"Bot {bot_name} is None, skipping")
                failed_count += 1
        except Exception as e:
            logger.error(f"Failed to register bot {bot_name}: {e}")
            failed_count += 1
    
    logger.info(f"Bot registration complete: {registered_count} registered, {failed_count} failed")
    return {"registered": registered_count, "failed": failed_count}


def get_bot_instance(bot_name: str) -> Optional[Any]:
    """Get a bot instance by name"""
    bot_class = BOTS_REGISTRY.get(bot_name)
    if bot_class:
        try:
            return bot_class()
        except Exception as e:
            logger.error(f"Failed to create bot instance {bot_name}: {e}")
    return None


def get_all_bots() -> Dict[str, str]:
    """Get all available bot names and display names"""
    return {
        name: getattr(bot_class, 'display_name', name.replace('_', ' ').title())
        for name, bot_class in BOTS_REGISTRY.items()
        if bot_class is not None
    }