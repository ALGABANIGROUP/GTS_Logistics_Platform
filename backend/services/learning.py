from __future__ import annotations

# backend/services/learning.py
# Alias for learning_bootstrap to maintain compatibility

from .learning_bootstrap import *
from backend.ai.learning_engine import bot_learning_engine
import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)

class LearningService:
    """Service for bot learning and training"""

    def __init__(self):
        self.engine = bot_learning_engine

    async def get_learning_stats(self) -> Dict[str, Any]:
        """Get learning statistics"""
        return self.engine.get_learning_stats()

    async def register_bot(self, **config) -> None:
        """Register a bot for learning"""
        self.engine.register_bot(**config)

    async def process_feedback(self, bot_id: str, feedback: Dict[str, Any]) -> None:
        """Process feedback for a bot"""
        # Implement feedback processing
        pass