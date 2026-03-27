import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
import httpx
from backend.core.settings import settings

logger = logging.getLogger(__name__)

class WeatherService:
    """
    Real-time weather service - connected to OpenWeatherMap API
    """

    def __init__(self):
        self.api_key = settings.OPENWEATHER_API_KEY
        self.base_url = "https://api.openweathermap.org/data/2.5"
        self.forecast_url = "https://api.openweathermap.org/data/2.5/forecast"

        # Cache to reduce API calls
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes

        logger.info("Weather Service initialized")

    async def get_current_weather(self, city: str = None, lat: float = None, lon: float = None) -> Dict:
        """
        Get current weather
        """
        cache_key = f"current_{city or f'{lat}_{lon}'}"

        # Check cache
        if cache_key in self.cache:
            cached, timestamp = self.cache[cache_key]
            if (datetime.now() - timestamp).seconds < self.cache_ttl:
                return cached

        try:
            params = {"appid": self.api_key, "units": "metric"}
            if city:
                params["q"] = city
            else:
                params["lat"] = lat
                params["lon"] = lon

            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.get(f"{self.base_url}/weather", params=params)
                if resp.status_code == 200:
                    data = resp.json()

                    result = {
                        "success": True,
                        "city": data.get("name"),
                        "country": data.get("sys", {}).get("country"),
                        "temperature": data.get("main", {}).get("temp"),
                        "feels_like": data.get("main", {}).get("feels_like"),
                        "humidity": data.get("main", {}).get("humidity"),
                        "pressure": data.get("main", {}).get("pressure"),
                        "wind_speed": data.get("wind", {}).get("speed"),
                        "wind_direction": data.get("wind", {}).get("deg"),
                        "clouds": data.get("clouds", {}).get("all"),
                        "description": data.get("weather", [{}])[0].get("description"),
                        "icon": data.get("weather", [{}])[0].get("icon"),
                        "timestamp": datetime.now().isoformat()
                    }

                    self.cache[cache_key] = (result, datetime.now())

                    return result

                error = resp.text
                logger.error(f"Weather API error: {resp.status_code} - {error}")
                return {"success": False, "error": f"API error: {resp.status_code}"}

        except Exception as e:
            logger.error(f"Error fetching weather: {e}")
            return {"success": False, "error": str(e)}

    async def get_forecast(self, city: str = None, lat: float = None, lon: float = None, days: int = 5) -> Dict:
        """
        Get weather forecast
        """
        try:
            params = {"appid": self.api_key, "units": "metric", "cnt": days * 8}
            if city:
                params["q"] = city
            else:
                params["lat"] = lat
                params["lon"] = lon

            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.get(self.forecast_url, params=params)
                if resp.status_code == 200:
                    data = resp.json()

                    forecasts = []
                    for item in data.get("list", []):
                        forecasts.append({
                            "datetime": item.get("dt_txt"),
                            "temperature": item.get("main", {}).get("temp"),
                            "feels_like": item.get("main", {}).get("feels_like"),
                            "humidity": item.get("main", {}).get("humidity"),
                            "pressure": item.get("main", {}).get("pressure"),
                            "wind_speed": item.get("wind", {}).get("speed"),
                            "description": item.get("weather", [{}])[0].get("description"),
                            "icon": item.get("weather", [{}])[0].get("icon"),
                            "rain": item.get("rain", {}).get("3h", 0),
                            "snow": item.get("snow", {}).get("3h", 0)
                        })

                    risks = self._analyze_weather_risks(forecasts)

                    return {
                        "success": True,
                        "city": data.get("city", {}).get("name"),
                        "country": data.get("city", {}).get("country"),
                        "forecasts": forecasts,
                        "risks": risks,
                        "timestamp": datetime.now().isoformat()
                    }

                return {"success": False, "error": f"API error: {resp.status_code}"}

        except Exception as e:
            logger.error(f"Error fetching forecast: {e}")
            return {"success": False, "error": str(e)}

    def _analyze_weather_risks(self, forecasts: List[Dict]) -> List[Dict]:
        """
        Analyze weather risks
        """
        risks = []

        for forecast in forecasts:
            risk = {
                "datetime": forecast["datetime"],
                "risk_level": "low",
                "risks": [],
                "recommendations": []
            }

            # Analyze rain
            rain = forecast.get("rain", 0)
            if rain > 20:
                risk["risk_level"] = "high"
                risk["risks"].append("heavy_rain")
                risk["recommendations"].append("Delay non-urgent shipments")
            elif rain > 10:
                risk["risk_level"] = "medium"
                risk["risks"].append("moderate_rain")
                risk["recommendations"].append("Reduce speed on highways")

            # Analyze wind
            wind = forecast.get("wind_speed", 0)
            if wind > 60:
                risk["risk_level"] = "severe"
                risk["risks"].append("strong_winds")
                risk["recommendations"].append("Stop high-profile trucks")
            elif wind > 40:
                if risk["risk_level"] == "low":
                    risk["risk_level"] = "medium"
                risk["risks"].append("moderate_winds")
                risk["recommendations"].append("Caution when driving high-profile trucks")

            # Analyze temperature
            temp = forecast.get("temperature", 0)
            if temp > 45:
                risk["risk_level"] = "severe"
                risk["risks"].append("extreme_heat")
                risk["recommendations"].append("Avoid driving at midday, drink plenty of water")
            elif temp > 38:
                if risk["risk_level"] == "low":
                    risk["risk_level"] = "medium"
                risk["risks"].append("high_temperature")
                risk["recommendations"].append("Ensure engine cooling, take frequent breaks")
            elif temp < -5:
                risk["risk_level"] = "high"
                risk["risks"].append("freezing")
                risk["recommendations"].append("Use tire chains, watch for ice")

            # Analyze fog
            if forecast.get("description", "").lower().find("fog") >= 0:
                risk["risk_level"] = "high"
                risk["risks"].append("fog")
                risk["recommendations"].append("Use fog lights, increase following distance")

            risks.append(risk)

        return risks


weather_service = WeatherService()


__all__ = ["WeatherService", "weather_service"]
