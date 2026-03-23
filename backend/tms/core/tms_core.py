from __future__ import annotations

"""
TMS Core orchestrator that reuses existing BOS bot execution.
Includes subscription management, permissions, and shipment lifecycle.
"""

import asyncio
from typing import Any, Dict, Optional
from enum import Enum
from datetime import datetime
import logging

from fastapi import Depends, HTTPException

logger = logging.getLogger(__name__)

try:
    from backend.bots.os import BotOS
except Exception:
    BotOS = None  # type: ignore


class SubscriptionTier(str, Enum):
    """Subscription tier levels"""
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class PermissionLevel(str, Enum):
    """Permission access levels"""
    VIEW_ONLY = "view_only"
    QUICK_RUN = "quick_run"
    CONTROL_PANEL = "control_panel"
    CONFIGURE = "configure"


class SubscriptionPlans:
    """Configuration for the three subscription plans"""
    
    PLANS = {
        SubscriptionTier.STARTER: {
            "name": "Starter",
            "price": 99,
            "currency": "USD",
            "max_shipments_per_month": 100,
            "max_team_members": 3,
            "bots": {
                "customer_service": PermissionLevel.QUICK_RUN,
                "documents_manager": PermissionLevel.QUICK_RUN,
                "freight_broker": PermissionLevel.QUICK_RUN,
            },
            "features": {
                "basic_tracking": True,
                "email_notifications": True,
                "api_access": False,
                "custom_reports": False,
                "webhooks": False,
                "sso": False,
            }
        },
        SubscriptionTier.PROFESSIONAL: {
            "name": "Professional",
            "price": 299,
            "currency": "USD",
            "max_shipments_per_month": 1000,
            "max_team_members": 10,
            "bots": {
                "customer_service": PermissionLevel.CONTROL_PANEL,
                "documents_manager": PermissionLevel.CONTROL_PANEL,
                "freight_broker": PermissionLevel.CONTROL_PANEL,
                "finance_bot": PermissionLevel.CONTROL_PANEL,
                "sales_team": PermissionLevel.CONTROL_PANEL,
            },
            "features": {
                "basic_tracking": True,
                "email_notifications": True,
                "api_access": True,
                "custom_reports": True,
                "webhooks": True,
                "sso": False,
            }
        },
        SubscriptionTier.ENTERPRISE: {
            "name": "Enterprise",
            "price": 799,
            "currency": "USD",
            "max_shipments_per_month": -1,  # unlimited
            "max_team_members": -1,  # unlimited
            "bots": {
                "customer_service": PermissionLevel.CONFIGURE,
                "documents_manager": PermissionLevel.CONFIGURE,
                "freight_broker": PermissionLevel.CONFIGURE,
                "finance_bot": PermissionLevel.CONFIGURE,
                "sales_team": PermissionLevel.CONFIGURE,
                "general_manager": PermissionLevel.CONFIGURE,
                "maintenance_bot": PermissionLevel.CONFIGURE,
            },
            "features": {
                "basic_tracking": True,
                "email_notifications": True,
                "api_access": True,
                "custom_reports": True,
                "webhooks": True,
                "sso": True,
                "dedicated_support": True,
                "custom_integrations": True,
            }
        }
    }


class TMSCore:
    def __init__(self) -> None:
        self._initialized = False
        self.subscription_plans = SubscriptionPlans.PLANS

    async def initialize(self) -> None:
        # Future: load TMS-specific configs if needed
        self._initialized = True

    async def ensure_ready(self) -> None:
        if not self._initialized:
            await self.initialize()

    async def check_bot_access(
        self,
        company_id: str,
        bot_key: str,
        required_action: str
    ) -> bool:
        """
        Check company's permission to access a specific bot
        
        Args:
            company_id: Company identifier
            bot_key: Bot key (customer_service, documents_manager, etc.)
            required_action: Required action
        
        Returns:
            True if permission exists
        """
        logger.info(f"Checking permission: {company_id} -> {bot_key}")
        
        # Note: Subscription data is fetched from database in production
        # Returning True as placeholder here
        return True

    def get_subscription_details(self, tier: SubscriptionTier) -> Dict:
        """Get subscription plan details"""
        return self.subscription_plans.get(tier, {})

    async def execute(self, bot_name: str, action: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        await self.ensure_ready()
        payload = payload or {}

        if BotOS is None:
            raise HTTPException(status_code=503, detail={"error": "bos_unavailable", "message": "BotOS not available"})

        bos = BotOS.get_instance()
        if bos is None:
            raise HTTPException(status_code=503, detail={"error": "bos_uninitialized", "message": "BotOS not initialized"})

        task_payload = {"action": action, **payload}
        try:
            result = await bos.execute_bot(bot_name, task_payload)
            return {"ok": True, "bot": bot_name, "action": action, "result": result}
        except Exception as e:
            raise HTTPException(status_code=500, detail={"error": "tms_execute_failed", "message": str(e)})


tms_core = TMSCore()
