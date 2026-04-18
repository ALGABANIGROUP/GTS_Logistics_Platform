from __future__ import annotations

import os
from datetime import datetime, timedelta
from typing import Any, Dict, List


class MapleLoadAIBot:
    """MapleLoad AI - Canadian freight sourcing agent (extensible scaffold)."""

    name = "mapleload"

    def __init__(self) -> None:
        self.base_url = os.getenv("INTERNAL_BASE_URL", "http://127.0.0.1:8010")
        self.email_from = os.getenv("MAPLELOAD_EMAIL_FROM", "freight@gabanilogistics.com")
        self.contact_name = os.getenv("MAPLELOAD_CONTACT_NAME", "Yassir Mossttafa")
        self.company_name = os.getenv("MAPLELOAD_COMPANY_NAME", "Gabani Transport Solutions (GTS)")

        # Search configuration
        self.search_providers = ["google_maps", "business_directories", "company_websites"]
        self.target_industries = ["Food", "Retail", "Manufacturing", "Wholesale", "Distribution"]
        self.canadian_provinces = ["ON", "QC", "BC", "AB", "MB", "SK", "NS", "NB", "NL", "PE", "YT", "NT", "NU"]

        # Email templates
        self.email_templates: Dict[str, Dict[str, str]] = {
            "initial_contact": {
                "subject": "Canadian Freight Support - Domestic Shipments",
                "body": """Hello {company_name},

I hope you're doing well.

My name is {contact_name}, reaching out from {company_name}, a Canada-based logistics company supporting businesses with domestic freight across Canada.

We work with shippers who need reliable capacity for palletized freight, LTL, and full truckload movements within Canada.

I wanted to quickly ask:
Do you currently manage outbound shipments internally, or work with external carriers/brokers?

If it makes sense, I'd be happy to connect briefly.

Best regards,
{contact_name}
{company_name}
{email_from}""",
            },
            "follow_up_5days": {
                "subject": "Quick follow-up - Canadian freight support",
                "body": """Hello {contact_person},

Just following up on my previous message.

We're currently onboarding Canadian shippers for domestic-only freight (no U.S. DOT or cross-border requirements).

If you're open to it, I'd be glad to understand your shipping lanes and see if we can support when needed.

Thank you,
{contact_name}""",
            },
            "positive_response": {
                "subject": "Next steps - Freight details",
                "body": """Hi {contact_person},

Thank you for getting back to me.

To better understand how we can support you, could you share:

- Typical origin & destination
- Load type (pallets / full truck)
- Frequency (weekly / monthly / seasonal)

I'll review internally and follow up promptly.

Best regards,
{contact_name}""",
            },
        }

        # Call script (text only)
        self.call_script = {
            "opening": "Hello {contact_person}, this is {contact_name} calling from {company_name} in Canada. I'm following up on a quick email we sent regarding domestic freight support.",
            "qualification": "I just wanted to ask: Do you ship within Canada regularly? Is this something handled in-house or via external partners?",
            "close": "No problem at all. I'll send a short follow-up email and we can reconnect whenever timing works.",
        }

        # In-memory storage (temporary)
        self.companies_db: List[Dict[str, Any]] = []
        self.leads_db: List[Dict[str, Any]] = []

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        payload:
          { "action": "search"|"qualify"|"outreach"|"report"|"test_email", "params": {...} }
        """
        action = (payload.get("action") or "search").lower()
        params = payload.get("params") or {}

        if action == "search":
            return await self._search_companies(params)
        if action == "qualify":
            return await self._qualify_leads(params)
        if action == "outreach":
            return await self._send_outreach(params)
        if action == "report":
            return await self._generate_report(params)
        if action == "test_email":
            return await self._send_test_email(params)

        return {"status": "error", "error": f"Unknown action: {action}"}

    async def process_message(self, message: str, context: Dict[str, Any] | None = None) -> Dict[str, Any]:
        ctx = context or {}
        payload = {
            "action": ctx.get("action") or "search",
            "params": ctx.get("params") or {},
            "message": message,
        }
        return await self.run(payload)

    async def _search_companies(self, params: Dict[str, Any]) -> Dict[str, Any]:
        try:
            industry = params.get("industry")
            province = params.get("province")
            city = params.get("city")
            limit = int(params.get("limit", 10))

            mock_companies = self._generate_mock_companies(limit, industry, province, city)

            for c in mock_companies:
                if c not in self.companies_db:
                    self.companies_db.append(c)

            return {
                "status": "success",
                "action": "search",
                "results": {
                    "total_found": len(mock_companies),
                    "companies": mock_companies,
                    "search_criteria": {"industry": industry, "province": province, "city": city, "limit": limit},
                },
                "message": f"Found {len(mock_companies)} Canadian companies",
            }
        except Exception as e:
            return {"status": "error", "action": "search", "error": str(e), "message": "Failed to search for companies"}

    async def _qualify_leads(self, params: Dict[str, Any]) -> Dict[str, Any]:
        try:
            company_ids = params.get("company_ids") or []
            criteria = params.get("criteria") or {}

            qualified: List[Dict[str, Any]] = []
            for company in self.companies_db:
                if company_ids and company.get("id") not in company_ids:
                    continue

                if self._evaluate_company(company, criteria):
                    lead = {
                        **company,
                        "qualified_date": datetime.utcnow().isoformat(),
                        "qualification_score": self._calculate_score(company),
                        "shipping_needs": self._estimate_shipping_needs(company),
                        "contact_strategy": self._determine_contact_strategy(company),
                    }
                    qualified.append(lead)
                    if lead not in self.leads_db:
                        self.leads_db.append(lead)

            return {
                "status": "success",
                "action": "qualify",
                "results": {"total_qualified": len(qualified), "qualified_leads": qualified, "criteria": criteria},
                "message": f"Qualified {len(qualified)} leads",
            }
        except Exception as e:
            return {"status": "error", "action": "qualify", "error": str(e), "message": "Failed to qualify leads"}

    async def _send_outreach(self, params: Dict[str, Any]) -> Dict[str, Any]:
        try:
            lead_ids = params.get("lead_ids") or []
            template_type = params.get("template", "initial_contact")
            schedule_delay = int(params.get("schedule_delay", 0))

            template = self.email_templates.get(template_type)
            if not template:
                return {"status": "error", "action": "outreach", "message": f"Template not found: {template_type}"}

            sent, failed = [], []
            for lead in self.leads_db:
                if lead_ids and lead.get("id") not in lead_ids:
                    continue
                try:
                    email_content = self._build_email_content(template, lead)
                    sent.append(
                        {
                            "lead_id": lead.get("id"),
                            "company_name": lead.get("name"),
                            "email": email_content["to"],
                            "subject": email_content["subject"],
                            "sent_at": datetime.utcnow().isoformat(),
                            "scheduled_for": (datetime.utcnow() + timedelta(days=schedule_delay)).isoformat()
                            if schedule_delay > 0
                            else None,
                            "template_used": template_type,
                            "status": "sent",
                        }
                    )
                    lead["last_contact"] = datetime.utcnow().isoformat()
                    lead["contact_count"] = int(lead.get("contact_count", 0)) + 1
                    lead["last_template"] = template_type
                except Exception as e:
                    failed.append(
                        {"lead_id": lead.get("id"), "company_name": lead.get("name"), "error": str(e), "status": "failed"}
                    )

            return {
                "status": "success",
                "action": "outreach",
                "results": {
                    "total_sent": len(sent),
                    "total_failed": len(failed),
                    "sent_emails": sent,
                    "failed_emails": failed,
                    "template_used": template_type,
                    "schedule_delay": schedule_delay,
                },
                "message": f"Sent {len(sent)} emails ({len(failed)} failed)",
            }
        except Exception as e:
            return {"status": "error", "action": "outreach", "error": str(e), "message": "Failed to send outreach"}

    async def _generate_report(self, params: Dict[str, Any]) -> Dict[str, Any]:
        try:
            period_days = int(params.get("period_days", 7))

            stats = {
                "companies_searched": len(self.companies_db),
                "leads_qualified": len(self.leads_db),
                "emails_sent": sum(1 for l in self.leads_db if int(l.get("contact_count", 0)) > 0),
                "responses_received": sum(1 for l in self.leads_db if l.get("response_received")),
                "positive_responses": sum(1 for l in self.leads_db if l.get("response_type") == "positive"),
                "hot_leads": [l for l in self.leads_db if int(l.get("qualification_score", 0)) > 80],
            }

            by_industry: Dict[str, int] = {}
            by_province: Dict[str, int] = {}
            for lead in self.leads_db:
                by_industry[lead.get("industry", "Unknown")] = by_industry.get(lead.get("industry", "Unknown"), 0) + 1
                by_province[lead.get("province", "Unknown")] = by_province.get(lead.get("province", "Unknown"), 0) + 1

            recommendations: List[str] = []
            if stats["positive_responses"] < 3:
                recommendations.append("Increase outreach frequency for high-scoring leads")
            if len(stats["hot_leads"]) > 5:
                recommendations.append("Consider phone follow-up for hot leads")
            if not by_industry:
                recommendations.append("Expand search to more industries")

            report = {
                "period": f"Last {period_days} days",
                "generated_at": datetime.utcnow().isoformat(),
                "summary": stats,
                "analysis": {
                    "by_industry": by_industry,
                    "by_province": by_province,
                    "success_rate": (stats["positive_responses"] / stats["emails_sent"] * 100)
                    if stats["emails_sent"] > 0
                    else 0.0,
                },
                "top_leads": stats["hot_leads"][:5],
                "recommendations": recommendations,
                "next_steps": [
                    "Continue weekly search for new companies",
                    "Follow up with non-responders after 5 days",
                    "Pass qualified hot leads to freight broker",
                ],
            }

            return {"status": "success", "action": "report", "report": report, "message": "Weekly report generated"}
        except Exception as e:
            return {"status": "error", "action": "report", "error": str(e), "message": "Failed to generate report"}

    async def _send_test_email(self, params: Dict[str, Any]) -> Dict[str, Any]:
        test_email = params.get("test_email", "test@example.com")
        template_type = params.get("template", "initial_contact")

        template = self.email_templates.get(template_type)
        if not template:
            return {"status": "error", "action": "test_email", "message": f"Template not found: {template_type}"}

        test_company = {"name": "Test Company Inc.", "industry": "Manufacturing", "province": "ON", "city": "Toronto", "email": test_email}
        email_content = self._build_email_content(template, test_company)

        return {
            "status": "success",
            "action": "test_email",
            "results": {
                "to": email_content["to"],
                "from": self.email_from,
                "subject": email_content["subject"],
                "body_preview": (email_content["body"][:200] + "...") if len(email_content["body"]) > 200 else email_content["body"],
                "template_used": template_type,
                "is_test": True,
            },
            "message": "Test email prepared (simulation)",
        }

    async def status(self) -> Dict[str, Any]:
        return {
            "name": "MapleLoad AI",
            "status": "active",
            "version": "1.0",
            "statistics": {
                "companies_in_db": len(self.companies_db),
                "qualified_leads": len(self.leads_db),
                "last_report": datetime.utcnow().isoformat(),
            },
        }

    async def config(self) -> Dict[str, Any]:
        return {
            "name": "MapleLoad AI",
            "description": "Canadian Freight Sourcing & Outreach Agent",
            "email_settings": {
                "from_address": self.email_from,
                "contact_name": self.contact_name,
                "company_name": self.company_name,
                "templates_available": list(self.email_templates.keys()),
            },
            "search_parameters": {
                "target_industries": self.target_industries,
                "canadian_provinces": self.canadian_provinces,
                "search_providers": self.search_providers,
            },
        }

    # ---------------- helpers ----------------

    def _generate_mock_companies(self, count: int, industry: str = None, province: str = None, city: str = None) -> List[Dict[str, Any]]:
        import random

        cities_by_province = {
            "ON": ["Toronto", "Ottawa", "Mississauga", "Hamilton", "London"],
            "QC": ["Montreal", "Quebec City", "Laval", "Gatineau", "Longueuil"],
            "BC": ["Vancouver", "Surrey", "Burnaby", "Richmond", "Kelowna"],
            "AB": ["Calgary", "Edmonton", "Red Deer", "Lethbridge", "Medicine Hat"],
        }

        industries = self.target_industries
        provinces = self.canadian_provinces[:4]

        companies: List[Dict[str, Any]] = []
        base_idx = len(self.companies_db)

        for i in range(count):
            comp_industry = industry or random.choice(industries)
            comp_province = province or random.choice(provinces)
            comp_city = city or random.choice(cities_by_province.get(comp_province, ["Unknown"]))

            companies.append(
                {
                    "id": f"comp_{base_idx + i + 1}",
                    "name": f"{comp_industry} {random.choice(['Inc.', 'Ltd.', 'Corp.', 'Group'])}",
                    "industry": comp_industry,
                    "province": comp_province,
                    "city": comp_city,
                    "email": f"info@{comp_industry.lower()}{i+1}.ca",
                    "employee_count": random.choice([10, 50, 100, 500, 1000]),
                    "estimated_shipping_volume": random.choice(["Low", "Medium", "High"]),
                    "found_via": random.choice(self.search_providers),
                    "discovery_date": datetime.utcnow().isoformat(),
                }
            )

        return companies

    def _evaluate_company(self, company: Dict[str, Any], criteria: Dict[str, Any]) -> bool:
        # Criteria reserved for future rules; current logic is fixed.
        score = self._calculate_score(company)
        return score >= 60

    def _calculate_score(self, company: Dict[str, Any]) -> int:
        score = 0

        emp_count = int(company.get("employee_count", 0))
        if emp_count >= 100:
            score += 30
        elif emp_count >= 50:
            score += 20
        elif emp_count >= 10:
            score += 10

        industry = company.get("industry", "")
        if industry in ["Manufacturing", "Distribution", "Wholesale"]:
            score += 40
        elif industry in ["Food", "Retail"]:
            score += 30
        else:
            score += 10

        province = company.get("province", "")
        if province in ["ON", "QC", "BC", "AB"]:
            score += 20

        shipping_volume = company.get("estimated_shipping_volume", "Low")
        if shipping_volume == "High":
            score += 10
        elif shipping_volume == "Medium":
            score += 5

        return min(score, 100)

    def _estimate_shipping_needs(self, company: Dict[str, Any]) -> Dict[str, Any]:
        industry = company.get("industry", "")
        emp_count = int(company.get("employee_count", 0))

        needs: Dict[str, Any] = {
            "likely_need": True,
            "estimated_frequency": "Weekly" if emp_count >= 100 else "Monthly",
            "load_types": [],
        }

        if industry == "Manufacturing":
            needs["load_types"] = ["FTL", "LTL", "Reefer"]
        elif industry == "Food":
            needs["load_types"] = ["Reefer", "LTL"]
        elif industry == "Distribution":
            needs["load_types"] = ["FTL", "LTL"]
        else:
            needs["load_types"] = ["LTL", "Dry Van"]

        return needs

    def _determine_contact_strategy(self, company: Dict[str, Any]) -> Dict[str, Any]:
        score = self._calculate_score(company)

        if score >= 80:
            return {"priority": "High", "contact_method": ["Email", "Phone follow-up"], "follow_up_days": 3, "template": "initial_contact"}
        if score >= 60:
            return {"priority": "Medium", "contact_method": ["Email"], "follow_up_days": 5, "template": "initial_contact"}
        return {"priority": "Low", "contact_method": ["Email"], "follow_up_days": 7, "template": "initial_contact"}

    def _build_email_content(self, template: Dict[str, str], company: Dict[str, Any]) -> Dict[str, Any]:
        contact_person = company.get("contact_person") or "Team"

        body = template["body"].format(
            company_name=company.get("name", "Company"),
            contact_name=self.contact_name,
            email_from=self.email_from,
            contact_person=contact_person,
        )

        return {
            "subject": template["subject"],
            "body": body,
            "to": company.get("email", "info@company.com"),
            "from": self.email_from,
            "reply_to": self.email_from,
        }


# Keep backward-compatible import name
MapleLoadBot = MapleLoadAIBot
