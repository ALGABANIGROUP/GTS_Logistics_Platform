from __future__ import annotations

from typing import Any

from backend.routes.bots_available_enhanced import ALL_BOTS
from backend.training_center.core.models import BotSpecialization


class BotConnector:
    """Resolve known bots from the platform catalog."""

    def __init__(self) -> None:
        self.catalog = {bot["id"]: bot for bot in ALL_BOTS}
        self.catalog.update(self._supplemental_catalog())
        self.aliases = {
            "customer_service": "customer_service",
            "customer_service_bot": "customer_service",
            "documents_manager": "documents_manager",
            "general_manager": "general_manager",
            "information_coordinator": "information_coordinator",
            "intelligence_bot": "intelligence_bot",
            "legal_bot": "legal_bot",
            "legal_consultant": "legal_bot",
            "maintenance_dev": "maintenance_dev",
            "mapleload_bot": "mapleload_bot",
            "mapleload_canada": "mapleload_bot",
            "operations_manager": "operations_manager_bot",
            "operations_manager_bot": "operations_manager_bot",
            "security_manager": "security_manager_bot",
            "security_manager_bot": "security_manager_bot",
            "safety_manager": "safety_manager_bot",
            "safety_manager_bot": "safety_manager_bot",
            "sales_team": "sales_bot",
            "sales_bot": "sales_bot",
            "system_admin": "system_manager_bot",
            "system_manager": "system_manager_bot",
            "system_manager_bot": "system_manager_bot",
            "finance_bot": "finance_bot",
            "freight_broker": "freight_broker",
            "ai_dispatcher": "ai_dispatcher",
            "trainer": "trainer_bot",
            "training_bot": "trainer_bot",
            "trainer_bot": "trainer_bot",
        }

    def _supplemental_catalog(self) -> dict[str, dict[str, Any]]:
        return {
            "security_manager_bot": {
                "id": "security_manager_bot",
                "name": "AI Security Manager",
                "description": "Security monitoring and threat response.",
                "icon": "SEC",
                "path": "/ai-bots/control?bot=security_manager_bot",
                "category": "Security",
                "enabled": True,
                "subscription_required": "enterprise",
            }
        }

    def normalize_bot_key(self, bot_key: str) -> str:
        normalized = str(bot_key or "").strip().lower().replace("-", "_").replace(" ", "_")
        return self.aliases.get(normalized, normalized)

    def list_trainable_bots(self) -> list[dict[str, Any]]:
        return [{**bot, "specialization": self.infer_specialization(bot).value} for bot in ALL_BOTS]

    def get_bot(self, bot_key: str) -> dict[str, Any] | None:
        canonical = self.normalize_bot_key(bot_key)
        bot = self.catalog.get(canonical)
        if not bot:
            return None
        return {**bot, "canonical_key": canonical, "specialization": self.infer_specialization(bot)}

    def infer_specialization(self, bot: dict[str, Any]) -> BotSpecialization:
        bot_id = bot["id"]
        category = str(bot.get("category", "")).lower()
        if "security" in bot_id:
            return BotSpecialization.SECURITY
        if bot_id in {"freight_broker", "ai_dispatcher", "mapleload_bot"}:
            return BotSpecialization.LOGISTICS
        if bot_id == "customer_service":
            return BotSpecialization.CUSTOMER_SERVICE
        if bot_id in {"operations_manager_bot", "safety_manager_bot"}:
            return BotSpecialization.OPERATIONS
        if bot_id == "finance_bot":
            return BotSpecialization.FINANCE
        if bot_id == "legal_bot":
            return BotSpecialization.LEGAL
        if bot_id == "sales_bot":
            return BotSpecialization.SALES
        if bot_id == "general_manager":
            return BotSpecialization.MANAGEMENT
        if bot_id in {"system_manager_bot", "maintenance_dev"}:
            return BotSpecialization.SYSTEM
        if bot_id == "trainer_bot":
            return BotSpecialization.TRAINING
        if category == "operations":
            return BotSpecialization.OPERATIONS
        return BotSpecialization.GENERAL
