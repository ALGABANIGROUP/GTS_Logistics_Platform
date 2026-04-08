# backend/services/__init__.py
"""
Services module for GTS Logistics Platform
"""
from .learning import LearningService
from .maintenance import MaintenanceService
from .legal import LegalService

__all__ = [
    'LearningService',
    'MaintenanceService',
    'LegalService'
]
