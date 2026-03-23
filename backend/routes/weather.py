from __future__ import annotations

import os
import asyncio
from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException, Query
from backend.services.weather_service import WeatherService

router = APIRouter(prefix="/api/v1/weather", tags=["Weather"])

# Initialize weather service
weather_service = WeatherService()
        "feels_like": 0,
        "humidity": 0,
        "wind_speed": 0,
        "description": "unavailable",
        "icon": None,
        "raw": {},
        "fallback": True,
    }


@router.get("/current")
async def get_current_weather(
    city: Optional[str] = Query(None, description="City name (e.g., Riyadh)"),
    lat: Optional[float] = Query(None, description="Latitude"),
    lon: Optional[float] = Query(None, description="Longitude"),
) -> Dict[str, Any]:
    """
    Get current weather (real data from OpenWeatherMap)
    """
    if not city and (lat is None or lon is None):
        raise HTTPException(status_code=400, detail="Either city or lat/lon required")

    result = await weather_service.get_current_weather(city, lat, lon)
    return result


@router.get("/forecast")
async def get_weather_forecast(
    city: Optional[str] = Query(None, description="City name (e.g., Riyadh)"),
    lat: Optional[float] = Query(None, description="Latitude"),
    lon: Optional[float] = Query(None, description="Longitude"),
    days: int = Query(5, ge=1, le=5, description="Forecast days"),
) -> Dict[str, Any]:
    """
    Weather forecast (real data)
    """
    if not city and (lat is None or lon is None):
        raise HTTPException(status_code=400, detail="Either city or lat/lon required")

    result = await weather_service.get_forecast(city, lat, lon, days)
    return result


__all__ = ["router"]