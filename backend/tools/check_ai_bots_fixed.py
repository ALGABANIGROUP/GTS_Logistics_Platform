# backend/core/ai_core.py
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod

class AIBotBase(ABC):
    """Base class for all AI bots"""

    def __init__(self):
        self.name = self.__class__.__name__
        self.version = "1.0"
        self.description = "AI Bot Base Class"

    @abstractmethod
    async def process_message(self, message: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Process a message and return response"""
        pass

    @abstractmethod
    async def get_capabilities(self) -> Dict[str, Any]:
        """Get bot capabilities"""
        pass

class GeneralManagerBot(AIBotBase):
    """General Manager AI Bot"""

    def __init__(self):
        super().__init__()
        self.name = "GeneralManagerBot"
        self.description = "Handles overall business management and strategy"
        self.version = "1.2"

    async def process_message(self, message: str, context: Dict[str, Any] = None) -> str:
        return f"GeneralManagerBot: I'll help with business strategy. You said: {message}"

    async def get_capabilities(self) -> Dict[str, Any]:
        return {
            "role": "General Management",
            "skills": ["strategy", "planning", "coordination"],
            "department": "Executive"
        }

class FreightBrokerBot(AIBotBase):
    """Freight Broker AI Bot"""

    def __init__(self):
        super().__init__()
        self.name = "FreightBrokerBot"
        self.description = "Manages freight brokerage and logistics coordination"
        self.version = "1.3"

    async def process_message(self, message: str, context: Dict[str, Any] = None) -> str:
        return f"FreightBrokerBot: I'll handle freight brokerage. You said: {message}"

    async def get_capabilities(self) -> Dict[str, Any]:
        return {
            "role": "Freight Brokerage",
            "skills": ["load matching", "carrier management", "rate negotiation"],
            "department": "Operations"
        }

class OperationsManagerBot(AIBotBase):
    """Operations Manager AI Bot"""

    def __init__(self):
        super().__init__()
        self.name = "OperationsManagerBot"
        self.description = "Manages daily operations and workflow"
        self.version = "1.1"

    async def process_message(self, message: str, context: Dict[str, Any] = None) -> str:
        return f"OperationsManagerBot: I'll manage operations. You said: {message}"

    async def get_capabilities(self) -> Dict[str, Any]:
        return {
            "role": "Operations Management",
            "skills": ["workflow", "scheduling", "coordination"],
            "department": "Operations"
        }

class FinanceBot(AIBotBase):
    """Finance AI Bot"""

    def __init__(self):
        super().__init__()
        self.name = "FinanceBot"
        self.description = "Handles financial operations and reporting"
        self.version = "1.4"

    async def process_message(self, message: str, context: Dict[str, Any] = None) -> str:
        return f"FinanceBot: I'll assist with finance. You said: {message}"

    async def get_capabilities(self) -> Dict[str, Any]:
        return {
            "role": "Financial Management",
            "skills": ["accounting", "reporting", "analysis"],
            "department": "Finance"
        }

class DocumentsManagerBot(AIBotBase):
    """Documents Manager AI Bot"""

    def __init__(self):
        super().__init__()
        self.name = "DocumentsManagerBot"
        self.description = "Manages documents and compliance"
        self.version = "1.2"

    async def process_message(self, message: str, context: Dict[str, Any] = None) -> str:
        return f"DocumentsManagerBot: I'll handle documents. You said: {message}"

    async def get_capabilities(self) -> Dict[str, Any]:
        return {
            "role": "Document Management",
            "skills": ["document processing", "compliance", "organization"],
            "department": "Administration"
        }

class AIMaintenanceDevBot(AIBotBase):
    """AI Maintenance and Development Bot"""

    def __init__(self):
        super().__init__()
        self.name = "AIMaintenanceDevBot"
        self.description = "Handles system maintenance and AI development"
        self.version = "1.3"

    async def process_message(self, message: str, context: Dict[str, Any] = None) -> str:
        return f"AIMaintenanceDevBot: I'll handle system maintenance. You said: {message}"

    async def get_capabilities(self) -> Dict[str, Any]:
        return {
            "role": "System Maintenance & Development",
            "skills": ["monitoring", "optimization", "development"],
            "department": "IT"
        }

class AIBotManager:
    """Manager for all AI bots"""

    def __init__(self):
        self.registered_bots: Dict[str, AIBotBase] = {}
        self.register_bots()

    def register_bots(self):
        """Register all AI bots"""
        bots = [
            GeneralManagerBot(),
            FreightBrokerBot(),
            OperationsManagerBot(),
            FinanceBot(),
            DocumentsManagerBot(),
            AIMaintenanceDevBot()
        ]

        for bot in bots:
            # Use name without "Bot" as identifier
            bot_id = bot.name.lower().replace('bot', '')
            self.registered_bots[bot_id] = bot

        print(f"[startup] AI core bots registered: {list(self.registered_bots.keys())}")

    def get_bot(self, bot_id: str) -> Optional[AIBotBase]:
        """Get a bot by ID"""
        return self.registered_bots.get(bot_id)

    async def process_with_bot(self, bot_id: str, message: str, context: Dict[str, Any] = None) -> str:
        """Process message with specific bot"""
        bot = self.get_bot(bot_id)
        if bot:
            return await bot.process_message(message, context)
        return f"Bot {bot_id} not found"

    def list_bots(self) -> Dict[str, Any]:
        """List all available bots"""
        return {
            "total_bots": len(self.registered_bots),
            "bots": {bot_id: {
                "name": bot.name,
                "description": bot.description,
                "version": bot.version
            } for bot_id, bot in self.registered_bots.items()}
        }

# Create global instance
bot_manager = AIBotManager()

# Export for easy access
__all__ = [
    'AIBotBase',
    'GeneralManagerBot',
    'FreightBrokerBot',
    'OperationsManagerBot',
    'FinanceBot',
    'DocumentsManagerBot',
    'AIMaintenanceDevBot',
    'AIBotManager',
    'bot_manager'
]