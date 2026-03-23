from __future__ import annotations

import asyncio
import json
import logging
import os
import uuid
from datetime import datetime, timedelta
from typing import Any, Awaitable, Callable, Dict, List, Optional

from pydantic import BaseModel, Field

from backend.ai.speech_service import speech_service
from backend.config import settings
from backend.services.ai_calls_store import list_recent_calls, record_call, record_event
from backend.services.chatgpt_service import ChatServiceUnavailableError, chatgpt_service
from backend.services.notification_service import notification_service
from backend.services.quo_api import get_quo_client

logger = logging.getLogger(__name__)

try:
    from redis.asyncio import Redis  # type: ignore
except Exception:  # pragma: no cover
    Redis = None  # type: ignore


class CallContext(BaseModel):
    call_id: str
    provider_call_id: Optional[str] = None
    from_number: str
    to_number: str
    bot_name: str
    purpose: str
    started_at: datetime
    ended_at: Optional[datetime] = None
    duration: Optional[int] = None
    status: str = "initiated"
    transcript: Optional[str] = None
    summary: Optional[str] = None
    sentiment: Optional[Dict[str, Any]] = None
    recording_url: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class QuoServiceEnhanced:
    """Enhanced wrapper around the existing Quo client with context, caching, and analysis."""

    def __init__(self) -> None:
        self.client = get_quo_client()
        self.call_contexts: Dict[str, CallContext] = {}
        self.webhook_handlers: Dict[str, List[Callable[[Dict[str, Any]], Awaitable[None]]]] = {}
        self._cache: Dict[str, tuple[datetime, str]] = {}
        self.redis = self._build_redis_client()

    def _build_redis_client(self) -> Optional[Any]:
        if Redis is None:
            return None
        try:
            redis_url = settings.REDIS_URL or os.getenv("REDIS_URL", "").strip()
            if redis_url:
                return Redis.from_url(redis_url, decode_responses=True)
            return Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                decode_responses=True,
            )
        except Exception as exc:
            logger.warning("Redis client setup failed, falling back to memory cache: %s", exc)
            return None

    async def _cache_set(self, key: str, value: Dict[str, Any], ttl_seconds: int) -> None:
        serialized = json.dumps(value, default=str)
        if self.redis is not None:
            try:
                await self.redis.setex(key, ttl_seconds, serialized)
                return
            except Exception as exc:
                logger.warning("Redis write failed for %s: %s", key, exc)
        self._cache[key] = (datetime.utcnow() + timedelta(seconds=ttl_seconds), serialized)

    async def _cache_get(self, key: str) -> Optional[Dict[str, Any]]:
        if self.redis is not None:
            try:
                value = await self.redis.get(key)
                return json.loads(value) if value else None
            except Exception as exc:
                logger.warning("Redis read failed for %s: %s", key, exc)
        item = self._cache.get(key)
        if not item:
            return None
        expires_at, serialized = item
        if expires_at < datetime.utcnow():
            self._cache.pop(key, None)
            return None
        return json.loads(serialized)

    async def make_smart_call(
        self,
        *,
        to: str,
        bot_name: str,
        purpose: str,
        context: Optional[Dict[str, Any]] = None,
        from_number: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        caller = from_number or self._get_bot_number(bot_name)
        result = await self.client.make_outbound_call(
            from_number=caller,
            to_number=to,
            user_id=user_id,
            call_flow={"type": "ai_assisted", "bot": bot_name, "purpose": purpose},
        )
        if "error" in result:
            return {"success": False, "error": result["error"], "provider": result}

        call_id = str(result.get("id") or result.get("callId") or f"call_{uuid.uuid4().hex[:12]}")
        model = CallContext(
            call_id=call_id,
            provider_call_id=str(result.get("id") or result.get("callId") or call_id),
            from_number=caller,
            to_number=to,
            bot_name=bot_name,
            purpose=purpose,
            started_at=datetime.utcnow(),
            metadata=context or {},
        )
        self.call_contexts[call_id] = model

        await self._cache_set(
            f"call_context:{call_id}",
            {
                "call_id": call_id,
                "provider_call_id": model.provider_call_id,
                "bot_name": bot_name,
                "purpose": purpose,
                "from_number": caller,
                "to_number": to,
                "metadata": context or {},
                "started_at": model.started_at.isoformat(),
            },
            ttl_seconds=3600,
        )
        await record_call(
            call_id=call_id,
            direction="outbound",
            from_number=caller,
            to_number=to,
            status="initiated",
            bot_name=bot_name,
            purpose=purpose,
            provider="quo",
            metadata=context or {},
            last_event="initiated",
        )
        await record_event(call_id=call_id, event_type="initiated", payload={"provider": result, "context": context or {}})
        await self._notify_call_event(
            bot_name=bot_name,
            template_key="system_alert",
            context={
                "user_name": "Call Operations",
                "message": f"Call initiated to {to} for {purpose}. Call ID: {call_id}",
            },
        )
        return {"success": True, "call_id": call_id, "provider": result}

    async def handle_call_webhook(self, call_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        context_data = await self._cache_get(f"call_context:{call_id}") or {}
        event = str(payload.get("event") or payload.get("type") or payload.get("status") or "call.event")
        status = str(payload.get("status") or event)
        await record_event(call_id=call_id, event_type=event, payload=payload)

        ctx = self.call_contexts.get(call_id)
        if ctx:
            ctx.status = status
            ctx.duration = payload.get("duration") or ctx.duration
            ctx.recording_url = payload.get("recording_url") or payload.get("recordingUrl") or ctx.recording_url
            if status in {"completed", "failed", "canceled", "no_answer"}:
                ctx.ended_at = datetime.utcnow()
        await record_call(
            call_id=call_id,
            direction=str(payload.get("direction") or context_data.get("direction") or "outbound"),
            from_number=payload.get("from") or context_data.get("from_number"),
            to_number=payload.get("to") or context_data.get("to_number"),
            status=status,
            bot_name=context_data.get("bot_name"),
            purpose=context_data.get("purpose"),
            provider="quo",
            metadata=payload,
            last_event=event,
        )

        if event in {"call.completed", "completed"}:
            await self._handle_call_completed(call_id, context_data, payload)
        elif event in {"call.recording.ready", "recording.ready"}:
            await self._handle_recording_ready(call_id, context_data, payload)
        elif event in {"call.transcript.ready", "transcript.ready"}:
            await self._handle_transcript_ready(call_id, context_data, payload)
        elif event in {"call.answered", "answered"}:
            await self._handle_call_answered(call_id, context_data, payload)

        for handler in self.webhook_handlers.get(call_id, []):
            try:
                await handler(payload)
            except Exception as exc:
                logger.warning("Custom call webhook handler failed for %s: %s", call_id, exc)
        return {"status": "processed", "call_id": call_id, "event": event}

    async def _handle_call_answered(self, call_id: str, context_data: Dict[str, Any], payload: Dict[str, Any]) -> None:
        updated = {**context_data, "answered_at": datetime.utcnow().isoformat(), "answer_payload": payload}
        await self._cache_set(f"call_context:{call_id}", updated, ttl_seconds=3600)

    async def _handle_call_completed(self, call_id: str, context_data: Dict[str, Any], payload: Dict[str, Any]) -> None:
        duration = int(payload.get("duration") or 0)
        bot_name = str(context_data.get("bot_name") or "operations_manager")
        purpose = str(context_data.get("purpose") or "call")
        await self._notify_call_event(
            bot_name=bot_name,
            template_key="system_alert",
            context={
                "user_name": "Call Operations",
                "message": f"Call {call_id} completed. Duration: {duration}s. Purpose: {purpose}.",
            },
        )

    async def _handle_recording_ready(self, call_id: str, context_data: Dict[str, Any], payload: Dict[str, Any]) -> None:
        url = str(payload.get("url") or payload.get("recording_url") or payload.get("recordingUrl") or "")
        if not url:
            return
        if call_id in self.call_contexts:
            self.call_contexts[call_id].recording_url = url
        await self._cache_set(
            f"call_recording:{call_id}",
            {"recording_url": url, "context": context_data},
            ttl_seconds=86400,
        )

    async def _handle_transcript_ready(self, call_id: str, context_data: Dict[str, Any], payload: Dict[str, Any]) -> None:
        transcript = str(payload.get("transcript") or "").strip()
        if not transcript:
            recording_url = str(payload.get("recording_url") or payload.get("url") or "")
            if recording_url:
                stt_result = await speech_service.transcribe(recording_url)
                transcript = str(stt_result.get("text") or "").strip()

        sentiment = await self.analyze_call_sentiment(transcript) if transcript else {}
        summary = await self.summarize_call(transcript, str(context_data.get("purpose") or "")) if transcript else "No transcript available."

        if call_id in self.call_contexts:
            self.call_contexts[call_id].transcript = transcript
            self.call_contexts[call_id].sentiment = sentiment
            self.call_contexts[call_id].summary = summary

        analysis_payload = {
            "transcript": transcript,
            "summary": summary,
            "sentiment": sentiment,
        }
        await self._cache_set(f"call_analysis:{call_id}", analysis_payload, ttl_seconds=86400)
        await record_event(call_id=call_id, event_type="analysis.ready", payload=analysis_payload)

        bot_name = str(context_data.get("bot_name") or "operations_manager")
        await self._notify_call_event(
            bot_name=bot_name,
            template_key="system_alert",
            context={
                "user_name": "Call Operations",
                "message": (
                    f"Call analysis ready for {call_id}. "
                    f"Sentiment: {sentiment.get('overall_sentiment', 'unknown')}. "
                    f"Summary: {summary}"
                ),
            },
        )

    async def analyze_call_sentiment(self, transcript: str) -> Dict[str, Any]:
        if not transcript.strip():
            return {"overall_sentiment": "neutral", "urgency": "low", "needs_human_followup": False}
        try:
            response = await chatgpt_service.chat(
                user_message=(
                    "Return compact JSON only with keys: overall_sentiment, urgency, "
                    "satisfaction_score, keywords, needs_human_followup.\n\n"
                    f"Transcript:\n{transcript[:2000]}"
                ),
                conversation_id=f"call_sentiment_{uuid.uuid4().hex[:8]}",
            )
            return self._coerce_json_text(response.get("response", ""))
        except ChatServiceUnavailableError:
            return self._fallback_sentiment(transcript)
        except Exception as exc:
            logger.warning("Call sentiment analysis failed: %s", exc)
            return self._fallback_sentiment(transcript)

    async def summarize_call(self, transcript: str, purpose: str) -> str:
        if not transcript.strip():
            return "No transcript available."
        try:
            response = await chatgpt_service.chat(
                user_message=f"Summarize this call in 2 sentences. Purpose: {purpose}\n\n{transcript[:2000]}",
                conversation_id=f"call_summary_{uuid.uuid4().hex[:8]}",
            )
            return str(response.get("response") or "").strip() or "Summary not available."
        except ChatServiceUnavailableError:
            return self._fallback_summary(transcript, purpose)
        except Exception as exc:
            logger.warning("Call summary generation failed: %s", exc)
            return self._fallback_summary(transcript, purpose)

    async def get_call_history(self, bot_name: Optional[str] = None, days: int = 7) -> List[Dict[str, Any]]:
        rows = await list_recent_calls(limit=max(50, days * 25))
        cutoff = datetime.utcnow() - timedelta(days=days)
        result: List[Dict[str, Any]] = []
        for row in rows:
            updated_at = row.get("updated_at")
            try:
                updated_dt = datetime.fromisoformat(str(updated_at).replace("Z", "+00:00")) if updated_at else datetime.utcnow()
            except Exception:
                updated_dt = datetime.utcnow()
            if updated_dt < cutoff:
                continue
            if bot_name and row.get("bot_name") != bot_name:
                continue
            analysis = await self._cache_get(f"call_analysis:{row['call_id']}") or {}
            result.append({**row, **analysis})
        return result

    async def get_call_transcript(self, call_id: str) -> Optional[str]:
        analysis = await self._cache_get(f"call_analysis:{call_id}")
        if analysis:
            return analysis.get("transcript")
        context = self.call_contexts.get(call_id)
        return context.transcript if context else None

    async def register_webhook_handler(
        self,
        call_id: str,
        handler: Callable[[Dict[str, Any]], Awaitable[None]],
    ) -> None:
        self.webhook_handlers.setdefault(call_id, []).append(handler)

    def _get_bot_number(self, bot_name: str) -> str:
        bot_numbers = {
            "customer_service": "+12345678901",
            "freight_broker": "+12345678902",
            "finance_bot": "+12345678903",
            "safety_manager": "+12345678904",
            "security_manager": "+12345678905",
            "operations_manager": "+12345678906",
            "general_manager": "+12345678907",
            "support": "+12345678908",
        }
        return bot_numbers.get(bot_name, settings.DEFAULT_CALLER_ID or "+12345678900")

    async def _notify_call_event(self, *, bot_name: str, template_key: str, context: Dict[str, Any]) -> None:
        try:
            await notification_service.send_bot_notification(
                bot_name=bot_name,
                template_key=template_key,
                context={
                    "user_email": settings.ADMIN_EMAIL or settings.SUPPORT_EMAIL or settings.SMTP_FROM,
                    **context,
                },
            )
        except Exception as exc:
            logger.warning("Call notification failed for %s: %s", bot_name, exc)

    def _coerce_json_text(self, text: str) -> Dict[str, Any]:
        raw = text.strip()
        if raw.startswith("```"):
            raw = raw.strip("`")
            raw = raw.split("\n", 1)[1] if "\n" in raw else raw
        try:
            value = json.loads(raw)
            return value if isinstance(value, dict) else {}
        except Exception:
            return self._fallback_sentiment(text)

    def _fallback_sentiment(self, transcript: str) -> Dict[str, Any]:
        lowered = transcript.lower()
        negative_terms = ["angry", "late", "delay", "issue", "problem", "complaint"]
        positive_terms = ["thanks", "great", "good", "resolved", "perfect"]
        negative_hits = sum(1 for term in negative_terms if term in lowered)
        positive_hits = sum(1 for term in positive_terms if term in lowered)
        if negative_hits > positive_hits:
            sentiment = "negative"
        elif positive_hits > negative_hits:
            sentiment = "positive"
        else:
            sentiment = "neutral"
        return {
            "overall_sentiment": sentiment,
            "urgency": "high" if "urgent" in lowered or "asap" in lowered else "medium",
            "satisfaction_score": 30 if sentiment == "negative" else 75 if sentiment == "positive" else 55,
            "keywords": [term for term in negative_terms + positive_terms if term in lowered][:8],
            "needs_human_followup": sentiment == "negative",
        }

    def _fallback_summary(self, transcript: str, purpose: str) -> str:
        snippet = " ".join(transcript.split())[:220]
        return f"Call purpose: {purpose or 'general inquiry'}. Transcript summary: {snippet}".strip()


quo_service = QuoServiceEnhanced()
