from __future__ import annotations
# backend/bots/base_bot.py
"""
Base Bot class for GTS Logistics Platform bots
"""
import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)

class BaseBot:
    """Base class for all AI bots in the platform"""

    def __init__(self, name: str, description: str, version: str = "1.0.0", mode: str = "active"):
        self.name = name
        self.display_name = name.replace("_", " ").replace("-", " ").title()
        self.description = description
        self.version = version
        self.mode = mode
        self.is_active = True

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input data - to be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement process method")

    async def get_status(self) -> Dict[str, Any]:
        """Get bot status"""
        return {
            "name": self.name,
            "display_name": self.display_name,
            "description": self.description,
            "version": self.version,
            "mode": self.mode,
            "is_active": self.is_active
        }
