"""
TMS Permissions System - Permission Checking & Hierarchy
Handles permission validation and level comparison
"""

import logging
from enum import Enum
from typing import Optional, Dict, List
from backend.tms.core.tms_core import PermissionLevel, SubscriptionTier, SubscriptionPlans

logger = logging.getLogger(__name__)


class BotPermissionChecker:
    """Bot permission verification system"""
    
    # Hierarchy: higher number = more permissions
    PERMISSION_HIERARCHY = {
        PermissionLevel.VIEW_ONLY: 1,
        PermissionLevel.QUICK_RUN: 2,
        PermissionLevel.CONTROL_PANEL: 3,
        PermissionLevel.CONFIGURE: 4
    }
    
    @classmethod
    def has_permission(cls, user_level: PermissionLevel, required_level: PermissionLevel) -> bool:
        """
        Check if user has required permission level
        
        Args:
            user_level: User's current permission level
            required_level: Required permission level for action
            
        Returns:
            True if user has sufficient permissions
        """
        user_rank = cls.PERMISSION_HIERARCHY.get(user_level, 0)
        required_rank = cls.PERMISSION_HIERARCHY.get(required_level, 999)
        
        return user_rank >= required_rank
    
    @classmethod
    def get_bot_permission(cls, subscription_tier: SubscriptionTier, bot_key: str) -> Optional[PermissionLevel]:
        """
        Get permission level for a bot in a subscription plan
        
        Args:
            subscription_tier: User's subscription plan
            bot_key: Bot identifier (e.g., 'freight_broker')
            
        Returns:
            PermissionLevel or None if bot not available
        """
        plan_config = SubscriptionPlans.PLANS.get(subscription_tier)
        
        if not plan_config:
            return None
        
        bots = plan_config.get("bots", {})
        return bots.get(bot_key)
    
    @classmethod
    def check_bot_access(
        cls, 
        subscription_tier: SubscriptionTier, 
        bot_key: str, 
        required_permission: PermissionLevel
    ) -> bool:
        """
        Check if subscription tier has required permission for bot
        
        Args:
            subscription_tier: User's subscription plan
            bot_key: Bot identifier
            required_permission: Required permission level
            
        Returns:
            True if access is granted
        """
        user_permission = cls.get_bot_permission(subscription_tier, bot_key)
        
        if user_permission is None:
            logger.warning(f"Bot '{bot_key}' not available in {subscription_tier} plan")
            return False
        
        has_access = cls.has_permission(user_permission, required_permission)
        
        if not has_access:
            logger.info(
                f"Permission denied: {subscription_tier} plan has {user_permission} "
                f"for bot '{bot_key}', but {required_permission} is required"
            )
        
        return has_access
    
    @classmethod
    def get_available_bots(cls, subscription_tier: SubscriptionTier) -> List[Dict]:
        """
        Get list of all bots available in subscription plan
        
        Args:
            subscription_tier: User's subscription plan
            
        Returns:
            List of dicts with bot info and permissions
        """
        plan_config = SubscriptionPlans.PLANS.get(subscription_tier)
        
        if not plan_config:
            return []
        
        bots = plan_config.get("bots", {})
        bot_list = []
        
        for bot_key, permission_level in bots.items():
            bot_list.append({
                "bot_key": bot_key,
                "bot_name": cls._get_bot_display_name(bot_key),
                "permission_level": permission_level.value,
                "capabilities": cls._get_capabilities_for_level(permission_level)
            })
        
        return bot_list
    
    @classmethod
    def _get_bot_display_name(cls, bot_key: str) -> str:
        """Get human-readable bot name"""
        bot_names = {
            "customer_service": "Customer Service Bot",
            "documents_manager": "Documents Manager",
            "freight_broker": "Freight Broker Bot",
            "finance_bot": "Finance Bot",
            "sales_team": "Sales Team Bot",
            "general_manager": "General Manager Bot",
            "maintenance_bot": "Maintenance Bot"
        }
        return bot_names.get(bot_key, bot_key.replace("_", " ").title())
    
    @classmethod
    def _get_capabilities_for_level(cls, level: PermissionLevel) -> List[str]:
        """Get list of capabilities for permission level"""
        capabilities = {
            PermissionLevel.VIEW_ONLY: [
                "View dashboards",
                "View reports",
                "Read-only access"
            ],
            PermissionLevel.QUICK_RUN: [
                "View dashboards",
                "View reports",
                "Run pre-defined templates",
                "Execute quick actions"
            ],
            PermissionLevel.CONTROL_PANEL: [
                "View dashboards",
                "View reports",
                "Run templates",
                "Full bot control",
                "Custom workflows",
                "Manual operations"
            ],
            PermissionLevel.CONFIGURE: [
                "All Control Panel features",
                "API integrations",
                "Custom configurations",
                "Webhooks setup",
                "Automation rules",
                "Advanced settings"
            ]
        }
        return capabilities.get(level, [])
    
    @classmethod
    def get_upgrade_recommendation(cls, current_tier: SubscriptionTier, bot_key: str) -> Optional[Dict]:
        """
        Get recommendation for upgrading to access more bot features
        
        Args:
            current_tier: Current subscription tier
            bot_key: Bot they want more access to
            
        Returns:
            Dict with upgrade info or None
        """
        current_permission = cls.get_bot_permission(current_tier, bot_key)
        
        if current_permission == PermissionLevel.CONFIGURE:
            return None  # Already at max level
        
        # Find next tier with higher permission
        tier_order = [SubscriptionTier.STARTER, SubscriptionTier.PROFESSIONAL, SubscriptionTier.ENTERPRISE]
        current_index = tier_order.index(current_tier)
        
        for next_tier in tier_order[current_index + 1:]:
            next_permission = cls.get_bot_permission(next_tier, bot_key)
            
            if next_permission and current_permission and cls.has_permission(next_permission, current_permission):
                if next_permission != current_permission:
                    plan_config = SubscriptionPlans.PLANS[next_tier]
                    return {
                        "recommended_tier": next_tier.value,
                        "recommended_plan_name": plan_config["name"],
                        "current_permission": current_permission.value if current_permission else "unknown",
                        "upgraded_permission": next_permission.value,
                        "price": plan_config["price"],
                        "additional_features": cls._get_capabilities_for_level(next_permission)
                    }
        
        return None


