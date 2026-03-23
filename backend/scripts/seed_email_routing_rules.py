from __future__ import annotations

import asyncio
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from sqlalchemy import text

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.database.session import async_session


@dataclass(frozen=True)
class MailboxBotAssignment:
    email_address: str
    bot_key: str


@dataclass(frozen=True)
class RoutingRuleSeed:
    email_address: str
    bot_key: Optional[str]
    condition_field: str
    condition_operator: str
    condition_value: object
    action_type: str
    action_config: Optional[dict]
    priority: int
    condition_match_all: bool = False
    is_active: bool = True


ASSIGNMENTS = [
    MailboxBotAssignment("accounts@gabanilogistics.com", "finance_bot"),
    MailboxBotAssignment("finance@gabanilogistics.com", "finance_bot"),
    MailboxBotAssignment("customers@gabanilogistics.com", "customer_service"),
    MailboxBotAssignment("operations@gabanilogistics.com", "operations_manager"),
    MailboxBotAssignment("freight@gabanilogistics.com", "freight_broker"),
    MailboxBotAssignment("doccontrol@gabanilogistics.com", "documents_manager"),
    MailboxBotAssignment("admin@gabanilogistics.com", "general_manager"),
]

RULES = [
    RoutingRuleSeed(
        email_address="accounts@gabanilogistics.com",
        bot_key="finance_bot",
        condition_field="subject",
        condition_operator="contains",
        condition_value=["invoice", "payment", "receipt"],
        action_type="process",
        action_config={"queue": "finance"},
        priority=1,
        condition_match_all=False,
    ),
    RoutingRuleSeed(
        email_address="finance@gabanilogistics.com",
        bot_key="finance_bot",
        condition_field="subject",
        condition_operator="contains",
        condition_value=["invoice", "payment", "receipt"],
        action_type="process",
        action_config={"queue": "finance"},
        priority=1,
        condition_match_all=False,
    ),
    RoutingRuleSeed(
        email_address="customers@gabanilogistics.com",
        bot_key="customer_service",
        condition_field="all",
        condition_operator="contains",
        condition_value=["help", "support", "issue", "complaint"],
        action_type="process",
        action_config={"queue": "customer_support"},
        priority=2,
        condition_match_all=False,
    ),
    RoutingRuleSeed(
        email_address="operations@gabanilogistics.com",
        bot_key=None,
        condition_field="all",
        condition_operator="contains",
        condition_value=["urgent", "asap", "critical", "emergency"],
        action_type="tag",
        action_config={"tags": ["urgent", "high-priority"], "priority": "high"},
        priority=3,
        condition_match_all=False,
    ),
    RoutingRuleSeed(
        email_address="admin@gabanilogistics.com",
        bot_key="operations_manager",
        condition_field="sender",
        condition_operator="contains",
        condition_value="operations@gabanilogistics.com",
        action_type="process",
        action_config={"queue": "operations"},
        priority=5,
    ),
    RoutingRuleSeed(
        email_address="freight@gabanilogistics.com",
        bot_key="freight_broker",
        condition_field="subject",
        condition_operator="contains",
        condition_value=["quote", "rate", "pricing", "carrier"],
        action_type="process",
        action_config={"queue": "freight"},
        priority=4,
        condition_match_all=False,
    ),
]


FIND_MAILBOX_ID_SQL = text("SELECT id FROM mailboxes WHERE email_address = :email_address LIMIT 1")
UPDATE_ASSIGNED_BOT_SQL = text(
    """
    UPDATE mailboxes
    SET assigned_bot_key = :bot_key, updated_at = NOW()
    WHERE id = :mailbox_id
    """
)
FIND_RULE_SQL = text(
    """
    SELECT id
    FROM bot_mailbox_rules
    WHERE mailbox_id = :mailbox_id
      AND COALESCE(bot_key, '') = COALESCE(:bot_key, '')
      AND condition_field = :condition_field
      AND condition_operator = :condition_operator
      AND condition_value::text = CAST(:condition_value AS jsonb)::text
      AND action_type = :action_type
      AND priority = :priority
    LIMIT 1
    """
)
INSERT_RULE_SQL = text(
    """
    INSERT INTO bot_mailbox_rules (
        mailbox_id,
        bot_key,
        condition_field,
        condition_operator,
        condition_value,
        condition_match_all,
        action_type,
        action_config,
        priority,
        is_active,
        created_by
    ) VALUES (
        :mailbox_id,
        :bot_key,
        :condition_field,
        :condition_operator,
        CAST(:condition_value AS jsonb),
        :condition_match_all,
        :action_type,
        CAST(:action_config AS jsonb),
        :priority,
        :is_active,
        NULL
    )
    """
)


async def main() -> None:
    assignments_applied = 0
    rules_created = 0

    async with async_session() as db:
        for assignment in ASSIGNMENTS:
            mailbox_id = await db.scalar(FIND_MAILBOX_ID_SQL, {"email_address": assignment.email_address})
            if not mailbox_id:
                continue
            await db.execute(
                UPDATE_ASSIGNED_BOT_SQL,
                {"mailbox_id": int(mailbox_id), "bot_key": assignment.bot_key},
            )
            assignments_applied += 1

        for rule in RULES:
            mailbox_id = await db.scalar(FIND_MAILBOX_ID_SQL, {"email_address": rule.email_address})
            if not mailbox_id:
                continue

            payload = {
                "mailbox_id": int(mailbox_id),
                "bot_key": rule.bot_key,
                "condition_field": rule.condition_field,
                "condition_operator": rule.condition_operator,
                "condition_value": json.dumps(rule.condition_value),
                "condition_match_all": rule.condition_match_all,
                "action_type": rule.action_type,
                "action_config": json.dumps(rule.action_config or {}),
                "priority": rule.priority,
                "is_active": rule.is_active,
            }

            existing_id = await db.scalar(FIND_RULE_SQL, payload)
            if existing_id:
                continue

            await db.execute(INSERT_RULE_SQL, payload)
            rules_created += 1

        await db.commit()

    print({"ok": True, "assignments_applied": assignments_applied, "rules_created": rules_created})


if __name__ == "__main__":
    asyncio.run(main())
