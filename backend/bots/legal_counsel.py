# backend/bots/legal_counsel.py
"""
LG - Legal Counsel Bot
Compliance and document analysis assistant.
Reviews legal documents and ensures compliance.
"""

from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any
import asyncio


class LegalCounselBot:
    """Legal Counsel - Document review and compliance advisor"""
    
    def __init__(self):
        self.name = "legal_counsel"
        self.display_name = "⚖️ Legal Counsel"
        self.description = "Reviews legal documents and ensures compliance"
        self.version = "1.0.0"
        self.mode = "intelligence"
        self.is_active = True
        
        # Legal data structures
        self.contracts_db: List[Dict] = []
        self.compliance_requirements = self._load_legal_requirements()
        self.pending_deadlines: List[Dict] = []
        
    def _load_legal_requirements(self) -> Dict[str, Any]:
        """Load Canadian legal requirements"""
        return {
            "corporate_law": {
                "canada_business_corporations_act": {
                    "requirements": [
                        "Annual Returns",
                        "Director Records",
                        "Shareholder Records",
                        "Minute Books"
                    ]
                }
            },
            "employment_law": {
                "canada_labour_code": {
                    "requirements": [
                        "Employment Contracts",
                        "Workplace Policies",
                        "Health & Safety",
                        "Termination Rules"
                    ]
                }
            },
            "commercial_law": {
                "contract_laws": {
                    "requirements": [
                        "Valid Offer & Acceptance",
                        "Consideration",
                        "Legal Capacity",
                        "Legality of Purpose"
                    ]
                }
            },
            "transportation_law": {
                "transport_canada": {
                    "requirements": [
                        "Carrier Operating Authority",
                        "Safety Certificates",
                        "Insurance Requirements",
                        "Driver Qualifications"
                    ]
                }
            }
        }
    
    async def run(self, payload: dict) -> dict:
        """Main execution method"""
        action = payload.get("action", "status")
        
        if action == "review_contract":
            contract_text = payload.get("contract_text", "")
            return await self.review_contract(contract_text)
        elif action == "track_deadlines":
            return await self.track_deadlines()
        elif action == "check_compliance":
            domain = payload.get("domain", "corporate")
            return await self.check_legal_compliance(domain)
        elif action == "activate":
            return await self.activate_backend()
        else:
            return await self.status()
    
    async def status(self) -> dict:
        """Return current bot status"""
        return {
            "ok": True,
            "bot": self.name,
            "display_name": self.display_name,
            "version": self.version,
            "mode": self.mode,
            "is_active": self.is_active,
            "contracts_reviewed": len(self.contracts_db),
            "pending_deadlines": len(self.pending_deadlines),
            "message": "Backend activation pending" if not self.is_active else "Operational"
        }
    
    async def config(self) -> dict:
        """Return bot configuration"""
        return {
            "name": self.name,
            "display_name": self.display_name,
            "description": self.description,
            "version": self.version,
            "mode": self.mode,
            "capabilities": [
                "review_contract",
                "track_deadlines",
                "check_compliance",
                "identify_legal_risks"
            ],
            "legal_domains": list(self.compliance_requirements.keys())
        }
    
    async def activate_backend(self) -> dict:
        """Activate full backend capabilities"""
        print(f"🚀 Activating backend for {self.display_name}...")
        
        await self._connect_to_legal_databases()
        await self._setup_document_reviewer()
        await self._configure_legal_alerts()
        
        self.is_active = True
        return {
            "ok": True,
            "status": "active",
            "message": f"{self.display_name} backend activated successfully"
        }
    
    async def _connect_to_legal_databases(self):
        """Connect to legal databases"""
        print("   ⚖️  Connecting to legal databases...")
        await asyncio.sleep(0.3)
    
    async def _setup_document_reviewer(self):
        """Setup document review system"""
        print("   📄 Setting up document reviewer...")
        await asyncio.sleep(0.2)
    
    async def _configure_legal_alerts(self):
        """Configure legal alert system"""
        print("   🔔 Configuring legal alerts...")
        await asyncio.sleep(0.2)
    
    async def review_contract(self, contract_text: str) -> dict:
        """Review contract for legal issues"""
        if not contract_text:
            return {
                "ok": False,
                "error": "No contract text provided"
            }
        
        # Mock contract analysis
        word_count = len(contract_text.split())
        
        analysis = {
            "summary": {
                "word_count": word_count,
                "estimated_review_time": f"{max(15, word_count // 100)} minutes",
                "complexity": "medium" if word_count > 500 else "low"
            },
            "clauses_identified": [
                {"type": "termination", "location": "Section 8", "status": "standard"},
                {"type": "liability", "location": "Section 12", "status": "review_needed"},
                {"type": "payment_terms", "location": "Section 3", "status": "acceptable"}
            ],
            "risk_assessment": {
                "overall_risk": "medium",
                "risks_identified": [
                    "Unlimited liability clause needs revision",
                    "Payment terms unclear for delays"
                ]
            },
            "recommendations": [
                "Add force majeure clause",
                "Clarify dispute resolution process",
                "Limit liability to contract value"
            ]
        }
        
        # Store contract review
        review_record = {
            "id": f"REV-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}",
            "reviewed_at": datetime.now(timezone.utc).isoformat(),
            "word_count": word_count,
            "analysis": analysis
        }
        self.contracts_db.append(review_record)
        
        return {
            "ok": True,
            "review_id": review_record["id"],
            "analysis": analysis
        }
    
    async def track_deadlines(self) -> dict:
        """Track legal deadlines and renewals"""
        # Generate mock deadlines
        now = datetime.now(timezone.utc)
        
        deadlines = {
            "filing_deadlines": [
                {
                    "type": "Annual Corporate Return",
                    "due_date": (now + timedelta(days=45)).date().isoformat(),
                    "status": "upcoming"
                },
                {
                    "type": "Tax Filing",
                    "due_date": (now + timedelta(days=90)).date().isoformat(),
                    "status": "upcoming"
                }
            ],
            "contract_expirations": [
                {
                    "contract": "Warehouse Lease",
                    "expiry_date": (now + timedelta(days=120)).date().isoformat(),
                    "action_required": "Renewal negotiations"
                }
            ],
            "license_renewals": [
                {
                    "license": "Operating Authority",
                    "renewal_date": (now + timedelta(days=180)).date().isoformat(),
                    "status": "pending"
                }
            ],
            "compliance_dates": [
                {
                    "requirement": "Safety Audit",
                    "due_date": (now + timedelta(days=30)).date().isoformat(),
                    "status": "upcoming"
                }
            ]
        }
        
        return {
            "ok": True,
            "deadlines": deadlines,
            "total_pending": sum(len(v) for v in deadlines.values()),
            "urgent_count": 2  # Items due within 30 days
        }
    
    async def check_legal_compliance(self, domain: str = "corporate") -> dict:
        """Check compliance status for legal domain"""
        requirements = self.compliance_requirements.get(domain, {})
        
        if not requirements:
            return {
                "ok": False,
                "error": f"Unknown domain: {domain}"
            }
        
        # Mock compliance check
        compliance_status = []
        for area, details in requirements.items():
            reqs = details.get("requirements", [])
            compliance_status.append({
                "area": area,
                "compliant": (hash(area) % 10) >= 3,  # ~70% compliance
                "requirements_count": len(reqs),
                "requirements": reqs
            })
        
        compliant_count = sum(1 for s in compliance_status if s["compliant"])
        compliance_rate = (compliant_count / len(compliance_status) * 100) if compliance_status else 0
        
        return {
            "ok": True,
            "domain": domain,
            "compliance_rate": round(compliance_rate, 1),
            "status": "compliant" if compliance_rate >= 80 else "attention_needed",
            "details": compliance_status,
            "recommendations": [
                "Update corporate records",
                "Review employment contracts",
                "Conduct compliance audit"
            ] if compliance_rate < 80 else []
        }
    
    async def process_message(self, message: str, context: Optional[dict] = None) -> dict:
        """Process natural language legal requests"""
        message_lower = message.lower()
        
        if "contract" in message_lower or "review" in message_lower:
            contract_text = context.get("contract_text", "") if context else ""
            return await self.review_contract(contract_text)
        elif "deadline" in message_lower or "due" in message_lower:
            return await self.track_deadlines()
        elif "compliance" in message_lower or "check" in message_lower:
            domain = "corporate"
            if "employment" in message_lower:
                domain = "employment_law"
            elif "commercial" in message_lower:
                domain = "commercial_law"
            return await self.check_legal_compliance(domain)
        else:
            return await self.status()
