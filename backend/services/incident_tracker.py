import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from enum import Enum
from dataclasses import dataclass, asdict
import json
import traceback

logger = logging.getLogger(__name__)

class IncidentSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class IncidentStatus(Enum):
    DETECTED = "detected"
    INVESTIGATING = "investigating"
    CONTAINED = "contained"
    RESOLVED = "resolved"
    POST_MORTEM = "post_mortem"

@dataclass
class Incident:
    """Incident model"""
    id: str
    title: str
    description: str
    severity: IncidentSeverity
    status: IncidentStatus
    detected_at: datetime
    service: str
    error_message: str
    stack_trace: Optional[str] = None
    affected_users: int = 0
    resolved_at: Optional[datetime] = None
    resolution_notes: Optional[str] = None
    root_cause: Optional[str] = None
    actions_taken: List[str] = None

    def __post_init__(self):
        if self.actions_taken is None:
            self.actions_taken = []

class IncidentTracker:
    """
    Incident tracking system - records and analyzes system errors
    """

    def __init__(self):
        self.active_incidents: Dict[str, Incident] = {}
        self.incident_history: List[Incident] = []
        self.log_buffer: List[Dict] = []

        logger.info("✅ Incident Tracker initialized")

    def capture_error(self, error_data: Dict) -> Incident:
        """
        Record new error as incident
        """
        incident_id = f"INC-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

        # Extract information
        service = error_data.get("service", "unknown")
        error_message = error_data.get("error", "Unknown error")
        stack_trace = error_data.get("traceback", "")

        # Determine severity
        severity = self._determine_severity(error_message, stack_trace)

        incident = Incident(
            id=incident_id,
            title=self._generate_title(error_message),
            description=error_data.get("description", error_message),
            severity=severity,
            status=IncidentStatus.DETECTED,
            detected_at=datetime.now(),
            service=service,
            error_message=error_message,
            stack_trace=stack_trace,
            affected_users=error_data.get("affected_users", 0)
        )

        self.active_incidents[incident_id] = incident

        logger.warning(f"🚨 Incident captured: {incident_id} - {incident.title}")

        # Send immediate alert
        self._send_alert(incident)

        return incident

    def investigate(self, incident_id: str, investigator: str, notes: str) -> Dict:
        """
        Start investigation of incident
        """
        if incident_id not in self.active_incidents:
            return {"error": "Incident not found"}

        incident = self.active_incidents[incident_id]
        incident.status = IncidentStatus.INVESTIGATING
        incident.actions_taken.append(f"Investigation started by {investigator}: {notes}")

        logger.info(f"🔍 Investigation started for {incident_id}")

        return {
            "success": True,
            "incident_id": incident_id,
            "status": incident.status.value,
            "message": f"Investigation started"
        }

    def contain(self, incident_id: str, action: str) -> Dict:
        """
        Contain incident (prevent further damage)
        """
        if incident_id not in self.active_incidents:
            return {"error": "Incident not found"}

        incident = self.active_incidents[incident_id]
        incident.status = IncidentStatus.CONTAINED
        incident.actions_taken.append(f"Contained: {action}")

        logger.info(f"🛡️ Incident contained: {incident_id} - {action}")

        return {
            "success": True,
            "incident_id": incident_id,
            "status": incident.status.value,
            "containment_action": action
        }

    def resolve(self, incident_id: str, resolution_notes: str, root_cause: str = None) -> Dict:
        """
        Resolve incident
        """
        if incident_id not in self.active_incidents:
            return {"error": "Incident not found"}

        incident = self.active_incidents[incident_id]
        incident.status = IncidentStatus.RESOLVED
        incident.resolved_at = datetime.now()
        incident.resolution_notes = resolution_notes
        incident.root_cause = root_cause
        incident.actions_taken.append(f"Resolved: {resolution_notes}")

        # Move to history
        self.incident_history.append(incident)
        del self.active_incidents[incident_id]

        logger.info(f"✅ Incident resolved: {incident_id}")

        return {
            "success": True,
            "incident_id": incident_id,
            "status": incident.status.value,
            "resolution_time": (incident.resolved_at - incident.detected_at).total_seconds(),
            "message": "Incident resolved"
        }

    def analyze_logs(self, incident_id: str, log_lines: List[str], window_minutes: int = 30) -> Dict:
        """
        Analyze logs related to incident
        """
        incident = self.active_incidents.get(incident_id)
        if not incident:
            # Search in history
            incident = next((i for i in self.incident_history if i.id == incident_id), None)
            if not incident:
                return {"error": "Incident not found"}

        # Analyze logs
        error_patterns = []
        related_errors = []

        for line in log_lines:
            if incident.error_message.lower() in line.lower():
                related_errors.append(line)

            # Common error patterns
            patterns = [
                (r'Connection refused', "Database connection issue"),
                (r'Timeout', "Request timeout"),
                (r'Authentication failed', "Auth issue"),
                (r'Permission denied', "Permission issue"),
                (r'Out of memory', "Memory issue")
            ]

            for pattern, description in patterns:
                if pattern in line:
                    error_patterns.append(description)

        return {
            "success": True,
            "incident_id": incident_id,
            "total_logs_analyzed": len(log_lines),
            "related_errors": len(related_errors),
            "error_patterns": list(set(error_patterns)),
            "sample_logs": related_errors[:10],
            "recommendation": self._get_recommendation(error_patterns)
        }

    def get_active_incidents(self) -> List[Dict]:
        """
        Get active incidents
        """
        return [
            {
                "id": i.id,
                "title": i.title,
                "severity": i.severity.value,
                "status": i.status.value,
                "detected_at": i.detected_at.isoformat(),
                "service": i.service,
                "affected_users": i.affected_users
            }
            for i in self.active_incidents.values()
        ]

    def get_incident_report(self, incident_id: str = None, days: int = 7) -> Dict:
        """
        Incident report
        """
        if incident_id:
            incident = next((i for i in self.incident_history if i.id == incident_id), None)
            if not incident:
                return {"error": "Incident not found"}

            return {
                "incident": asdict(incident),
                "timeline": self._generate_timeline(incident),
                "impact_analysis": self._analyze_impact(incident)
            }

        # Comprehensive report for period
        cutoff = datetime.now() - timedelta(days=days)
        relevant_incidents = [i for i in self.incident_history if i.detected_at >= cutoff]

        return {
            "period_days": days,
            "total_incidents": len(relevant_incidents),
            "by_severity": {
                "critical": sum(1 for i in relevant_incidents if i.severity == IncidentSeverity.CRITICAL),
                "high": sum(1 for i in relevant_incidents if i.severity == IncidentSeverity.HIGH),
                "medium": sum(1 for i in relevant_incidents if i.severity == IncidentSeverity.MEDIUM),
                "low": sum(1 for i in relevant_incidents if i.severity == IncidentSeverity.LOW)
            },
            "by_service": self._group_by_service(relevant_incidents),
            "avg_resolution_time": self._calculate_avg_resolution(relevant_incidents),
            "incidents": [asdict(i) for i in relevant_incidents[-20:]]
        }

    def _determine_severity(self, error_message: str, stack_trace: str) -> IncidentSeverity:
        """Determine incident severity"""
        error_lower = error_message.lower()

        # High severity keywords
        if any(keyword in error_lower for keyword in ["critical", "fatal", "emergency", "database down"]):
            return IncidentSeverity.CRITICAL

        if any(keyword in error_lower for keyword in ["error", "failed", "exception", "timeout"]):
            return IncidentSeverity.HIGH

        if any(keyword in error_lower for keyword in ["warning", "deprecated", "slow"]):
            return IncidentSeverity.MEDIUM

        return IncidentSeverity.LOW

    def _generate_title(self, error_message: str) -> str:
        """Generate incident title"""
        max_length = 80
        if len(error_message) > max_length:
            return error_message[:max_length] + "..."
        return error_message

    def _send_alert(self, incident: Incident):
        """Send alert for incident"""
        # In practice, this can be connected to notification system
        logger.warning(f"🚨 ALERT: [{incident.severity.value.upper()}] {incident.title}")

    def _get_recommendation(self, error_patterns: List[str]) -> str:
        """Recommendation based on error patterns"""
        if "Database connection issue" in error_patterns:
            return "Check database connectivity, verify credentials, and restart connection pool."
        if "Request timeout" in error_patterns:
            return "Increase timeout settings or optimize slow queries."
        if "Auth issue" in error_patterns:
            return "Verify authentication tokens and session management."
        if "Permission issue" in error_patterns:
            return "Check file and directory permissions."
        if "Memory issue" in error_patterns:
            return "Increase memory allocation or optimize memory usage."
        return "Review application logs for more details."

    def _generate_timeline(self, incident: Incident) -> List[Dict]:
        """Generate incident timeline"""
        timeline = [
            {"time": incident.detected_at.isoformat(), "event": "Incident detected"},
            {"time": incident.detected_at.isoformat(), "event": "Alert sent"}
        ]

        for action in incident.actions_taken:
            timeline.append({"time": datetime.now().isoformat(), "event": action})

        if incident.resolved_at:
            timeline.append({"time": incident.resolved_at.isoformat(), "event": "Incident resolved"})

        return timeline

    def _analyze_impact(self, incident: Incident) -> Dict:
        """Analyze incident impact"""
        resolution_time = (incident.resolved_at - incident.detected_at).total_seconds() if incident.resolved_at else None

        return {
            "duration_minutes": resolution_time / 60 if resolution_time else None,
            "affected_users": incident.affected_users,
            "severity_score": {"critical": 100, "high": 60, "medium": 30, "low": 10}.get(incident.severity.value, 0),
            "estimated_impact": self._estimate_impact(incident)
        }

    def _estimate_impact(self, incident: Incident) -> str:
        """Estimate impact"""
        if incident.severity == IncidentSeverity.CRITICAL:
            return "Major service disruption - immediate attention required"
        elif incident.severity == IncidentSeverity.HIGH:
            return "Partial service degradation - high priority"
        elif incident.severity == IncidentSeverity.MEDIUM:
            return "Minor impact - scheduled fix"
        return "Low impact - monitor only"

    def _group_by_service(self, incidents: List[Incident]) -> Dict:
        """Group incidents by service"""
        services = {}
        for incident in incidents:
            services[incident.service] = services.get(incident.service, 0) + 1
        return services

    def _calculate_avg_resolution(self, incidents: List[Incident]) -> float:
        """Calculate average resolution time"""
        resolved = [i for i in incidents if i.resolved_at]
        if not resolved:
            return 0

        total_seconds = sum((i.resolved_at - i.detected_at).total_seconds() for i in resolved)
        return (total_seconds / len(resolved)) / 60  # in minutes


incident_tracker = IncidentTracker()


__all__ = [
    "Incident",
    "IncidentSeverity",
    "IncidentStatus",
    "IncidentTracker",
    "incident_tracker",
]
