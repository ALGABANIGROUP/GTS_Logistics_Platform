from __future__ import annotations

import base64
import logging
import re
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
        self._encryption_keys: Dict[str, str] = {}

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        context = payload.get("context") if isinstance(payload.get("context"), dict) else None
        source = context or payload
        action = source.get("action", "dashboard")

        if action == "threat_scan":
            return await self._run_threat_scan()
        if action == "access_control":
            return await self._manage_access_control(source)
        if action == "security_alerts":
            return await self._get_security_alerts()
        if action == "session_monitoring":
            return await self._monitor_sessions()
        if action == "incident_response":
            return await self._handle_security_incident(source)
        if action == "audit_report":
            return await self._generate_audit_report()
        if action == "encrypt_sensitive_data":
            return await self._encrypt_sensitive_data(source)
        if action == "decrypt_sensitive_data":
            return await self._decrypt_sensitive_data(source)
        if action == "create_session":
            return await self._create_session(source)
        if action == "validate_session":
            return await self._validate_session(source)
        return self.get_dashboard()

    async def process_message(self, message: str) -> Dict[str, Any]:
        message_lower = (message or "").lower()
        threats: List[Dict[str, Any]] = []

        if "sql injection" in message_lower or "drop table" in message_lower:
            threats.append({"type": "sql_injection", "severity": "high"})

        ip_match = re.search(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", message or "")
        if ip_match:
            threats.append({"type": "malicious_ip", "value": ip_match.group(0), "severity": "medium"})

        return {
            "ok": True,
            "success": True,
            "has_threats": bool(threats),
            "threats": threats,
            "action": "message_analysis",
        }

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
            "ok": True,
            "success": True,
            "bot": self.name,
            "display_name": self.display_name,
            "quick_stats": {
                "open_alerts": len(self.security_alerts),
                "active_sessions": len(self.active_sessions),
                "compliance_score": 94.5,
                "blocked_ips": 2,
            },
            "compliance": {
                "score": 94.5,
                "frameworks": ["SOC 2", "ISO 27001"],
                "status": "good",
                "gdpr": "compliant",
            },
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

    async def _encrypt_sensitive_data(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        raw = str(payload.get("data") or "")
        purpose = str(payload.get("purpose") or "general")
        key_id = f"key_{len(self._encryption_keys) + 1}"
        self._encryption_keys[key_id] = purpose
        encrypted_data = base64.urlsafe_b64encode(raw.encode("utf-8")).decode("ascii")
        return {
            "ok": True,
            "success": True,
            "key_id": key_id,
            "encrypted_data": encrypted_data,
            "purpose": purpose,
            "action": "encrypt_sensitive_data",
        }

    async def _decrypt_sensitive_data(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        encrypted_data = str(payload.get("encrypted_data") or "")
        decrypted = base64.urlsafe_b64decode(encrypted_data.encode("ascii")).decode("utf-8")
        return {
            "ok": True,
            "success": True,
            "decrypted_data": decrypted,
            "key_id": payload.get("key_id"),
            "action": "decrypt_sensitive_data",
        }

    async def _create_session(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        session = {
            "session_id": f"sess_{len(self.active_sessions) + 1}",
            "user_id": payload.get("user_id"),
            "ip": payload.get("ip"),
            "user_agent": payload.get("user_agent"),
            "created_at": datetime.now().isoformat(),
        }
        self.active_sessions.append(session)
        return {
            "ok": True,
            "success": True,
            **session,
            "action": "create_session",
        }

    async def _validate_session(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        session_id = payload.get("session_id")
        ip = payload.get("ip")
        session = next((item for item in self.active_sessions if item.get("session_id") == session_id), None)
        valid = bool(session and (ip is None or session.get("ip") == ip))
        return {
            "ok": True,
            "success": True,
            "valid": valid,
            "session_id": session_id,
            "action": "validate_session",
        }

    async def detect_brute_force(self, attempts: List[Dict[str, Any]]) -> Dict[str, Any]:
        grouped: Dict[str, int] = {}
        for attempt in attempts:
            if attempt.get("success") is False:
                ip = str(attempt.get("ip_address") or "unknown")
                grouped[ip] = grouped.get(ip, 0) + 1

        top_ip = max(grouped, key=grouped.get) if grouped else None
        return {
            "ok": True,
            "is_brute_force": bool(top_ip and grouped[top_ip] >= 5),
            "source_ip": top_ip,
            "failed_attempts": grouped.get(top_ip, 0) if top_ip else 0,
        }

    async def detect_ddos(self, traffic: List[Dict[str, Any]]) -> Dict[str, Any]:
        unique_ips = len({entry.get("ip") for entry in traffic if entry.get("ip")})
        return {
            "ok": True,
            "is_ddos": len(traffic) >= 100 and unique_ips >= 50,
            "request_count": len(traffic),
            "unique_ips": unique_ips,
        }
