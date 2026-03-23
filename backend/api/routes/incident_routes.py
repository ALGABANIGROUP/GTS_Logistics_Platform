from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from backend.services.incident_tracker import IncidentTracker, IncidentSeverity
from backend.security.auth import get_current_user, require_roles

router = APIRouter(prefix="/api/v1/incidents", tags=["Incidents"])

# Create tracker (Singleton)
incident_tracker = IncidentTracker()

class ErrorCapture(BaseModel):
    service: str
    error: str
    description: Optional[str] = None
    traceback: Optional[str] = None
    affected_users: int = 0

class InvestigationStart(BaseModel):
    investigator: str
    notes: str

class ContainAction(BaseModel):
    action: str

class ResolutionAction(BaseModel):
    resolution_notes: str
    root_cause: Optional[str] = None

class LogAnalysis(BaseModel):
    log_lines: List[str]
    window_minutes: int = 30

@router.post("/capture")
async def capture_error(
    error: ErrorCapture,
    current_user = Depends(require_roles(["super_admin", "admin", "manager"]))
):
    """
    Record new error as incident
    """
    incident = incident_tracker.capture_error(error.dict())
    return {
        "success": True,
        "incident_id": incident.id,
        "severity": incident.severity.value,
        "status": incident.status.value,
        "message": "Incident captured"
    }

@router.post("/{incident_id}/investigate")
async def investigate_incident(
    incident_id: str,
    investigation: InvestigationStart,
    current_user = Depends(require_roles(["super_admin", "admin"]))
):
    """
    Start investigation of incident
    """
    result = incident_tracker.investigate(
        incident_id,
        investigation.investigator,
        investigation.notes
    )
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result

@router.post("/{incident_id}/contain")
async def contain_incident(
    incident_id: str,
    contain: ContainAction,
    current_user = Depends(require_roles(["super_admin", "admin"]))
):
    """
    Contain incident
    """
    result = incident_tracker.contain(incident_id, contain.action)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result

@router.post("/{incident_id}/resolve")
async def resolve_incident(
    incident_id: str,
    resolution: ResolutionAction,
    current_user = Depends(require_roles(["super_admin", "admin"]))
):
    """
    Resolve incident
    """
    result = incident_tracker.resolve(
        incident_id,
        resolution.resolution_notes,
        resolution.root_cause
    )
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result

@router.post("/{incident_id}/analyze-logs")
async def analyze_incident_logs(
    incident_id: str,
    logs: LogAnalysis,
    current_user = Depends(require_roles(["super_admin", "admin", "manager"]))
):
    """
    Analyze logs related to incident
    """
    result = incident_tracker.analyze_logs(
        incident_id,
        logs.log_lines,
        logs.window_minutes
    )
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result

@router.get("/active")
async def get_active_incidents(
    current_user = Depends(require_roles(["super_admin", "admin", "manager"]))
):
    """
    Active incidents
    """
    return {
        "success": True,
        "incidents": incident_tracker.get_active_incidents(),
        "total": len(incident_tracker.active_incidents)
    }

@router.get("/report")
async def get_incident_report(
    incident_id: Optional[str] = None,
    days: int = Query(7, ge=1, le=90),
    current_user = Depends(require_roles(["super_admin", "admin"]))
):
    """
    Incident report
    """
    return incident_tracker.get_incident_report(incident_id, days)

@router.get("/stats")
async def get_incident_stats(
    current_user = Depends(require_roles(["super_admin", "admin", "manager"]))
):
    """
    Incident statistics
    """
    active = incident_tracker.get_active_incidents()
    report = incident_tracker.get_incident_report(days=30)

    return {
        "active_count": len(active),
        "critical_active": sum(1 for i in active if i["severity"] == "critical"),
        "total_last_30_days": report.get("total_incidents", 0),
        "avg_resolution_time_minutes": report.get("avg_resolution_time", 0),
        "top_services": report.get("by_service", {})
    }