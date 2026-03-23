"""
Operations Manager Bot
Cross-bot coordination, alert routing, and operational orchestration.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
import copy


class OperationsManagerBot:
    """Operational command bot that coordinates reports, alerts, and workflows."""

    def __init__(self) -> None:
        self.name = "operations_manager"
        self.display_name = "AI Operations Manager"
        self.description = "Coordinates workflows, alerts, and task execution across bots"
        self.version = "2.0.0"
        self.mode = "orchestration"
        self.is_active = True

        now = datetime.now(timezone.utc)
        self.reports: List[Dict[str, Any]] = [
            {
                "report_id": "RPT001",
                "source_bot": "dispatcher",
                "report_type": "shipment_delay",
                "severity": "high",
                "summary": "Shipment SH-1234 is delayed by 3 hours due to heavy congestion.",
                "data": {"shipment_id": "SH-1234", "delay_hours": 3, "reason": "traffic"},
                "received_at": (now - timedelta(hours=2)).isoformat(),
                "requires_action": True,
            },
            {
                "report_id": "RPT002",
                "source_bot": "safety_bot",
                "report_type": "incident",
                "severity": "critical",
                "summary": "Roadside incident detected with no injuries reported.",
                "data": {"incident_id": "INC-1001", "location": "Riyadh Ring Road", "injuries": 0},
                "received_at": (now - timedelta(hours=1, minutes=10)).isoformat(),
                "requires_action": True,
            },
            {
                "report_id": "RPT003",
                "source_bot": "finance_bot",
                "report_type": "invoice_overdue",
                "severity": "medium",
                "summary": "A customer invoice remains unpaid after 15 days.",
                "data": {"customer": "Al Amal Co.", "amount": 50000, "days_overdue": 15},
                "received_at": (now - timedelta(minutes=35)).isoformat(),
                "requires_action": False,
            },
        ]
        self.commands: List[Dict[str, Any]] = [
            {
                "command_id": "CMD001",
                "target_bot": "customer_service",
                "command_type": "notify_customer",
                "priority": "high",
                "status": "executed",
                "issued_at": (now - timedelta(hours=1, minutes=55)).isoformat(),
            },
            {
                "command_id": "CMD002",
                "target_bot": "dispatcher",
                "command_type": "reschedule_shipment",
                "priority": "high",
                "status": "in_progress",
                "issued_at": (now - timedelta(hours=1, minutes=50)).isoformat(),
            },
        ]
        self.cross_bot_tasks: List[Dict[str, Any]] = [
            {
                "task_id": "WF001",
                "workflow_name": "new_shipment",
                "status": "completed",
                "progress": 100,
                "current_step": "completed",
                "steps": 5,
                "completed_at": (now - timedelta(hours=3)).isoformat(),
            },
            {
                "task_id": "WF002",
                "workflow_name": "incident_response",
                "status": "in_progress",
                "progress": 60,
                "current_step": "customer notification",
                "steps": 5,
                "completed_at": None,
            },
        ]
        self.composite_alerts: List[Dict[str, Any]] = [
            {
                "alert_id": "ALT-C001",
                "severity": "critical",
                "description": "Incident and shipment-delay alerts are correlated on the same route corridor.",
                "source_bots": ["dispatcher", "safety_bot"],
                "related_alerts": ["RPT001", "RPT002"],
                "correlation_score": 86,
                "recommended_actions": [
                    "Route remaining loads away from the incident corridor.",
                    "Notify affected customers immediately.",
                ],
                "assigned_bots": ["dispatcher", "customer_service", "safety_bot"],
                "status": "active",
                "created_at": (now - timedelta(minutes=55)).isoformat(),
            }
        ]
        self.orchestration_log: List[Dict[str, Any]] = [
            {
                "log_type": "report_received",
                "reference_id": "RPT001",
                "description": "Delay report received from dispatcher.",
                "created_at": (now - timedelta(hours=2)).isoformat(),
            },
            {
                "log_type": "gm_escalated",
                "reference_id": "RPT002",
                "description": "Critical incident escalated to General Manager.",
                "created_at": (now - timedelta(hours=1)).isoformat(),
            },
        ]
        self.workflow_templates: Dict[str, Dict[str, Any]] = {
            "new_customer": {
                "name": "New customer onboarding",
                "steps": [
                    {"bot": "sales_bot", "action": "register_customer", "description": "Register customer profile"},
                    {"bot": "finance_bot", "action": "create_account", "description": "Create finance account"},
                    {"bot": "documents_manager", "action": "generate_contract", "description": "Generate contract"},
                    {"bot": "partner_manager", "action": "assign_partner", "description": "Assign partner"},
                    {"bot": "customer_service", "action": "send_welcome", "description": "Send welcome pack"},
                ],
            },
            "new_shipment": {
                "name": "New shipment workflow",
                "steps": [
                    {"bot": "freight_broker", "action": "book_shipment", "description": "Book the shipment"},
                    {"bot": "dispatcher", "action": "assign_driver", "description": "Assign driver"},
                    {"bot": "safety_bot", "action": "check_route", "description": "Run route safety check"},
                    {"bot": "documents_manager", "action": "generate_waybill", "description": "Generate waybill"},
                    {"bot": "customer_service", "action": "notify_customer", "description": "Notify customer"},
                ],
            },
            "incident_response": {
                "name": "Incident response",
                "steps": [
                    {"bot": "dispatcher", "action": "stop_truck", "description": "Stop truck"},
                    {"bot": "safety_bot", "action": "dispatch_help", "description": "Dispatch safety help"},
                    {"bot": "legal_bot", "action": "document_incident", "description": "Document the incident"},
                    {"bot": "customer_service", "action": "notify_customer", "description": "Notify customer"},
                    {"bot": "general_manager", "action": "receive_escalation", "description": "Escalate summary"},
                ],
            },
        }

    async def run(self, payload: dict) -> dict:
        """Main execution entrypoint."""
        context = payload.get("context", {}) or {}
        action = payload.get("action") or context.get("action") or payload.get("meta", {}).get("action") or "status"

        if action == "status":
            return await self.status()
        if action == "config":
            return await self.config()
        if action == "dashboard":
            return await self.get_dashboard()
        if action == "receive_report":
            return await self.receive_report(context.get("report") or payload.get("report") or context)
        if action == "daily_summary":
            return await self.get_daily_summary()
        if action == "weekly_summary":
            return await self.get_weekly_summary()
        if action == "workflows":
            return await self.get_workflows()
        if action == "execute_workflow":
            workflow_name = str(context.get("workflow_name") or payload.get("workflow_name") or "new_shipment")
            data = context.get("data") or payload.get("data") or {}
            return await self.execute_workflow(workflow_name, data)
        if action == "workflow_status":
            task_id = str(context.get("task_id") or payload.get("task_id") or "WF002")
            return await self.get_workflow_status(task_id)
        if action == "active_alerts":
            return await self.get_active_alerts()
        if action == "create_composite_alert":
            alert_ids = context.get("alert_ids") or payload.get("alert_ids") or []
            return await self.create_composite_alert(alert_ids)
        if action == "command_queue":
            return await self.get_command_queue()
        return {"ok": False, "error": f"Unknown action: {action}"}

    async def process_message(self, message: str, context: Optional[dict] = None) -> dict:
        """Support natural-language and explicit context actions."""
        context = context or {}
        if context.get("action"):
            return await self.run({"context": context})

        message_lower = (message or "").lower()
        if "dashboard" in message_lower or "overview" in message_lower:
            return await self.get_dashboard()
        if "report" in message_lower or "summary" in message_lower:
            return await self.get_daily_summary()
        if "workflow" in message_lower:
            return await self.get_workflows()
        if "alert" in message_lower:
            return await self.get_active_alerts()
        if "command" in message_lower:
            return await self.get_command_queue()
        return await self.status()

    async def status(self) -> dict:
        """Return bot status."""
        quick_stats = self._quick_stats()
        return {
            "ok": True,
            "bot": self.name,
            "display_name": self.display_name,
            "version": self.version,
            "mode": self.mode,
            "is_active": self.is_active,
            "quick_stats": quick_stats,
            "message": "Operations orchestration is active",
        }

    async def config(self) -> dict:
        """Return capabilities."""
        return {
            "name": self.name,
            "display_name": self.display_name,
            "description": self.description,
            "version": self.version,
            "mode": self.mode,
            "capabilities": [
                "dashboard",
                "receive_report",
                "daily_summary",
                "weekly_summary",
                "workflows",
                "execute_workflow",
                "workflow_status",
                "active_alerts",
                "create_composite_alert",
                "command_queue",
            ],
        }

    async def receive_report(self, report: Dict[str, Any]) -> dict:
        """Receive and process a bot report."""
        normalized = self._normalize_report(report)
        self.reports.insert(0, normalized)

        dispatched_commands = self._determine_actions(normalized)
        for command in dispatched_commands:
            self.commands.insert(0, command)

        escalated = normalized["severity"] == "critical"
        if escalated:
            self.orchestration_log.insert(
                0,
                {
                    "log_type": "gm_escalated",
                    "reference_id": normalized["report_id"],
                    "description": f"Critical report from {normalized['source_bot']} escalated to General Manager.",
                    "created_at": datetime.now(timezone.utc).isoformat(),
                },
            )

        self.orchestration_log.insert(
            0,
            {
                "log_type": "report_received",
                "reference_id": normalized["report_id"],
                "description": f"Report received from {normalized['source_bot']}.",
                "created_at": datetime.now(timezone.utc).isoformat(),
            },
        )

        return {
            "ok": True,
            "received": True,
            "report_id": normalized["report_id"],
            "actions_dispatched": len(dispatched_commands),
            "escalated": escalated,
            "commands": dispatched_commands,
        }

    async def get_daily_summary(self) -> dict:
        """Aggregate current daily report signals."""
        by_bot: Dict[str, int] = {}
        by_severity = {"low": 0, "medium": 0, "high": 0, "critical": 0}
        by_type: Dict[str, int] = {}
        critical_reports: List[Dict[str, Any]] = []

        for report in self.reports:
            by_bot[report["source_bot"]] = by_bot.get(report["source_bot"], 0) + 1
            by_severity[report["severity"]] = by_severity.get(report["severity"], 0) + 1
            by_type[report["report_type"]] = by_type.get(report["report_type"], 0) + 1
            if report["severity"] == "critical":
                critical_reports.append(
                    {
                        "id": report["report_id"],
                        "bot": report["source_bot"],
                        "summary": report["summary"],
                    }
                )

        repeated_types = [
            f"{report_type} repeated {count} times"
            for report_type, count in by_type.items()
            if count > 1
        ]

        return {
            "ok": True,
            "date": datetime.now(timezone.utc).date().isoformat(),
            "total_reports": len(self.reports),
            "by_bot": by_bot,
            "by_severity": by_severity,
            "by_type": by_type,
            "critical_reports": critical_reports,
            "patterns": repeated_types,
        }

    async def get_weekly_summary(self) -> dict:
        """Return a lightweight weekly rollup."""
        daily_counts = [
            {"date": (datetime.now(timezone.utc) - timedelta(days=index)).date().isoformat(), "total_reports": max(2, len(self.reports) - index), "critical": 1 if index < 2 else 0}
            for index in range(7)
        ]
        return {
            "ok": True,
            "period": "weekly",
            "daily_stats": list(reversed(daily_counts)),
            "total": sum(item["total_reports"] for item in daily_counts),
            "top_bots": self._top_bots(),
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    async def execute_workflow(self, workflow_name: str, data: Dict[str, Any]) -> dict:
        """Execute a workflow template in memory."""
        template = self.workflow_templates.get(workflow_name)
        if not template:
            return {"ok": False, "error": f"Workflow '{workflow_name}' not found"}

        task_id = f"WF{len(self.cross_bot_tasks) + 100:03d}"
        results = []
        for index, step in enumerate(template["steps"], start=1):
            results.append(
                {
                    "step": index,
                    "bot": step["bot"],
                    "action": step["action"],
                    "description": step["description"],
                    "status": "success",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            )

        record = {
            "task_id": task_id,
            "workflow_name": workflow_name,
            "status": "completed",
            "progress": 100,
            "current_step": "completed",
            "steps": len(template["steps"]),
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "results": results,
            "data": data,
        }
        self.cross_bot_tasks.insert(0, record)
        self.orchestration_log.insert(
            0,
            {
                "log_type": "command_issued",
                "reference_id": task_id,
                "description": f"Workflow {workflow_name} executed across {len(template['steps'])} steps.",
                "created_at": datetime.now(timezone.utc).isoformat(),
            },
        )
        return {"ok": True, **record}

    async def get_workflows(self) -> dict:
        """Return workflow templates."""
        workflows = []
        for workflow_id, template in self.workflow_templates.items():
            workflows.append(
                {
                    "id": workflow_id,
                    "name": template["name"],
                    "steps_count": len(template["steps"]),
                    "steps": [step["description"] for step in template["steps"]],
                }
            )
        return {"ok": True, "workflows": workflows}

    async def get_workflow_status(self, task_id: str) -> dict:
        """Return workflow task status."""
        task = next((item for item in self.cross_bot_tasks if item["task_id"] == task_id), None)
        if not task:
            return {"ok": False, "error": f"Workflow task '{task_id}' not found"}
        return {"ok": True, "workflow": copy.deepcopy(task)}

    async def create_composite_alert(self, alert_ids: List[str]) -> dict:
        """Create or reuse a composite alert based on reports."""
        related = [report for report in self.reports if report["report_id"] in alert_ids]
        if len(related) < 2:
            return {"ok": False, "error": "At least two reports are required to build a composite alert"}

        severity = "critical" if any(item["severity"] == "critical" for item in related) else "high"
        composite = {
            "alert_id": f"ALT-C{len(self.composite_alerts) + 2:03d}",
            "severity": severity,
            "description": f"Composite alert created from {len(related)} related reports.",
            "source_bots": sorted({item["source_bot"] for item in related}),
            "related_alerts": [item["report_id"] for item in related],
            "correlation_score": min(100, 50 + len(related) * 12),
            "recommended_actions": [
                "Review cross-bot dependencies immediately.",
                "Assign a single owner for coordinated resolution.",
            ],
            "assigned_bots": sorted({cmd["target_bot"] for cmd in self._determine_actions(related[0])} | {related[0]["source_bot"]}),
            "status": "active",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        self.composite_alerts.insert(0, composite)
        return {"ok": True, "composite_alert": composite}

    async def get_active_alerts(self) -> dict:
        """Return active composite alerts."""
        active = [alert for alert in self.composite_alerts if alert["status"] == "active"]
        return {"ok": True, "alerts": copy.deepcopy(active)}

    async def get_command_queue(self) -> dict:
        """Return queued and recent commands."""
        return {
            "ok": True,
            "pending_commands": [copy.deepcopy(cmd) for cmd in self.commands if cmd["status"] in {"queued", "in_progress"}],
            "recent_commands": copy.deepcopy(self.commands[:5]),
        }

    async def get_dashboard(self) -> dict:
        """Return the main operations dashboard payload."""
        return {
            "ok": True,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "quick_stats": self._quick_stats(),
            "reports": {
                "recent": copy.deepcopy(self.reports[:5]),
                "daily_summary": (await self.get_daily_summary()),
            },
            "workflows": {
                "templates": len(self.workflow_templates),
                "in_progress": len([task for task in self.cross_bot_tasks if task["status"] == "in_progress"]),
                "recent": copy.deepcopy(self.cross_bot_tasks[:5]),
            },
            "alerts": copy.deepcopy(self.composite_alerts[:5]),
            "command_queue": {
                "pending": len([cmd for cmd in self.commands if cmd["status"] in {"queued", "in_progress"}]),
                "recent": copy.deepcopy(self.commands[:5]),
            },
            "recent_activity": copy.deepcopy(self.orchestration_log[:8]),
        }

    def _quick_stats(self) -> Dict[str, Any]:
        return {
            "reports_today": len(self.reports),
            "critical_today": len([report for report in self.reports if report["severity"] == "critical"]),
            "pending_commands": len([cmd for cmd in self.commands if cmd["status"] in {"queued", "in_progress"}]),
            "active_alerts": len([alert for alert in self.composite_alerts if alert["status"] == "active"]),
            "active_workflows": len([task for task in self.cross_bot_tasks if task["status"] == "in_progress"]),
        }

    def _normalize_report(self, report: Dict[str, Any]) -> Dict[str, Any]:
        severity_map = {
            "low": "low",
            "medium": "medium",
            "high": "high",
            "critical": "critical",
        }
        severity = severity_map.get(str(report.get("severity", "medium")).lower(), "medium")
        return {
            "report_id": report.get("report_id") or f"RPT{len(self.reports) + 100:03d}",
            "source_bot": report.get("source_bot") or report.get("bot_name") or "unknown",
            "report_type": report.get("report_type") or report.get("type") or "general",
            "severity": severity,
            "summary": report.get("summary", ""),
            "data": report.get("data", {}),
            "received_at": report.get("received_at") or datetime.now(timezone.utc).isoformat(),
            "requires_action": bool(report.get("requires_action", severity in {"high", "critical"})),
        }

    def _determine_actions(self, report: Dict[str, Any]) -> List[Dict[str, Any]]:
        report_type = str(report.get("report_type", "")).lower()
        priority = "immediate" if report["severity"] == "critical" else "high"
        commands: List[Dict[str, Any]] = []

        if "delay" in report_type:
            commands.extend(
                [
                    self._make_command("customer_service", "notify_customer", priority),
                    self._make_command("dispatcher", "reschedule_shipment", priority),
                ]
            )
        elif "incident" in report_type:
            commands.extend(
                [
                    self._make_command("safety_bot", "emergency_response", "immediate"),
                    self._make_command("dispatcher", "stop_vehicle", "high"),
                    self._make_command("general_manager", "receive_escalation", "high"),
                ]
            )
        elif "invoice" in report_type or "financial" in report_type:
            commands.extend(
                [
                    self._make_command("finance_bot", "collect_payment", priority),
                    self._make_command("customer_service", "follow_up_customer", "medium"),
                ]
            )

        return commands

    def _make_command(self, target_bot: str, command_type: str, priority: str) -> Dict[str, Any]:
        return {
            "command_id": f"CMD{len(self.commands) + 100:03d}",
            "target_bot": target_bot,
            "command_type": command_type,
            "priority": priority,
            "status": "queued",
            "issued_at": datetime.now(timezone.utc).isoformat(),
        }

    def _top_bots(self) -> List[Dict[str, Any]]:
        counts: Dict[str, int] = {}
        for report in self.reports:
            counts[report["source_bot"]] = counts.get(report["source_bot"], 0) + 1
        sorted_counts = sorted(counts.items(), key=lambda item: item[1], reverse=True)
        return [{"bot": bot, "count": count} for bot, count in sorted_counts[:5]]
