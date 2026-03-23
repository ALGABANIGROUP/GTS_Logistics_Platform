# backend/vizion_bus.py
from __future__ import annotations
from typing import Any, Optional

_db: Any | None = None

def set_db(db: Any) -> None:
    """Called once from main.py after vizion_eye is initialized."""
    global _db
    _db = db

def enabled() -> bool:
    return _db is not None

def log(event: str, obj: Optional[dict] = None, meta: Optional[dict] = None) -> None:
    """Thin wrapper to avoid crashes if VIZION isn't available."""
    if _db:
        try:
            _db.log_event(event, obj, meta)
        except Exception:
            # never crash your app for observability
            pass
