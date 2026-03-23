from __future__ import annotations

import json
import re
from typing import Any, Dict, Optional, Tuple

BOT_ALIASES = {
    "finance": "finance_bot",
    "finance_bot": "finance_bot",
    "accounts": "finance_bot",
    "freight": "freight_broker",
    "freight_broker": "freight_broker",
    "broker": "freight_broker",
    "ops": "operations_manager",
    "operations": "operations_manager",
    "operations_manager": "operations_manager",
    "general": "general_manager",
    "general_manager": "general_manager",
    "maintenance": "maintenance_dev",
    "maintenance_dev": "maintenance_dev",
    "documents": "documents_manager",
    "docs": "documents_manager",
    "documents_manager": "documents_manager",
    "system_admin": "system_admin",
    "admin": "system_admin",
    "customer": "customer_service",
    "customer_service": "customer_service",
    "support": "customer_service",
    "safety": "safety",
    "legal": "legal_consultant",
    "legal_consultant": "legal_consultant",
    "strategy": "strategy_advisor",
    "strategy_advisor": "strategy_advisor",
    "info": "information_coordinator",
    "information": "information_coordinator",
    "information_coordinator": "information_coordinator",
    "security": "security",
    "partner": "partner",
    "sales": "sales",
    "mapleload": "mapleload",
}

COMMAND_RE = re.compile(
    r"\b(bot|action|task|run|execute)\s*[:=]\s*([a-zA-Z0-9 _-]+?)(?=\s+\b(?:bot|action|task|run|execute)\s*[:=]|$)",
    re.I,
)


def normalize_bot_name(value: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9 _-]+", "", value or "").strip().lower()
    cleaned = re.sub(r"[\s-]+", "_", cleaned)
    return cleaned


def _extract_tokens(text: str) -> Tuple[Optional[str], Optional[str]]:
    bot_name = None
    task_type = None
    for key, raw in COMMAND_RE.findall(text or ""):
        key_lower = key.lower()
        normalized = normalize_bot_name(raw)
        if key_lower == "bot":
            bot_name = normalized
        elif key_lower in {"action", "task"}:
            task_type = normalize_bot_name(raw)
        elif key_lower in {"run", "execute"} and not bot_name:
            bot_name = normalized
    return bot_name, task_type


def _resolve_bot_name(raw: Optional[str]) -> Optional[str]:
    if not raw:
        return None
    normalized = normalize_bot_name(raw)
    return BOT_ALIASES.get(normalized, normalized) or None


def parse_command(command: str) -> Dict[str, Any]:
    text = (command or "").strip()
    if not text:
        return {"ok": False, "error": "empty_command"}

    if text.startswith("{") or text.startswith("["):
        try:
            payload = json.loads(text)
        except Exception:
            payload = None
        if isinstance(payload, dict):
            bot_name = _resolve_bot_name(
                payload.get("bot")
                or payload.get("bot_name")
                or payload.get("botKey")
                or payload.get("name")
            )
            task_type = normalize_bot_name(
                payload.get("task_type") or payload.get("task") or payload.get("action") or "run"
            )
            params = payload.get("params") if isinstance(payload.get("params"), dict) else {}
            return {
                "ok": True,
                "bot_name": bot_name,
                "task_type": task_type or "run",
                "params": params,
                "source": "json",
            }

    tokens = text.split()
    bot_guess = None
    task_guess = None
    if tokens and tokens[0].lower() in {"run", "execute", "start"}:
        if len(tokens) > 1:
            bot_guess = tokens[1]
        if len(tokens) > 2:
            task_guess = tokens[2]
    elif tokens:
        bot_guess = tokens[0]
        if len(tokens) > 1:
            task_guess = tokens[1]

    extracted_bot, extracted_task = _extract_tokens(text)
    bot_name = _resolve_bot_name(extracted_bot or bot_guess)
    task_type = normalize_bot_name(extracted_task or task_guess or "run")

    return {
        "ok": True,
        "bot_name": bot_name,
        "task_type": task_type or "run",
        "params": {},
        "source": "text",
    }
