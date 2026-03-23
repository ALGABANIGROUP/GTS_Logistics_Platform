from __future__ import annotations
from typing import Dict, Type, Optional, Any

# Re-exported adapter: backend/integrations/loadboards/truckerpath.py
try:
    from .truckerpath import TruckerPathProvider  # type: ignore
    _import_error: Optional[Exception] = None
except Exception as e:
    TruckerPathProvider = None  # type: ignore
    _import_error = e

_PROVIDERS: Dict[str, Type[Any]] = {}

if TruckerPathProvider:
    _PROVIDERS["truckerpath"] = TruckerPathProvider  # type: ignore

def register_provider(name: str, cls: Type[Any]) -> None:
    """Register a provider class at runtime."""
    _PROVIDERS[(name or "").lower()] = cls

def get_provider(name: str) -> Type[Any]:
    """Return the provider class by name (lowercased)."""
    key = (name or "").lower()
    try:
        return _PROVIDERS[key]
    except KeyError:
        msg = f"Loadboard provider '{name}' not available."
        if _import_error:
            msg += f" Root cause: {_import_error}"
        raise ImportError(msg)

def list_providers() -> Dict[str, str]:
    """Debug helper: returns {key: ClassName}."""
    return {k: v.__name__ for k, v in _PROVIDERS.items()}
