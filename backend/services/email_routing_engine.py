from __future__ import annotations

import logging
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.email_center import BotMailboxRule, EmailMessage, Mailbox
from backend.services.email_ai_analyzer import EmailAIAnalyzer


logger = logging.getLogger(__name__)


class ConditionOperator:
    CONTAINS = "contains"
    EQUALS = "equals"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"
    REGEX = "regex"
    IN = "in"
    NOT_CONTAINS = "not_contains"
    NOT_EQUALS = "not_equals"

    ALL = {
        CONTAINS,
        EQUALS,
        STARTS_WITH,
        ENDS_WITH,
        REGEX,
        IN,
        NOT_CONTAINS,
        NOT_EQUALS,
    }


class ActionType:
    PROCESS = "process"
    FORWARD = "forward"
    REPLY = "reply"
    IGNORE = "ignore"
    TAG = "tag"
    ASSIGN = "assign"
    ESCALATE = "escalate"

    ALL = {
        PROCESS,
        FORWARD,
        REPLY,
        IGNORE,
        TAG,
        ASSIGN,
        ESCALATE,
    }


class EmailRoutingEngine:
    """Apply mailbox routing rules to inbound email messages."""

    BOT_CAPABILITIES = {
        "finance_bot": {"billing", "invoice", "payment", "refund", "receipt", "overdue"},
        "customer_service": {"support", "general", "help", "issue", "complaint", "question"},
        "operations_manager": {"operations", "shipment", "dispatch", "delivery", "pickup", "route"},
        "freight_broker": {"sales", "quote", "pricing", "rate", "freight", "carrier"},
        "legal_bot": {"legal", "compliance", "claim", "contract", "liability", "terms"},
    }

    def __init__(
        self,
        db: AsyncSession,
        analyzer: Optional[EmailAIAnalyzer] = None,
        ai_confidence_threshold: float = 0.75,
    ):
        self.db = db
        self.analyzer = analyzer
        self.ai_confidence_threshold = ai_confidence_threshold

    async def route_message(self, message_id: int) -> Dict[str, Any]:
        message = await self.db.get(EmailMessage, message_id)
        if not message:
            raise ValueError(f"Message {message_id} not found")

        mailbox = await self.db.get(Mailbox, message.mailbox_id)
        if not mailbox:
            logger.warning("Mailbox %s not found for message %s", message.mailbox_id, message_id)
            return self._unmatched_result()

        rules = await self._get_active_rules(mailbox.id)
        content = self._prepare_content(message)

        for rule in rules:
            if self._check_rule(rule, content):
                return {
                    "matched": True,
                    "applied_rule_id": rule.id,
                    "action_type": rule.action_type,
                    "action_config": rule.action_config or {},
                    "bot_key": rule.bot_key or mailbox.assigned_bot_key,
                    "rule_priority": rule.priority,
                    "route_source": "rule",
                }

        ai_result = self._route_from_analysis(message, mailbox)
        if ai_result:
            return ai_result

        if mailbox.assigned_bot_key:
            return {
                "matched": True,
                "applied_rule_id": None,
                "action_type": ActionType.PROCESS,
                "action_config": {},
                "bot_key": mailbox.assigned_bot_key,
                "rule_priority": None,
                "route_source": "mailbox_default",
            }

        return self._unmatched_result()

    async def apply_routing_to_message(self, message_id: int) -> Tuple[bool, Optional[str]]:
        message = await self.db.get(EmailMessage, message_id)
        if not message:
            raise ValueError(f"Message {message_id} not found")

        if not message.analysis_result:
            analyzer = self.analyzer or EmailAIAnalyzer(self.db)
            analysis_result = await analyzer.analyze_message(message_id)
            message.analysis_result = analysis_result

        result = await self.route_message(message_id)
        message = await self.db.get(EmailMessage, message_id)
        if not message:
            raise ValueError(f"Message {message_id} not found")

        now = datetime.now(timezone.utc)
        message.analyzed_at = now
        existing_analysis = message.analysis_result or {}
        message.analysis_result = {
            **existing_analysis,
            "matched": result.get("matched", False),
            "action_type": result.get("action_type"),
            "bot_key": result.get("bot_key"),
            "applied_rule_id": result.get("applied_rule_id"),
            "rule_priority": result.get("rule_priority"),
            "route_source": result.get("route_source"),
            "routing_confidence": result.get("routing_confidence"),
        }

        if result.get("matched"):
            message.applied_rule_id = result.get("applied_rule_id")
            message.processed_by_bot = result.get("bot_key")
            message.processed_at = now
            await self.db.commit()
            return True, result.get("bot_key")

        await self.db.commit()
        return False, None

    async def get_rules_for_mailbox(self, mailbox_id: int) -> List[Dict[str, Any]]:
        stmt = (
            select(BotMailboxRule)
            .where(BotMailboxRule.mailbox_id == mailbox_id)
            .order_by(BotMailboxRule.priority.asc(), BotMailboxRule.id.asc())
        )
        result = await self.db.execute(stmt)
        rules = sorted(
            list(result.scalars().all()),
            key=lambda rule: ((rule.priority or 0), rule.id or 0),
        )
        return [self._rule_to_dict(rule) for rule in rules]

    async def _get_active_rules(self, mailbox_id: int) -> List[BotMailboxRule]:
        stmt = (
            select(BotMailboxRule)
            .where(
                and_(
                    BotMailboxRule.mailbox_id == mailbox_id,
                    BotMailboxRule.is_active.is_(True),
                )
            )
            .order_by(BotMailboxRule.priority.asc(), BotMailboxRule.id.asc())
        )
        result = await self.db.execute(stmt)
        rules = list(result.scalars().all())
        return sorted(rules, key=lambda rule: ((rule.priority or 0), rule.id or 0))

    def _prepare_content(self, message: EmailMessage) -> Dict[str, str]:
        to_addrs = message.to_addrs or []
        cc_addrs = message.cc_addrs or []
        recipients = " ".join([*to_addrs, *cc_addrs])
        subject = message.subject or ""
        body = message.body_preview or ""
        sender = message.from_addr or ""

        return {
            "subject": subject,
            "body": body,
            "sender": sender,
            "recipients": recipients,
            "all": " ".join(filter(None, [subject, body, sender, recipients])),
        }

    def _route_from_analysis(self, message: EmailMessage, mailbox: Mailbox) -> Optional[Dict[str, Any]]:
        analysis = message.analysis_result or {}
        if not isinstance(analysis, dict):
            return None

        best_bot, routing_confidence = self._select_bot_from_analysis(analysis, mailbox)
        if not best_bot or routing_confidence < self.ai_confidence_threshold:
            return None

        return {
            "matched": True,
            "applied_rule_id": None,
            "action_type": ActionType.PROCESS,
            "action_config": {
                "analysis_category": analysis.get("category"),
                "analysis_method": analysis.get("method"),
                "analysis_keywords": analysis.get("keywords") or [],
            },
            "bot_key": best_bot,
            "rule_priority": None,
            "route_source": "ai",
            "routing_confidence": routing_confidence,
        }

    def _select_bot_from_analysis(
        self,
        analysis: Dict[str, Any],
        mailbox: Mailbox,
    ) -> Tuple[Optional[str], float]:
        category = str(analysis.get("category") or "general").strip().lower()
        keywords = {
            str(keyword).strip().lower()
            for keyword in (analysis.get("keywords") or [])
            if str(keyword).strip()
        }
        sentiment = analysis.get("sentiment") or {}
        urgency = str(sentiment.get("urgency") or "").lower()
        analysis_confidence = self._normalize_confidence(analysis.get("confidence"))

        best_bot: Optional[str] = None
        best_score = 0.0

        for bot_key, capabilities in self.BOT_CAPABILITIES.items():
            score = 0.0
            if category in capabilities:
                score += 0.5

            overlap = len(keywords.intersection(capabilities))
            score += min(0.3, overlap * 0.1)

            if urgency == "high" and bot_key in {"customer_service", "operations_manager", "finance_bot"}:
                score += 0.05

            if mailbox.assigned_bot_key and mailbox.assigned_bot_key == bot_key:
                score += 0.05

            if score > best_score:
                best_score = score
                best_bot = bot_key

        if not best_bot or best_score <= 0:
            return None, 0.0

        final_confidence = round(min(0.99, (analysis_confidence * 0.7) + (best_score * 0.3)), 2)
        return best_bot, final_confidence

    def _normalize_confidence(self, value: Any) -> float:
        try:
            return max(0.0, min(float(value), 1.0))
        except (TypeError, ValueError):
            return 0.0

    def _check_rule(self, rule: BotMailboxRule, content: Dict[str, str]) -> bool:
        field_value = content.get(rule.condition_field, "")
        if not field_value and rule.condition_field != "all":
            return False

        try:
            return self._evaluate_condition(
                operator=rule.condition_operator,
                field_value=field_value,
                condition_value=rule.condition_value,
                match_all=rule.condition_match_all,
            )
        except Exception:
            logger.exception("Failed to evaluate routing rule %s", rule.id)
            return False

    def _evaluate_condition(
        self,
        *,
        operator: str,
        field_value: str,
        condition_value: Any,
        match_all: bool,
    ) -> bool:
        haystack = (field_value or "").lower()

        if operator == ConditionOperator.CONTAINS:
            values = self._normalize_values(condition_value)
            if not values:
                return False
            predicate = lambda value: value in haystack
            return all(predicate(value) for value in values) if match_all else any(
                predicate(value) for value in values
            )

        if operator == ConditionOperator.NOT_CONTAINS:
            values = self._normalize_values(condition_value)
            if not values:
                return False
            predicate = lambda value: value not in haystack
            return all(predicate(value) for value in values) if match_all else any(
                predicate(value) for value in values
            )

        if operator == ConditionOperator.EQUALS:
            if isinstance(condition_value, list):
                expected = [str(value).lower() for value in condition_value]
                return haystack in expected
            return haystack == str(condition_value).lower()

        if operator == ConditionOperator.NOT_EQUALS:
            if isinstance(condition_value, list):
                expected = [str(value).lower() for value in condition_value]
                return haystack not in expected
            return haystack != str(condition_value).lower()

        if operator == ConditionOperator.STARTS_WITH:
            return haystack.startswith(str(condition_value).lower())

        if operator == ConditionOperator.ENDS_WITH:
            return haystack.endswith(str(condition_value).lower())

        if operator == ConditionOperator.REGEX:
            return bool(re.search(str(condition_value), field_value or "", re.IGNORECASE))

        if operator == ConditionOperator.IN:
            values = self._normalize_values(condition_value)
            return haystack in values

        return False

    def _normalize_values(self, condition_value: Any) -> List[str]:
        if isinstance(condition_value, list):
            return [str(value).lower() for value in condition_value if str(value).strip()]
        if condition_value is None:
            return []
        text = str(condition_value).strip().lower()
        return [text] if text else []

    def _rule_to_dict(self, rule: BotMailboxRule) -> Dict[str, Any]:
        return {
            "id": rule.id,
            "mailbox_id": rule.mailbox_id,
            "bot_key": rule.bot_key,
            "condition_field": rule.condition_field,
            "condition_operator": rule.condition_operator,
            "condition_value": rule.condition_value,
            "condition_match_all": rule.condition_match_all,
            "action_type": rule.action_type,
            "action_config": rule.action_config,
            "priority": rule.priority,
            "is_active": rule.is_active,
            "times_matched": rule.times_matched,
            "last_matched_at": rule.last_matched_at.isoformat() if rule.last_matched_at else None,
            "created_at": rule.created_at.isoformat() if rule.created_at else None,
            "updated_at": rule.updated_at.isoformat() if rule.updated_at else None,
            "created_by": rule.created_by,
        }

    def _unmatched_result(self) -> Dict[str, Any]:
        return {
            "matched": False,
            "applied_rule_id": None,
            "action_type": None,
            "action_config": {},
            "bot_key": None,
            "rule_priority": None,
            "route_source": "unmatched",
            "routing_confidence": 0.0,
        }
