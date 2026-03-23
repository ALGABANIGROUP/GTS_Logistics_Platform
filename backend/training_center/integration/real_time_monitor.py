from __future__ import annotations

from typing import Any


class RealTimeMonitor:
    """Maintain lightweight session snapshots for API reads."""

    def __init__(self) -> None:
        self._snapshots: dict[str, dict[str, Any]] = {}

    def track(self, session_id: str, payload: dict[str, Any]) -> None:
        self._snapshots[session_id] = payload

    def get(self, session_id: str) -> dict[str, Any] | None:
        return self._snapshots.get(session_id)

    def list_all(self) -> list[dict[str, Any]]:
        return list(self._snapshots.values())
