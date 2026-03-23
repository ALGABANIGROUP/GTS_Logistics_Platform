from __future__ import annotations

import os
from typing import Optional

from .manager import SourceManager
from .open_canada import OpenCanadaSource
from .statscan import StatsCanSource

_manager: Optional[SourceManager] = None

EXTERNAL_SOURCES_ENABLED = os.getenv("EXTERNAL_SOURCES_ENABLED", "1").strip().lower() in {
    "1",
    "true",
    "yes",
    "on",
}


def init_sources() -> SourceManager:
    global _manager
    if _manager is not None:
        return _manager

    manager = SourceManager()
    if not EXTERNAL_SOURCES_ENABLED:
        _manager = manager
        return _manager

    manager.register(StatsCanSource())
    manager.register(OpenCanadaSource())
    _manager = manager
    return _manager


def get_sources_manager() -> SourceManager:
    if _manager is None:
        raise RuntimeError("Sources manager has not been initialized")
    return _manager
