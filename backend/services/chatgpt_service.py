"""
ChatGPT integration service.

This service only uses a real OpenAI-compatible provider when explicitly
configured. It no longer returns mock conversational responses in production
paths, because that created misleading behavior for users and operators.
"""

from __future__ import annotations

import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

import httpx

logger = logging.getLogger(__name__)


class ChatServiceUnavailableError(RuntimeError):
    """Raised when the external chat provider is not configured or unavailable."""


class ChatGPTService:
    """Handles AI chat, sentiment, and lightweight conversation history."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = (api_key or os.getenv("OPENAI_API_KEY") or "").strip()
        self.model = (os.getenv("OPENAI_CHAT_MODEL") or "gpt-4o-mini").strip()
        self.api_base = (
            os.getenv("OPENAI_API_BASE_URL") or "https://api.openai.com/v1"
        ).rstrip("/")
        self.timeout_seconds = float(os.getenv("OPENAI_TIMEOUT_SECONDS", "30"))
        self.conversation_history: Dict[str, List[Dict[str, Any]]] = {}
        self.system_prompts = self._load_system_prompts()

    def is_configured(self) -> bool:
        return bool(self.api_key)

    def _load_system_prompts(self) -> Dict[str, str]:
        """Load system prompts for different conversation types."""
        return {
            "customer_support": (
                "You are a helpful customer support agent for Gabani Transport "
                "Solutions (GTS), a logistics and shipping company. Help with "
                "tracking shipments, quotes, delivery questions, and issue "
                "resolution. Be accurate and professional. If you do not know "
                "something, say so clearly and suggest a human handoff."
            ),
            "driver_assistant": (
                "You are an AI assistant for delivery drivers at Gabani "
                "Transport Solutions. Prioritize safety and efficiency."
            ),
            "sales_assistant": (
                "You are a sales assistant for Gabani Transport Solutions. "
                "Be persuasive but honest and focus on customer value."
            ),
        }

    async def chat(
        self,
        user_message: str,
        conversation_id: str,
        user_context: Optional[Dict[str, Any]] = None,
        conversation_type: str = "customer_support",
    ) -> Dict[str, Any]:
        """
        Process a chat message with a configured AI provider.
        """
        if not self.is_configured():
            raise ChatServiceUnavailableError(
                "Chat service is not configured. Set OPENAI_API_KEY to enable AI chat."
            )

        try:
            history = self.conversation_history.setdefault(conversation_id, [])
            history.append(
                {
                    "role": "user",
                    "content": user_message,
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )

            enhanced_prompt = self._build_enhanced_prompt(
                user_message=user_message,
                user_context=user_context,
                conversation_type=conversation_type,
            )

            ai_response = await self._call_chatgpt_api(
                messages=[
                    {
                        "role": "system",
                        "content": self.system_prompts.get(
                            conversation_type,
                            self.system_prompts["customer_support"],
                        ),
                    },
                    *[
                        {"role": item["role"], "content": item["content"]}
                        for item in history[:-1]
                    ],
                    {"role": "user", "content": enhanced_prompt},
                ]
            )

            history.append(
                {
                    "role": "assistant",
                    "content": ai_response,
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )

            return {
                "response": ai_response,
                "conversation_id": conversation_id,
                "timestamp": datetime.utcnow().isoformat(),
            }
        except ChatServiceUnavailableError:
            raise
        except Exception as exc:
            logger.error("Error in chat: %s", exc)
            raise

    def _build_enhanced_prompt(
        self,
        user_message: str,
        user_context: Optional[Dict[str, Any]],
        conversation_type: str,
    ) -> str:
        """Build enhanced prompt with available user context."""
        del conversation_type  # reserved for future prompt branching

        context_parts = [user_message]

        if user_context:
            if "shipment" in user_context:
                shipment = user_context["shipment"]
                context_parts.append(
                    (
                        f"[Context: Customer asking about shipment "
                        f"#{shipment.get('id')} from {shipment.get('origin')} "
                        f"to {shipment.get('destination')}, status: "
                        f"{shipment.get('status')}]"
                    )
                )

            if "customer" in user_context:
                customer = user_context["customer"]
                context_parts.append(
                    (
                        f"[Context: Customer {customer.get('name')}, "
                        f"total shipments: {customer.get('total_shipments', 0)}]"
                    )
                )

        return "\n".join(context_parts)

    async def _call_chatgpt_api(self, messages: List[Dict[str, str]]) -> str:
        """Call the configured OpenAI-compatible chat completions endpoint."""
        if not self.is_configured():
            raise ChatServiceUnavailableError(
                "Chat service is not configured. Set OPENAI_API_KEY to enable AI chat."
            )

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.3,
            "max_tokens": 500,
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                response = await client.post(
                    f"{self.api_base}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()
        except httpx.HTTPStatusError as exc:
            logger.error(
                "OpenAI API returned %s: %s",
                exc.response.status_code,
                exc.response.text[:300],
            )
            raise ChatServiceUnavailableError("Chat provider request failed.") from exc
        except httpx.HTTPError as exc:
            logger.error("OpenAI API call failed: %s", exc)
            raise ChatServiceUnavailableError("Chat provider is unavailable.") from exc

        try:
            return str(data["choices"][0]["message"]["content"]).strip()
        except Exception as exc:
            logger.error("Unexpected OpenAI response shape: %s", exc)
            raise ChatServiceUnavailableError(
                "Chat provider returned an invalid response."
            ) from exc

    async def get_shipment_info_response(
        self,
        shipment_id: str,
        db_session: Any,
    ) -> str:
        """
        Get an AI-generated shipment response.

        This method no longer fabricates shipment details. If no provider is
        configured, it raises a clear configuration error instead.
        """
        del db_session  # shipment lookup is not implemented in this service yet

        if not self.is_configured():
            raise ChatServiceUnavailableError(
                "Shipment AI responses are unavailable until OPENAI_API_KEY is configured."
            )

        return await self._call_chatgpt_api(
            messages=[
                {
                    "role": "system",
                    "content": self.system_prompts["customer_support"],
                },
                {
                    "role": "user",
                    "content": (
                        "A customer is asking for shipment details. "
                        f"Shipment reference: {shipment_id}. "
                        "If live shipment data is unavailable, say so clearly and "
                        "direct the customer to support."
                    ),
                },
            ]
        )

    async def analyze_sentiment(self, message: str) -> Dict[str, Any]:
        """
        Analyze sentiment of user message using a lightweight local heuristic.
        """
        try:
            negative_keywords = [
                "bad",
                "terrible",
                "worst",
                "angry",
                "frustrated",
                "delay",
                "late",
                "lost",
            ]
            positive_keywords = [
                "great",
                "excellent",
                "thank",
                "good",
                "happy",
                "fast",
                "perfect",
            ]
            urgent_keywords = [
                "urgent",
                "emergency",
                "asap",
                "immediately",
                "now",
                "lost",
                "stolen",
            ]

            message_lower = message.lower()

            negative_count = sum(
                1 for word in negative_keywords if word in message_lower
            )
            positive_count = sum(
                1 for word in positive_keywords if word in message_lower
            )
            urgent_count = sum(1 for word in urgent_keywords if word in message_lower)

            if negative_count > positive_count:
                sentiment = "negative"
                score = max(0.0, 1.0 - (negative_count * 0.2))
            elif positive_count > negative_count:
                sentiment = "positive"
                score = min(1.0, 0.7 + (positive_count * 0.1))
            else:
                sentiment = "neutral"
                score = 0.5

            if urgent_count > 0 or negative_count >= 3:
                urgency = "high"
            elif negative_count > 0:
                urgency = "medium"
            else:
                urgency = "low"

            return {
                "sentiment": sentiment,
                "score": score,
                "urgency": urgency,
                "needs_human_agent": urgency == "high"
                or (sentiment == "negative" and score < 0.3),
            }
        except Exception as exc:
            logger.error("Error analyzing sentiment: %s", exc)
            return {
                "sentiment": "neutral",
                "score": 0.5,
                "urgency": "low",
                "needs_human_agent": False,
            }

    def clear_conversation(self, conversation_id: str) -> None:
        """Clear conversation history."""
        if conversation_id in self.conversation_history:
            del self.conversation_history[conversation_id]

    def get_conversation_summary(self, conversation_id: str) -> Dict[str, Any]:
        """Get summary of conversation."""
        if conversation_id not in self.conversation_history:
            return {"exists": False}

        history = self.conversation_history[conversation_id]
        return {
            "exists": True,
            "message_count": len(history),
            "started_at": history[0]["timestamp"] if history else None,
            "last_message_at": history[-1]["timestamp"] if history else None,
            "messages": history,
        }


chatgpt_service = ChatGPTService()
