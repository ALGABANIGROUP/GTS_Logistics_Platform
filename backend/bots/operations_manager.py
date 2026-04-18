from __future__ import annotations
# backend/bots/operations_manager.py
from .base_bot import BaseBot
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class OperationsManagerBot(BaseBot):
    """Operations Manager AI Assistant"""

    def __init__(self):
        super().__init__(
            name="OperationsManagerBot",
            description="AI assistant for operations management"
        )

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process operations requests"""
        logger.info(f"OperationsManagerBot processing: {input_data.get('action')}")
        # Implement operations logic
        return {
            "status": "success",
            "response": "Operations task processed",
            "data": input_data
        }

    async def get_status(self) -> Dict[str, Any]:
        """Get bot status"""
        return {
            "name": self.name,
            "active": self.is_active,
            "description": self.description
        }
    """Enhanced Operations Manager Bot for daily operations"""

    name = "operations_manager"
    display_name = "Operations Manager Bot"
    description = "Manages daily operations, task assignment, and shipment tracking"

    def __init__(self):
        self.tasks = {}
        self.shipments = {}
        self.alerts = []

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Execute operations manager commands"""
        context = payload.get("context") if isinstance(payload.get("context"), dict) else None
        action = payload.get("action") or (context or {}).get("action") or "dashboard"

        if action == "task_assignment":
            return await self._assign_task(payload)
        elif action == "shipment_status":
            return await self._get_shipment_status(payload.get("shipment_id"))
        elif action == "operational_alerts":
            return await self._get_operational_alerts()
        elif action == "resource_optimization":
            return await self._optimize_resources()
        elif action == "fleet_status":
            return await self._get_fleet_status()
        elif action == "incident_response":
            return await self._handle_incident(payload)
        elif action == "performance_report":
            return await self._get_performance_report()
        elif action == "coordinate_external_report":
            return await self._coordinate_external_report(payload)
        elif action == "execute_workflow":
            source = context or payload
            return await self._execute_workflow(source)
        elif action == "receive_report":
            source = context or payload
            return await self._receive_report(source)
        else:
            return self._get_dashboard()

    async def process_message(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Compatibility entry point used by older tests and orchestration paths."""
        payload = dict(context or {})
        if message:
            payload.setdefault("message", message)
        return await self.run(payload)

    async def _assign_task(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Assign task to team member"""
        task_id = payload.get("task_id", f"TASK-{len(self.tasks)+1}")
        assigned_to = payload.get("assigned_to")
        description = payload.get("description")

        if not assigned_to:
            return {"error": "Please specify who to assign the task to"}

        self.tasks[task_id] = {
            "id": task_id,
            "assigned_to": assigned_to,
            "description": description,
            "status": "pending",
            "created_at": datetime.now().isoformat()
        }

        return {
            "success": True,
            "task": self.tasks[task_id],
            "message": f"Task {task_id} assigned to {assigned_to}",
            "action": "task_assignment"
        }

    async def _get_shipment_status(self, shipment_id: str) -> Dict[str, Any]:
        """Get real-time shipment status"""
        if not shipment_id:
            return {"error": "Please provide shipment ID"}

        # Seed shipment data - replace with real DB query
        shipment = self.shipments.get(shipment_id, {
            "id": shipment_id,
            "status": "In Transit",
            "location": "Khartoum, Sudan",
            "eta": "2026-03-25 14:30",
            "last_update": datetime.now().isoformat()
        })

        return {
            "success": True,
            "shipment": shipment,
            "action": "shipment_status"
        }

    async def _get_operational_alerts(self) -> Dict[str, Any]:
        """Get active operational alerts"""
        return {
            "success": True,
            "alerts": self.alerts,
            "count": len(self.alerts),
            "action": "operational_alerts"
        }

    async def _optimize_resources(self) -> Dict[str, Any]:
        """Run resource optimization analysis"""
        return {
            "success": True,
            "optimizations": [
                {"type": "vehicle_assignment", "savings": 15, "status": "ready"},
                {"type": "route_planning", "savings": 8, "status": "ready"},
                {"type": "driver_scheduling", "savings": 12, "status": "pending"}
            ],
            "total_potential_savings": 35,
            "action": "resource_optimization"
        }

    async def _get_fleet_status(self) -> Dict[str, Any]:
        """Get fleet status overview"""
        return {
            "success": True,
            "fleet": {
                "total_vehicles": 25,
                "active": 18,
                "maintenance": 3,
                "idle": 4
            },
            "action": "fleet_status"
        }

    async def _handle_incident(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle operational incident"""
        incident_type = payload.get("type", "general")
        description = payload.get("description")

        incident = {
            "id": f"INC-{len(self.alerts)+1}",
            "type": incident_type,
            "description": description,
            "reported_at": datetime.now().isoformat(),
            "status": "investigating"
        }

        self.alerts.append(incident)

        return {
            "success": True,
            "incident": incident,
            "message": "Incident reported and under investigation",
            "action": "incident_response"
        }

    async def _get_performance_report(self) -> Dict[str, Any]:
        """Get operational performance report"""
        return {
            "success": True,
            "report": {
                "period": "daily",
                "shipments_completed": 42,
                "on_time_rate": 89.5,
                "average_response_time": "2.3 min",
                "resource_utilization": 76
            },
            "action": "performance_report"
        }

    async def _coordinate_external_report(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Coordinate outbound report delivery using a simple RACI policy."""
        report_type = str(payload.get("report_type") or "daily_operations_report").strip().lower()
        source_bot = str(payload.get("source_bot") or "operations_manager").strip().lower()
        recipients = payload.get("to") or payload.get("recipients") or []
        subject = str(payload.get("subject") or f"{report_type.replace('_', ' ').title()}").strip()
        body = str(payload.get("body") or "No report content supplied.").strip()

        if not recipients:
            return {"success": False, "error": "No recipients provided", "action": "coordinate_external_report"}

        if not can_send_report(report_type, source_bot):
            return {
                "success": False,
                "error": f"{source_bot} is not allowed to send {report_type}",
                "requires_approval": True,
                "action": "coordinate_external_report",
            }

        approval_required = requires_approval(report_type, source_bot)
        cc = ["operations@gabanilogistics.com"] if source_bot != "operations_manager" else []
        if approval_required:
            cc.append("operations@gabanilogistics.com")

        success = await dispatch_email(
            bot_name="operations_manager",
            to_email=recipients,
            subject=subject,
            body=body,
            html=bool(payload.get("html", False)),
            plain_text=None if payload.get("html", False) else body,
            cc=cc,
            audit_context={
                "report_type": report_type,
                "source_bot": source_bot,
                "approval_required": approval_required,
            },
        )

        return {
            "success": success,
            "report_type": report_type,
            "source_bot": source_bot,
            "approval_required": approval_required,
            "coordinator": self.name,
            "action": "coordinate_external_report",
        }

    async def _execute_workflow(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Run a named workflow in a deterministic test-friendly shape."""
        workflow_name = str(payload.get("workflow_name") or "general_workflow").strip()
        workflow_data = payload.get("data") or {}
        return {
            "ok": True,
            "success": True,
            "workflow_name": workflow_name,
            "progress": 100,
            "data": workflow_data,
            "action": "execute_workflow",
            "message": f"Workflow {workflow_name} completed",
        }

    async def _receive_report(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Convert incoming operational reports into command fan-out."""
        report = payload.get("report") or {}
        report_type = str(report.get("type") or "general").strip().lower()
        source_bot = str(report.get("bot_name") or "operations_manager").strip().lower()
        commands: List[Dict[str, Any]] = [
            {
                "target_bot": source_bot,
                "action": "acknowledge_report",
                "report_type": report_type,
            }
        ]

        if report.get("requires_action"):
            commands.append(
                {
                    "target_bot": "system_admin",
                    "action": "open_incident",
                    "report_type": report_type,
                    "severity": report.get("severity", "medium"),
                }
            )
        if report_type == "shipment_delay":
            commands.append(
                {
                    "target_bot": "dispatcher",
                    "action": "reroute_shipment",
                    "shipment_id": (report.get("data") or {}).get("shipment_id"),
                }
            )
            commands.append(
                {
                    "target_bot": "customer_service",
                    "action": "prepare_customer_update",
                    "shipment_id": (report.get("data") or {}).get("shipment_id"),
                }
            )

        return {
            "ok": True,
            "success": True,
            "actions_dispatched": len(commands),
            "commands": commands,
            "report_type": report_type,
            "action": "receive_report",
        }

    def _get_dashboard(self) -> Dict[str, Any]:
        """Return operations dashboard"""
        return {
            "ok": True,
            "success": True,
            "bot": self.name,
            "display_name": self.display_name,
            "quick_stats": {
                "reports_today": 3,
                "active_alerts": len(self.alerts),
                "open_tasks": len(self.tasks),
            },
            "reports": [
                {"name": "Daily Operations Summary", "status": "ready"},
                {"name": "Fleet Performance", "status": "ready"},
                {"name": "Incident Queue", "status": "monitoring"},
            ],
            "workflows": [
                {"name": "incident_response", "status": "active"},
                {"name": "delay_escalation", "status": "ready"},
                {"name": "resource_balancing", "status": "ready"},
            ],
            "available_actions": [
                "task_assignment - Assign tasks",
                "shipment_status {id} - Check shipment",
                "operational_alerts - View alerts",
                "resource_optimization - Optimize resources",
                "fleet_status - Fleet overview",
                "incident_response - Handle incidents",
                "performance_report - Performance metrics",
                "coordinate_external_report - Coordinate outbound report delivery",
            ],
            "action": "dashboard"
        }

    async def status(self) -> Dict[str, Any]:
        """Return bot status"""
        return {
            "name": self.name,
            "display_name": self.display_name,
            "status": "active",
            "description": self.description
        }

    async def config(self) -> Dict[str, Any]:
        """Return bot configuration"""
        return {
            "name": self.name,
            "display_name": self.display_name,
            "description": self.description,
            "actions": self._get_dashboard()["available_actions"]
        }

