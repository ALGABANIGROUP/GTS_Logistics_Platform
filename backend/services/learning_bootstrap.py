from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict, List

from backend.ai.learning_engine import bot_learning_engine

logger = logging.getLogger(__name__)


DEFAULT_LEARNING_BOTS: List[Dict[str, Any]] = [
    {
        "bot_id": "general_manager",
        "bot_name": "General Manager Bot",
        "enabled": True,
        "frequency": "daily",
        "intensity": "medium",
        "data_sources": ["error_logs", "performance_metrics", "user_feedback"],
    },
    {
        "bot_id": "operations_manager",
        "bot_name": "Operations Manager Bot",
        "enabled": True,
        "frequency": "daily",
        "intensity": "high",
        "data_sources": ["error_logs", "performance_metrics", "user_feedback"],
    },
    {
        "bot_id": "finance_bot",
        "bot_name": "Finance Bot",
        "enabled": True,
        "frequency": "daily",
        "intensity": "high",
        "data_sources": ["error_logs", "performance_metrics", "user_feedback"],
    },
    {
        "bot_id": "freight_broker",
        "bot_name": "Freight Broker Bot",
        "enabled": True,
        "frequency": "hourly",
        "intensity": "high",
        "data_sources": ["error_logs", "performance_metrics", "user_feedback"],
    },
    {
        "bot_id": "documents_manager",
        "bot_name": "Documents Manager Bot",
        "enabled": True,
        "frequency": "daily",
        "intensity": "medium",
        "data_sources": ["error_logs", "performance_metrics", "user_feedback"],
    },
    {
        "bot_id": "customer_service",
        "bot_name": "Customer Service Bot",
        "enabled": True,
        "frequency": "hourly",
        "intensity": "high",
        "data_sources": ["error_logs", "performance_metrics", "user_feedback"],
    },
    {
        "bot_id": "system_admin",
        "bot_name": "System Admin Bot",
        "enabled": True,
        "frequency": "daily",
        "intensity": "medium",
        "data_sources": ["error_logs", "performance_metrics", "user_feedback"],
    },
    {
        "bot_id": "information_coordinator",
        "bot_name": "Information Coordinator Bot",
        "enabled": True,
        "frequency": "daily",
        "intensity": "medium",
        "data_sources": ["error_logs", "performance_metrics", "user_feedback"],
    },
    {
        "bot_id": "strategy_advisor",
        "bot_name": "Strategy Advisor Bot",
        "enabled": True,
        "frequency": "weekly",
        "intensity": "low",
        "data_sources": ["error_logs", "performance_metrics", "user_feedback"],
    },
    {
        "bot_id": "maintenance_dev",
        "bot_name": "Maintenance Dev Bot",
        "enabled": True,
        "frequency": "daily",
        "intensity": "medium",
        "data_sources": ["error_logs", "performance_metrics", "user_feedback"],
    },
    {
        "bot_id": "legal_consultant",
        "bot_name": "Legal Consultant Bot",
        "enabled": True,
        "frequency": "daily",
        "intensity": "medium",
        "data_sources": ["error_logs", "performance_metrics", "user_feedback"],
    },
    {
        "bot_id": "safety_manager",
        "bot_name": "Safety Manager Bot",
        "enabled": True,
        "frequency": "daily",
        "intensity": "high",
        "data_sources": ["error_logs", "performance_metrics", "user_feedback"],
    },
    {
        "bot_id": "sales_team",
        "bot_name": "Sales Team Bot",
        "enabled": True,
        "frequency": "daily",
        "intensity": "high",
        "data_sources": ["error_logs", "performance_metrics", "user_feedback"],
    },
    {
        "bot_id": "security_manager",
        "bot_name": "Security Manager Bot",
        "enabled": True,
        "frequency": "hourly",
        "intensity": "high",
        "data_sources": ["error_logs", "performance_metrics", "user_feedback"],
    },
    {
        "bot_id": "mapleload_canada",
        "bot_name": "MapleLoad Canada Bot",
        "enabled": True,
        "frequency": "hourly",
        "intensity": "high",
        "data_sources": ["error_logs", "performance_metrics", "user_feedback"],
    },
    {
        "bot_id": "partner_manager",
        "bot_name": "Partner Manager Bot",
        "enabled": True,
        "frequency": "daily",
        "intensity": "medium",
        "data_sources": ["error_logs", "performance_metrics", "user_feedback"],
    },
]


def register_default_learning_bots() -> Dict[str, Any]:
    registered = []
    for config in DEFAULT_LEARNING_BOTS:
        bot_learning_engine.register_bot(**config)
        registered.append(config["bot_id"])
    stats = bot_learning_engine.get_learning_stats()
    logger.info(
        "Registered %s learning bots. enabled=%s",
        stats.get("total_bots_registered"),
        stats.get("enabled_bots"),
    )
    return {
        "registered_bot_ids": registered,
        "stats": stats,
    }


def run_learning_for_all_bots() -> Dict[str, Any]:
    results: Dict[str, Any] = {}
    for config in DEFAULT_LEARNING_BOTS:
        bot_id = config["bot_id"]
        profile = bot_learning_engine.learning_profiles.get(bot_id)
        if not profile or not profile.enabled:
            continue
        results[bot_id] = bot_learning_engine.perform_learning(bot_id)
    return {
        "bots_processed": len(results),
        "results": results,
        "stats": bot_learning_engine.get_learning_stats(),
    }


async def learning_scheduler_loop(interval_hours: int = 6) -> None:
    logger.info("Learning scheduler loop started (every %s hours)", interval_hours)
    try:
        while True:
            await asyncio.sleep(max(1, int(interval_hours)) * 3600)
            try:
                result = run_learning_for_all_bots()
                logger.info(
                    "Learning scheduler executed. bots_processed=%s total_registered=%s",
                    result.get("bots_processed"),
                    result.get("stats", {}).get("total_bots_registered"),
                )
            except Exception as exc:
                logger.warning("Learning scheduler run failed: %s", exc)
    except asyncio.CancelledError:
        logger.info("Learning scheduler loop stopped")
        raise
