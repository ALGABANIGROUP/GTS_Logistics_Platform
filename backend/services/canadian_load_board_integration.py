"""
Canadian Load Board Integration Service
Connects to TruckerPath, DAT, Loadlink, and Canadian freight data sources
"""

import aiohttp
import asyncio
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class CanadianLoadBoardIntegration:
    """
    Integration service for Canadian and cross-border freight load boards
    
    Supported Platforms:
    - TruckerPath API (North America)
    - DAT One Load Board (US/Canada)
    - Loadlink (Canadian specific)
    - TruckMiles (Canadian routes)
    """
    
    def __init__(self):
        self.truckerpath_api_key = None
        self.dat_api_key = None
        self.loadlink_api_key = None
        self.truckmiles_api_key = None
        
        self.base_urls = {
            "truckerpath": "https://api.truckerpath.com/v1",
            "dat": "https://api.dat.com/v3",
            "loadlink": "https://api.loadlink.ca/v1",
            "truckmiles": "https://api.truckmiles.com/v1"
        }
    
    async def search_loads(
        self,
        origin: Optional[str] = None,
        destination: Optional[str] = None,
        trailer_type: Optional[str] = None,
        min_weight: int = 0,
        max_weight: int = 100000,
        equipment: Optional[str] = None
    ) -> List[Dict]:
        """
        Search for loads across all integrated platforms
        Returns aggregated results from multiple sources
        """
        
        tasks = [
            self._fetch_truckerpath_loads(origin, destination, trailer_type),
            self._fetch_dat_loads(origin, destination, trailer_type),
            self._fetch_loadlink_loads(origin, destination, trailer_type),
            self._fetch_truckmiles_loads(origin, destination, trailer_type)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Aggregate and deduplicate loads
        all_loads = []
        for result in results:
            if isinstance(result, list):
                all_loads.extend(result)
        
        # Sort by rate and relevance
        return self._rank_and_filter_loads(all_loads, origin, destination)
    
    async def _fetch_truckerpath_loads(
        self, 
        origin: Optional[str], 
        destination: Optional[str],
        trailer_type: Optional[str]
    ) -> List[Dict]:
        """
        Fetch loads from TruckerPath API
        
        API Documentation: https://truckerpath.com/developers
        """
        
        if not self.truckerpath_api_key:
            logger.warning("TruckerPath API key not configured")
            return []
        
        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    "origin": origin,
                    "destination": destination,
                    "equipment_type": trailer_type,
                    "api_key": self.truckerpath_api_key
                }
                
                async with session.get(
                    f"{self.base_urls['truckerpath']}/loads/search",
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._normalize_truckerpath_data(data)
                    else:
                        logger.error(f"TruckerPath API error: {response.status}")
                        return []
                        
        except Exception as e:
            logger.error(f"TruckerPath fetch error: {str(e)}")
            return []
    
    async def _fetch_dat_loads(
        self, 
        origin: Optional[str], 
        destination: Optional[str],
        trailer_type: Optional[str]
    ) -> List[Dict]:
        """
        Fetch loads from DAT One Load Board
        
        API Documentation: https://www.dat.com/api
        """
        
        if not self.dat_api_key:
            logger.warning("DAT API key not configured")
            return []
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.dat_api_key}",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "origin": origin,
                    "destination": destination,
                    "equipment_type": trailer_type,
                    "search_radius": 150
                }
                
                async with session.post(
                    f"{self.base_urls['dat']}/loads/search",
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._normalize_dat_data(data)
                    else:
                        logger.error(f"DAT API error: {response.status}")
                        return []
                        
        except Exception as e:
            logger.error(f"DAT fetch error: {str(e)}")
            return []
    
    async def _fetch_loadlink_loads(
        self, 
        origin: Optional[str], 
        destination: Optional[str],
        trailer_type: Optional[str]
    ) -> List[Dict]:
        """
        Fetch loads from Loadlink (Canadian specific)
        
        API Documentation: https://loadlink.ca/api-docs
        """
        
        if not self.loadlink_api_key:
            logger.warning("Loadlink API key not configured")
            return []
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "X-API-Key": self.loadlink_api_key,
                    "Content-Type": "application/json"
                }
                
                params = {
                    "origin_province": origin,
                    "destination": destination,
                    "trailer_type": trailer_type
                }
                
                async with session.get(
                    f"{self.base_urls['loadlink']}/loads",
                    params=params,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._normalize_loadlink_data(data)
                    else:
                        logger.error(f"Loadlink API error: {response.status}")
                        return []
                        
        except Exception as e:
            logger.error(f"Loadlink fetch error: {str(e)}")
            return []
    
    async def _fetch_truckmiles_loads(
        self, 
        origin: Optional[str], 
        destination: Optional[str],
        trailer_type: Optional[str]
    ) -> List[Dict]:
        """
        Fetch loads from TruckMiles (Canadian routes)
        
        API Documentation: https://truckmiles.com/api
        """
        
        if not self.truckmiles_api_key:
            logger.warning("TruckMiles API key not configured")
            return []
        
        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    "pickup": origin,
                    "delivery": destination,
                    "equipment": trailer_type,
                    "key": self.truckmiles_api_key
                }
                
                async with session.get(
                    f"{self.base_urls['truckmiles']}/freight/search",
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._normalize_truckmiles_data(data)
                    else:
                        logger.error(f"TruckMiles API error: {response.status}")
                        return []
                        
        except Exception as e:
            logger.error(f"TruckMiles fetch error: {str(e)}")
            return []
    
    def _normalize_truckerpath_data(self, data: Dict) -> List[Dict]:
        """Normalize TruckerPath API response to unified format"""
        loads = []
        for item in data.get('loads', []):
            loads.append({
                "source": "TruckerPath",
                "load_id": item.get('id'),
                "pickup": item.get('origin', {}).get('city'),
                "pickup_province": item.get('origin', {}).get('state'),
                "dropoff": item.get('destination', {}).get('city'),
                "dropoff_province": item.get('destination', {}).get('state'),
                "distance": item.get('distance_miles'),
                "rate_cad": item.get('rate_usd', 0) * 1.35,  # USD to CAD conversion
                "trailer": item.get('equipment_type'),
                "weight": item.get('weight_lbs'),
                "broker": item.get('company_name'),
                "phone": item.get('contact_phone'),
                "posted_age": item.get('age')
            })
        return loads
    
    def _normalize_dat_data(self, data: Dict) -> List[Dict]:
        """Normalize DAT One API response to unified format"""
        loads = []
        for item in data.get('results', []):
            loads.append({
                "source": "DAT",
                "load_id": item.get('loadId'),
                "pickup": item.get('origin', {}).get('city'),
                "pickup_province": item.get('origin', {}).get('state'),
                "dropoff": item.get('destination', {}).get('city'),
                "dropoff_province": item.get('destination', {}).get('state'),
                "distance": item.get('miles'),
                "rate_cad": item.get('lineHaulRate', 0) * 1.35,
                "trailer": item.get('equipmentType'),
                "weight": item.get('weight'),
                "broker": item.get('companyName'),
                "phone": item.get('phoneNumber'),
                "posted_age": item.get('age')
            })
        return loads
    
    def _normalize_loadlink_data(self, data: Dict) -> List[Dict]:
        """Normalize Loadlink API response to unified format"""
        loads = []
        for item in data.get('loads', []):
            loads.append({
                "source": "Loadlink",
                "load_id": item.get('load_number'),
                "pickup": item.get('pickup_city'),
                "pickup_province": item.get('pickup_province'),
                "dropoff": item.get('delivery_city'),
                "dropoff_province": item.get('delivery_province'),
                "distance": item.get('distance_km') * 0.621371,  # km to miles
                "rate_cad": item.get('rate_cad'),
                "trailer": item.get('trailer_type'),
                "weight": item.get('weight_lbs'),
                "broker": item.get('broker_name'),
                "phone": item.get('contact_phone'),
                "posted_age": item.get('hours_posted', 0)
            })
        return loads
    
    def _normalize_truckmiles_data(self, data: Dict) -> List[Dict]:
        """Normalize TruckMiles API response to unified format"""
        loads = []
        for item in data.get('freight', []):
            loads.append({
                "source": "TruckMiles",
                "load_id": item.get('id'),
                "pickup": item.get('pickup_location'),
                "pickup_province": item.get('pickup_region'),
                "dropoff": item.get('delivery_location'),
                "dropoff_province": item.get('delivery_region'),
                "distance": item.get('total_miles'),
                "rate_cad": item.get('rate_cad'),
                "trailer": item.get('equipment'),
                "weight": item.get('weight'),
                "broker": item.get('carrier'),
                "phone": item.get('phone'),
                "posted_age": item.get('posted')
            })
        return loads
    
    def _rank_and_filter_loads(
        self,
        loads: List[Dict],
        origin: Optional[str],
        destination: Optional[str]
    ) -> List[Dict]:
        """Rank loads by relevance and profitability"""
        
        # Calculate profit score for each load
        for load in loads:
            distance = load.get('distance', 0)
            rate = load.get('rate_cad', 0)
            
            if distance > 0:
                rate_per_mile = rate / distance
                operating_cost_per_mile = 2.00  # CAD average
                profit_per_mile = rate_per_mile - operating_cost_per_mile
                
                load['rate_per_mile'] = rate_per_mile
                load['profit_score'] = profit_per_mile * distance
            else:
                load['profit_score'] = 0
        
        # Sort by profit score (highest first)
        loads.sort(key=lambda x: x.get('profit_score', 0), reverse=True)
        
        return loads

    async def get_market_rates(
        self,
        origin_province: str,
        destination_province: str,
        trailer_type: str
    ) -> Dict:
        """
        Get current market rates for specific lane
        
        Data sources:
        - Canadian Freight Index
        - Provincial trucking associations
        - Historical rate data
        """
        
        # Mock implementation - replace with real market data API
        return {
            "lane": f"{origin_province} → {destination_province}",
            "trailer_type": trailer_type,
            "spot_rate_cad_per_mile": {
                "average": 2.45,
                "low": 2.10,
                "high": 2.85
            },
            "contract_rate_cad_per_mile": 2.15,
            "trend": "stable",
            "volume_index": 78,  # 0-100 scale
            "last_updated": datetime.utcnow().isoformat()
        }
    
    async def find_backhaul_opportunities(
        self,
        current_location: str,
        home_base: str,
        trailer_type: str,
        date_range: int = 3
    ) -> List[Dict]:
        """
        Find backhaul opportunities for return trips
        Helps minimize empty miles
        """
        
        # Search for loads from current location back to home base
        return await self.search_loads(
            origin=current_location,
            destination=home_base,
            trailer_type=trailer_type
        )

# Singleton instance
canadian_load_board = CanadianLoadBoardIntegration()
