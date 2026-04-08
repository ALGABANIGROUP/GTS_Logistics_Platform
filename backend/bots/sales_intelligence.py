from __future__ import annotations
"""
SALE - Sales Intelligence Bot
Sales Intelligence
Manages customer relationships and drives revenue growth.
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
import asyncio
import copy


class SalesIntelligenceBot:
    """Sales Intelligence bot with dashboard, forecasting, and pipeline actions."""

    def __init__(self) -> None:
        self.name = "sales_intelligence"
        self.display_name = "Sales Intelligence"
        self.description = "Manages customer relationships and drives revenue growth"
        self.version = "1.1.0"
        self.mode = "intelligence"
        self.is_active = False

        self._seeded = False
        self._next_lead_id = 100
        self._next_deal_id = 100
        self._next_customer_id = 100

        self.leads_db: List[Dict[str, Any]] = []
        self.customers_db: List[Dict[str, Any]] = []
        self.deals_pipeline: List[Dict[str, Any]] = []
        self.revenue_data: List[Dict[str, Any]] = []

    async def _ensure_seed_data(self) -> None:
        if self._seeded:
            return

        now = datetime.now(timezone.utc)
        self.leads_db = [
            {
                "id": "LEAD_001",
                "name": "Tech Solutions Inc",
                "contact": "John Smith",
                "email": "john@techsolutions.com",
                "phone": "+1-555-0101",
                "status": "QUALIFIED",
                "source": "Website",
                "value": 15000,
                "created_at": now.isoformat(),
            },
            {
                "id": "LEAD_002",
                "name": "Global Logistics LLC",
                "contact": "Sarah Johnson",
                "email": "sarah@globallog.com",
                "phone": "+1-555-0102",
                "status": "CONTACTED",
                "source": "Referral",
                "value": 25000,
                "created_at": (now - timedelta(days=2)).isoformat(),
            },
            {
                "id": "LEAD_003",
                "name": "Northern Cold Chain",
                "contact": "Omar Rahman",
                "email": "omar@northerncold.com",
                "phone": "+1-555-0103",
                "status": "NEGOTIATION",
                "source": "LinkedIn",
                "value": 42000,
                "created_at": (now - timedelta(days=5)).isoformat(),
            },
        ]
        self.deals_pipeline = [
            {
                "id": "DEAL_001",
                "customer": "Acme Corporation",
                "value": 45000,
                "stage": "PROPOSAL",
                "probability": 60,
                "close_date": (now + timedelta(days=30)).isoformat(),
                "owner": "Sales Team",
            },
            {
                "id": "DEAL_002",
                "customer": "Pacific Shipping",
                "value": 32000,
                "stage": "NEGOTIATION",
                "probability": 75,
                "close_date": (now + timedelta(days=15)).isoformat(),
                "owner": "Sales Team",
            },
            {
                "id": "DEAL_003",
                "customer": "Metro Retail Group",
                "value": 88000,
                "stage": "DISCOVERY",
                "probability": 35,
                "close_date": (now + timedelta(days=45)).isoformat(),
                "owner": "Enterprise Desk",
            },
        ]
        self.customers_db = [
            {
                "id": "CUST_001",
                "name": "Acme Corporation",
                "industry": "Manufacturing",
                "segment": "VIP",
                "lifetime_value": 125000,
                "total_shipments": 45,
                "status": "Active",
                "since": "2024-01-15",
                "health": 92,
                "churn_risk": "LOW",
            },
            {
                "id": "CUST_002",
                "name": "Pacific Shipping",
                "industry": "Logistics",
                "segment": "REGULAR",
                "lifetime_value": 98000,
                "total_shipments": 38,
                "status": "Active",
                "since": "2024-03-20",
                "health": 84,
                "churn_risk": "LOW",
            },
            {
                "id": "CUST_003",
                "name": "Metro Retail Group",
                "industry": "Retail",
                "segment": "POTENTIAL",
                "lifetime_value": 61000,
                "total_shipments": 19,
                "status": "At Risk",
                "since": "2025-02-10",
                "health": 68,
                "churn_risk": "MEDIUM",
            },
        ]
        self.revenue_data = [
            {"month": "2026-01", "revenue": 118000},
            {"month": "2026-02", "revenue": 134000},
            {"month": "2026-03", "revenue": 151000},
        ]
        self._seeded = True

    async def _dispatch_action(self, action: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        await self._ensure_seed_data()
        payload = data or {}

        if action == "dashboard":
            return await self.get_dashboard_data()
        if action == "get_leads":
            return await self.get_leads()
        if action == "get_deals":
            return await self.get_deals()
        if action == "get_customers":
            return await self.get_customers()
        if action == "create_lead":
            return await self.create_lead(payload.get("data", payload))
        if action == "update_lead":
            return await self.update_lead(payload.get("lead_id"), payload.get("status"))
        if action == "create_deal":
            return await self.create_deal(payload.get("data", payload))
        if action == "update_deal":
            return await self.update_deal(payload.get("deal_id"), payload.get("stage"))
        if action == "analyze_customers":
            return await self.analyze_customer_behavior(payload.get("customer_id"))
        if action == "forecast_revenue":
            return await self.predict_revenue_growth(int(payload.get("months", 12) or 12))
        if action == "optimize_sales":
            return await self.optimize_sales_process()
        if action == "activate":
            return await self.activate_backend()
        if action == "pricing_strategy":
            return await self.get_pricing_strategy()
        if action == "competitor_analysis":
            return await self.get_competitor_analysis()
        if action == "recommendations":
            return await self.get_recommendations(payload.get("customer_id"))
        return await self.status()

    async def run(self, payload: dict) -> dict:
        """Main execution method."""
        action = (
            payload.get("action")
            or payload.get("context", {}).get("action")
            or payload.get("meta", {}).get("action")
            or "status"
        )
        return await self._dispatch_action(action, payload.get("context") or payload)

    async def status(self) -> dict:
        """Return current bot status."""
        await self._ensure_seed_data()
        return {
            "ok": True,
            "bot": self.name,
            "display_name": self.display_name,
            "version": self.version,
            "mode": self.mode,
            "is_active": self.is_active,
            "customers_tracked": len(self.customers_db),
            "active_deals": len(self.deals_pipeline),
            "message": "Backend activation pending" if not self.is_active else "Operational",
        }

    async def config(self) -> dict:
        """Return bot configuration."""
        return {
            "name": self.name,
            "display_name": self.display_name,
            "description": self.description,
            "version": self.version,
            "mode": self.mode,
            "capabilities": [
                "dashboard",
                "get_leads",
                "get_deals",
                "get_customers",
                "create_lead",
                "update_lead",
                "create_deal",
                "update_deal",
                "analyze_customers",
                "forecast_revenue",
                "optimize_sales",
                "pricing_strategy",
                "competitor_analysis",
                "recommendations",
                "activate",
            ],
        }

    async def activate_backend(self) -> dict:
        """Activate full backend capabilities."""
        await self._connect_to_crm()
        await self._setup_market_analysis()
        await self._configure_revenue_forecasting()
        self.is_active = True
        return {
            "ok": True,
            "status": "active",
            "message": f"{self.display_name} backend activated successfully",
        }

    async def _connect_to_crm(self) -> None:
        await asyncio.sleep(0.1)

    async def _setup_market_analysis(self) -> None:
        await asyncio.sleep(0.1)

    async def _configure_revenue_forecasting(self) -> None:
        await asyncio.sleep(0.1)

    async def analyze_customer_behavior(self, customer_id: Optional[str] = None) -> dict:
        """Analyze customer behavior patterns."""
        await self._ensure_seed_data()
        customer = None
        if customer_id:
            customer = next((item for item in self.customers_db if item["id"] == customer_id), None)

        return {
            "ok": True,
            "customer_id": customer_id,
            "customer": customer,
            "analysis": {
                "customer_segments": {
                    "high_value": 15,
                    "medium_value": 45,
                    "low_value": 40,
                },
                "purchase_patterns": {
                    "recurring": 65,
                    "one_time": 35,
                },
                "churn_risk": {
                    "high": 5,
                    "medium": 15,
                    "low": 80,
                },
                "upsell_opportunities": 23,
            },
            "recommendations": [
                "Focus on high-value customer retention.",
                "Target medium-value customers for upselling.",
                "Launch a recovery sequence for medium-risk accounts.",
            ],
        }

    async def predict_revenue_growth(self, months: int = 12) -> dict:
        """Predict revenue growth over specified period."""
        await self._ensure_seed_data()
        current_revenue = sum(item["value"] for item in self.deals_pipeline)
        monthly_growth_rate = 1.06

        projections = []
        for index in range(1, months + 1):
            projected = current_revenue * (monthly_growth_rate ** index)
            projections.append(
                {
                    "month": (datetime.now(timezone.utc) + timedelta(days=30 * index)).strftime("%Y-%m"),
                    "projected_revenue": round(projected, 2),
                    "projected": round(projected, 2),
                    "growth_rate": 6.0,
                }
            )

        return {
            "ok": True,
            "forecast": {
                "period_months": months,
                "current_revenue": current_revenue,
                "base_growth_rate": 6.0,
                "projections": projections,
                "key_drivers": [
                    "Market expansion",
                    "Customer acquisition",
                    "Upselling success",
                ],
                "risks": [
                    "Market saturation",
                    "Competitive pressure",
                    "Economic downturn",
                ],
            },
        }

    async def optimize_sales_process(self) -> dict:
        """Optimize sales process and pipeline."""
        await self._ensure_seed_data()
        stalled_deals = [deal for deal in self.deals_pipeline if deal["probability"] < 50]
        high_value_leads = [lead for lead in self.leads_db if lead["value"] >= 20000]
        total_opportunity = sum(item["value"] for item in stalled_deals) + sum(item["value"] for item in high_value_leads)

        return {
            "ok": True,
            "recommendations": [
                {
                    "priority": "HIGH",
                    "action": "Re-engage low-probability deals with a targeted commercial offer.",
                    "estimatedValue": sum(item["value"] for item in stalled_deals),
                },
                {
                    "priority": "HIGH",
                    "action": "Promote premium fulfillment services to qualified logistics accounts.",
                    "estimatedValue": sum(item["value"] for item in high_value_leads),
                },
            ],
            "totalOpportunity": total_opportunity,
            "optimizations": {
                "lead_scoring": {
                    "improvement": "15% more accurate",
                    "recommendation": "Use weighted intent signals from company size, budget, and source quality.",
                },
                "pipeline_management": {
                    "avg_deal_size": "$55,000",
                    "conversion_rate": "34%",
                    "recommendation": "Prioritize deals above $40k with a close date inside 45 days.",
                },
                "sales_cycle": {
                    "current_avg": "41 days",
                    "target": "32 days",
                    "recommendation": "Automate proposal follow-ups after 48 hours of inactivity.",
                },
            },
            "action_items": [
                "Launch a follow-up sequence for negotiation-stage deals.",
                "Promote bundle offers to logistics and retail accounts.",
                "Push premium monitoring as an upsell for qualified customers.",
            ],
        }

    async def get_dashboard_data(self) -> dict:
        """Get complete dashboard data."""
        await self._ensure_seed_data()
        leads = await self.get_leads()
        deals = await self.get_deals()
        customers = await self.get_customers()
        forecast = await self.predict_revenue_growth(6)
        recommendations = await self.get_recommendations()
        pricing = await self.get_pricing_strategy()
        competitors = await self.get_competitor_analysis()

        deals_list = deals.get("deals", [])
        total_revenue = sum(item.get("value", 0) for item in deals_list)
        strong_deals = [deal for deal in deals_list if deal.get("probability", 0) >= 70]

        return {
            "ok": True,
            "leads": leads.get("leads", []),
            "deals": deals_list,
            "customers": customers.get("customers", []),
            "forecast": forecast.get("forecast", {}).get("projections", []),
            "insights": {
                "pricing": pricing,
                "competitors": competitors,
                "recommendations": recommendations.get("recommendations", []),
            },
            "stats": {
                "totalLeads": len(leads.get("leads", [])),
                "totalDeals": len(deals_list),
                "totalRevenue": total_revenue,
                "conversionRate": round((len(strong_deals) / max(len(deals_list), 1)) * 100, 1),
                "avgDealSize": round(total_revenue / max(len(deals_list), 1), 2),
            },
        }

    async def get_leads(self) -> dict:
        """Get all sales leads."""
        await self._ensure_seed_data()
        return {"ok": True, "leads": copy.deepcopy(self.leads_db)}

    async def get_deals(self) -> dict:
        """Get all deals in pipeline."""
        await self._ensure_seed_data()
        return {"ok": True, "deals": copy.deepcopy(self.deals_pipeline)}

    async def get_customers(self) -> dict:
        """Get all customers."""
        await self._ensure_seed_data()
        return {"ok": True, "customers": copy.deepcopy(self.customers_db)}

    async def create_lead(self, data: dict) -> dict:
        """Create new lead."""
        await self._ensure_seed_data()
        self._next_lead_id += 1

        lead = {
            "id": f"LEAD_{self._next_lead_id}",
            "name": data.get("name", "New Lead"),
            "contact": data.get("contact", ""),
            "email": data.get("email", ""),
            "phone": data.get("phone", ""),
            "status": str(data.get("status") or "NEW").upper(),
            "source": data.get("source", "Manual"),
            "value": float(data.get("value", 0) or 0),
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        self.leads_db.insert(0, lead)

        if data.get("name"):
            self._next_customer_id += 1
            self.customers_db.insert(
                0,
                {
                    "id": f"CUST_{self._next_customer_id}",
                    "name": data.get("name"),
                    "industry": data.get("industry", "Unassigned"),
                    "segment": "NEW",
                    "lifetime_value": float(data.get("value", 0) or 0),
                    "total_shipments": 0,
                    "status": "Prospect",
                    "since": datetime.now(timezone.utc).date().isoformat(),
                    "health": 72,
                    "churn_risk": "LOW",
                },
            )

        return {"ok": True, "lead": lead, "message": "Lead created successfully"}

    async def update_lead(self, lead_id: str, status: str) -> dict:
        """Update lead status."""
        await self._ensure_seed_data()
        updated = None
        for lead in self.leads_db:
            if lead["id"] == lead_id:
                lead["status"] = str(status or lead["status"]).upper()
                updated = copy.deepcopy(lead)
                break

        return {
            "ok": True,
            "lead_id": lead_id,
            "status": str(status or "").upper(),
            "lead": updated,
            "message": f"Lead {lead_id} updated to {status}",
        }

    async def create_deal(self, data: dict) -> dict:
        """Create new deal."""
        await self._ensure_seed_data()
        self._next_deal_id += 1

        deal = {
            "id": f"DEAL_{self._next_deal_id}",
            "customer": data.get("customer", "New Customer"),
            "value": float(data.get("value", 0) or 0),
            "stage": str(data.get("stage") or "DISCOVERY").upper(),
            "probability": int(data.get("probability", 30) or 30),
            "close_date": data.get("close_date") or (datetime.now(timezone.utc) + timedelta(days=60)).isoformat(),
            "owner": "Sales Team",
        }
        self.deals_pipeline.insert(0, deal)
        return {"ok": True, "deal": deal, "message": "Deal created successfully"}

    async def update_deal(self, deal_id: str, stage: str) -> dict:
        """Update deal stage."""
        await self._ensure_seed_data()
        updated = None
        for deal in self.deals_pipeline:
            if deal["id"] == deal_id:
                deal["stage"] = str(stage or deal["stage"]).upper()
                updated = copy.deepcopy(deal)
                break

        return {
            "ok": True,
            "deal_id": deal_id,
            "stage": str(stage or "").upper(),
            "deal": updated,
            "message": f"Deal {deal_id} moved to {stage}",
        }

    async def get_pricing_strategy(self) -> dict:
        """Return a lightweight pricing strategy signal."""
        await self._ensure_seed_data()
        return {
            "ok": True,
            "strategy": {
                "mode": "dynamic",
                "demand_signal": "high",
                "recommended_adjustment_percent": 6,
                "bulk_discount_threshold": 5,
                "notes": [
                    "Protect margin on urgent fulfillment lanes.",
                    "Offer tiered discounts for repeat enterprise accounts.",
                ],
            },
        }

    async def get_competitor_analysis(self) -> dict:
        """Return competitor pricing and positioning signals."""
        await self._ensure_seed_data()
        return {
            "ok": True,
            "market_position": "above_average",
            "competitors": [
                {"name": "NorthStar Freight", "price_index": 0.96, "service_score": 0.77},
                {"name": "BlueRoute Logistics", "price_index": 1.08, "service_score": 0.82},
            ],
            "recommendations": [
                "Defend premium pricing on temperature-controlled routes.",
                "Counter low-cost rivals with bundled warehousing offers.",
            ],
        }

    async def get_recommendations(self, customer_id: Optional[str] = None) -> dict:
        """Return targeted sales recommendations."""
        await self._ensure_seed_data()
        customer = None
        if customer_id:
            customer = next((item for item in self.customers_db if item["id"] == customer_id), None)
        customer_name = customer["name"] if customer else "priority accounts"

        return {
            "ok": True,
            "customer_id": customer_id,
            "recommendations": [
                {
                    "type": "upsell",
                    "title": f"Offer premium monitoring to {customer_name}.",
                    "score": 88,
                },
                {
                    "type": "cross_sell",
                    "title": "Bundle storage and last-mile services for mid-market accounts.",
                    "score": 81,
                },
            ],
        }

    async def process_message(self, message: str, context: Optional[dict] = None) -> dict:
        """Process natural language sales requests."""
        context = context or {}
        action = context.get("action")
        if action:
            return await self._dispatch_action(action, context)

        message_lower = message.lower()
        if "customer" in message_lower or "analyze" in message_lower:
            return await self.analyze_customer_behavior()
        if "forecast" in message_lower or "revenue" in message_lower or "predict" in message_lower:
            return await self.predict_revenue_growth()
        if "optimize" in message_lower or "improve" in message_lower:
            return await self.optimize_sales_process()
        if "pricing" in message_lower:
            return await self.get_pricing_strategy()
        if "competitor" in message_lower:
            return await self.get_competitor_analysis()
        return await self.status()

