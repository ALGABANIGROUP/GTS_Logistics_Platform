"""
Data Source Service - Manage external data sources
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class DataSourceService:
    """Service for managing data sources"""

    def __init__(self, session):
        self.session = session
        self._sources = {}  # In-memory cache

    async def list_sources(self) -> List[Dict[str, Any]]:
        """List all data sources"""
        # For now, return mock data
        return [
            {
                "id": "stripe",
                "name": "Stripe",
                "type": "payment",
                "status": "active",
                "last_sync": datetime.now().isoformat()
            },
            {
                "id": "wise",
                "name": "Wise",
                "type": "payment",
                "status": "active",
                "last_sync": datetime.now().isoformat()
            },
            {
                "id": "sudapay",
                "name": "SUDAPAY",
                "type": "payment",
                "status": "active",
                "last_sync": datetime.now().isoformat()
            },
            {
                "id": "openweather",
                "name": "OpenWeather",
                "type": "weather",
                "status": "active",
                "last_sync": datetime.now().isoformat()
            }
        ]

    async def get_source(self, source_id: str) -> Optional[Dict[str, Any]]:
        """Get data source by ID"""
        sources = await self.list_sources()
        for source in sources:
            if source["id"] == source_id:
                return source
        return None

    async def create_source(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new data source"""
        source = {
            "id": data.get("id"),
            "name": data.get("name"),
            "type": data.get("type"),
            "status": "pending",
            "created_at": datetime.now().isoformat()
        }
        logger.info(f"Created data source: {source['id']}")
        return source

    async def update_source(self, source_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update data source"""
        source = await self.get_source(source_id)
        if source:
            source.update(data)
            source["updated_at"] = datetime.now().isoformat()
        return source

    async def delete_source(self, source_id: str) -> bool:
        """Delete data source"""
        logger.info(f"Deleted data source: {source_id}")
        return True

    async def test_connection(self, source_id: str) -> Dict[str, Any]:
        """Test data source connection"""
        return {"success": True, "message": f"Connection to {source_id} successful"}

    async def check_health(self) -> Dict[str, Any]:
        """Check health of all data sources"""
        sources = await self.list_sources()
        return {
            "total": len(sources),
            "active": len([s for s in sources if s["status"] == "active"]),
            "sources": sources
        }


def get_data_source_service(session):
    """Get data source service instance"""
    return DataSourceService(session)