"""Intelligent router that wires inbound emails to workflows."""
from __future__ import annotations

from typing import Any, Dict

from .processors import PROCESSOR_REGISTRY


class WorkflowEngine:
    """Executes simple workflow steps sequentially."""

    def execute(self, email: Dict[str, Any], workflow: list[dict[str, Any]]) -> Dict[str, Any]:
        results = []
        for step in workflow:
            processor_key = step.get("processor")
            processor = PROCESSOR_REGISTRY.get(processor_key)
            if not processor:
                continue
            outcome = processor.process(email)
            results.append({"step": step.get("step"), "outcome": outcome})
        return {"workflow": workflow, "results": results, "success": True}


class IntegrationService:
    """Scaffold for integrating with internal services."""

    def __init__(self) -> None:
        self.connected = True


class IntelligentEmailRouter:
    def __init__(self) -> None:
        self.processors = PROCESSOR_REGISTRY
        self.workflow_engine = WorkflowEngine()
        self.integration_service = IntegrationService()

    def route_and_process(self, email_message: Dict[str, Any]) -> Dict[str, Any]:
        email_type = self._classify_email_type(email_message)
        if email_type == "shipment_request":
            return self._handle_shipment_workflow(email_message)
        if email_type == "invoice":
            return self._handle_invoice_workflow(email_message)
        if email_type == "customer_support":
            return self._handle_support_workflow(email_message)
        if email_type == "safety_incident":
            return self._handle_safety_workflow(email_message)
        if email_type == "security_alert":
            return self._handle_security_workflow(email_message)
        return self._handle_general_workflow(email_message)

    def _classify_email_type(self, email: Dict[str, Any]) -> str:
        subject = (email.get("subject") or "").lower()
        body = (email.get("body") or "").lower()
        if any(token in subject or token in body for token in ["shipment", "quote", "carrier"]):
            return "shipment_request"
        if "invoice" in subject or "invoice" in body:
            return "invoice"
        if "support" in subject or "help" in body:
            return "customer_support"
        if any(token in body for token in ["incident", "accident", "safety"]):
            return "safety_incident"
        if any(token in body for token in ["breach", "security", "alert"]):
            return "security_alert"
        return "general"

    def _handle_shipment_workflow(self, email: Dict[str, Any]) -> Dict[str, Any]:
        workflow = [
            {"step": "extract_shipment_details", "processor": "freight", "auto": True},
            {"step": "find_carriers", "processor": "freight", "auto": True},
            {"step": "generate_quotes", "processor": "freight", "auto": True},
            {"step": "create_documents", "processor": "documents", "auto": True},
            {"step": "calculate_costs", "processor": "finance", "auto": True},
            {"step": "send_response", "processor": "customer_service", "auto": True},
        ]
        return self.workflow_engine.execute(email, workflow)

    def _handle_invoice_workflow(self, email: Dict[str, Any]) -> Dict[str, Any]:
        workflow = [
            {"step": "extract_invoice_data", "processor": "finance", "auto": True},
            {"step": "validate_invoice", "processor": "finance", "auto": True},
            {"step": "record_in_database", "processor": "finance", "auto": True},
            {"step": "schedule_payment", "processor": "finance", "auto": True},
            {"step": "archive_document", "processor": "documents", "auto": True},
        ]
        return self.workflow_engine.execute(email, workflow)

    def _handle_support_workflow(self, email: Dict[str, Any]) -> Dict[str, Any]:
        workflow = [
            {"step": "classify_support", "processor": "customer_service", "auto": True},
        ]
        return self.workflow_engine.execute(email, workflow)

    def _handle_safety_workflow(self, email: Dict[str, Any]) -> Dict[str, Any]:
        workflow = [
            {"step": "log_safety_incident", "processor": "safety", "auto": True},
        ]
        return self.workflow_engine.execute(email, workflow)

    def _handle_security_workflow(self, email: Dict[str, Any]) -> Dict[str, Any]:
        workflow = [
            {"step": "log_security_alert", "processor": "security", "auto": True},
            {"step": "notify_admin", "processor": "system_admin", "auto": True},
        ]
        return self.workflow_engine.execute(email, workflow)

    def _handle_general_workflow(self, email: Dict[str, Any]) -> Dict[str, Any]:
        processor = self.processors.get("customer_service")
        result = processor.process(email) if processor else {}
        return {"workflow": [], "results": [result], "success": True}


__all__ = ["IntelligentEmailRouter", "WorkflowEngine", "IntegrationService"]
