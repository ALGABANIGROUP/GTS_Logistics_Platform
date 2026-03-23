# backend/tools/open_web_leads/adapters/base.py

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List
from datetime import datetime

from ..schemas import OpenWebLeadCreate


class BaseOpenWebLeadAdapter(ABC):
    """
    Every lead source (website) should inherit from this class
    and implement exactly one method: fetch_leads().
    
    The purpose of this base class is to standardize how different
    web sources provide new freight/shipment leads into the system.
    """

    # Example: "acme-logistics.com"
    "freightera.com"
    source_name: str

    @abstractmethod
    async def fetch_leads(self) -> List[OpenWebLeadCreate]:
        """
        Fetch and return a list of OpenWebLeadCreate objects collected
        from this specific source.

        Each subclass must implement this method.
        """
        ...
