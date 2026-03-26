from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class SecurityManagerBot:
    """In-memory security operations bot used by bot registry and tests."""

    name = "security_manager"
    display_name = "Security Manager Bot"
    description = "Monitors access, scans for threats, and prepares audit summaries"

    def __init__(self) -> None:
        self.security_alerts: List[Dict[str, Any]] = []
        self.active_sessions: List[Dict[str, Any]] = []

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        action = payload.get("action", "dashboard")

        if action == "threat_scan":
            return await self._run_threat_scan()
        if action == "access_control":
            return await self._manage_access_control(payload)
        if action == "security_alerts":
            return await self._get_security_alerts()
        if action == "session_monitoring":
            return await self._monitor_sessions()
        if action == "incident_response":
            return await self._handle_security_incident(payload)
        if action == "audit_report":
            return await self._generate_audit_report()
        return self.get_dashboard()

    async def _run_threat_scan(self) -> Dict[str, Any]:
        threats_found = [
            {"type": "suspicious_login", "severity": "medium", "source": "192.168.1.100"},
            {"type": "unusual_activity", "severity": "low", "source": "user_session_45"},
            {"type": "failed_auth_attempts", "severity": "high", "source": "api_endpoint"},
        ]
        return {
            "success": True,
            "scan_completed": True,
            "threats_detected": len(threats_found),
            "threats": threats_found,
            "scan_timestamp": datetime.now().isoformat(),
            "action": "threat_scan",
        }

    async def _manage_access_control(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        user_id = payload.get("user_id")
        access_action = payload.get("access_action", "check")

        if not user_id:
            return {"success": False, "error": "Please specify user ID", "action": "access_control"}

        if access_action == "grant":
            permission = payload.get("permission", "read")
            return {
                "success": True,
                "user_id": user_id,
                "permission": permission,
                "status": "granted",
                "message": f"Access granted to {user_id}",
                "action": "access_control",
            }
        if access_action == "revoke":
            return {
                "success": True,
                "user_id": user_id,
                "status": "revoked",
                "message": f"Access revoked from {user_id}",
                "action": "access_control",
            }
        return {
            "success": True,
            "user_id": user_id,
            "permissions": ["read", "write"],
            "status": "active",
            "action": "access_control",
        }

    async def _get_security_alerts(self) -> Dict[str, Any]:
        return {
            "success": True,
            "alerts": self.security_alerts,
            "count": len(self.security_alerts),
            "critical_count": len([a for a in self.security_alerts if a.get("severity") == "critical"]),
            "action": "security_alerts",
        }

    async def _monitor_sessions(self) -> Dict[str, Any]:
        now = datetime.now()
        sessions = [
            {
                "session_id": "sess_001",
                "user": "admin",
                "ip": "192.168.1.1",
                "last_activity": now.isoformat(),
            },
            {
                "session_id": "sess_002",
                "user": "user1",
                "ip": "192.168.1.50",
                "last_activity": (now - timedelta(minutes=5)).isoformat(),
            },
        ]
        self.active_sessions = sessions
        return {
            "success": True,
            "active_sessions": len(sessions),
            "sessions": sessions,
            "suspicious_sessions": 0,
            "action": "session_monitoring",
        }

    async def _handle_security_incident(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        incident = {
            "id": f"SEC-{len(self.security_alerts) + 1}",
            "type": payload.get("type", "general"),
            "description": payload.get("description"),
            "reported_at": datetime.now().isoformat(),
            "status": "investigating",
            "severity": "high",
        }
        self.security_alerts.append(incident)
        return {
            "success": True,
            "incident": incident,
            "message": "Security incident reported and investigation initiated",
            "action": "incident_response",
        }

    async def _generate_audit_report(self) -> Dict[str, Any]:
        return {
            "success": True,
            "report": {
                "period": "daily",
                "total_events": 1250,
                "failed_logins": 12,
                "successful_logins": 89,
                "suspicious_activities": 3,
                "blocked_attempts": 8,
                "compliance_score": 94.5,
            },
            "action": "audit_report",
        }

    def get_dashboard(self) -> Dict[str, Any]:
        return {
            "success": True,
            "bot": self.name,
            "display_name": self.display_name,
            "available_actions": [
                "threat_scan - Run security scan",
                "access_control - Manage permissions",
                "security_alerts - View alerts",
                "session_monitoring - Monitor sessions",
                "incident_response - Handle incidents",
                "audit_report - Generate audit report",
            ],
            "action": "dashboard",
        }

    async def status(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "display_name": self.display_name,
            "status": "active",
            "description": self.description,
            "open_alerts": len(self.security_alerts),
            "tracked_sessions": len(self.active_sessions),
        }

    async def config(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "display_name": self.display_name,
            "description": self.description,
            "actions": self.get_dashboard()["available_actions"],
        }
