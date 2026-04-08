# backend/routes/security_bot.py
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging
from pydantic import BaseModel, Field

from backend.database.session import get_async_session
from backend.security.auth import get_current_user
from backend.models.user import User
from backend.models.audit_log import AuditLog

router = APIRouter(prefix="/security", tags=["Security Manager"])
logger = logging.getLogger(__name__)


# ==================== Models ====================
class SecurityAlert(BaseModel):
    id: str
    title: str
    severity: str  # critical, high, medium, low
    category: str  # login, permission, data, network, system
    message: str
    source_ip: Optional[str]
    user_email: Optional[str]
    timestamp: str
    status: str  # new, investigating, resolved, false_positive
    assigned_to: Optional[str]


class SecurityScan(BaseModel):
    id: str
    name: str
    type: str
    status: str  # pending, running, completed, failed
    progress: int
    started_at: str
    completed_at: Optional[str]
    findings: List[Dict[str, Any]]


class SecurityMetrics(BaseModel):
    total_alerts: int
    critical_alerts: int
    high_alerts: int
    resolved_alerts: int
    active_sessions: int
    failed_logins_24h: int
    suspicious_activities: int
    last_scan: Optional[str]


# ==================== Mock Data (سيتم استبدالها بقاعدة بيانات حقيقية) ====================
SECURITY_ALERTS = [
    {
        "id": "alert_001",
        "title": "Multiple failed login attempts",
        "severity": "high",
        "category": "login",
        "message": "5 failed login attempts from IP 192.168.1.100 in 5 minutes",
        "source_ip": "192.168.1.100",
        "user_email": "unknown",
        "timestamp": datetime.now().isoformat(),
        "status": "investigating",
        "assigned_to": "Security Bot"
    },
    {
        "id": "alert_002",
        "title": "Suspicious API access pattern",
        "severity": "medium",
        "category": "api",
        "message": "Unusual API request pattern detected from user admin@gts.com",
        "source_ip": "10.0.0.45",
        "user_email": "admin@gts.com",
        "timestamp": (datetime.now() - timedelta(hours=2)).isoformat(),
        "status": "new",
        "assigned_to": None
    },
    {
        "id": "alert_003",
        "title": "Database query timeout",
        "severity": "low",
        "category": "database",
        "message": "Slow query detected on users table (took 5.2 seconds)",
        "source_ip": None,
        "user_email": None,
        "timestamp": (datetime.now() - timedelta(hours=5)).isoformat(),
        "status": "resolved",
        "assigned_to": "System Admin"
    },
    {
        "id": "alert_004",
        "title": "Unauthorized access attempt",
        "severity": "critical",
        "category": "permission",
        "message": "User 'test@example.com' attempted to access admin endpoint",
        "source_ip": "203.0.113.55",
        "user_email": "test@example.com",
        "timestamp": (datetime.now() - timedelta(hours=3)).isoformat(),
        "status": "new",
        "assigned_to": None
    }
]

SECURITY_SCANS = [
    {
        "id": "scan_001",
        "name": "Full System Security Scan",
        "type": "full",
        "status": "completed",
        "progress": 100,
        "started_at": (datetime.now() - timedelta(hours=12)).isoformat(),
        "completed_at": (datetime.now() - timedelta(hours=11, minutes=30)).isoformat(),
        "findings": [
            {"severity": "high", "description": "Outdated SSL certificate on api.gtsdispatcher.com", "remediation": "Renew SSL certificate"},
            {"severity": "medium", "description": "Missing security headers on /api/v1 endpoint", "remediation": "Add security headers"}
        ]
    },
    {
        "id": "scan_002",
        "name": "Vulnerability Assessment",
        "type": "vulnerability",
        "status": "running",
        "progress": 65,
        "started_at": (datetime.now() - timedelta(hours=1)).isoformat(),
        "completed_at": None,
        "findings": []
    }
]

SECURITY_METRICS = {
    "total_alerts": len(SECURITY_ALERTS),
    "critical_alerts": len([a for a in SECURITY_ALERTS if a["severity"] == "critical"]),
    "high_alerts": len([a for a in SECURITY_ALERTS if a["severity"] == "high"]),
    "resolved_alerts": len([a for a in SECURITY_ALERTS if a["status"] == "resolved"]),
    "active_sessions": 42,
    "failed_logins_24h": 12,
    "suspicious_activities": 8,
    "last_scan": SECURITY_SCANS[0]["completed_at"]
}


# ==================== API Endpoints ====================

