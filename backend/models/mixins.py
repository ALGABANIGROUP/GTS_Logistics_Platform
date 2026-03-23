"""
DEV stub for backend.models.mixins

Some models import TenantScopedMixin but the module is missing in this repo snapshot.
This minimal mixin is enough to unblock imports for local development/auth testing.

If you later implement real multi-tenant scoping, replace this with the real mixins.
"""

class TenantScopedMixin:
    # Keep it empty to avoid altering DB schema in dev unexpectedly.
    pass
