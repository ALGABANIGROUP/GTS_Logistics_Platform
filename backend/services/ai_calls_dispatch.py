from __future__ import annotations

import logging
from typing import Any, Dict, Optional

try:
    from backend.bots import get_bot_os  # type: ignore
except Exception:  # pragma: no cover - fallback when BOS not available
    get_bot_os = None  # type: ignore

logger = logging.getLogger(__name__)

# Preferred marketing/insights bots to handle call flows
MARKETING_BOTS = [
    "sales_intelligence",
    "information_coordinator",
    "strategy_advisor",
    "marketing_bot",
    "customer_service",
]


async def dispatch_to_marketing_bot(task_type: str, params: Dict[str, Any]) -> Optional[str]:
    if get_bot_os is None:
        logger.warning("BotOS not available; skipping dispatch for %s", task_type)
        return None
    try:
        bot_os = get_bot_os()
    except Exception as exc:  # pragma: no cover
        logger.warning("BotOS unavailable: %s", exc)
        return None

    for bot_name in MARKETING_BOTS:
        try:
            result = await bot_os.execute_bot(bot_name, task_type=task_type, params=params, allow_paused=False)
            if result and result.status != "failed":
                logger.info("Dispatched %s to bot %s", task_type, bot_name)
                return bot_name
        except Exception as exc:
            logger.warning("Dispatch to bot %s failed: %s", bot_name, exc)
    return None
