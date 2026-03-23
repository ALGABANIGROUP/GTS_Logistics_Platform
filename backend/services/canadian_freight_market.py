from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Dict

logger = logging.getLogger(__name__)


class CanadianFreightMarketService:
    """Lightweight Canadian market rate service.

    Provides static fallback data so freight market routes can boot even when
    upstream integrations are not wired.
    """

    cache_duration = 3600

    def __init__(self) -> None:
        self._initialized = False
        self._market_data: Dict[str, Dict[str, Any]] = {}

    async def initialize(self) -> None:
        if self._initialized:
            return
        self._market_data = self._build_static_rates()
        self._initialized = True
        logger.info("CanadianFreightMarketService initialized with %s corridors", len(self._market_data))

    async def shutdown(self) -> None:
        self._initialized = False
        self._market_data = {}

    async def get_current_market_data(self) -> Dict[str, Dict[str, Any]]:
        if not self._initialized:
            await self.initialize()
        return self._market_data

    async def generate_intelligence_report(self) -> Dict[str, Any]:
        return {
            "market_overview": {
                "trend": "stable",
                "note": "Static fallback rates in use",
            },
            "anomalies_detected": {
                "count": 0,
                "details": {},
            },
        }

    async def calculate_profitability_score(self, corridor_data: Dict[str, Any]) -> float:
        rate = float(corridor_data.get("rate_per_km") or 0)
        volatility = float(corridor_data.get("volatility_index") or 0)
        base = min(1.0, max(0.0, rate / 5.0))
        return round(max(0.0, base - volatility * 0.1), 3)

    def _build_static_rates(self) -> Dict[str, Dict[str, Any]]:
        now = datetime.now(timezone.utc).isoformat()
        return {
            "toronto_vancouver": {
                "corridor_id": "TOR-VAN",
                "name": "Toronto - Vancouver",
                "origin": "Toronto, ON",
                "origin_province": "ON",
                "destination": "Vancouver, BC",
                "destination_province": "BC",
                "highway": "Trans-Canada Hwy",
                "distance_km": 4360.0,
                "rate_per_km": 2.95,
                "total_trip_cost": 12862.0,
                "currency": "CAD",
                "unit": "kilometer",
                "base_rate_per_km": 2.75,
                "trend": {"direction": "stable", "change_pct": 0.0},
                "volatility_index": 0.12,
                "data_quality": "fallback",
                "cargo_types": ["general", "dry_van"],
                "typical_transit_days": 5.5,
                "seasonal_adjustment": 1.0,
                "updated_at": now,
                "data_sources": ["fallback"],
            },
            "montreal_calgary": {
                "corridor_id": "MTL-CGY",
                "name": "Montreal - Calgary",
                "origin": "Montreal, QC",
                "origin_province": "QC",
                "destination": "Calgary, AB",
                "destination_province": "AB",
                "highway": "Trans-Canada Hwy",
                "distance_km": 3690.0,
                "rate_per_km": 2.65,
                "total_trip_cost": 9789.0,
                "currency": "CAD",
                "unit": "kilometer",
                "base_rate_per_km": 2.5,
                "trend": {"direction": "up", "change_pct": 1.2},
                "volatility_index": 0.15,
                "data_quality": "fallback",
                "cargo_types": ["general", "reefer"],
                "typical_transit_days": 4.8,
                "seasonal_adjustment": 1.02,
                "updated_at": now,
                "data_sources": ["fallback"],
            },
            "toronto_montreal": {
                "corridor_id": "TOR-MTL",
                "name": "Toronto - Montreal",
                "origin": "Toronto, ON",
                "origin_province": "ON",
                "destination": "Montreal, QC",
                "destination_province": "QC",
                "highway": "Hwy 401",
                "distance_km": 542.0,
                "rate_per_km": 2.1,
                "total_trip_cost": 1138.0,
                "currency": "CAD",
                "unit": "kilometer",
                "base_rate_per_km": 2.0,
                "trend": {"direction": "down", "change_pct": -0.8},
                "volatility_index": 0.08,
                "data_quality": "fallback",
                "cargo_types": ["general", "ltl"],
                "typical_transit_days": 1.1,
                "seasonal_adjustment": 0.98,
                "updated_at": now,
                "data_sources": ["fallback"],
            },
        }
