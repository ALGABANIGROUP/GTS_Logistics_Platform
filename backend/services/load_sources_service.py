"""
Load Sources Service - Intelligent Freight Source Discovery
Provides smart search and filtering for freight sources including load boards,
warehouses, 3PL providers, and logistics partners in Canada and North America.
"""
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class SourceType(str, Enum):
    """Types of freight sources"""
    LOAD_BOARD = "load_board"
    WAREHOUSE_DIRECTORY = "warehouse_directory"
    WAREHOUSE_PROVIDER = "warehouse_provider"
    LOGISTICS_PROVIDER = "logistics_provider"
    FREIGHT_CARRIER = "freight_carrier"
    SHIPPING_PARTNER = "shipping_partner"
    FULFILLMENT_PROVIDER = "fulfillment_provider"
    DIRECTORY = "directory"
    ALL = "all"


class Country(str, Enum):
    """Geographic locations"""
    CANADA = "Canada"
    USA = "USA"
    NORTH_AMERICA = "North America"
    ALL = "all"


# Load Sources Database
LOAD_SOURCES = [
    {
        "name": "Logistware",
        "website": "https://www.logistware.ca",
        "email": "customerservice@logistware.ca",
        "description": "Canada load board where shippers book faster and carriers win more bids. Verified Canadian loads with SHA recognition.",
        "type": "load_board",
        "country": "Canada",
        "verified": True,
    },
    {
        "name": "Multi Action",
        "website": "https://www.multiaction.ca",
        "email": "jfortin@multiaction.ca",
        "phone": "(418) 660-1180, poste 237",
        "description": "Shipping Department - Multi Action. Hours: 7AM to 4PM (Closed 12-1PM). Address: 6890 boulevard Ste-Anne, L'Ange-Gardien, QC G0A 2K0 Canada",
        "type": "shipping_partner",
        "country": "Canada",
        "verified": True,
    },
    {
        "name": "UShip Canada",
        "website": "https://www.uship.com/ca/",
        "email": None,
        "description": "UShip Canada - Online marketplace for shipping and logistics services.",
        "type": "load_board",
        "country": "Canada",
        "verified": True,
    },
    {
        "name": "DAT Load Board",
        "website": "https://www.dat.com/find-truck-loads",
        "email": None,
        "description": "DAT - Find truck loads and manage your trucking business. Largest load board with real-time freight matching.",
        "type": "load_board",
        "country": "North America",
        "verified": True,
    },
    {
        "name": "PickATruckLoad",
        "website": "https://www.pickatruckload.com",
        "email": None,
        "description": "Load board source for freight and shipping opportunities.",
        "type": "load_board",
        "country": "North America",
        "verified": True,
    },
    {
        "name": "Freightera",
        "website": "https://www.freightera.com",
        "email": "clientcare@freightera.com",
        "phone": "(800) 886-4870",
        "description": "Canadian freight and logistics marketplace. Hours: 5:30 AM – 5:00 PM PST Mon-Fri. Office: 408 – 55 Water Street, Vancouver, BC V6B 1A1, Canada. Accounting: Ext. 4",
        "type": "load_board",
        "country": "Canada",
        "verified": True,
    },
    {
        "name": "Warehouse Discovery",
        "website": "https://warehousediscovery.com/",
        "email": None,
        "description": "Warehouse Services Directory (Canada) - Contract & fulfillment warehouses, refrigerated storage, 3PL providers.",
        "type": "warehouse_directory",
        "country": "Canada",
        "verified": True,
    },
    {
        "name": "CIREA - Warehouse Locator",
        "website": "https://www.cirea.ca/warehouse-locator",
        "email": "info@cirea.ca",
        "description": "Canadian Industrial Real Estate Affiliation warehouse locator. Find general warehouses, refrigerated storage, co-packing, fulfillment & 3PL in major cities (Vancouver, Toronto, Montreal, Calgary).",
        "type": "warehouse_directory",
        "country": "Canada",
        "verified": True,
    },
    {
        "name": "Scott's Directories - Warehouse & 3PL",
        "website": "https://www.scottsdirectories.com/list-of-warehouse-companies-in-canada/",
        "email": None,
        "description": "Directory of thousands of logistics, 3PL, and warehouse companies in Canada with contact data, industry, locations, storage services, and transportation options.",
        "type": "directory",
        "country": "Canada",
        "verified": True,
    },
    {
        "name": "GoodFirms - Warehousing Companies Canada",
        "website": "https://www.goodfirms.co/supply-chain-logistics-companies/warehousing/canada",
        "email": None,
        "description": "List of top-rated warehousing and fulfillment companies in Canada (2026) with detailed reviews and ratings.",
        "type": "directory",
        "country": "Canada",
        "verified": True,
    },
    {
        "name": "VersaCold",
        "website": "https://www.foodlogistics.com/warehousing/cold-storage/company/21578449/versacold",
        "email": "mmayer@iron.markets",
        "phone": "647-296-5014",
        "description": "Largest temperature-sensitive warehouse network in Canada. Provider of refrigerated storage and cold chain logistics. Contact: Marina Mayer (mmayer@iron.markets), Brian Hines (bhines@iron.markets), Susan Joyce (sjoyce@iron.markets)",
        "type": "warehouse_provider",
        "country": "Canada",
        "verified": True,
    },
    {
        "name": "Congebec Logistics",
        "website": "https://congebec.com/en/",
        "email": None,
        "phone": "1 877 683-3491",
        "description": "Storage, distribution, and cold transport services. Multi-temperature warehouse and logistics provider in Canada. Head Office: 810, avenue Godin, Québec, QC G1M 2X9. Phone: 418 683-3491, Fax: 418 683-6387",
        "type": "warehouse_provider",
        "country": "Canada",
        "verified": True,
    },
    {
        "name": "DelGate",
        "website": "https://delgate.ca",
        "email": "rates@delgate.ca",
        "phone": "+1 833-335-4283",
        "description": "3PL and distribution company offering warehouses and shipping services in Canada. Located at Unit1 - 403 East Kent Ave North, Vancouver BC. Sales: rates@delgate.ca, Order Help: help@delgate.ca, Alt Phone: 778-340-1111",
        "type": "warehouse_provider",
        "country": "Canada",
        "verified": True,
    },
    {
        "name": "MTS Logistics",
        "website": "https://mtslogistics.com",
        "email": "info@mtslogistics.com",
        "description": "Canadian logistics and transportation services provider.",
        "type": "logistics_provider",
        "country": "Canada",
        "verified": True,
    },
    {
        "name": "Canadian Freightways",
        "website": "https://canadianfreightways.com",
        "email": "info@canadianfreightways.com",
        "description": "Canadian freight transportation and logistics company.",
        "type": "freight_carrier",
        "country": "Canada",
        "verified": True,
    },
    {
        "name": "Trans Logistics",
        "website": "https://translogistics.com",
        "email": "info@translogistics.com",
        "description": "Transportation and logistics services provider in Canada.",
        "type": "logistics_provider",
        "country": "Canada",
        "verified": True,
    },
    {
        "name": "Cascades",
        "website": "https://www.cascades.com",
        "email": "info@cascades.com",
        "description": "Canadian packaging and logistics solutions provider.",
        "type": "logistics_provider",
        "country": "Canada",
        "verified": True,
    },
    {
        "name": "Supply Chain Canada",
        "website": "https://www.supplychaincanada.com",
        "email": "info@supplychaincanada.com",
        "description": "Supply chain management and logistics services in Canada.",
        "type": "logistics_provider",
        "country": "Canada",
        "verified": True,
    },
    {
        "name": "WCP Logistics",
        "website": "https://wcplogistics.com",
        "email": "info@wcplogistics.com",
        "description": "Warehouse and logistics services provider in Canada.",
        "type": "logistics_provider",
        "country": "Canada",
        "verified": True,
    },
]


