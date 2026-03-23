import aiohttp
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
from backend.core.settings import settings

logger = logging.getLogger(__name__)

class WeatherService:
    """
    خدمة الطقس الحقيقية - متصلة بـ OpenWeatherMap API
    """

    def __init__(self):
        self.api_key = settings.OPENWEATHER_API_KEY
        self.base_url = "https://api.openweathermap.org/data/2.5"
        self.forecast_url = "https://api.openweathermap.org/data/2.5/forecast"

        # ذاكرة تخزين مؤقت لتقليل الاستدعاءات
        self.cache = {}
        self.cache_ttl = 300  # 5 دقائق

        logger.info("✅ Weather Service initialized")

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

            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/weather", params=params) as resp:
                    if resp.status == 200:
                        data = await resp.json()

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

                        # تخزين في الكاش
                        self.cache[cache_key] = (result, datetime.now())

                        return result
                    else:
                        error = await resp.text()
                        logger.error(f"Weather API error: {resp.status} - {error}")
                        return {"success": False, "error": f"API error: {resp.status}"}

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

            async with aiohttp.ClientSession() as session:
                async with session.get(self.forecast_url, params=params) as resp:
                    if resp.status == 200:
                        data = await resp.json()

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

                        # تحليل المخاطر الجوية
                        risks = self._analyze_weather_risks(forecasts)

                        return {
                            "success": True,
                            "city": data.get("city", {}).get("name"),
                            "country": data.get("city", {}).get("country"),
                            "forecasts": forecasts,
                            "risks": risks,
                            "timestamp": datetime.now().isoformat()
                        }
                    else:
                        return {"success": False, "error": f"API error: {resp.status}"}

        except Exception as e:
            logger.error(f"Error fetching forecast: {e}")
            return {"success": False, "error": str(e)}

    def _analyze_weather_risks(self, forecasts: List[Dict]) -> List[Dict]:
        """
        تحليل المخاطر الجوية
        """
        risks = []

        for forecast in forecasts:
            risk = {
                "datetime": forecast["datetime"],
                "risk_level": "low",
                "risks": [],
                "recommendations": []
            }

            # تحليل الأمطار
            rain = forecast.get("rain", 0)
            if rain > 20:
                risk["risk_level"] = "high"
                risk["risks"].append("heavy_rain")
                risk["recommendations"].append("تأخير الشحنات غير العاجلة")
            elif rain > 10:
                risk["risk_level"] = "medium"
                risk["risks"].append("moderate_rain")
                risk["recommendations"].append("تخفيض السرعة على الطرق السريعة")

            # تحليل الرياح
            wind = forecast.get("wind_speed", 0)
            if wind > 60:
                risk["risk_level"] = "severe"
                risk["risks"].append("strong_winds")
                risk["recommendations"].append("إيقاف الشاحنات المرتفعة")
            elif wind > 40:
                if risk["risk_level"] == "low":
                    risk["risk_level"] = "medium"
                risk["risks"].append("moderate_winds")
                risk["recommendations"].append("الحذر عند قيادة الشاحنات المرتفعة")

            # تحليل درجات الحرارة
            temp = forecast.get("temperature", 0)
            if temp > 45:
                risk["risk_level"] = "severe"
                risk["risks"].append("extreme_heat")
                risk["recommendations"].append("تجنب القيادة في منتصف النهار، شرب الماء بكثرة")
            elif temp > 38:
                if risk["risk_level"] == "low":
                    risk["risk_level"] = "medium"
                risk["risks"].append("high_temperature")
                risk["recommendations"].append("تأكد من تبريد المحرك، خذ استراحات متكررة")
            elif temp < -5:
                risk["risk_level"] = "high"
                risk["risks"].append("freezing")
                risk["recommendations"].append("استخدام سلاسل الإطارات، الحذر من الجليد")

            # تحليل الضباب
            if forecast.get("description", "").lower().find("fog") >= 0:
                risk["risk_level"] = "high"
                risk["risks"].append("fog")
                risk["recommendations"].append("استخدام أنوار الضباب، زيادة مسافة الأمان")

            risks.append(risk)

        return risks