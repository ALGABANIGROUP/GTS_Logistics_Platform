from __future__ import annotations

import asyncio
import json
import logging
import re
from datetime import datetime
from typing import Any, Dict, List

from backend.services.chatgpt_service import ChatServiceUnavailableError, chatgpt_service

logger = logging.getLogger(__name__)

try:
    import spacy  # type: ignore
    from spacy.matcher import Matcher  # type: ignore
except Exception:
    spacy = None  # type: ignore
    Matcher = None  # type: ignore


class CallInfoExtractor:
    def __init__(self) -> None:
        self.nlp: Any = None
        self.matcher: Any = None
        self.model_loaded = False

    async def load_model(self) -> bool:
        if self.model_loaded:
            return True
        if spacy is None or Matcher is None:
            logger.warning("spaCy not installed; using regex-based extraction")
            return False
        try:
            loop = asyncio.get_running_loop()
            try:
                self.nlp = await loop.run_in_executor(None, lambda: spacy.load("en_core_web_lg"))
            except Exception:
                self.nlp = await loop.run_in_executor(None, lambda: spacy.load("en_core_web_sm"))
            self.matcher = Matcher(self.nlp.vocab)
            self.matcher.add("SHIPMENT_ID", [[{"LOWER": {"IN": ["shipment", "load", "order"]}}, {"IS_PUNCT": True, "OP": "?"}, {"LIKE_NUM": True}]])
            self.matcher.add("INVOICE_ID", [[{"LOWER": {"IN": ["invoice", "bill", "inv"]}}, {"IS_PUNCT": True, "OP": "?"}, {"LIKE_NUM": True}]])
            self.matcher.add("AMOUNT", [[{"LOWER": {"IN": ["$", "usd", "cad", "dollar"]}}, {"LIKE_NUM": True}]])
            self.model_loaded = True
            logger.info("Call NER model loaded")
            return True
        except Exception as exc:
            logger.warning("Failed to load spaCy model, using regex extraction: %s", exc)
            return False

    async def extract_info(self, transcript: str) -> Dict[str, Any]:
        await self.load_model()
        entities = await self._extract_entities(transcript)
        enhanced = await self._enhance_extraction(transcript, entities)
        return {
            "entities": entities,
            "enhanced": enhanced,
            "summary": self._generate_extraction_summary(entities, enhanced),
        }

    async def _extract_entities(self, transcript: str) -> Dict[str, List[str]]:
        base = {
            "PERSON": [],
            "ORG": [],
            "GPE": [],
            "DATE": [],
            "TIME": [],
            "MONEY": [],
            "PHONE": [],
            "EMAIL": [],
            "SHIPMENT_ID": [],
            "INVOICE_ID": [],
            "AMOUNT": [],
            "TRACKING_NUMBER": [],
            "VEHICLE_PLATE": [],
        }
        base["PHONE"] = list(dict.fromkeys(re.findall(r"\+?\d[\d\s\-]{7,}\d", transcript)))
        base["EMAIL"] = list(dict.fromkeys(re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", transcript)))
        base["TRACKING_NUMBER"] = list(dict.fromkeys(re.findall(r"\b[A-Z]{2}\d{9}[A-Z]{2}\b", transcript)))
        base["VEHICLE_PLATE"] = list(dict.fromkeys(re.findall(r"\b[A-Z]{2,4}-\d{2,4}\b", transcript)))
        base["SHIPMENT_ID"] = list(dict.fromkeys(re.findall(r"\b(?:shipment|load|order)[\s#:.-]*(\d{3,})\b", transcript, flags=re.I)))
        base["INVOICE_ID"] = list(dict.fromkeys(re.findall(r"\b(?:invoice|bill|inv)[\s#:.-]*([A-Z0-9-]{3,})\b", transcript, flags=re.I)))
        base["AMOUNT"] = list(dict.fromkeys(re.findall(r"\b(?:USD|CAD|\$)\s?\d[\d,]*(?:\.\d{2})?\b", transcript, flags=re.I)))
        if self.model_loaded and self.nlp is not None:
            try:
                doc = self.nlp(transcript)
                for ent in doc.ents:
                    if ent.label_ in base and ent.text not in base[ent.label_]:
                        base[ent.label_].append(ent.text)
                if self.matcher is not None:
                    matches = self.matcher(doc)
                    for match_id, start, end in matches:
                        label = self.nlp.vocab.strings[match_id]
                        span = doc[start:end].text
                        if label in base and span not in base[label]:
                            base[label].append(span)
            except Exception as exc:
                logger.debug("spaCy entity extraction fallback triggered: %s", exc)
        return base

    async def _enhance_extraction(self, transcript: str, entities: Dict[str, Any]) -> Dict[str, Any]:
        if not transcript.strip():
            return {}
        try:
            response = await chatgpt_service.chat(
                user_message=(
                    "Return compact JSON only with keys: shipment_numbers, invoice_numbers, driver_names, "
                    "customer_names, locations, dates, amounts, action_items, urgency, summary.\n\n"
                    f"Transcript:\n{transcript[:1500]}"
                ),
                conversation_id=f"call_extract_{datetime.utcnow().timestamp()}",
            )
            return self._coerce_json(response.get("response", ""))
        except ChatServiceUnavailableError:
            return self._fallback_enhanced(entities)
        except Exception as exc:
            logger.warning("Enhanced call extraction failed: %s", exc)
            return self._fallback_enhanced(entities)

    def _generate_extraction_summary(self, entities: Dict[str, Any], enhanced: Dict[str, Any]) -> str:
        parts: List[str] = []
        if entities.get("SHIPMENT_ID"):
            parts.append(f"Shipments: {', '.join(entities['SHIPMENT_ID'])}")
        if entities.get("INVOICE_ID"):
            parts.append(f"Invoices: {', '.join(entities['INVOICE_ID'])}")
        amounts = entities.get("MONEY", []) + entities.get("AMOUNT", [])
        if amounts:
            parts.append(f"Amounts: {', '.join(amounts)}")
        if entities.get("PERSON"):
            parts.append(f"People: {', '.join(entities['PERSON'])}")
        if entities.get("GPE"):
            parts.append(f"Locations: {', '.join(entities['GPE'])}")
        actions = enhanced.get("action_items")
        if isinstance(actions, list) and actions:
            parts.append(f"Actions: {', '.join(actions)}")
        return " | ".join(parts) if parts else "No structured information extracted"

    def _coerce_json(self, text: str) -> Dict[str, Any]:
        raw = text.strip()
        if raw.startswith("```"):
            raw = raw.strip("`")
            raw = raw.split("\n", 1)[1] if "\n" in raw else raw
        try:
            value = json.loads(raw)
            return value if isinstance(value, dict) else {}
        except Exception:
            return {}

    def _fallback_enhanced(self, entities: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "shipment_numbers": entities.get("SHIPMENT_ID", []),
            "invoice_numbers": entities.get("INVOICE_ID", []),
            "driver_names": [],
            "customer_names": entities.get("PERSON", []),
            "locations": entities.get("GPE", []),
            "dates": entities.get("DATE", []),
            "amounts": entities.get("MONEY", []) + entities.get("AMOUNT", []),
            "action_items": [],
            "urgency": "medium",
            "summary": "Fallback extraction generated from regex and named entities.",
        }


info_extractor = CallInfoExtractor()
