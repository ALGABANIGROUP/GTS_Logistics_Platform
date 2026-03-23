from __future__ import annotations

import os
import pkgutil

# Allow "models.*" imports to resolve to backend/models/*
__path__ = pkgutil.extend_path(__path__, __name__)
_backend_models = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend", "models"))
if os.path.isdir(_backend_models) and _backend_models not in __path__:
    __path__.append(_backend_models)

__all__: list[str] = []
