from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from backend.services.chatgpt_service import ChatServiceUnavailableError, chatgpt_service

logger = logging.getLogger(__name__)

try:
    from textblob import TextBlob  # type: ignore
except Exception:
    TextBlob = None  # type: ignore

try:
    from transformers import pipeline  # type: ignore
except Exception:
    pipeline = None  # type: ignore


class CallSentimentAnalyzer:
    def __init__(self) -> None:
        self.model_loaded = False
        self.sentiment_pipeline: Any = None
        self.emotion_pipeline: Any = None

    async def load_models(self) -> bool:
        if self.model_loaded:
            return True
        if pipeline is None:
            logger.warning("transformers not installed; using fallback call sentiment analysis")
            return False
        try:
            loop = asyncio.get_running_loop()
            self.sentiment_pipeline = await loop.run_in_executor(
                None,
                lambda: pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english"),
            )
            try:
                self.emotion_pipeline = await loop.run_in_executor(
                    None,
                    lambda: pipeline("text-classification", model="j-hartmann/emotion-english-distilroberta-base"),
                )
            except Exception as exc:
                logger.warning("Emotion model unavailable: %s", exc)
                self.emotion_pipeline = None
            self.model_loaded = True
            logger.info("Call sentiment models loaded")
            return True
        except Exception as exc:
            logger.warning("Failed to load call sentiment models: %s", exc)
            return False

    async def analyze_transcript(self, transcript: str, speaker_labels: Optional[List[str]] = None) -> Dict[str, Any]:
        await self.load_models()
        segments = self._split_transcript(transcript)
        segment_results = [await self._analyze_segment(segment) for segment in segments]
        overall = await self._analyze_overall(transcript)
        speaker_sentiment: Dict[str, List[Dict[str, Any]]] = {}
        if speaker_labels and len(speaker_labels) == len(segment_results):
            for speaker, result in zip(speaker_labels, segment_results):
                speaker_sentiment.setdefault(speaker, []).append(result)
        return {
            "overall": overall,
            "segments": segment_results,
            "speaker_sentiment": speaker_sentiment,
            "timeline": self._generate_timeline(segment_results),
            "summary": await self._generate_summary(transcript, overall),
        }

    async def _analyze_segment(self, text: str) -> Dict[str, Any]:
        sentiment_result = await self._get_sentiment(text)
        emotion_result = await self._get_emotion(text)
        polarity = 0.0
        subjectivity = 0.0
        if TextBlob is not None:
            blob = TextBlob(text)
            polarity = float(blob.sentiment.polarity)
            subjectivity = float(blob.sentiment.subjectivity)
        return {
            "text": text[:200] + ("..." if len(text) > 200 else ""),
            "sentiment": sentiment_result,
            "emotion": emotion_result,
            "polarity": polarity,
            "subjectivity": subjectivity,
            "length": len(text),
        }

    async def _get_sentiment(self, text: str) -> Dict[str, Any]:
        if self.sentiment_pipeline is not None:
            try:
                loop = asyncio.get_running_loop()
                result = await loop.run_in_executor(None, lambda: self.sentiment_pipeline(text[:512])[0])
                label = str(result.get("label", "neutral")).lower()
                score = float(result.get("score", 0.5))
                sentiment = "neutral"
                if "pos" in label or label == "5 stars" or label == "4 stars":
                    sentiment = "positive"
                elif "neg" in label or label == "1 star" or label == "2 stars":
                    sentiment = "negative"
                return {"sentiment": sentiment, "score": score, "confidence": score}
            except Exception as exc:
                logger.debug("Transformer sentiment fallback triggered: %s", exc)
        return self._fallback_sentiment(text)

    async def _get_emotion(self, text: str) -> Dict[str, Any]:
        if self.emotion_pipeline is not None:
            try:
                loop = asyncio.get_running_loop()
                result = await loop.run_in_executor(None, lambda: self.emotion_pipeline(text[:512])[0])
                return {"emotion": result.get("label", "neutral"), "score": float(result.get("score", 0.5))}
            except Exception as exc:
                logger.debug("Emotion model fallback triggered: %s", exc)
        return {"emotion": "neutral", "score": 0.5}

    async def _analyze_overall(self, transcript: str) -> Dict[str, Any]:
        if not transcript.strip():
            return self._fallback_overall(transcript)
        try:
            response = await chatgpt_service.chat(
                user_message=(
                    "Return compact JSON only with keys: overall_sentiment, customer_satisfaction, urgency_level, "
                    "key_issues, resolution_status, needs_followup, followup_reason, agent_performance.\n\n"
                    f"Transcript:\n{transcript[:2000]}"
                ),
                conversation_id=f"call_overall_{datetime.utcnow().timestamp()}",
            )
            return self._coerce_json(response.get("response", ""))
        except ChatServiceUnavailableError:
            return self._fallback_overall(transcript)
        except Exception as exc:
            logger.warning("Overall call analysis failed: %s", exc)
            return self._fallback_overall(transcript)

    async def _generate_summary(self, transcript: str, analysis: Dict[str, Any]) -> str:
        if not transcript.strip():
            return "No transcript available."
        try:
            response = await chatgpt_service.chat(
                user_message=(
                    "Summarize this call in 2-3 sentences. Focus on issue, resolution, and next steps.\n\n"
                    f"{transcript[:1000]}"
                ),
                conversation_id=f"call_summary_{datetime.utcnow().timestamp()}",
            )
            return str(response.get("response") or "").strip() or self._fallback_summary(transcript, analysis)
        except Exception:
            return self._fallback_summary(transcript, analysis)

    def _split_transcript(self, transcript: str, max_length: int = 500) -> List[str]:
        words = transcript.split()
        segments: List[str] = []
        current: List[str] = []
        current_len = 0
        for word in words:
            current_len += len(word) + 1
            if current_len > max_length and current:
                segments.append(" ".join(current))
                current = [word]
                current_len = len(word)
            else:
                current.append(word)
        if current:
            segments.append(" ".join(current))
        return segments or [transcript]

    def _generate_timeline(self, segments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return [
            {
                "time": idx * 30,
                "sentiment": segment["sentiment"]["sentiment"],
                "score": segment["sentiment"]["score"],
                "emotion": segment["emotion"]["emotion"],
            }
            for idx, segment in enumerate(segments)
        ]

    def _coerce_json(self, text: str) -> Dict[str, Any]:
        raw = text.strip()
        if raw.startswith("```"):
            raw = raw.strip("`")
            raw = raw.split("\n", 1)[1] if "\n" in raw else raw
        try:
            value = json.loads(raw)
            return value if isinstance(value, dict) else self._fallback_overall(raw)
        except Exception:
            return self._fallback_overall(raw)

    def _fallback_sentiment(self, text: str) -> Dict[str, Any]:
        lowered = text.lower()
        positive_terms = ["thanks", "great", "good", "resolved", "perfect"]
        negative_terms = ["angry", "late", "delay", "problem", "issue", "complaint"]
        pos = sum(1 for term in positive_terms if term in lowered)
        neg = sum(1 for term in negative_terms if term in lowered)
        if TextBlob is not None:
            polarity = float(TextBlob(text).sentiment.polarity)
        else:
            polarity = 0.25 if pos > neg else -0.25 if neg > pos else 0.0
        if polarity > 0.1:
            sentiment = "positive"
        elif polarity < -0.1:
            sentiment = "negative"
        else:
            sentiment = "neutral"
        return {"sentiment": sentiment, "score": abs(polarity), "confidence": 0.65}

    def _fallback_overall(self, transcript: str) -> Dict[str, Any]:
        segment = self._fallback_sentiment(transcript)
        return {
            "overall_sentiment": segment["sentiment"],
            "customer_satisfaction": 75 if segment["sentiment"] == "positive" else 35 if segment["sentiment"] == "negative" else 55,
            "urgency_level": "high" if "urgent" in transcript.lower() or "asap" in transcript.lower() else "medium",
            "key_issues": [],
            "resolution_status": "unknown",
            "needs_followup": segment["sentiment"] == "negative",
            "followup_reason": "Negative tone detected" if segment["sentiment"] == "negative" else "",
            "agent_performance": "average",
        }

    def _fallback_summary(self, transcript: str, analysis: Dict[str, Any]) -> str:
        snippet = " ".join(transcript.split())[:220]
        return f"Call sentiment is {analysis.get('overall_sentiment', 'unknown')}. Summary: {snippet}"


sentiment_analyzer = CallSentimentAnalyzer()
