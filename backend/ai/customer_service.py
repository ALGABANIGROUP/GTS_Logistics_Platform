from __future__ import annotations

import traceback
from datetime import datetime
from typing import Any, Dict, List, Optional

from backend.ai.ai_bots import BaseAIBot
from backend.services.ai_customer_service import get_ai_customer_service


class CustomerServiceLearningBot(BaseAIBot):
    name = "customer_service"
    description = "Customer service bot with conversation analytics and escalation support."
    learning_frequency = "hourly"
    learning_intensity = "high"

    def __init__(self) -> None:
        super().__init__()
        self._svc = get_ai_customer_service()
        self.conversations: Dict[str, Dict[str, Any]] = {}
        self.tickets: Dict[int, Dict[str, Any]] = {}
        self.activities: List[Dict[str, Any]] = []
        self._ticket_sequence = 1

    def start_conversation(
        self,
        user_id: str,
        conversation_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        resolved_id = conversation_id or f"conv_{user_id}_{int(datetime.utcnow().timestamp())}"
        conversation = self.conversations.get(resolved_id)
        if conversation is None:
            incoming = metadata or {}
            conversation = {
                "id": resolved_id,
                "user_id": str(user_id),
                "customer_name": incoming.get("customer_name") or incoming.get("name") or f"Customer {user_id}",
                "customer_email": incoming.get("customer_email") or incoming.get("email"),
                "channel": incoming.get("channel") or "webchat",
                "status": "active",
                "created_at": datetime.utcnow().isoformat(),
                "last_updated_at": datetime.utcnow().isoformat(),
                "messages": [],
                "metadata": incoming,
                "unread_count": 0,
                "needs_human": False,
                "language": "en",
                "sentiment": "neutral",
                "last_intent": "unknown",
                "linked_ticket_id": None,
            }
            self.conversations[resolved_id] = conversation
            self._add_activity("conversation_started", conversation["customer_name"], resolved_id)
        return conversation

    async def process_message(
        self,
        message: str,
        user_id: str,
        conversation_id: str,
    ) -> Dict[str, Any]:
        started_at = datetime.utcnow()
        conversation = self.start_conversation(user_id=user_id, conversation_id=conversation_id)
        text = (message or "").strip()

        try:
            generated = self._svc.generate_reply(text, customer_context=conversation.get("metadata"))
            conversation["messages"].append(
                {
                    "id": len(conversation["messages"]) + 1,
                    "role": "user",
                    "sender": "customer",
                    "text": text,
                    "content": text,
                    "timestamp": datetime.utcnow().isoformat(),
                    "user_id": str(user_id),
                }
            )
            conversation["messages"].append(
                {
                    "id": len(conversation["messages"]) + 1,
                    "role": "bot",
                    "sender": "bot",
                    "text": generated["reply"],
                    "content": generated["reply"],
                    "timestamp": datetime.utcnow().isoformat(),
                    "intent": generated["intent"],
                    "sentiment": generated["sentiment"]["label"],
                    "language": generated["language"],
                }
            )
            conversation["last_updated_at"] = datetime.utcnow().isoformat()
            conversation["language"] = generated["language"]
            conversation["sentiment"] = generated["sentiment"]["label"]
            conversation["last_intent"] = generated["intent"]
            conversation["needs_human"] = bool(generated["needs_human"])
            conversation["status"] = "escalated" if generated["needs_human"] else "active"
            conversation["unread_count"] = 0

            linked_ticket = None
            if generated["needs_human"] and not conversation.get("linked_ticket_id"):
                linked_ticket = self.create_ticket(
                    customer_email=conversation.get("customer_email") or f"{user_id}@unknown.local",
                    subject=f"{generated['intent'].replace('_', ' ').title()} support request",
                    description=text,
                    conversation_id=conversation_id,
                    priority="high" if generated["urgency"] in {"high", "critical"} else "medium",
                    category=self._map_intent_to_category(generated["intent"]),
                    customer_name=conversation.get("customer_name"),
                )
                conversation["linked_ticket_id"] = linked_ticket["id"]
                self._add_activity("ticket_created", conversation["customer_name"], linked_ticket["ticket_number"])

            response_time_ms = (datetime.utcnow() - started_at).total_seconds() * 1000
            accuracy = 0.93 if generated["intent"] != "unknown" else 0.76
            self.record_execution_success(response_time_ms=response_time_ms, accuracy=accuracy)
            self._add_activity("bot_replied", conversation["customer_name"], generated["intent"])

            return {
                "conversation_id": conversation_id,
                "response": generated["reply"],
                "suggestion": generated["reply"],
                "intent": generated["intent"],
                "sentiment": generated["sentiment"],
                "language": generated["language"],
                "urgency": generated["urgency"],
                "needs_human": generated["needs_human"],
                "negotiation_offer": generated.get("negotiation_offer"),
                "ticket": linked_ticket,
                "generated_at": datetime.utcnow().isoformat(),
            }
        except Exception as exc:
            self.record_execution_error(
                error_type=type(exc).__name__,
                error_message=str(exc),
                severity=0.9,
                traceback=traceback.format_exc(),
            )
            return {
                "conversation_id": conversation_id,
                "response": "I'm sorry, I'm having trouble processing your request right now.",
                "suggestion": "I'm sorry, I'm having trouble processing your request right now.",
                "intent": "error",
                "sentiment": {"label": "neutral", "score": 0.0},
                "language": "en",
                "urgency": "medium",
                "needs_human": True,
                "error": str(exc),
                "generated_at": datetime.utcnow().isoformat(),
            }

    def collect_conversation_feedback(
        self,
        conversation_id: str,
        rating: int,
        feedback: Optional[str] = None,
    ) -> Dict[str, Any]:
        conversation = self.conversations.get(conversation_id)
        if conversation is None:
            raise KeyError(conversation_id)

        self.collect_feedback(
            rating=rating,
            session_id=conversation_id,
            comment=feedback,
            user_id=conversation.get("user_id"),
            feedback_type="conversation",
        )
        conversation["feedback"] = {
            "rating": rating,
            "comment": feedback,
            "timestamp": datetime.utcnow().isoformat(),
        }
        self._add_activity("feedback_received", conversation["customer_name"], str(rating))
        return conversation["feedback"]

    def get_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        return self.conversations.get(conversation_id)

    def list_conversations(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        filters = filters or {}
        conversations = list(self.conversations.values())
        conversations.sort(key=lambda item: item.get("last_updated_at", ""), reverse=True)

        status_filter = filters.get("status")
        channel_filter = filters.get("channel")
        if status_filter and status_filter != "all":
            conversations = [item for item in conversations if item.get("status") == status_filter]
        if channel_filter and channel_filter != "all":
            conversations = [item for item in conversations if item.get("channel") == channel_filter]

        return [
            {
                "id": item["id"],
                "userId": item.get("user_id"),
                "customerName": item.get("customer_name"),
                "channel": item.get("channel"),
                "status": item.get("status"),
                "unread": item.get("unread_count", 0) > 0,
                "unreadCount": item.get("unread_count", 0),
                "createdAt": item.get("created_at"),
                "lastUpdatedAt": item.get("last_updated_at"),
                "lastMessage": item.get("messages", [])[-1]["content"] if item.get("messages") else None,
                "lastMessageTime": self._format_time(item.get("last_updated_at")),
                "messageCount": len(item.get("messages", [])),
                "sentiment": item.get("sentiment", "neutral"),
                "language": item.get("language", "en"),
                "intent": item.get("last_intent", "unknown"),
                "needsHuman": item.get("needs_human", False),
                "linkedTicketId": item.get("linked_ticket_id"),
            }
            for item in conversations
        ]

    def create_ticket(
        self,
        customer_email: str,
        subject: str,
        description: str,
        conversation_id: Optional[str] = None,
        priority: str = "medium",
        category: str = "general",
        customer_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        ticket_id = self._ticket_sequence
        self._ticket_sequence += 1
        ticket = {
            "id": ticket_id,
            "ticket_number": f"TKT-{ticket_id:05d}",
            "customer_email": customer_email,
            "customer_name": customer_name or "Customer",
            "subject": subject,
            "description": description,
            "status": "open",
            "priority": priority,
            "category": category,
            "assigned_to": None,
            "conversation_id": conversation_id,
            "comments": [],
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }
        self.tickets[ticket_id] = ticket
        return ticket

    def list_tickets(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        filters = filters or {}
        tickets = list(self.tickets.values())
        tickets.sort(key=lambda item: item.get("created_at", ""), reverse=True)

        if filters.get("id"):
            tickets = [item for item in tickets if item["id"] == int(filters["id"])]
        if filters.get("status") and filters["status"] != "all":
            tickets = [item for item in tickets if item.get("status") == filters["status"]]
        if filters.get("priority") and filters["priority"] != "all":
            tickets = [item for item in tickets if item.get("priority") == filters["priority"]]
        if filters.get("assigned_to") and filters["assigned_to"] != "all":
            tickets = [item for item in tickets if str(item.get("assigned_to")) == str(filters["assigned_to"])]
        if filters.get("search"):
            search = str(filters["search"]).lower()
            tickets = [
                item for item in tickets
                if search in (item.get("subject") or "").lower()
                or search in (item.get("description") or "").lower()
                or search in item.get("ticket_number", "").lower()
            ]
        return tickets

    def update_ticket(self, ticket_id: int, patch: Dict[str, Any]) -> Dict[str, Any]:
        ticket = self.tickets.get(ticket_id)
        if ticket is None:
            raise KeyError(ticket_id)
        for field in ["subject", "description", "status", "priority", "assigned_to"]:
            if field in patch and patch[field] is not None:
                ticket[field] = patch[field]
        if "comments" in patch and isinstance(patch["comments"], list):
            ticket["comments"] = patch["comments"]
        ticket["updated_at"] = datetime.utcnow().isoformat()
        self._add_activity("ticket_updated", ticket.get("customer_name"), ticket["ticket_number"])
        return ticket

    def close_ticket(self, ticket_id: int, resolution: str = "") -> Dict[str, Any]:
        ticket = self.tickets.get(ticket_id)
        if ticket is None:
            raise KeyError(ticket_id)
        ticket["status"] = "closed"
        ticket["resolution"] = resolution
        ticket["updated_at"] = datetime.utcnow().isoformat()
        self._add_activity("ticket_closed", ticket.get("customer_name"), ticket["ticket_number"])
        return ticket

    def get_recent_activity(self, range_name: str = "today") -> List[Dict[str, Any]]:
        return self.activities[:20]

    def get_top_agents(self) -> List[Dict[str, Any]]:
        return [
            {"id": 1, "name": "Maya Carter", "role": "Senior Support Agent", "resolved": 42, "rating": 4.9},
            {"id": 2, "name": "Omar Bennett", "role": "Customer Success Agent", "resolved": 35, "rating": 4.7},
            {"id": 3, "name": "Lina Ford", "role": "Escalation Specialist", "resolved": 28, "rating": 4.8},
        ]

    def get_conversation_metrics(self, range_name: str = "today") -> Dict[str, Any]:
        conversations = list(self.conversations.values())
        total = len(conversations)
        escalated = sum(1 for item in conversations if item.get("needs_human"))
        resolved = sum(1 for item in conversations if item.get("status") in {"resolved", "closed"})
        return {
            "range": range_name,
            "total": total,
            "resolved": resolved,
            "escalated": escalated,
            "avgDuration": "4m" if total else "0m",
        }

    def get_stats(self) -> Dict[str, Any]:
        from backend.ai.data_collection_service import data_collection_service
        from backend.ai.learning_engine import bot_learning_engine

        profile = bot_learning_engine.get_bot_profile(self.name) or {}
        feedback = data_collection_service.get_bot_feedback(self.name, limit=500)
        performance = data_collection_service.get_bot_performance_history(self.name, limit=500)

        average_rating = round(
            sum(item["rating"] for item in feedback) / len(feedback), 2
        ) if feedback else 0.0
        average_response_time = round(
            sum(item["response_time"] for item in performance) / len(performance), 2
        ) if performance else 0.0

        return {
            "bot_id": self.name,
            "conversations": len(self.conversations),
            "messages": sum(len(item.get("messages", [])) for item in self.conversations.values()),
            "pending_tickets": sum(1 for item in self.tickets.values() if item.get("status") not in {"closed", "resolved"}),
            "average_rating": average_rating,
            "average_response_time_ms": average_response_time,
            "learning_profile": profile,
            "errors": data_collection_service.get_bot_error_logs(self.name, limit=20),
            "recent_feedback": feedback[:10],
        }

    def _add_activity(self, action: str, user: Optional[str], target: str) -> None:
        self.activities.insert(0, {
            "id": f"activity_{len(self.activities) + 1}",
            "user": user or "System",
            "action": action.replace("_", " "),
            "target": target,
            "time": self._format_time(datetime.utcnow().isoformat()),
        })
        self.activities = self.activities[:50]

    @staticmethod
    def _format_time(value: Optional[str]) -> str:
        if not value:
            return "now"
        try:
            dt = datetime.fromisoformat(value.replace("Z", ""))
            return dt.strftime("%H:%M")
        except ValueError:
            return "now"

    @staticmethod
    def _map_intent_to_category(intent: str) -> str:
        mapping = {
            "billing": "billing",
            "shipment": "operations",
            "technical": "technical",
            "complaint": "complaint",
            "negotiation": "sales",
        }
        return mapping.get(intent, "general")


customer_service_learning_bot = CustomerServiceLearningBot()
