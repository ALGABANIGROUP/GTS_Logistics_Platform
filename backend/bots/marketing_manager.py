"""
Marketing Manager Bot
Campaign management, lead generation, ROI analysis, customer segmentation, and promotion workflows.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
import copy


class MarketingManagerBot:
    """Shared-runtime marketing manager with campaign and lead workflows."""

    def __init__(self) -> None:
        self.name = "marketing_manager"
        self.display_name = "AI Marketing Manager"
        self.description = "Runs campaigns, scores leads, analyzes ROI, and segments customers"
        self.version = "2.0.0"
        self.mode = "growth"
        self.is_active = True

        now = datetime.now(timezone.utc)
        self.campaigns: List[Dict[str, Any]] = [
            {
                "campaign_id": "CAMP001",
                "name": "Spring Freight Growth",
                "type": "email",
                "channel": "Email",
                "budget": 5000.0,
                "spent": 750.0,
                "start_date": (now - timedelta(days=14)).date().isoformat(),
                "end_date": (now + timedelta(days=16)).date().isoformat(),
                "target_audience": {"industry": "retail", "size": "mid-market"},
                "content": "Promote seasonal freight capacity and onboarding support.",
                "goals": {"leads": 80, "revenue": 30000},
                "status": "active",
                "created_at": (now - timedelta(days=15)).isoformat(),
            },
            {
                "campaign_id": "CAMP002",
                "name": "Search Expansion Campaign",
                "type": "search",
                "channel": "Google Ads",
                "budget": 10000.0,
                "spent": 3200.0,
                "start_date": (now - timedelta(days=5)).date().isoformat(),
                "end_date": (now + timedelta(days=25)).date().isoformat(),
                "target_audience": {"intent": "high", "region": "GCC"},
                "content": "Capture high-intent logistics and transport searches.",
                "goals": {"leads": 60, "revenue": 45000},
                "status": "active",
                "created_at": (now - timedelta(days=6)).isoformat(),
            },
        ]
        self.campaign_performance: List[Dict[str, Any]] = [
            {
                "campaign_id": "CAMP001",
                "report_date": now.date().isoformat(),
                "impressions": 15000,
                "clicks": 750,
                "ctr": 5.0,
                "conversions": 25,
                "conversion_rate": 3.33,
                "cost": 500.0,
                "revenue": 2500.0,
                "roi": 400.0,
                "leads_generated": 25,
            },
            {
                "campaign_id": "CAMP002",
                "report_date": now.date().isoformat(),
                "impressions": 22000,
                "clicks": 880,
                "ctr": 4.0,
                "conversions": 30,
                "conversion_rate": 3.41,
                "cost": 1100.0,
                "revenue": 4300.0,
                "roi": 290.91,
                "leads_generated": 30,
            },
        ]
        self.leads: List[Dict[str, Any]] = [
            {
                "lead_id": "LEAD001",
                "source_campaign": "CAMP001",
                "source_channel": "Email",
                "first_name": "Ahmed",
                "last_name": "Al Salmi",
                "email": "ahmed@company.com",
                "phone": "+971501111111",
                "company": "Hope Trading",
                "position": "Operations Director",
                "lead_score": 85,
                "lead_status": "qualified",
                "converted_to_customer": False,
                "customer_id": None,
                "created_at": (now - timedelta(days=3)).isoformat(),
                "interactions": [{"type": "email_open", "timestamp": (now - timedelta(days=2)).isoformat()}],
            },
            {
                "lead_id": "LEAD002",
                "source_campaign": "CAMP002",
                "source_channel": "Google Ads",
                "first_name": "Noura",
                "last_name": "Al Qahtani",
                "email": "noura@business.com",
                "phone": "+971552222222",
                "company": "Noor Holdings",
                "position": "Marketing Manager",
                "lead_score": 70,
                "lead_status": "new",
                "converted_to_customer": False,
                "customer_id": None,
                "created_at": (now - timedelta(days=1)).isoformat(),
                "interactions": [],
            },
        ]
        self.promotions: List[Dict[str, Any]] = [
            {
                "promo_id": "PROMO001",
                "name": "10% New Customer Discount",
                "type": "discount",
                "discount_value": 10.0,
                "min_purchase": None,
                "valid_from": now.date().isoformat(),
                "valid_to": (now + timedelta(days=45)).date().isoformat(),
                "target_segment": "new",
                "status": "active",
            }
        ]
        self.customer_promotions: List[Dict[str, Any]] = []
        self.customers: List[Dict[str, Any]] = [
            {"customer_id": "CUST001", "name": "Hope Trading", "total_spent": 75000, "orders_count": 15, "last_order_date": (now - timedelta(days=10)).isoformat(), "segment": "high_value"},
            {"customer_id": "CUST002", "name": "Noor Holdings", "total_spent": 45000, "orders_count": 8, "last_order_date": (now - timedelta(days=25)).isoformat(), "segment": "medium_value"},
            {"customer_id": "CUST003", "name": "Salam Retail", "total_spent": 120000, "orders_count": 22, "last_order_date": (now - timedelta(days=5)).isoformat(), "segment": "high_value"},
            {"customer_id": "CUST004", "name": "Fahd Stores", "total_spent": 8000, "orders_count": 2, "last_order_date": (now - timedelta(days=70)).isoformat(), "segment": "at_risk"},
        ]

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        context = payload.get("context", {}) or {}
        action = payload.get("action") or context.get("action") or payload.get("meta", {}).get("action") or "status"

        if action == "status":
            return await self.status()
        if action == "config":
            return await self.config()
        if action == "dashboard":
            return await self.get_dashboard()
        if action == "create_campaign":
            return await self.create_campaign(context.get("data") or payload.get("data") or context)
        if action == "get_active_campaigns":
            return await self.get_active_campaigns()
        if action == "record_campaign_performance":
            return await self.record_campaign_performance(
                str(context.get("campaign_id") or payload.get("campaign_id") or ""),
                context.get("metrics") or payload.get("metrics") or {},
            )
        if action == "analyze_campaign":
            return await self.analyze_campaign(str(context.get("campaign_id") or payload.get("campaign_id") or ""))
        if action == "update_campaign_status":
            return await self.update_campaign_status(
                str(context.get("campaign_id") or payload.get("campaign_id") or ""),
                str(context.get("status") or payload.get("status") or ""),
            )
        if action == "add_lead":
            return await self.add_lead(context.get("data") or payload.get("data") or context)
        if action == "qualify_lead":
            return await self.qualify_lead(
                str(context.get("lead_id") or payload.get("lead_id") or ""),
                str(context.get("status") or payload.get("status") or "contacted"),
                context.get("notes") or payload.get("notes"),
            )
        if action == "convert_lead":
            return await self.convert_lead(
                str(context.get("lead_id") or payload.get("lead_id") or ""),
                str(context.get("customer_id") or payload.get("customer_id") or ""),
            )
        if action == "get_top_leads":
            return await self.get_top_leads(int(context.get("limit") or payload.get("limit") or 10))
        if action == "analyze_leads":
            return await self.analyze_leads()
        if action == "analyze_channel_roi":
            return await self.analyze_channel_roi()
        if action == "forecast_roi":
            return await self.forecast_roi(float(context.get("budget") or payload.get("budget") or 0))
        if action == "calculate_cac":
            return await self.calculate_cac()
        if action == "segment_customers":
            return await self.segment_customers()
        if action == "get_segment_customers":
            return await self.get_segment_customers(str(context.get("segment_name") or payload.get("segment_name") or ""))
        if action == "suggest_segment_strategies":
            return await self.suggest_segment_strategies(str(context.get("segment_name") or payload.get("segment_name") or ""))
        if action == "create_promotion":
            return await self.create_promotion(context.get("data") or payload.get("data") or context)
        if action == "send_promotion_to_segment":
            return await self.send_promotion_to_segment(
                str(context.get("segment") or payload.get("segment") or ""),
                str(context.get("promo_id") or payload.get("promo_id") or ""),
            )
        return await self.status()

    async def process_message(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        context = context or {}
        if context.get("action"):
            return await self.run({"context": context})

        text = (message or "").lower()
        if "campaign" in text:
            return await self.get_active_campaigns()
        if "lead" in text:
            return await self.analyze_leads()
        if "roi" in text or "forecast" in text:
            return await self.forecast_roi(float(context.get("budget") or 10000))
        if "segment" in text:
            return await self.segment_customers()
        return await self.get_dashboard()

    async def status(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "bot": self.name,
            "display_name": self.display_name,
            "version": self.version,
            "mode": self.mode,
            "is_active": self.is_active,
            "campaigns": len(self.campaigns),
            "leads": len(self.leads),
            "message": "Marketing workflows are active.",
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
                "create_campaign",
                "get_active_campaigns",
                "record_campaign_performance",
                "analyze_campaign",
                "update_campaign_status",
                "add_lead",
                "qualify_lead",
                "convert_lead",
                "get_top_leads",
                "analyze_leads",
                "analyze_channel_roi",
                "forecast_roi",
                "calculate_cac",
                "segment_customers",
                "get_segment_customers",
                "suggest_segment_strategies",
                "create_promotion",
                "send_promotion_to_segment",
            ],
        }

    async def create_campaign(self, campaign_data: Dict[str, Any]) -> Dict[str, Any]:
        now = datetime.now(timezone.utc)
        campaign_id = f"CAMP{now.strftime('%y%m%d%H%M%S')}{len(self.campaigns):02d}"
        campaign = {
            "campaign_id": campaign_id,
            "name": campaign_data.get("name", "Untitled Campaign"),
            "type": campaign_data.get("type", "email"),
            "channel": campaign_data.get("channel", "Email"),
            "budget": float(campaign_data.get("budget", 0) or 0),
            "spent": 0.0,
            "start_date": campaign_data.get("start_date") or now.date().isoformat(),
            "end_date": campaign_data.get("end_date"),
            "target_audience": campaign_data.get("target_audience", {}),
            "content": campaign_data.get("content", ""),
            "goals": campaign_data.get("goals", {}),
            "status": "draft",
            "created_at": now.isoformat(),
        }
        self.campaigns.insert(0, campaign)
        return {"ok": True, "campaign": copy.deepcopy(campaign)}

    async def update_campaign_status(self, campaign_id: str, status: str) -> Dict[str, Any]:
        campaign = self._find_campaign(campaign_id)
        if not campaign:
            return {"ok": False, "error": f"Campaign '{campaign_id}' not found"}
        campaign["status"] = status or campaign["status"]
        return {"ok": True, "campaign_id": campaign_id, "new_status": campaign["status"]}

    async def record_campaign_performance(self, campaign_id: str, metrics: Dict[str, Any]) -> Dict[str, Any]:
        campaign = self._find_campaign(campaign_id)
        if not campaign:
            return {"ok": False, "error": f"Campaign '{campaign_id}' not found"}
        impressions = int(metrics.get("impressions", 0) or 0)
        clicks = int(metrics.get("clicks", 0) or 0)
        conversions = int(metrics.get("conversions", 0) or 0)
        cost = float(metrics.get("cost", 0) or 0)
        revenue = float(metrics.get("revenue", 0) or 0)
        ctr = round((clicks / impressions) * 100, 2) if impressions else 0.0
        conversion_rate = round((conversions / clicks) * 100, 2) if clicks else 0.0
        roi = round(((revenue - cost) / cost) * 100, 2) if cost else 0.0
        performance = {
            "campaign_id": campaign_id,
            "report_date": datetime.now(timezone.utc).date().isoformat(),
            "impressions": impressions,
            "clicks": clicks,
            "ctr": ctr,
            "conversions": conversions,
            "conversion_rate": conversion_rate,
            "cost": cost,
            "revenue": revenue,
            "roi": roi,
            "leads_generated": conversions,
        }
        self.campaign_performance.append(performance)
        campaign["spent"] = round(float(campaign.get("spent", 0)) + cost, 2)
        return {"ok": True, "performance": performance}

    async def analyze_campaign(self, campaign_id: str) -> Dict[str, Any]:
        campaign = self._find_campaign(campaign_id)
        if not campaign:
            return {"ok": False, "error": f"Campaign '{campaign_id}' not found"}
        performance = [item for item in self.campaign_performance if item["campaign_id"] == campaign_id]
        total_cost = sum(item["cost"] for item in performance)
        total_revenue = sum(item["revenue"] for item in performance)
        total_clicks = sum(item["clicks"] for item in performance)
        total_impressions = sum(item["impressions"] for item in performance)
        total_conversions = sum(item["conversions"] for item in performance)
        roi = round(((total_revenue - total_cost) / total_cost) * 100, 2) if total_cost else 0.0
        return {
            "ok": True,
            "campaign_id": campaign_id,
            "campaign_name": campaign["name"],
            "metrics": {
                "total_impressions": total_impressions,
                "total_clicks": total_clicks,
                "total_conversions": total_conversions,
                "total_cost": total_cost,
                "total_revenue": total_revenue,
            },
            "averages": {
                "ctr": round((total_clicks / total_impressions) * 100, 2) if total_impressions else 0.0,
                "conversion_rate": round((total_conversions / total_clicks) * 100, 2) if total_clicks else 0.0,
                "roi": roi,
                "cpa": round(total_cost / total_conversions, 2) if total_conversions else 0.0,
            },
        }

    async def get_active_campaigns(self) -> Dict[str, Any]:
        campaigns = [copy.deepcopy(item) for item in self.campaigns if item["status"] == "active"]
        return {"ok": True, "count": len(campaigns), "campaigns": campaigns}

    async def add_lead(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        now = datetime.now(timezone.utc)
        lead_id = f"LEAD{now.strftime('%y%m%d%H%M%S')}{len(self.leads):02d}"
        lead = {
            "lead_id": lead_id,
            "source_campaign": lead_data.get("source_campaign"),
            "source_channel": lead_data.get("source_channel", "unknown"),
            "first_name": lead_data.get("first_name", ""),
            "last_name": lead_data.get("last_name", ""),
            "email": lead_data.get("email", ""),
            "phone": lead_data.get("phone"),
            "company": lead_data.get("company"),
            "position": lead_data.get("position"),
            "lead_score": self._lead_score(lead_data),
            "lead_status": "new",
            "converted_to_customer": False,
            "customer_id": None,
            "created_at": now.isoformat(),
            "interactions": [],
        }
        self.leads.insert(0, lead)
        return {"ok": True, "lead": copy.deepcopy(lead)}

    async def qualify_lead(self, lead_id: str, status: str, notes: Optional[str] = None) -> Dict[str, Any]:
        lead = self._find_lead(lead_id)
        if not lead:
            return {"ok": False, "error": f"Lead '{lead_id}' not found"}
        lead["lead_status"] = status or lead["lead_status"]
        lead["interactions"].append({"type": "qualification", "timestamp": datetime.now(timezone.utc).isoformat(), "notes": notes or ""})
        return {"ok": True, "lead_id": lead_id, "new_status": lead["lead_status"]}

    async def convert_lead(self, lead_id: str, customer_id: str) -> Dict[str, Any]:
        lead = self._find_lead(lead_id)
        if not lead:
            return {"ok": False, "error": f"Lead '{lead_id}' not found"}
        lead["lead_status"] = "converted"
        lead["converted_to_customer"] = True
        lead["customer_id"] = customer_id
        return {"ok": True, "lead_id": lead_id, "customer_id": customer_id}

    async def get_top_leads(self, limit: int = 10) -> Dict[str, Any]:
        active = [copy.deepcopy(item) for item in self.leads if item["lead_status"] in {"new", "contacted", "qualified"}]
        active.sort(key=lambda item: item["lead_score"], reverse=True)
        return {"ok": True, "count": min(limit, len(active)), "leads": active[:limit]}

    async def analyze_leads(self) -> Dict[str, Any]:
        total = len(self.leads)
        by_source: Dict[str, int] = {}
        by_status: Dict[str, int] = {}
        for lead in self.leads:
            by_source[lead.get("source_channel", "unknown")] = by_source.get(lead.get("source_channel", "unknown"), 0) + 1
            by_status[lead["lead_status"]] = by_status.get(lead["lead_status"], 0) + 1
        return {
            "ok": True,
            "total_leads": total,
            "by_source": by_source,
            "by_status": by_status,
            "conversion_rate": round((by_status.get("converted", 0) / total) * 100, 2) if total else 0.0,
        }

    async def analyze_channel_roi(self) -> Dict[str, Any]:
        grouped: Dict[str, Dict[str, Any]] = {}
        for campaign in self.campaigns:
            channel = campaign["channel"]
            if channel not in grouped:
                grouped[channel] = {"total_cost": 0.0, "total_revenue": 0.0, "total_conversions": 0, "campaigns_count": 0}
            grouped[channel]["campaigns_count"] += 1
            for perf in [item for item in self.campaign_performance if item["campaign_id"] == campaign["campaign_id"]]:
                grouped[channel]["total_cost"] += perf["cost"]
                grouped[channel]["total_revenue"] += perf["revenue"]
                grouped[channel]["total_conversions"] += perf["conversions"]
        for data in grouped.values():
            cost = data["total_cost"]
            revenue = data["total_revenue"]
            conversions = data["total_conversions"]
            data["roi_percent"] = round(((revenue - cost) / cost) * 100, 2) if cost else 0.0
            data["cac"] = round(cost / conversions, 2) if conversions else 0.0
        ordered = sorted(grouped.items(), key=lambda item: item[1]["roi_percent"], reverse=True)
        return {"ok": True, "by_channel": grouped, "best_channel": ordered[0] if ordered else None, "worst_channel": ordered[-1] if ordered else None}

    async def forecast_roi(self, budget: float) -> Dict[str, Any]:
        roi_values = [item["roi"] for item in self.campaign_performance]
        average_roi = sum(roi_values) / len(roi_values) if roi_values else 0.0
        predicted_revenue = round(budget * (1 + (average_roi / 100)), 2)
        return {"ok": True, "budget": budget, "predicted_roi_percent": round(average_roi, 2), "predicted_revenue": predicted_revenue, "confidence": "medium" if len(roi_values) < 5 else "high"}

    async def calculate_cac(self) -> Dict[str, Any]:
        total_cost = sum(item["spent"] for item in self.campaigns)
        converted = len([item for item in self.leads if item["converted_to_customer"]])
        cac = round(total_cost / converted, 2) if converted else 0.0
        return {"ok": True, "total_cost": total_cost, "new_customers": converted, "cac": cac, "is_efficient": cac < 500 or converted == 0}

    async def segment_customers(self) -> Dict[str, Any]:
        segments = {
            "high_value": [c for c in self.customers if c["total_spent"] > 50000],
            "medium_value": [c for c in self.customers if 10000 <= c["total_spent"] <= 50000],
            "low_value": [c for c in self.customers if c["total_spent"] < 10000],
            "loyal": [c for c in self.customers if c["orders_count"] > 10],
            "at_risk": [c for c in self.customers if 60 <= self._days_since(c["last_order_date"]) < 90],
            "new": [c for c in self.customers if self._days_since(c["last_order_date"]) < 30 and c["orders_count"] <= 1],
        }
        stats = {
            name: {
                "count": len(items),
                "avg_spent": round(sum(c["total_spent"] for c in items) / len(items), 2) if items else 0.0,
                "percentage": round((len(items) / len(self.customers)) * 100, 2) if self.customers else 0.0,
            }
            for name, items in segments.items()
        }
        return {"ok": True, "total_customers": len(self.customers), "segments": stats}

    async def get_segment_customers(self, segment_name: str) -> Dict[str, Any]:
        segmented = await self.segment_customers()
        if not segmented["ok"]:
            return segmented
        if segment_name == "high_value":
            customers = [c for c in self.customers if c["total_spent"] > 50000]
        elif segment_name == "medium_value":
            customers = [c for c in self.customers if 10000 <= c["total_spent"] <= 50000]
        elif segment_name == "low_value":
            customers = [c for c in self.customers if c["total_spent"] < 10000]
        elif segment_name == "loyal":
            customers = [c for c in self.customers if c["orders_count"] > 10]
        elif segment_name == "at_risk":
            customers = [c for c in self.customers if 60 <= self._days_since(c["last_order_date"]) < 90]
        else:
            customers = []
        return {"ok": True, "segment_name": segment_name, "count": len(customers), "customers": copy.deepcopy(customers)}

    async def suggest_segment_strategies(self, segment_name: str) -> Dict[str, Any]:
        strategies = {
            "high_value": ["Offer a VIP loyalty program.", "Give early access to premium services."],
            "medium_value": ["Run targeted upsell offers.", "Bundle complementary freight services."],
            "low_value": ["Launch a welcome sequence.", "Test onboarding discounts."],
            "at_risk": ["Send a recovery promotion.", "Have sales do direct outreach."],
            "new": ["Start a welcome drip campaign.", "Promote the second-order incentive."],
            "loyal": ["Invite to referral program.", "Use ambassador-style retention offers."],
        }
        return {"ok": True, "segment_name": segment_name, "strategies": strategies.get(segment_name, ["Use general nurture messaging."])}

    async def create_promotion(self, promo_data: Dict[str, Any]) -> Dict[str, Any]:
        now = datetime.now(timezone.utc)
        promo_id = f"PROMO{now.strftime('%y%m%d%H%M%S')}{len(self.promotions):02d}"
        promotion = {
            "promo_id": promo_id,
            "name": promo_data.get("name", "Untitled Promotion"),
            "type": promo_data.get("type", "discount"),
            "discount_value": float(promo_data.get("discount_value", 0) or 0),
            "min_purchase": promo_data.get("min_purchase"),
            "valid_from": promo_data.get("valid_from") or now.date().isoformat(),
            "valid_to": promo_data.get("valid_to") or (now + timedelta(days=30)).date().isoformat(),
            "target_segment": promo_data.get("target_segment"),
            "status": "active",
        }
        self.promotions.insert(0, promotion)
        return {"ok": True, "promotion": copy.deepcopy(promotion)}

    async def send_promotion_to_segment(self, segment_name: str, promo_id: str) -> Dict[str, Any]:
        customers = (await self.get_segment_customers(segment_name)).get("customers", [])
        sent = 0
        for customer in customers[:50]:
            self.customer_promotions.append(
                {
                    "customer_id": customer["customer_id"],
                    "promo_id": promo_id,
                    "sent_at": datetime.now(timezone.utc).isoformat(),
                }
            )
            sent += 1
        return {"ok": True, "segment": segment_name, "promo_id": promo_id, "sent_count": sent}

    async def get_dashboard(self) -> Dict[str, Any]:
        active_campaigns = [item for item in self.campaigns if item["status"] == "active"]
        converted = len([item for item in self.leads if item["converted_to_customer"]])
        impressions = sum(item["impressions"] for item in self.campaign_performance)
        clicks = sum(item["clicks"] for item in self.campaign_performance)
        conversions = sum(item["conversions"] for item in self.campaign_performance)
        revenue = sum(item["revenue"] for item in self.campaign_performance)
        return {
            "ok": True,
            "campaigns": {
                "total": len(self.campaigns),
                "active": len(active_campaigns),
                "total_spent": round(sum(item["spent"] for item in self.campaigns), 2),
            },
            "leads": {
                "total": len(self.leads),
                "new": len([item for item in self.leads if item["lead_status"] == "new"]),
                "qualified": len([item for item in self.leads if item["lead_status"] == "qualified"]),
                "converted": converted,
                "conversion_rate": round((converted / len(self.leads)) * 100, 2) if self.leads else 0.0,
            },
            "today": {
                "impressions": impressions,
                "clicks": clicks,
                "conversions": conversions,
                "revenue": revenue,
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def _find_campaign(self, campaign_id: str) -> Optional[Dict[str, Any]]:
        return next((item for item in self.campaigns if item["campaign_id"] == campaign_id), None)

    def _find_lead(self, lead_id: str) -> Optional[Dict[str, Any]]:
        return next((item for item in self.leads if item["lead_id"] == lead_id), None)

    def _lead_score(self, lead_data: Dict[str, Any]) -> int:
        score = 50
        email = str(lead_data.get("email") or "")
        if "@" in email and not email.endswith(("@gmail.com", "@yahoo.com", "@hotmail.com")):
            score += 15
        position = str(lead_data.get("position") or "").lower()
        if any(term in position for term in ("director", "head", "chief", "manager")):
            score += 20
        if lead_data.get("phone"):
            score += 10
        if lead_data.get("source_campaign"):
            score += 5
        return min(score, 100)

    def _days_since(self, iso_value: str) -> int:
        return (datetime.now(timezone.utc) - datetime.fromisoformat(iso_value)).days
