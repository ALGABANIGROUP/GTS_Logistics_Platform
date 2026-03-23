from __future__ import annotations

import os
from typing import Any, Iterable, MutableMapping, Optional, Sequence

from .base import BaseSource, SourceItem

class OpenCanadaSource(BaseSource):
    name = "open_canada"
    entity_type = "dataset"
    description = "Open Canada CKAN catalog (government open data portal)"

    _BASE_URL = os.getenv("OPEN_CANADA_BASE_URL", "https://open.canada.ca/data/api/3/action")
    _DEFAULT_QUERY = os.getenv("OPEN_CANADA_DEFAULT_QUERY", "transport")
    _DEFAULT_FILTER = os.getenv("OPEN_CANADA_DEFAULT_FILTER")

    async def search(
        self,
        *,
        query: Optional[str] = None,
        limit: int = 10,
        province: Optional[str] = None,
    ) -> list[SourceItem]:
        params: dict[str, Any] = {
            "q": query or self._DEFAULT_QUERY,
            "rows": max(limit, 1),
        }
        if self._DEFAULT_FILTER:
            params["fq"] = self._DEFAULT_FILTER

        try:
            payload = await self._get_json(f"{self._BASE_URL}/package_search", params=params)
        except Exception:
            return []

        result = payload.get("result") if isinstance(payload, MutableMapping) else None
        if not isinstance(result, MutableMapping):
            return []

        raw_packages = result.get("results")
        if not isinstance(raw_packages, list):
            return []

        province_flag = (province or "").strip().lower()
        results: list[SourceItem] = []

        for pkg in raw_packages:
            if not isinstance(pkg, MutableMapping):
                continue
            if province_flag and not self._matches_province(pkg, province_flag):
                continue

            title = str(pkg.get("title") or pkg.get("name") or "").strip()
            if not title:
                continue

            item = SourceItem(
                source=self.name,
                entity_type=self.entity_type,
                title=title,
                description=self._extract_description(pkg),
                location=self._extract_location(pkg),
                tags=self._collect_tags(pkg),
                raw=pkg,
            )
            results.append(item)
            if len(results) >= limit:
                break

        return results

    def _extract_description(self, pkg: MutableMapping[str, Any]) -> Optional[str]:
        value = pkg.get("notes") or pkg.get("description")
        if isinstance(value, str):
            return value.strip() or None
        return None

    def _extract_location(self, pkg: MutableMapping[str, Any]) -> Optional[str]:
        extras = pkg.get("extras")
        if isinstance(extras, Iterable):
            for extra in extras:
                if isinstance(extra, MutableMapping):
                    if extra.get("key") in {"province", "region", "geographic_coverage"}:
                        if val := extra.get("value"):
                            return str(val).strip()

        for key in ("geographic_coverage", "location", "coverage"):
            value = pkg.get(key)
            if value:
                return str(value).strip()

        return None

    def _collect_tags(self, pkg: MutableMapping[str, Any]) -> list[str]:
        tags = []
        for raw in pkg.get("tags") or []:
            if isinstance(raw, MutableMapping):
                name = raw.get("name")
                if name:
                    tags.append(str(name).strip())
        return sorted({tag for tag in tags if tag})

    def _matches_province(self, pkg: MutableMapping[str, Any], province: str) -> bool:
        if province in (pkg.get("geographic_coverage") or "").lower():
            return True
        extras = pkg.get("extras")
        if isinstance(extras, Iterable):
            for extra in extras:
                if not isinstance(extra, MutableMapping):
                    continue
                value = extra.get("value")
                key = extra.get("key")
                if key and province in str(key).lower():
                    return True
                if value and province in str(value).lower():
                    return True
        return False
