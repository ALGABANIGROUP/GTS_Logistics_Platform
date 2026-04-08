# backend/routes/system_manager_bot.py
from fastapi import APIRouter, HTTPException, Depends, status, Query, BackgroundTasks
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging
import psutil
import platform
import asyncio
from pydantic import BaseModel, Field

from backend.database.session import get_async_session
from backend.security.auth import get_current_user
from backend.models.user import User

router = APIRouter(tags=["System Manager Bot"])
logger = logging.getLogger(__name__)


# ==================== Models ====================
class SystemHealth(BaseModel):
    cpu_percent: float
    memory_percent: float
    memory_used_gb: float
    memory_total_gb: float
    disk_percent: float
    disk_free_gb: float
    disk_total_gb: float
    uptime_seconds: float
    database_status: str
    database_response_time: int
    active_bots: int
    total_bots: int


class RoleDistribution(BaseModel):
    role: str
    count: int
    percentage: float


class UserAccess(BaseModel):
    id: int
    email: str
    full_name: str
    role: str
    assigned_bots: List[str]
    features: List[str]
    last_login: Optional[str]


# ==================== Mock Data (will be replaced with real database) ====================
SYSTEM_HEALTH = {
    "cpu_percent": 23.5,
    "cpu_cores": 8,
    "memory_percent": 45.2,
    "memory_used_gb": 7.2,
    "memory_total_gb": 16.0,
    "disk_percent": 58.3,
    "disk_free_gb": 245.5,
    "disk_total_gb": 500.0,
    "uptime_seconds": 3888000,  # 45 days
    "database_status": "healthy",
    "database_response_time": 45,
    "active_bots": 14,
    "total_bots": 14,
    "bot_names": [
        "AI Dispatcher", "AI Operations Manager", "AI Safety Manager",
        "AI Security Manager", "AI System Manager", "AI Legal Consultant",
        "AI Finance Bot", "AI Sales Bot", "AI Customer Service",
        "AI Documents Manager", "AI Information Coordinator", "AI Trainer Bot",
        "AI Partner Manager", "AI Maintenance Dev"
    ]
}

ROLE_DISTRIBUTION = [
    {"role": "super_admin", "count": 2, "percentage": 5.0},
    {"role": "admin", "count": 5, "percentage": 12.5},
    {"role": "manager", "count": 8, "percentage": 20.0},
    {"role": "dispatcher", "count": 12, "percentage": 30.0},
    {"role": "carrier", "count": 8, "percentage": 20.0},
    {"role": "shipper", "count": 5, "percentage": 12.5}
]

USERS_ACCESS = [
    {
        "id": 1,
        "email": "superadmin@gts.com",
        "full_name": "Super Administrator",
        "role": "super_admin",
        "assigned_bots": ["AI System Manager", "AI Security Manager", "AI Legal Consultant"],
        "features": ["all"],
        "last_login": "2026-04-05T10:30:00"
    },
    {
        "id": 2,
        "email": "admin@gts.com",
        "full_name": "System Administrator",
        "role": "admin",
        "assigned_bots": ["AI System Manager", "AI Operations Manager"],
        "features": ["user_management", "reporting"],
        "last_login": "2026-04-05T09:15:00"
    },
    {
        "id": 3,
        "email": "dispatcher@gts.com",
        "full_name": "Dispatcher",
        "role": "dispatcher",
        "assigned_bots": ["AI Dispatcher"],
        "features": ["dispatch", "tracking"],
        "last_login": "2026-04-05T08:00:00"
    },
    {
        "id": 4,
        "email": "carrier@fastfreight.com",
        "full_name": "Fast Freight Carrier",
        "role": "carrier",
        "assigned_bots": ["AI Freight Broker"],
        "features": ["load_board", "bidding"],
        "last_login": "2026-04-04T16:45:00"
    },
    {
        "id": 5,
        "email": "shipper@abcmfg.com",
        "full_name": "ABC Manufacturing",
        "role": "shipper",
        "assigned_bots": ["AI Freight Broker"],
        "features": ["shipment_creation", "tracking"],
        "last_login": "2026-04-04T14:20:00"
    }
]

FEATURE_FLAGS = [
    {"name": "ai_bots_advanced", "enabled": True, "description": "Advanced AI bot features"},
    {"name": "real_time_tracking", "enabled": True, "description": "Real-time shipment tracking"},
    {"name": "analytics_dashboard", "enabled": True, "description": "Advanced analytics"},
    {"name": "automated_reporting", "enabled": False, "description": "Automated report generation"},
    {"name": "api_access", "enabled": True, "description": "External API access"}
]

