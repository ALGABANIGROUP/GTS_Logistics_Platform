from __future__ import annotations

from typing import Optional


def _normalize_prompt(body: Optional[str]) -> str:
    text = (body or "").strip()
    return text if text else "No email body provided."


def generate_reply(body: Optional[str]) -> str:
    text = _normalize_prompt(body)
    lowered = text.lower()

    if any(keyword in lowered for keyword in ("invoice", "payment", "refund", "billing")):
        return "Finance bot received your request. We will review the payment details and reply with the next step."
    if any(keyword in lowered for keyword in ("shipment", "load", "carrier", "dispatch", "freight")):
        return "Operations bot received your request. We will review the shipment details and follow up shortly."
    if any(keyword in lowered for keyword in ("contract", "legal", "compliance", "policy")):
        return "Legal bot received your request. We will review the document and respond with guidance."
    if any(keyword in lowered for keyword in ("safety", "incident", "risk", "accident")):
        return "Safety bot received your request. We will review the incident details and respond shortly."

    return f"Auto-reply received: {text[:240]}"


__all__ = ["generate_reply"]
