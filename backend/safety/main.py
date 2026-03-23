"""
AI Safety Manager Bot - Core Service
"""

import asyncio
import logging
import random
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

from .core.compliance_monitor import ComplianceMonitor
from .core.emergency_responder import EmergencyResponder
from .core.incident_manager import IncidentManager
from .core.inspection_manager import InspectionManager
from .core.risk_predictor import RiskPredictor
from .core.training_manager import TrainingManager

logger = logging.getLogger(__name__)


class IncidentSeverity(Enum):
    MINOR = "minor"
    MODERATE = "moderate"
    MAJOR = "major"
    CRITICAL = "critical"
    FATAL = "fatal"


class IncidentType(Enum):
    SLIP_TRIP_FALL = "slip_trip_fall"
    EQUIPMENT_ACCIDENT = "equipment_accident"
    VEHICLE_ACCIDENT = "vehicle_accident"
    FIRE = "fire"
    CHEMICAL_SPILL = "chemical_spill"
    ELECTRICAL_ACCIDENT = "electrical_accident"
    MANUAL_HANDLING = "manual_handling"
    OTHER = "other"


class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"
    CRITICAL = "critical"


@dataclass
class SafetyConfig:
    compliance_check_interval: int = 3600
    inspection_schedule_interval: int = 86400
    risk_assessment_interval: int = 7200
    alert_threshold_risk: RiskLevel = RiskLevel.HIGH


@dataclass
class IncidentReport:
    id: str
    type: IncidentType
    severity: IncidentSeverity
    description: str
    location: str
    reported_by: str
    reported_at: datetime
    injured_persons: Optional[List[Dict[str, Any]]] = None
    witnesses: Optional[List[str]] = None
    immediate_actions: Optional[List[str]] = None
    investigation_status: str = "reported"


