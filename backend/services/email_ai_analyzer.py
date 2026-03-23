from __future__ import annotations

import json
import logging
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.email_center import EmailMessage
from backend.services.chatgpt_service import (
    ChatGPTService,
    ChatServiceUnavailableError,
    chatgpt_service,
)


logger = logging.getLogger(__name__)


class EmailAIAnalyzer:
    """Analyze email content using AI when available, otherwise local heuristics."""

    CATEGORY_KEYWORDS = {
        "billing": ["invoice", "payment", "billing", "refund", "overdue", "receipt"],
        "support": ["help", "support", "issue", "problem", "error", "unable"],
        "operations": ["shipment", "dispatch", "pickup", "delivery", "route", "driver"],
        "sales": ["quote", "pricing", "proposal", "rate", "contract", "deal"],
        "legal": ["legal", "agreement", "terms", "compliance", "claim", "liability"],
    }

    POSITIVE_KEYWORDS = [
        "thanks",
        "thank you",
        "great",
        "excellent",
        "happy",
        "appreciate",
        "good",
        "resolved",
    ]
    NEGATIVE_KEYWORDS = [
        "urgent",
        "complaint",
        "issue",
        "problem",
        "delay",
        "late",
        "unacceptable",
        "angry",
        "frustrated",
        "failed",
        "overdue",
        "missing",
    ]
    HIGH_URGENCY_KEYWORDS = [
        "urgent",
        "asap",
        "immediately",
        "today",
        "now",
        "critical",
        "overdue",
    ]

    def __init__(
        self,
        db: AsyncSession,
        chat_service: Optional[ChatGPTService] = None,
    ):
        self.db = db
        self.chat_service = chat_service or chatgpt_service

    async def analyze_message(self, message_id: int) -> Dict[str, Any]:
        message = await self.db.get(EmailMessage, message_id)
        if not message:
            raise ValueError(f"Message {message_id} not found")

        fallback_result = self._build_fallback_analysis(message)
        result = fallback_result

        if self.chat_service.is_configured():
            try:
                ai_result = await self._analyze_with_chatgpt(message)
                result = self._merge_analysis_results(fallback_result, ai_result)
            except ChatServiceUnavailableError:
                logger.warning(
                    "Email AI analysis provider unavailable for message %s; falling back to local heuristics.",
                    message_id,
                )
            except Exception:
                logger.exception(
                    "Unexpected AI analysis failure for message %s; falling back to local heuristics.",
                    message_id,
                )

        analyzed_at = datetime.now(timezone.utc)
        result["analyzed_at"] = analyzed_at.isoformat()
        message.analyzed_at = analyzed_at
        message.analysis_result = result
        await self.db.commit()
        return result

    async def _analyze_with_chatgpt(self, message: EmailMessage) -> Dict[str, Any]:
        content = self._compose_message_content(message)
        prompt = (
            "Analyze the following email and return strict JSON only. "
            "Use this schema: "
            "{"
            '"version":"1.0",'
            '"method":"chatgpt",'
            '"keywords":["string"],'
            '"sentiment":{"label":"positive|neutral|negative","score":0.0,"urgency":"low|medium|high"},'
            '"category":"billing|support|operations|sales|legal|general",'
            '"language":"en",'
            '"summary":"string",'
            '"confidence":0.0,'
            '"entities":{"invoice_numbers":["string"],"amounts":[0],"dates":["YYYY-MM-DD"]}'
            "}. "
            "Do not include markdown fences.\n\n"
            f"Email content:\n{content}"
        )
        response = await self.chat_service.chat(
            user_message=prompt,
            conversation_id=f"email-analysis-{message.id}",
            user_context={
                "email_message_id": message.id,
                "mailbox_id": message.mailbox_id,
            },
            conversation_type="customer_support",
        )
        parsed = self._parse_chatgpt_response(response.get("response", ""))
        parsed["method"] = "chatgpt"
        return parsed

    def _build_fallback_analysis(self, message: EmailMessage) -> Dict[str, Any]:
        keywords = self._extract_keywords(message)
        sentiment = self._detect_sentiment_and_urgency(message)
        category = self._detect_category(message, keywords)
        language = self._detect_language(message)
        entities = self._extract_entities(message)
        summary = self._summarize_fallback(message, category, sentiment["urgency"])
        confidence = self._estimate_fallback_confidence(keywords, category, sentiment)

        return {
            "version": "1.0",
            "method": "fallback",
            "keywords": keywords,
            "sentiment": sentiment,
            "category": category,
            "language": language,
            "summary": summary,
            "confidence": confidence,
            "entities": entities,
        }

    def _compose_message_content(self, message: EmailMessage) -> str:
        recipients = ", ".join((message.to_addrs or []) + (message.cc_addrs or []))
        return "\n".join(
            [
                f"From: {message.from_addr or ''}",
                f"To: {recipients}",
                f"Subject: {message.subject or ''}",
                "",
                message.body_preview or "",
            ]
        ).strip()

    def _extract_keywords(self, message: EmailMessage) -> List[str]:
        text = self._combined_text(message).lower()
        tokens = re.findall(r"\b[a-z0-9][a-z0-9_-]{2,}\b", text)
        stop_words = {
            "the",
            "and",
            "for",
            "with",
            "that",
            "this",
            "from",
            "have",
            "your",
            "about",
            "please",
            "hello",
            "regards",
            "thanks",
            "thank",
            "team",
        }
        seen: set[str] = set()
        keywords: List[str] = []
        for token in tokens:
            if token in stop_words or token in seen:
                continue
            if token.isdigit():
                continue
            seen.add(token)
            keywords.append(token)
            if len(keywords) >= 10:
                break
        return keywords

    def _detect_sentiment_and_urgency(self, message: EmailMessage) -> Dict[str, Any]:
        text = self._combined_text(message).lower()
        positive_hits = sum(1 for word in self.POSITIVE_KEYWORDS if word in text)
        negative_hits = sum(1 for word in self.NEGATIVE_KEYWORDS if word in text)
        urgency_hits = sum(1 for word in self.HIGH_URGENCY_KEYWORDS if word in text)

        if negative_hits > positive_hits:
            label = "negative"
            score = min(0.95, 0.55 + (negative_hits * 0.1))
        elif positive_hits > negative_hits:
            label = "positive"
            score = min(0.95, 0.55 + (positive_hits * 0.08))
        else:
            label = "neutral"
            score = 0.5

        if urgency_hits > 0 or negative_hits >= 2:
            urgency = "high"
        elif negative_hits == 1 or "soon" in text:
            urgency = "medium"
        else:
            urgency = "low"

        return {
            "label": label,
            "score": round(score, 2),
            "urgency": urgency,
        }

    def _detect_category(self, message: EmailMessage, keywords: List[str]) -> str:
        text = self._combined_text(message).lower()
        best_category = "general"
        best_score = 0

        for category, terms in self.CATEGORY_KEYWORDS.items():
            score = sum(1 for term in terms if term in text or term in keywords)
            if score > best_score:
                best_category = category
                best_score = score

        return best_category

    def _detect_language(self, message: EmailMessage) -> str:
        text = self._combined_text(message)
        if re.search(r"[\u0600-\u06FF]", text):
            return "ar"
        return "en"

    def _extract_entities(self, message: EmailMessage) -> Dict[str, Any]:
        text = self._combined_text(message)

        invoice_numbers = sorted(
            {
                match.group(0)
                for match in re.finditer(
                    r"\b(?:INV|INVOICE|BILL)(?:[-_ ]?\d+)+\b",
                    text,
                    re.IGNORECASE,
                )
            }
        )
        amounts = [
            float(match.group(1).replace(",", ""))
            for match in re.finditer(r"(?:\$|USD\s?|CAD\s?)(\d[\d,]*(?:\.\d+)?)", text, re.IGNORECASE)
        ]
        dates = sorted(
            {
                match.group(0)
                for match in re.finditer(r"\b\d{4}-\d{2}-\d{2}\b", text)
            }
        )

        normalized_amounts: List[int | float] = []
        for amount in amounts:
            normalized_amounts.append(int(amount) if amount.is_integer() else amount)

        return {
            "invoice_numbers": invoice_numbers,
            "amounts": normalized_amounts,
            "dates": dates,
        }

    def _summarize_fallback(self, message: EmailMessage, category: str, urgency: str) -> str:
        subject = (message.subject or "").strip()
        sender = (message.from_addr or "unknown sender").strip()
        if subject:
            return f"Email from {sender} about {category}: {subject} ({urgency} urgency)"
        return f"Email from {sender} categorized as {category} with {urgency} urgency"

    def _estimate_fallback_confidence(
        self,
        keywords: List[str],
        category: str,
        sentiment: Dict[str, Any],
    ) -> float:
        score = 0.35
        if keywords:
            score += min(0.2, len(keywords) * 0.02)
        if category != "general":
            score += 0.2
        if sentiment.get("urgency") == "high":
            score += 0.1
        if sentiment.get("label") != "neutral":
            score += 0.1
        return round(min(score, 0.75), 2)

    def _parse_chatgpt_response(self, raw_response: str) -> Dict[str, Any]:
        cleaned = raw_response.strip()
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", cleaned, flags=re.DOTALL)
        parsed = json.loads(cleaned)
        if not isinstance(parsed, dict):
            raise ChatServiceUnavailableError("Chat analysis did not return an object.")
        return parsed

    def _merge_analysis_results(
        self,
        fallback_result: Dict[str, Any],
        ai_result: Dict[str, Any],
    ) -> Dict[str, Any]:
        sentiment = ai_result.get("sentiment")
        entities = ai_result.get("entities")

        result = dict(fallback_result)
        result.update(
            {
                "version": str(ai_result.get("version") or fallback_result["version"]),
                "method": "chatgpt",
                "keywords": ai_result.get("keywords") or fallback_result["keywords"],
                "category": ai_result.get("category") or fallback_result["category"],
                "language": ai_result.get("language") or fallback_result["language"],
                "summary": ai_result.get("summary") or fallback_result["summary"],
                "confidence": self._normalize_confidence(
                    ai_result.get("confidence"), fallback_result["confidence"]
                ),
            }
        )
        result["sentiment"] = sentiment if isinstance(sentiment, dict) else fallback_result["sentiment"]
        result["entities"] = entities if isinstance(entities, dict) else fallback_result["entities"]
        return result

    def _normalize_confidence(self, value: Any, default: float) -> float:
        try:
            return round(max(0.0, min(float(value), 1.0)), 2)
        except (TypeError, ValueError):
            return default

    def _combined_text(self, message: EmailMessage) -> str:
        parts = [
            message.subject or "",
            message.body_preview or "",
            message.from_addr or "",
            " ".join(message.to_addrs or []),
            " ".join(message.cc_addrs or []),
        ]
        return " ".join(part for part in parts if part).strip()
