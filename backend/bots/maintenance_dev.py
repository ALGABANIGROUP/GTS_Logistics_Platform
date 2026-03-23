"""
Maintenance Dev Bot
Error detection, auto-healing, predictive maintenance, update orchestration, and performance analysis.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
import copy
import re
import statistics


class MaintenanceDevBot:
    """Shared-runtime maintenance and repair bot."""

    def __init__(self) -> None:
        self.name = "maintenance_dev"
        self.display_name = "AI Maintenance Dev"
        self.description = "Maintains bot health, detects faults, suggests fixes, and coordinates updates"
        self.version = "2.0.0"
        self.mode = "infrastructure"
        self.is_active = True

        now = datetime.now(timezone.utc)
        self.error_logs: List[Dict[str, Any]] = [
            {
                "error_id": "ERR001",
                "bot_name": "legal_bot",
                "error_type": "timeout",
                "error_message": "Request timeout after 30 seconds during contract review.",
                "severity": "high",
                "status": "new",
                "first_seen": (now - timedelta(hours=5)).isoformat(),
                "last_seen": (now - timedelta(hours=1)).isoformat(),
                "fix_applied": None,
            },
            {
                "error_id": "ERR002",
                "bot_name": "dispatcher",
                "error_type": "database_error",
                "error_message": "Database connection failed while dispatching shipment.",
                "severity": "critical",
                "status": "investigating",
                "first_seen": (now - timedelta(hours=8)).isoformat(),
                "last_seen": (now - timedelta(hours=2)).isoformat(),
                "fix_applied": None,
            },
            {
                "error_id": "ERR003",
                "bot_name": "customer_service",
                "error_type": "memory_leak",
                "error_message": "Memory usage keeps increasing beyond expected baseline.",
                "severity": "medium",
                "status": "new",
                "first_seen": (now - timedelta(days=1)).isoformat(),
                "last_seen": (now - timedelta(hours=6)).isoformat(),
                "fix_applied": None,
            },
        ]
        self.fix_templates: List[Dict[str, Any]] = [
            {
                "pattern": r"(timeout|slow response)",
                "fix_type": "restart",
                "command": "systemctl restart {bot_name}",
                "description": "Restart the bot to recover from response delays.",
                "success_rate": 85,
            },
            {
                "pattern": r"(database|connection).*(error|failed)",
                "fix_type": "reload_config",
                "command": "docker compose restart {bot_name}",
                "description": "Reload configuration and re-establish service connections.",
                "success_rate": 75,
            },
            {
                "pattern": r"(memory|heap).*(leak|overflow|usage)",
                "fix_type": "restart",
                "command": "systemctl restart {bot_name}",
                "description": "Restart the bot to free accumulated memory.",
                "success_rate": 90,
            },
        ]
        self.fix_history: List[Dict[str, Any]] = []
        self.failure_predictions: List[Dict[str, Any]] = [
            {
                "prediction_id": "PRED001",
                "bot_name": "legal_bot",
                "predicted_failure_type": "memory_exhaustion",
                "probability": 75.5,
                "estimated_time_to_failure": 48,
                "recommended_action": "Increase memory or schedule a controlled restart.",
                "predicted_at": (now - timedelta(hours=3)).isoformat(),
            }
        ]
        self.bot_updates: List[Dict[str, Any]] = [
            {
                "update_id": "UPD001",
                "bot_name": "security_manager",
                "current_version": "1.0.0",
                "target_version": "1.1.0",
                "update_type": "minor",
                "status": "scheduled",
                "scheduled_time": (now + timedelta(hours=6)).isoformat(),
                "completed_at": None,
            }
        ]
        self.bot_health: Dict[str, Dict[str, Any]] = {
            "legal_bot": {
                "health_score": 65.5,
                "error_rate": 12.3,
                "avg_response_time": 450,
                "uptime_percent": 92.5,
                "cpu_usage": 45.0,
                "memory_usage": 88.0,
                "uptime_days": 18,
            },
            "dispatcher": {
                "health_score": 95.2,
                "error_rate": 1.2,
                "avg_response_time": 38,
                "uptime_percent": 99.9,
                "cpu_usage": 19.0,
                "memory_usage": 41.0,
                "uptime_days": 7,
            },
            "security_manager": {
                "health_score": 97.0,
                "error_rate": 0.7,
                "avg_response_time": 30,
                "uptime_percent": 99.95,
                "cpu_usage": 12.0,
                "memory_usage": 36.0,
                "uptime_days": 5,
            },
        }
        self.performance_history: Dict[str, List[Dict[str, Any]]] = {
            "dispatcher": [
                {"bot_name": "dispatcher", "response_time": 36, "error_rate": 1.0, "cpu_usage": 18, "memory_usage": 38, "timestamp": (now - timedelta(hours=9)).isoformat()},
                {"bot_name": "dispatcher", "response_time": 38, "error_rate": 1.1, "cpu_usage": 19, "memory_usage": 40, "timestamp": (now - timedelta(hours=8)).isoformat()},
                {"bot_name": "dispatcher", "response_time": 35, "error_rate": 1.0, "cpu_usage": 17, "memory_usage": 39, "timestamp": (now - timedelta(hours=7)).isoformat()},
                {"bot_name": "dispatcher", "response_time": 40, "error_rate": 1.4, "cpu_usage": 20, "memory_usage": 41, "timestamp": (now - timedelta(hours=6)).isoformat()},
                {"bot_name": "dispatcher", "response_time": 42, "error_rate": 1.6, "cpu_usage": 22, "memory_usage": 42, "timestamp": (now - timedelta(hours=5)).isoformat()},
                {"bot_name": "dispatcher", "response_time": 39, "error_rate": 1.2, "cpu_usage": 19, "memory_usage": 41, "timestamp": (now - timedelta(hours=4)).isoformat()},
                {"bot_name": "dispatcher", "response_time": 41, "error_rate": 1.3, "cpu_usage": 20, "memory_usage": 43, "timestamp": (now - timedelta(hours=3)).isoformat()},
                {"bot_name": "dispatcher", "response_time": 37, "error_rate": 1.1, "cpu_usage": 18, "memory_usage": 40, "timestamp": (now - timedelta(hours=2)).isoformat()},
                {"bot_name": "dispatcher", "response_time": 43, "error_rate": 1.5, "cpu_usage": 21, "memory_usage": 42, "timestamp": (now - timedelta(hours=1)).isoformat()},
                {"bot_name": "dispatcher", "response_time": 44, "error_rate": 1.7, "cpu_usage": 23, "memory_usage": 44, "timestamp": now.isoformat()},
            ],
            "legal_bot": [
                {"bot_name": "legal_bot", "response_time": 320, "error_rate": 6.0, "cpu_usage": 34, "memory_usage": 71, "timestamp": (now - timedelta(hours=9)).isoformat()},
                {"bot_name": "legal_bot", "response_time": 340, "error_rate": 6.5, "cpu_usage": 35, "memory_usage": 74, "timestamp": (now - timedelta(hours=8)).isoformat()},
                {"bot_name": "legal_bot", "response_time": 360, "error_rate": 7.0, "cpu_usage": 37, "memory_usage": 76, "timestamp": (now - timedelta(hours=7)).isoformat()},
                {"bot_name": "legal_bot", "response_time": 390, "error_rate": 8.0, "cpu_usage": 40, "memory_usage": 78, "timestamp": (now - timedelta(hours=6)).isoformat()},
                {"bot_name": "legal_bot", "response_time": 420, "error_rate": 9.0, "cpu_usage": 42, "memory_usage": 80, "timestamp": (now - timedelta(hours=5)).isoformat()},
                {"bot_name": "legal_bot", "response_time": 450, "error_rate": 10.0, "cpu_usage": 44, "memory_usage": 83, "timestamp": (now - timedelta(hours=4)).isoformat()},
                {"bot_name": "legal_bot", "response_time": 470, "error_rate": 10.5, "cpu_usage": 45, "memory_usage": 84, "timestamp": (now - timedelta(hours=3)).isoformat()},
                {"bot_name": "legal_bot", "response_time": 490, "error_rate": 11.0, "cpu_usage": 46, "memory_usage": 86, "timestamp": (now - timedelta(hours=2)).isoformat()},
                {"bot_name": "legal_bot", "response_time": 520, "error_rate": 12.0, "cpu_usage": 48, "memory_usage": 88, "timestamp": (now - timedelta(hours=1)).isoformat()},
                {"bot_name": "legal_bot", "response_time": 550, "error_rate": 13.0, "cpu_usage": 50, "memory_usage": 90, "timestamp": now.isoformat()},
            ],
        }
        self.error_patterns = {
            "timeout": [r"timeout", r"timed out", r"connection timeout"],
            "database_error": [r"database.*error", r"connection.*failed", r"mysql.*error"],
            "memory_leak": [r"memory.*leak", r"out of memory", r"heap.*overflow", r"memory usage"],
            "api_error": [r"api.*error", r"invalid response", r"http.*[45][0-9]{2}", r"failed to call"],
            "authentication": [r"unauthorized", r"invalid.*token", r"authentication.*failed"],
        }

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
        if action == "get_errors":
            return await self.get_errors(
                context.get("status") or payload.get("status"),
                context.get("bot_name") or payload.get("bot_name"),
            )
        if action == "resolve_error":
            return await self.resolve_error(
                str(context.get("error_id") or payload.get("error_id") or ""),
                context.get("fix_applied") or payload.get("fix_applied"),
            )
        if action == "try_auto_fix":
            return await self.try_auto_fix(context.get("error_info") or payload.get("error_info") or {})
        if action == "suggest_fixes":
            return await self.suggest_fixes(str(context.get("error_message") or payload.get("error_message") or ""))
        if action == "restart_bot":
            return await self.restart_bot(
                str(context.get("bot_name") or payload.get("bot_name") or ""),
                bool(context.get("force") or payload.get("force") or False),
            )
        if action == "fix_stats":
            return await self.get_fix_stats()
        if action == "predict_failures":
            return await self.predict_failures(str(context.get("bot_name") or payload.get("bot_name") or ""))
        if action == "analyze_bot_trends":
            return await self.analyze_bot_trends(
                str(context.get("bot_name") or payload.get("bot_name") or ""),
                int(context.get("hours") or payload.get("hours") or 24),
            )
        if action == "check_updates":
            return await self.check_updates(
                str(context.get("bot_name") or payload.get("bot_name") or ""),
                str(context.get("current_version") or payload.get("current_version") or "1.0.0"),
            )
        if action == "schedule_update":
            return await self.schedule_update(
                str(context.get("bot_name") or payload.get("bot_name") or ""),
                str(context.get("target_version") or payload.get("target_version") or ""),
                context.get("schedule_time") or payload.get("schedule_time"),
            )
        if action == "execute_update":
            return await self.execute_update(str(context.get("update_id") or payload.get("update_id") or ""))
        if action == "rollback_update":
            return await self.rollback_update(
                str(context.get("bot_name") or payload.get("bot_name") or ""),
                str(context.get("version") or payload.get("version") or ""),
            )
        if action == "pending_updates":
            return await self.get_pending_updates()
        if action == "analyze_performance":
            return await self.analyze_performance(
                str(context.get("bot_name") or payload.get("bot_name") or ""),
                int(context.get("hours") or payload.get("hours") or 24),
            )
        if action == "compare_bots_performance":
            return await self.compare_bots_performance()
        if action == "detect_degradation":
            return await self.detect_degradation(str(context.get("bot_name") or payload.get("bot_name") or ""))
        return await self.status()

    async def process_message(
        self, message: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        text = (message or "").strip().lower()
        context = context or {}

        if "dashboard" in text or "overview" in text:
            return await self.get_dashboard()
        if "error" in text or "fault" in text:
            return await self.report_error(
                str(context.get("bot_name") or "legal_bot"),
                str(context.get("error_message") or "timeout after 30 seconds"),
            )
        if "update" in text:
            return await self.check_updates(
                str(context.get("bot_name") or "security_manager"),
                str(context.get("current_version") or "1.0.0"),
            )
        if "predict" in text or "failure" in text:
            return await self.predict_failures(str(context.get("bot_name") or "legal_bot"))
        if "performance" in text:
            return await self.analyze_performance(str(context.get("bot_name") or "dispatcher"), 24)
        return await self.status()

    async def status(self) -> Dict[str, Any]:
        open_errors = len([item for item in self.error_logs if item["status"] in {"new", "investigating"}])
        pending_updates = len([item for item in self.bot_updates if item["status"] in {"pending", "scheduled"}])
        return {
            "ok": True,
            "bot": self.name,
            "display_name": self.display_name,
            "version": self.version,
            "mode": self.mode,
            "is_active": self.is_active,
            "maintenance_status": {
                "open_errors": open_errors,
                "pending_updates": pending_updates,
                "fix_success_rate": round(self._fix_success_rate(), 2),
            },
            "message": "Maintenance workflows are active.",
        }

    async def config(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "name": self.name,
            "display_name": self.display_name,
            "description": self.description,
            "version": self.version,
            "mode": self.mode,
            "capabilities": [
                "dashboard",
                "report_error",
                "get_errors",
                "resolve_error",
                "try_auto_fix",
                "suggest_fixes",
                "restart_bot",
                "fix_stats",
                "predict_failures",
                "analyze_bot_trends",
                "check_updates",
                "schedule_update",
                "execute_update",
                "rollback_update",
                "pending_updates",
                "analyze_performance",
                "compare_bots_performance",
                "detect_degradation",
            ],
        }

    async def report_error(
        self, bot_name: str, error_message: str, severity: Optional[str] = None
    ) -> Dict[str, Any]:
        if not bot_name or not error_message:
            return {"ok": False, "error": "bot_name and error_message are required"}

        analysis = self._analyze_error(error_message)
        now = datetime.now(timezone.utc)
        error_id = f"ERR{now.strftime('%y%m%d%H%M%S')}{len(self.error_logs):02d}"
        record = {
            "error_id": error_id,
            "bot_name": bot_name,
            "error_type": analysis["error_type"],
            "error_message": error_message,
            "severity": severity or analysis["severity"],
            "status": "new",
            "first_seen": now.isoformat(),
            "last_seen": now.isoformat(),
            "fix_applied": None,
        }
        self.error_logs.append(record)

        fix_result = None
        if analysis["requires_attention"]:
            fix_result = await self.try_auto_fix({"bot_name": bot_name, "error_message": error_message})
            if fix_result.get("ok") and fix_result.get("fixed"):
                record["fix_applied"] = fix_result.get("action_taken")

        return {
            "ok": True,
            "error_id": error_id,
            "analysis": analysis,
            "auto_fix_applied": bool(fix_result and fix_result.get("fixed")),
            "fix_result": fix_result,
        }

    async def get_errors(
        self, status: Optional[str] = None, bot_name: Optional[str] = None
    ) -> Dict[str, Any]:
        items = copy.deepcopy(self.error_logs)
        if status:
            items = [item for item in items if item["status"] == status]
        if bot_name:
            items = [item for item in items if item["bot_name"] == bot_name]
        items.sort(key=lambda item: item["last_seen"], reverse=True)
        return {"ok": True, "count": len(items), "errors": items}

    async def resolve_error(self, error_id: str, fix_applied: Optional[str] = None) -> Dict[str, Any]:
        for item in self.error_logs:
            if item["error_id"] == error_id:
                item["status"] = "fixed"
                item["resolved_at"] = datetime.now(timezone.utc).isoformat()
                item["fix_applied"] = fix_applied or item.get("fix_applied") or "manual_resolution"
                return {"ok": True, "status": "resolved", "error_id": error_id, "fix_applied": item["fix_applied"]}
        return {"ok": False, "error": f"Error '{error_id}' not found"}

    async def try_auto_fix(self, error_info: Dict[str, Any]) -> Dict[str, Any]:
        bot_name = str(error_info.get("bot_name") or "unknown_bot")
        error_message = str(error_info.get("error_message") or "")
        template = self._find_fix_template(error_message)
        if template is None:
            return {"ok": False, "fixed": False, "reason": "No auto-fix template matched the error."}

        action_taken = template["command"].format(bot_name=bot_name)
        success = template.get("success_rate", 0) >= 70
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "bot_name": bot_name,
            "error": error_message[:200],
            "fix_type": template["fix_type"],
            "command": action_taken,
            "success": success,
            "message": template["description"],
        }
        self.fix_history.append(record)
        return {
            "ok": True,
            "fixed": success,
            "fix_type": template["fix_type"],
            "action_taken": action_taken,
            "message": template["description"],
            "estimated_success_rate": template["success_rate"],
        }

    async def suggest_fixes(self, error_message: str) -> Dict[str, Any]:
        suggestions: List[Dict[str, Any]] = []
        for template in self.fix_templates:
            if re.search(template["pattern"], error_message, re.IGNORECASE):
                suggestions.append(
                    {
                        "fix_type": template["fix_type"],
                        "description": template["description"],
                        "command": template["command"],
                        "success_rate": template["success_rate"],
                        "confidence": self._calculate_confidence(error_message, template["pattern"]),
                    }
                )
        return {"ok": True, "count": len(suggestions), "suggestions": suggestions}

    async def restart_bot(self, bot_name: str, force: bool = False) -> Dict[str, Any]:
        if not bot_name:
            return {"ok": False, "error": "bot_name is required"}
        action = f"restart:{bot_name}"
        if force:
            action += ":force"
        self.fix_history.append(
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "bot_name": bot_name,
                "error": "manual_restart",
                "fix_type": "restart",
                "command": action,
                "success": True,
                "message": "Manual restart issued.",
            }
        )
        return {
            "ok": True,
            "success": True,
            "bot_name": bot_name,
            "action": "restart",
            "force": force,
            "message": f"Restart command queued for {bot_name}.",
        }

    async def get_fix_stats(self) -> Dict[str, Any]:
        total = len(self.fix_history)
        successful = len([item for item in self.fix_history if item["success"]])
        by_type: Dict[str, int] = {}
        for item in self.fix_history:
            by_type[item["fix_type"]] = by_type.get(item["fix_type"], 0) + 1
        return {
            "ok": True,
            "total_attempts": total,
            "successful_fixes": successful,
            "success_rate": round((successful / total) * 100, 2) if total else 0.0,
            "fixes_by_type": by_type,
            "last_fix": copy.deepcopy(self.fix_history[-1]) if self.fix_history else None,
        }

    async def predict_failures(self, bot_name: str) -> Dict[str, Any]:
        stats = self.bot_health.get(bot_name)
        if not stats:
            return {"ok": False, "error": f"No health data found for '{bot_name}'"}

        probability = self._predict_failure_probability(stats)
        schedule = self._suggest_maintenance_schedule(bot_name, stats)
        return {
            "ok": True,
            "bot_name": bot_name,
            "failure_analysis": probability,
            "maintenance_schedule": schedule,
            "predicted_at": datetime.now(timezone.utc).isoformat(),
        }

    async def analyze_bot_trends(self, bot_name: str, hours: int = 24) -> Dict[str, Any]:
        history = self._get_bot_metrics(bot_name, hours)
        if len(history) < 5:
            return {"ok": False, "error": f"Not enough trend data for '{bot_name}'"}

        predictions: List[Dict[str, Any]] = []
        for metric, threshold in (
            ("error_rate", 10),
            ("response_time", 500),
            ("cpu_usage", 80),
            ("memory_usage", 90),
        ):
            values = [float(item.get(metric, 0)) for item in history]
            slope = self._linear_slope(values)
            current = values[-1]
            predicted = current + (slope * 10)
            if predicted > threshold or slope > 1:
                predictions.append(
                    {
                        "metric": metric,
                        "current_value": round(current, 2),
                        "predicted_value": round(predicted, 2),
                        "trend_slope": round(slope, 3),
                        "severity": "high" if predicted > threshold else "medium",
                    }
                )

        return {
            "ok": True,
            "bot_name": bot_name,
            "analysis_time": datetime.now(timezone.utc).isoformat(),
            "predictions": predictions,
            "points": len(history),
        }

    async def check_updates(self, bot_name: str, current_version: str) -> Dict[str, Any]:
        available_updates = {
            "security_manager": {"latest": "1.2.0", "type": "security", "critical": True},
            "legal_bot": {"latest": "1.1.0", "type": "minor", "critical": False},
            "dispatcher": {"latest": "2.0.0", "type": "major", "critical": True},
        }
        update_info = available_updates.get(bot_name)
        if update_info and update_info["latest"] != current_version:
            return {
                "ok": True,
                "update_available": True,
                "bot_name": bot_name,
                "current_version": current_version,
                "latest_version": update_info["latest"],
                "update_type": update_info["type"],
                "critical": update_info["critical"],
                "changelog": self._get_changelog(bot_name, update_info["latest"]),
            }
        return {
            "ok": True,
            "update_available": False,
            "bot_name": bot_name,
            "current_version": current_version,
            "message": "No updates are currently available.",
        }

    async def schedule_update(
        self, bot_name: str, target_version: str, schedule_time: Optional[str] = None
    ) -> Dict[str, Any]:
        if not bot_name or not target_version:
            return {"ok": False, "error": "bot_name and target_version are required"}
        scheduled_time = schedule_time or (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
        update_id = f"UPD{datetime.now(timezone.utc).strftime('%y%m%d%H%M%S')}{len(self.bot_updates):02d}"
        update = {
            "update_id": update_id,
            "bot_name": bot_name,
            "current_version": "unknown",
            "target_version": target_version,
            "update_type": "scheduled",
            "status": "scheduled",
            "scheduled_time": scheduled_time,
            "completed_at": None,
        }
        self.bot_updates.append(update)
        return {"ok": True, **copy.deepcopy(update)}

    async def execute_update(self, update_id: str) -> Dict[str, Any]:
        for update in self.bot_updates:
            if update["update_id"] == update_id:
                update["status"] = "completed"
                update["completed_at"] = datetime.now(timezone.utc).isoformat()
                return {
                    "ok": True,
                    "success": True,
                    "update_id": update_id,
                    "bot_name": update["bot_name"],
                    "target_version": update["target_version"],
                    "completed_at": update["completed_at"],
                }
        return {"ok": False, "error": f"Update '{update_id}' not found"}

    async def rollback_update(self, bot_name: str, version: str) -> Dict[str, Any]:
        if not bot_name or not version:
            return {"ok": False, "error": "bot_name and version are required"}
        return {
            "ok": True,
            "success": True,
            "bot_name": bot_name,
            "rolled_back_to": version,
            "rolled_back_at": datetime.now(timezone.utc).isoformat(),
            "message": f"Rollback prepared for {bot_name}.",
        }

    async def get_pending_updates(self) -> Dict[str, Any]:
        updates = [copy.deepcopy(item) for item in self.bot_updates if item["status"] in {"pending", "scheduled"}]
        return {"ok": True, "count": len(updates), "updates": updates}

    async def analyze_performance(self, bot_name: str, hours: int = 24) -> Dict[str, Any]:
        metrics = self._get_bot_metrics(bot_name, hours)
        if len(metrics) < 5:
            return {"ok": False, "error": f"Not enough performance data for '{bot_name}'"}

        response_times = [float(item["response_time"]) for item in metrics if item.get("response_time") is not None]
        error_rates = [float(item["error_rate"]) for item in metrics if item.get("error_rate") is not None]
        cpu_usages = [float(item["cpu_usage"]) for item in metrics if item.get("cpu_usage") is not None]

        stats = {
            "response_time": {
                "avg": round(statistics.mean(response_times), 2) if response_times else 0,
                "min": round(min(response_times), 2) if response_times else 0,
                "max": round(max(response_times), 2) if response_times else 0,
                "p95": round(self._percentile(response_times, 95), 2) if response_times else 0,
            },
            "error_rate": {
                "avg": round(statistics.mean(error_rates), 2) if error_rates else 0,
                "trend": self._trend(error_rates),
            },
            "cpu_usage": {
                "avg": round(statistics.mean(cpu_usages), 2) if cpu_usages else 0,
                "peak": round(max(cpu_usages), 2) if cpu_usages else 0,
            },
        }
        health_score = self._calculate_health_score(stats)
        return {
            "ok": True,
            "bot_name": bot_name,
            "analysis_period": f"{len(metrics)} points",
            "statistics": stats,
            "health_score": health_score,
            "performance_grade": self._grade(health_score),
            "recommendations": self._performance_recommendations(stats),
        }

    async def compare_bots_performance(self) -> Dict[str, Any]:
        comparison: Dict[str, Dict[str, Any]] = {}
        for bot_name, metrics in self.performance_history.items():
            response_times = [float(item["response_time"]) for item in metrics if item.get("response_time") is not None]
            error_rates = [float(item["error_rate"]) for item in metrics if item.get("error_rate") is not None]
            comparison[bot_name] = {
                "avg_response_time": round(statistics.mean(response_times), 2) if response_times else 0,
                "avg_error_rate": round(statistics.mean(error_rates), 2) if error_rates else 0,
                "data_points": len(metrics),
            }

        ordered = sorted(comparison.items(), key=lambda item: (item[1]["avg_error_rate"], item[1]["avg_response_time"]))
        return {
            "ok": True,
            "comparison": comparison,
            "best_performing": ordered[0][0] if ordered else None,
            "worst_performing": ordered[-1][0] if ordered else None,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    async def detect_degradation(self, bot_name: str) -> Dict[str, Any]:
        metrics = self._get_bot_metrics(bot_name, 48)
        if len(metrics) < 10:
            return {"ok": True, "bot_name": bot_name, "degradations": []}

        half = len(metrics) // 2
        first_half = metrics[:half]
        second_half = metrics[half:]
        degradations: List[Dict[str, Any]] = []
        for metric in ("response_time", "error_rate", "cpu_usage"):
            first_values = [float(item.get(metric, 0)) for item in first_half]
            second_values = [float(item.get(metric, 0)) for item in second_half]
            first_avg = statistics.mean(first_values) if first_values else 0
            second_avg = statistics.mean(second_values) if second_values else 0
            if first_avg <= 0:
                continue
            delta = ((second_avg - first_avg) / first_avg) * 100
            if delta > 20:
                degradations.append(
                    {
                        "metric": metric,
                        "degradation_percent": round(delta, 2),
                        "first_avg": round(first_avg, 2),
                        "second_avg": round(second_avg, 2),
                        "severity": "high" if delta > 50 else "medium",
                    }
                )
        return {"ok": True, "bot_name": bot_name, "degradations": degradations}

    async def get_dashboard(self) -> Dict[str, Any]:
        active_errors = [item for item in self.error_logs if item["status"] in {"new", "investigating"}]
        pending_updates = [item for item in self.bot_updates if item["status"] in {"pending", "scheduled"}]
        fix_stats = await self.get_fix_stats()
        performance = await self.compare_bots_performance()
        return {
            "ok": True,
            "active_errors": len(active_errors),
            "critical_errors": len([item for item in active_errors if item["severity"] == "critical"]),
            "fix_success_rate": fix_stats["success_rate"],
            "pending_updates": len(pending_updates),
            "bot_health": {
                "best": performance.get("best_performing"),
                "worst": performance.get("worst_performing"),
            },
            "open_error_ids": [item["error_id"] for item in active_errors[:5]],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def _analyze_error(self, error_message: str) -> Dict[str, Any]:
        error_type = "unknown"
        confidence = 0
        matched_pattern = None
        for candidate_type, patterns in self.error_patterns.items():
            for pattern in patterns:
                if re.search(pattern, error_message, re.IGNORECASE):
                    error_type = candidate_type
                    confidence = 80 + (len(pattern) % 20)
                    matched_pattern = pattern
                    break
            if confidence:
                break

        severity = self._error_severity(error_type, error_message)
        return {
            "error_type": error_type,
            "severity": severity,
            "confidence": confidence,
            "matched_pattern": matched_pattern,
            "suggested_fix": self._suggested_fix(error_type),
            "requires_attention": severity in {"high", "critical"},
        }

    def _error_severity(self, error_type: str, error_message: str) -> str:
        text = error_message.lower()
        if any(keyword in text for keyword in ("critical", "fatal", "panic")):
            return "critical"
        mapping = {
            "timeout": "medium",
            "database_error": "high",
            "memory_leak": "high",
            "api_error": "medium",
            "authentication": "high",
        }
        return mapping.get(error_type, "low")

    def _suggested_fix(self, error_type: str) -> str:
        fixes = {
            "timeout": "Restart the bot or raise the timeout threshold.",
            "database_error": "Verify the database connection and reload service configuration.",
            "memory_leak": "Restart the bot and review memory-heavy workflows.",
            "api_error": "Check upstream API availability and retry rules.",
            "authentication": "Refresh credentials or rotate the service token.",
        }
        return fixes.get(error_type, "Review detailed logs for a manual fix.")

    def _find_fix_template(self, error_message: str) -> Optional[Dict[str, Any]]:
        for template in self.fix_templates:
            if re.search(template["pattern"], error_message, re.IGNORECASE):
                return template
        return None

    def _calculate_confidence(self, error_message: str, pattern: str) -> int:
        confidence = 70
        if re.search(pattern, error_message, re.IGNORECASE):
            confidence += 20
        return min(confidence, 100)

    def _fix_success_rate(self) -> float:
        if not self.fix_history:
            return 0.0
        successful = len([item for item in self.fix_history if item["success"]])
        return (successful / len(self.fix_history)) * 100

    def _predict_failure_probability(self, bot_stats: Dict[str, Any]) -> Dict[str, Any]:
        probability = 0
        factors: List[str] = []
        error_rate = float(bot_stats.get("error_rate", 0))
        response_time = float(bot_stats.get("avg_response_time", 0))
        uptime_days = float(bot_stats.get("uptime_days", 0))
        cpu_usage = float(bot_stats.get("cpu_usage", 0))
        memory_usage = float(bot_stats.get("memory_usage", 0))

        if error_rate > 10:
            probability += 30
            factors.append(f"High error rate: {error_rate}%")
        elif error_rate > 5:
            probability += 15
            factors.append(f"Moderate error rate: {error_rate}%")

        if response_time > 500:
            probability += 25
            factors.append(f"High response time: {response_time}ms")
        elif response_time > 200:
            probability += 10
            factors.append(f"Elevated response time: {response_time}ms")

        if uptime_days > 30:
            probability += 20
            factors.append(f"Long uptime without restart: {uptime_days} days")

        if cpu_usage > 80:
            probability += 25
            factors.append(f"High CPU usage: {cpu_usage}%")

        if memory_usage > 90:
            probability += 30
            factors.append(f"High memory usage: {memory_usage}%")
        elif memory_usage > 70:
            probability += 15
            factors.append(f"Elevated memory usage: {memory_usage}%")

        if probability >= 70:
            risk_level = "critical"
            action = "Immediate intervention required."
        elif probability >= 50:
            risk_level = "high"
            action = "Schedule urgent maintenance."
        elif probability >= 30:
            risk_level = "medium"
            action = "Keep the bot under close monitoring."
        else:
            risk_level = "low"
            action = "No immediate maintenance risk detected."

        return {
            "failure_probability": min(probability, 100),
            "risk_level": risk_level,
            "factors": factors,
            "recommended_action": action,
            "estimated_time_to_failure": self._eta_to_failure(probability),
        }

    def _suggest_maintenance_schedule(self, bot_name: str, current_health: Dict[str, Any]) -> Dict[str, Any]:
        health_score = float(current_health.get("health_score", 100))
        if health_score > 90:
            frequency = "monthly"
            next_maintenance = datetime.now(timezone.utc) + timedelta(days=30)
            tasks = ["Routine check", "Log review"]
        elif health_score > 70:
            frequency = "biweekly"
            next_maintenance = datetime.now(timezone.utc) + timedelta(days=14)
            tasks = ["Performance check", "Cache cleanup", "Error review"]
        elif health_score > 50:
            frequency = "weekly"
            next_maintenance = datetime.now(timezone.utc) + timedelta(days=7)
            tasks = ["Performance tuning", "Restart plan", "Configuration review"]
        else:
            frequency = "immediate"
            next_maintenance = datetime.now(timezone.utc) + timedelta(hours=12)
            tasks = ["Urgent maintenance", "Root-cause analysis", "Targeted repair"]

        return {
            "bot_name": bot_name,
            "current_health_score": health_score,
            "recommended_frequency": frequency,
            "next_maintenance": next_maintenance.isoformat(),
            "suggested_tasks": tasks,
            "priority": "high" if health_score < 60 else "medium" if health_score < 80 else "low",
        }

    def _eta_to_failure(self, probability: float) -> str:
        if probability >= 80:
            return "within 24 hours"
        if probability >= 60:
            return "within 2-3 days"
        if probability >= 40:
            return "within a week"
        if probability >= 20:
            return "within two weeks"
        return "more than a month"

    def _linear_slope(self, values: List[float]) -> float:
        n = len(values)
        if n < 2:
            return 0.0
        x_values = list(range(n))
        sum_x = sum(x_values)
        sum_y = sum(values)
        sum_xy = sum(x_values[i] * values[i] for i in range(n))
        sum_x2 = sum(x * x for x in x_values)
        denominator = (n * sum_x2) - (sum_x * sum_x)
        if denominator == 0:
            return 0.0
        return ((n * sum_xy) - (sum_x * sum_y)) / denominator

    def _get_bot_metrics(self, bot_name: str, hours: int) -> List[Dict[str, Any]]:
        history = self.performance_history.get(bot_name, [])
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
        return [
            copy.deepcopy(item)
            for item in history
            if datetime.fromisoformat(item["timestamp"]) >= cutoff
        ]

    def _percentile(self, values: List[float], percentile: int) -> float:
        if not values:
            return 0.0
        ordered = sorted(values)
        index = min(len(ordered) - 1, int(len(ordered) * percentile / 100))
        return ordered[index]

    def _trend(self, values: List[float]) -> str:
        if len(values) < 3:
            return "insufficient_data"
        if values[-1] > values[0] * 1.1:
            return "rising"
        if values[-1] < values[0] * 0.9:
            return "falling"
        return "stable"

    def _calculate_health_score(self, stats: Dict[str, Any]) -> float:
        score = 100.0
        response_time = float(stats["response_time"]["avg"])
        error_rate = float(stats["error_rate"]["avg"])
        cpu_usage = float(stats["cpu_usage"]["avg"])

        if response_time > 500:
            score -= 30
        elif response_time > 200:
            score -= 15
        elif response_time > 100:
            score -= 5

        if error_rate > 10:
            score -= 40
        elif error_rate > 5:
            score -= 20
        elif error_rate > 1:
            score -= 5

        if cpu_usage > 80:
            score -= 25
        elif cpu_usage > 60:
            score -= 10

        return max(0.0, min(100.0, round(score, 2)))

    def _grade(self, score: float) -> str:
        if score >= 90:
            return "A"
        if score >= 75:
            return "B"
        if score >= 60:
            return "C"
        if score >= 40:
            return "D"
        return "F"

    def _performance_recommendations(self, stats: Dict[str, Any]) -> List[str]:
        recommendations: List[str] = []
        if stats["response_time"]["avg"] > 300:
            recommendations.append("Response time is elevated; review the hottest code path or add headroom.")
        if stats["error_rate"]["avg"] > 5:
            recommendations.append("Error rate is elevated; inspect recent incidents and retry policies.")
        if stats["cpu_usage"]["avg"] > 70:
            recommendations.append("CPU usage is elevated; rebalance load or schedule maintenance.")
        if stats["response_time"]["p95"] > stats["response_time"]["avg"] * 2:
            recommendations.append("Latency variance is high; look for intermittent bottlenecks.")
        return recommendations

    def _get_changelog(self, bot_name: str, target_version: str) -> List[str]:
        changelogs = {
            "security_manager": {
                "1.1.0": ["Improved intrusion rules", "Added MFA reliability fixes"],
                "1.2.0": ["Threat signature refresh", "Lower monitoring overhead"],
            },
            "legal_bot": {
                "1.1.0": ["Expanded legal reference set", "Faster contract parsing"],
            },
            "dispatcher": {
                "2.0.0": ["New routing engine", "Higher live-tracking throughput"],
            },
        }
        return changelogs.get(bot_name, {}).get(target_version, ["General maintenance update"])
