from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, and_, desc, func
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.config import get_db_async
from backend.security.auth import get_current_user
from .models import HealthSnapshot, Incident, RemediationAction, MaintenanceAuditLog, AlertRule
from .service import MaintenanceService
from .core import maintenance_core
from pydantic import BaseModel

logger = logging.getLogger("maintenance")

router = APIRouter(prefix="/maintenance", tags=["maintenance"])


# Request/Response Models
class ChatMessage(BaseModel):
    message: str
    user_id: Optional[str] = None


class ChatResponse(BaseModel):
    success: bool
    response: str
    analysis: Optional[Dict[str, Any]] = None
    incident_id: Optional[int] = None


class CycleRequest(BaseModel):
    force: bool = False


@router.post("/health/collect")
async def trigger_health_collection(db: AsyncSession = Depends(get_db_async)) -> Dict[str, Any]:
    """Manually trigger health data collection."""
    try:
        service = MaintenanceService()
        await service.collect_and_analyze_health(db)
        return {"status": "success", "message": "Health collection triggered"}
    except Exception as e:
        logger.error(f"Failed to trigger health collection: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to collect health data: {str(e)}")


@router.get("/health")
async def get_system_health(db: AsyncSession = Depends(get_db_async)) -> Dict[str, Any]:
    """Get current system health status."""
    try:
        # Get latest snapshot
        result = await db.execute(
            select(HealthSnapshot).order_by(desc(HealthSnapshot.timestamp)).limit(1)
        )
        snapshot = result.scalar_one_or_none()

        if not snapshot:
            return {"status": "unknown", "message": "No health data available"}

        # Get recent incidents
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        result = await db.execute(
            select(Incident).where(
                and_(Incident.created_at >= one_hour_ago, Incident.status == "open")
            )
        )
        active_incidents = result.scalars().all()

        return {
            "status": snapshot.overall_status,
            "timestamp": snapshot.timestamp.isoformat(),
            "metrics": {
                "cpu_percent": snapshot.cpu_percent,
                "memory_percent": snapshot.memory_percent,
                "disk_percent": snapshot.disk_percent,
                "db_latency_ms": snapshot.db_latency_ms,
                "load_average": snapshot.load_average
            },
            "bots": snapshot.bot_metrics or {},
            "active_incidents": len(active_incidents),
            "last_updated": snapshot.created_at.isoformat()
        }

    except Exception as e:
        logger.exception("Failed to get system health")  # includes traceback
        raise HTTPException(status_code=500, detail=f"Failed to retrieve health data: {e}")


@router.get("/snapshots")
async def get_health_snapshots(
    limit: int = Query(50, ge=1, le=1000),
    hours: int = Query(24, ge=1, le=168),
    db: AsyncSession = Depends(get_db_async)
) -> Dict[str, Any]:
    """Get recent health snapshots."""
    try:
        since = datetime.utcnow() - timedelta(hours=hours)

        result = await db.execute(
            select(HealthSnapshot).where(HealthSnapshot.timestamp >= since)
            .order_by(desc(HealthSnapshot.timestamp)).limit(limit)
        )
        snapshots = result.scalars().all()

        return {
            "snapshots": [
                {
                    "id": s.id,
                    "timestamp": s.timestamp.isoformat(),
                    "cpu_percent": s.cpu_percent,
                    "memory_percent": s.memory_percent,
                    "disk_percent": s.disk_percent,
                    "db_latency_ms": s.db_latency_ms,
                    "overall_status": s.overall_status,
                    "bot_metrics": s.bot_metrics
                }
                for s in snapshots
            ],
            "count": len(snapshots)
        }

    except Exception as e:
        logger.error(f"Failed to get snapshots: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve snapshots")


@router.get("/incidents")
async def get_incidents(
    status_filter: Optional[str] = Query(None, pattern="^(open|investigating|resolved|closed)$"),
    severity: Optional[str] = Query(None, pattern="^(info|warning|error|critical)$"),
    limit: int = Query(50, ge=1, le=500),
    db: AsyncSession = Depends(get_db_async)
) -> Dict[str, Any]:
    """Get maintenance incidents."""
    try:
        query = select(Incident)

        if status_filter:
            query = query.where(Incident.status == status_filter)
        if severity:
            query = query.where(Incident.severity == severity)

        result = await db.execute(
            query.order_by(desc(Incident.created_at)).limit(limit)
        )
        incidents = result.scalars().all()

        return {
            "incidents": [
                {
                    "id": i.id,
                    "title": i.title,
                    "description": i.description,
                    "severity": i.severity,
                    "status": i.status,
                    "component": i.component,
                    "component_id": i.component_id,
                    "created_at": i.created_at.isoformat(),
                    "resolved_at": i.resolved_at.isoformat() if i.resolved_at is not None else None,
                    "auto_remediated": i.auto_remediated
                }
                for i in incidents
            ],
            "count": len(incidents)
        }

    except Exception as e:
        logger.error(f"Failed to get incidents: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve incidents")


