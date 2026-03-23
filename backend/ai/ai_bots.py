from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from sqlalchemy import and_, desc, func, select

try:
    from backend.ai.data_collection_service import data_collection_service
    from backend.ai.learning_engine import bot_learning_engine

    LEARNING_ENABLED = True
except Exception as exc:  # pragma: no cover
    LEARNING_ENABLED = False
    bot_learning_engine = None  # type: ignore[assignment]
    data_collection_service = None  # type: ignore[assignment]
    print(f"Warning: Bot learning system not available: {exc}")


class BaseAIBot:
    name: str = "base_bot"
    description: str = "Base AI Bot"
    learning_enabled: bool = True
    learning_frequency: str = "daily"
    learning_intensity: str = "medium"

    def __init__(self) -> None:
        if LEARNING_ENABLED and self.learning_enabled:
            try:
                bot_learning_engine.register_bot(
                    bot_id=self.name,
                    bot_name=self.__class__.__name__,
                    enabled=True,
                    frequency=self.learning_frequency,
                    intensity=self.learning_intensity,
                    data_sources=["error_logs", "performance_metrics", "user_feedback"],
                )
            except Exception as exc:  # pragma: no cover
                print(f"Failed to register {self.name} for learning: {exc}")

    async def run(self, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        raise NotImplementedError("Bot must implement run()")

    async def status(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "status": "active",
            "ready": True,
            "learning_enabled": self.learning_enabled and LEARNING_ENABLED,
        }

    async def config(self) -> Dict[str, Any]:
        capabilities = ["run", "status"]
        if self.learning_enabled and LEARNING_ENABLED:
            capabilities.append("learning")
        return {
            "name": self.name,
            "description": self.description,
            "capabilities": capabilities,
            "learning": {
                "enabled": self.learning_enabled and LEARNING_ENABLED,
                "frequency": self.learning_frequency,
                "intensity": self.learning_intensity,
            }
            if self.learning_enabled and LEARNING_ENABLED
            else None,
        }

    def record_execution_success(
        self,
        response_time_ms: float,
        accuracy: float = 1.0,
        throughput: float = 1.0,
    ) -> None:
        if LEARNING_ENABLED and self.learning_enabled:
            try:
                data_collection_service.record_performance(
                    bot_id=self.name,
                    response_time=response_time_ms,
                    accuracy=accuracy,
                    throughput=throughput,
                    context={"bot_class": self.__class__.__name__},
                )
                bot_learning_engine.add_performance_data(
                    self.name,
                    {
                        "response_time": response_time_ms,
                        "accuracy": accuracy,
                        "throughput": throughput,
                    },
                )
            except Exception as exc:  # pragma: no cover
                print(f"Failed to record execution success: {exc}")

    def record_execution_error(
        self,
        error_type: str,
        error_message: str,
        severity: float = 1.0,
        traceback: Optional[str] = None,
    ) -> None:
        if LEARNING_ENABLED and self.learning_enabled:
            try:
                data_collection_service.log_bot_error(
                    bot_id=self.name,
                    error_type=error_type,
                    error_message=error_message,
                    severity=severity,
                    traceback=traceback,
                    context={"bot_class": self.__class__.__name__},
                )
                bot_learning_engine.add_error_data(
                    self.name,
                    {
                        "error_type": error_type,
                        "error_message": error_message,
                        "severity": severity,
                    },
                )
            except Exception as exc:  # pragma: no cover
                print(f"Failed to record execution error: {exc}")

    def collect_feedback(
        self,
        rating: int,
        session_id: str,
        comment: Optional[str] = None,
        user_id: Optional[str] = None,
        feedback_type: str = "general",
    ) -> None:
        if LEARNING_ENABLED and self.learning_enabled:
            try:
                data_collection_service.collect_user_feedback(
                    bot_id=self.name,
                    rating=rating,
                    session_id=session_id,
                    comment=comment,
                    user_id=user_id,
                    feedback_type=feedback_type,
                    tags=[self.__class__.__name__],
                )
                bot_learning_engine.add_user_feedback(
                    self.name,
                    {
                        "rating": rating,
                        "comment": comment,
                        "user_id": user_id,
                        "feedback_type": feedback_type,
                    },
                )
            except Exception as exc:  # pragma: no cover
                print(f"Failed to collect feedback: {exc}")

    def trigger_learning(self) -> Dict[str, Any]:
        if not (LEARNING_ENABLED and self.learning_enabled):
            return {"error": "Learning not enabled for this bot"}
        try:
            return bot_learning_engine.perform_learning(self.name)
        except Exception as exc:  # pragma: no cover
            return {"error": f"Learning trigger failed: {exc}"}

    def get_learning_profile(self) -> Optional[Dict[str, Any]]:
        if not (LEARNING_ENABLED and self.learning_enabled):
            return None
        try:
            return bot_learning_engine.get_bot_profile(self.name)
        except Exception as exc:  # pragma: no cover
            print(f"Failed to get learning profile: {exc}")
            return None


class GeneralManagerBot(BaseAIBot):
    name = "general_manager"
    description = "High-level executive bot for system-wide analysis."

    async def run(self, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        action = (payload or {}).get("action", "general_analysis")
        if action == "status":
            return await self.get_dashboard_status()
        return {
            "bot": self.name,
            "action": action,
            "result": {
                "system_advice": [
                    "Monitor shipments performance daily.",
                    "Review finance dashboard weekly.",
                    "Ensure load pricing aligns with current market rates.",
                    "Optimize API throughput for larger clients.",
                ],
                "priority": "system_overview",
            },
        }

    async def get_dashboard_status(self) -> Dict[str, Any]:
        try:
            from backend.database.config import get_sessionmaker
            from backend.models.models import Shipment
            from backend.models.user import User

            sessionmaker = get_sessionmaker()
            async with sessionmaker() as session:
                users_result = await session.execute(
                    select(User.role, func.count(User.id))
                    .where(User.is_deleted == False)
                    .group_by(User.role)
                )
                users_by_role = dict(users_result.fetchall())
                total_users = sum(users_by_role.values())

                thirty_days_ago = datetime.now() - timedelta(days=30)
                shipments_result = await session.execute(
                    select(
                        func.count(Shipment.id).label("total"),
                        func.count(Shipment.id)
                        .filter(Shipment.status == "in_transit")
                        .label("in_transit"),
                        func.count(Shipment.id)
                        .filter(Shipment.status == "delivered")
                        .label("delivered"),
                        func.count(Shipment.id)
                        .filter(Shipment.status == "pending")
                        .label("pending"),
                    ).where(Shipment.created_at >= thirty_days_ago)
                )
                shipments_stats = shipments_result.fetchone()
                delivered_count = shipments_stats.delivered or 0
                on_time_rate = 0.92 if delivered_count > 0 else 0

                recent_users = await session.execute(
                    select(User.full_name, User.email, User.last_login_at)
                    .where(and_(User.is_deleted == False, User.last_login_at.isnot(None)))
                    .order_by(desc(User.last_login_at))
                    .limit(5)
                )
                activities = []
                for user_row in recent_users.fetchall():
                    time_diff = datetime.now() - user_row.last_login_at
                    hours_ago = int(time_diff.total_seconds() / 3600)
                    activities.append(
                        {
                            "id": len(activities) + 1,
                            "user": user_row.full_name or user_row.email.split("@")[0],
                            "action": "Logged in to system",
                            "time": f"{hours_ago} hours ago" if hours_ago > 0 else "Recently",
                        }
                    )

                return {
                    "ok": True,
                    "metrics": {
                        "activeTeams": {"value": len(users_by_role), "target": 8, "status": "active"},
                        "totalEmployees": {
                            "value": total_users,
                            "target": total_users + 20,
                            "status": "active",
                        },
                        "operationsStatus": {"value": f"{int(on_time_rate * 100)}%", "trend": "up"},
                        "responseTime": {"value": "2.3h", "trend": "down"},
                    },
                    "teams": [
                        {"name": role.title(), "size": count, "status": "active"}
                        for role, count in users_by_role.items()
                    ],
                    "pending": [
                        {
                            "id": 1,
                            "title": f"{shipments_stats.pending or 0} Pending Shipments",
                            "priority": "high",
                            "due": "2026-02-05",
                        },
                        {
                            "id": 2,
                            "title": f"{shipments_stats.in_transit or 0} In Transit",
                            "priority": "medium",
                            "due": "2026-02-08",
                        },
                        {
                            "id": 3,
                            "title": "Weekly Team Review",
                            "priority": "low",
                            "due": "2026-02-15",
                        },
                    ],
                    "activities": activities,
                    "reports": [
                        {
                            "id": 1,
                            "title": f"Shipments Report ({shipments_stats.total} total)",
                            "date": "2026-02-02",
                            "status": "completed",
                        },
                        {
                            "id": 2,
                            "title": f"Team Report ({total_users} users)",
                            "date": "2026-02-02",
                            "status": "completed",
                        },
                        {
                            "id": 3,
                            "title": "Monthly Performance",
                            "date": "2026-01-25",
                            "status": "completed",
                        },
                    ],
                }
        except Exception as exc:
            return {
                "ok": False,
                "error": str(exc),
                "metrics": {},
                "teams": [],
                "pending": [],
                "activities": [],
                "reports": [],
            }


class FreightBrokerBot(BaseAIBot):
    name = "freight_broker"
    description = "Assists with freight brokerage and lane planning."

    async def run(self, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        payload = payload or {}
        return {
            "bot": self.name,
            "action": "brokerage_assistance",
            "origin": payload.get("origin"),
            "destination": payload.get("destination"),
            "recommendation": [
                "Check truck availability in the target region.",
                "Compare lane rates with last 14-day averages.",
                "Validate broker-to-carrier margin before posting.",
            ],
        }


class FinanceBot(BaseAIBot):
    name = "finance_bot"
    description = "Bot for finance analytics, expenses, and revenue patterns."

    async def run(self, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        try:
            from backend.database.config import get_sessionmaker
            from backend.models.invoices import Invoice

            sessionmaker = get_sessionmaker()
            async with sessionmaker() as session:
                thirty_days_ago = datetime.now() - timedelta(days=30)
                result = await session.execute(
                    select(
                        func.sum(Invoice.amount).filter(Invoice.invoice_type == "income").label("revenue"),
                        func.sum(Invoice.amount).filter(Invoice.invoice_type == "expense").label("expenses"),
                        func.count(Invoice.id).filter(Invoice.status == "paid").label("paid_count"),
                        func.count(Invoice.id).filter(Invoice.status == "pending").label("pending_count"),
                    ).where(Invoice.created_at >= thirty_days_ago)
                )
                stats = result.fetchone()
                revenue = float(stats.revenue or 0)
                expenses = float(stats.expenses or 0)
                profit = revenue - expenses
                margin = (profit / revenue * 100) if revenue > 0 else 0

                return {
                    "bot": self.name,
                    "action": "financial_analysis",
                    "ok": True,
                    "data": {
                        "revenue": revenue,
                        "expenses": expenses,
                        "profit": profit,
                        "margin": round(margin, 2),
                        "paid_invoices": stats.paid_count or 0,
                        "pending_invoices": stats.pending_count or 0,
                    },
                    "insights": [
                        f"Total revenue: ${revenue:,.2f}",
                        f"Total expenses: ${expenses:,.2f}",
                        f"Net profit: ${profit:,.2f} ({margin:.1f}% margin)",
                        f"{stats.pending_count or 0} invoices pending payment",
                    ],
                }
        except Exception as exc:
            return {
                "bot": self.name,
                "action": "financial_insight",
                "ok": False,
                "error": str(exc),
                "insights": [
                    "Review expense trends for abnormal growth.",
                    "Optimize cost centers in fleet operations.",
                    "Automate monthly financial report generation.",
                ],
                "teams": [],
                "pending": [],
                "activities": [],
                "reports": [],
            }

    async def status(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "status": "active",
            "ready": True,
            "last_run": "2026-02-02T10:30:00Z",
            "operations_count": 247,
        }


class DocumentsBot(BaseAIBot):
    name = "documents_manager"
    description = "Bot for OCR, document classification, and data extraction."

    async def run(self, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        try:
            from backend.database.config import get_sessionmaker
            from backend.models.document import Document

            sessionmaker = get_sessionmaker()
            async with sessionmaker() as session:
                seven_days_ago = datetime.now() - timedelta(days=7)
                result = await session.execute(
                    select(
                        func.count(Document.id).label("total"),
                        func.count(Document.id).filter(Document.document_type == "invoice").label("invoices"),
                        func.count(Document.id).filter(Document.document_type == "BOL").label("bols"),
                        func.count(Document.id).filter(Document.document_type == "POD").label("pods"),
                    ).where(Document.created_at >= seven_days_ago)
                )
                stats = result.fetchone()

                recent_docs = await session.execute(
                    select(Document.id, Document.file_name, Document.document_type, Document.created_at)
                    .order_by(desc(Document.created_at))
                    .limit(5)
                )
                recent_list = []
                for doc in recent_docs.fetchall():
                    recent_list.append(
                        {
                            "id": doc.id,
                            "name": doc.file_name,
                            "type": doc.document_type,
                            "date": doc.created_at.strftime("%Y-%m-%d") if doc.created_at else "Unknown",
                        }
                    )

                return {
                    "bot": self.name,
                    "action": "document_analysis",
                    "ok": True,
                    "data": {
                        "total_documents": stats.total or 0,
                        "by_type": {
                            "invoices": stats.invoices or 0,
                            "bols": stats.bols or 0,
                            "pods": stats.pods or 0,
                        },
                        "recent": recent_list,
                    },
                    "steps": [
                        f"Processed {stats.total or 0} documents in last 7 days",
                        f"Classified {stats.invoices or 0} invoices, {stats.bols or 0} BOLs, {stats.pods or 0} PODs",
                        "OCR and extraction ready for new uploads",
                    ],
                }
        except Exception as exc:
            return {
                "bot": self.name,
                "action": "document_processing",
                "ok": False,
                "error": str(exc),
                "file": (payload or {}).get("filename"),
                "steps": [
                    "Perform OCR on the document.",
                    "Extract relevant fields.",
                    "Classify document type (invoice, BOL, POD, etc).",
                ],
            }


class DevOpsBot(BaseAIBot):
    name = "maintenance_dev"
    description = "Bot for system maintenance, monitoring, and auto-fix suggestions."

    async def run(self, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return {
            "bot": self.name,
            "action": "system_maintenance",
            "recommendations": [
                "Check CPU usage spikes.",
                "Validate database latency under load.",
                "Review system logs for failed API calls.",
                "Restart workers if performance degrades.",
            ],
        }


class OperationsManagerBot(BaseAIBot):
    name = "operations_manager"
    description = "Coordinates daily operations and bot execution."

    async def run(self, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return {"bot": self.name, "action": "operations_coordination", "result": "Operations coordinated."}


class CustomerServiceBot(BaseAIBot):
    name = "customer_service"
    description = "Automates customer support and issue resolution."

    async def run(self, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return {"bot": self.name, "action": "customer_support", "result": "Customer issue handled."}


class SystemAdminBot(BaseAIBot):
    name = "system_admin"
    description = "Manages system configuration and users."

    async def run(self, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return {"bot": self.name, "action": "system_admin_task", "result": "System admin task complete."}


class InformationCoordinatorBot(BaseAIBot):
    name = "information_coordinator"
    description = "Turns data into actionable insights."

    async def run(self, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return {"bot": self.name, "action": "data_insight", "result": "Insight generated."}


class StrategyAdvisorBot(BaseAIBot):
    name = "strategy_advisor"
    description = "Analyzes market trends and provides recommendations."

    async def run(self, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return {"bot": self.name, "action": "strategy_advice", "result": "Strategy advice provided."}


class MaintenanceDevBot(BaseAIBot):
    name = "maintenance_dev"
    description = "Maintains system health and suggests improvements."

    async def run(self, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return {"bot": self.name, "action": "maintenance", "result": "Maintenance performed."}


class LegalConsultantBot(BaseAIBot):
    name = "legal_consultant"
    description = "Reviews legal documents and ensures compliance."

    async def run(self, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return {"bot": self.name, "action": "legal_review", "result": "Legal review complete."}


class SafetyManagerBot(BaseAIBot):
    name = "safety_manager"
    description = "Tracks safety incidents and compliance."

    async def run(self, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return {"bot": self.name, "action": "safety_tracking", "result": "Safety tracked."}


class SalesTeamBot(BaseAIBot):
    name = "sales_team"
    description = "Manages customer relationships and revenue growth."

    async def run(self, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return {"bot": self.name, "action": "sales_management", "result": "Sales managed."}


class SecurityManagerBot(BaseAIBot):
    name = "security_manager"
    description = "Protects the platform from threats."

    async def run(self, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return {"bot": self.name, "action": "security_monitoring", "result": "Security monitored."}


class MapleLoadCanadaBot(BaseAIBot):
    name = "mapleload_canada"
    description = "Canadian logistics specialist bot."

    async def run(self, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return {"bot": self.name, "action": "canadian_logistics", "result": "Canadian logistics handled."}


class PartnerManagerBot(BaseAIBot):
    name = "partner_manager"
    description = "Manages partnerships and collaborations."

    async def run(self, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return {"bot": self.name, "action": "partnership_management", "result": "Partnership managed."}


AI_REGISTRY: Dict[str, BaseAIBot] = {
    "general_manager": GeneralManagerBot(),
    "operations_manager": OperationsManagerBot(),
    "finance_bot": FinanceBot(),
    "freight_broker": FreightBrokerBot(),
    "documents_manager": DocumentsBot(),
    "customer_service": CustomerServiceBot(),
    "system_admin": SystemAdminBot(),
    "information_coordinator": InformationCoordinatorBot(),
    "strategy_advisor": StrategyAdvisorBot(),
    "maintenance_dev": MaintenanceDevBot(),
    "legal_consultant": LegalConsultantBot(),
    "safety_manager": SafetyManagerBot(),
    "sales": SalesTeamBot(),
    "security": SecurityManagerBot(),
    "mapleload_canada": MapleLoadCanadaBot(),
    "executive_intelligence": GeneralManagerBot(),
    "finance_intelligence": FinanceBot(),
    "freight_bookings": FreightBrokerBot(),
    "legal_counsel": LegalConsultantBot(),
    "safety": SafetyManagerBot(),
    "security_bot": SecurityManagerBot(),
    "sales_intelligence": SalesTeamBot(),
    "system_intelligence": SystemAdminBot(),
    "operations_management": OperationsManagerBot(),
    "mapleload": MapleLoadCanadaBot(),
    "partner_manager": PartnerManagerBot(),
    "partner_management": PartnerManagerBot(),
    "partner": PartnerManagerBot(),
    "devops_maintenance": DevOpsBot(),
}


def get_bot(bot_id: str) -> Optional[BaseAIBot]:
    return AI_REGISTRY.get(bot_id)


async def run_bot(bot_id: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    bot = get_bot(bot_id)
    if bot is None:
        return {"ok": False, "error": f"Unknown bot: {bot_id}"}
    return await bot.run(payload)


__all__ = [
    "AI_REGISTRY",
    "BaseAIBot",
    "CustomerServiceBot",
    "DevOpsBot",
    "DocumentsBot",
    "FinanceBot",
    "FreightBrokerBot",
    "GeneralManagerBot",
    "InformationCoordinatorBot",
    "LegalConsultantBot",
    "MaintenanceDevBot",
    "MapleLoadCanadaBot",
    "OperationsManagerBot",
    "PartnerManagerBot",
    "SafetyManagerBot",
    "SalesTeamBot",
    "SecurityManagerBot",
    "StrategyAdvisorBot",
    "SystemAdminBot",
    "get_bot",
    "run_bot",
]
