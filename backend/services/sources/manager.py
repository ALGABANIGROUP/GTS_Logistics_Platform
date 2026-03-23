from __future__ import annotations

from typing import Iterable, List, Optional

from .base import BaseSource, SourceItem

MAX_SEARCH_LIMIT = 50


class SourceManager:
    def __init__(self) -> None:
        self._sources: dict[str, BaseSource] = {}

    def register(self, source: BaseSource) -> None:
        self._sources[source.name] = source

    def list_sources(self) -> list[str]:
        return sorted(self._sources.keys())

    def get(self, name: str) -> Optional[BaseSource]:
        return self._sources.get(name)

    async def search(
        self,
        *,
        source: Optional[str] = None,
        entity_type: Optional[str] = None,
        query: Optional[str] = None,
        province: Optional[str] = None,
        limit: int = 10,
    ) -> list[SourceItem]:
        limit = max(1, min(limit, MAX_SEARCH_LIMIT))
        results: list[SourceItem] = []

        for src in self._sources.values():
            if source and src.name != source:
                continue
            if entity_type and src.entity_type != entity_type:
                continue
            chunk = await src.search(query=query, limit=limit, province=province)
            results.extend(chunk)
            if len(results) >= limit:
                break

        return results[:limit]

    async def collect_all(
        self,
        *,
        limit_per_source: int = 5,
        province: Optional[str] = None,
    ) -> list[SourceItem]:
        limit_per_source = max(1, min(limit_per_source, MAX_SEARCH_LIMIT))
        gathered: list[SourceItem] = []
        for src in self._sources.values():
            items = await src.search(query=None, limit=limit_per_source, province=province)
            gathered.extend(items)
        return gathered
