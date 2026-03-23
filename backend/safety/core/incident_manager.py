"""
Incident Manager and Investigation System
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple

logger = logging.getLogger(__name__)


class IncidentManager:
    """Main Incident Manager"""

    def __init__(self):
        self.incident_database = []
        self.investigation_reports = []
        self.root_cause_analysis = {}

        # Analysis patterns
        self.patterns = {
            "common_causes": [
                "Not wearing PPE",
                "Insufficient training",
                "Negligence",
                "Poor maintenance",
                "Unsafe procedures",
                "Haste",
                "Fatigue",
                "Noise",
                "Insufficient lighting",
            ],
            "equipment_related": [
                "Broken equipment",
                "Technical failure",
                "Damaged tool",
                "Defective device",
                "No maintenance",
            ],
            "environmental": [
                "Slippery floor",
                "Clutter",
                "Obstacles",
                "Heat",
                "Humidity",
                "Noise",
            ],
        }

    async def record_incident(self, incident) -> Dict[str, Any]:
        """Record an incident"""
        try:
            incident_record = {
                "id": incident.id,
                "type": incident.type.value,
                "severity": incident.severity.value,
                "description": incident.description,
                "location": incident.location,
                "reported_by": incident.reported_by,
                "reported_at": incident.reported_at.isoformat(),
                "injured_persons": incident.injured_persons or [],
                "witnesses": incident.witnesses or [],
                "immediate_actions": incident.immediate_actions or [],
                "investigation_status": "recorded",
                "recorded_at": datetime.utcnow().isoformat(),
            }

            self.incident_database.append(incident_record)

            # Automatically start investigation for major incidents
            if incident.severity.value in ["major", "critical", "fatal"]:
                await self._initiate_investigation(incident)

            logger.info(f"Incident {incident.id} recorded successfully")

            return {
                "status": "recorded",
                "incident_id": incident.id,
                "investigation_initiated": incident.severity.value
                in ["major", "critical", "fatal"],
            }

        except Exception as e:
            logger.error(f"Incident recording failed: {str(e)}")
            return {"error": str(e)}

    async def _initiate_investigation(self, incident):
        """Initiate investigation for the incident"""
        try:
            investigation = {
                "investigation_id": f"INV_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                "incident_id": incident.id,
                "type": incident.type.value,
                "severity": incident.severity.value,
                "initiated_at": datetime.utcnow().isoformat(),
                "status": "in_progress",
                "investigation_team": ["Safety Manager", "Area Supervisor"],
                "timeline": [
                    {
                        "time": datetime.utcnow().isoformat(),
                        "action": "Investigation started",
                        "by": "AI Safety Manager Bot",
                    }
                ],
                "evidence_collected": [],
                "witness_statements": [],
                "findings": [],
                "root_cause": "",
                "recommendations": [],
            }

            self.investigation_reports.append(investigation)

            # Run preliminary analysis
            await self._perform_preliminary_analysis(incident, investigation)

            logger.info(f"Investigation initiated for incident {incident.id}")

        except Exception as e:
            logger.error(f"Investigation initiation failed: {str(e)}")

    async def _perform_preliminary_analysis(self, incident, investigation):
        """Perform preliminary analysis"""
        description_lower = incident.description.lower()

        # Search for common cause patterns
        causes_found = []
        for category, patterns in self.patterns.items():
            for pattern in patterns:
                if pattern.lower() in description_lower:
                    causes_found.append(
                        {"category": category, "pattern": pattern, "confidence": "high"}
                    )

        investigation["preliminary_findings"] = causes_found

        # Determine initial root causes
        if causes_found:
            root_causes = []
            for cause in causes_found[:3]:  # First 3 causes
                root_causes.append(f"{cause['category']}: {cause['pattern']}")

            investigation["root_cause"] = ", ".join(root_causes)

            # Generate initial recommendations
            recommendations = []
            for cause in causes_found:
                rec = self._generate_recommendation(cause["category"], cause["pattern"])
                if rec:
                    recommendations.append(rec)

            investigation["recommendations"] = recommendations[:5]  # First 5 recommendations

    def _generate_recommendation(self, category: str, pattern: str) -> str:
        """Generate a recommendation based on the cause"""
        recommendations = {
            "common_causes": {
                "Not wearing PPE": "Enhance monitoring and use of personal protective equipment",
                "Insufficient training": "Provide additional training and retraining",
                "Negligence": "Promote safety culture and penalties for violators",
                "Poor maintenance": "Improve equipment maintenance scheduling",
            },
            "equipment_related": {
                "Broken equipment": "Immediate maintenance and thorough inspection",
                "Technical failure": "Review operating and maintenance procedures",
                "Damaged tool": "Thorough inspection of tools and replace damaged ones",
            },
            "environmental": {
                "Slippery floor": "Immediate cleaning and place warning signs",
                "Clutter": "Regular cleaning and organizing program",
                "Obstacles": "Remove obstacles and clearly mark pathways",
            },
        }

        if category in recommendations and pattern in recommendations[category]:
            return recommendations[category][pattern]

        return f"Review safety procedures related to {pattern}"

    async def get_incident_statistics(self, days: int = 30) -> Dict[str, Any]:
        """Get incident statistics"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)

            incidents_in_period = [
                inc
                for inc in self.incident_database
                if datetime.fromisoformat(inc["reported_at"]) > cutoff_date
            ]

            statistics = {
                "period_days": days,
                "total_incidents": len(incidents_in_period),
                "by_type": {},
                "by_severity": {},
                "by_location": {},
                "trend_analysis": {},
                "key_insights": [],
            }

            for incident in incidents_in_period:
                # By type
                inc_type = incident["type"]
                statistics["by_type"][inc_type] = (
                    statistics["by_type"].get(inc_type, 0) + 1
                )

                # By severity
                severity = incident["severity"]
                statistics["by_severity"][severity] = (
                    statistics["by_severity"].get(severity, 0) + 1
                )

                # By location
                location = incident["location"]
                statistics["by_location"][location] = (
                    statistics["by_location"].get(location, 0) + 1
                )

            # Generate insights
            if statistics["total_incidents"] > 0:
                if statistics["by_type"]:
                    most_common_type = max(
                        statistics["by_type"].items(), key=lambda x: x[1]
                    )[0]
                    statistics["key_insights"].append(
                        f"Most common type: {most_common_type}"
                    )

                if statistics["by_location"]:
                    most_risky_location = max(
                        statistics["by_location"].items(), key=lambda x: x[1]
                    )[0]
                    statistics["key_insights"].append(
                        f"Most risky location: {most_risky_location}"
                    )

                if (
                    "major" in statistics["by_severity"]
                    or "critical" in statistics["by_severity"]
                ):
                    statistics["key_insights"].append(
                        "There are serious incidents that require urgent attention"
                    )

            return statistics

        except Exception as e:
            logger.error(f"Incident statistics generation failed: {str(e)}")
            return {"error": str(e)}

    async def generate_incident_report(self, incident_id: str) -> Dict[str, Any]:
        """Generate incident report"""
        try:
            # Find incident
            incident = None
            for inc in self.incident_database:
                if inc["id"] == incident_id:
                    incident = inc
                    break

            if not incident:
                return {"error": f"Incident {incident_id} not found"}

            # Find investigation report
            investigation = None
            for inv in self.investigation_reports:
                if inv["incident_id"] == incident_id:
                    investigation = inv
                    break

            # Build final report payload
            report = {
                "report_id": f"REP_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                "incident_id": incident_id,
                "generated_at": datetime.utcnow().isoformat(),
                "incident_details": {
                    "type": incident["type"],
                    "severity": incident["severity"],
                    "description": incident["description"],
                    "location": incident["location"],
                    "reported_by": incident["reported_by"],
                    "reported_at": incident["reported_at"],
                    "injured_persons": incident["injured_persons"],
                    "immediate_actions": incident["immediate_actions"],
                },
                "investigation_summary": investigation or {"status": "no_investigation"},
                "root_cause_analysis": self.root_cause_analysis.get(incident_id, {}),
                "follow_up_required": incident["severity"]
                in ["major", "critical", "fatal"],
                "report_status": "final",
            }

            return report

        except Exception as e:
            logger.error(f"Incident report generation failed: {str(e)}")
            return {"error": str(e)}
