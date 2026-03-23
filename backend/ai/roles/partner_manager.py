from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


ALLOWED_REQUIRED_BOTS = {
    "strategy_advisor",
    "legal_consultant",
    "system_admin",
    "secai_security_manager",
}


@dataclass
class PartnerManagerBot:
    """
    Partner Manager orchestrates partner workflows via Operations Manager only.
    """

    name: str = "partner_manager"

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        action = str((payload or {}).get("action") or "partner_dashboard").strip().lower()
        partner_id = (payload or {}).get("partner_id")
        inputs = (payload or {}).get("inputs") or {}

        plan = self._build_plan(action, partner_id, inputs)
        if not plan:
            return {
                "ok": False,
                "action": action,
                "partner_id": partner_id,
                "data": {},
                "warnings": [f"Unsupported action: {action}"],
                "next_steps": ["Use a supported action name."],
            }

        try:
            ops_result = await self._orchestrate(plan)
            return {
                "ok": True,
                "action": action,
                "partner_id": partner_id,
                "data": {
                    "workflow": plan,
                    "workflow_name": plan.get("workflow_name"),
                    "required_bots": plan.get("required_bots", []),
                    "operations_manager_response": ops_result,
                },
                "warnings": [],
                "next_steps": plan.get("next_steps", []),
            }
        except Exception as exc:
            return {
                "ok": False,
                "action": action,
                "partner_id": partner_id,
                "data": {"workflow": plan},
                "warnings": [f"Orchestration failed: {exc}"],
                "next_steps": ["Retry the request or inspect Operations Manager logs."],
            }

    async def process_message(self, message: str, context: Dict[str, Any] | None = None) -> Dict[str, Any]:
        ctx = context or {}
        payload = {
            "action": ctx.get("action") or "partner_dashboard",
            "partner_id": ctx.get("partner_id"),
            "inputs": ctx.get("inputs") or {},
            "message": message,
        }
        return await self.run(payload)

    async def status(self) -> Dict[str, Any]:
        return {
            "name": "AI Partner Manager",
            "description": "Partner lifecycle management via Operations Manager orchestration.",
            "status": "active",
        }

    async def config(self) -> Dict[str, Any]:
        return {
            "name": "AI Partner Manager",
            "actions": list(self._action_map().keys()),
            "orchestration": {
                "delegates_to": "operations_manager",
                "required_bots_allowlist": sorted(ALLOWED_REQUIRED_BOTS),
            },
        }

    def _action_map(self) -> Dict[str, Dict[str, Any]]:
        return {
            "create_agreement": {
                "workflow_name": "partner_agreement_create",
                "required_bots": ["legal_consultant"],
                "expected_outputs": {
                    "agreement_draft": "object",
                    "compliance_checklist": "list",
                },
                "next_steps": ["Review agreement draft and confirm partner terms."],
            },
            "negotiate_agreement": {
                "workflow_name": "partner_agreement_negotiate",
                "required_bots": ["legal_consultant", "strategy_advisor"],
                "expected_outputs": {
                    "negotiation_summary": "object",
                    "open_items": "list",
                },
                "next_steps": ["Confirm negotiation outcomes and update terms."],
            },
            "execute_agreement": {
                "workflow_name": "partner_agreement_execute",
                "required_bots": ["legal_consultant", "system_admin"],
                "expected_outputs": {
                    "execution_receipt": "object",
                    "activation_status": "string",
                },
                "next_steps": ["Notify partner and activate onboarding workflow."],
            },
            "monitor_agreement": {
                "workflow_name": "partner_agreement_monitor",
                "required_bots": ["system_admin", "secai_security_manager"],
                "expected_outputs": {
                    "monitoring_summary": "object",
                    "alerts": "list",
                },
                "next_steps": ["Review alerts and schedule compliance follow-up."],
            },
            "evaluate_partner": {
                "workflow_name": "partner_evaluation",
                "required_bots": ["strategy_advisor", "secai_security_manager"],
                "expected_outputs": {
                    "scorecard": "object",
                    "risks": "list",
                },
                "next_steps": ["Share evaluation summary with Operations Manager."],
            },
            "risk_report": {
                "workflow_name": "partner_risk_report",
                "required_bots": ["secai_security_manager"],
                "expected_outputs": {
                    "risk_profile": "object",
                    "mitigation_plan": "list",
                },
                "next_steps": ["Review risk profile and assign mitigation owner."],
            },
            "partner_dashboard": {
                "workflow_name": "partner_dashboard",
                "required_bots": ["strategy_advisor"],
                "expected_outputs": {
                    "dashboard": "object",
                    "kpis": "list",
                },
                "next_steps": ["Refresh dashboard weekly."],
            },
            "commission_report": {
                "workflow_name": "partner_commission_report",
                "required_bots": ["system_admin"],
                "expected_outputs": {
                    "commission_summary": "object",
                    "payout_schedule": "list",
                },
                "next_steps": ["Share commission summary with finance team."],
            },
            "profitability_report": {
                "workflow_name": "partner_profitability_report",
                "required_bots": ["strategy_advisor"],
                "expected_outputs": {
                    "profitability": "object",
                    "trend_analysis": "object",
                },
                "next_steps": ["Highlight top-performing partner segments."],
            },
            "growth_recommendation": {
                "workflow_name": "partner_growth_recommendation",
                "required_bots": ["strategy_advisor"],
                "expected_outputs": {
                    "recommendations": "list",
                    "supporting_data": "object",
                },
                "next_steps": ["Review recommendations and align with quarterly goals."],
            },
        }

    def _build_plan(
        self, action: str, partner_id: Optional[str], inputs: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        mapping = self._action_map()
        if action not in mapping:
            return None
        template = mapping[action]
        required_bots = [
            bot for bot in template.get("required_bots", []) if bot in ALLOWED_REQUIRED_BOTS
        ]
        return {
            "workflow_name": template["workflow_name"],
            "partner_id": partner_id,
            "inputs": inputs,
            "required_bots": required_bots,
            "expected_outputs": template.get("expected_outputs", {}),
            "next_steps": template.get("next_steps", []),
        }

    async def _orchestrate(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        registry = self._get_registry()
        ops = registry.get("operations_manager")
        if ops is None:
            raise RuntimeError("Operations Manager is not available in registry")
        payload = {
            "workflow_name": plan["workflow_name"],
            "partner_id": plan.get("partner_id"),
            "inputs": plan.get("inputs", {}),
            "required_bots": plan.get("required_bots", []),
            "expected_outputs": plan.get("expected_outputs", {}),
        }
        return await ops.run(payload)

    def _get_registry(self):
        from backend.main import ai_registry

        return ai_registry
