# Import the canonical Base from backend.database.base
from backend.database.base import Base

# Re-export for backward compatibility
__all__ = ["Base"]