@router.get("/dashboard")
async def get_security_dashboard(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get security dashboard data"""
    return {
        "metrics": SECURITY_METRICS,
        "recent_alerts": SECURITY_ALERTS[:5],
        "active_scans": [s for s in SECURITY_SCANS if s["status"] in ["pending", "running"]],
        "system_status": {
            "firewall": "active",
            "antivirus": "active",
            "intrusion_detection": "active",
            "last_audit": (datetime.now() - timedelta(days=1)).isoformat()
        }
    }


@router.get("/alerts")
async def get_security_alerts(
    severity: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get security alerts with filtering"""
    alerts = SECURITY_ALERTS.copy()

    if severity:
        alerts = [a for a in alerts if a["severity"] == severity]
    if status:
        alerts = [a for a in alerts if a["status"] == status]

    alerts.sort(key=lambda x: x["timestamp"], reverse=True)

    return {
        "alerts": alerts[:limit],
        "total": len(alerts),
        "by_severity": {
            "critical": len([a for a in alerts if a["severity"] == "critical"]),
            "high": len([a for a in alerts if a["severity"] == "high"]),
            "medium": len([a for a in alerts if a["severity"] == "medium"]),
            "low": len([a for a in alerts if a["severity"] == "low"])
        }
    }


@router.get("/alerts/{alert_id}")
async def get_alert_details(
    alert_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get detailed information about a specific alert"""
    alert = next((a for a in SECURITY_ALERTS if a["id"] == alert_id), None)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert


@router.patch("/alerts/{alert_id}/status")
async def update_alert_status(
    alert_id: str,
    status: str,
    notes: Optional[str] = None,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Update alert status (investigating, resolved, false_positive)"""
    alert = next((a for a in SECURITY_ALERTS if a["id"] == alert_id), None)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    alert["status"] = status
    alert["resolved_at"] = datetime.now().isoformat() if status == "resolved" else None
    alert["resolved_by"] = current_user.get("email")

    logger.info(f"Alert {alert_id} status updated to {status} by {current_user.get('email')}")

    return {"message": "Alert status updated", "alert": alert}


@router.post("/scan/start")
async def start_security_scan(
    scan_type: str = "quick",
    background_tasks: BackgroundTasks = BackgroundTasks(),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Start a new security scan"""
    new_scan = {
        "id": f"scan_{len(SECURITY_SCANS) + 1:03d}",
        "name": f"{scan_type.capitalize()} Security Scan",
        "type": scan_type,
        "status": "running",
        "progress": 0,
        "started_at": datetime.now().isoformat(),
        "completed_at": None,
        "findings": []
    }

    SECURITY_SCANS.append(new_scan)

    # Simulate scan progress
    background_tasks.add_task(simulate_scan_progress, new_scan["id"])

    return {"message": "Security scan started", "scan_id": new_scan["id"]}


async def simulate_scan_progress(scan_id: str):
    """Simulate scan progress (in production, this would be real scanning)"""
    import asyncio
    scan = next((s for s in SECURITY_SCANS if s["id"] == scan_id), None)
    if not scan:
        return

    for progress in [10, 25, 45, 60, 75, 85, 95, 100]:
        await asyncio.sleep(2)
        scan["progress"] = progress

        if progress == 100:
            scan["status"] = "completed"
            scan["completed_at"] = datetime.now().isoformat()
            scan["findings"] = [
                {"severity": "low", "description": "No critical vulnerabilities found", "remediation": None}
            ]


@router.get("/scans")
async def get_security_scans(
    limit: int = 20,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get list of security scans"""
    scans = SECURITY_SCANS.copy()
    scans.sort(key=lambda x: x["started_at"], reverse=True)
    return {"scans": scans[:limit], "total": len(scans)}


@router.get("/scans/{scan_id}")
async def get_scan_details(
    scan_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get detailed information about a security scan"""
    scan = next((s for s in SECURITY_SCANS if s["id"] == scan_id), None)
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    return scan


@router.get("/metrics")
async def get_security_metrics(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get security metrics summary"""
    return SECURITY_METRICS


@router.get("/sessions/active")
async def get_active_sessions(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get active user sessions"""
    return {
        "active_sessions": [
            {"user": "admin@gts.com", "ip": "192.168.1.1", "last_activity": datetime.now().isoformat(), "device": "Chrome on Windows"},
            {"user": "manager@gts.com", "ip": "192.168.1.2", "last_activity": (datetime.now() - timedelta(minutes=5)).isoformat(), "device": "Safari on Mac"},
            {"user": "dispatcher@gts.com", "ip": "192.168.1.3", "last_activity": (datetime.now() - timedelta(minutes=15)).isoformat(), "device": "Firefox on Linux"}
        ],
        "total": 3
    }