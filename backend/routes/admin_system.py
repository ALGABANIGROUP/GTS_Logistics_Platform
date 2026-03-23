"""
System Admin Bot API Routes
Real database data for admin management
"""

from fastapi import APIRouter, Body, Depends, Query
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta, timezone
from backend.security.auth import get_current_user, require_roles
from urllib.parse import urlsplit
import os
import time

try:
    import psutil  # type: ignore
except Exception:
    psutil = None

router = APIRouter(prefix="/api/v1/admin", tags=["Admin System"])


def _bytes_to_gb(value: float) -> float:
    return round(value / (1024 ** 3), 2)


def _format_uptime(seconds: float) -> str:
    if seconds is None:
        return "unknown"
    total_seconds = max(int(seconds), 0)
    days, remainder = divmod(total_seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, _ = divmod(remainder, 60)
    if days:
        return f"{days}d {hours}h {minutes}m"
    if hours:
        return f"{hours}h {minutes}m"
    return f"{minutes}m"


def _derive_status(*percents: float) -> str:
    values = [p for p in percents if isinstance(p, (int, float))]
    if not values:
        return "unknown"
    peak = max(values)
    if peak >= 90:
        return "critical"
    if peak >= 75:
        return "warning"
    return "healthy"


def _get_sqlite_db_size_bytes() -> Optional[int]:
    dsn = os.getenv("ASYNC_DATABASE_URL", "").strip() or os.getenv("DATABASE_URL", "").strip()
    if not dsn:
        return None
    try:
        parts = urlsplit(dsn)
    except Exception:
        return None
    if not parts.scheme.startswith("sqlite"):
        return None
    db_path = parts.path or ""
    if os.name == "nt" and db_path.startswith("/") and len(db_path) >= 3 and db_path[2] == ":":
        db_path = db_path[1:]
    if not db_path:
        return None
    abs_path = os.path.abspath(db_path)
    if not os.path.exists(abs_path):
        return None
    try:
        return os.path.getsize(abs_path)
    except Exception:
        return None


def _get_disk_usage_path() -> str:
    if os.name == "nt":
        return os.getenv("SYSTEMDRIVE", "C:") + "\\"
    return "/"


@router.get("/health/system")
async def get_system_health(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """Get system health information"""
    try:
        cpu_percent = 0.0
        cpu_cores = os.cpu_count() or 0
        cpu_cores_physical = cpu_cores
        memory_percent = 0.0
        memory_total_gb = 0.0
        memory_available_gb = 0.0
        memory_used_gb = 0.0
        disk_percent = 0.0
        disk_total_gb = 0.0
        disk_free_gb = 0.0
        disk_used_gb = 0.0
        uptime_seconds = None

        if psutil:
            cpu_percent = float(psutil.cpu_percent(interval=0.2))
            cpu_cores = int(psutil.cpu_count(logical=True) or cpu_cores)
            cpu_cores_physical = int(psutil.cpu_count(logical=False) or cpu_cores)
            mem = psutil.virtual_memory()
            memory_percent = float(mem.percent)
            memory_total_gb = _bytes_to_gb(mem.total)
            memory_available_gb = _bytes_to_gb(mem.available)
            memory_used_gb = _bytes_to_gb(mem.used)
            disk = psutil.disk_usage(_get_disk_usage_path())
            disk_percent = float(disk.percent)
            disk_total_gb = _bytes_to_gb(disk.total)
            disk_free_gb = _bytes_to_gb(disk.free)
            disk_used_gb = _bytes_to_gb(disk.used)
            uptime_seconds = time.time() - psutil.boot_time()

        status = _derive_status(cpu_percent, memory_percent, disk_percent) if psutil else "unknown"

        return {
            "status": status,
            "system": {
                "cpu": {
                    "percent": round(cpu_percent, 2),
                    "cores": cpu_cores,
                    "cores_physical": cpu_cores_physical,
                },
                "memory": {
                    "percent": round(memory_percent, 2),
                    "total_gb": memory_total_gb,
                    "available_gb": memory_available_gb,
                    "used_gb": memory_used_gb,
                },
                "disk": {
                    "percent": round(disk_percent, 2),
                    "total_gb": disk_total_gb,
                    "free_gb": disk_free_gb,
                    "used_gb": disk_used_gb,
                },
                "uptime": _format_uptime(uptime_seconds),
            },
            "api": {
                "uptime_hours": round((uptime_seconds or 0) / 3600, 2) if uptime_seconds is not None else None,
                "requests_24h": None,
                "avg_response_ms": None,
            },
        }
    except Exception as e:
        return {
            "status": "error",
            "system": {
                "cpu": {"percent": 0, "cores": 0, "cores_physical": 0},
                "memory": {"percent": 0, "total_gb": 0, "available_gb": 0, "used_gb": 0},
                "disk": {"percent": 0, "total_gb": 0, "free_gb": 0, "used_gb": 0},
                "uptime": "unknown",
            }
        }


@router.get("/health/database")
async def get_database_health(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """Get database health information"""
    try:
        from backend.database.config import get_sessionmaker
        from backend.models.user import User
        from sqlalchemy import select, func, text
        
        sessionmaker = get_sessionmaker()
        start_time = time.perf_counter()
        async with sessionmaker() as session:
            # Count users
            users_count = await session.scalar(select(func.count(User.id))) or 0
            
            # Try to count other tables
            shipments_count = 0
            invoices_count = 0
            documents_count = 0
            
            try:
                from backend.models.shipment import Shipment
                shipments_count = await session.scalar(select(func.count(Shipment.id))) or 0
            except Exception:
                pass
            
            try:
                from backend.models.invoice import Invoice
                invoices_count = await session.scalar(select(func.count(Invoice.id))) or 0
            except Exception:
                pass
            
            try:
                from backend.models.document import Document
                documents_count = await session.scalar(select(func.count(Document.id))) or 0
            except Exception:
                pass

            db_size_bytes = None
            try:
                db_size_bytes = await session.scalar(
                    text("SELECT pg_database_size(current_database())")
                )
            except Exception:
                db_size_bytes = _get_sqlite_db_size_bytes()

            response_time_ms = round((time.perf_counter() - start_time) * 1000, 2)

            return {
                "status": "healthy" if response_time_ms < 500 else "warning",
                "database": {
                    "connection": "active",
                    "response_time_ms": response_time_ms,
                    "size_bytes": db_size_bytes,
                    "size_gb": _bytes_to_gb(db_size_bytes) if db_size_bytes is not None else None,
                    "table_counts": {
                        "users": users_count,
                        "shipments": shipments_count,
                        "invoices": invoices_count,
                        "documents": documents_count
                    }
                }
            }
    except Exception as e:
        return {
            "status": "error",
            "database": {
                "connection": "failed",
                "error": str(e),
                "table_counts": {}
            }
        }


@router.get("/health/detailed")
async def get_detailed_health(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """Get detailed health information"""
    cpu_percent = 0.0
    memory_percent = 0.0
    disk_percent = 0.0
    if psutil:
        cpu_percent = float(psutil.cpu_percent(interval=0.2))
        memory_percent = float(psutil.virtual_memory().percent)
        disk_percent = float(psutil.disk_usage(_get_disk_usage_path()).percent)

    issues: List[str] = []
    recommendations: List[str] = []

    if cpu_percent >= 85:
        issues.append("CPU usage is high.")
        recommendations.append("Investigate high CPU processes and scale resources if needed.")
    if memory_percent >= 85:
        issues.append("Memory usage is high.")
        recommendations.append("Check memory leaks and consider increasing RAM.")
    if disk_percent >= 85:
        issues.append("Disk usage is high.")
        recommendations.append("Clean up disk space or expand storage capacity.")

    overall_status = _derive_status(cpu_percent, memory_percent, disk_percent) if psutil else "unknown"

    db_status = "unknown"
    db_response = None
    try:
        from backend.database.config import get_sessionmaker
        from sqlalchemy import text
        sessionmaker = get_sessionmaker()
        start_time = time.perf_counter()
        async with sessionmaker() as session:
            await session.execute(text("SELECT 1"))
        db_response = round((time.perf_counter() - start_time) * 1000, 2)
        db_status = "healthy" if db_response < 500 else "warning"
    except Exception as exc:
        db_status = "error"
        issues.append("Database connectivity error.")
        recommendations.append("Verify database connection and availability.")

    storage_status = "healthy" if disk_percent < 85 else "warning"

    return {
        "overall_status": overall_status,
        "timestamp": datetime.now().isoformat(),
        "issues": issues,
        "recommendations": recommendations,
        "components": {
            "api": {"status": "operational" if overall_status != "critical" else "warning"},
            "database": {"status": db_status, "response_ms": db_response},
            "cache": {"status": "healthy"},
            "storage": {"status": storage_status},
            "system": {"status": overall_status},
        },
    }


@router.get("/users/statistics")
async def get_users_statistics(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """Get user statistics"""
    try:
        from backend.database.config import get_sessionmaker
        from backend.models.user import User
        from sqlalchemy import select, func
        from datetime import datetime, timedelta
        
        sessionmaker = get_sessionmaker()
        async with sessionmaker() as session:
            # Total users
            total_users = await session.scalar(select(func.count(User.id))) or 0
            
            # Active users
            active_users = await session.scalar(
                select(func.count(User.id)).where(User.is_active == True)
            ) or 0
            
            # Inactive users
            inactive_users = total_users - active_users
            
            # New users in last 7 days
            week_ago = datetime.now() - timedelta(days=7)
            new_users = await session.scalar(
                select(func.count(User.id)).where(User.created_at >= week_ago)
            ) or 0
            
            # Get role distribution
            result = await session.execute(
                select(User.role, func.count(User.id)).group_by(User.role)
            )
            role_dist = dict(result.all()) if result else {}
            
            return {
                "ok": True,
                "summary": {
                    "total_users": total_users,
                    "active_users": active_users,
                    "inactive_users": inactive_users,
                    "new_users_7d": new_users,
                    "growth_rate": round((new_users / max(total_users, 1)) * 100, 2)
                },
                "by_role": role_dist,
                "last_updated": datetime.now().isoformat()
            }
    except Exception as e:
        return {
            "ok": False,
            "error": str(e),
            "summary": {
                "total_users": 0,
                "active_users": 0,
                "inactive_users": 0,
                "new_users_7d": 0,
                "growth_rate": 0
            }
        }


@router.get("/users/statistics/summary")
async def get_users_statistics_summary(
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """Compatibility summary for /admin/users/statistics/summary"""
    try:
        from backend.database.config import get_sessionmaker
        from backend.models.user import User
        from sqlalchemy import select, func
        from datetime import datetime, timedelta, timezone

        sessionmaker = get_sessionmaker()
        async with sessionmaker() as session:
            total_users = await session.scalar(select(func.count(User.id))) or 0
            active_users = await session.scalar(
                select(func.count(User.id)).where(User.is_active == True)
            ) or 0
            inactive_users = total_users - active_users

            cutoff = datetime.now(timezone.utc) - timedelta(days=7)
            new_users_last_7_days = await session.scalar(
                select(func.count(User.id)).where(User.created_at >= cutoff)
            ) or 0

            role_result = await session.execute(
                select(User.role, func.count(User.id)).group_by(User.role)
            )
            by_role = {str(role or "unknown").upper(): int(count or 0) for role, count in role_result.all()}

            country_result = await session.execute(
                select(User.country, func.count(User.id)).group_by(User.country)
            )
            by_country = {str(country or "unknown"): int(count or 0) for country, count in country_result.all()}

            return {
                "summary": {
                    "total_users": total_users,
                    "active_users": active_users,
                    "inactive_users": inactive_users,
                    "new_users_last_7_days": new_users_last_7_days,
                },
                "distribution": {
                    "by_role": by_role,
                    "by_country": by_country,
                },
            }
    except Exception as e:
        return {
            "summary": {
                "total_users": 0,
                "active_users": 0,
                "inactive_users": 0,
                "new_users_last_7_days": 0,
            },
            "distribution": {
                "by_role": {},
                "by_country": {},
            },
            "error": str(e),
        }


@router.get("/users/list")
async def list_users(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    role: Optional[str] = None,
    active_only: bool = False,
    search: Optional[str] = None,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """List users with pagination and filters"""
    try:
        from backend.database.config import get_sessionmaker
        from backend.models.user import User
        from sqlalchemy import select, func, or_
        
        sessionmaker = get_sessionmaker()
        async with sessionmaker() as session:
            # Build query with filters
            filters = []
            if active_only:
                filters.append(User.is_active == True)
            if role:
                filters.append(User.role == role)
            if search:
                filters.append(or_(User.email.ilike(f"%{search}%"), User.full_name.ilike(f"%{search}%")))
            
            # Get total count
            count_query = select(func.count(User.id))
            if filters:
                for f in filters:
                    count_query = count_query.where(f)
            
            total = await session.scalar(count_query) or 0
            
            # Get paginated results
            query = select(User)
            if filters:
                for f in filters:
                    query = query.where(f)
            
            offset = (page - 1) * limit
            query = query.offset(offset).limit(limit)
            
            result = await session.execute(query)
            users = result.scalars().all()
            
            users_data = [
                {
                    "id": u.id,
                    "email": u.email,
                    "full_name": u.full_name or "N/A",
                    "role": u.role,
                    "is_active": u.is_active,
                    "created_at": u.created_at.isoformat() if u.created_at else None,
                    "last_login": u.last_login.isoformat() if u.last_login else None
                }
                for u in users
            ]
            
            return {
                "users": users_data,
                "total": total,
                "page": page,
                "limit": limit,
                "total_pages": (total + limit - 1) // limit
            }
    except Exception as e:
        return {
            "users": [],
            "total": 0,
            "page": page,
            "limit": limit,
            "total_pages": 0,
            "error": str(e)
        }


@router.get("/system/users/{user_id}")
async def get_user_details(
    user_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """Get user details"""
    try:
        from backend.database.config import get_sessionmaker
        from backend.models.user import User
        from sqlalchemy import select
        
        sessionmaker = get_sessionmaker()
        async with sessionmaker() as session:
            user = await session.scalar(select(User).where(User.id == user_id))
            
            if not user:
                return {"ok": False, "error": "User not found"}
            
            return {
                "ok": True,
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "full_name": user.full_name,
                    "role": user.role,
                    "is_active": user.is_active,
                    "created_at": user.created_at.isoformat() if user.created_at else None,
                    "last_login": user.last_login.isoformat() if user.last_login else None
                }
            }
    except Exception as e:
        return {"ok": False, "error": str(e)}


@router.get("/dashboard/stats")
async def get_dashboard_stats(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """Get overall dashboard statistics"""
    try:
        from backend.database.config import get_sessionmaker
        from backend.models.user import User
        from sqlalchemy import select, func
        
        sessionmaker = get_sessionmaker()
        async with sessionmaker() as session:
            total_users = await session.scalar(select(func.count(User.id))) or 0
            active_users = await session.scalar(
                select(func.count(User.id)).where(User.is_active == True)
            ) or 0

            cpu_percent = 0.0
            memory_percent = 0.0
            disk_percent = 0.0
            if psutil:
                cpu_percent = float(psutil.cpu_percent(interval=0.1))
                memory_percent = float(psutil.virtual_memory().percent)
                disk_percent = float(psutil.disk_usage(_get_disk_usage_path()).percent)

            system_status = _derive_status(cpu_percent, memory_percent, disk_percent) if psutil else "unknown"

            return {
                "status": system_status,
                "timestamp": datetime.now().isoformat(),
                "metrics": {
                    "total_users": total_users,
                    "active_users": active_users,
                    "inactive_users": total_users - active_users,
                    "system_health": 100 - int(max(cpu_percent, memory_percent, disk_percent)),
                }
            }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "metrics": {"total_users": 0, "active_users": 0}
        }


# ============ Missing endpoints for admin unified functionality ============

@router.get("/system/users/management")
async def management_users(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    role: Optional[str] = None,
    active_only: bool = False,
    search: Optional[str] = None,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """Alias for /users/list - Management view of users"""
    try:
        from backend.database.config import get_sessionmaker
        from backend.models.user import User
        from sqlalchemy import select, func, or_
        
        sessionmaker = get_sessionmaker()
        async with sessionmaker() as session:
            # Build query with filters
            filters = []
            if active_only:
                filters.append(User.is_active == True)
            if role:
                filters.append(User.role == role)
            if search:
                filters.append(or_(User.email.ilike(f"%{search}%"), User.full_name.ilike(f"%{search}%")))
            
            # Get total count
            count_query = select(func.count(User.id))
            if filters:
                for f in filters:
                    count_query = count_query.where(f)
            
            total = await session.scalar(count_query) or 0
            
            # Get paginated results
            query = select(User)
            if filters:
                for f in filters:
                    query = query.where(f)
            
            offset = (page - 1) * limit
            query = query.offset(offset).limit(limit)
            
            result = await session.execute(query)
            users = result.scalars().all()
            
            users_data = [
                {
                    "id": u.id,
                    "email": u.email,
                    "full_name": u.full_name or "N/A",
                    "role": u.role,
                    "is_active": u.is_active,
                    "created_at": u.created_at.isoformat() if u.created_at else None,
                    "last_login": u.last_login.isoformat() if u.last_login else None
                }
                for u in users
            ]
            
            return {
                "users": users_data,
                "total": total,
                "page": page,
                "limit": limit,
                "total_pages": (total + limit - 1) // limit
            }
    except Exception as e:
        return {
            "users": [],
            "total": 0,
            "page": page,
            "limit": limit,
            "total_pages": 0,
            "error": str(e)
        }


@router.get("/system/roles")
async def list_roles(
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """Get available user roles"""
    roles = [
        {"name": "super_admin", "label": "Super Admin", "level": 5},
        {"name": "owner", "label": "Owner", "level": 4},
        {"name": "system_admin", "label": "System Admin", "level": 4},
        {"name": "admin", "label": "Admin", "level": 3},
        {"name": "manager", "label": "Manager", "level": 2},
        {"name": "user", "label": "User", "level": 1},
        {"name": "partner", "label": "Partner", "level": 1},
    ]
    return {
        "data": {
            "roles": roles
        }
    }


@router.get("/system/org/tree")
async def get_org_tree(
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """Get organization chart tree"""
    try:
        from backend.database.config import get_sessionmaker
        from backend.models.user import User
        from sqlalchemy import select
        
        sessionmaker = get_sessionmaker()
        async with sessionmaker() as session:
            result = await session.execute(select(User))
            users = result.scalars().all()

            nodes = {}
            for user in users:
                nodes[user.id] = {
                    "id": user.id,
                    "name": user.full_name or user.email,
                    "role": user.role,
                    "email": user.email,
                    "children": []
                }

            roots = []
            for user in users:
                node = nodes[user.id]
                if user.manager_id and user.manager_id in nodes:
                    nodes[user.manager_id]["children"].append(node)
                else:
                    roots.append(node)

            return {
                "data": {
                    "tree": roots
                }
            }
    except Exception as e:
        return {
            "data": {
                "tree": []
            },
            "error": str(e)
        }


@router.post("/system/org/units/{user_id}/move")
async def move_user_to_manager(
    user_id: int,
    payload: Dict[str, Any] = Body(default={}),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """Move user to new manager"""
    try:
        from backend.database.config import get_sessionmaker
        from backend.models.user import User
        
        sessionmaker = get_sessionmaker()
        async with sessionmaker() as session:
            manager_id = payload.get("manager_id") if isinstance(payload, dict) else None
            # Check if user exists
            user = await session.get(User, user_id)
            if not user:
                return {"error": "User not found", "success": False}
            
            # Check if manager exists (if provided)
            if manager_id:
                manager = await session.get(User, manager_id)
                if not manager:
                    return {"error": "Manager not found", "success": False}
            
            # Update manager
            user.manager_id = manager_id
            await session.commit()
            
            return {
                "success": True,
                "message": f"User {user.email} moved to manager {manager_id or 'None'}",
                "user_id": user_id,
                "manager_id": manager_id
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
