from __future__ import annotations

import os
import pkgutil

# Allow "database.*" imports to resolve to backend/database/*
__path__ = pkgutil.extend_path(__path__, __name__)
_backend_db = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend", "database"))
if os.path.isdir(_backend_db) and _backend_db not in __path__:
    __path__.append(_backend_db)

__all__: list[str] = []
