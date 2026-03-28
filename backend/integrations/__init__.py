from __future__ import annotations

from backend.integrations.base import BaseProvider, ProviderConfig
from backend.integrations.mapleload import MapleLoadProvider
from backend.integrations.truckerpath import TruckerPathProvider
from backend.integrations.wise import WiseProvider

__all__ = [
    "BaseProvider",
    "MapleLoadProvider",
    "ProviderConfig",
    "TruckerPathProvider",
    "WiseProvider",
    "create_provider",
]


def create_provider(provider_name: str, config: ProviderConfig) -> BaseProvider:
    """Create a concrete provider instance by integration name."""
    providers = {
        "mapleload": MapleLoadProvider,
        "truckerpath": TruckerPathProvider,
        "wise": WiseProvider,
    }

    provider_class = providers.get((provider_name or "").lower())
    if provider_class is None:
        raise ValueError(f"Unknown provider type: {provider_name}")

    return provider_class(config)
