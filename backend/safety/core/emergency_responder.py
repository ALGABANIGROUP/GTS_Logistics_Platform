"""
Safety Core Module
Emergency Responder System
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class EmergencyResponder:
    """Provides emergency response plans and execution tracking."""

    def __init__(self):
        self.emergency_response_logs = []
        self.emergency_plans = self._load_emergency_plans()

    def _load_emergency_plans(self) -> Dict[str, Any]:
        """Load predefined emergency response plans."""
        return {
            "fire": {
                "title": "Fire Emergency Response",
                "activation_conditions": ["Smoke or flames detected", "Fire alarm activation"],
                "immediate_actions": [
                    "Activate alarm and start evacuation",
                    "Isolate affected area if safe",
                    "Contact emergency services (998)",
                    "Account for all personnel at assembly points",
                ],
            },
            "chemical_spill": {
                "title": "Chemical Spill Response",
                "activation_conditions": ["Hazardous substance leak", "Exposure symptoms reported"],
                "immediate_actions": [
                    "Evacuate and cordon off contaminated zone",
                    "Use spill containment kit and PPE",
                    "Notify EHS coordinator immediately",
                    "Document material type and estimated volume",
                ],
            },
            "medical_emergency": {
                "title": "Medical Emergency Response",
                "activation_conditions": ["Injury or medical collapse", "Severe health distress report"],
                "immediate_actions": [
                    "Call onsite first-aid team",
                    "Contact emergency medical services",
                    "Stabilize patient if trained to do so",
                    "Secure incident scene for responders",
                ],
            },
        }

    async def get_emergency_plan(
        self, incident_type, location: str
    ) -> Optional[Dict[str, Any]]:
        """Select and return the most relevant emergency plan."""
        try:
            incident_type_str = (
                incident_type.value if hasattr(incident_type, "value") else str(incident_type)
            )

            if "fire" in incident_type_str.lower():
                plan = self.emergency_plans["fire"]
            elif "chemical" in incident_type_str.lower():
                plan = self.emergency_plans["chemical_spill"]
            else:
                plan = self.emergency_plans["medical_emergency"]

            plan["id"] = f"PLAN_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            plan["location"] = location

            return plan

        except Exception as e:
            logger.error(f"Failed to get emergency plan: {str(e)}")
            return None

    async def execute_emergency_response(
        self, plan_id: str, incident_id: str
    ) -> Dict[str, Any]:
        """Create response execution record for an active incident."""
        try:
            response = {
                "response_id": f"RESP_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                "plan_id": plan_id,
                "incident_id": incident_id,
                "initiated_at": datetime.utcnow().isoformat(),
                "status": "in_progress",
                "actions_executed": [],
            }

            self.emergency_response_logs.append(response)

            return response

        except Exception as e:
            logger.error(f"Emergency response execution failed: {str(e)}")
            return {"error": str(e)}
