# backend/ai/bots/maintenance_dev.py
from __future__ import annotations

import os
from datetime import datetime
from typing import Any, Dict, Optional

class AIMaintenanceDevBot:
    """
    Lightweight maintenance/dev bot.
    - Safe status(): never calls external services; always returns a valid dict.
    - run(payload): supports basic actions without DB dependency.
      Actions:
        - "scan": return a quick synthetic checklist
        - "register_task": echo back a normalized task (no DB insert here)
        - "health_check": return a simple OK map
    """

    name = "maintenance_dev"

    def _enabled(self) -> bool:
        return os.getenv("MAINT_DEV_ENABLED", "1") in ("1", "true", "True", "yes", "on")

    def status(self) -> Dict[str, Any]:
        try:
            enabled = self._enabled()
            cron = os.getenv("MAINT_SCHEDULE_CRON", "0 3 * * *")   # daily at 03:00 as a default
            targets = os.getenv("MAINT_TARGETS", "api,db,ai,frontend").split(",")
            return {
                "ok": True,
                "role": self.name,
                "mode": "online" if enabled else "offline",
                "enabled": enabled,
                "cron": cron,
                "targets": [t.strip() for t in targets if t.strip()],
                "timestamp": datetime.utcnow().isoformat(),
            }
        except Exception as e:
            return {
                "ok": False,
                "role": self.name,
                "mode": "offline",
                "reason": f"status_error: {e.__class__.__name__}",
                "timestamp": datetime.utcnow().isoformat(),
            }

    def run(self, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute a lightweight action without external dependencies.
        Expected payload:
          {
            "action": "scan" | "register_task" | "health_check",
            "task": { "title": "...", "component": "api|db|ai|frontend", "severity": "low|med|high", "due_at": "YYYY-MM-DD" }
          }
        """
        payload = payload or {}
        action = (payload.get("action") or "scan").lower()

        if action == "scan":
            return {
                "ok": True,
                "role": self.name,
                "action": "scan",
                "checklist": [
                    {"component": "api", "status": "ok"},
                    {"component": "db", "status": "ok"},
                    {"component": "ai", "status": "ok"},
                    {"component": "frontend", "status": "ok"},
                ],
                "timestamp": datetime.utcnow().isoformat(),
            }

        if action == "health_check":
            return {
                "ok": True,
                "role": self.name,
                "action": "health_check",
                "summary": {
                    "api": "ok",
                    "db": "ok",
                    "ai": "ok",
                    "frontend": "ok",
                },
                "timestamp": datetime.utcnow().isoformat(),
            }

        if action == "register_task":
            task = payload.get("task") or {}
            normalized = {
                "title": str(task.get("title") or "Maintenance task"),
                "component": str(task.get("component") or "api"),
                "severity": str(task.get("severity") or "low"),
                "due_at": str(task.get("due_at") or ""),
                "created_at": datetime.utcnow().isoformat(),
            }
            return {
                "ok": True,
                "role": self.name,
                "action": "register_task",
                "task": normalized,
                "note": "Task accepted (no DB insert in this lightweight version).",
            }

        return {
            "ok": False,
            "role": self.name,
            "action": action,
            "reason": "unknown_action",
        }
