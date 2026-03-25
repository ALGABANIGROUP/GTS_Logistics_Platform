"""
Security Manager Bot - Enhanced security monitoring and threat detection
Handles access control, security incidents, and system protection
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class SecurityManagerBot:
    """Enhanced Security Manager Bot for system protection"""

    name = "security_manager"
    display_name = "Security Manager Bot"
    description = "Manages security monitoring, access control, and threat detection"

    def __init__(self):
        self.security_alerts = []
        self.access_logs = []
        self.threat_patterns = {}
        self.active_sessions = {}

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Execute security manager commands"""
        action = payload.get("action", "dashboard")

        if action == "threat_scan":
            return await self._run_threat_scan()
        elif action == "access_control":
            return await self._manage_access_control(payload)
        elif action == "security_alerts":
            return await self._get_security_alerts()
        elif action == "session_monitoring":
            return await self._monitor_sessions()
        elif action == "incident_response":
            return await self._handle_security_incident(payload)
        elif action == "audit_report":
            return await self._generate_audit_report()
        else:
            return self._get_dashboard()

    async def _run_threat_scan(self) -> Dict[str, Any]:
        """Run comprehensive threat detection scan"""
        threats_found = [
            {"type": "suspicious_login", "severity": "medium", "source": "192.168.1.100"},
            {"type": "unusual_activity", "severity": "low", "source": "user_session_45"},
            {"type": "failed_auth_attempts", "severity": "high", "source": "api_endpoint"}
        ]

        return {
            "success": True,
            "scan_completed": True,
            "threats_detected": len(threats_found),
            "threats": threats_found,
            "scan_timestamp": datetime.now().isoformat(),
            "action": "threat_scan"
        }

    async def _manage_access_control(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Manage user access permissions"""
        user_id = payload.get("user_id")
        action = payload.get("access_action")  # grant, revoke, check

        if not user_id:
            return {"error": "Please specify user ID"}

        if action == "grant":
            permission = payload.get("permission", "read")
            return {
                "success": True,
                "user_id": user_id,
                "permission": permission,
                "status": "granted",
                "message": f"Access granted to {user_id}",
                "action": "access_control"
            }
        elif action == "revoke":
            return {
                "success": True,
                "user_id": user_id,
                "status": "revoked",
                "message": f"Access revoked from {user_id}",
                "action": "access_control"
            }
        else:  # check
            current_permissions = ["read", "write"]  # Mock data
            return {
                "success": True,
                "user_id": user_id,
                "permissions": current_permissions,
                "status": "active",
                "action": "access_control"
            }

    async def _get_security_alerts(self) -> Dict[str, Any]:
        """Get active security alerts"""
        return {
            "success": True,
            "alerts": self.security_alerts,
            "count": len(self.security_alerts),
            "critical_count": len([a for a in self.security_alerts if a.get("severity") == "critical"]),
            "action": "security_alerts"
        }

    async def _monitor_sessions(self) -> Dict[str, Any]:
        """Monitor active user sessions"""
        sessions = [
            {"session_id": "sess_001", "user": "admin", "ip": "192.168.1.1", "last_activity": datetime.now().isoformat()},
            {"session_id": "sess_002", "user": "user1", "ip": "192.168.1.50", "last_activity": (datetime.now() - timedelta(minutes=5)).isoformat()},
        ]

        return {
            "success": True,
            "active_sessions": len(sessions),
            "sessions": sessions,
            "suspicious_sessions": 0,
            "action": "session_monitoring"
        }

    async def _handle_security_incident(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle security incident response"""
        incident_type = payload.get("type", "general")
        description = payload.get("description")

        incident = {
            "id": f"SEC-{len(self.security_alerts)+1}",
            "type": incident_type,
            "description": description,
            "reported_at": datetime.now().isoformat(),
            "status": "investigating",
            "severity": "high"
        }

        self.security_alerts.append(incident)

        return {
            "success": True,
            "incident": incident,
            "message": "Security incident reported and investigation initiated",
            "action": "incident_response"
        }

    async def _generate_audit_report(self) -> Dict[str, Any]:
        """Generate security audit report"""
        return {
            "success": True,
            "report": {
                "period": "daily",
                "total_events": 1250,
                "failed_logins": 12,
                "successful_logins": 89,
                "suspicious_activities": 3,
                "blocked_attempts": 8,
                "compliance_score": 94.5
            },
            "action": "audit_report"
        }

    def _get_dashboard(self) -> Dict[str, Any]:
        """Return security dashboard"""
        return {
            "success": True,
            "bot": self.name,
            "display_name": self.display_name,
            "available_actions": [
                "threat_scan - Run security scan",
                "access_control {user_id} - Manage permissions",
                "security_alerts - View alerts",
                "session_monitoring - Monitor sessions",
                "incident_response - Handle incidents",
                "audit_report - Generate audit"
            ],
            "action": "dashboard"
        }

    async def status(self) -> Dict[str, Any]:
        """Return bot status"""
        return {
            "name": self.name,
            "display_name": self.display_name,
            "status": "active",
            "description": self.description
        }

    async def config(self) -> Dict[str, Any]:
        """Return bot configuration"""
        return {
            "name": self.name,
            "display_name": self.display_name,
            "description": self.description,
            "actions": self._get_dashboard()["available_actions"]
        }
                    "ip_address": "192.168.1.0/24",
                    "reason": "Internal network",
                    "created_at": (now - timedelta(days=90)).isoformat(),
                }
            ],
        }
        self.login_attempts: List[Dict[str, Any]] = []
        self.audit_log: List[Dict[str, Any]] = [
            {
                "log_id": "AUD001",
                "timestamp": (now - timedelta(hours=4)).isoformat(),
                "event_type": "policy_review",
                "user_id": "admin-1",
                "ip_address": "10.0.0.15",
                "resource": "security:api_gateway",
                "action": "Reviewed firewall rules",
                "status": "success",
                "severity": "info",
                "details": {"change_ticket": "CHG-102"},
            }
        ]
        self.mfa_profiles: Dict[str, Dict[str, Any]] = {}
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.encryption_keys: Dict[str, Dict[str, Any]] = {}

        self.attack_patterns = {
            "sql_injection": [
                r"\bunion\s+select\b",
                r"\bor\b\s+'?\d+'?='?\d+'?",
                r"--",
                r";\s*drop\s+table",
            ],
            "xss": [
                r"<script",
                r"javascript:",
                r"onerror\s*=",
                r"onload\s*=",
            ],
            "path_traversal": [
                r"\.\./",
                r"\.\.\\",
                r"%2e%2e%2f",
            ],
            "command_injection": [
                r"(?:\|\||&&|;)\s*(?:wget|curl|bash|sh|powershell|cmd)",
                r"`.+`",
            ],
        }
        self.country_compliance = {
            "gdpr": [
                {"control": "Encryption for sensitive data", "passed": True, "weight": 25},
                {"control": "Audit trails enabled", "passed": True, "weight": 20},
                {"control": "Session management", "passed": True, "weight": 15},
                {"control": "MFA available for admins", "passed": False, "weight": 20},
                {"control": "Incident response process", "passed": True, "weight": 20},
            ],
            "hipaa": [
                {"control": "Encryption for regulated records", "passed": True, "weight": 25},
                {"control": "Access logging", "passed": True, "weight": 20},
                {"control": "Strong authentication", "passed": False, "weight": 20},
                {"control": "Backup readiness", "passed": True, "weight": 15},
                {"control": "Periodic audit review", "passed": True, "weight": 20},
            ],
        }

    async def run(self, payload: dict) -> dict:
        """Main shared-runtime entrypoint."""
        context = payload.get("context", {}) or {}
        action = payload.get("action") or context.get("action") or payload.get("meta", {}).get("action") or "status"

        if action == "status":
            return await self.status()
        if action == "config":
            return await self.config()
        if action == "dashboard":
            return await self.get_dashboard()
        if action == "analyze_request":
            request_data = context.get("request_data") or payload.get("request_data") or {}
            return await self.analyze_request(request_data)
        if action == "detect_brute_force":
            attempts = context.get("login_attempts") or payload.get("login_attempts") or []
            window_minutes = int(context.get("window_minutes") or payload.get("window_minutes") or 5)
            return await self.detect_brute_force(attempts, window_minutes)
        if action == "detect_ddos":
            traffic_patterns = context.get("traffic_patterns") or payload.get("traffic_patterns") or []
            return await self.detect_ddos(traffic_patterns)
        if action == "encrypt_sensitive_data":
            data = str(context.get("data") or payload.get("data") or "")
            purpose = str(context.get("purpose") or payload.get("purpose") or "general")
            return await self.encrypt_sensitive_data(data, purpose)
        if action == "decrypt_sensitive_data":
            encrypted_data = str(context.get("encrypted_data") or payload.get("encrypted_data") or "")
            key_id = str(context.get("key_id") or payload.get("key_id") or "")
            return await self.decrypt_sensitive_data(encrypted_data, key_id)
        if action == "hash_password":
            password = str(context.get("password") or payload.get("password") or "")
            return await self.hash_password(password)
        if action == "verify_password":
            password = str(context.get("password") or payload.get("password") or "")
            stored_hash = str(context.get("stored_hash") or payload.get("stored_hash") or "")
            salt = str(context.get("salt") or payload.get("salt") or "")
            return await self.verify_password(password, stored_hash, salt)
        if action == "setup_mfa":
            user_id = str(context.get("user_id") or payload.get("user_id") or "")
            return await self.setup_mfa(user_id)
        if action == "verify_mfa":
            user_id = str(context.get("user_id") or payload.get("user_id") or "")
            code = str(context.get("code") or payload.get("code") or "")
            return await self.verify_mfa(user_id, code)
        if action == "create_session":
            user_id = str(context.get("user_id") or payload.get("user_id") or "")
            ip = str(context.get("ip") or context.get("ip_address") or payload.get("ip") or payload.get("ip_address") or "")
            user_agent = str(context.get("user_agent") or payload.get("user_agent") or "unknown")
            return await self.create_session(user_id, ip, user_agent)
        if action == "validate_session":
            session_id = str(context.get("session_id") or payload.get("session_id") or "")
            ip = str(context.get("ip") or payload.get("ip") or "")
            return await self.validate_session(session_id, ip)
        if action == "check_ip_threat":
            ip = str(context.get("ip") or payload.get("ip") or "")
            return await self.check_ip_threat(ip)
        if action == "check_domain_threat":
            domain = str(context.get("domain") or payload.get("domain") or "")
            return await self.check_domain_threat(domain)
        if action == "recent_threats":
            hours = int(context.get("hours") or payload.get("hours") or 24)
            return await self.get_recent_threats(hours)
        if action == "audit_report":
            hours = int(context.get("hours") or payload.get("hours") or 24)
            return await self.get_audit_report(hours)
        if action == "gdpr_compliance":
            return await self.check_gdpr_compliance()
        if action == "hipaa_compliance":
            return await self.check_hipaa_compliance()

        return await self.status()

    async def process_message(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Parse natural-language requests into structured actions."""
        text = (message or "").strip().lower()
        context = context or {}

        if "dashboard" in text or "security posture" in text or "overview" in text:
            return await self.get_dashboard()
        if "gdpr" in text:
            return await self.check_gdpr_compliance()
        if "hipaa" in text:
            return await self.check_hipaa_compliance()
        if "encrypt" in text:
            data = str(context.get("data") or "sensitive payload")
            purpose = str(context.get("purpose") or "message_request")
            return await self.encrypt_sensitive_data(data, purpose)
        if "domain" in text or "phishing" in text:
            domain_match = re.search(r"([a-z0-9.-]+\.[a-z]{2,})", text)
            domain = domain_match.group(1) if domain_match else str(context.get("domain") or "gts-logistics-verify.com")
            return await self.check_domain_threat(domain)
        if "ip" in text or "address" in text:
            ip_match = re.search(r"\b\d{1,3}(?:\.\d{1,3}){3}\b", text)
            ip = ip_match.group(0) if ip_match else str(context.get("ip") or "45.123.45.67")
            return await self.check_ip_threat(ip)
        if "request" in text or "sql" in text or "xss" in text:
            request_data = context.get("request_data") or {
                "request_id": "REQ-MSG-001",
                "url": "/api/admin?user=1%20OR%20'1'='1",
                "params": {"user": "1 OR '1'='1"},
                "headers": {"user-agent": "curl/8.0"},
                "ip": "45.123.45.67",
            }
            return await self.analyze_request(request_data)
        return await self.status()

    async def status(self) -> dict:
        critical = sum(1 for event in self.security_events if event["severity"] == "critical")
        high = sum(1 for event in self.security_events if event["severity"] == "high")
        return {
            "ok": True,
            "bot": self.name,
            "display_name": self.display_name,
            "version": self.version,
            "mode": self.mode,
            "is_active": self.is_active,
            "security_status": {
                "threat_level": "high" if critical else "medium" if high else "low",
                "active_alerts": len([event for event in self.security_events if event["status"] in {"detected", "investigating", "contained"}]),
                "blocked_ips": len(self.ip_lists["blacklist"]),
            },
            "message": "Security controls are active and monitoring all registered bots.",
        }

    async def config(self) -> dict:
        return {
            "name": self.name,
            "display_name": self.display_name,
            "description": self.description,
            "version": self.version,
            "mode": self.mode,
            "capabilities": [
                "dashboard",
                "analyze_request",
                "detect_brute_force",
                "detect_ddos",
                "encrypt_sensitive_data",
                "setup_mfa",
                "create_session",
                "check_ip_threat",
                "check_domain_threat",
                "audit_report",
                "gdpr_compliance",
                "hipaa_compliance",
            ],
        }

    async def get_dashboard(self) -> Dict[str, Any]:
        recent_threats = sorted(self.threat_indicators, key=lambda item: item["last_seen"], reverse=True)
        audit_report = await self.get_audit_report(24)
        gdpr = await self.check_gdpr_compliance()
        hipaa = await self.check_hipaa_compliance()
        open_events = [event for event in self.security_events if event["status"] in {"detected", "investigating", "contained"}]
        failed_logins = sum(1 for attempt in self.login_attempts if not attempt.get("success"))

        return {
            "ok": True,
            "quick_stats": {
                "events_today": len(self.security_events),
                "critical_events": sum(1 for event in self.security_events if event["severity"] == "critical"),
                "failed_logins_24h": failed_logins,
                "blocked_ips": len(self.ip_lists["blacklist"]),
                "active_threats": len(recent_threats),
                "open_events": len(open_events),
            },
            "recent_threats": copy.deepcopy(recent_threats[:5]),
            "recent_events": copy.deepcopy(sorted(self.security_events, key=lambda item: item["detected_at"], reverse=True)[:5]),
            "compliance": {
                "gdpr": gdpr["status"],
                "hipaa": hipaa["status"],
            },
            "audit_summary": audit_report["summary"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    async def analyze_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        threats: List[Dict[str, Any]] = []
        url = str(request_data.get("url") or "")
        params = request_data.get("params") or {}
        headers = request_data.get("headers") or {}
        ip = str(request_data.get("ip") or "")

        for attack_type, patterns in self.attack_patterns.items():
            for pattern in patterns:
                if re.search(pattern, url, re.IGNORECASE):
                    threats.append({"type": attack_type, "location": "url", "severity": "high", "pattern": pattern})
                    break

        for key, value in params.items():
            if not isinstance(value, str):
                continue
            for attack_type, patterns in self.attack_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, value, re.IGNORECASE):
                        threats.append({"type": attack_type, "location": f"param:{key}", "severity": "high", "pattern": pattern})
                        break

        user_agent = str(headers.get("user-agent") or headers.get("User-Agent") or "")
        if user_agent and ("curl" in user_agent.lower() or len(user_agent) < 8):
            threats.append({"type": "suspicious_user_agent", "location": "header:user-agent", "severity": "low", "value": user_agent})

        ip_assessment = await self.check_ip_threat(ip) if ip else {"is_malicious": False, "risk_score": 0}
        if ip_assessment.get("is_malicious"):
            threats.append({"type": "malicious_ip", "location": "ip", "severity": "high", "value": ip, "risk_score": ip_assessment["risk_score"]})

        threat_level = self._threat_level(threats)
        result = {
            "ok": True,
            "request_id": request_data.get("request_id") or f"REQ-{secrets.token_hex(4)}",
            "has_threats": bool(threats),
            "threat_level": threat_level,
            "threats": threats,
            "recommended_action": self._recommended_action(threat_level),
        }
        if threats:
            self._record_event(
                event_type="intrusion_attempt",
                severity=threat_level,
                source_ip=ip or None,
                description=f"Detected {len(threats)} threat indicators in incoming request.",
                details=result,
            )
        return result

    async def detect_brute_force(self, login_attempts: List[Dict[str, Any]], window_minutes: int = 5) -> Dict[str, Any]:
        attempts = copy.deepcopy(login_attempts)
        suspicious_ips: List[Dict[str, Any]] = []
        grouped: Dict[str, List[datetime]] = {}
        failures: Dict[str, int] = {}

        for attempt in attempts:
            ip = str(attempt.get("ip_address") or "")
            timestamp = attempt.get("attempt_time")
            if isinstance(timestamp, str):
                parsed = datetime.fromisoformat(timestamp)
            else:
                parsed = timestamp
            if not ip or not parsed:
                continue
            grouped.setdefault(ip, []).append(parsed)
            if not attempt.get("success"):
                failures[ip] = failures.get(ip, 0) + 1

        for ip, timestamps in grouped.items():
            if len(timestamps) < 5:
                continue
            window = max(timestamps) - min(timestamps)
            if window.total_seconds() <= window_minutes * 60 and failures.get(ip, 0) >= 5:
                suspicious_ips.append(
                    {
                        "ip": ip,
                        "attempts_count": len(timestamps),
                        "failed_attempts": failures.get(ip, 0),
                        "time_window_seconds": round(window.total_seconds(), 2),
                    }
                )

        return {
            "ok": True,
            "is_brute_force": bool(suspicious_ips),
            "suspicious_ips": suspicious_ips,
            "total_attempts": len(attempts),
            "window_minutes": window_minutes,
        }

    async def detect_ddos(self, traffic_patterns: List[Dict[str, Any]]) -> Dict[str, Any]:
        if len(traffic_patterns) < 10:
            return {"ok": True, "is_ddos": False, "confidence": 0, "indicators": [], "stats": {}}

        timestamps: List[datetime] = []
        ips = set()
        user_agents = set()
        for item in traffic_patterns:
            timestamp = item.get("timestamp")
            if isinstance(timestamp, str):
                parsed = datetime.fromisoformat(timestamp)
            else:
                parsed = timestamp
            if parsed:
                timestamps.append(parsed)
            if item.get("ip"):
                ips.add(item["ip"])
            if item.get("user_agent"):
                user_agents.add(item["user_agent"])

        duration = max((max(timestamps) - min(timestamps)).total_seconds(), 1) if timestamps else 1
        requests_per_second = len(traffic_patterns) / duration
        indicators: List[str] = []
        if requests_per_second > 100:
            indicators.append(f"High request rate detected: {requests_per_second:.2f} req/s")
        if len(ips) > 100 and len(user_agents) < 10:
            indicators.append("Many source IPs share very few user agents")

        return {
            "ok": True,
            "is_ddos": bool(indicators),
            "confidence": min(len(indicators) * 45, 100),
            "indicators": indicators,
            "stats": {
                "requests_per_second": round(requests_per_second, 2),
                "unique_ips": len(ips),
                "unique_user_agents": len(user_agents),
            },
        }

    async def encrypt_sensitive_data(self, data: str, purpose: str) -> Dict[str, Any]:
        key_id = self._ensure_key(purpose)
        key_material = self.encryption_keys[key_id]["key"]
        payload = data.encode("utf-8")
        combined = bytes(payload[i] ^ key_material[i % len(key_material)] for i in range(len(payload)))
        encrypted_data = base64.urlsafe_b64encode(combined).decode("utf-8")
        return {
            "ok": True,
            "key_id": key_id,
            "encrypted_data": encrypted_data,
            "algorithm": "xor+base64-demo",
            "purpose": purpose,
        }

    async def decrypt_sensitive_data(self, encrypted_data: str, key_id: str) -> Dict[str, Any]:
        key = self.encryption_keys.get(key_id)
        if not key:
            return {"ok": False, "error": "Unknown key id"}

        decoded = base64.urlsafe_b64decode(encrypted_data.encode("utf-8"))
        plain = bytes(decoded[i] ^ key["key"][i % len(key["key"])] for i in range(len(decoded)))
        return {
            "ok": True,
            "decrypted_data": plain.decode("utf-8"),
            "key_id": key_id,
        }

    async def hash_password(self, password: str) -> Dict[str, Any]:
        salt = os.urandom(16)
        digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100_000)
        return {
            "ok": True,
            "hash": base64.urlsafe_b64encode(digest).decode("utf-8"),
            "salt": base64.b64encode(salt).decode("utf-8"),
            "algorithm": "PBKDF2-HMAC-SHA256",
            "iterations": 100_000,
        }

    async def verify_password(self, password: str, stored_hash: str, salt: str) -> Dict[str, Any]:
        digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), base64.b64decode(salt), 100_000)
        valid = base64.urlsafe_b64encode(digest).decode("utf-8") == stored_hash
        return {"ok": True, "valid": valid}

    async def setup_mfa(self, user_id: str) -> Dict[str, Any]:
        secret = secrets.token_urlsafe(16)
        backup_codes = [f"{secrets.randbelow(10**8):08d}" for _ in range(8)]
        profile = {
            "user_id": user_id,
            "secret": secret,
            "backup_codes": backup_codes,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        self.mfa_profiles[user_id] = profile
        self._log_audit("mfa_setup", user_id=user_id, severity="info", details={"backup_codes": len(backup_codes)})
        return {
            "ok": True,
            "user_id": user_id,
            "secret": secret,
            "backup_codes": backup_codes,
            "instructions": "Add the secret to your authenticator app and keep backup codes offline.",
        }

    async def verify_mfa(self, user_id: str, code: str) -> Dict[str, Any]:
        profile = self.mfa_profiles.get(user_id)
        if not profile:
            return {"ok": False, "verified": False, "error": "MFA is not configured for this user"}

        verified = code == profile["secret"][-6:] or code in profile["backup_codes"]
        if verified and code in profile["backup_codes"]:
            profile["backup_codes"].remove(code)
        self._log_audit(
            "mfa_verify",
            user_id=user_id,
            severity="info" if verified else "medium",
            status="success" if verified else "failure",
        )
        return {"ok": True, "verified": verified}

    async def create_session(self, user_id: str, ip: str, user_agent: str) -> Dict[str, Any]:
        session_id = hashlib.sha256(f"{user_id}:{ip}:{datetime.now(timezone.utc).isoformat()}".encode("utf-8")).hexdigest()
        expires_at = datetime.now(timezone.utc) + timedelta(hours=8)
        self.active_sessions[session_id] = {
            "user_id": user_id,
            "ip": ip,
            "user_agent": user_agent,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "expires_at": expires_at.isoformat(),
            "last_activity": datetime.now(timezone.utc).isoformat(),
        }
        self._log_audit("session_created", user_id=user_id, ip_address=ip, severity="info", details={"session_id": session_id[:12]})
        return {"ok": True, "session_id": session_id, "expires_at": expires_at.isoformat(), "max_age": 28800}

    async def validate_session(self, session_id: str, ip: str) -> Dict[str, Any]:
        session = self.active_sessions.get(session_id)
        if not session:
            return {"ok": True, "valid": False}
        if datetime.fromisoformat(session["expires_at"]) < datetime.now(timezone.utc):
            self.active_sessions.pop(session_id, None)
            return {"ok": True, "valid": False}
        session["last_activity"] = datetime.now(timezone.utc).isoformat()
        return {"ok": True, "valid": True, "ip_changed": session["ip"] != ip}

    async def check_ip_threat(self, ip: str) -> Dict[str, Any]:
        threats = [copy.deepcopy(item) for item in self.threat_indicators if item["indicator_type"] == "ip" and item["indicator"] == ip]
        if ip.startswith("45.") or ip.startswith("185."):
            threats.append(
                {
                    "threat_id": f"THR-GEO-{ip.replace('.', '')[:8]}",
                    "indicator_type": "ip",
                    "indicator": ip,
                    "threat_type": "suspicious_origin",
                    "confidence": 40,
                    "severity": "medium",
                    "source": "pattern",
                    "recommended_action": "Monitor and challenge with MFA",
                }
            )
        risk_score = min(sum(item.get("confidence", 0) for item in threats), 100)
        return {
            "ok": True,
            "ip": ip,
            "is_malicious": bool(threats),
            "threat_count": len(threats),
            "threats": threats,
            "risk_score": risk_score,
            "checked_at": datetime.now(timezone.utc).isoformat(),
        }

    async def check_domain_threat(self, domain: str) -> Dict[str, Any]:
        threats = [copy.deepcopy(item) for item in self.threat_indicators if item["indicator_type"] == "domain" and item["indicator"] == domain]
        for suffix in (".xyz", ".top", ".work"):
            if domain.endswith(suffix):
                threats.append(
                    {
                        "threat_id": f"THR-TLD-{suffix[1:]}",
                        "indicator_type": "domain",
                        "indicator": domain,
                        "threat_type": "suspicious_tld",
                        "confidence": 30,
                        "severity": "low",
                        "source": "pattern",
                        "recommended_action": "Review sender reputation",
                    }
                )
                break
        risk_score = min(sum(item.get("confidence", 0) for item in threats), 100)
        return {
            "ok": True,
            "domain": domain,
            "is_malicious": bool(threats),
            "threats": threats,
            "risk_score": risk_score,
            "checked_at": datetime.now(timezone.utc).isoformat(),
        }

    async def get_recent_threats(self, hours: int = 24) -> Dict[str, Any]:
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
        threats = [
            copy.deepcopy(item)
            for item in self.threat_indicators
            if datetime.fromisoformat(item["last_seen"]) >= cutoff
        ]
        threats.sort(key=lambda item: item["last_seen"], reverse=True)
        return {"ok": True, "hours": hours, "threats": threats}

    async def get_audit_report(self, hours: int = 24) -> Dict[str, Any]:
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
        relevant = [entry for entry in self.audit_log if datetime.fromisoformat(entry["timestamp"]) >= cutoff]
        by_severity: Dict[str, int] = {}
        by_type: Dict[str, int] = {}
        for entry in relevant:
            by_severity[entry["severity"]] = by_severity.get(entry["severity"], 0) + 1
            by_type[entry["event_type"]] = by_type.get(entry["event_type"], 0) + 1
        return {
            "ok": True,
            "summary": {
                "period_hours": hours,
                "total_events": len(relevant),
                "by_severity": by_severity,
                "by_type": by_type,
            },
            "events": copy.deepcopy(relevant[-25:]),
        }

    async def check_gdpr_compliance(self) -> Dict[str, Any]:
        return self._compliance_result("gdpr", "GDPR")

    async def check_hipaa_compliance(self) -> Dict[str, Any]:
        return self._compliance_result("hipaa", "HIPAA")

    def _compliance_result(self, key: str, standard: str) -> Dict[str, Any]:
        controls = self.country_compliance[key]
        score = sum(item["weight"] for item in controls if item["passed"])
        findings = [
            {
                "requirement": item["control"],
                "status": "compliant" if item["passed"] else "attention_required",
            }
            for item in controls
        ]
        return {
            "ok": True,
            "standard": standard,
            "overall_score": score,
            "findings": findings,
            "status": "compliant" if score >= 70 else "non_compliant",
            "checked_at": datetime.now(timezone.utc).isoformat(),
        }

    def _ensure_key(self, purpose: str) -> str:
        for key_id, meta in self.encryption_keys.items():
            if meta["purpose"] == purpose:
                return key_id
        key_id = f"KEY{datetime.now(timezone.utc).strftime('%y%m%d%H%M%S')}"
        self.encryption_keys[key_id] = {
            "key": os.urandom(16),
            "purpose": purpose,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "expires_at": (datetime.now(timezone.utc) + timedelta(days=90)).isoformat(),
        }
        return key_id

    def _record_event(
        self,
        event_type: str,
        severity: str,
        description: str,
        source_ip: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        event_id = f"SEC{datetime.now(timezone.utc).strftime('%y%m%d%H%M%S')}"
        self.security_events.append(
            {
                "event_id": event_id,
                "event_type": event_type,
                "severity": severity,
                "source_ip": source_ip,
                "source_bot": None,
                "description": description,
                "status": "detected",
                "detected_at": datetime.now(timezone.utc).isoformat(),
                "actions_taken": ["Investigate"],
                "details": details or {},
            }
        )
        self._log_audit(
            action=event_type,
            ip_address=source_ip,
            severity=severity,
            details={"description": description},
        )

    def _log_audit(
        self,
        action: str,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        severity: str = "info",
        status: str = "success",
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        digest = hashlib.sha256(f"{action}:{datetime.now(timezone.utc).isoformat()}".encode("utf-8")).hexdigest()[:16]
        self.audit_log.append(
            {
                "log_id": digest,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "event_type": action,
                "user_id": user_id,
                "ip_address": ip_address,
                "resource": "security:runtime",
                "action": action,
                "status": status,
                "severity": severity,
                "details": details or {},
            }
        )

    def _threat_level(self, threats: List[Dict[str, Any]]) -> str:
        if not threats:
            return "none"
        severity_rank = {"low": 1, "medium": 2, "high": 3, "critical": 4}
        return max((item.get("severity", "low") for item in threats), key=lambda level: severity_rank.get(level, 0))

    def _recommended_action(self, threat_level: str) -> str:
        actions = {
            "none": "No action required.",
            "low": "Monitor the source and keep logging enabled.",
            "medium": "Require additional verification and review the request.",
            "high": "Block the source, open an incident, and notify security owners.",
            "critical": "Block immediately, isolate the affected flow, and escalate response.",
        }
        return actions.get(threat_level, "Review manually.")
