"""
Safety Core Module
Compliance Monitor System
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple

logger = logging.getLogger(__name__)


class ComplianceMonitor:
    """Tracks regulatory compliance checks and audit scheduling."""

    def __init__(self):
        self.compliance_standards = self._load_compliance_standards()
        self.compliance_records = []
        self.audit_schedule = []

    def _load_compliance_standards(self) -> Dict[str, Any]:
        """Load internal catalog of compliance standards and requirements."""
        return {
            "osha_standards": {
                "personal_protective_equipment": {
                    "id": "OSHA-1910.132",
                    "title": "Personal Protective Equipment",
                    "requirements": [
                        "PPE hazard assessments are documented",
                        "Employees are issued role-appropriate PPE",
                        "PPE training records are current",
                        "Damaged PPE is replaced promptly",
                    ],
                    "compliance_check": "monthly",
                    "severity": "high",
                },
                "hazard_communication": {
                    "id": "OSHA-1910.1200",
                    "title": "Hazard Communication",
                    "requirements": [
                        "Safety data sheets are accessible",
                        "Chemical containers are properly labeled",
                        "Staff are trained on hazard communication",
                        "Hazard communication plan is reviewed",
                    ],
                    "compliance_check": "quarterly",
                    "severity": "high",
                },
                "emergency_action_plans": {
                    "id": "OSHA-1910.38",
                    "title": "Emergency Action Plans",
                    "requirements": [
                        "Evacuation routes are posted",
                        "Emergency contacts are up to date",
                        "Roles and responsibilities are documented",
                        "Emergency drills are conducted regularly",
                    ],
                    "compliance_check": "semi_annual",
                    "severity": "critical",
                },
            },
            "iso_45001_requirements": {
                "leadership_and_commitment": {
                    "id": "ISO-45001-5.1",
                    "title": "Leadership and Commitment",
                    "requirements": [
                        "Leadership sets documented safety objectives",
                        "Safety policy is communicated organization-wide",
                        "Resources are allocated for OH&S performance",
                        "Leaders review safety performance indicators",
                    ],
                    "compliance_check": "annual",
                    "severity": "medium",
                },
                "risk_assessment": {
                    "id": "ISO-45001-6.1",
                    "title": "Risk and Opportunity Assessment",
                    "requirements": [
                        "Hazards are identified systematically",
                        "Risk controls are defined and implemented",
                        "Residual risks are periodically reviewed",
                        "Opportunities for improvement are recorded",
                    ],
                    "compliance_check": "quarterly",
                    "severity": "high",
                },
            },
            "uae_safety_regulations": {
                "warehouse_safety": {
                    "id": "UAE-WHS-001",
                    "title": "Warehouse Safety Controls",
                    "requirements": [
                        "Aisles and exits remain unobstructed",
                        "Storage racks comply with load limits",
                        "Forklift routes are clearly marked",
                        "Incident reporting process is active",
                    ],
                    "compliance_check": "monthly",
                    "severity": "high",
                },
                "fire_safety": {
                    "id": "UAE-FIRE-001",
                    "title": "Fire Safety Compliance",
                    "requirements": [
                        "Fire suppression systems are inspected",
                        "Alarm systems are tested and documented",
                        "Emergency exits and signage are compliant",
                        "Fire response drills are performed",
                    ],
                    "compliance_check": "quarterly",
                    "severity": "critical",
                },
            },
        }

    async def check_safety_compliance(self) -> Dict[str, Any]:
        """Run compliance checks across all configured standards."""
        try:
            compliance_report = {
                "check_date": datetime.utcnow().isoformat(),
                "standards_checked": [],
                "issues_found": [],
                "compliance_rate": 0.0,
                "overall_status": "compliant",
                "recommendations": [],
            }

            total_requirements = 0
            compliant_requirements = 0

            # Iterate standards and evaluate compliance
            for category, standards in self.compliance_standards.items():
                for standard_id, standard in standards.items():
                    total_requirements += len(standard["requirements"])

                    compliance_report["standards_checked"].append(
                        {
                            "category": category,
                            "standard_id": standard["id"],
                            "title": standard["title"],
                            "check_frequency": standard["compliance_check"],
                        }
                    )

                    # Evaluate each standard
                    is_compliant, issues = await self._check_standard_compliance(
                        standard
                    )

                    if is_compliant:
                        compliant_requirements += len(standard["requirements"])
                    else:
                        compliance_report["issues_found"].extend(issues)
                        compliance_report["overall_status"] = "non_compliant"

            # Compute compliance rate
            if total_requirements > 0:
                compliance_rate = (compliant_requirements / total_requirements) * 100
                compliance_report["compliance_rate"] = round(compliance_rate, 2)

                if compliance_rate < 80:
                    compliance_report["overall_status"] = "needs_improvement"
                elif compliance_rate < 60:
                    compliance_report["overall_status"] = "poor"

            # Store report history
            self.compliance_records.append(compliance_report)

            # Keep latest 100 records
            if len(self.compliance_records) > 100:
                self.compliance_records = self.compliance_records[-100:]

            return compliance_report

        except Exception as e:
            logger.error(f"Safety compliance check failed: {str(e)}")
            return {"error": str(e)}

    async def _check_standard_compliance(
        self, standard: Dict[str, Any]
    ) -> Tuple[bool, List[Dict[str, Any]]]:
        """Evaluate one standard and return issues when non-compliant."""
        issues = []
        is_compliant = True

        import random

        for requirement in standard["requirements"]:
            # Simulated non-compliance chance
            if random.random() < 0.2:  # 20% probability
                is_compliant = False

                issue = {
                    "standard_id": standard["id"],
                    "standard_title": standard["title"],
                    "requirement": requirement,
                    "severity": standard["severity"],
                    "description": f"Requirement not satisfied: {requirement}",
                    "deadline": (datetime.utcnow() + timedelta(days=14)).isoformat(),
                }

                issues.append(issue)

        return is_compliant, issues

    async def schedule_compliance_audit(
        self, audit_type: str, auditor: str
    ) -> Dict[str, Any]:
        """Schedule a compliance audit with pre-defined scope."""
        try:
            audit = {
                "audit_id": f"AUDIT_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                "type": audit_type,
                "auditor": auditor,
                "scheduled_for": (datetime.utcnow() + timedelta(days=7)).isoformat(),
                "status": "scheduled",
                "scope": [],
                "preparation_required": [],
                "created_at": datetime.utcnow().isoformat(),
            }

            # Set audit scope by type
            if audit_type == "osha_compliance":
                audit["scope"] = [
                    "OSHA regulatory requirements",
                    "Workplace hazard controls",
                    "Incident and corrective action records",
                ]
            elif audit_type == "iso_45001":
                audit["scope"] = [
                    "OH&S management system clauses",
                    "Leadership and worker participation",
                    "Continuous improvement evidence",
                ]
            elif audit_type == "internal":
                audit["scope"] = [
                    "Internal policy compliance",
                    "Training and competency records",
                    "Inspection and maintenance logs",
                ]

            self.audit_schedule.append(audit)

            return audit

        except Exception as e:
            logger.error(f"Compliance audit scheduling failed: {str(e)}")
            return {"error": str(e)}
