from __future__ import annotations

import os
from typing import Any, Iterable, MutableMapping, Optional, Sequence

from .base import BaseSource, SourceItem


def _find_list_key(payload: MutableMapping[str, Any], keys: Sequence[str]) -> Sequence[Any]:
    for key in keys:
        value = payload.get(key)
        if isinstance(value, list):
            return value
        if isinstance(value, MutableMapping):
            nested = value.get("data")
            if isinstance(nested, list):
                return nested
    return []


class StatsCanSource(BaseSource):
    name = "statscan"
    entity_type = "dataset"
    description = "Statistics Canada open data catalog"

    _DEFAULT_QUERY = os.getenv("STATCAN_DEFAULT_QUERY", "transport")
    _ENDPOINT = os.getenv(
        "STATCAN_PRODUCT_LIST_URL",
        "https://www150.statcan.gc.ca/t1/wds/rest/getProductList",
    )

    async def search(
        self,
        *,
        query: Optional[str] = None,
        limit: int = 10,
        province: Optional[str] = None,
    ) -> list[SourceItem]:
        params = {
            "searchText": query or self._DEFAULT_QUERY,
            "length": max(limit, 1),
            "start": 0,
        }
        try:
            payload = await self._get_json(self._ENDPOINT, params=params)
        except Exception:
            return []

        rows = _find_list_key(payload, ("object", "data", "rows", "products"))
        results: list[SourceItem] = []
        province_flag = (province or "").strip().lower()

        for row in rows:
            if not isinstance(row, MutableMapping):
                continue
            if province_flag and not self._matches_province(row, province_flag):
                continue

            title = self._extract_title(row)
            if not title:
                continue

            item = SourceItem(
                source=self.name,
                entity_type=self.entity_type,
                title=title,
                description=self._extract_description(row),
                location=self._extract_location(row),
                tags=self._collect_tags(row),
                raw=row,
            )
            results.append(item)
            if len(results) >= limit:
                break
        return results

    def _extract_title(self, row: MutableMapping[str, Any]) -> str:
        return (
            str(row.get("title") or row.get("productTitle") or row.get("title_en") or "")
            .strip()
        )

    def _extract_description(self, row: MutableMapping[str, Any]) -> Optional[str]:
        return (
            str(row.get("description") or row.get("abstractExchange") or "")
            .strip()
            or None
        )

    def _extract_location(self, row: MutableMapping[str, Any]) -> Optional[str]:
        for key in ("geographicArea", "geographic_area", "province", "territory", "location"):
            if value := row.get(key):
                return str(value).strip()
        if extras := row.get("extras"):
            if isinstance(extras, Iterable):
                for extra in extras:
                    if isinstance(extra, MutableMapping) and extra.get("key") in {"province", "region", "territory"}:
                        if val := extra.get("value"):
                            return str(val).strip()
        return None

    def _collect_tags(self, row: MutableMapping[str, Any]) -> list[str]:
        tags: list[str] = []
        for key in ("subject", "theme", "keywords", "tags"):
            value = row.get(key)
            if isinstance(value, list):
                tags.extend(str(v).strip() for v in value if v)
        return sorted({tag for tag in tags if tag})

    def _matches_province(self, row: MutableMapping[str, Any], province: str) -> bool:
        province = province.lower()
        for key in ("province", "territory", "geographicArea", "geographic_area", "location"):
            raw = row.get(key)
            if raw and province in str(raw).lower():
                return True
        if extras := row.get("extras"):
            if isinstance(extras, Iterable):
                for extra in extras:
                    if isinstance(extra, MutableMapping):
                        if key := extra.get("key"):
                            if province in str(key).lower():
                                return True
                        if value := extra.get("value"):
                            if province in str(value).lower():
                                return True
        return False
