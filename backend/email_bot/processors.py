"""Email processors for specific bot domains."""
from __future__ import annotations

from typing import Any, Dict, List


class BaseEmailProcessor:
    def process(self, email: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError


class FinanceEmailProcessor(BaseEmailProcessor):
    """Processes financial emails: invoices, payments, accounting."""

    def process(self, email: Dict[str, Any]) -> Dict[str, Any]:
        actions: List[Dict[str, Any]] = []

        if self._is_invoice_email(email):
            invoice_data = self._extract_invoice_data(email)
            actions.append({"type": "create_invoice", "data": invoice_data, "auto_process": True})

        if self._is_payment_email(email):
            payment_data = self._extract_payment_data(email)
            actions.append({"type": "record_payment", "data": payment_data, "auto_process": True})

        response = self._generate_auto_response(email, actions)
        return {"processed": True, "actions": actions, "response": response}

    def _is_invoice_email(self, email: Dict[str, Any]) -> bool:
        subject = email.get("subject", "").lower()
        body = email.get("body", "").lower()
        return "invoice" in subject or "invoice" in body

    def _is_payment_email(self, email: Dict[str, Any]) -> bool:
        subject = email.get("subject", "").lower()
        body = email.get("body", "").lower()
        return "payment" in subject or "payment" in body

    def _extract_invoice_data(self, email: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "subject": email.get("subject"),
            "from": email.get("from"),
            "amount": None,
            "due_date": None,
            "attachments": email.get("attachments", []),
        }

    def _extract_payment_data(self, email: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "subject": email.get("subject"),
            "from": email.get("from"),
            "amount": None,
            "reference": None,
        }

    def _generate_auto_response(self, email: Dict[str, Any], actions: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not actions:
            return {"auto_response_sent": False}
        return {"auto_response_sent": True, "template": "finance_auto_response.html"}


class CustomerServiceEmailProcessor(BaseEmailProcessor):
    """Processes customer support inquiries."""

    def process(self, email: Dict[str, Any]) -> Dict[str, Any]:
        intent = self._classify_intent(email)
        handlers = {
            "tracking": self._handle_tracking_request,
            "complaint": self._handle_complaint,
            "quote_request": self._handle_quote_request,
            "general_inquiry": self._handle_general_inquiry,
        }
        if intent in handlers:
            result = handlers[intent](email)
            if result.get("auto_reply_possible"):
                result["auto_reply_sent"] = True
            return result
        return {"needs_human_review": True, "escalated_to": "admin"}

    def _classify_intent(self, email: Dict[str, Any]) -> str:
        subject = email.get("subject", "").lower()
        body = email.get("body", "").lower()
        if "track" in subject or "tracking" in body:
            return "tracking"
        if "complaint" in subject or "issue" in body:
            return "complaint"
        if "quote" in subject or "price" in body:
            return "quote_request"
        return "general_inquiry"

    def _handle_tracking_request(self, email: Dict[str, Any]) -> Dict[str, Any]:
        return {"auto_reply_possible": True, "action": "tracking_response"}

    def _handle_complaint(self, email: Dict[str, Any]) -> Dict[str, Any]:
        return {"needs_human_review": True, "action": "complaint_logged"}

    def _handle_quote_request(self, email: Dict[str, Any]) -> Dict[str, Any]:
        return {"auto_reply_possible": True, "action": "quote_generated"}

    def _handle_general_inquiry(self, email: Dict[str, Any]) -> Dict[str, Any]:
        return {"auto_reply_possible": True, "action": "generic_reply"}


class FreightEmailProcessor(BaseEmailProcessor):
    """Processes freight and shipment requests."""

    def process(self, email: Dict[str, Any]) -> Dict[str, Any]:
        request = self._extract_shipment_request(email)
        if not request:
            return {"error": "could_not_extract_shipment_details"}
        carriers = self._find_available_carriers(request)
        quotes = self._generate_quotes(request, carriers)
        return {
            "shipment_created": True,
            "quotes_generated": len(quotes),
            "carriers_contacted": len(carriers),
            "auto_reply_sent": True,
        }

    def _extract_shipment_request(self, email: Dict[str, Any]) -> Dict[str, Any] | None:
        body = email.get("body", "").lower()
        if "shipment" in body or "quote" in body:
            return {"source": email.get("from"), "body": email.get("body")}
        return None

    def _find_available_carriers(self, request: Dict[str, Any]) -> List[Dict[str, Any]]:
        return [{"name": "Carrier A"}, {"name": "Carrier B"}]

    def _generate_quotes(self, request: Dict[str, Any], carriers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return [{"carrier": carrier["name"], "price": None} for carrier in carriers]


class DocumentsEmailProcessor(BaseEmailProcessor):
    def process(self, email: Dict[str, Any]) -> Dict[str, Any]:
        return {"processed": True, "action": "archive_document", "auto_reply_sent": False}


class OperationsEmailProcessor(BaseEmailProcessor):
    def process(self, email: Dict[str, Any]) -> Dict[str, Any]:
        return {"processed": True, "action": "dispatch_review", "auto_reply_sent": False}


class SafetyEmailProcessor(BaseEmailProcessor):
    def process(self, email: Dict[str, Any]) -> Dict[str, Any]:
        return {"processed": True, "action": "safety_incident_logged", "auto_reply_sent": False}


class SecurityEmailProcessor(BaseEmailProcessor):
    """Processes security alerts and investigation requests."""

    def process(self, email: Dict[str, Any]) -> Dict[str, Any]:
        severity = self._assess_severity(email)
        actions = []
        
        if severity in ["critical", "high"]:
            actions.append({
                "type": "immediate_investigation",
                "priority": severity,
                "alert_admins": True,
                "auto_escalate": True
            })
        
        actions.append({
            "type": "security_incident_logged",
            "severity": severity,
            "timestamp": None,
            "requires_review": severity in ["critical", "high"]
        })
        
        return {
            "processed": True,
            "actions": actions,
            "severity": severity,
            "auto_reply_sent": severity not in ["critical", "high"]
        }
    
    def _assess_severity(self, email: Dict[str, Any]) -> str:
        content = (email.get("subject", "") + " " + email.get("body", "")).lower()
        if any(word in content for word in ["breach", "compromised", "unauthorized", "critical"]):
            return "critical"
        if any(word in content for word in ["alert", "suspicious", "unusual"]):
            return "high"
        return "medium"


class InvestmentEmailProcessor(BaseEmailProcessor):
    """Processes investment and partnership inquiries."""

    def process(self, email: Dict[str, Any]) -> Dict[str, Any]:
        investment_type = self._classify_investment(email)
        actions = []
        
        if investment_type == "partnership":
            actions.append({
                "type": "partnership_inquiry",
                "extract_details": True,
                "require_ceo_review": True
            })
        elif investment_type == "funding":
            actions.append({
                "type": "funding_opportunity",
                "extract_terms": True,
                "require_finance_review": True
            })
        else:
            actions.append({
                "type": "general_inquiry",
                "escalate_to": "strategy_advisor"
            })
        
        return {
            "processed": True,
            "investment_type": investment_type,
            "actions": actions,
            "requires_manual_review": True,
            "auto_reply_sent": False
        }
    
    def _classify_investment(self, email: Dict[str, Any]) -> str:
        content = (email.get("subject", "") + " " + email.get("body", "")).lower()
        if any(word in content for word in ["partnership", "collaborate", "joint"]):
            return "partnership"
        if any(word in content for word in ["funding", "investment", "capital", "fund"]):
            return "funding"
        return "inquiry"


class SystemAdminEmailProcessor(BaseEmailProcessor):
    """Processes system administration and management tasks."""

    def process(self, email: Dict[str, Any]) -> Dict[str, Any]:
        admin_type = self._classify_admin_task(email)
        actions = []
        
        if admin_type == "user_management":
            actions.append({
                "type": "user_management_task",
                "priority": "high",
                "requires_verification": True
            })
        elif admin_type == "system_maintenance":
            actions.append({
                "type": "schedule_maintenance",
                "priority": "high",
                "notify_users": True
            })
        else:
            actions.append({
                "type": "admin_task",
                "requires_review": True
            })
        
        return {
            "processed": True,
            "admin_type": admin_type,
            "actions": actions,
            "auto_reply_sent": False
        }
    
    def _classify_admin_task(self, email: Dict[str, Any]) -> str:
        content = (email.get("subject", "") + " " + email.get("body", "")).lower()
        if any(word in content for word in ["user", "account", "access", "permission"]):
            return "user_management"
        if any(word in content for word in ["maintenance", "update", "backup", "deploy"]):
            return "system_maintenance"
        return "general"


PROCESSOR_REGISTRY = {
    "finance": FinanceEmailProcessor(),
    "customer_service": CustomerServiceEmailProcessor(),
    "freight": FreightEmailProcessor(),
    "documents": DocumentsEmailProcessor(),
    "operations": OperationsEmailProcessor(),
    "safety": SafetyEmailProcessor(),
    "security": SecurityEmailProcessor(),
    "investments": InvestmentEmailProcessor(),
    "system_admin": SystemAdminEmailProcessor(),
}
