"""
Platform Expense Model

Alias for PlatformInfrastructureExpense to maintain backward compatibility.
The canonical model is in platform_infrastructure_expense.py
"""

from backend.models.platform_infrastructure_expense import PlatformInfrastructureExpense as PlatformExpense

__all__ = ["PlatformExpense"]

