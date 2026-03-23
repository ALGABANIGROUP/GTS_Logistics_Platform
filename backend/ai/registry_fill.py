from __future__ import annotations

from dataclasses import dataclass
import sys
from typing import Any, Dict, Optional

from backend.ai.roles.bot_permissions import BOT_POLICIES


def _get_registry():
    for module_name in ("backend.main", "main"):
        module = sys.modules.get(module_name)
        if module is not None and hasattr(module, "ai_registry"):
            return module.ai_registry

    try:
        from backend import main as main_module  # type: ignore
    except Exception:
        from .. import main as main_module  # type: ignore
    return main_module.ai_registry


@dataclass
class PlaceholderBot:
    """Registered bot placeholder (returns 501 for run)."""

    name: str

    async def run(self, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return {
            "success": False,
            "bot_key": self.name,
            "detail": "This bot is registered but not implemented yet.",
            "status_code": 501,
        }

    async def status(self) -> Dict[str, Any]:
        return {
            "bot_key": self.name,
            "status": "registered_placeholder",
            "implemented": False,
        }

    async def config(self) -> Dict[str, Any]:
        return {
            "bot_key": self.name,
            "config": {},
            "implemented": False,
        }


@dataclass
class AliasBot:
    """Alias bot that forwards calls to another bot key."""

    name: str
    target_key: str

    def _target(self):
        registry = _get_registry()
        return registry.get(self.target_key)

    async def run(self, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return await self._target().run(payload or {})

    async def status(self) -> Dict[str, Any]:
        data = await self._target().status()
        data["alias_of"] = self.target_key
        data["bot_key"] = self.name
        return data

    async def config(self) -> Dict[str, Any]:
        data = await self._target().config()
        data["alias_of"] = self.target_key
        data["bot_key"] = self.name
        return data


ALIAS_MAP: Dict[str, str] = {
    "maintenance_bot": "maintenance_dev",
    "sales_team": "sales_bot",
    "security_manager": "security_bot",
    "support": "customer_service",
    "ops": "operations_bot",
    "gm": "general_manager",
    "docs": "documents_manager",
    "frt": "freight_bot",
    "mlc": "mapleload_canada",
}


def ensure_all_bots_registered(registry=None) -> Dict[str, Any]:
    registry = registry or _get_registry()
    expected_keys = set(BOT_POLICIES.keys())

    registered = set(registry.list().keys())
    added = []

    for key in sorted(expected_keys):
        if key in registered:
            continue

        if key in ALIAS_MAP:
            target = ALIAS_MAP[key]
            if target not in registry.list():
                registry.register(PlaceholderBot(name=target))
            registry.register(AliasBot(name=key, target_key=target))
            added.append((key, f"alias->{target}"))
            continue

        registry.register(PlaceholderBot(name=key))
        added.append((key, "placeholder"))

    return {
        "expected": len(expected_keys),
        "registered_now": len(registry.list().keys()),
        "added": added,
    }
