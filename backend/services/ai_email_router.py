# backend/services/ai_email_router.py
from __future__ import annotations

from typing import Any, Dict, List

import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

try:
    from openai.types.chat import ChatCompletionMessageParam
except Exception:
    # Fallback type if OpenAI types are not available at type-check time
    ChatCompletionMessageParam = Dict[str, Any]  # type: ignore[misc]

# Safe OpenAI client accessor
try:
    from backend.ai.openai_safe_client import get_openai_client as _real_get_openai_client  # type: ignore[import]
except Exception:
    _real_get_openai_client = None  # type: ignore[assignment]


def get_openai_client() -> Any:
    """
    Safe wrapper around the real OpenAI client factory.

    Returns:
        - AsyncOpenAI instance if configured
        - None otherwise

    Typed as Any to keep static analysis (Pylance) simple.
    """
    if _real_get_openai_client is None:
        return None
    try:
        return _real_get_openai_client()
    except Exception:
        return None


OPENAI_ENABLED = os.getenv("OPENAI_ENABLED", "0").lower() in ("1", "true", "yes", "on")
EXTERNAL_APIS_ENABLED = os.getenv("EXTERNAL_APIS_ENABLED", "0").lower() in (
    "1",
    "true",
    "yes",
    "on",
)

router = APIRouter(prefix="/ai/email", tags=["AI Email Router"])


class EmailPayload(BaseModel):
    """
    Basic email payload for routing.
    """

    subject: str
    body: str


class EmailRoutingResult(BaseModel):
    """
    AI routing decision.
    """

    category: str
    subcategory: str | None = None
    suggested_assignee: str | None = None
    priority: str | None = None
    raw_ai_answer: str | None = None


@router.post("/route", response_model=EmailRoutingResult)
async def route_email(payload: EmailPayload) -> EmailRoutingResult:
    """
    Route an inbound email (subject + body) to the right queue/agent using AI.

    If OpenAI is disabled, returns a simple rule-based fallback.
    """
    subject = payload.subject.strip()
    body = payload.body.strip()

    # Fallback logic if AI is disabled
    if not (OPENAI_ENABLED and EXTERNAL_APIS_ENABLED):
        category = "general"
        priority = "normal"

        lowered = (subject + " " + body).lower()
        if "invoice" in lowered or "billing" in lowered:
            category = "finance"
        elif "load" in lowered or "shipment" in lowered or "truck" in lowered:
            category = "operations"
        elif "complaint" in lowered or "problem" in lowered:
            category = "support"
            priority = "high"

        return EmailRoutingResult(
            category=category,
            subcategory=None,
            suggested_assignee=None,
            priority=priority,
            raw_ai_answer=None,
        )

    client = get_openai_client()
    if client is None:
        # Same fallback if client could not be created
        return EmailRoutingResult(
            category="general",
            subcategory=None,
            suggested_assignee=None,
            priority="normal",
            raw_ai_answer=None,
        )

    try:
        # Build messages with the precise OpenAI types
        messages: List[ChatCompletionMessageParam] = [
            {
                "role": "system",
                "content": (
                    "You are an AI email router for a trucking & logistics company (GTS Logistics). "
                    "Your job is to classify inbound emails into ROUTING FIELDS:\n"
                    "- category: one of [operations, finance, safety, hr, it, support, general]\n"
                    "- subcategory: a short label (for example: 'invoice-dispute', 'new-load-request', 'carrier-onboarding').\n"
                    "- suggested_assignee: either a role or a mailbox, such as 'operations@gabanilogistics.com', "
                    "'finance@gabanilogistics.com', 'safety officer', 'HR manager'.\n"
                    "- priority: one of [low, normal, high, urgent].\n\n"
                    "Return a short JSON-like answer in plain text. Do NOT include any extra explanation."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Email subject: {subject}\n\n"
                    f"Email body:\n{body}\n\n"
                    "Decide the routing fields now."
                ),
            },
        ]

        # Call OpenAI chat completions (Async)
        response = await client.chat.completions.create(  # type: ignore[call-arg]
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.2,
            max_tokens=300,
        )

        ai_text = ""
        if response and response.choices:
            ai_text = (response.choices[0].message.content or "").strip()

        # Very simple parsing: we try to detect fields via keywords
        # (You can later replace this with proper JSON parsing if you format the prompt strictly)
        lowered = ai_text.lower()
        category = "general"
        priority = "normal"

        if "operations" in lowered:
            category = "operations"
        elif "finance" in lowered:
            category = "finance"
        elif "safety" in lowered:
            category = "safety"
        elif "support" in lowered:
            category = "support"
        elif "hr" in lowered or "human resources" in lowered:
            category = "hr"
        elif "it" in lowered:
            category = "it"

        if "urgent" in lowered:
            priority = "urgent"
        elif "high" in lowered:
            priority = "high"
        elif "low" in lowered:
            priority = "low"

        suggested_assignee: str | None = None
        if "operations@" in lowered:
            suggested_assignee = "operations@gabanilogistics.com"
        elif "finance@" in lowered:
            suggested_assignee = "finance@gabanilogistics.com"
        elif "safety@" in lowered:
            suggested_assignee = "safety@gabanilogistics.com"

        # Subcategory is hard to parse reliably without stricter JSON, so we leave it None for now.
        return EmailRoutingResult(
            category=category,
            subcategory=None,
            suggested_assignee=suggested_assignee,
            priority=priority,
            raw_ai_answer=ai_text or None,
        )
    except Exception as e:
        # In case of any errors from OpenAI or network
        raise HTTPException(status_code=500, detail=f"AI email routing failed: {e}")
