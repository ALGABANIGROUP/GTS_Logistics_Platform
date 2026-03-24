"""
GTS Logistics AI Bots Package
"""

# البوتات الأساسية
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

# البوتات المطورة
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

# قائمة جميع البوتات المتاحة
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

# إضافة البوتات المطورة إذا كانت متوفرة
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

# قاموس البوتات للتسجيل
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

# إضافة البوتات المطورة للقاموس
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
