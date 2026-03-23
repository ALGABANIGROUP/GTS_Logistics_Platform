# backend/core/feature_flags.py
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Set


class Region(str, Enum):
    GCC = "GCC"
    EGYPT = "EGYPT"
    NA = "NA"  # North America (US/CA)
    GLOBAL = "GLOBAL"


class Mode(str, Enum):
    TMS = "TMS"
    HYBRID = "HYBRID"  # TMS + optional Load Board
    LOAD_BOARD = "LOAD_BOARD"  # future-ready, not default


class Feature(str, Enum):
    AI_DISPATCHER = "AI_DISPATCHER"
    PRICING_ENGINE = "PRICING_ENGINE"
    ROUTING_AI = "ROUTING_AI"
    CARRIER_SELECTION_AI = "CARRIER_SELECTION_AI"
    RISK_DELAY_PREDICTOR = "RISK_DELAY_PREDICTOR"

    FLEET_MANAGEMENT = "FLEET_MANAGEMENT"
    INTERNAL_ASSIGNMENT = "INTERNAL_ASSIGNMENT"
    CONTRACTS = "CONTRACTS"
    INVOICING = "INVOICING"

    LOAD_BOARD = "LOAD_BOARD"
    SPOT_MARKET = "SPOT_MARKET"
    EXTERNAL_APIS = "EXTERNAL_APIS"


@dataclass(frozen=True)
class RegionConfig:
    region: Region
    mode: Mode
    enabled: Set[Feature]
    disabled: Set[Feature]


# ---------------------------------------------------------------------
# Defaults: Designed to match your "TMS + AI" direction
# ---------------------------------------------------------------------
DEFAULTS: Dict[Region, RegionConfig] = {
    Region.GCC: RegionConfig(
        region=Region.GCC,
        mode=Mode.TMS,
        enabled={
            Feature.AI_DISPATCHER,
            Feature.PRICING_ENGINE,
            Feature.ROUTING_AI,
            Feature.CARRIER_SELECTION_AI,
            Feature.RISK_DELAY_PREDICTOR,
            Feature.FLEET_MANAGEMENT,
            Feature.INTERNAL_ASSIGNMENT,
            Feature.CONTRACTS,
            Feature.INVOICING,
        },
        disabled={
            Feature.LOAD_BOARD,
            Feature.SPOT_MARKET,
        },
    ),
    Region.EGYPT: RegionConfig(
        region=Region.EGYPT,
        mode=Mode.TMS,
        enabled={
            Feature.AI_DISPATCHER,
            Feature.PRICING_ENGINE,
            Feature.ROUTING_AI,
            Feature.CARRIER_SELECTION_AI,
            Feature.RISK_DELAY_PREDICTOR,
            Feature.FLEET_MANAGEMENT,
            Feature.INTERNAL_ASSIGNMENT,
            Feature.CONTRACTS,
            Feature.INVOICING,
        },
        disabled={
            Feature.LOAD_BOARD,
            Feature.SPOT_MARKET,
        },
    ),
    Region.NA: RegionConfig(
        region=Region.NA,
        mode=Mode.HYBRID,
        enabled={
            Feature.AI_DISPATCHER,
            Feature.PRICING_ENGINE,
            Feature.ROUTING_AI,
            Feature.CARRIER_SELECTION_AI,
            Feature.RISK_DELAY_PREDICTOR,
            Feature.FLEET_MANAGEMENT,
            Feature.INTERNAL_ASSIGNMENT,
            Feature.CONTRACTS,
            Feature.INVOICING,
            Feature.LOAD_BOARD,
        },
        disabled={
            Feature.SPOT_MARKET,  # keep off by default
        },
    ),
    Region.GLOBAL: RegionConfig(
        region=Region.GLOBAL,
        mode=Mode.TMS,
        enabled={
            Feature.AI_DISPATCHER,
            Feature.PRICING_ENGINE,
            Feature.ROUTING_AI,
            Feature.CARRIER_SELECTION_AI,
            Feature.RISK_DELAY_PREDICTOR,
            Feature.FLEET_MANAGEMENT,
            Feature.INTERNAL_ASSIGNMENT,
            Feature.CONTRACTS,
            Feature.INVOICING,
        },
        disabled={
            Feature.LOAD_BOARD,
            Feature.SPOT_MARKET,
        },
    ),
}


def normalize_region(value: str | None) -> Region:
    if not value:
        return Region.GLOBAL
    v = value.strip().upper()
    if v in ("GCC", "GULF", "UAE", "KSA", "SAUDI", "QATAR", "OMAN", "BAHRAIN", "KUWAIT"):
        return Region.GCC
    if v in ("EG", "EGYPT"):
        return Region.EGYPT
    if v in ("NA", "US", "USA", "CA", "CANADA", "NORTH_AMERICA"):
        return Region.NA
    return Region.GLOBAL


def region_config(region: Region) -> RegionConfig:
    return DEFAULTS.get(region, DEFAULTS[Region.GLOBAL])


def is_enabled(region: Region, feature: Feature) -> bool:
    cfg = region_config(region)
    if feature in cfg.disabled:
        return False
    return feature in cfg.enabled


def mode_for_region(region: Region) -> Mode:
    return region_config(region).mode


def features_for_region(region: Region) -> dict:
    cfg = region_config(region)
    return {
        "region": cfg.region.value,
        "mode": cfg.mode.value,
        "enabled": sorted([f.value for f in cfg.enabled]),
        "disabled": sorted([f.value for f in cfg.disabled]),
    }
