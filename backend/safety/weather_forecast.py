"""
Weather Forecast System - Real-time weather monitoring
Analyzes hazards and provides safety recommendations
"""

import aiohttp
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging
from backend.services.weather_service import WeatherService

logger = logging.getLogger(__name__)


class WeatherForecaster:
    """Advanced weather forecasting and hazard analysis using real weather data"""

    def __init__(self):
        self.weather_service = WeatherService()
        self.forecast_cache = {}
        
    async def check_route_weather(self, coordinates: List[List[float]], 
                                 departure_time: datetime) -> Dict:
        """Check weather conditions along route"""
        
        weather_analysis = {
            "hazards": [],
            "conditions": [],
            "recommendations": [],
            "overall_risk": "low"
        }
        
        try:
            # Get weather for key points
            key_points = self.get_key_points(coordinates, 3)
            
            for point in key_points:
                point_weather = await self.get_weather_forecast(point, departure_time)
                
                # Analyze weather hazards
                hazards = self.analyze_weather_hazards(point_weather)
                weather_analysis["hazards"].extend(hazards)
                
                # Record conditions
                weather_analysis["conditions"].append({
                    "location": point,
                    "temperature": point_weather.get('temperature', {}),
                    "precipitation": point_weather.get('precipitation', {}),
                    "wind": point_weather.get('wind', {}),
                    "visibility": point_weather.get('visibility', 10)
                })
                
            # Determine overall risk level
            if any(h['severity'] == 'severe' for h in weather_analysis["hazards"]):
                weather_analysis["overall_risk"] = "severe"
            elif any(h['severity'] == 'high' for h in weather_analysis["hazards"]):
                weather_analysis["overall_risk"] = "high"
            elif any(h['severity'] == 'medium' for h in weather_analysis["hazards"]):
                weather_analysis["overall_risk"] = "medium"
                
            # Generate recommendations
            weather_analysis["recommendations"] = self.generate_weather_recommendations(
                weather_analysis["hazards"]
            )
            
            return weather_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing weather: {e}")
            return self.get_fallback_weather_analysis()
            
    async def get_weather_forecast(self, coordinates: List[float],
                                  target_time: datetime) -> Dict:
        """Get weather forecast for specific location and time using real weather data"""

        cache_key = f"weather_{coordinates[0]}_{coordinates[1]}_{target_time.date()}"

        # Check cache
        if cache_key in self.forecast_cache:
            cached_data = self.forecast_cache[cache_key]
            if datetime.utcnow().timestamp() - cached_data['timestamp'] < 3600:
                return cached_data['data']

        try:
            # Get real weather forecast
            forecast_result = await self.weather_service.get_forecast(
                lat=coordinates[0],
                lon=coordinates[1],
                days=3
            )

            if forecast_result.get("success"):
                # Convert to expected format
                forecasts = forecast_result.get("forecasts", [])
                if forecasts:
                    # Get forecast for target time (simplified - take first forecast)
                    forecast_data = forecasts[0]

                    forecast = {
                        "temperature": {
                            "celsius": forecast_data.get("temperature", 25),
                            "fahrenheit": (forecast_data.get("temperature", 25) * 9/5) + 32
                        },
                        "condition": forecast_data.get("description", "Clear"),
                        "precipitation": {
                            "mm": forecast_data.get("rain", 0),
                            "inches": forecast_data.get("rain", 0) * 0.0393701,
                            "probability": 0  # Simplified
                        },
                        "wind": {
                            "speed_kph": forecast_data.get("wind_speed", 0) * 3.6,  # m/s to km/h
                            "speed_mph": forecast_data.get("wind_speed", 0) * 2.237,
                            "direction": "N",  # Simplified
                            "gust_kph": forecast_data.get("wind_speed", 0) * 4.32
                        },
                        "humidity": forecast_data.get("humidity", 50),
                        "visibility_km": 10,  # Default
                        "uv_index": 5,  # Default
                        "feels_like_c": forecast_data.get("feels_like", forecast_data.get("temperature", 25)),
                        "feels_like_f": ((forecast_data.get("feels_like", forecast_data.get("temperature", 25))) * 9/5) + 32
                    }

                    self.forecast_cache[cache_key] = {
                        'data': forecast,
                        'timestamp': datetime.utcnow().timestamp()
                    }

                    return forecast

        except Exception as e:
            logger.error(f"Error fetching real weather forecast: {e}")

        # Fallback to seed data if API fails
        logger.warning("Using fallback seed weather data")
        forecast = {
            "temperature": {"celsius": 25, "fahrenheit": 77},
            "condition": "Clear",
            "precipitation": {"mm": 0, "inches": 0, "probability": 0},
            "wind": {"speed_kph": 15, "speed_mph": 9, "direction": "N", "gust_kph": 25},
            "humidity": 50,
            "visibility_km": 10,
            "uv_index": 5,
            "feels_like_c": 25,
            "feels_like_f": 77
        }

        self.forecast_cache[cache_key] = {
            'data': forecast,
            'timestamp': datetime.utcnow().timestamp()
        }

        return forecast
            
    def analyze_weather_hazards(self, weather_data: Dict) -> List[Dict]:
        """Analyze weather-related hazards"""
        
        hazards = []
        
        # Check heavy rain
        precipitation = weather_data.get('precipitation', {})
        precip_mm = precipitation.get('mm', 0)
        precip_prob = precipitation.get('probability', 0)
        
        if precip_mm > 10 or precip_prob > 70:
            hazards.append({
                "type": "heavy_rain",
                "severity": "high" if precip_mm > 20 else "medium",
                "intensity_mm": precip_mm,
                "probability": precip_prob,
                "impact": "Reduced visibility, slipping hazard"
            })
            
        # Check strong winds
        wind_speed = weather_data.get('wind', {}).get('speed_kph', 0)
        wind_gust = weather_data.get('wind', {}).get('gust_kph', 0)
        
        if wind_gust > 60:
            hazards.append({
                "type": "strong_winds",
                "severity": "high" if wind_gust > 80 else "medium",
                "wind_speed_kph": wind_speed,
                "gust_speed_kph": wind_gust,
                "impact": "Vehicle instability, falling objects hazard"
            })
            
        # Check fog/visibility
        visibility = weather_data.get('visibility_km', 10)
        
        if visibility < 1:
            hazards.append({
                "type": "fog",
                "severity": "severe" if visibility < 0.5 else "high",
                "visibility_km": visibility,
                "impact": "Severely reduced visibility"
            })
            
        # Check extreme heat
        temperature = weather_data.get('temperature', {}).get('celsius', 25)
        
        if temperature > 40:
            hazards.append({
                "type": "extreme_heat",
                "severity": "high" if temperature > 45 else "medium",
                "temperature_c": temperature,
                "impact": "Driver fatigue, vehicle overheating"
            })
            
        # Check freezing conditions
        if temperature < 0:
            hazards.append({
                "type": "freezing",
                "severity": "high" if temperature < -5 else "medium",
                "temperature_c": temperature,
                "impact": "Slippery roads, fuel system freezing"
            })
            
        # Check thunderstorms
        condition = weather_data.get('condition', '').lower()
        if 'thunder' in condition or 'storm' in condition:
            hazards.append({
                "type": "thunderstorm",
                "severity": "high",
                "description": condition,
                "impact": "Strong winds, lightning, heavy rain"
            })
            
        return hazards
        
    def generate_weather_recommendations(self, hazards: List[Dict]) -> List[Dict]:
        """Generate weather-based recommendations"""
        
        recommendations = []
        
        for hazard in hazards:
            hazard_type = hazard.get('type')
            severity = hazard.get('severity')
            
            if hazard_type == "heavy_rain":
                recommendations.append({
                    "action": "reduce_speed",
                    "priority": "high" if severity in ["high", "severe"] else "medium",
                    "message": "Reduce speed due to heavy rain",
                    "details": f"Expected rainfall: {hazard.get('intensity_mm', 0)} mm"
                })
                
            elif hazard_type == "strong_winds":
                recommendations.append({
                    "action": "avoid_open_areas",
                    "priority": "high" if severity == "high" else "medium",
                    "message": "Avoid exposed roads and bridges due to strong winds",
                    "details": f"Wind gusts up to {hazard.get('gust_speed_kph', 0)} kph"
                })
                
            elif hazard_type == "fog":
                recommendations.append({
                    "action": "use_fog_lights",
                    "priority": "high",
                    "message": "Use fog lights and exercise extreme caution",
                    "details": f"Visibility: {hazard.get('visibility_km', 0)} km"
                })
                
            elif hazard_type == "extreme_heat":
                recommendations.append({
                    "action": "check_cooling_system",
                    "priority": "medium",
                    "message": "Check cooling system and water levels",
                    "details": f"Temperature: {hazard.get('temperature_c', 0)}°C"
                })
                
            elif hazard_type == "freezing":
                recommendations.append({
                    "action": "use_winter_tires",
                    "priority": "high",
                    "message": "Use winter tires and adequate antifreeze",
                    "details": f"Temperature: {hazard.get('temperature_c', 0)}°C"
                })
                
            elif hazard_type == "thunderstorm":
                recommendations.append({
                    "action": "delay_trip",
                    "priority": "high",
                    "message": "Postpone trip if possible",
                    "details": "Thunderstorm expected"
                })
                
        return recommendations
        
    def get_key_points(self, coordinates: List[List[float]], num_points: int = 3) -> List[List[float]]:
        """Extract key points along route"""
        
        if len(coordinates) <= num_points:
            return coordinates
            
        step = len(coordinates) // num_points
        key_points = []
        
        for i in range(num_points):
            index = min(i * step, len(coordinates) - 1)
            key_points.append(coordinates[index])
            
        return key_points
        
    def get_fallback_weather_analysis(self) -> Dict:
        """Return fallback weather analysis"""
        
        return {
            "hazards": [],
            "conditions": [{
                "location": [0, 0],
                "temperature": {"celsius": 25},
                "precipitation": {"mm": 0, "probability": 0},
                "wind": {"speed_kph": 15},
                "visibility": 10
            }],
            "recommendations": [],
            "overall_risk": "low",
            "is_fallback_data": True
        }
        
    async def update_forecasts(self):
        """Update all forecasts"""
        
        logger.info("Updating weather forecasts...")
        
        current_time = datetime.utcnow().timestamp()
        keys_to_remove = []
        
        for key, cached in self.forecast_cache.items():
            if current_time - cached['timestamp'] > 3600:
                keys_to_remove.append(key)
                
        for key in keys_to_remove:
            del self.forecast_cache[key]
            
        logger.info(f"Updated forecasts, removed {len(keys_to_remove)} expired entries")
