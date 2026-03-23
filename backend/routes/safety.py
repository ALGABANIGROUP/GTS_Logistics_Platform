"""
Safety Management API Routes
"""

from fastapi import APIRouter, HTTPException, Query, Body
from typing import Dict, Any, List, Optional
from datetime import datetime

# Import safety manager
try:
    from backend.safety.main import safety_manager
except ImportError:
    safety_manager = None

router = APIRouter(prefix="/api/v1/safety", tags=["safety"])


@router.get("/status")
async def get_safety_status() -> Dict[str, Any]:
    """Return overall safety system status."""
    if not safety_manager:
        return {"error": "Safety manager not initialized"}
    return await safety_manager.get_status()


@router.get("/config")
async def get_safety_config() -> Dict[str, Any]:
    """Return active safety configuration."""
    if not safety_manager:
        return {"error": "Safety manager not initialized"}
    return await safety_manager.get_config()


@router.get("/dashboard")
async def get_safety_dashboard() -> Dict[str, Any]:
    """Return safety dashboard summary data."""
    if not safety_manager:
        return {"error": "Safety manager not initialized"}
    return await safety_manager.get_safety_dashboard()


@router.post("/incidents/report")
async def report_incident(payload: Dict[str, Any] = Body(...)) -> Dict[str, Any]:
    """Report a new safety incident."""
    if not safety_manager:
        return {"error": "Safety manager not initialized"}
    
    return await safety_manager.report_incident(
        incident_type=payload.get("incident_type"),
        severity=payload.get("severity"),
        description=payload.get("description"),
        location=payload.get("location"),
        reporter=payload.get("reporter"),
        injured_persons=payload.get("injured_persons"),
        witnesses=payload.get("witnesses"),
    )


@router.get("/incidents/statistics")
async def get_incidents_statistics(days: int = Query(30)) -> Dict[str, Any]:
    """Return incident statistics for a given time window."""
    if not safety_manager:
        return {"error": "Safety manager not initialized"}
    return await safety_manager.incident_manager.get_incident_statistics(days=days)


@router.get("/compliance/check")
async def check_compliance() -> Dict[str, Any]:
    """Run compliance checks and return findings."""
    if not safety_manager:
        return {"error": "Safety manager not initialized"}
    return await safety_manager.compliance_monitor.check_safety_compliance()


@router.get("/risks/assess")
async def assess_risks() -> Dict[str, Any]:
    """Run current safety risk assessment."""
    if not safety_manager:
        return {"error": "Safety manager not initialized"}
    return await safety_manager.risk_predictor.assess_current_risks()


@router.post("/risks/detailed-assessment")
async def perform_detailed_risk_assessment(payload: Dict[str, Any] = Body(...)) -> Dict[str, Any]:
    """Run a detailed risk assessment for a target activity and area."""
    if not safety_manager:
        return {"error": "Safety manager not initialized"}
    
    return await safety_manager.risk_predictor.perform_detailed_assessment(
        area=payload.get("area"),
        activity=payload.get("activity"),
        assessor=payload.get("assessor"),
    )


@router.get("/inspections/schedule")
async def get_inspection_schedule() -> Dict[str, Any]:
    """Return upcoming and planned inspection schedule."""
    if not safety_manager:
        return {"error": "Safety manager not initialized"}
    return {"inspections": safety_manager.inspection_schedule}


@router.post("/inspections/conduct")
async def conduct_inspection(payload: Dict[str, Any] = Body(...)) -> Dict[str, Any]:
    """Submit and process an inspection event."""
    if not safety_manager:
        return {"error": "Safety manager not initialized"}
    
    return await safety_manager.inspection_manager.conduct_inspection(
        inspection_type=payload.get("inspection_type"),
        inspector=payload.get("inspector"),
        location=payload.get("location"),
    )


@router.get("/training/requirements")
async def check_training_requirements() -> Dict[str, Any]:
    """Return training requirement status."""
    if not safety_manager:
        return {"error": "Safety manager not initialized"}
    return await safety_manager.training_manager.check_training_requirements()


@router.post("/training/schedule")
async def schedule_training(payload: Dict[str, Any] = Body(...)) -> Dict[str, Any]:
    """Schedule a safety training course."""
    if not safety_manager:
        return {"error": "Safety manager not initialized"}
    
    return await safety_manager.training_manager.schedule_training_course(
        course_id=payload.get("course_id"),
        participants=payload.get("participants", []),
        scheduled_date=payload.get("scheduled_date"),
    )


@router.get("/alerts/recent")
async def get_recent_alerts(hours: int = Query(24)) -> Dict[str, Any]:
    """Return recent safety alerts within the given time window."""
    if not safety_manager:
        return {"error": "Safety manager not initialized"}
    
    from datetime import timedelta

    cutoff_time = datetime.utcnow() - timedelta(hours=hours)

    recent_alerts = [
        a
        for a in safety_manager.safety_alerts
        if datetime.fromisoformat(a["timestamp"]) > cutoff_time
    ]

    return {"alerts": recent_alerts, "count": len(recent_alerts)}


@router.post("/audit/schedule")
async def schedule_compliance_audit(payload: Dict[str, Any] = Body(...)) -> Dict[str, Any]:
    """Schedule a compliance audit."""
    if not safety_manager:
        return {"error": "Safety manager not initialized"}
    
    return await safety_manager.compliance_monitor.schedule_compliance_audit(
        audit_type=payload.get("audit_type"),
        auditor=payload.get("auditor"),
    )