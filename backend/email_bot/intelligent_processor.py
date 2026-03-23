"""Intelligent email processor that maps inbound messages to bots."""
from __future__ import annotations

from typing import Any, Dict, List

from .rules import PRIORITY_RULES


class EmailClassifier:
    """Simple keyword-based email classifier placeholder."""

    def analyze_email(self, email: Dict[str, Any]) -> Dict[str, Any]:
        subject = email.get("subject", "") or ""
        body = email.get("body", "") or ""
        keywords = set()
        for token in (subject + " " + body).lower().split():
            cleaned = token.strip(".,:;!?")
            if cleaned:
                keywords.add(cleaned)
        return {"keywords": keywords}


class PriorityQueue:
    """Minimal priority queue placeholder for routing."""

    def __init__(self) -> None:
        self.items: List[Dict[str, Any]] = []

    def push(self, item: Dict[str, Any]) -> None:
        self.items.append(item)

    def pop(self) -> Dict[str, Any] | None:
        if not self.items:
            return None
        return self.items.pop(0)


class IntelligentEmailProcessor:
    """Maps inbound emails to the right bot with priority hints."""

    def __init__(self) -> None:
        self.bot_map = self._create_bot_mapping()
        self.classifier = EmailClassifier()
        self.priority_queue = PriorityQueue()

    def _create_bot_mapping(self) -> Dict[str, Dict[str, Any]]:
        return {
            "accounts@gabanilogistics.com": {
                "bot": "finance_bot",
                "system": "gts_main",
                "responsibilities": ["invoices", "payments", "accounting"],
                "priority": "high",
            },
            "admin@gabanilogistics.com": {
                "bot": "system_admin",
                "system": "admin",
                "responsibilities": ["system_management", "user_management"],
                "priority": "critical",
            },
            "customers@gabanilogistics.com": {
                "bot": "customer_service",
                "system": "both",
                "responsibilities": ["customer_support", "complaints", "inquiries"],
                "priority": "medium",
            },
            "doccontrol@gabanilogistics.com": {
                "bot": "documents_manager",
                "system": "both",
                "responsibilities": ["documents", "approvals", "archiving"],
                "priority": "medium",
            },
            "driver@gabanistore.com": {
                "bot": "operations_manager",
                "system": "tms",
                "responsibilities": ["driver_management", "operations"],
                "priority": "high",
            },
            "finance@gabanilogistics.com": {
                "bot": "finance_bot",
                "system": "both",
                "responsibilities": ["financial_analysis", "cost_calculation"],
                "priority": "high",
            },
            "freight@gabanilogistics.com": {
                "bot": "freight_broker",
                "system": "tms",
                "responsibilities": ["freight_quotes", "carrier_coordination"],
                "priority": "high",
            },
            "investments@gabanilogistics.com": {
                "bot": "strategy_advisor",
                "system": "gts_main",
                "responsibilities": ["investments", "partnerships"],
                "priority": "low",
            },
            "marketing@gabanilogistics.com": {
                "bot": "sales_team",
                "system": "gts_main",
                "responsibilities": ["marketing", "sales", "crm"],
                "priority": "medium",
            },
            "no-reply@gabanilogistics.com": {
                "bot": "system_notifier",
                "system": "both",
                "responsibilities": ["system_notifications", "alerts"],
                "priority": "system",
            },
            "operations@gabanilogistics.com": {
                "bot": "operations_manager",
                "system": "both",
                "responsibilities": ["operations_coordination"],
                "priority": "high",
            },
            "safety@gabanistore.com": {
                "bot": "safety_manager",
                "system": "both",
                "responsibilities": ["safety_incidents", "compliance"],
                "priority": "critical",
            },
            "security@gabanistore.com": {
                "bot": "security_manager",
                "system": "admin",
                "responsibilities": ["security_alerts", "investigations"],
                "priority": "critical",
            },
        }

    def process_incoming_email(self, email_message: Dict[str, Any]) -> Dict[str, Any]:
        try:
            analysis = self.classifier.analyze_email(email_message)
            target_bot = self._determine_target_bot(email_message, analysis)
            priority = self._calculate_priority(email_message, analysis)
            self._log_email_processing(email_message, target_bot, priority)
            result = self._route_to_bot(email_message, target_bot, analysis)
            self._handle_follow_up(email_message, result)
            return {
                "success": True,
                "bot": target_bot,
                "priority": priority,
                "action_taken": result.get("action"),
                "response_sent": result.get("response_sent", False) or result.get("auto_reply_sent", False),
            }
        except Exception as exc:  # pragma: no cover - defensive
            self._handle_processing_error(email_message, exc)
            return {"success": False, "error": str(exc)}

    def _determine_target_bot(self, email: Dict[str, Any], analysis: Dict[str, Any]) -> str:
        keywords = analysis.get("keywords", set())
        rules = {
            "finance_bot": [
                lambda: "invoice" in keywords,
                lambda: "payment" in keywords,
                lambda: "account" in keywords,
                lambda: email.get("to") in {"accounts@gabanilogistics.com", "finance@gabanilogistics.com"},
            ],
            "customer_service": [
                lambda: "support" in keywords,
                lambda: "help" in keywords,
                lambda: "complaint" in keywords,
                lambda: email.get("to") == "customers@gabanilogistics.com",
            ],
            "freight_broker": [
                lambda: "shipment" in keywords,
                lambda: "quote" in keywords,
                lambda: "carrier" in keywords,
                lambda: email.get("to") == "freight@gabanilogistics.com",
            ],
            "documents_manager": [
                lambda: "document" in keywords,
                lambda: "approval" in keywords,
                lambda: "sign" in keywords,
                lambda: email.get("to") == "doccontrol@gabanilogistics.com",
            ],
            "operations_manager": [
                lambda: "driver" in keywords,
                lambda: "schedule" in keywords,
                lambda: "dispatch" in keywords,
                lambda: email.get("to") in {"driver@gabanistore.com", "operations@gabanilogistics.com"},
            ],
            "safety_manager": [
                lambda: "safety" in keywords,
                lambda: "accident" in keywords,
                lambda: "incident" in keywords,
                lambda: email.get("to") == "safety@gabanistore.com",
            ],
            "security_manager": [
                lambda: "security" in keywords,
                lambda: "breach" in keywords,
                lambda: "investigation" in keywords,
                lambda: email.get("to") == "security@gabanistore.com",
            ],
        }
        for bot_name, conditions in rules.items():
            if any(condition() for condition in conditions):
                return bot_name
        return "customer_service"

    def _calculate_priority(self, email: Dict[str, Any], analysis: Dict[str, Any]) -> str:
        subject = (email.get("subject") or "").upper()
        body = (email.get("body") or "").lower()
        sender = email.get("from", "")
        for level, criteria_list in PRIORITY_RULES.items():
            for criteria in criteria_list:
                if "contains" in criteria and any(token in body for token in criteria["contains"]):
                    return level
                if "from_domain" in criteria and sender in criteria["from_domain"]:
                    return level
                if "subject_contains" in criteria and any(token in subject for token in criteria["subject_contains"]):
                    return level
        return "MEDIUM"

    def _log_email_processing(self, email: Dict[str, Any], target_bot: str, priority: str) -> None:
        self.priority_queue.push({"email_id": email.get("id"), "bot": target_bot, "priority": priority})

    def _route_to_bot(self, email: Dict[str, Any], target_bot: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        return {"action": "routed", "bot": target_bot, "analysis": analysis, "response_sent": False}

    def _handle_follow_up(self, email: Dict[str, Any], result: Dict[str, Any]) -> None:
        _ = (email, result)

    def _handle_processing_error(self, email: Dict[str, Any], error: Exception) -> None:
        _ = (email, error)


__all__ = ["IntelligentEmailProcessor", "EmailClassifier", "PriorityQueue"]