@router.get("/remediation")
async def get_remediation_actions(
    status: Optional[str] = Query(None, pattern="^(pending|running|completed|failed)$"),
    limit: int = Query(50, ge=1, le=500),
    db: AsyncSession = Depends(get_db_async)
) -> Dict[str, Any]:
    """Get remediation actions."""
    try:
        query = select(RemediationAction)

        if status:
            query = query.where(RemediationAction.status == status)

        result = await db.execute(
            query.order_by(desc(RemediationAction.created_at)).limit(limit)
        )
        actions = result.scalars().all()

        return {
            "actions": [
                {
                    "id": a.id,
                    "action_type": a.action_type,
                    "action_params": a.action_params,
                    "status": a.status,
                    "success": a.success,
                    "executed_at": a.executed_at.isoformat() if a.executed_at is not None else None,
                    "completed_at": a.completed_at.isoformat() if a.completed_at is not None else None,
                    "runbook_id": a.runbook_id,
                    "error_message": a.error_message
                }
                for a in actions
            ],
            "count": len(actions)
        }

    except Exception as e:
        logger.error(f"Failed to get remediation actions: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve actions")


@router.post("/remediation/{runbook_id}")
async def execute_remediation(
    runbook_id: str,
    params: Optional[Dict[str, Any]] = None,
    db: AsyncSession = Depends(get_db_async),
    claims: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """Manually execute a remediation runbook."""
    try:
        from .service import RemediationService

        if params is None:
            params = {}

        # Add user context
        params["user_id"] = claims.get("sub")
        params["executed_by"] = "manual"

        success = await RemediationService.execute_runbook(db, runbook_id, params)

        if success:
            return {"success": True, "message": f"Runbook {runbook_id} executed successfully"}
        else:
            raise HTTPException(status_code=500, detail=f"Runbook {runbook_id} execution failed")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to execute runbook: {e}")
        raise HTTPException(status_code=500, detail="Failed to execute remediation")


@router.get("/report/daily")
async def get_daily_report(db: AsyncSession = Depends(get_db_async)) -> Dict[str, Any]:
    """Get daily maintenance report."""
    try:
        from .service import MaintenanceReporter

        report = await MaintenanceReporter.generate_daily_report(db)
        return {"report": report}

    except Exception as e:
        logger.error(f"Failed to generate daily report: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate report")


@router.get("/stats")
async def get_maintenance_stats(db: AsyncSession = Depends(get_db_async)) -> Dict[str, Any]:
    """Get maintenance statistics."""
    try:
        # Count incidents by status
        result = await db.execute(
            select(Incident.status, func.count(Incident.id))
            .group_by(Incident.status)
        )
        incident_rows = result.fetchall()
        incident_stats = {row[0]: row[1] for row in incident_rows}

        # Count remediation actions by status
        result = await db.execute(
            select(RemediationAction.status, func.count(RemediationAction.id))
            .group_by(RemediationAction.status)
        )
        remediation_rows = result.fetchall()
        remediation_stats = {row[0]: row[1] for row in remediation_rows}

        # Recent health status
        result = await db.execute(
            select(HealthSnapshot.overall_status, func.count(HealthSnapshot.id))
            .where(HealthSnapshot.timestamp >= datetime.utcnow() - timedelta(hours=24))
            .group_by(HealthSnapshot.overall_status)
        )
        health_rows = result.fetchall()
        health_stats = {row[0]: row[1] for row in health_rows}

        return {
            "incidents": incident_stats,
            "remediation": remediation_stats,
            "health": health_stats,
            "generated_at": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Failed to get maintenance stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve statistics")


# ==================== NEW ADVANCED ENDPOINTS ====================

@router.post("/chat")
async def chat_with_bot(
    message: ChatMessage,
    db: AsyncSession = Depends(get_db_async),
    current_user: Dict = Depends(get_current_user)
) -> ChatResponse:
    """Chat interface for maintenance bot - NLP powered"""
    try:
        user_id = str(current_user.get('id', 'unknown'))
        
        result = await maintenance_core.process_user_message(
            db,
            message.message,
            user_id
        )
        
        return ChatResponse(
            success=result.get('success', False),
            response=result.get('response', ''),
            analysis=result.get('analysis')
        )
    
    except Exception as e:
        logger.error(f"Chat processing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process message: {str(e)}")


@router.post("/run-cycle")
async def run_maintenance_cycle(
    request: CycleRequest,
    db: AsyncSession = Depends(get_db_async),
    current_user: Dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """Trigger a full maintenance cycle (scan, analyze, fix, recommend)"""
    try:
        # Check if user is admin
        if current_user.get('role') != 'super_admin':
            raise HTTPException(status_code=403, detail="Only admins can trigger maintenance cycles")
        
        result = await maintenance_core.run_full_cycle(db)
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Maintenance cycle failed: {e}")
        raise HTTPException(status_code=500, detail=f"Cycle failed: {str(e)}")


@router.get("/system-status")
async def get_advanced_system_status(
    db: AsyncSession = Depends(get_db_async),
    current_user: Dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get comprehensive system status with predictions and trends"""
    try:
        status = await maintenance_core.get_system_status(db)
        return status
    
    except Exception as e:
        logger.error(f"Failed to get system status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get status: {str(e)}")


@router.get("/recommendations")
async def get_recommendations(
    limit: int = Query(default=10, ge=1, le=100),
    priority: Optional[str] = Query(default=None, pattern="^(CRITICAL|HIGH|MEDIUM|LOW)$"),
    db: AsyncSession = Depends(get_db_async),
    current_user: Dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get smart recommendations for system improvements"""
    try:
        # Generate fresh recommendations
        scan_data = {
            'code': {'test_coverage': 75, 'avg_complexity': 8},
            'performance': {'avg_memory_percent': 75, 'avg_api_latency_ms': 245},
            'security': {'vulnerable_dependencies': []},
            'infrastructure': {},
            'reliability': {'uptime_percent': 99.5, 'error_rate': 0.008}
        }
        
        recommendations = await maintenance_core.recommender.generate_recommendations(db, scan_data)
        
        # Filter by priority if specified
        if priority:
            recommendations = [r for r in recommendations if r.priority == priority]
        
        # Limit results
        recommendations = recommendations[:limit]
        
        return {
            'recommendations': [r.to_dict() for r in recommendations],
            'total': len(recommendations),
            'generated_at': datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Failed to get recommendations: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get recommendations: {str(e)}")


@router.post("/auto-fix/{incident_id}")
async def trigger_auto_fix(
    incident_id: int,
    db: AsyncSession = Depends(get_db_async),
    current_user: Dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """Manually trigger auto-fix for a specific incident"""
    try:
        # Get incident
        result = await db.execute(
            select(Incident).where(Incident.id == incident_id)
        )
        incident = result.scalar_one_or_none()
        
        if not incident:
            raise HTTPException(status_code=404, detail="Incident not found")
        
        # Prepare issue data
        issue_data = {
            'incident_id': incident.id,
            'type': incident.component or 'general',
            'severity': incident.severity,
            'title': incident.title,
            'description': incident.description,
            'metrics': {}
        }
        
        # Attempt fix
        fix_result = await maintenance_core.auto_fixer.diagnose_and_fix(db, issue_data)
        
        return fix_result
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Auto-fix failed: {e}")
        raise HTTPException(status_code=500, detail=f"Auto-fix failed: {str(e)}")


@router.get("/knowledge-graph")
async def get_knowledge_graph(
    db: AsyncSession = Depends(get_db_async),
    current_user: Dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get project knowledge graph data"""
    try:
        graph = maintenance_core.knowledge_graph
        
        return {
            'nodes': {
                category: len(nodes)
                for category, nodes in graph.nodes.items()
            },
            'relationships_count': len(graph.relationships),
            'last_update': graph.last_update.isoformat() if graph.last_update else None,
            'insights': graph.generate_insights()
        }
    
    except Exception as e:
        logger.error(f"Failed to get knowledge graph: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get graph: {str(e)}")


@router.get("/health/trends")
async def get_health_trends(
    hours: int = Query(default=24, ge=1, le=168),
    db: AsyncSession = Depends(get_db_async),
    current_user: Dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get health metrics trends over time"""
    try:
        start_time = datetime.utcnow() - timedelta(hours=hours)
        
        result = await db.execute(
            select(HealthSnapshot)
            .where(HealthSnapshot.timestamp >= start_time)
            .order_by(HealthSnapshot.timestamp)
        )
        snapshots = result.scalars().all()
        
        if not snapshots:
            return {'message': 'No data available', 'datapoints': []}
        
        datapoints = [
            {
                'timestamp': s.timestamp.isoformat(),
                'cpu_percent': s.cpu_percent,
                'memory_percent': s.memory_percent,
                'disk_percent': s.disk_percent,
                'db_latency_ms': s.db_latency_ms,
                'overall_status': s.overall_status
            }
            for s in snapshots
        ]
        
        # Calculate trends
        health_monitor = maintenance_core.health_monitor
        health_monitor.metrics_history = [
            {
                'timestamp': s.timestamp,
                'metrics': {
                    'cpu_percent': s.cpu_percent,
                    'memory_percent': s.memory_percent,
                    'db_latency_ms': s.db_latency_ms
                }
            }
            for s in snapshots
        ]
        
        trends = health_monitor.analyze_trends()
        predictions = health_monitor.predict_issues()
        
        return {
            'datapoints': datapoints,
            'trends': trends,
            'predictions': predictions,
            'period_hours': hours
        }
    
    except Exception as e:
        logger.error(f"Failed to get trends: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get trends: {str(e)}")
