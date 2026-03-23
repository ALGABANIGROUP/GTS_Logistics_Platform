"""
Backend package initializer for GTS Logistics.

This file ensures that environment variables are loaded
automatically when the backend package is imported.

If the env_bootstrap module is not found, the import is safely ignored.
"""

# Ensure environment bootstrap loads correctly
try:
    import env_bootstrap  # noqa: F401
except ImportError:
    pass

# Expose common backend modules if needed
__all__ = [
    "env_bootstrap",
]
