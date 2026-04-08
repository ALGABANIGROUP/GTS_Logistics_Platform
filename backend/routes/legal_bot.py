from __future__ import annotations

import copy
import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from backend.security.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/legal", tags=["Legal Consultant"])


CANADIAN_REGULATIONS: List[Dict[str, Any]] = [
    {
        "id": "ca_on_reg_161_25",
        "name": "Ontario Regulation 161/25",
        "title": "Pilot Project - Automated Haulers",
        "source": "Government of Ontario",
        "category": "regulation",
        "region": "Canada",
        "transport_mode": "road",
        "summary": "Ontario regulation governing the pilot project for automated commercial motor vehicles on designated roads.",
        "applicable_in": "Ontario, Canada",
        "topics": ["compliance", "automation", "carrier"],
        "applies_to": ["carriers", "technology providers"],
        "published_at": "2025-08-13T00:00:00+00:00",
        "url": "https://www.ontario.ca/laws/regulation/250161",
        "key_points": [
            "Registrar approval is required before operating automated haulers.",
            "Insurance and safety safeguards remain mandatory during the pilot.",
            "Pilot participation is limited to designated conditions and roads.",
        ],
        "official": True,
    },
    {
        "id": "ca_cbsa_carm",
        "name": "CBSA CARM",
        "title": "CBSA Assessment and Revenue Management",
        "source": "Canada Border Services Agency",
        "category": "customs",
        "region": "Canada",
        "transport_mode": "customs",
        "summary": "The CBSA digital system used to manage commercial accounting, duties, taxes, and importer interactions.",
        "applicable_in": "Canada",
        "topics": ["customs", "trade", "brokers"],
        "applies_to": ["brokers", "importers", "carriers"],
        "published_at": "2024-10-21T00:00:00+00:00",
        "url": "https://www.cbsa-asfc.gc.ca/services/carm-gcra/menu-eng.html",
        "key_points": [
            "Commercial import participants should use the CARM client portal.",
            "Duty and tax workflows are handled digitally through CBSA systems.",
            "Cross-border operators should align customs submissions with CARM requirements.",
        ],
        "official": True,
    },
    {
        "id": "ca_transportation_act",
        "name": "Canada Transportation Act",
        "title": "Federal transportation framework",
        "source": "Justice Laws Website",
        "category": "trade",
        "region": "Canada",
        "transport_mode": "multimodal",
        "summary": "Federal statute governing regulated transportation activities, economic regulation, and national transportation policy.",
        "applicable_in": "Canada",
        "topics": ["carrier", "transport", "compliance"],
        "applies_to": ["carriers", "shippers", "brokers"],
        "published_at": "1996-07-01T00:00:00+00:00",
        "url": "https://laws-lois.justice.gc.ca/eng/acts/c-10.4/",
        "key_points": [
            "The Act establishes Canada’s national transportation policy framework.",
            "Transportation regulation interacts with federal and provincial carrier rules.",
            "Commercial operators should align service, safety, and market activity with the Act.",
        ],
        "official": True,
    },
    {
        "id": "ca_tdg_overview",
        "name": "Transport Canada Dangerous Goods",
        "title": "Transportation of Dangerous Goods program",
        "source": "Transport Canada",
        "category": "safety",
        "region": "Canada",
        "transport_mode": "multimodal",
        "summary": "Transport Canada program and regulatory guidance for the safe transportation of dangerous goods.",
        "applicable_in": "Canada",
        "topics": ["safety", "dangerous_goods", "compliance"],
        "applies_to": ["carriers", "shippers"],
        "published_at": "2024-01-01T00:00:00+00:00",
        "url": "https://tc.canada.ca/en/dangerous-goods",
        "key_points": [
            "Dangerous-goods shipments require classification, documentation, and training controls.",
            "Packaging, placarding, and emergency-response obligations depend on the goods involved.",
            "Transport Canada publishes guidance and program material for compliance.",
        ],
        "official": True,
    },
]


class LegalSearchRequest(BaseModel):
    query: str = ""
    category: Optional[str] = None
    region: Optional[str] = None
    limit: int = 20


