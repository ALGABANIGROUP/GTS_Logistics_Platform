from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException, Query

from backend.services.weather_service import WeatherService

router = APIRouter(prefix="/api/v1/weather", tags=["Weather"])
weather_service = WeatherService()


@router.get("/current")
async def get_current_weather(
    city: Optional[str] = Query(None, description="City name"),
    lat: Optional[float] = Query(None, description="Latitude"),
    lon: Optional[float] = Query(None, description="Longitude"),
) -> Dict[str, Any]:
    if not city and (lat is None or lon is None):
        raise HTTPException(status_code=400, detail="Either city or lat/lon required")
    return await weather_service.get_current_weather(city=city, lat=lat, lon=lon)


@router.get("/forecast")
async def get_weather_forecast(
    city: Optional[str] = Query(None, description="City name"),
    lat: Optional[float] = Query(None, description="Latitude"),
    lon: Optional[float] = Query(None, description="Longitude"),
    days: int = Query(5, ge=1, le=5, description="Forecast days"),
) -> Dict[str, Any]:
    if not city and (lat is None or lon is None):
        raise HTTPException(status_code=400, detail="Either city or lat/lon required")
    return await weather_service.get_forecast(city=city, lat=lat, lon=lon, days=days)


__all__ = ["router"]
