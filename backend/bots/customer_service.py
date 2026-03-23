# backend/bots/customer_service.py
"""
Customer Service Bot
Handles customer inquiries, support tickets, and service requests.
"""

from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any
import asyncio


class CustomerServiceBot:
    """Customer Service - Support and inquiry management"""

    def __init__(self):
        self.name = "customer_service"
        self.display_name = "👥 Customer Service"
        self.description = "Customer inquiry handling and support"
        self.version = "1.0.0"
        self.mode = "support"
        self.is_active = True

        # Support data structures
        self.support_tickets: List[Dict] = []
        self.customer_inquiries: List[Dict] = []
        self.faq_database: Dict[str, str] = {}

    async def run(self, payload: dict) -> dict:
        """Main execution method"""
        action = payload.get("action", "status")

        if action == "status":
            return await self.status()
        elif action == "create_ticket":
            return await self.create_ticket(payload.get("data", {}))
        elif action == "get_tickets":
            return await self.get_tickets()
        elif action == "update_ticket":
            return await self.update_ticket(payload.get("ticket_id"), payload.get("status"))
        elif action == "search_faq":
            return await self.search_faq(payload.get("query", ""))
        elif action == "get_inquiries":
            return await self.get_inquiries()
        else:
            return {"error": f"Unknown action: {action}"}

    async def status(self) -> dict:
        """Return bot health/status."""
        return {
            "ok": True,
            "bot": self.name,
            "version": self.version,
            "active_tickets": len([t for t in self.support_tickets if t.get("status") == "open"]),
            "total_inquiries": len(self.customer_inquiries),
            "message": "Customer service operational"
        }

    async def create_ticket(self, data: dict) -> dict:
        """Create a new support ticket"""
        ticket = {
            "id": f"TICKET-{len(self.support_tickets) + 1}",
            "customer_id": data.get("customer_id"),
            "subject": data.get("subject"),
            "description": data.get("description"),
            "priority": data.get("priority", "medium"),
            "status": "open",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        self.support_tickets.append(ticket)
        return {"success": True, "ticket": ticket}

    async def get_tickets(self) -> dict:
        """Get all support tickets"""
        return {"tickets": self.support_tickets}

    async def update_ticket(self, ticket_id: str, status: str) -> dict:
        """Update ticket status"""
        for ticket in self.support_tickets:
            if ticket["id"] == ticket_id:
                ticket["status"] = status
                ticket["updated_at"] = datetime.now(timezone.utc).isoformat()
                return {"success": True, "ticket": ticket}
        return {"error": "Ticket not found"}

    async def search_faq(self, query: str) -> dict:
        """Search FAQ database"""
        # Simple keyword matching
        results = []
        for question, answer in self.faq_database.items():
            if query.lower() in question.lower():
                results.append({"question": question, "answer": answer})
        return {"results": results[:5]}  # Return top 5 matches

    async def get_inquiries(self) -> dict:
        """Get customer inquiries"""
        return {"inquiries": self.customer_inquiries}