class AISafetyManagerBot:
    def __init__(self, config: Optional[SafetyConfig] = None):
        self.config = config or SafetyConfig()
        self.incident_manager = IncidentManager()
        self.compliance_monitor = ComplianceMonitor()
        self.risk_predictor = RiskPredictor()
        self.inspection_manager = InspectionManager()
        self.emergency_responder = EmergencyResponder()
        self.training_manager = TrainingManager()

        self.name = "safety_manager"
        self.display_name = "AI Safety Manager"
        self.description = "Monitors safety risks, incidents, compliance, and emergency readiness"
        self.version = "1.1.0"
        self.status = "running"
        self.is_active = True
        self.is_running = False
        self.tasks: List[asyncio.Task] = []

        self.active_incidents: List[IncidentReport] = []
        self.safety_alerts: List[Dict[str, Any]] = []
        self.risk_assessments: List[Dict[str, Any]] = []
        self.inspection_schedule: List[Dict[str, Any]] = []
        self.driver_monitoring_history: Dict[int, List[Dict[str, Any]]] = {}
        self.vehicle_sensor_history: Dict[int, List[Dict[str, Any]]] = {}
        self.weather_alert_history: List[Dict[str, Any]] = []
        self.preventive_actions: List[Dict[str, Any]] = []
        self.safety_metrics = {
            "total_incidents": 0,
            "incidents_today": 0,
            "incidents_this_month": 0,
            "days_without_accident": 120,
            "compliance_rate": 95.0,
            "risk_level": "low",
            "high_risk_drivers": 0,
            "sensor_alerts": 0,
            "weather_alerts": 0,
        }

    def _push_alert(self, alert_type: str, severity: str, title: str, description: str, **extra: Any) -> None:
        self.safety_alerts.append(
            {
                "id": f"{alert_type}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}",
                "type": alert_type,
                "severity": severity,
                "title": title,
                "description": description,
                "timestamp": datetime.utcnow().isoformat(),
                **extra,
            }
        )

    async def _update_safety_metrics(self) -> None:
        self.safety_metrics["high_risk_drivers"] = sum(
            1
            for history in self.driver_monitoring_history.values()
            if history and history[-1]["risk_level"] in {"HIGH", "CRITICAL"}
        )
        self.safety_metrics["sensor_alerts"] = sum(
            1 for history in self.vehicle_sensor_history.values() if history and history[-1]["alerts"]
        )
        self.safety_metrics["weather_alerts"] = len([a for a in self.weather_alert_history if a.get("is_active", True)])
        self.safety_metrics["incidents_this_month"] = len(
            [i for i in self.active_incidents if i.reported_at >= datetime.utcnow() - timedelta(days=30)]
        )
        if self.safety_alerts and any(alert["severity"] == "critical" for alert in self.safety_alerts[-10:]):
            self.safety_metrics["risk_level"] = "critical"
        elif self.safety_metrics["high_risk_drivers"] > 0 or self.safety_metrics["sensor_alerts"] > 1:
            self.safety_metrics["risk_level"] = "high"
        elif self.safety_metrics["weather_alerts"] > 0 or self.safety_alerts:
            self.safety_metrics["risk_level"] = "medium"
        else:
            self.safety_metrics["risk_level"] = "low"

    async def report_incident(
        self,
        incident_type: str,
        severity: str,
        description: str,
        location: str,
        reporter: str,
        injured_persons: Optional[List[Dict[str, Any]]] = None,
        witnesses: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        if incident_type not in [it.value for it in IncidentType]:
            return {"error": f"Invalid incident type: {incident_type}"}
        if severity not in [sv.value for sv in IncidentSeverity]:
            return {"error": f"Invalid severity: {severity}"}

        incident = IncidentReport(
            id=f"INC_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            type=IncidentType(incident_type),
            severity=IncidentSeverity(severity),
            description=description,
            location=location,
            reported_by=reporter,
            reported_at=datetime.utcnow(),
            injured_persons=injured_persons or [],
            witnesses=witnesses or [],
            immediate_actions=["Secure the area", "Notify the safety supervisor"],
        )
        self.active_incidents.append(incident)
        self.safety_metrics["total_incidents"] += 1
        self.safety_metrics["incidents_today"] += 1
        await self.incident_manager.record_incident(incident)
        await self.risk_predictor.update_risk_assessment(incident)
        self._push_alert("incident", severity, f"Incident reported: {incident_type} at {location}", description)
        return {
            "success": True,
            "incident_id": incident.id,
            "status": "reported",
            "timestamp": incident.reported_at.isoformat(),
            "analysis": {
                "root_causes": ["Operational review required", "Driver and route conditions need validation"],
                "prevention_measures": [
                    "Review root cause with dispatcher and safety lead.",
                    "Confirm driver briefing before the next assignment.",
                ],
                "risk_score": 30 if severity == "minor" else 55 if severity == "moderate" else 78,
            },
        }

    async def monitor_driver(
        self,
        driver_id: int,
        hours_driven: int,
        speeding_events: int = 0,
        hard_braking: int = 0,
        rapid_acceleration: int = 0,
        rest_hours: int = 8,
        heart_rate: Optional[int] = None,
    ) -> Dict[str, Any]:
        fatigue_score = min(100, hours_driven * 9 + max(0, 7 - rest_hours) * 8 + (12 if heart_rate and (heart_rate < 55 or heart_rate > 110) else 0))
        behavior_score = max(0, 100 - speeding_events * 6 - hard_braking * 4 - rapid_acceleration * 3)
        safety_score = round(max(0, 100 - ((fatigue_score * 0.55) + ((100 - behavior_score) * 0.45))), 2)
        risk_level = "CRITICAL" if fatigue_score >= 85 or behavior_score <= 40 else "HIGH" if fatigue_score >= 70 or behavior_score <= 60 else "MEDIUM" if fatigue_score >= 50 or behavior_score <= 75 else "LOW"
        alerts = []
        if fatigue_score >= 70:
            alerts.append("Driver fatigue is elevated. Schedule a rest stop immediately.")
        if behavior_score <= 60:
            alerts.append("Driving behavior is outside the preferred safety range.")
        payload = {
            "driver_id": driver_id,
            "timestamp": datetime.utcnow().isoformat(),
            "fatigue_score": fatigue_score,
            "behavior_score": behavior_score,
            "safety_score": safety_score,
            "risk_level": risk_level,
            "alerts": alerts,
        }
        self.driver_monitoring_history.setdefault(driver_id, []).append(payload)
        if risk_level in {"HIGH", "CRITICAL"}:
            self._push_alert("driver", "high", f"Driver {driver_id} requires intervention", "Fatigue or unsafe behavior threshold exceeded.")
        await self._update_safety_metrics()
        return payload

    async def get_driver_history(self, driver_id: int, days: int = 7) -> Dict[str, Any]:
        cutoff = datetime.utcnow() - timedelta(days=days)
        history = [item for item in self.driver_monitoring_history.get(driver_id, []) if datetime.fromisoformat(item["timestamp"]) >= cutoff]
        avg_score = round(sum(item["safety_score"] for item in history) / max(len(history), 1), 2) if history else 0
        return {"driver_id": driver_id, "period_days": days, "avg_safety_score": avg_score, "history": history[-10:]}

    async def read_vehicle_sensors(self, vehicle_id: int) -> Dict[str, Any]:
        readings = {
            "engine_temperature": round(random.uniform(82, 106), 1),
            "tire_pressure": round(random.uniform(27, 39), 1),
            "brake_health": round(random.uniform(18, 78), 1),
            "fuel_level": round(random.uniform(6, 88), 1),
        }
        alerts = []
        if readings["engine_temperature"] >= 95:
            alerts.append("Engine temperature is outside the preferred range.")
        if readings["tire_pressure"] <= 29:
            alerts.append("Tire pressure is outside the preferred range.")
        if readings["brake_health"] <= 25:
            alerts.append("Brake health is below the warning threshold.")
        health_score = max(0, 100 - len(alerts) * 18)
        snapshot = {
            "vehicle_id": vehicle_id,
            "timestamp": datetime.utcnow().isoformat(),
            "readings": readings,
            "alerts": alerts,
            "health_score": health_score,
            "needs_maintenance": health_score < 65,
        }
        self.vehicle_sensor_history.setdefault(vehicle_id, []).append(snapshot)
        if alerts:
            self._push_alert("vehicle", "high" if health_score < 65 else "medium", f"Vehicle {vehicle_id} requires attention", "; ".join(alerts))
        await self._update_safety_metrics()
        return snapshot

    async def get_weather_alerts(self, region: str) -> Dict[str, Any]:
        profiles = [
            ("Heavy rain", "high", 0.55, 2.0, "low"),
            ("Fog", "high", 0.45, 2.4, "very_low"),
            ("High temperature", "medium", 0.9, 1.2, "good"),
        ]
        kind, severity, speed_reduction, risk_factor, visibility = random.choice(profiles)
        alert = {
            "region": region,
            "alert_type": kind,
            "severity": severity,
            "start_time": datetime.utcnow().isoformat(),
            "end_time": (datetime.utcnow() + timedelta(hours=6)).isoformat(),
            "impact": {"speed_reduction": speed_reduction, "risk_factor": risk_factor, "visibility": visibility},
            "recommendations": ["Review live conditions with the dispatcher.", "Adjust route timing if needed."],
            "affected_routes": [f"{region} corridor", f"{region} outer ring"],
            "is_active": True,
        }
        self.weather_alert_history.append(alert)
        self._push_alert("weather", severity, f"Weather advisory for {region}", f"{kind} is affecting active routes.")
        await self._update_safety_metrics()
        return alert

    async def evaluate_route_safety(self, route_name: str, region: str, distance_km: float, route_type: str = "highway", speed_limit: int = 100) -> Dict[str, Any]:
        weather = await self.get_weather_alerts(region)
        risk_factor = weather["impact"]["risk_factor"] * (1.25 if distance_km > 300 else 1.0) * (1.2 if route_type == "mountain" else 1.0)
        safety_level = "SAFE" if risk_factor < 1.5 else "WARNING" if risk_factor < 2.0 else "HIGH_RISK" if risk_factor < 2.5 else "CRITICAL"
        decision = "Proceed with standard caution." if safety_level == "SAFE" else "Delay if timing is flexible." if safety_level == "WARNING" else "Dispatch approval required before departure." if safety_level == "HIGH_RISK" else "Cancel or reroute the trip immediately."
        return {
            "route_name": route_name,
            "region": region,
            "distance_km": distance_km,
            "weather_condition": weather["alert_type"],
            "risk_factor": round(risk_factor, 2),
            "safety_level": safety_level,
            "decision": decision,
            "recommended_speed": int(speed_limit * weather["impact"]["speed_reduction"]),
            "special_precautions": ["Confirm driver rest compliance before dispatch.", "Review live conditions with the dispatcher."],
        }

    async def create_preventive_action(self, action_type: str, description: str, priority: str = "MEDIUM", assigned_to: Optional[str] = None, due_date: Optional[str] = None, **links: Any) -> Dict[str, Any]:
        action = {
            "id": f"PA_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}",
            "action_type": action_type,
            "description": description,
            "priority": priority.upper(),
            "assigned_to": assigned_to or "Safety Team",
            "due_date": due_date,
            "status": "pending",
            "created_at": datetime.utcnow().isoformat(),
            **links,
        }
        self.preventive_actions.append(action)
        return {"success": True, "action": action}

    async def complete_preventive_action(self, action_id: str) -> Dict[str, Any]:
        for action in self.preventive_actions:
            if action["id"] == action_id:
                action["status"] = "completed"
                action["completed_at"] = datetime.utcnow().isoformat()
                return {"success": True, "action": action}
        return {"success": False, "error": "Preventive action not found"}

    async def generate_daily_report(self) -> Dict[str, Any]:
        recent_driver_entries = [history[-1] for history in self.driver_monitoring_history.values() if history]
        avg_safety = round(sum(item["safety_score"] for item in recent_driver_entries) / max(len(recent_driver_entries), 1), 2) if recent_driver_entries else 0
        patterns = await self.incident_manager.get_incident_statistics(days=30)
        return {
            "report_date": datetime.utcnow().date().isoformat(),
            "incidents": {
                "total_incidents": self.safety_metrics["total_incidents"],
                "critical_incidents": len([inc for inc in self.active_incidents if inc.severity in {IncidentSeverity.CRITICAL, IncidentSeverity.FATAL}]),
                "total_injuries": sum(len(inc.injured_persons or []) for inc in self.active_incidents),
                "total_fatalities": len([inc for inc in self.active_incidents if inc.severity == IncidentSeverity.FATAL]),
            },
            "driver_safety": {"avg_safety": avg_safety, "high_risk_drivers": self.safety_metrics["high_risk_drivers"]},
            "weather_alerts": self.safety_metrics["weather_alerts"],
            "patterns": patterns,
            "recommendations": [
                "Review all high-risk driver alerts before the next dispatch cycle.",
                "Schedule immediate inspections for vehicles with critical sensor alerts.",
            ],
            "timestamp": datetime.utcnow().isoformat(),
        }

    async def get_safety_dashboard(self) -> Dict[str, Any]:
        await self._update_safety_metrics()
        recent_alerts = self.safety_alerts[-5:]
        return {
            "status": self.status,
            "timestamp": datetime.utcnow().isoformat(),
            "metrics": self.safety_metrics,
            "safety_score": max(0, round(100 - (len([a for a in recent_alerts if a["severity"] in {"high", "critical"}]) * 7) - (self.safety_metrics["high_risk_drivers"] * 5), 2)),
            "days_without_accident": self.safety_metrics["days_without_accident"],
            "compliance_rate": round(self.safety_metrics["compliance_rate"], 1),
            "total_incidents": self.safety_metrics["total_incidents"],
            "incidents_today": self.safety_metrics["incidents_today"],
            "risk_level": str(self.safety_metrics["risk_level"]).upper(),
            "current_alerts": len(recent_alerts),
            "recent_alerts": recent_alerts,
            "active_alerts": [item["title"] for item in recent_alerts],
            "quick_stats": {
                "open_incidents": len(self.active_incidents),
                "high_risk_drivers": self.safety_metrics["high_risk_drivers"],
                "sensor_alerts": self.safety_metrics["sensor_alerts"],
                "weather_alerts": self.safety_metrics["weather_alerts"],
            },
            "recent_incidents": [{"incident_number": inc.id, "incident_type": inc.type.value, "severity": inc.severity.value, "incident_time": inc.reported_at.isoformat()} for inc in self.active_incidents[-5:]],
            "top_drivers": [{"driver_id": driver_id, "avg_score": round(sum(item["safety_score"] for item in history) / len(history), 1)} for driver_id, history in self.driver_monitoring_history.items() if history][:5],
        }

    async def run(self, payload: dict) -> dict:
        action = payload.get("action") or payload.get("context", {}).get("action") or "status"
        context = payload.get("context", {}) or payload
        if action == "status":
            return await self.get_status()
        if action == "config":
            return await self.get_config()
        if action == "dashboard":
            return await self.get_safety_dashboard()
        if action == "report_incident":
            return await self.report_incident(context.get("incident_type"), context.get("severity"), context.get("description"), context.get("location"), context.get("reporter"), context.get("injured_persons"), context.get("witnesses"))
        if action == "monitor_driver":
            return await self.monitor_driver(int(context.get("driver_id")), int(context.get("hours_driven", 0)), int(context.get("speeding_events", 0)), int(context.get("hard_braking", 0)), int(context.get("rapid_acceleration", 0)), int(context.get("rest_hours", 8)), context.get("heart_rate"))
        if action == "driver_history":
            return await self.get_driver_history(int(context.get("driver_id")), int(context.get("days", 7)))
        if action == "vehicle_sensors":
            return await self.read_vehicle_sensors(int(context.get("vehicle_id")))
        if action == "weather_alerts":
            return await self.get_weather_alerts(context.get("region", "Riyadh"))
        if action == "evaluate_route":
            return await self.evaluate_route_safety(context.get("name", "Active Route"), context.get("region", "Riyadh"), float(context.get("distance_km", 0)), context.get("type", "highway"), int(context.get("speed_limit", 100)))
        if action == "create_preventive_action":
            return await self.create_preventive_action(
                context.get("action_type", "general"),
                context.get("description", "Preventive action created from AI workflow."),
                context.get("priority", "MEDIUM"),
                context.get("assigned_to"),
                context.get("due_date"),
                incident_id=context.get("incident_id"),
                driver_id=context.get("driver_id"),
                vehicle_id=context.get("vehicle_id"),
            )
        if action == "complete_preventive_action":
            return await self.complete_preventive_action(str(context.get("action_id")))
        if action == "daily_report":
            return await self.generate_daily_report()
        return {"error": f"Unknown action: {action}"}

    async def process_message(self, message: str, context: Optional[dict] = None) -> dict:
        context = context or {}
        if context.get("action"):
            return await self.run({"context": context})
        if "incident" in message.lower():
            return await self.run({"action": "report_incident", **context})
        if "driver" in message.lower():
            return await self.run({"action": "monitor_driver", **context})
        if "weather" in message.lower() or "route" in message.lower():
            return await self.run({"action": "weather_alerts", **context})
        if "dashboard" in message.lower():
            return await self.get_safety_dashboard()
        return await self.get_status()

    async def get_status(self) -> dict:
        return {"ok": True, "bot": self.name, "display_name": self.display_name, "version": self.version, "status": self.status, "is_active": self.is_active, "message": "Safety manager is operational"}

    async def get_config(self) -> dict:
        return {
            "name": self.name,
            "display_name": self.display_name,
            "description": self.description,
            "capabilities": [
                "Incident reporting and triage",
                "Driver fatigue and behavior monitoring",
                "Vehicle sensor intelligence",
                "Weather and route risk evaluation",
                "Preventive action management",
                "Daily safety reporting",
            ],
            "version": self.version,
        }


safety_manager = AISafetyManagerBot()
