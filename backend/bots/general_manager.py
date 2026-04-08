from __future__ import annotations
# backend/bots/general_manager.py
import copy
import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from .base_bot import BaseBot

logger = logging.getLogger(__name__)

class GeneralManagerBot(BaseBot):
    """General Manager AI Assistant"""

    def __init__(self):
        super().__init__(
            name="GeneralManagerBot",
            description="AI assistant for general management tasks"
        )

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process management requests"""
        logger.info(f"GeneralManagerBot processing: {input_data.get('action')}")
        # Implement management logic
        return {
            "status": "success",
            "response": "Task processed by General Manager",
            "data": input_data
        }

    async def get_status(self) -> Dict[str, Any]:
        """Get bot status"""
        return {
            "name": self.name,
            "active": self.is_active,
            "description": self.description
        }
    """Enterprise executive bot with a unified management dashboard."""

    def __init__(self) -> None:
        self.name = "general_manager"
        self.display_name = "AI General Manager"
        self.description = "Executive orchestration, reporting, and decision support"
        self.version = "2.0.0"
        self.mode = "governance"
        self.is_active = True

        self._bots = [
            {"bot": "dispatcher", "status": "active", "reports_today": 41, "last_seen_minutes": 3},
            {"bot": "customer_service", "status": "active", "reports_today": 28, "last_seen_minutes": 4},
            {"bot": "sales_bot", "status": "active", "reports_today": 16, "last_seen_minutes": 8},
            {"bot": "safety_bot", "status": "active", "reports_today": 12, "last_seen_minutes": 11},
            {"bot": "intelligence_bot", "status": "active", "reports_today": 9, "last_seen_minutes": 17},
            {"bot": "mapleload_bot", "status": "active", "reports_today": 14, "last_seen_minutes": 13},
            {"bot": "documents_manager", "status": "active", "reports_today": 23, "last_seen_minutes": 6},
        ]
        self.strategic_initiatives: List[Dict[str, Any]] = [
            {
                "id": "INIT-201",
                "title": "US Market Expansion Program",
                "owner": "Expansion Office",
                "priority": "high",
                "status": "active",
                "progress": 64,
                "target_completion": "2026-07-15",
                "milestones": ["Carrier shortlist", "Pricing model", "Compliance review"],
            },
            {
                "id": "INIT-202",
                "title": "Customer Recovery Sprint",
                "owner": "Customer Service",
                "priority": "high",
                "status": "active",
                "progress": 48,
                "target_completion": "2026-04-18",
                "milestones": ["VIP triage", "Response SLA", "Ticket backlog reduction"],
            },
            {
                "id": "INIT-203",
                "title": "Fleet Maintenance Readiness",
                "owner": "Safety",
                "priority": "medium",
                "status": "planned",
                "progress": 22,
                "target_completion": "2026-05-30",
                "milestones": ["Inspection calendar", "Vendor booking", "Reserve vehicles"],
            },
        ]
        self.decision_log: List[Dict[str, Any]] = [
            {
                "id": "DEC-301",
                "title": "Approve Riyadh hiring request",
                "description": "Authorize three additional drivers for peak lanes.",
                "decision_maker": "General Manager",
                "outcome": "approved",
                "resolved": True,
                "logged_at": datetime.now(timezone.utc).isoformat(),
                "impact": "high",
            },
            {
                "id": "DEC-302",
                "title": "Review US expansion budget",
                "description": "Validate first-phase cross-border rollout budget.",
                "decision_maker": "General Manager",
                "outcome": "pending",
                "resolved": False,
                "logged_at": (datetime.now(timezone.utc) - timedelta(hours=6)).isoformat(),
                "impact": "high",
            },
        ]
        self.executive_reports: List[Dict[str, Any]] = []

    async def run(self, payload: dict) -> dict:
        """Main execution method."""
        context = payload.get("context", {}) or {}
        action = payload.get("action") or context.get("action") or payload.get("meta", {}).get("action") or "status"

        if action == "status":
            return await self.status()
        if action == "config":
            return await self.config()
        if action in {"dashboard", "executive_dashboard", "get_dashboard"}:
            return await self.get_dashboard()
        if action == "strategic_recommendations":
            return await self.get_strategic_recommendations()
        if action == "daily_briefing":
            return await self.get_daily_briefing()
        if action == "weekly_report":
            return await self.get_weekly_report()
        if action == "monthly_report":
            return await self.get_monthly_report()
        if action == "quarterly_report":
            return await self.get_quarterly_report()
        if action == "forecast":
            return await self.forecast_next_period(int(context.get("months", payload.get("months", 3)) or 3))
        if action == "leadership_meeting":
            return await self.prepare_leadership_meeting(str(context.get("meeting_type", payload.get("meeting_type", "weekly"))))
        if action == "company_overview":
            return await self.get_company_overview()
        if action == "bots_status":
            return await self.get_all_bots_status()
        if action == "create_initiative":
            return await self.create_initiative(context.get("data") or payload.get("data", {}))
        if action == "get_initiatives":
            return await self.get_initiatives()
        if action == "log_decision":
            return await self.log_decision(context.get("data") or payload.get("data", {}))
        if action == "get_decisions":
            return {"ok": True, "decisions": copy.deepcopy(self.decision_log)}
        if action == "evaluate_decision":
            return await self.evaluate_decision(context.get("decision") or payload.get("decision") or {})
        if action == "get_kpis":
            return await self.get_kpis()
        if action == "generate_report":
            report_type = str(context.get("report_type") or payload.get("report_type") or "weekly").lower()
            return await self.generate_report(report_type)
        return {"ok": False, "error": f"Unknown action: {action}"}

    async def process_message(self, message: str, context: Optional[dict] = None) -> dict:
        """Handle natural-language requests and explicit context actions."""
        context = context or {}
        if context.get("action"):
            return await self.run({"context": context})

        message_lower = (message or "").lower()
        if "dashboard" in message_lower or "overview" in message_lower:
            return await self.get_dashboard()
        if "briefing" in message_lower or "daily" in message_lower:
            return await self.get_daily_briefing()
        if "weekly" in message_lower:
            return await self.get_weekly_report()
        if "monthly" in message_lower:
            return await self.get_monthly_report()
        if "quarter" in message_lower:
            return await self.get_quarterly_report()
        if "forecast" in message_lower or "predict" in message_lower:
            return await self.forecast_next_period()
        if "recommend" in message_lower or "strategy" in message_lower:
            return await self.get_strategic_recommendations()
        if "team" in message_lower or "bot" in message_lower:
            return await self.get_all_bots_status()
        return await self.status()

    async def status(self) -> dict:
        """Return current executive bot status."""
        dashboard = self._dashboard_model()
        return {
            "ok": True,
            "bot": self.name,
            "display_name": self.display_name,
            "version": self.version,
            "mode": self.mode,
            "is_active": self.is_active,
            "metrics": {
                "activeTeams": {"value": dashboard["team_status"]["active_bots"], "target": 15, "status": "active"},
                "totalEmployees": {"value": 187, "target": 200, "status": "active"},
                "operationsStatus": {"value": f'{dashboard["department_performance"]["operations"]["score"]}%', "trend": "positive"},
                "responseTime": {"value": "0.4h", "trend": "neutral"},
            },
            "teams": dashboard["team_status"]["details"],
            "pending": dashboard["critical_alerts"],
            "activities": dashboard["strategic_recommendations"][:3],
            "reports": [report["title"] for report in self.executive_reports[-3:]],
            "message": "Executive command center operational",
        }

    async def config(self) -> dict:
        """Return available bot capabilities."""
        return {
            "name": self.name,
            "display_name": self.display_name,
            "description": self.description,
            "version": self.version,
            "mode": self.mode,
            "capabilities": [
                "dashboard",
                "strategic_recommendations",
                "daily_briefing",
                "weekly_report",
                "monthly_report",
                "quarterly_report",
                "forecast",
                "leadership_meeting",
                "company_overview",
                "bots_status",
                "create_initiative",
                "get_initiatives",
                "log_decision",
                "evaluate_decision",
                "get_kpis",
                "generate_report",
            ],
        }

    async def get_dashboard(self) -> dict:
        """Return the unified executive dashboard."""
        return {
            "ok": True,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            **self._dashboard_model(),
        }

    async def create_initiative(self, data: dict) -> dict:
        """Create a strategic initiative."""
        initiative = {
            "id": f"INIT-{len(self.strategic_initiatives) + 300}",
            "title": data.get("title", "New initiative"),
            "description": data.get("description", ""),
            "owner": data.get("owner", "Executive Office"),
            "priority": data.get("priority", "medium"),
            "status": data.get("status", "active"),
            "progress": int(data.get("progress", 0) or 0),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "target_completion": data.get("target_completion"),
            "milestones": data.get("milestones", []),
        }
        self.strategic_initiatives.insert(0, initiative)
        return {"ok": True, "initiative": initiative}

    async def get_initiatives(self) -> dict:
        """Return tracked strategic initiatives."""
        return {"ok": True, "initiatives": copy.deepcopy(self.strategic_initiatives)}

    async def generate_report(self, report_type: str) -> dict:
        """Return a report based on the requested type."""
        report_map = {
            "daily": self.get_daily_briefing,
            "weekly": self.get_weekly_report,
            "monthly": self.get_monthly_report,
            "quarterly": self.get_quarterly_report,
        }
        report = await report_map.get(report_type, self.get_weekly_report)()
        self.executive_reports.append(report)
        return {"ok": True, "report_type": report_type, "report": report}

    async def log_decision(self, data: dict) -> dict:
        """Log an executive decision."""
        decision = {
            "id": f"DEC-{len(self.decision_log) + 400}",
            "title": data.get("title", "Executive decision"),
            "description": data.get("description", ""),
            "decision_maker": data.get("decision_maker", "General Manager"),
            "outcome": data.get("outcome", "pending"),
            "resolved": bool(data.get("resolved", False)),
            "logged_at": datetime.now(timezone.utc).isoformat(),
            "impact": data.get("impact", "medium"),
        }
        self.decision_log.insert(0, decision)
        return {"ok": True, "decision": decision}

    async def get_kpis(self) -> dict:
        """Return the unified KPI block."""
        return {"ok": True, "kpis": copy.deepcopy(self._dashboard_model()["unified_kpi"])}

    async def get_strategic_recommendations(self) -> dict:
        """Return SWOT-style strategic guidance and a roadmap."""
        dashboard = self._dashboard_model()
        recommendations = copy.deepcopy(dashboard["strategic_recommendations"])
        return {
            "ok": True,
            "analysis": {
                "strengths": [
                    "Operations and safety scores are both above 90.",
                    "International expansion readiness is high.",
                    "Intelligence and sales signals are aligned on growth lanes.",
                ],
                "weaknesses": [
                    "Customer service remains the lowest-performing function.",
                    "A small cluster of delayed shipments is driving executive alerts.",
                ],
                "opportunities": [
                    "US expansion is commercially attractive.",
                    "Three partner promotions can improve retention.",
                    "Dynamic pricing can defend margin during peak periods.",
                ],
                "threats": [
                    "Fuel-price pressure on cross-border lanes.",
                    "VIP customer churn if service issues remain unresolved.",
                ],
                "overall_assessment": "Strong momentum with targeted service and execution gaps to close.",
            },
            "top_recommendations": recommendations,
            "roadmap": {
                "short_term": recommendations[:2],
                "medium_term": [
                    {
                        "title": "Strengthen customer-response workflows",
                        "priority": "high",
                        "expected_impact": "+0.3 CSAT improvement",
                        "timeframe": "30-60 days",
                    }
                ],
                "long_term": [
                    {
                        "title": "Scale US and Gulf market operations",
                        "priority": "high",
                        "expected_impact": "+25% international revenue",
                        "timeframe": "6-12 months",
                    }
                ],
            },
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    async def get_daily_briefing(self) -> dict:
        """Return a daily executive briefing."""
        dashboard = self._dashboard_model()
        return {
            "ok": True,
            "report_type": "daily_briefing",
            "title": "Daily executive briefing",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "executive_summary": "Operations are stable overall, with immediate attention needed on customer escalation and delayed shipments.",
            "key_metrics": {
                "unified_kpi": dashboard["unified_kpi"]["current"],
                "revenue_yesterday": 425000,
                "shipments_yesterday": 412,
                "customer_satisfaction": 4.2,
            },
            "critical_issues": copy.deepcopy(dashboard["critical_alerts"]),
            "focus_for_today": [
                "Resolve the VIP customer escalation.",
                "Approve the Riyadh hiring request.",
                "Review first-stage US expansion budget.",
            ],
        }

    async def get_weekly_report(self) -> dict:
        """Return a weekly executive report."""
        dashboard = self._dashboard_model()
        return {
            "ok": True,
            "report_type": "weekly_report",
            "title": "Weekly executive report",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "performance_summary": {
                "unified_kpi": dashboard["unified_kpi"]["current"],
                "revenue": 2_850_000,
                "shipments": 2_850,
                "customer_satisfaction": 4.3,
                "on_time_delivery": 94.2,
            },
            "department_reports": copy.deepcopy(dashboard["department_performance"]),
            "strategic_recommendations": copy.deepcopy(dashboard["strategic_recommendations"]),
        }

    async def get_monthly_report(self) -> dict:
        """Return a monthly executive report."""
        dashboard = self._dashboard_model()
        return {
            "ok": True,
            "report_type": "monthly_report",
            "title": "Monthly executive report",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "performance_highlights": {
                "revenue": {"actual": 12_500_000, "target": 12_000_000, "variance": "+4.2%"},
                "profit": {"actual": 2_800_000, "target": 2_500_000, "variance": "+12.0%"},
                "new_customers": {"actual": 85, "target": 70, "variance": "+21.4%"},
                "market_share": {"actual": 12.5, "target": 12.0, "variance": "+0.5"},
            },
            "department_performance": copy.deepcopy(dashboard["department_performance"]),
            "expansion_snapshot": copy.deepcopy(dashboard["expansion_snapshot"]),
            "next_month_priorities": [
                "Launch the US market pilot.",
                "Hire three additional Riyadh drivers.",
                "Reduce customer response-time backlog.",
            ],
        }

    async def get_quarterly_report(self) -> dict:
        """Return a board-style quarterly report."""
        return {
            "ok": True,
            "report_type": "quarterly_report",
            "title": "Quarterly board report",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "board_highlights": [
                "Revenue reached 36.2M SAR with 18.2% quarter-over-quarter growth.",
                "International shipment volume grew 35%.",
                "Unified executive score improved to 87.5.",
            ],
            "financial_performance": {
                "revenue": 36_200_000,
                "net_profit": 8_100_000,
                "profit_margin": 22.4,
                "roi": 18.5,
            },
            "next_quarter_plan": {
                "strategic_initiatives": [
                    "US market expansion",
                    "Customer app release",
                    "Driver hiring and maintenance readiness",
                ],
                "financial_targets": {
                    "revenue_target": 40_000_000,
                    "profit_target": 9_500_000,
                    "new_customers_target": 100,
                },
            },
        }

    async def forecast_next_period(self, months: int = 3) -> dict:
        """Return a lightweight strategic forecast."""
        forecasts: List[Dict[str, Any]] = []
        base_revenue = 12_500_000.0
        base_customers = 452

        for index in range(1, months + 1):
            month_date = datetime.now(timezone.utc) + timedelta(days=30 * index)
            seasonal = 1.12 if month_date.month in {4, 11, 12} else 1.04
            forecasts.append(
                {
                    "month": month_date.strftime("%Y-%m"),
                    "predicted_revenue": round(base_revenue * seasonal * (1 + index * 0.02), 2),
                    "predicted_customers": int(base_customers * (1 + index * 0.03)),
                    "predicted_shipments": int(12_000 * seasonal * (1 + index * 0.02)),
                    "confidence": "high" if index <= 2 else "medium",
                }
            )

        return {
            "ok": True,
            "forecast_date": datetime.now(timezone.utc).isoformat(),
            "months_ahead": months,
            "forecasts": forecasts,
            "growth_rate": "+18%",
            "assumptions": ["Stable market conditions", "Monthly customer growth near 3%"],
        }

    async def prepare_leadership_meeting(self, meeting_type: str = "weekly") -> dict:
        """Prepare an executive meeting pack."""
        normalized = meeting_type.strip().lower().replace("-", "_")
        agenda_map = {
            "daily": ["Yesterday performance", "Critical issues", "Today priorities"],
            "weekly": ["Weekly score review", "Cross-bot alerts", "Strategic recommendations", "Next-week plan"],
            "monthly": ["Monthly performance", "Financial review", "Initiative progress", "Expansion roadmap"],
        }
        attendees_map = {
            "daily": ["Operations lead", "Customer service lead"],
            "weekly": ["All department heads", "Finance lead", "Expansion lead"],
            "monthly": ["Executive leadership", "Department heads", "Planning manager"],
        }

        return {
            "ok": True,
            "meeting_date": datetime.now(timezone.utc).isoformat(),
            "meeting_type": normalized,
            "agenda": agenda_map.get(normalized, agenda_map["weekly"]),
            "required_attendees": attendees_map.get(normalized, attendees_map["weekly"]),
            "key_discussion_points": [
                "Delayed-shipment cluster and customer follow-up.",
                "US market readiness and carrier onboarding.",
                "Fleet maintenance readiness before next peak cycle.",
            ],
            "preparation_time_minutes": len(agenda_map.get(normalized, agenda_map["weekly"])) * 6,
        }

    async def get_company_overview(self) -> dict:
        """Return a concise company overview."""
        return {
            "ok": True,
            "company_name": "GTS Logistics",
            "established": 2020,
            "employees": 187,
            "drivers": 85,
            "vehicles": 120,
            "offices": ["Riyadh", "Jeddah", "Dammam", "Toronto"],
            "markets": ["Saudi Arabia", "Canada", "United States", "UAE"],
            "partners": 28,
            "customers": 452,
            "total_shipments_all_time": 152000,
            "vision": "Lead regional logistics through reliable and intelligent operations.",
            "mission": "Deliver integrated logistics with operational discipline and AI-led insight.",
        }

    async def get_all_bots_status(self) -> dict:
        """Return a status summary for connected bots."""
        details = [
            {
                "bot": item["bot"],
                "status": item["status"],
                "reports_today": item["reports_today"],
                "last_report": (datetime.now(timezone.utc) - timedelta(minutes=item["last_seen_minutes"])).isoformat(),
            }
            for item in self._bots
        ]
        return {
            "ok": True,
            "total_bots": len(details),
            "active_bots": sum(1 for item in details if item["status"] == "active"),
            "inactive_bots": sum(1 for item in details if item["status"] != "active"),
            "details": details,
        }

    async def evaluate_decision(self, decision: Dict[str, Any]) -> dict:
        """Evaluate an executive decision before approval."""
        decision_type = str(decision.get("type", "general")).lower()
        impact_matrix = {
            "expansion": {
                "positive": ["Revenue growth", "Market-share gains", "Brand reach"],
                "negative": ["Higher upfront cost", "Execution complexity", "Compliance risk"],
                "time_to_impact": "6-12 months",
                "success_probability": 78,
            },
            "hiring": {
                "positive": ["Higher capacity", "Lower delivery delays", "Better service resilience"],
                "negative": ["Payroll increase", "Training time"],
                "time_to_impact": "1-3 months",
                "success_probability": 84,
            },
            "technology": {
                "positive": ["Better data quality", "Operational leverage", "Faster decisions"],
                "negative": ["Implementation cost", "Temporary disruption"],
                "time_to_impact": "3-6 months",
                "success_probability": 81,
            },
        }
        analysis = impact_matrix.get(
            decision_type,
            {
                "positive": ["General performance uplift"],
                "negative": ["Unspecified execution risk"],
                "time_to_impact": "3-6 months",
                "success_probability": 58,
            },
        )
        return {
            "ok": True,
            "decision": decision,
            "analysis": {
                "expected_positive_impacts": analysis["positive"],
                "expected_negative_impacts": analysis["negative"],
                "time_to_realize": analysis["time_to_impact"],
                "success_probability": analysis["success_probability"],
                "recommendation": "recommended" if analysis["success_probability"] >= 75 else "proceed_with_caution",
            },
            "alternatives": self._decision_alternatives(decision_type),
            "risk_factors": self._decision_risks(decision_type),
        }

    def _dashboard_model(self) -> Dict[str, Any]:
        return {
            "unified_kpi": {
                "current": 87.5,
                "previous": 84.2,
                "change": "+3.3",
                "target": 90.0,
                "status": "improving",
            },
            "department_performance": {
                "operations": {"score": 92.3, "change": "+2.1", "status": "excellent"},
                "finance": {"score": 85.7, "change": "+1.5", "status": "good"},
                "customers": {"score": 78.4, "change": "-0.8", "status": "warning"},
                "safety": {"score": 95.6, "change": "+3.2", "status": "excellent"},
                "expansion": {"score": 82.1, "change": "+5.4", "status": "good"},
                "intelligence": {"score": 88.9, "change": "+2.3", "status": "good"},
            },
            "critical_alerts": [
                {"id": "ALT001", "title": "Delayed shipment cluster on Riyadh lanes", "severity": "high", "source": "dispatcher", "action_required": True},
                {"id": "ALT002", "title": "VIP customer escalation needs immediate callback", "severity": "high", "source": "customer_service", "action_required": True},
                {"id": "ALT003", "title": "Five vehicles due for maintenance this week", "severity": "medium", "source": "safety_bot", "action_required": True},
            ],
            "strategic_recommendations": [
                {"id": "REC001", "title": "Hire 3 additional Riyadh drivers", "priority": "high", "impact": "+15% route capacity", "owner": "HR / Operations", "deadline": (datetime.now(timezone.utc) + timedelta(days=7)).date().isoformat()},
                {"id": "REC002", "title": "Launch US market expansion pilot", "priority": "high", "impact": "+25% international revenue opportunity", "owner": "Expansion Office", "deadline": (datetime.now(timezone.utc) + timedelta(days=30)).date().isoformat()},
                {"id": "REC003", "title": "Promote 3 high-performing partners", "priority": "medium", "impact": "+10% partner retention", "owner": "Partner Success", "deadline": (datetime.now(timezone.utc) + timedelta(days=14)).date().isoformat()},
            ],
            "financial_snapshot": {"revenue": 12_500_000, "profit_margin": 22.4, "pending_payments": 3_450_000, "monthly_growth": 18.0},
            "operational_snapshot": {"total_shipments": 1_247, "on_time_delivery": 94.2, "delayed_shipments": 75, "active_drivers": 85},
            "customer_snapshot": {"customer_satisfaction": 4.2, "new_customers": 18, "open_tickets": 23, "churn_rate": 2.3},
            "expansion_snapshot": {"international_shipments": 345, "active_markets": ["US", "UK", "SA", "AE"], "planned_markets": ["DE", "MX", "SG"], "new_markets": 2},
            "intelligence_snapshot": {"new_opportunities": 3, "priority_markets": ["US", "SA", "AE"], "trend_signal": "positive"},
            "team_status": {
                "total_bots": len(self._bots),
                "active_bots": sum(1 for item in self._bots if item["status"] == "active"),
                "inactive_bots": sum(1 for item in self._bots if item["status"] != "active"),
                "details": [{"bot": item["bot"], "status": item["status"], "reports_today": item["reports_today"]} for item in self._bots],
            },
            "quick_actions": [
                "Approve Riyadh hiring request",
                "Review US pilot budget",
                "Escalate VIP-customer recovery plan",
            ],
        }

    def _decision_alternatives(self, decision_type: str) -> List[Dict[str, Any]]:
        options = {
            "expansion": [
                {"option": "Pilot one region first", "risk": "low", "cost": "300K", "time": "3-4 months"},
                {"option": "Partner-led market entry", "risk": "medium", "cost": "150K", "time": "2-3 months"},
            ],
            "hiring": [
                {"option": "Temporary contractor ramp", "risk": "low", "cost": "80K", "time": "2-4 weeks"},
                {"option": "Internal transfer and promotion", "risk": "medium", "cost": "50K", "time": "4-6 weeks"},
            ],
            "technology": [
                {"option": "Phase rollout by department", "risk": "low", "cost": "200K", "time": "2-3 months"},
                {"option": "External implementation partner", "risk": "medium", "cost": "350K", "time": "6-8 weeks"},
            ],
        }
        return options.get(decision_type, [{"option": "Run a smaller pilot", "risk": "unknown", "cost": "TBD", "time": "TBD"}])

    def _decision_risks(self, decision_type: str) -> List[str]:
        risks = {
            "expansion": ["Regulatory delays", "Carrier onboarding friction", "Higher than expected CAC"],
            "hiring": ["Slow ramp-up", "Training overhead", "Retention risk"],
            "technology": ["Implementation delays", "Adoption resistance", "Integration defects"],
        }
        return risks.get(decision_type, ["Unspecified execution risk"])


