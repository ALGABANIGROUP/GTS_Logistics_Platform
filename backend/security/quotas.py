"""
Tenant Quota System
Enforces per-tenant resource limits based on subscription plan
"""

import logging
from enum import Enum
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class QuotaType(str, Enum):
    """Types of quotas"""
    MAX_USERS = "max_users"
    MAX_TICKETS_PER_DAY = "max_tickets_per_day"
    MAX_SHIPMENTS_PER_DAY = "max_shipments_per_day"
    MAX_STORAGE_MB = "max_storage_mb"
    MAX_API_CALLS_PER_MINUTE = "max_api_calls_per_minute"
    ADVANCED_ANALYTICS = "advanced_analytics"
    CUSTOM_INTEGRATIONS = "custom_integrations"
    WEBHOOK_SUPPORT = "webhook_support"


# Default quotas per plan
DEFAULT_QUOTAS: Dict[str, Dict[str, any]] = {
    "free_trial": {
        QuotaType.MAX_USERS.value: 3,
        QuotaType.MAX_TICKETS_PER_DAY.value: 10,
        QuotaType.MAX_SHIPMENTS_PER_DAY.value: 5,
        QuotaType.MAX_STORAGE_MB.value: 100,
        QuotaType.MAX_API_CALLS_PER_MINUTE.value: 10,
        QuotaType.ADVANCED_ANALYTICS.value: False,
        QuotaType.CUSTOM_INTEGRATIONS.value: False,
        QuotaType.WEBHOOK_SUPPORT.value: False,
    },
    "basic": {
        QuotaType.MAX_USERS.value: 10,
        QuotaType.MAX_TICKETS_PER_DAY.value: 100,
        QuotaType.MAX_SHIPMENTS_PER_DAY.value: 50,
        QuotaType.MAX_STORAGE_MB.value: 1024,
        QuotaType.MAX_API_CALLS_PER_MINUTE.value: 60,
        QuotaType.ADVANCED_ANALYTICS.value: False,
        QuotaType.CUSTOM_INTEGRATIONS.value: True,
        QuotaType.WEBHOOK_SUPPORT.value: False,
    },
    "professional": {
        QuotaType.MAX_USERS.value: 50,
        QuotaType.MAX_TICKETS_PER_DAY.value: 1000,
        QuotaType.MAX_SHIPMENTS_PER_DAY.value: 500,
        QuotaType.MAX_STORAGE_MB.value: 10240,
        QuotaType.MAX_API_CALLS_PER_MINUTE.value: 300,
        QuotaType.ADVANCED_ANALYTICS.value: True,
        QuotaType.CUSTOM_INTEGRATIONS.value: True,
        QuotaType.WEBHOOK_SUPPORT.value: True,
    },
    "enterprise": {
        QuotaType.MAX_USERS.value: 999999,
        QuotaType.MAX_TICKETS_PER_DAY.value: 999999,
        QuotaType.MAX_SHIPMENTS_PER_DAY.value: 999999,
        QuotaType.MAX_STORAGE_MB.value: 999999,
        QuotaType.MAX_API_CALLS_PER_MINUTE.value: 9999,
        QuotaType.ADVANCED_ANALYTICS.value: True,
        QuotaType.CUSTOM_INTEGRATIONS.value: True,
        QuotaType.WEBHOOK_SUPPORT.value: True,
    },
}


class QuotaChecker:
    """Check and enforce quotas for a tenant"""
    
    def __init__(self, tenant_plan: str, tenant_quotas: Optional[Dict] = None):
        """
        Initialize quota checker
        
        Args:
            tenant_plan: Subscription plan (free_trial, basic, professional, enterprise)
            tenant_quotas: Custom quotas override (JSON from DB)
        """
        self.tenant_plan = tenant_plan.lower() if tenant_plan else "free_trial"
        
        # Get default quotas for plan
        self.quotas = DEFAULT_QUOTAS.get(self.tenant_plan, DEFAULT_QUOTAS["free_trial"]).copy()
        
        # Override with custom quotas if provided
        if tenant_quotas and isinstance(tenant_quotas, dict):
            self.quotas.update(tenant_quotas)
    
    def get_quota(self, quota_type: str) -> any:
        """Get quota value for a specific type"""
        return self.quotas.get(quota_type)
    
    def check_limit(self, quota_type: str, current_usage: int, increment: int = 1) -> tuple[bool, Optional[str]]:
        """
        Check if usage is within quota limit
        
        Args:
            quota_type: Type of quota to check
            current_usage: Current usage count
            increment: Amount to add (default 1)
            
        Returns:
            (is_within_limit, error_message)
        """
        limit = self.get_quota(quota_type)
        
        if limit is None:
            return True, None
        
        if current_usage + increment > limit:
            return False, f"{quota_type} limit ({limit}) exceeded"
        
        return True, None
    
    def check_feature_access(self, feature_name: str) -> tuple[bool, Optional[str]]:
        """
        Check if tenant has access to a feature
        
        Args:
            feature_name: Name of feature (e.g., 'advanced_analytics')
            
        Returns:
            (has_access, error_message)
        """
        feature_quota = f"{feature_name.lower()}"
        
        # Check if feature is a boolean quota
        if feature_quota in self.quotas:
            has_access = self.quotas[feature_quota]
            if not has_access:
                return False, f"Feature '{feature_name}' not available in {self.tenant_plan} plan"
            return True, None
        
        # Feature not recognized, allow by default
        return True, None
    
    def get_all_quotas(self) -> Dict:
        """Get all quotas for this tenant"""
        return self.quotas.copy()
    
    def get_usage_percentage(self, quota_type: str, current_usage: int) -> float:
        """Get usage as percentage of limit"""
        limit = self.get_quota(quota_type)
        if limit is None or limit == 0:
            return 0.0
        
        percentage = (current_usage / limit) * 100
        return min(percentage, 100.0)  # Cap at 100%
