from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class CustomerIntent:
    label: str
    confidence: float


class AICustomerService:
    """
    Lightweight customer service helper with deterministic analysis.
    The service stays dependency-free and is safe to run without external APIs.
    """

    POSITIVE_TOKENS = {
        "thanks", "thank", "great", "good", "excellent", "perfect", "resolved", "helpful",
        "merci", "bien", "parfait", "super",
    }
    NEGATIVE_TOKENS = {
        "bad", "terrible", "awful", "wrong", "angry", "upset", "broken", "delay", "delayed",
        "late", "hate", "not working", "problem",
        "mauvais", "retard", "probleme", "problème", "colere", "colère",
    }
    URGENT_TOKENS = {
        "urgent", "asap", "immediately", "emergency", "critical", "now",
        "urgentement", "immédiatement", "critique",
    }
    NEGOTIATION_TOKENS = {
        "price", "pricing", "discount", "offer", "cheaper", "quote", "cost",
        "prix", "remise", "offre", "tarif",
    }

    def detect_intent(self, message: str) -> CustomerIntent:
        text = (message or "").lower()

        if any(k in text for k in ["invoice", "billing", "paid", "payment", "charge", "refund"]):
            return CustomerIntent(label="billing", confidence=0.92)
        if any(k in text for k in ["tracking", "shipment", "load", "truck", "delivery", "pickup", "eta"]):
            return CustomerIntent(label="shipment", confidence=0.92)
        if any(k in text for k in ["login", "password", "portal", "error", "bug", "issue", "cannot access"]):
            return CustomerIntent(label="technical", confidence=0.9)
        if any(k in text for k in self.NEGOTIATION_TOKENS):
            return CustomerIntent(label="negotiation", confidence=0.82)
        if any(k in text for k in ["complaint", "angry", "unacceptable", "complain", "bad service"]):
            return CustomerIntent(label="complaint", confidence=0.84)
        if any(k in text for k in ["hello", "hi", "good morning", "good evening", "bonjour", "salut"]):
            return CustomerIntent(label="greeting", confidence=0.8)
        if any(k in text for k in ["question", "support", "help", "assist", "inquiry"]):
            return CustomerIntent(label="general", confidence=0.7)

        return CustomerIntent(label="unknown", confidence=0.4)

    def analyze_message(self, message: str) -> Dict[str, Any]:
        text = (message or "").strip()
        lowered = text.lower()
        language = self.detect_language(text)
        intent = self.detect_intent(lowered)

        positive_hits = sum(1 for token in self.POSITIVE_TOKENS if token in lowered)
        negative_hits = sum(1 for token in self.NEGATIVE_TOKENS if token in lowered)
        urgent_hits = sum(1 for token in self.URGENT_TOKENS if token in lowered)
        negotiation_hits = sum(1 for token in self.NEGOTIATION_TOKENS if token in lowered)

        denominator = max(1, positive_hits + negative_hits + 2)
        sentiment_score = round((positive_hits - negative_hits) / denominator, 2)
        if sentiment_score >= 0.2:
            sentiment_label = "positive"
        elif sentiment_score <= -0.2:
            sentiment_label = "negative"
        else:
            sentiment_label = "neutral"

        if urgent_hits >= 2:
            urgency = "critical"
        elif urgent_hits == 1:
            urgency = "high"
        elif intent.label in {"technical", "complaint"}:
            urgency = "medium"
        else:
            urgency = "low"

        needs_human = (
            urgency in {"high", "critical"}
            or intent.label in {"technical", "complaint"}
            or sentiment_label == "negative"
        )

        analysis: Dict[str, Any] = {
            "intent": intent.label,
            "confidence": intent.confidence,
            "language": language,
            "sentiment": {"label": sentiment_label, "score": sentiment_score},
            "urgency": urgency,
            "needs_human": needs_human,
            "wants_discount": negotiation_hits > 0 or intent.label == "negotiation",
        }
        if analysis["wants_discount"]:
            analysis["negotiation_offer"] = self._build_negotiation_offer(message=text)
        return analysis

    def generate_reply(self, message: str, customer_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        analysis = self.analyze_message(message)
        language = analysis["language"]
        intent = analysis["intent"]
        negotiation_offer = analysis.get("negotiation_offer")

        if intent == "billing":
            reply_key = "billing"
        elif intent == "shipment":
            reply_key = "shipment"
        elif intent == "technical":
            reply_key = "technical"
        elif intent == "negotiation":
            reply_key = "negotiation"
        elif intent == "complaint":
            reply_key = "complaint"
        elif intent == "greeting":
            reply_key = "greeting"
        else:
            reply_key = "general"

        reply = self._localize_reply(reply_key, language, negotiation_offer=negotiation_offer)

        suggested_channel = "human_agent" if analysis["needs_human"] else "self_service"
        return {
            "intent": intent,
            "reply": reply,
            "language": language,
            "sentiment": analysis["sentiment"],
            "urgency": analysis["urgency"],
            "needs_human": analysis["needs_human"],
            "suggested_channel": suggested_channel,
            "negotiation_offer": negotiation_offer,
        }

    def detect_language(self, message: str) -> str:
        text = (message or "").strip()
        if not text:
            return "en"

        arabic_count = sum(1 for char in text if "\u0600" <= char <= "\u06FF")
        ascii_letters = sum(1 for char in text if char.isascii() and char.isalpha())
        lowered = text.lower()
        french_hits = sum(1 for token in ["bonjour", "merci", "livraison", "prix", "facture", "problème", "probleme"] if token in lowered)

        if arabic_count > ascii_letters:
            return "ar"
        if french_hits:
            return "fr"
        return "en"

    def _build_negotiation_offer(self, message: str) -> Dict[str, Any]:
        lowered = (message or "").lower()
        if any(token in lowered for token in ["bulk", "volume", "large", "contract"]):
            discount_percent = 12
        elif any(token in lowered for token in ["loyal", "repeat", "returning"]):
            discount_percent = 10
        else:
            discount_percent = 7
        return {
            "discount_percent": discount_percent,
            "offer_type": "percentage",
            "label": f"{discount_percent}% service discount",
            "expires_in_hours": 24,
        }

    def _localize_reply(
        self,
        reply_key: str,
        language: str,
        negotiation_offer: Optional[Dict[str, Any]] = None,
    ) -> str:
        replies = {
            "en": {
                "greeting": "Hello. How can GTS support you today?",
                "general": "Thank you for contacting GTS. Please share a bit more detail so we can help you quickly.",
                "billing": "Please share your invoice number or payment reference and we will review the billing details.",
                "shipment": "Please send the shipment ID, load number, or delivery route so we can check the latest status.",
                "technical": "We detected a technical issue. Please share the page, error message, and time of the problem so a human agent can investigate.",
                "complaint": "We are sorry about the experience. Your case should be reviewed by a human agent, and we are preparing an escalation now.",
                "negotiation": "We can offer a limited discount for this request.",
            },
            "fr": {
                "greeting": "Bonjour. Comment GTS peut-il vous aider aujourd'hui ?",
                "general": "Merci de contacter GTS. Merci de partager plus de détails pour que nous puissions vous aider rapidement.",
                "billing": "Merci de partager votre numéro de facture ou la référence du paiement pour que nous puissions vérifier.",
                "shipment": "Merci d'envoyer l'identifiant de l'envoi, le numéro du chargement ou l'itinéraire pour vérifier le statut.",
                "technical": "Nous avons détecté un problème technique. Merci de partager la page, le message d'erreur et l'heure du problème.",
                "complaint": "Nous sommes désolés pour cette expérience. Le dossier va être transmis à un agent humain.",
                "negotiation": "Nous pouvons proposer une remise limitée pour cette demande.",
            },
            "ar": {
                "greeting": "Hello. How can GTS help you today?",
                "general": "Thank you for contacting GTS. Please share more details so we can help you quickly.",
                "billing": "Please send the invoice number or payment reference so we can review billing details.",
                "shipment": "Please send the shipment number or load number or delivery route to check the status.",
                "technical": "A technical issue has been detected. Please share the page, error message, and time of the problem for a human agent to follow up.",
                "complaint": "We apologize for this experience. The case will be escalated to a human agent now.",
                "negotiation": "We can offer a limited discount on this request.",
            },
        }

        localized = replies.get(language, replies["en"]).get(reply_key, replies["en"]["general"])
        if reply_key == "negotiation" and negotiation_offer:
            if language == "fr":
                return f"{localized} Current offer: {negotiation_offer['discount_percent']}% valid for {negotiation_offer['expires_in_hours']} hours."
            if language == "ar":
                return f"{localized} Current offer: {negotiation_offer['discount_percent']}% valid for {negotiation_offer['expires_in_hours']} hours."
            return f"{localized} Current offer: {negotiation_offer['discount_percent']}% valid for {negotiation_offer['expires_in_hours']} hours."
        return localized


_customer_service = AICustomerService()


def get_ai_customer_service() -> AICustomerService:
    return _customer_service