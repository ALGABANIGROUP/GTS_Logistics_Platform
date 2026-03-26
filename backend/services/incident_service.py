from __future__ import annotations

from typing import Any, Dict, List

from backend.services.incident_tracker import incident_tracker


class IncidentServiceAdapter:
    async def get_recent_incidents(self, limit: int = 5) -> List[Dict[str, Any]]:
        incidents = getattr(incident_tracker, "incidents", []) or []
        return list(incidents)[-limit:]


incident_service = IncidentServiceAdapter()

__all__ = ["incident_service", "IncidentServiceAdapter"]
