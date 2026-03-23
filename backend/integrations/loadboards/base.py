# backend/integrations/loadboards/base.py
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict

class BaseLoadBoard(ABC):
    """Unified async interface every load board provider must implement."""

    @abstractmethod
    async def ping(self) -> Dict[str, Any]:
        """Health check with the provider (mock or real)."""
        ...

    @abstractmethod
    async def create_company(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Create/register your company at the provider."""
        ...

    @abstractmethod
    async def post_load(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Post (publish) a load to the provider."""
        ...

    @abstractmethod
    async def register_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Generic webhook registration (events-style)."""
        ...

    @abstractmethod
    async def register_webhook_add(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Alternative webhook registration (e.g., type=BOOK|BID)."""
        ...

    @abstractmethod
    async def tracking_create(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Create a tracking order/session at the provider."""
        ...

    @abstractmethod
    async def push_tracking_points(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Push tracking points/locations to the provider."""
        ...
