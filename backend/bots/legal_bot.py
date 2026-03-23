"""
Legal Consultant Bot
Legal research, contract review, compliance checks, and transport liability guidance.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import copy
import re


class LegalBot:
    """Shared-runtime legal consultant with transport-focused legal knowledge."""

    def __init__(self) -> None:
        self.name = "legal_bot"
        self.display_name = "AI Legal Consultant"
        self.description = "Legal research, contract analysis, compliance checks, and liability guidance"
        self.version = "2.0.0"
        self.mode = "governance"
        self.is_active = True

        self.laws: Dict[str, Dict[str, Any]] = {
            "hamburg_rules_1978": {
                "id": "hamburg_rules_1978",
                "name": "Hamburg Rules 1978",
                "category": "international",
                "region": "International",
                "transport_mode": "maritime",
                "summary": "UN framework for carrier liability in maritime cargo carriage.",
                "applicable_in": "International",
                "topics": ["liability", "cargo", "maritime"],
                "liability_limit": {"per_package": "835 SDR", "per_kg": "2.5 SDR/kg"},
                "key_points": [
                    "Carrier remains liable unless it proves reasonable avoidance measures.",
                    "Liability is capped per package or per kilogram, whichever is higher.",
                ],
            },
            "cmr_convention_1956": {
                "id": "cmr_convention_1956",
                "name": "CMR Convention 1956",
                "category": "international",
                "region": "Europe",
                "transport_mode": "road",
                "summary": "Core legal convention for cross-border road carriage of goods.",
                "applicable_in": "Europe and other contracting states",
                "topics": ["liability", "road", "documents"],
                "liability_limit": {"per_kg": "8.33 SDR/kg"},
                "key_points": [
                    "Carrier is liable for loss, damage, and delay during carriage.",
                    "The CMR waybill formalizes the transport relationship.",
                ],
            },
            "montreal_convention_1999": {
                "id": "montreal_convention_1999",
                "name": "Montreal Convention 1999",
                "category": "international",
                "region": "International",
                "transport_mode": "air",
                "summary": "Unified framework for international air-carriage liability.",
                "applicable_in": "International",
                "topics": ["liability", "air", "cargo"],
                "liability_limit": {"per_kg": "19 SDR/kg"},
                "key_points": [
                    "Applies to damage occurring during air carriage.",
                    "Special drawing rights are used as the unit of account.",
                ],
            },
            "saudi_transport_law": {
                "id": "saudi_transport_law",
                "name": "Saudi Public Transport Law",
                "category": "regional",
                "region": "Saudi Arabia",
                "transport_mode": "road",
                "summary": "Regulates land transport licensing, carrier obligations, and enforcement.",
                "applicable_in": "Saudi Arabia",
                "topics": ["compliance", "road", "licensing"],
                "liability_limit": {"general": "Cargo value subject to statutory and contractual rules"},
                "key_points": [
                    "Carrier remains responsible for cargo from receipt to delivery unless exempted by force majeure or shipper fault.",
                    "Licensing and operating cards are mandatory for lawful transport activity.",
                ],
            },
            "canada_transport_act": {
                "id": "canada_transport_act",
                "name": "Canada Transportation Act",
                "category": "regional",
                "region": "Canada",
                "transport_mode": "multimodal",
                "summary": "Federal legal framework covering regulated transportation activities in Canada.",
                "applicable_in": "Canada",
                "topics": ["compliance", "carrier", "transport"],
                "liability_limit": {"general": "Carrier and modal rules apply based on service and province"},
                "key_points": [
                    "Transport compliance interacts with federal and provincial carrier regimes.",
                    "Insurance, safety fitness, and customs interfaces are critical for operators.",
                ],
            },
            "cargo_insurance_clauses": {
                "id": "cargo_insurance_clauses",
                "name": "Institute Cargo Clauses",
                "category": "topic",
                "region": "International",
                "transport_mode": "multimodal",
                "summary": "Insurance framework for cargo risks, exclusions, and all-risk coverage structures.",
                "applicable_in": "International",
                "topics": ["insurance", "cargo", "claims"],
                "key_points": [
                    "Clause A is broadest, while Clause C is the narrowest base cover.",
                    "War and strikes risks are usually handled under separate clauses.",
                ],
            },
            "kyoto_convention": {
                "id": "kyoto_convention",
                "name": "Revised Kyoto Convention",
                "category": "topic",
                "region": "International",
                "transport_mode": "customs",
                "summary": "Framework for simplified and harmonized customs procedures.",
                "applicable_in": "International",
                "topics": ["customs", "documents", "compliance"],
                "key_points": [
                    "Promotes transparency and simplified customs processing.",
                    "Supports pre-arrival processing and harmonized declarations.",
                ],
            },
        }
        self.region_aliases = {
            "saudi": "Saudi Arabia",
            "saudi arabia": "Saudi Arabia",
            "ksa": "Saudi Arabia",
            "canada": "Canada",
            "europe": "Europe",
            "eu": "Europe",
            "international": "International",
            "uae": "UAE",
            "emirates": "UAE",
        }
        self.topic_aliases = {
            "liability": "liability",
            "contracts": "contracts",
            "contract": "contracts",
            "insurance": "insurance",
            "customs": "customs",
            "documents": "documents",
            "compliance": "compliance",
            "cargo": "cargo",
        }
        self.country_requirements: Dict[str, Dict[str, List[str]]] = {
            "Saudi Arabia": {
                "licenses": ["Carrier license", "Driver license", "Operating card"],
                "documents": ["Commercial invoice", "Waybill", "Certificate of origin"],
                "insurance": ["Vehicle liability insurance", "Cargo insurance"],
                "restrictions": ["Restricted goods controls", "Weight controls"],
            },
            "UAE": {
                "licenses": ["Transport permit", "Driver card"],
                "documents": ["Commercial invoice", "Waybill", "Certificate of origin"],
                "insurance": ["Vehicle liability insurance", "Cargo insurance"],
                "restrictions": ["Weight controls", "Restricted goods controls"],
            },
            "Canada": {
                "licenses": ["Safety fitness certificate", "Operating authority"],
                "documents": ["Bill of lading", "Customs invoice"],
                "insurance": ["Liability insurance", "Cargo insurance"],
                "restrictions": ["Hours of service", "Weight limits"],
            },
            "Germany": {
                "licenses": ["EU license", "Driver card"],
                "documents": ["CMR waybill", "Customs declaration"],
                "insurance": ["Motor liability insurance"],
                "restrictions": ["Driving time rules", "Weight limits"],
            },
        }
        self.standard_clauses = {
            "partnership": [
                {"title": "Parties", "importance": "high", "keywords": ["party", "parties"]},
                {"title": "Scope", "importance": "high", "keywords": ["scope", "purpose"]},
                {"title": "Profit distribution", "importance": "high", "keywords": ["profit", "distribution"]},
                {"title": "Term and termination", "importance": "high", "keywords": ["term", "termination"]},
                {"title": "Dispute resolution", "importance": "medium", "keywords": ["dispute", "arbitration"]},
            ],
            "carriage": [
                {"title": "Cargo description", "importance": "high", "keywords": ["cargo", "goods"]},
                {"title": "Route and delivery", "importance": "high", "keywords": ["delivery", "route"]},
                {"title": "Carrier liability", "importance": "high", "keywords": ["liability"]},
                {"title": "Freight charges", "importance": "high", "keywords": ["freight", "payment"]},
                {"title": "Governing law", "importance": "medium", "keywords": ["law", "governing law"]},
            ],
        }
        self.risk_patterns = [
            {"pattern": r"unlimited liability", "risk": "Unlimited liability exposure", "severity": "high"},
            {"pattern": r"waive(?:s|d)? .*claim", "risk": "Waiver of core claim rights", "severity": "high"},
            {"pattern": r"perpetual term|indefinite term", "risk": "Indefinite contract term", "severity": "medium"},
            {"pattern": r"foreign arbitration", "risk": "Potentially unfavorable arbitration seat", "severity": "medium"},
            {"pattern": r"governing law[: ]+unknown", "risk": "Unclear governing law", "severity": "high"},
        ]
        self.recent_searches: List[Dict[str, Any]] = []
        self.contract_reviews: List[Dict[str, Any]] = []

    async def run(self, payload: dict) -> dict:
        """Main shared-runtime entrypoint."""
        context = payload.get("context", {}) or {}
        action = payload.get("action") or context.get("action") or payload.get("meta", {}).get("action") or "status"

        if action == "status":
            return await self.status()
        if action == "config":
            return await self.config()
        if action == "dashboard":
            return await self.get_dashboard()
        if action == "search_laws":
            query = str(context.get("query") or payload.get("query") or "")
            filters = context.get("filters") or payload.get("filters") or {}
            return await self.search_laws(query, filters)
        if action == "get_law":
            law_id = str(context.get("law_id") or payload.get("law_id") or "")
            return await self.get_law(law_id)
        if action == "laws_by_region":
            region = str(context.get("region") or payload.get("region") or "")
            return await self.get_laws_by_region(region)
        if action == "laws_by_topic":
            topic = str(context.get("topic") or payload.get("topic") or "")
            return await self.get_laws_by_topic(topic)
        if action == "analyze_contract":
            contract_text = str(context.get("contract_text") or payload.get("contract_text") or "")
            metadata = context.get("metadata") or payload.get("metadata") or {}
            return await self.analyze_contract(contract_text, metadata)
        if action == "compare_contract":
            contract_text = str(context.get("contract_text") or payload.get("contract_text") or "")
            contract_type = str(context.get("contract_type") or payload.get("contract_type") or "carriage")
            return await self.compare_with_standard(contract_text, contract_type)
        if action == "draft_contract":
            contract_type = str(context.get("contract_type") or payload.get("contract_type") or "generic")
            parties = context.get("parties") or payload.get("parties") or {}
            terms = context.get("terms") or payload.get("terms") or {}
            return await self.draft_contract(contract_type, parties, terms)
        if action == "check_shipment_compliance":
            origin = str(context.get("origin") or payload.get("origin") or "")
            destination = str(context.get("destination") or payload.get("destination") or "")
            shipment_data = context.get("shipment_data") or payload.get("shipment_data") or {}
            return await self.check_shipment_compliance(origin, destination, shipment_data)
        if action == "check_company_compliance":
            country = str(context.get("country") or payload.get("country") or "")
            company_data = context.get("company_data") or payload.get("company_data") or {}
            return await self.check_company_compliance(country, company_data)
        if action == "check_driver_compliance":
            country = str(context.get("country") or payload.get("country") or "")
            driver_data = context.get("driver_data") or payload.get("driver_data") or {}
            return await self.check_driver_compliance(driver_data, country)
        if action == "calculate_liability":
            law = str(context.get("law") or payload.get("law") or "cmr_convention_1956")
            weight = float(context.get("weight") or payload.get("weight") or 0)
            value = float(context.get("value") or payload.get("value") or 0)
            damage_type = str(context.get("damage_type") or payload.get("damage_type") or "damage")
            return await self.calculate_liability(law, weight, value, damage_type)
        if action == "compare_liability_limits":
            countries = context.get("countries") or payload.get("countries") or []
            return await self.compare_liability_limits(countries)
        if action == "required_documents":
            origin = str(context.get("origin") or payload.get("origin") or "")
            destination = str(context.get("destination") or payload.get("destination") or "")
            goods_type = str(context.get("goods_type") or payload.get("goods_type") or "general")
            return await self.get_required_documents(origin, destination, goods_type)
        return {"ok": False, "error": f"Unknown action: {action}"}

    async def process_message(self, message: str, context: Optional[dict] = None) -> dict:
        """Handle legal natural-language requests."""
        context = context or {}
        if context.get("action"):
            return await self.run({"context": context})

        message_lower = (message or "").lower()
        if "contract" in message_lower and "draft" in message_lower:
            return await self.draft_contract("carriage", {}, {})
        if "contract" in message_lower or "review" in message_lower:
            return await self.analyze_contract(message, {})
        if "law" in message_lower or "cmr" in message_lower or "montreal" in message_lower:
            return await self.search_laws(message, {})
        if "compliance" in message_lower:
            return await self.check_company_compliance("Saudi Arabia", {"name": "GTS Logistics"})
        if "liability" in message_lower:
            return await self.calculate_liability("cmr_convention_1956", 1000, 15000, "damage")
        if "document" in message_lower:
            return await self.get_required_documents("Canada", "Saudi Arabia", "electronics")
        return await self.status()

    async def status(self) -> dict:
        return {
            "ok": True,
            "bot": self.name,
            "display_name": self.display_name,
            "version": self.version,
            "mode": self.mode,
            "is_active": self.is_active,
            "law_count": len(self.laws),
            "regions_covered": len({law["region"] for law in self.laws.values()}),
            "topics_covered": len({topic for law in self.laws.values() for topic in law.get("topics", [])}),
            "message": "Legal research and compliance engine is active",
        }

    async def config(self) -> dict:
        return {
            "name": self.name,
            "display_name": self.display_name,
            "description": self.description,
            "version": self.version,
            "mode": self.mode,
            "capabilities": [
                "dashboard",
                "search_laws",
                "get_law",
                "laws_by_region",
                "laws_by_topic",
                "analyze_contract",
                "compare_contract",
                "draft_contract",
                "check_shipment_compliance",
                "check_company_compliance",
                "check_driver_compliance",
                "calculate_liability",
                "compare_liability_limits",
                "required_documents",
            ],
        }

    async def get_dashboard(self) -> dict:
        return {
            "ok": True,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "stats": {
                "total_laws": len(self.laws),
                "regions_covered": len({law["region"] for law in self.laws.values()}),
                "topics_covered": len({topic for law in self.laws.values() for topic in law.get("topics", [])}),
                "contracts_reviewed": len(self.contract_reviews),
            },
            "common_queries": [
                "CMR liability limit",
                "Required customs documents for Saudi Arabia",
                "Canada transport compliance",
            ],
            "recent_searches": copy.deepcopy(self.recent_searches[:5]),
            "coverage": {
                "international": len([law for law in self.laws.values() if law["category"] == "international"]),
                "regional": len([law for law in self.laws.values() if law["category"] == "regional"]),
                "topics": len([law for law in self.laws.values() if law["category"] == "topic"]),
            },
        }

    async def search_laws(self, query: str, filters: Dict[str, Any]) -> dict:
        query_lower = query.lower().strip()
        results: List[Dict[str, Any]] = []
        for law in self.laws.values():
            haystacks = [
                law["name"].lower(),
                law["summary"].lower(),
                law.get("applicable_in", "").lower(),
                " ".join(law.get("topics", [])).lower(),
            ]
            if query_lower and not any(query_lower in item for item in haystacks):
                continue
            if filters:
                if filters.get("region") and law["region"] != filters["region"]:
                    continue
                if filters.get("transport_mode") and law["transport_mode"] != filters["transport_mode"]:
                    continue
                if filters.get("category") and law["category"] != filters["category"]:
                    continue
            results.append(
                {
                    "id": law["id"],
                    "name": law["name"],
                    "category": law["category"],
                    "summary": law["summary"],
                    "applicable_in": law["applicable_in"],
                    "relevance": 90,
                }
            )
        self._remember_search(query, filters)
        return {"ok": True, "query": query, "results": results[:20], "count": len(results[:20])}

    async def get_law(self, law_id: str) -> dict:
        law = self.laws.get(law_id)
        if not law:
            return {"ok": False, "error": f"Law '{law_id}' not found"}
        return {"ok": True, "law": copy.deepcopy(law)}

    async def get_laws_by_region(self, region: str) -> dict:
        normalized = self.region_aliases.get(region.lower(), region)
        laws = [
            {"id": law["id"], "name": law["name"], "region": law["region"], "summary": law["summary"]}
            for law in self.laws.values()
            if normalized.lower() in law["region"].lower() or normalized.lower() in law["applicable_in"].lower()
        ]
        return {"ok": True, "region": normalized, "laws": laws}

    async def get_laws_by_topic(self, topic: str) -> dict:
        normalized = self.topic_aliases.get(topic.lower(), topic.lower())
        laws = [
            {"id": law["id"], "name": law["name"], "topic": normalized, "summary": law["summary"]}
            for law in self.laws.values()
            if normalized in law.get("topics", [])
        ]
        return {"ok": True, "topic": normalized, "laws": laws}

    async def analyze_contract(self, contract_text: str, metadata: Dict[str, Any]) -> dict:
        text = contract_text or ""
        risks = []
        for rule in self.risk_patterns:
            if re.search(rule["pattern"], text, re.IGNORECASE):
                risks.append({"risk": rule["risk"], "severity": rule["severity"], "pattern": rule["pattern"]})

        governing_law = self._extract_governing_law(text)
        compliance_issues = []
        for required in ["liability", "force majeure", "term", "termination"]:
            if required not in text.lower():
                compliance_issues.append(f"Missing core clause: {required}")

        clauses_summary = {
            "parties": self._extract_parties(text),
            "subject": self._extract_subject(text),
            "duration": self._extract_duration(text),
            "price": self._extract_price(text),
            "governing_law": governing_law,
            "dispute_resolution": self._extract_dispute_resolution(text),
        }
        result = {
            "ok": True,
            "analysis_date": datetime.now(timezone.utc).isoformat(),
            "clauses_summary": clauses_summary,
            "risks": risks,
            "compliance": {
                "is_compliant": not compliance_issues,
                "issues": compliance_issues,
            },
            "suggestions": self._generate_contract_suggestions(risks, compliance_issues),
            "risk_level": self._calculate_risk_level(risks),
        }
        self.contract_reviews.insert(
            0,
            {
                "review_id": f"REV-{len(self.contract_reviews) + 101}",
                "reviewed_at": datetime.now(timezone.utc).isoformat(),
                "risk_level": result["risk_level"],
                "governing_law": governing_law,
            },
        )
        return result

    async def compare_with_standard(self, contract_text: str, contract_type: str) -> dict:
        standards = self.standard_clauses.get(contract_type, self.standard_clauses["carriage"])
        missing = []
        text_lower = (contract_text or "").lower()
        for clause in standards:
            if not any(keyword in text_lower for keyword in clause["keywords"]):
                missing.append(
                    {
                        "clause": clause["title"],
                        "importance": clause["importance"],
                        "recommendation": f"Add clause: {clause['title']}",
                    }
                )
        completeness = round(100 - (len(missing) / max(1, len(standards)) * 100), 2)
        return {
            "ok": True,
            "contract_type": contract_type,
            "missing_clauses": missing,
            "completeness_percentage": completeness,
            "recommendations": [item["recommendation"] for item in missing[:5]],
        }

    async def draft_contract(self, contract_type: str, parties: Dict[str, Any], terms: Dict[str, Any]) -> dict:
        if contract_type == "partnership":
            content = self._draft_partnership_contract(parties, terms)
        elif contract_type == "carriage":
            content = self._draft_carriage_contract(parties, terms)
        else:
            content = self._draft_generic_contract(parties, terms)
        return {
            "ok": True,
            "contract_type": contract_type,
            "content": content,
            "parties": parties,
            "terms": terms,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    async def check_shipment_compliance(self, origin: str, destination: str, shipment_data: Dict[str, Any]) -> dict:
        issues: List[str] = []
        warnings: List[str] = []
        for country in [origin, destination]:
            req = self.country_requirements.get(country)
            if not req:
                continue
            docs = shipment_data.get("documents", [])
            for document in req["documents"]:
                if document not in docs:
                    warnings.append(f"Missing document for {country}: {document}")

        if origin != destination:
            customs_docs = ["Commercial invoice", "Waybill"]
            for document in customs_docs:
                if document not in shipment_data.get("documents", []):
                    issues.append(f"Missing customs document: {document}")

        weight = float(shipment_data.get("weight", 0) or 0)
        if destination in {"Saudi Arabia", "UAE", "Germany"} and weight > 40000:
            issues.append(f"Weight {weight:.0f} kg exceeds common road limit in {destination}")

        status = "compliant"
        message = "Shipment is compliant"
        if issues:
            status = "non_compliant"
            message = "Shipment is not compliant and requires corrective action"
        elif warnings:
            status = "warning"
            message = "Shipment is compliant with warnings"
        return {
            "ok": True,
            "origin": origin,
            "destination": destination,
            "status": status,
            "message": message,
            "issues": issues,
            "warnings": warnings,
            "recommendations": [f"Resolve: {item}" for item in issues + warnings][:8],
        }

    async def check_company_compliance(self, country: str, company_data: Dict[str, Any]) -> dict:
        requirements = self.country_requirements.get(country, {"licenses": [], "documents": [], "insurance": [], "restrictions": []})
        details = {}
        total = 0
        compliant = 0
        for category, items in requirements.items():
            category_items = []
            provided = company_data.get(category, []) or company_data.get(category.rstrip("s"), [])
            for item in items:
                total += 1
                status = "compliant" if item in provided else "missing"
                if status == "compliant":
                    compliant += 1
                category_items.append({"requirement": item, "status": status})
            details[category] = {"items": category_items}
        percentage = round((compliant / total * 100), 2) if total else 0.0
        missing = [item["requirement"] for category in details.values() for item in category["items"] if item["status"] == "missing"]
        return {
            "ok": True,
            "country": country,
            "company": company_data.get("name"),
            "compliance_percentage": percentage,
            "status": "excellent" if percentage >= 90 else "good" if percentage >= 70 else "attention_needed",
            "details": details,
            "missing_requirements": missing,
        }

    async def check_driver_compliance(self, driver_data: Dict[str, Any], country: str) -> dict:
        issues = []
        license_info = driver_data.get("license", {})
        if not license_info:
            issues.append("Missing driver license information")
        elif license_info.get("expiry") and license_info["expiry"] < datetime.now(timezone.utc).date().isoformat():
            issues.append("Driver license is expired")

        max_hours = {"Saudi Arabia": 8, "UAE": 8, "Canada": 13, "Germany": 9}.get(country, 8)
        if float(driver_data.get("hours_worked", 0) or 0) > max_hours:
            issues.append("Driver exceeds maximum daily working hours")

        if country == "Germany" and driver_data.get("cargo_type") == "hazardous" and not driver_data.get("adr_certificate"):
            issues.append("ADR certificate is required for hazardous cargo")

        return {
            "ok": True,
            "driver_id": driver_data.get("id"),
            "country": country,
            "is_compliant": not issues,
            "issues": issues,
            "recommendations": [f"Correct: {issue}" for issue in issues],
        }

    async def calculate_liability(self, law: str, weight: float, value: float, damage_type: str) -> dict:
        limits = {
            "hague_rules_1924": {"per_package": 100, "unit": "GBP"},
            "hamburg_rules_1978": {"per_kg": 2.5, "per_package": 835, "unit": "SDR"},
            "cmr_convention_1956": {"per_kg": 8.33, "unit": "SDR"},
            "montreal_convention_1999": {"per_kg": 19.0, "unit": "SDR"},
            "rotterdam_rules_2008": {"per_kg": 3.0, "per_package": 875, "unit": "SDR"},
        }
        config = limits.get(law, {"per_kg": 8.33, "unit": "SDR"})
        compensation = config.get("per_package", 0.0)
        if "per_kg" in config:
            compensation = max(compensation, weight * float(config["per_kg"]))
        max_compensation = min(compensation, value)
        return {
            "ok": True,
            "law_applied": law,
            "damage_type": damage_type,
            "calculation_method": "per_kg" if "per_kg" in config else "per_package",
            "compensation": round(compensation, 2),
            "max_compensation": round(max_compensation, 2),
            "unit": config["unit"],
            "value_limit_reached": max_compensation < value,
            "notes": "Indicative legal guidance only; local law and contract wording may change the result.",
        }

    async def compare_liability_limits(self, countries: List[str]) -> dict:
        mapping = {
            "Saudi Arabia": {
                "road_local": "Cargo value under local transport law and contract terms",
                "air_montreal": "19 SDR/kg",
                "sea": "Contractual or Hague/Hague-Visby practice",
            },
            "Canada": {
                "road_local": "Provincial and federal carrier rules apply",
                "air_montreal": "19 SDR/kg",
                "sea": "Modal rules and contract terms apply",
            },
            "Germany": {
                "road_cmr": "8.33 SDR/kg",
                "air_montreal": "19 SDR/kg",
                "sea": "Hague-Visby or Hamburg practice depending route and contract",
            },
            "UAE": {
                "road_local": "50 AED/kg under local approach",
                "air_montreal": "19 SDR/kg",
                "sea": "Contract and maritime rules apply",
            },
        }
        return {
            "ok": True,
            "comparison": {country: mapping.get(country, {"general": "Check local law and contract"}) for country in countries},
        }

    async def get_required_documents(self, origin: str, destination: str, goods_type: str) -> dict:
        documents = [
            {"name": "Commercial invoice", "required": True, "copies": 3},
            {"name": "Waybill", "required": True, "type": self._shipping_document_type(origin, destination)},
        ]
        if destination in {"Saudi Arabia", "UAE", "Egypt"}:
            documents.append({"name": "Certificate of origin", "required": True, "certified": True})
        if goods_type in {"food", "agricultural"}:
            documents.append({"name": "Health certificate", "required": True})
        if goods_type == "electronics":
            documents.append({"name": "Conformity certificate", "required": "depends_on_destination"})
        return {"ok": True, "origin": origin, "destination": destination, "goods_type": goods_type, "documents": documents}

    def _remember_search(self, query: str, filters: Dict[str, Any]) -> None:
        self.recent_searches.insert(
            0,
            {
                "query": query,
                "filters": filters,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        )

    def _extract_parties(self, text: str) -> Dict[str, str]:
        parties = {}
        first = re.search(r"first party[: ]+([^\n]+)", text, re.IGNORECASE)
        second = re.search(r"second party[: ]+([^\n]+)", text, re.IGNORECASE)
        if first:
            parties["first_party"] = first.group(1).strip()
        if second:
            parties["second_party"] = second.group(1).strip()
        return parties

    def _extract_subject(self, text: str) -> str:
        match = re.search(r"subject[: ]+([^\n]+)", text, re.IGNORECASE)
        return match.group(1).strip() if match else "Not clearly specified"

    def _extract_duration(self, text: str) -> Dict[str, Any]:
        duration = {}
        match = re.search(r"(\d+)\s+(day|days|month|months|year|years)", text, re.IGNORECASE)
        if match:
            duration["period"] = f"{match.group(1)} {match.group(2)}"
        if "indefinite" in text.lower():
            duration["period"] = "indefinite"
        return duration

    def _extract_price(self, text: str) -> float:
        match = re.search(r"(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(sar|usd|eur|cad|aed|riyal|dollar|euro)", text, re.IGNORECASE)
        return float(match.group(1).replace(",", "")) if match else 0.0

    def _extract_governing_law(self, text: str) -> str:
        match = re.search(r"governing law[: ]+([^\n]+)", text, re.IGNORECASE)
        return match.group(1).strip() if match else "Not specified"

    def _extract_dispute_resolution(self, text: str) -> str:
        text_lower = text.lower()
        if "arbitration" in text_lower:
            return "arbitration"
        if "court" in text_lower or "litigation" in text_lower:
            return "litigation"
        return "not specified"

    def _generate_contract_suggestions(self, risks: List[Dict[str, Any]], compliance_issues: List[str]) -> List[str]:
        suggestions = []
        for risk in risks:
            if risk["severity"] == "high":
                suggestions.append(f"Revise immediately: {risk['risk']}")
        for issue in compliance_issues:
            suggestions.append(issue)
        if not suggestions:
            suggestions.append("Contract structure is generally sound; complete a jurisdiction-specific legal review.")
        return suggestions

    def _calculate_risk_level(self, risks: List[Dict[str, Any]]) -> str:
        high = len([risk for risk in risks if risk["severity"] == "high"])
        medium = len([risk for risk in risks if risk["severity"] == "medium"])
        if high:
            return "high"
        if medium > 1:
            return "medium"
        return "low"

    def _shipping_document_type(self, origin: str, destination: str) -> str:
        if any(item in destination for item in ["Germany", "France", "Europe"]):
            return "CMR waybill"
        if any(item in origin for item in ["Canada"]) and any(item in destination for item in ["Saudi Arabia", "UAE"]):
            return "Ocean or multimodal bill of lading"
        return "Commercial transport waybill"

    def _draft_partnership_contract(self, parties: Dict[str, Any], terms: Dict[str, Any]) -> str:
        return (
            f"Partnership Agreement\n\n"
            f"First party: {parties.get('first_party', 'TBD')}\n"
            f"Second party: {parties.get('second_party', 'TBD')}\n\n"
            f"Subject: {terms.get('subject', 'Logistics and transport cooperation')}\n"
            f"Term: {terms.get('duration', '12 months')}\n"
            f"Profit distribution: {terms.get('profit_distribution', 'As agreed by the parties')}\n"
            f"Dispute resolution: {terms.get('dispute_resolution', 'Arbitration before a mutually agreed seat')}\n"
            f"Governing law: {terms.get('governing_law', 'To be specified')}\n"
        )

    def _draft_carriage_contract(self, parties: Dict[str, Any], terms: Dict[str, Any]) -> str:
        return (
            f"Carriage Agreement\n\n"
            f"Carrier: {parties.get('carrier', 'TBD')}\n"
            f"Shipper: {parties.get('shipper', 'TBD')}\n\n"
            f"Cargo: {terms.get('cargo_description', 'General cargo')}\n"
            f"Route: {terms.get('route', 'To be defined')}\n"
            f"Freight: {terms.get('freight_rate', 'To be defined')}\n"
            f"Liability standard: {terms.get('liability_standard', 'Applicable transport convention and local law')}\n"
            f"Payment terms: {terms.get('payment_terms', 'Net 30')}\n"
            f"Governing law: {terms.get('governing_law', 'To be specified')}\n"
        )

    def _draft_generic_contract(self, parties: Dict[str, Any], terms: Dict[str, Any]) -> str:
        return (
            f"Service Agreement\n\n"
            f"Parties: {parties or {'party_one': 'TBD', 'party_two': 'TBD'}}\n"
            f"Scope: {terms.get('subject', 'Services to be defined')}\n"
            f"Term: {terms.get('duration', 'To be defined')}\n"
            f"Governing law: {terms.get('governing_law', 'To be specified')}\n"
        )