class UsageAnalytics:
    """Usage analytics helper for subscription and upgrade recommendations."""
    
    @staticmethod
    async def analyze_company_usage(company_id: str) -> Dict:
        """
        Analyze company usage patterns
        
        Args:
            company_id: Company UUID
            
        Returns:
            Dict with usage stats and recommendations
        """
        # This would query actual database
        # Placeholder implementation
        return {
            "monthly_shipments": 0,
            "active_users": 0,
            "bot_usage_frequency": {},
            "needs_upgrade": False,
            "upgrade_reason": None,
            "recommended_plan": None
        }
    
    @staticmethod
    def check_usage_limits(
        current_tier: SubscriptionTier,
        monthly_shipments: int,
        active_users: int
    ) -> Dict:
        """
        Check if company is near or exceeding plan limits
        
        Args:
            current_tier: Current subscription plan
            monthly_shipments: Number of shipments this month
            active_users: Number of active users
            
        Returns:
            Dict with limit status and warnings
        """
        plan_config = SubscriptionPlans.PLANS.get(current_tier)
        
        if not plan_config:
            return {"valid": False, "error": "Invalid plan"}
        
        max_shipments = plan_config["max_shipments_per_month"]
        max_users = plan_config["max_team_members"]
        
        # -1 means unlimited
        shipments_ok = max_shipments == -1 or monthly_shipments <= max_shipments
        users_ok = max_users == -1 or active_users <= max_users
        
        warnings = []
        
        if max_shipments != -1 and monthly_shipments > max_shipments * 0.8:
            warnings.append(f"Approaching shipment limit ({monthly_shipments}/{max_shipments})")
        
        if max_users != -1 and active_users >= max_users:
            warnings.append(f"At user limit ({active_users}/{max_users})")
        
        return {
            "valid": shipments_ok and users_ok,
            "shipments_ok": shipments_ok,
            "users_ok": users_ok,
            "warnings": warnings,
            "needs_upgrade": len(warnings) > 0,
            "monthly_shipments": monthly_shipments,
            "max_shipments": max_shipments,
            "active_users": active_users,
            "max_users": max_users
        }


# Decorator for permission checking
def require_bot_permission(bot_key: str, required_level: PermissionLevel):
    """
    Decorator to enforce bot permission requirements
    
    Usage:
        @require_bot_permission('freight_broker', PermissionLevel.CONTROL_PANEL)
        async def execute_broker_action():
            ...
    """
    def decorator(func):
        async def wrapper(*args, subscription_tier: SubscriptionTier | None = None, **kwargs):
            if not subscription_tier:
                raise ValueError("subscription_tier required")
            
            if not BotPermissionChecker.check_bot_access(subscription_tier, bot_key, required_level or PermissionLevel.VIEW_ONLY):
                raise PermissionError(
                    f"Insufficient permissions for {bot_key}. "
                    f"Required: {(required_level or PermissionLevel.VIEW_ONLY).value}, "
                    f"Available: {BotPermissionChecker.get_bot_permission(subscription_tier, bot_key)}"
                )
            
            return await func(*args, subscription_tier=subscription_tier, **kwargs)
        
        return wrapper
    return decorator
