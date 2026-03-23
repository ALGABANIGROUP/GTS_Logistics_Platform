from __future__ import annotations

from contextvars import ContextVar

# Tenant context used by security.auth and multi-tenant routes.
# Defaults are safe for single-tenant/dev environments.

current_tenant_id: ContextVar[str | None] = ContextVar("current_tenant_id", default=None)
is_global_user: ContextVar[bool] = ContextVar("is_global_user", default=False)

__all__ = ["current_tenant_id", "is_global_user"]
