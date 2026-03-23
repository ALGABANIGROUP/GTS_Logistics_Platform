# backend/integrations/loadboards/truckerpath.py
from __future__ import annotations

"""
Adapter that re-exports TruckerPathProvider so that
'from .truckerpath import TruckerPathProvider' works from registry.py.

It tries common locations:
  - backend/integrations/truckerpath/provider.py
  - backend/integrations/truckerpath/__init__.py
"""

try:
    # Most common: provider defined in provider.py
    from backend.integrations.truckerpath.provider import TruckerPathProvider  # type: ignore
except Exception:
    try:
        # Or exported at package level
        from backend.integrations.truckerpath import TruckerPathProvider  # type: ignore
    except Exception as e:
        raise ImportError(
            "Could not locate TruckerPathProvider in backend.integrations.truckerpath.\n"
            "Expected one of:\n"
            "  - backend/integrations/truckerpath/provider.py (class TruckerPathProvider)\n"
            "  - backend/integrations/truckerpath/__init__.py (export TruckerPathProvider)\n"
            f"Original error: {e}"
        )

__all__ = ["TruckerPathProvider"]