ACTIVE_ALERTS = [
    {"id": 1, "severity": "warning", "message": "Database connection pool at 85% capacity", "timestamp": datetime.now().isoformat()},
    {"id": 2, "severity": "info", "message": "SSL certificate expires in 30 days", "timestamp": datetime.now().isoformat()},
]

BOTTLENECKS = [
    {"id": 1, "component": "Database", "issue": "Slow query on shipments table", "impact": "Medium", "suggestion": "Add index on created_at"},
    {"id": 2, "component": "API Gateway", "issue": "Rate limiting near threshold", "impact": "Low", "suggestion": "Increase rate limit for premium users"}
]

RESOURCE_FORECAST = {
    "cpu_forecast": [25, 28, 32, 35, 38, 42, 45, 48, 52, 55],
    "memory_forecast": [45, 47, 50, 52, 55, 58, 60, 62, 65, 68],
    "forecast_days": 10,
    "recommendation": "Consider upgrading memory in 3 months"
}


# ==================== Helper Functions ====================
def get_real_system_metrics() -> Dict[str, Any]:
    """Get real system metrics"""
    try:
        metrics = {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "cpu_cores": psutil.cpu_count(logical=True),
            "memory_percent": psutil.virtual_memory().percent,
            "memory_used_gb": round(psutil.virtual_memory().used / (1024**3), 1),
            "memory_total_gb": round(psutil.virtual_memory().total / (1024**3), 1),
            "disk_percent": psutil.disk_usage('/').percent,
            "disk_free_gb": round(psutil.disk_usage('/').free / (1024**3), 1),
            "disk_total_gb": round(psutil.disk_usage('/').total / (1024**3), 1),
            "uptime_seconds": (datetime.now() - datetime.fromtimestamp(psutil.boot_time())).total_seconds(),
        }
        return metrics
    except Exception as e:
        logger.error(f"Failed to get system metrics: {e}")
        return SYSTEM_HEALTH


# ==================== API Endpoints ====================

