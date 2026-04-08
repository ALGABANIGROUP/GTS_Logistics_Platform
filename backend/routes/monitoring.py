# backend/routes/monitoring.py
"""
Monitoring and analytics routes
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging

from backend.monitoring.sentry_integration import SentryIntegration
from backend.monitoring.metrics_collector import MetricsCollector
from backend.monitoring.alert_manager import AlertManager, AlertSeverity, AlertStatus
from backend.security.auth import get_current_user
from backend.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/monitoring", tags=["monitoring"])

# Initialize monitoring components
sentry = SentryIntegration()
metrics = MetricsCollector()
alerts = AlertManager()

# Import email service for backward compatibility
try:
    from backend.services.email_scheduler import is_polling_running, last_poll_cycle_at
except ImportError:
    def is_polling_running():
        return False
    def last_poll_cycle_at():
        return None

@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "services": {
            "database": "connected",  # TODO: Add actual DB health check
            "redis": "connected",     # TODO: Add Redis health check
            "external_apis": "operational"  # TODO: Add external API checks
        }
    }

@router.get("/health/detailed")
async def detailed_health_check() -> Dict[str, Any]:
    """Detailed health check with system metrics"""
    try:
        system_metrics = metrics.get_metrics(hours=1)

        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "uptime": system_metrics.get("uptime", 0),
            "system": system_metrics.get("aggregates", {}),
            "database": {
                "status": "connected",
                "pool_size": metrics.get_db_pool_size(),
                "active_connections": metrics.get_active_db_connections()
            },
            "application": {
                "request_count": metrics.get_request_count(),
                "error_count": metrics.get_error_count(),
                "active_users": metrics.get_active_users(),
                "avg_response_time": metrics.get_average_response_time()
            }
        }
    except Exception as e:
        logger.error(f"Health check error: {e}")
        raise HTTPException(status_code=500, detail="Health check failed")

@router.get("/metrics")
async def get_metrics(
    metric_name: Optional[str] = Query(None, description="Specific metric to retrieve"),
    hours: int = Query(24, description="Hours of history to retrieve")
) -> Dict[str, Any]:
    """Get system metrics"""
    try:
        return metrics.get_metrics(metric_name, hours)
    except Exception as e:
        logger.error(f"Metrics retrieval error: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve metrics")

@router.get("/metrics/system")
async def get_system_metrics(hours: int = 24) -> Dict[str, Any]:
    """Get system-level metrics"""
    try:
        return metrics.get_metrics("system", hours)
    except Exception as e:
        logger.error(f"System metrics error: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve system metrics")

@router.get("/alerts")
async def get_alerts(
    status: Optional[str] = Query(None, description="Filter by alert status"),
    severity: Optional[str] = Query(None, description="Filter by alert severity"),
    source: Optional[str] = Query(None, description="Filter by alert source")
) -> Dict[str, Any]:
    """Get alerts with optional filtering"""
    try:
        status_filter = AlertStatus(status) if status else None
        severity_filter = AlertSeverity(severity) if severity else None

        alerts_list = alerts.get_alerts(status_filter, severity_filter, source)

        return {
            "alerts": alerts_list,
            "total": len(alerts_list),
            "active": len([a for a in alerts_list if a["status"] == "active"]),
            "acknowledged": len([a for a in alerts_list if a["status"] == "acknowledged"]),
            "resolved": len([a for a in alerts_list if a["status"] == "resolved"])
        }
    except Exception as e:
        logger.error(f"Alerts retrieval error: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve alerts")

@router.get("/alerts/history")
async def get_alert_history(days: int = 7) -> Dict[str, Any]:
    """Get alert history"""
    try:
        history = alerts.get_alert_history(days)
        return {
            "history": history,
            "total": len(history),
            "period_days": days
        }
    except Exception as e:
        logger.error(f"Alert history error: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve alert history")

@router.post("/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(
    alert_id: str,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Acknowledge an alert"""
    try:
        await alerts.acknowledge_alert(alert_id)
        return {"message": f"Alert {alert_id} acknowledged", "alert_id": alert_id}
    except Exception as e:
        logger.error(f"Alert acknowledge error: {e}")
        raise HTTPException(status_code=500, detail="Failed to acknowledge alert")

@router.post("/alerts/{alert_id}/resolve")
async def resolve_alert(
    alert_id: str,
    resolution_note: Optional[str] = Query(None, description="Resolution note"),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Resolve an alert"""
    try:
        await alerts.resolve_alert(alert_id, resolution_note)
        return {"message": f"Alert {alert_id} resolved", "alert_id": alert_id}
    except Exception as e:
        logger.error(f"Alert resolve error: {e}")
        raise HTTPException(status_code=500, detail="Failed to resolve alert")

@router.get("/sentry/issues")
async def get_sentry_issues(
    limit: int = Query(50, description="Maximum number of issues to return"),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get recent Sentry issues"""
    try:
        # This would integrate with Sentry API in a real implementation
        return {
            "issues": [],
            "total": 0,
            "limit": limit,
            "note": "Sentry integration requires API key configuration"
        }
    except Exception as e:
        logger.error(f"Sentry issues error: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve Sentry issues")

@router.post("/sentry/test")
async def test_sentry_integration() -> Dict[str, Any]:
    """Test Sentry integration by sending a test error"""
    try:
        sentry.capture_message("Test message from monitoring endpoint", level="info")
        return {"message": "Test event sent to Sentry"}
    except Exception as e:
        logger.error(f"Sentry test error: {e}")
        raise HTTPException(status_code=500, detail="Failed to send test event to Sentry")

@router.get("/debug/info")
async def get_debug_info(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get debug information for troubleshooting"""
    try:
        return {
            "timestamp": datetime.now().isoformat(),
            "user": {
                "id": current_user.id,
                "email": current_user.email,
                "role": current_user.role
            },
            "system": {
                "python_version": __import__("sys").version,
                "platform": __import__("platform").platform(),
                "uptime": metrics.aggregates.get("uptime", 0)
            },
            "monitoring": {
                "sentry_enabled": sentry.is_enabled(),
                "metrics_collected": len(metrics.metrics),
                "active_alerts": len(alerts.get_alerts(AlertStatus.ACTIVE))
            }
        }
    except Exception as e:
        logger.error(f"Debug info error: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve debug info")

@router.get("/email/status")
async def get_email_status() -> dict:
    """Legacy email status endpoint for backward compatibility"""
    return {
        "is_running": is_polling_running(),
        "status": "active" if is_polling_running() else "inactive",
        "last_cycle_at": last_poll_cycle_at(),
    }

@router.post("/maintenance/cleanup")
async def cleanup_old_data(
    days: int = Query(30, description="Days of data to keep"),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Clean up old monitoring data"""
    try:
        if current_user.role not in ["admin", "system_admin"]:
            raise HTTPException(status_code=403, detail="Insufficient permissions")

        alerts.cleanup_old_alerts(days)

        return {
            "message": f"Cleaned up data older than {days} days",
            "alerts_cleaned": "completed"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Cleanup error: {e}")
        raise HTTPException(status_code=500, detail="Failed to cleanup old data")
