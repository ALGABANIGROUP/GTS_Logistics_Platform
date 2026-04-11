"""
backend.models package

This repo snapshot may miss some model modules. Keep imports optional in dev
so the app can boot and critical routes (auth) can load.
"""

# Core model(s) that must exist
from .user import User  # noqa: F401
from .document import Document  # noqa: F401

# Optional models (do not fail app startup if missing)
_optional_modules = [
    ("password_reset_token", "PasswordResetToken"),
    ("tenant", "Tenant"),
    ("partner", "LogisticsPartner"),
    ("social_media", "SocialMedia"),
    ("ws_notifications", "WSNotification"),
    ("platform_expense", "PlatformExpense"),
    ("models", "Shipment"),
    ("models", "MessageLog"),
]

for mod_name, symbol in _optional_modules:
    try:
        module = __import__(f"{__name__}.{mod_name}", fromlist=[symbol])
        globals()[symbol] = getattr(module, symbol)
    except Exception:
        # Intentionally ignore missing/failed optional models in dev
        pass
