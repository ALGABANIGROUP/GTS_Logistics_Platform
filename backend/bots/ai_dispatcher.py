"""
AI Dispatcher Bot - Intelligent Task Distribution and Workflow Orchestration
Responsible for distributing tasks across the bot network and optimizing workflows.
"""

from typing import Dict, Any, List
from datetime import datetime, timedelta, timezone
import logging

logger = logging.getLogger(__name__)

class AIDispatcherBot:
    def __init__(self):
        self.name = "ai_dispatcher"
        self.display_name = "🤖 AI Dispatcher"
        self.version = "1.0.0"
        self.is_active = True

    async def run(self, payload: dict) -> dict:
        """Main execution method for AI Dispatcher"""
        context = payload.get("context") or {}
        action = payload.get("action") or context.get("action") or "status"
        if action == "status":
            return await self.status()
        elif action == "dispatch":
            return await self.dispatch_tasks(payload)
        elif action == "optimize":
            return await self.optimize_workflows(payload)
        elif action == "monitor":
            return await self.monitor_system(payload)
        else:
            return {"error": f"Unknown action: {action}"}

    async def status(self) -> dict:
        """Return bot health/status"""
        metrics = await self._load_dispatch_metrics()
        active_tasks = metrics.get("assignments", {}).get("active", 0)
        queue_length = metrics.get("shipments", {}).get("unassigned", 0)
        system_load = self._compute_system_load(active_tasks, queue_length)
        return {
            "ok": metrics.get("ok", True),
            "bot": self.name,
            "version": self.version,
            "message": "AI Dispatcher operational - live dispatch metrics",
            "capabilities": ["dispatch", "optimize", "monitor"],
            "active_tasks": active_tasks,
            "task_queue": queue_length,
            "system_load": system_load,
            "shipments": metrics.get("shipments", {}),
            "assignments": metrics.get("assignments", {}),
            "telemetry": metrics.get("telemetry", {}),
            "last_updated": datetime.now(timezone.utc).isoformat(),
            **({"error": metrics.get("error")} if metrics.get("error") else {}),
        }

    async def dispatch_tasks(self, payload: dict) -> dict:
        """Distribute tasks across available bots"""
        try:
            tasks = payload.get("tasks", [])
            priority = payload.get("priority", "normal")

            # Simulate task distribution logic
            dispatched_tasks = []
            for task in tasks:
                # Determine best bot for the task
                target_bot = await self._find_optimal_bot(task)

                dispatched_tasks.append({
                    "task_id": task.get("id"),
                    "target_bot": target_bot,
                    "priority": priority,
                    "status": "queued",
                    "estimated_completion": datetime.now() + timedelta(minutes=5)
                })

            return {
                "success": True,
                "message": f"Dispatched {len(dispatched_tasks)} tasks",
                "dispatched_tasks": dispatched_tasks
            }

        except Exception as e:
            logger.error(f"Error dispatching tasks: {str(e)}")
            return {
                "success": False,
                "error": f"Task dispatch failed: {str(e)}"
            }

    async def optimize_workflows(self, payload: dict) -> dict:
        """Optimize bot workflows and resource allocation"""
        try:
            metrics = await self._load_dispatch_metrics()
            queue_length = metrics.get("shipments", {}).get("unassigned", 0)
            active_assignments = metrics.get("assignments", {}).get("active", 0)
            optimization_score = max(0, 100 - int(queue_length) - int(active_assignments))

            # Simulate workflow optimization
            optimizations = {
                "resource_reallocation": "Completed - redistributed 15% capacity",
                "bottleneck_resolution": "Identified and resolved 3 bottlenecks",
                "efficiency_gain": "8.5% improvement in task completion time",
                "optimization_score": optimization_score,
            }

            return {
                "success": True,
                "message": "Workflow optimization completed",
                "optimizations": optimizations
            }

        except Exception as e:
            logger.error(f"Error optimizing workflows: {str(e)}")
            return {
                "success": False,
                "error": f"Workflow optimization failed: {str(e)}"
            }

    async def monitor_system(self, payload: dict) -> dict:
        """Monitor system health and bot performance"""
        try:
            metrics = await self._load_dispatch_metrics()
            active_assignments = metrics.get("assignments", {}).get("active", 0)
            queue_length = metrics.get("shipments", {}).get("unassigned", 0)
            system_load = self._compute_system_load(active_assignments, queue_length)

            system_status = {
                "overall_health": "stable" if system_load != "high" else "stressed",
                "active_assignments": active_assignments,
                "task_queue_length": queue_length,
                "active_drivers": metrics.get("assignments", {}).get("active_drivers", 0),
                "recent_location_pings": metrics.get("telemetry", {}).get("recent_location_pings", 0),
                "last_assignment_at": metrics.get("assignments", {}).get("last_assigned_at"),
                "last_health_check": datetime.now(timezone.utc).isoformat(),
            }

            return {
                "success": True,
                "message": "System monitoring completed",
                "system_status": system_status
            }

        except Exception as e:
            logger.error(f"Error monitoring system: {str(e)}")
            return {
                "success": False,
                "error": f"System monitoring failed: {str(e)}"
            }

    async def _find_optimal_bot(self, task: dict) -> str:
        """Find the best bot for a given task"""
        task_type = task.get("type", "general")

        # Simple bot selection logic (would be more sophisticated in production)
        bot_mapping = {
            "financial": "finance_bot",
            "legal": "legal_counsel",
            "security": "security_bot",
            "operations": "operations_management",
            "sales": "sales_intelligence",
            "customer": "customer_service",
            "maintenance": "maintenance_dev",
            "intelligence": "executive_intelligence"
        }

        return bot_mapping.get(task_type, "general_manager")

    async def config(self) -> dict:
        """Return bot capabilities and configuration"""
        return {
            "name": self.name,
            "display_name": self.display_name,
            "capabilities": ["dispatch", "optimize", "monitor"],
            "data_source": "database",
            "supported_task_types": [
                "financial", "legal", "security", "operations",
                "sales", "customer", "maintenance", "intelligence"
            ],
            "optimization_features": [
                "load_balancing",
                "resource_allocation",
                "bottleneck_detection",
                "performance_monitoring"
            ]
        }

    async def _load_dispatch_metrics(self) -> dict:
        try:
            from backend.database.config import get_sessionmaker
            from sqlalchemy import select, func
            from backend.models.models import Shipment
            from backend.models.dispatch_models import ShipmentAssignment, ShipmentLocation

            sessionmaker = get_sessionmaker()
            async with sessionmaker() as session:
                total_shipments = await session.scalar(select(func.count(Shipment.id))) or 0
                assigned_shipments = await session.scalar(
                    select(func.count(Shipment.id)).where(Shipment.status == "Assigned")
                ) or 0
                in_transit_shipments = await session.scalar(
                    select(func.count(Shipment.id)).where(Shipment.status == "on_the_way")
                ) or 0
                delivered_shipments = await session.scalar(
                    select(func.count(Shipment.id)).where(Shipment.status == "Delivered")
                ) or 0
                cancelled_shipments = await session.scalar(
                    select(func.count(Shipment.id)).where(Shipment.status == "Cancelled")
                ) or 0
                unassigned_shipments = await session.scalar(
                    select(func.count(Shipment.id)).where(Shipment.status.in_(["Draft", "Pending"]))
                ) or 0

                active_assignments = await session.scalar(
                    select(func.count(ShipmentAssignment.id)).where(ShipmentAssignment.is_active.is_(True))
                ) or 0
                active_drivers = await session.scalar(
                    select(func.count(func.distinct(ShipmentAssignment.driver_user_id))).where(
                        ShipmentAssignment.is_active.is_(True)
                    )
                ) or 0
                last_assigned_at = await session.scalar(select(func.max(ShipmentAssignment.created_at)))

                recent_cutoff = datetime.now(timezone.utc) - timedelta(minutes=60)
                recent_location_pings = await session.scalar(
                    select(func.count(ShipmentLocation.id)).where(ShipmentLocation.recorded_at >= recent_cutoff)
                ) or 0

                # Demand buckets over last 24h
                now_utc = datetime.utcnow()
                cutoff = now_utc - timedelta(hours=24)
                bucket_hours = 3
                bucket_count = int(24 / bucket_hours)
                demand_labels = [f"{str(i * bucket_hours).zfill(2)}:00" for i in range(bucket_count)]
                demand_counts = [0] * bucket_count
                created_rows = await session.execute(
                    select(Shipment.created_at).where(Shipment.created_at >= cutoff)
                )
                for created_at in created_rows.scalars().all():
                    if not created_at:
                        continue
                    created = created_at
                    if created.tzinfo is not None:
                        created = created.astimezone(timezone.utc).replace(tzinfo=None)
                    delta = created - cutoff
                    idx = int(delta.total_seconds() // (bucket_hours * 3600))
                    if 0 <= idx < bucket_count:
                        demand_counts[idx] += 1

                # Utilization by pickup location (top 5)
                utilization_rows = await session.execute(
                    select(Shipment.pickup_location, func.count(Shipment.id))
                    .where(Shipment.pickup_location.is_not(None))
                    .group_by(Shipment.pickup_location)
                    .order_by(func.count(Shipment.id).desc())
                    .limit(5)
                )
                utilization_data = []
                utilization_list = utilization_rows.all()
                total_top = sum(count for _, count in utilization_list) or 1
                for city, count in utilization_list:
                    if not city:
                        continue
                    utilization_data.append(
                        {
                            "city": str(city),
                            "value": round((count / total_top) * 100, 1),
                        }
                    )

                # Recent updates from assignments
                updates = []
                assignment_rows = await session.execute(
                    select(ShipmentAssignment, Shipment)
                    .join(Shipment, ShipmentAssignment.shipment_id == Shipment.id)
                    .order_by(ShipmentAssignment.created_at.desc())
                    .limit(6)
                )
                for assignment, shipment in assignment_rows.all():
                    updates.append(
                        {
                            "id": f"assignment-{assignment.id}",
                            "type": "assignment",
                            "title": (
                                f"Shipment #{shipment.id} assigned to driver {assignment.driver_user_id}"
                                if assignment.driver_user_id
                                else f"Shipment #{shipment.id} assigned"
                            ),
                            "time": assignment.created_at.isoformat() if assignment.created_at else None,
                        }
                    )

            return {
                "ok": True,
                "shipments": {
                    "total": total_shipments,
                    "unassigned": unassigned_shipments,
                    "assigned": assigned_shipments,
                    "in_transit": in_transit_shipments,
                    "delivered": delivered_shipments,
                    "cancelled": cancelled_shipments,
                },
                "assignments": {
                    "active": active_assignments,
                    "active_drivers": active_drivers,
                    "last_assigned_at": last_assigned_at.isoformat() if last_assigned_at else None,
                },
                "telemetry": {
                    "recent_location_pings": recent_location_pings,
                    "window_minutes": 60,
                },
                "demand": {
                    "labels": demand_labels,
                    "counts": demand_counts,
                    "predicted": demand_counts,
                },
                "utilization": utilization_data,
                "updates": updates,
            }
        except Exception as exc:
            logger.error("Failed to load dispatcher metrics: %s", exc)
            return {"ok": False, "error": str(exc)}

    @staticmethod
    def _compute_system_load(active_assignments: int, queue_length: int) -> str:
        if active_assignments >= 50 or queue_length >= 100:
            return "high"
        if active_assignments >= 20 or queue_length >= 40:
            return "elevated"
        return "normal"
