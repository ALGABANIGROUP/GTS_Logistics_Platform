"""Integration layer between email system and BOS (Bot Operating System)."""
from __future__ import annotations

import logging
from typing import Any, Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class EmailBotIntegration:
    """Bridges incoming emails to BOS bot execution with intelligent routing."""

    def __init__(self, bot_os=None):
        """Initialize with optional reference to BOS orchestrator."""
        self.bot_os = bot_os
        self.email_to_bot_mapping = self._create_email_bot_mapping()
        self.execution_history: list[Dict[str, Any]] = []

    def _create_email_bot_mapping(self) -> Dict[str, Dict[str, Any]]:
        """Define which bot handles which email account."""
        return {
            "accounts@gabanilogistics.com": {
                "primary_bot": "finance_bot",
                "backup_bot": "platform_expenses",
                "workflows": ["invoice_processing", "payment_recording", "reconciliation"],
                "auto_execute": True,
                "requires_approval": False,
                "priority": "high"
            },
            "admin@gabanilogistics.com": {
                "primary_bot": "general_manager",
                "backup_bot": "system_admin",
                "workflows": ["system_management", "user_management"],
                "auto_execute": False,
                "requires_approval": True,
                "priority": "critical"
            },
            "customers@gabanilogistics.com": {
                "primary_bot": "customer_service",
                "backup_bot": "general_manager",
                "workflows": ["support_routing", "complaint_handling", "inquiry_response"],
                "auto_execute": True,
                "requires_approval": False,
                "priority": "medium"
            },
            "doccontrol@gabanilogistics.com": {
                "primary_bot": "documents_manager",
                "backup_bot": "general_manager",
                "workflows": ["document_processing", "approval_workflows", "archiving"],
                "auto_execute": True,
                "requires_approval": True,
                "priority": "high"
            },
            "driver@gabanilogistics.com": {
                "primary_bot": "operations_manager",
                "backup_bot": "freight_broker",
                "workflows": ["driver_coordination", "dispatch_management", "route_optimization"],
                "auto_execute": True,
                "requires_approval": False,
                "priority": "high"
            },
            "finance@gabanilogistics.com": {
                "primary_bot": "finance_bot",
                "backup_bot": "platform_expenses",
                "workflows": ["financial_analysis", "cost_calculation", "reporting"],
                "auto_execute": True,
                "requires_approval": False,
                "priority": "high"
            },
            "freight@gabanilogistics.com": {
                "primary_bot": "freight_broker",
                "backup_bot": "customer_service",
                "workflows": ["shipment_processing", "carrier_coordination", "quote_generation"],
                "auto_execute": True,
                "requires_approval": False,
                "priority": "high"
            },
            "investments@gabanilogistics.com": {
                "primary_bot": "strategy_advisor",
                "backup_bot": "general_manager",
                "workflows": ["partnership_evaluation", "investment_analysis"],
                "auto_execute": False,
                "requires_approval": True,
                "priority": "medium"
            },
            "operations@gabanilogistics.com": {
                "primary_bot": "legal_consultant",
                "backup_bot": "general_manager",
                "workflows": ["contract_review", "compliance_check", "dispute_handling"],
                "auto_execute": False,
                "requires_approval": True,
                "priority": "high"
            },
            "marketing@gabanilogistics.com": {
                "primary_bot": "strategy_advisor",
                "backup_bot": "customer_service",
                "workflows": ["campaign_coordination", "lead_management"],
                "auto_execute": True,
                "requires_approval": False,
                "priority": "low"
            },
            "operations@gabanilogistics.com": {
                "primary_bot": "operations_manager",
                "backup_bot": "general_manager",
                "workflows": ["operation_coordination", "resource_planning"],
                "auto_execute": True,
                "requires_approval": False,
                "priority": "high"
            },
            "safety@gabanilogistics.com": {
                "primary_bot": "safety_manager",
                "backup_bot": "maintenance_dev",
                "workflows": ["incident_reporting", "compliance_tracking", "preventive_measures"],
                "auto_execute": True,
                "requires_approval": False,
                "priority": "critical"
            },
            "security@gabanilogistics.com": {
                "primary_bot": "security_manager",
                "backup_bot": "general_manager",
                "workflows": ["threat_assessment", "breach_response", "investigation"],
                "auto_execute": True,
                "requires_approval": False,
                "priority": "critical"
            }
        }

    async def route_email_to_bot(self, email: Dict[str, Any]) -> Dict[str, Any]:
        """Route incoming email to appropriate bot and execute workflow."""
        email_to = email.get("to", "")
        email_id = email.get("id")

        # Get bot configuration for this email account
        bot_config = self.email_to_bot_mapping.get(email_to)
        if not bot_config:
            logger.warning(f"No bot mapping for email account: {email_to}")
            return {
                "success": False,
                "error": "unmapped_email_account",
                "email_to": email_to
            }

        primary_bot = bot_config.get("primary_bot")
        workflows = bot_config.get("workflows", [])
        auto_execute = bot_config.get("auto_execute", False)
        requires_approval = bot_config.get("requires_approval", False)
        priority = bot_config.get("priority", "medium")

        # Determine which workflow to execute
        workflow = self._select_workflow(email, workflows)

        # Build execution payload
        execution_payload = {
            "action": workflow,
            "email_id": email_id,
            "source": email_to,
            "priority": priority,
            "requires_approval": requires_approval,
            "metadata": {
                "from": email.get("from"),
                "subject": email.get("subject"),
                "timestamp": datetime.utcnow().isoformat()
            }
        }

        # Execute via BOS if available
        result = {
            "success": True,
            "email_id": email_id,
            "bot": primary_bot,
            "workflow": workflow,
            "auto_execute": auto_execute,
            "requires_approval": requires_approval,
            "execution_payload": execution_payload,
            "timestamp": datetime.utcnow().isoformat()
        }

        if self.bot_os and auto_execute and not requires_approval:
            try:
                # Execute bot via BOS
                if primary_bot:
                    bot_result = await self._execute_via_bos(primary_bot, execution_payload)
                    result["bot_execution"] = bot_result
                    result["executed"] = True
                else:
                    result["executed"] = False
                    result["reason"] = "no_primary_bot"
            except Exception as e:
                logger.error(f"Error executing bot {primary_bot}: {e}")
                result["bot_execution"] = {"error": str(e)}
                result["executed"] = False
        else:
            result["executed"] = False
            result["reason"] = "approval_required" if requires_approval else "bos_unavailable"

        # Record in history
        self.execution_history.append(result)

        return result

    def _select_workflow(self, email: Dict[str, Any], available_workflows: list[str]) -> str:
        """Select appropriate workflow based on email content."""
        subject = (email.get("subject", "") or "").lower()
        body = (email.get("body", "") or "").lower()
        content = f"{subject} {body}"

        # Default to first available workflow
        if not available_workflows:
            return "general_processing"

        # Keyword-based workflow selection
        workflow_keywords = {
            "invoice_processing": ["invoice", "bill", "statement"],
            "payment_recording": ["payment", "paid", "transfer"],
            "shipment_processing": ["shipment", "load", "pickup"],
            "support_routing": ["help", "support", "issue"],
            "incident_reporting": ["incident", "accident", "injury"],
            "threat_assessment": ["threat", "suspicious", "alert"],
            "contract_review": ["contract", "agreement", "terms"],
            "campaign_coordination": ["campaign", "marketing", "promotion"]
        }

        for workflow, keywords in workflow_keywords.items():
            if workflow in available_workflows:
                if any(keyword in content for keyword in keywords):
                    return workflow

        return available_workflows[0]

    async def _execute_via_bos(self, bot_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Execute bot action through BOS orchestrator."""
        if not self.bot_os:
            raise RuntimeError("BOS orchestrator not configured")

        try:
            # Call BOS run method
            result = await self.bot_os.run_bot(bot_name, payload)
            return result
        except Exception as e:
            logger.error(f"BOS execution failed: {e}")
            raise

    def get_execution_history(self, limit: int = 100) -> list[Dict[str, Any]]:
        """Get recent email-to-bot execution history."""
        return self.execution_history[-limit:]

    def get_bot_for_email(self, email_account: str) -> Optional[str]:
        """Get primary bot for an email account."""
        config = self.email_to_bot_mapping.get(email_account)
        return config.get("primary_bot") if config else None

    def get_email_accounts_for_bot(self, bot_name: str) -> list[str]:
        """Get all email accounts handled by a specific bot."""
        return [
            email for email, config in self.email_to_bot_mapping.items()
            if config.get("primary_bot") == bot_name or config.get("backup_bot") == bot_name
        ]

    def add_custom_mapping(self, email_account: str, bot_config: Dict[str, Any]) -> None:
        """Add or update custom email-to-bot mapping."""
        if not email_account.endswith("@gabanilogistics.com"):
            raise ValueError("Invalid email domain")
        self.email_to_bot_mapping[email_account] = bot_config
        logger.info(f"Added custom mapping for {email_account} -> {bot_config.get('primary_bot')}")


__all__ = ["EmailBotIntegration"]