@router.get("/health")
async def get_system_health(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get system health metrics"""
    
    user_role = current_user.get("role", "").lower()
    if user_role not in ["super_admin", "admin", "manager"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    real_metrics = get_real_system_metrics()
    
    return {
        "status": "healthy" if real_metrics["cpu_percent"] < 80 else "degraded",
        "timestamp": datetime.now().isoformat(),
        "metrics": {
            "cpu": {
                "percent": real_metrics["cpu_percent"],
                "cores": real_metrics["cpu_cores"],
                "status": "normal" if real_metrics["cpu_percent"] < 70 else "high"
            },
            "memory": {
                "percent": real_metrics["memory_percent"],
                "used_gb": real_metrics["memory_used_gb"],
                "total_gb": real_metrics["memory_total_gb"],
                "status": "normal" if real_metrics["memory_percent"] < 80 else "high"
            },
            "disk": {
                "percent": real_metrics["disk_percent"],
                "free_gb": real_metrics["disk_free_gb"],
                "total_gb": real_metrics["disk_total_gb"],
                "status": "normal" if real_metrics["disk_percent"] < 85 else "warning"
            },
            "database": {
                "status": SYSTEM_HEALTH["database_status"],
                "response_time_ms": SYSTEM_HEALTH["database_response_time"]
            },
            "uptime": {
                "seconds": real_metrics["uptime_seconds"],
                "days": round(real_metrics["uptime_seconds"] / 86400, 1),
                "human_readable": f"{int(real_metrics['uptime_seconds'] / 86400)} days, {int((real_metrics['uptime_seconds'] % 86400) / 3600)} hours"
            },
            "bots": {
                "active": SYSTEM_HEALTH["active_bots"],
                "total": SYSTEM_HEALTH["total_bots"],
                "names": SYSTEM_HEALTH["bot_names"]
            }
        }
    }


@router.get("/roles/distribution")
async def get_role_distribution(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get role distribution statistics"""
    
    user_role = current_user.get("role", "").lower()
    if user_role not in ["super_admin", "admin"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    return {
        "roles": ROLE_DISTRIBUTION,
        "total_users": sum(r["count"] for r in ROLE_DISTRIBUTION),
        "last_updated": datetime.now().isoformat()
    }


@router.get("/users/access")
async def get_user_access(
    page: int = 1,
    limit: int = 20,
    search: Optional[str] = None,
    role: Optional[str] = None,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get user access directory"""
    
    user_role = current_user.get("role", "").lower()
    if user_role not in ["super_admin", "admin"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    users = USERS_ACCESS.copy()
    
    if search:
        search_lower = search.lower()
        users = [
            u for u in users
            if search_lower in u["email"].lower()
            or search_lower in u["full_name"].lower()
        ]
    
    if role and role != "all":
        users = [u for u in users if u["role"] == role]
    
    total = len(users)
    start = (page - 1) * limit
    end = start + limit
    users = users[start:end]
    
    return {
        "users": users,
        "total": total,
        "page": page,
        "limit": limit
    }


@router.get("/features")
async def get_feature_flags(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get all feature flags"""
    
    return {
        "features": FEATURE_FLAGS,
        "total": len(FEATURE_FLAGS),
        "enabled": len([f for f in FEATURE_FLAGS if f["enabled"]])
    }


@router.post("/features/{feature_name}/toggle")
async def toggle_feature_flag(
    feature_name: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Toggle a feature flag (admin only)"""
    
    user_role = current_user.get("role", "").lower()
    if user_role not in ["super_admin", "admin"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    feature = next((f for f in FEATURE_FLAGS if f["name"] == feature_name), None)
    if not feature:
        raise HTTPException(status_code=404, detail="Feature not found")
    
    feature["enabled"] = not feature["enabled"]
    
    return {"message": f"Feature {feature_name} toggled", "enabled": feature["enabled"]}


@router.get("/alerts/active")
async def get_active_alerts(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get active system alerts"""
    
    return {
        "alerts": ACTIVE_ALERTS,
        "total": len(ACTIVE_ALERTS),
        "critical": len([a for a in ACTIVE_ALERTS if a["severity"] == "critical"]),
        "warning": len([a for a in ACTIVE_ALERTS if a["severity"] == "warning"])
    }


@router.get("/bottlenecks")
async def get_bottlenecks(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get system bottlenecks"""
    
    user_role = current_user.get("role", "").lower()
    if user_role not in ["super_admin", "admin"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    return {
        "bottlenecks": BOTTLENECKS,
        "total": len(BOTTLENECKS)
    }


@router.get("/forecast")
async def get_resource_forecast(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get resource usage forecast"""
    
    return RESOURCE_FORECAST


@router.post("/sql/analyze")
async def analyze_sql_query(
    query: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Analyze SQL query for optimization suggestions"""
    
    user_role = current_user.get("role", "").lower()
    if user_role not in ["super_admin", "admin"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Simple query analysis
    suggestions = []
    
    if "SELECT *" in query.upper():
        suggestions.append("Avoid SELECT * - specify only needed columns")
    if "NOT IN" in query.upper():
        suggestions.append("Consider using NOT EXISTS instead of NOT IN for better performance")
    if "WHERE" in query.upper() and "INDEX" not in query.upper():
        suggestions.append("Ensure proper indexes exist on WHERE clause columns")
    
    return {
        "query": query,
        "analysis": {
            "complexity": "medium" if len(query) > 100 else "low",
            "estimated_cost": len(query) // 10,
            "suggestions": suggestions if suggestions else ["Query looks optimal"],
            "optimized_version": query.replace("SELECT *", "SELECT id, customer_id, status") if "SELECT *" in query.upper() else None
        }
    }


@router.get("/dashboard")
async def get_system_dashboard(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get complete system dashboard data"""
    
    user_role = current_user.get("role", "").lower()
    if user_role not in ["super_admin", "admin", "manager"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    real_metrics = get_real_system_metrics()
    
    return {
        "system_health": {
            "cpu_percent": real_metrics["cpu_percent"],
            "memory_percent": real_metrics["memory_percent"],
            "disk_percent": real_metrics["disk_percent"],
            "database_status": SYSTEM_HEALTH["database_status"],
            "uptime_days": round(real_metrics["uptime_seconds"] / 86400, 1),
            "active_bots": SYSTEM_HEALTH["active_bots"],
            "total_bots": SYSTEM_HEALTH["total_bots"]
        },
        "role_distribution": ROLE_DISTRIBUTION,
        "user_access": USERS_ACCESS[:5],
        "feature_flags": FEATURE_FLAGS,
        "alerts": ACTIVE_ALERTS,
        "bottlenecks": BOTTLENECKS,
        "forecast": RESOURCE_FORECAST
    }