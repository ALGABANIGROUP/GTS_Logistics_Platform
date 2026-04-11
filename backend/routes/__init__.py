# backend/routes/__init__.py
from . import auth
from . import admin_users
from . import tenants
from . import partners
from . import system_manager_bot
from . import marketing_bot
# from . import security_bot
from .registry import iter_registered_routers

__all__ = ["auth", "admin_users", "tenants", "partners", "system_manager_bot", "marketing_bot", "iter_registered_routers"]
