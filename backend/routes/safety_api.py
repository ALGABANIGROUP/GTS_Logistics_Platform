from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.safety.main import safety_manager

router = APIRouter(prefix="/api/v1/safety", tags=["Safety Manager"])


class IncidentPayload(BaseModel):
    incident_type: str = "other"
    severity: str = "moderate"
    description: str
    location: str
    reporter: str = "system"
    injured_persons: List[Dict[str, Any]] = Field(default_factory=list)
    witnesses: List[str] = Field(default_factory=list)


class DriverMonitorPayload(BaseModel):
    driver_id: int
    hours_driven: int = 0
    speeding_events: int = 0
    hard_braking: int = 0
    rapid_acceleration: int = 0
    rest_hours: int = 8
    heart_rate: Optional[int] = None


class RouteEvaluationPayload(BaseModel):
    name: str
    region: str
    distance_km: float
    type: str = "highway"
    speed_limit: int = 100


class PreventiveActionPayload(BaseModel):
    action_type: str
    description: str
    priority: str = "medium"
    assigned_to: Optional[str] = None
    due_date: Optional[str] = None
    incident_id: Optional[str] = None
    driver_id: Optional[int] = None
    vehicle_id: Optional[int] = None


def _compliance_breakdown(issues: List[Dict[str, Any]]) -> Dict[str, float]:
    if not issues:
        return {"OSHA": 100.0, "ISO 45001": 100.0, "UAE Safety": 100.0}

    buckets = {"OSHA": [], "ISO 45001": [], "UAE Safety": []}
    for issue in issues:
        standard_id = str(issue.get("standard_id", ""))
        if standard_id.startswith("OSHA"):
            buckets["OSHA"].append(issue)
        elif standard_id.startswith("ISO"):
            buckets["ISO 45001"].append(issue)
        else:
            buckets["UAE Safety"].append(issue)

    results: Dict[str, float] = {}
    for label, bucket in buckets.items():
        results[label] = round(max(60.0, 100.0 - (len(bucket) * 7.5)), 1) if bucket else 100.0
    return results


@router.get("/dashboard")
async def get_safety_dashboard() -> Dict[str, Any]:
    return await safety_manager.get_safety_dashboard()


@router.get("/incidents/statistics")
async def get_incidents_statistics(days: int = 30) -> Dict[str, Any]:
    stats = await safety_manager.incident_manager.get_incident_statistics(days=days)
    return {
        "total": stats.get("total_incidents", 0),
        "total_incidents": stats.get("total_incidents", 0),
        "by_type": stats.get("by_type", {}),
        "by_severity": stats.get("by_severity", {}),
        "by_location": stats.get("by_location", {}),
        "historical": stats.get("trend_analysis", []),
        "key_insights": stats.get("key_insights", []),
    }


@router.get("/compliance/check")
async def get_compliance_status() -> Dict[str, Any]:
    report = await safety_manager.compliance_monitor.check_safety_compliance()
    issues = report.get("issues_found", [])
    return {
        "status": report.get("overall_status", "unknown"),
        "score": report.get("compliance_rate", 0.0),
        "compliance_rate": report.get("compliance_rate", 0.0),
        "requirements": {
            "standards_checked": len(report.get("standards_checked", [])),
            "issues_found": len(issues),
        },
        "issues": issues[:10],
        "compliance_by_framework": _compliance_breakdown(issues),
        "recommendations": report.get("recommendations", []),
        "next_audit": None,
    }


@router.get("/risks/assess")
async def assess_risks() -> Dict[str, Any]:
    assessment = await safety_manager.risk_predictor.assess_current_risks()
    return {
        "overall_risk": str(assessment.get("overall_risk_level", "unknown")).upper(),
        "risk_factors": assessment.get("high_risks", []),
        "high_risk_areas": assessment.get("high_risks", []),
        "recommendations": [
            item.get("mitigation")
            for item in assessment.get("high_risks", [])
            if item.get("mitigation")
        ],
    }


@router.post("/incidents/report")
async def report_incident(payload: IncidentPayload) -> Dict[str, Any]:
    result = await safety_manager.report_incident(
        incident_type=payload.incident_type,
        severity=payload.severity,
        description=payload.description,
        location=payload.location,
        reporter=payload.reporter,
        injured_persons=payload.injured_persons,
        witnesses=payload.witnesses,
    )
    if result.get("error"):
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.post("/drivers/monitor")
async def monitor_driver(payload: DriverMonitorPayload) -> Dict[str, Any]:
    return await safety_manager.monitor_driver(
        driver_id=payload.driver_id,
        hours_driven=payload.hours_driven,
        speeding_events=payload.speeding_events,
        hard_braking=payload.hard_braking,
        rapid_acceleration=payload.rapid_acceleration,
        rest_hours=payload.rest_hours,
        heart_rate=payload.heart_rate,
    )


@router.get("/drivers/{driver_id}/history")
async def get_driver_history(driver_id: int, days: int = 7) -> Dict[str, Any]:
    return await safety_manager.get_driver_history(driver_id=driver_id, days=days)


@router.get("/vehicles/{vehicle_id}/sensors")
async def read_vehicle_sensors(vehicle_id: int) -> Dict[str, Any]:
    return await safety_manager.read_vehicle_sensors(vehicle_id=vehicle_id)


@router.get("/weather/alerts/{region}")
async def get_weather_alerts(region: str) -> Dict[str, Any]:
    return await safety_manager.get_weather_alerts(region=region)


@router.post("/routes/evaluate")
async def evaluate_route(payload: RouteEvaluationPayload) -> Dict[str, Any]:
    return await safety_manager.evaluate_route_safety(
        route_name=payload.name,
        region=payload.region,
        distance_km=payload.distance_km,
        route_type=payload.type,
        speed_limit=payload.speed_limit,
    )


@router.post("/preventive-actions")
async def create_preventive_action(payload: PreventiveActionPayload) -> Dict[str, Any]:
    return await safety_manager.create_preventive_action(**payload.model_dump())


@router.put("/preventive-actions/{action_id}/complete")
async def complete_preventive_action(action_id: str) -> Dict[str, Any]:
    result = await safety_manager.complete_preventive_action(action_id=action_id)
    if not result.get("success"):
        raise HTTPException(status_code=404, detail=result.get("error", "Preventive action not found"))
    return result


@router.get("/reports/daily")
async def get_daily_report() -> Dict[str, Any]:
    return await safety_manager.generate_daily_report()


@router.get("/status")
async def get_safety_status() -> Dict[str, Any]:
    return await safety_manager.get_status()


@router.get("/config")
async def get_safety_config() -> Dict[str, Any]:
    return await safety_manager.get_config()