class LoadSourcesService:
    """Service for intelligent load sources discovery and management"""

    def __init__(self):
        self.sources = LOAD_SOURCES
        logger.info(f"[LoadSourcesService] Initialized with {len(self.sources)} sources")

    async def search_sources(
        self,
        query: Optional[str] = None,
        source_type: Optional[str] = None,
        country: Optional[str] = None,
        verified_only: bool = False,
        limit: int = 20
    ) -> Dict[str, Any]:
        """
        Smart search for freight sources
        
        Args:
            query: Search query (name, description, email)
            source_type: Filter by source type
            country: Filter by country
            verified_only: Only return verified sources
            limit: Maximum results to return
            
        Returns:
            Dictionary with search results and metadata
        """
        try:
            filtered = self.sources.copy()
            
            # Filter by source type
            if source_type and source_type != "all":
                filtered = [s for s in filtered if s.get("type") == source_type]
            
            # Filter by country
            if country and country != "all":
                filtered = [s for s in filtered if s.get("country") == country]
            
            # Filter by verified status
            if verified_only:
                filtered = [s for s in filtered if s.get("verified", False)]
            
            # Search query
            if query:
                query_lower = query.lower()
                filtered = [
                    s for s in filtered
                    if query_lower in s.get("name", "").lower()
                    or query_lower in s.get("description", "").lower()
                    or query_lower in str(s.get("email", "")).lower()
                ]
            
            # Limit results
            results = filtered[:limit]
            
            return {
                "ok": True,
                "sources": results,
                "total": len(results),
                "filtered_from": len(filtered),
                "total_available": len(self.sources),
                "filters_applied": {
                    "query": query,
                    "source_type": source_type,
                    "country": country,
                    "verified_only": verified_only
                },
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"[LoadSourcesService] Search error: {e}")
            return {
                "ok": False,
                "error": str(e),
                "sources": [],
                "total": 0
            }

    async def get_source_by_name(self, name: str) -> Optional[Dict]:
        """Get a specific source by name"""
        for source in self.sources:
            if source.get("name", "").lower() == name.lower():
                return source
        return None

    async def get_sources_by_type(self, source_type: str) -> List[Dict]:
        """Get all sources of a specific type"""
        return [s for s in self.sources if s.get("type") == source_type]

    async def get_canadian_sources(self) -> List[Dict]:
        """Get all Canadian sources"""
        return [s for s in self.sources if s.get("country") == "Canada"]

    async def get_load_boards(self) -> List[Dict]:
        """Get all load board sources"""
        return await self.get_sources_by_type("load_board")

    async def get_warehouse_providers(self) -> List[Dict]:
        """Get all warehouse providers"""
        return [s for s in self.sources if "warehouse" in s.get("type", "")]

    async def get_source_stats(self) -> Dict[str, Any]:
        """Get statistics about available sources"""
        stats = {
            "total_sources": len(self.sources),
            "by_type": {},
            "by_country": {},
            "verified_count": sum(1 for s in self.sources if s.get("verified", False)),
            "with_email": sum(1 for s in self.sources if s.get("email")),
            "with_phone": sum(1 for s in self.sources if s.get("phone")),
        }
        
        # Count by type
        for source in self.sources:
            source_type = source.get("type", "unknown")
            stats["by_type"][source_type] = stats["by_type"].get(source_type, 0) + 1
        
        # Count by country
        for source in self.sources:
            country = source.get("country", "unknown")
            stats["by_country"][country] = stats["by_country"].get(country, 0) + 1
        
        return stats

    async def smart_recommendations(
        self,
        requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Get smart recommendations based on specific requirements
        
        Args:
            requirements: Dict with keys like 'need_cold_storage', 'need_3pl',
                         'region', 'equipment_type', etc.
        """
        recommendations = []
        
        # Example smart recommendation logic
        if requirements.get("need_cold_storage"):
            cold_storage = [s for s in self.sources if "refrigerat" in s.get("description", "").lower() or "cold" in s.get("description", "").lower()]
            recommendations.extend(cold_storage)
        
        if requirements.get("need_3pl"):
            three_pl = [s for s in self.sources if "3pl" in s.get("description", "").lower() or s.get("type") == "logistics_provider"]
            recommendations.extend(three_pl)
        
        if requirements.get("need_load_board"):
            load_boards = await self.get_load_boards()
            recommendations.extend(load_boards)
        
        # Remove duplicates
        unique_recs = []
        seen_names = set()
        for rec in recommendations:
            if rec.get("name") not in seen_names:
                unique_recs.append(rec)
                seen_names.add(rec.get("name"))
        
        return {
            "ok": True,
            "recommendations": unique_recs,
            "count": len(unique_recs),
            "based_on": requirements,
            "timestamp": datetime.utcnow().isoformat()
        }


# Global service instance
load_sources_service = LoadSourcesService()


__all__ = [
    "LoadSourcesService",
    "load_sources_service",
    "SourceType",
    "Country",
    "LOAD_SOURCES"
]
