"""
Traffic Analysis System - Real-time traffic monitoring and prediction
Analyzes congestion, accidents, and traffic patterns
"""

import aiohttp
import asyncio
from typing import List, Dict, Optional
from datetime import datetime
import logging
from math import radians, sin, cos, sqrt, atan2

logger = logging.getLogger(__name__)


class TrafficAnalyzer:
    """Advanced traffic analysis and prediction engine"""
    
    def __init__(self):
        self.api_key = "demo_traffic_key"
        self.base_url = "https://api.trafficdata.com/v1"
        self.cached_data = {}
        self.cache_expiry = {}
        
    async def analyze_route(self, coordinates: List[List[float]]) -> Dict:
        """Analyze traffic conditions on given route"""
        
        try:
            # Get traffic data
            traffic_data = await self.get_traffic_data(coordinates)
            
            # Analyze congestion
            congestion_analysis = self.analyze_congestion(traffic_data)
            
            # Analyze accidents
            accidents_analysis = self.analyze_accidents(traffic_data)
            
            # Analyze speed patterns
            speed_analysis = self.analyze_speed(traffic_data)
            
            # Predict future traffic
            predictions = await self.predict_traffic(coordinates)
            
            return {
                "congestion_level": congestion_analysis.get('level', 'low'),
                "congestion_points": congestion_analysis.get('points', []),
                "accidents": accidents_analysis.get('count', 0),
                "accident_details": accidents_analysis.get('details', []),
                "average_speed": speed_analysis.get('avg_speed', 0),
                "speed_violations": speed_analysis.get('violations', 0),
                "traffic_predictions": predictions,
                "route_length_km": self.calculate_route_length(coordinates),
                "estimated_traffic_delay_minutes": congestion_analysis.get('delay_minutes', 0),
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing traffic: {e}")
            return self.get_fallback_data()
            
    async def get_traffic_data(self, coordinates: List[List[float]]) -> Dict:
        """Fetch traffic data from API"""
        
        cache_key = self.generate_cache_key(coordinates)
        
        # Check cache
        if cache_key in self.cached_data and self.is_cache_valid(cache_key):
            logger.debug(f"Using cached data for: {cache_key}")
            return self.cached_data[cache_key]
            
        # Fetch new data (mock implementation)
        try:
            mock_data = {
                "segments": [
                    {
                        "coordinates": coordinates[0],
                        "density": 0.4,
                        "speed": 70,
                        "free_flow_speed": 100,
                        "delay": 5
                    }
                ],
                "incidents": []
            }
            
            self.cached_data[cache_key] = mock_data
            self.cache_expiry[cache_key] = datetime.utcnow().timestamp() + 300
            
            return mock_data
            
        except Exception as e:
            logger.error(f"Failed to fetch traffic data: {e}")
            raise
                    
    def analyze_congestion(self, traffic_data: Dict) -> Dict:
        """Analyze congestion levels"""
        
        congestion_level = "low"
        congestion_points = []
        total_delay = 0
        
        if 'segments' in traffic_data:
            for segment in traffic_data['segments']:
                speed = segment.get('speed', 0)
                free_flow_speed = segment.get('free_flow_speed', 60)
                
                if speed < free_flow_speed * 0.3:
                    level = "severe"
                elif speed < free_flow_speed * 0.6:
                    level = "high"
                elif speed < free_flow_speed * 0.8:
                    level = "medium"
                else:
                    level = "low"
                    
                if level in ["high", "severe"]:
                    congestion_points.append({
                        "location": segment.get('coordinates'),
                        "level": level,
                        "speed": speed,
                        "density": segment.get('density', 0),
                        "delay_minutes": segment.get('delay', 0)
                    })
                    total_delay += segment.get('delay', 0)
                    
            if any(p['level'] == 'severe' for p in congestion_points):
                congestion_level = "severe"
            elif any(p['level'] == 'high' for p in congestion_points):
                congestion_level = "high"
            elif len(congestion_points) > 0:
                congestion_level = "medium"
                
        return {
            "level": congestion_level,
            "points": congestion_points,
            "delay_minutes": total_delay,
            "total_congestion_points": len(congestion_points)
        }
        
    def analyze_accidents(self, traffic_data: Dict) -> Dict:
        """Analyze traffic accidents"""
        
        accidents = traffic_data.get('incidents', [])
        filtered_accidents = []
        
        for accident in accidents:
            if accident.get('type') in ['accident', 'crash', 'road_closed']:
                filtered_accidents.append({
                    "type": accident.get('type'),
                    "severity": accident.get('severity', 'unknown'),
                    "location": accident.get('coordinates'),
                    "description": accident.get('description', ''),
                    "start_time": accident.get('start_time'),
                    "expected_clearance": accident.get('expected_clearance')
                })
                
        return {
            "count": len(filtered_accidents),
            "details": filtered_accidents,
            "has_major_accident": any(a['severity'] in ['high', 'severe'] for a in filtered_accidents)
        }
        
    def analyze_speed(self, traffic_data: Dict) -> Dict:
        """Analyze speed patterns"""
        
        speeds = []
        violations = 0
        
        if 'segments' in traffic_data:
            for segment in traffic_data['segments']:
                speed = segment.get('speed', 0)
                speed_limit = segment.get('speed_limit', 60)
                
                speeds.append(speed)
                
                if speed > speed_limit * 1.1:
                    violations += 1
                    
        avg_speed = sum(speeds) / len(speeds) if speeds else 0
        
        return {
            "avg_speed": round(avg_speed, 1),
            "max_speed": max(speeds) if speeds else 0,
            "min_speed": min(speeds) if speeds else 0,
            "violations": violations,
            "speed_variation": max(speeds) - min(speeds) if speeds else 0
        }
        
    async def predict_traffic(self, coordinates: List[List[float]]) -> Dict:
        """Predict future traffic conditions"""
        
        predictions = []
        current_hour = datetime.utcnow().hour
        
        for hour_offset in range(1, 5):
            predicted_hour = (current_hour + hour_offset) % 24
            
            if 7 <= predicted_hour <= 9 or 16 <= predicted_hour <= 18:
                congestion_level = "high"
            elif 10 <= predicted_hour <= 15:
                congestion_level = "medium"
            else:
                congestion_level = "low"
                
            predictions.append({
                "hour": predicted_hour,
                "congestion_level": congestion_level,
                "estimated_delay_minutes": 10 if congestion_level == "medium" else 20 if congestion_level == "high" else 5,
                "confidence": 0.85 if congestion_level == "high" else 0.75
            })
            
        return predictions
        
    def calculate_route_length(self, coordinates: List[List[float]]) -> float:
        """Calculate route length in kilometers"""
        
        if len(coordinates) < 2:
            return 0
            
        total_distance = 0
        
        for i in range(len(coordinates) - 1):
            lat1, lon1 = coordinates[i]
            lat2, lon2 = coordinates[i + 1]
            distance = self.haversine_distance(lat1, lon1, lat2, lon2)
            total_distance += distance
            
        return round(total_distance, 2)
        
    def haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points using Haversine formula"""
        
        R = 6371  # Earth radius in kilometers
        
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        
        return R * c
        
    def generate_cache_key(self, coordinates: List[List[float]]) -> str:
        """Generate cache key for route"""
        
        return f"traffic_{hash(str(coordinates))}"
        
    def is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached data is still valid"""
        
        if cache_key not in self.cache_expiry:
            return False
            
        current_time = datetime.utcnow().timestamp()
        return current_time < self.cache_expiry[cache_key]
        
    def get_fallback_data(self) -> Dict:
        """Return fallback data when API fails"""
        
        return {
            "congestion_level": "unknown",
            "congestion_points": [],
            "accidents": 0,
            "average_speed": 60,
            "traffic_predictions": [],
            "route_length_km": 0,
            "estimated_traffic_delay_minutes": 0,
            "is_fallback_data": True
        }
        
    async def refresh_data(self):
        """Refresh cached data"""
        
        logger.info("Refreshing traffic analysis data...")
        self.cached_data.clear()
        self.cache_expiry.clear()
