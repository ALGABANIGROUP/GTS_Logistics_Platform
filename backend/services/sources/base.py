from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, Iterable, Mapping, MutableMapping, Optional

import httpx
from pydantic import BaseModel, Field


class SourceItem(BaseModel):
    source: str
    entity_type: str
    title: str
    description: Optional[str] = None
    location: Optional[str] = None
    tags: list[str] = Field(default_factory=list)
    raw: Mapping[str, Any] = Field(default_factory=dict)
    fetched_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_real: bool = True


class BaseSource(ABC):
    name: str
    entity_type: str
    description: str

    def __init__(self, *, timeout: float = 15.0) -> None:
        self._timeout = httpx.Timeout(timeout)

    async def _get_json(
        self,
        url: str,
        *,
        params: Optional[Mapping[str, Any]] = None,
        headers: Optional[Mapping[str, str]] = None,
    ) -> MutableMapping[str, Any]:
        async with httpx.AsyncClient(timeout=self._timeout, headers=headers) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            payload = response.json()
            if isinstance(payload, MutableMapping):
                return payload
            if isinstance(payload, Iterable):
                return {"data": payload}  # type: ignore[arg-type]
            return {}

    @abstractmethod
    async def search(
        self,
        *,
        query: Optional[str] = None,
        limit: int = 10,
        province: Optional[str] = None,
    ) -> list[SourceItem]:
        """
        Fetch metadata items that match the provided query and filters.
        """
        raise NotImplementedError()
