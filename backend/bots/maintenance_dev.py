"""
Maintenance Dev bot runtime used by startup registration and legacy routes.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional


class MaintenanceDevBot:
    name = "maintenance_dev"
    display_name = "Maintenance Dev Bot"
    description = "Manages system maintenance, auto-repair, and development support"

    def __init__(self) -> None:
        now = datetime.now(timezone.utc)
        self.active_errors: List[Dict[str, Any]] = []
        self.resolved_errors: List[Dict[str, Any]] = []
        self.pending_updates: List[Dict[str, Any]] = [
            {
                "bot_name": "security_manager",
                "current_version": "1.0.0",
                "target_version": "1.1.0",
                "update_type": "minor",
                "status": "scheduled",
                "scheduled_time": (now + timedelta(hours=6)).isoformat(),
            }
        ]
        self.bot_health: Dict[str, Dict[str, Any]] = {
            "dispatcher": {"health_score": 95.2, "error_rate": 1.2, "avg_response_time": 38, "uptime_percent": 99.9},
            "legal_bot": {"health_score": 65.5, "error_rate": 12.3, "avg_response_time": 450, "uptime_percent": 92.5},
            "security_manager": {"health_score": 97.0, "error_rate": 0.7, "avg_response_time": 30, "uptime_percent": 99.95},
        }
        self.performance_history: Dict[str, List[Dict[str, Any]]] = {
            "dispatcher": [
                {"response_time": 36, "error_rate": 1.0, "timestamp": (now - timedelta(hours=2)).isoformat()},
                {"response_time": 38, "error_rate": 1.1, "timestamp": (now - timedelta(hours=1)).isoformat()},
                {"response_time": 41, "error_rate": 1.4, "timestamp": now.isoformat()},
            ],
            "legal_bot": [
                {"response_time": 420, "error_rate": 9.0, "timestamp": (now - timedelta(hours=2)).isoformat()},
                {"response_time": 470, "error_rate": 10.5, "timestamp": (now - timedelta(hours=1)).isoformat()},
                {"response_time": 520, "error_rate": 12.0, "timestamp": now.isoformat()},
            ],
        }
        self.fix_attempts: List[Dict[str, Any]] = []

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        context = payload.get("context", {}) or {}
        action = (
            payload.get("action")
            or context.get("action")
            or payload.get("meta", {}).get("action")
            or "status"
        )

        if action == "status":
            return await self.status()
        if action == "config":
            return await self.config()
        if action == "dashboard":
            return await self.get_dashboard()
        if action == "report_error":
            return await self.report_error(
                str(context.get("bot_name") or payload.get("bot_name") or ""),
                str(context.get("error_message") or payload.get("error_message") or ""),
                context.get("severity") or payload.get("severity"),
            )
        if action == "resolve_error":
            return await self.resolve_error(
                str(context.get("error_id") or payload.get("error_id") or ""),
                context.get("fix_applied") or payload.get("fix_applied"),
            )
        if action == "fix_stats":
            return await self.fix_stats()
        if action == "check_updates":
            return await self.check_updates(
                str(context.get("bot_name") or payload.get("bot_name") or ""),
                str(context.get("current_version") or payload.get("current_version") or "1.0.0"),
            )
        if action == "analyze_performance":
            return await self.analyze_performance(
                str(context.get("bot_name") or payload.get("bot_name") or ""),
                int(context.get("hours") or payload.get("hours") or 24),
            )
        if action == "predict_failures":
            return await self.predict_failures(str(context.get("bot_name") or payload.get("bot_name") or ""))
        return {"ok": False, "error": f"Unknown action: {action}"}

    async def process_message(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        context = context or {}
        if context.get("action"):
            return await self.run({"context": context})
        if context.get("bot_name") and context.get("error_message"):
            return await self.report_error(
                str(context["bot_name"]),
                str(context["error_message"]),
                context.get("severity"),
            )
        if "dashboard" in (message or "").lower():
            return await self.get_dashboard()
        return await self.status()

    async def get_dashboard(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "active_errors": deepcopy(self.active_errors),
            "pending_updates": deepcopy(self.pending_updates),
            "bot_health": deepcopy(self.bot_health),
            "total_fix_attempts": len(self.fix_attempts),
        }

    async def report_error(self, bot_name: str, error_message: str, severity: Optional[str] = None) -> Dict[str, Any]:
        error_type = self._classify_error(error_message)
        error_id = f"ERR-{len(self.active_errors) + len(self.resolved_errors) + 1:04d}"
        record = {
            "error_id": error_id,
            "bot_name": bot_name or "unknown",
            "error_message": error_message,
            "severity": severity or ("critical" if error_type == "database_error" else "high" if error_type == "timeout" else "medium"),
            "status": "active",
            "reported_at": datetime.now(timezone.utc).isoformat(),
        }
        self.active_errors.append(record)
        analysis = {
            "error_type": error_type,
            "recommended_fix": self._recommended_fix(error_type),
        }
        fix_result = None
        auto_fix_applied = False
        if error_type == "memory_leak":
            auto_fix_applied = True
            fix_result = {
                "action": "restart_worker",
                "status": "completed",
            }
            self.fix_attempts.append({"error_id": error_id, "fix_applied": fix_result["action"], "status": "completed"})
        return {
            "ok": True,
            "error_id": error_id,
            "analysis": analysis,
            "auto_fix_applied": auto_fix_applied,
            "fix_result": fix_result,
        }

    async def resolve_error(self, error_id: str, fix_applied: Optional[str]) -> Dict[str, Any]:
        record = next((item for item in self.active_errors if item["error_id"] == error_id), None)
        if not record:
            return {"ok": False, "error": "Error not found"}
        self.active_errors = [item for item in self.active_errors if item["error_id"] != error_id]
        resolved = deepcopy(record)
        resolved["status"] = "resolved"
        resolved["resolved_at"] = datetime.now(timezone.utc).isoformat()
        resolved["fix_applied"] = fix_applied
        self.resolved_errors.append(resolved)
        self.fix_attempts.append({"error_id": error_id, "fix_applied": fix_applied, "status": "resolved"})
        return {"ok": True, "status": "resolved", "error": resolved}

    async def fix_stats(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "total_attempts": len(self.fix_attempts),
            "resolved_errors": len(self.resolved_errors),
            "active_errors": len(self.active_errors),
        }

    async def check_updates(self, bot_name: str, current_version: str) -> Dict[str, Any]:
        update = next((item for item in self.pending_updates if item["bot_name"] == bot_name), None)
        return {
            "ok": True,
            "bot_name": bot_name,
            "current_version": current_version,
            "update_available": update is not None,
            "update": deepcopy(update),
        }

    async def analyze_performance(self, bot_name: str, hours: int) -> Dict[str, Any]:
        history = self.performance_history.get(bot_name, [])
        response_times = [item["response_time"] for item in history]
        error_rates = [item["error_rate"] for item in history]
        stats = {
            "avg_response_time": round(sum(response_times) / max(len(response_times), 1), 2) if response_times else 0,
            "max_response_time": max(response_times) if response_times else 0,
            "avg_error_rate": round(sum(error_rates) / max(len(error_rates), 1), 2) if error_rates else 0,
            "samples": len(history),
            "hours": hours,
        }
        return {"ok": True, "bot_name": bot_name, "statistics": stats, "history": deepcopy(history)}

    async def predict_failures(self, bot_name: str) -> Dict[str, Any]:
        health = self.bot_health.get(bot_name, {})
        error_rate = float(health.get("error_rate", 0))
        failure_probability = min(0.95, round((error_rate / 20.0) + 0.05, 2))
        return {
            "ok": True,
            "bot_name": bot_name,
            "failure_analysis": {
                "failure_probability": failure_probability,
                "risk_level": "high" if failure_probability >= 0.6 else "medium" if failure_probability >= 0.3 else "low",
            },
        }

    async def status(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "name": self.name,
            "display_name": self.display_name,
            "status": "active",
            "description": self.description,
        }

    async def config(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "name": self.name,
            "display_name": self.display_name,
            "description": self.description,
            "actions": [
                "dashboard",
                "report_error",
                "resolve_error",
                "fix_stats",
                "check_updates",
                "analyze_performance",
                "predict_failures",
            ],
        }

    def _classify_error(self, error_message: str) -> str:
        lowered = (error_message or "").lower()
        if "timeout" in lowered:
            return "timeout"
        if "database" in lowered or "connection failed" in lowered:
            return "database_error"
        if "memory" in lowered:
            return "memory_leak"
        if "token" in lowered or "unauthorized" in lowered:
            return "authentication"
        return "general_error"

    def _recommended_fix(self, error_type: str) -> str:
        recommendations = {
            "timeout": "Increase timeout or inspect slow dependency",
            "database_error": "Reconnect pool and validate database availability",
            "memory_leak": "Restart worker and inspect memory growth",
            "authentication": "Rotate credentials and verify token issuer",
            "general_error": "Inspect logs and reproduce with debug mode",
        }
        return recommendations.get(error_type, recommendations["general_error"])