class CanadianLegalDataService:
    def __init__(self) -> None:
        self._cache_ttl = timedelta(minutes=10)
        self._updates_cache: List[Dict[str, Any]] = []
        self._cache_time: Optional[datetime] = None

    def _fresh_cache(self) -> bool:
        return bool(
            self._cache_time
            and datetime.now(timezone.utc) - self._cache_time < self._cache_ttl
        )

    async def fetch_open511_events(self, limit: int = 6) -> List[Dict[str, Any]]:
        try:
            async with httpx.AsyncClient(timeout=12.0, follow_redirects=True) as client:
                response = await client.get("https://api.open511.gov.bc.ca/events")
                response.raise_for_status()
                payload = response.json()
        except Exception as exc:
            logger.warning("Failed to fetch Open511 legal feed: %s", exc)
            return []

        events = payload.get("events") if isinstance(payload, dict) else []
        mapped: List[Dict[str, Any]] = []
        for event in events[:limit]:
            roads = event.get("roads") or []
            road = roads[0] if roads else {}
            mapped.append(
                {
                    "id": f"open511::{event.get('id')}",
                    "name": event.get("headline") or event.get("event_type") or "Road update",
                    "title": event.get("description") or event.get("headline") or "Road update",
                    "source": "DriveBC Open511",
                    "category": "safety",
                    "region": "Canada",
                    "transport_mode": "road",
                    "summary": event.get("description") or "Real-time British Columbia road advisory.",
                    "applicable_in": "British Columbia, Canada",
                    "topics": ["roads", "safety", "operations"],
                    "applies_to": ["carriers"],
                    "published_at": event.get("updated") or event.get("created") or datetime.now(timezone.utc).isoformat(),
                    "url": event.get("url") or "https://api.open511.gov.bc.ca/events",
                    "key_points": [
                        f"Status: {event.get('status', 'ACTIVE')}",
                        f"Severity: {event.get('severity', 'unknown')}",
                        f"Road: {road.get('name', 'British Columbia road network')}",
                    ],
                    "official": True,
                    "live": True,
                }
            )
        return mapped

    async def get_all_updates(self) -> List[Dict[str, Any]]:
        if self._fresh_cache():
            return copy.deepcopy(self._updates_cache)

        updates = copy.deepcopy(CANADIAN_REGULATIONS)
        updates.extend(await self.fetch_open511_events())
        updates.sort(key=lambda item: item.get("published_at") or "", reverse=True)

        self._updates_cache = copy.deepcopy(updates)
        self._cache_time = datetime.now(timezone.utc)
        return updates

    async def search(self, query: str, category: Optional[str], region: Optional[str], limit: int) -> List[Dict[str, Any]]:
        query_lower = query.strip().lower()
        updates = await self.get_all_updates()
        results: List[Dict[str, Any]] = []

        for item in updates:
            if category and item.get("category") != category:
                continue
            if region and region.lower() not in str(item.get("region") or "").lower():
                continue

            haystack = " ".join(
                [
                    str(item.get("name") or ""),
                    str(item.get("title") or ""),
                    str(item.get("summary") or ""),
                    " ".join(item.get("topics") or []),
                    str(item.get("source") or ""),
                ]
            ).lower()

            if query_lower and query_lower not in haystack:
                continue

            results.append(item)

        return results[:limit]


legal_service = CanadianLegalDataService()


def _normalize_sources(updates: List[Dict[str, Any]]) -> List[str]:
    seen = []
    for item in updates:
        source = str(item.get("source") or "").strip()
        if source and source not in seen:
            seen.append(source)
    return seen


@router.get("/updates")
async def get_legal_updates(
    category: Optional[str] = None,
    region: Optional[str] = "Canada",
    limit: int = 20,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    updates = await legal_service.get_all_updates()

    if category:
        updates = [item for item in updates if item.get("category") == category]
    if region:
        updates = [
            item
            for item in updates
            if region.lower() in str(item.get("region") or "").lower()
            or region.lower() in str(item.get("applicable_in") or "").lower()
        ]

    return {
        "updates": updates[:limit],
        "total": len(updates),
        "last_sync": datetime.now(timezone.utc).isoformat(),
        "sources": _normalize_sources(updates),
    }


@router.get("/dashboard")
async def get_legal_dashboard(
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    updates = await legal_service.get_all_updates()
    recent_updates = updates[:6]
    categories = {item.get("category") for item in updates if item.get("category")}
    regions = {item.get("region") for item in updates if item.get("region")}

    return {
        "ok": True,
        "stats": {
            "total_laws": len(updates),
            "regions_covered": len(regions),
            "topics_covered": len(categories),
            "contracts_reviewed": 0,
            "canadian_updates": len(recent_updates),
        },
        "coverage": {
            "official_sources": len(_normalize_sources(updates)),
            "live_feeds": 1,
            "canadian_updates": len(recent_updates),
            "road_events": len([item for item in updates if item.get("live")]),
        },
        "common_queries": [
            "Ontario Regulation 161/25",
            "CBSA CARM requirements",
            "Canada Transportation Act",
            "DriveBC road restrictions",
        ],
        "recent_searches": [],
        "recent_updates": recent_updates,
        "active_sources": _normalize_sources(updates),
        "subscription_status": {
            "real_time": True,
            "update_frequency": "On request",
            "next_scheduled": (datetime.now(timezone.utc) + timedelta(minutes=10)).isoformat(),
        },
    }


@router.get("/categories")
async def get_legal_categories(
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    return {
        "categories": [
            {"value": "regulation", "label": "Government Regulations"},
            {"value": "safety", "label": "Safety Standards"},
            {"value": "customs", "label": "Customs & Border"},
            {"value": "trade", "label": "Trade & Transport"},
        ]
    }


@router.post("/search")
async def search_legal_content(
    payload: LegalSearchRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    results = await legal_service.search(
        query=payload.query,
        category=payload.category,
        region=payload.region,
        limit=payload.limit,
    )
    return {
        "query": payload.query,
        "results": results,
        "total": len(results),
    }


@router.get("/regulation/{regulation_id}")
async def get_regulation_detail(
    regulation_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    updates = await legal_service.get_all_updates()
    regulation = next((item for item in updates if item.get("id") == regulation_id), None)
    if not regulation:
        raise HTTPException(status_code=404, detail="Regulation not found")
    return regulation


@router.get("/road/restrictions")
async def get_road_restrictions(
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    events = await legal_service.fetch_open511_events(limit=10)
    return {
        "events": events,
        "source": "DriveBC Open511",
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "note": "Real-time data from the British Columbia Open511 feed.",
    }

