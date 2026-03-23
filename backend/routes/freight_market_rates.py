"""
Canadian Freight Market Rates API
Provides real-time market rates for Canadian freight corridors in CAD
"""

from contextlib import asynccontextmanager
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from backend.security.auth import get_current_user
from backend.services.canadian_freight_market import CanadianFreightMarketService

@asynccontextmanager
async def router_lifespan(_app):
    await market_service.initialize()
    try:
        yield
    finally:
        await market_service.shutdown()


router = APIRouter(
    prefix="/api/v1/freight",
    tags=["Canadian Freight Market"],
    lifespan=router_lifespan,
)

class CanadianMarketRate(BaseModel):
    """Canadian market rate for a freight corridor"""
    corridor_id: str = Field(..., description="Unique corridor identifier")
    name: str = Field(..., description="Corridor name")
    origin: str = Field(..., description="Origin city and province")
    origin_province: str = Field(..., description="Origin province code")
    destination: str = Field(..., description="Destination city and province")
    destination_province: str = Field(..., description="Destination province code")
    highway: str = Field(..., description="Primary highway/route")
    distance_km: float = Field(..., description="Distance in kilometers")
    rate_per_km: float = Field(..., description="Current rate in CAD per kilometer")
    total_trip_cost: float = Field(..., description="Total trip cost in CAD")
    currency: str = "CAD"
    unit: str = "kilometer"
    base_rate_per_km: float = Field(..., description="Base rate in CAD per kilometer")
    trend: Dict[str, Any] = Field(..., description="Market trend analysis")
    volatility_index: float = Field(..., description="Market volatility score (0-1)")
    data_quality: str = Field(..., description="Data quality indicator")
    cargo_types: List[str] = Field(..., description="Common cargo types")
    typical_transit_days: float = Field(..., description="Typical transit time in days")
    seasonal_adjustment: float = Field(..., description="Current seasonal adjustment factor")
    updated_at: str = Field(..., description="Last update timestamp")
    data_sources: List[str] = Field(..., description="Data sources used")

class MarketRatesResponse(BaseModel):
    """Response containing Canadian market rates"""
    rates: List[CanadianMarketRate]
    timestamp: str
    market_intelligence: Dict[str, Any]
    service_version: str = "2.0"
    data_coverage: str = "Canada National"
    next_update: str
    anomalies_detected: int
    average_rate_per_km: float

class RouteAnalysisRequest(BaseModel):
    """Request for route analysis"""
    origin: str
    destination: str
    cargo_type: Optional[str] = None
    truck_type: Optional[str] = None # dry_van, reefer, flatbed, etc.
    urgency: Optional[str] = "standard" # standard, expedited
    weight_kg: Optional[float] = None
    volume_m3: Optional[float] = None

class RouteAnalysisResponse(BaseModel):
    """Response for route analysis"""
    origin: str
    destination: str
    estimated_distance_km: float
    market_rate_per_km: float
    total_estimated_cost: float
    currency: str = "CAD"
    typical_transit_days: float
    recommended_truck_type: Optional[str]
    seasonal_adjustment: float
    market_trend: Dict[str, Any]
    confidence_score: float
    alternative_routes: List[Dict[str, Any]]
    updated_at: str

# Canadian freight market service instance
market_service = CanadianFreightMarketService()

@router.get("/canadian-market-rates", response_model=MarketRatesResponse)
async def get_canadian_market_rates(
    current_user: Dict[str, Any] = Depends(get_current_user),
    include_analysis: bool = False
) -> MarketRatesResponse:
    """
    Get current Canadian market rates for all major freight corridors

    Rates are in CAD per kilometer and based on official Canadian sources:
    - Transport Canada Statistics
    - Statistics Canada Freight Data
    - Provincial Transportation Ministries
    - Industry Association Reports
    """
    try:
        # Fetch real market data
        market_data = await market_service.get_current_market_data()
        if not market_data:
            raise HTTPException(
                status_code=503,
                detail="Market data service temporarily unavailable"
            )
        # Convert to response format
        rates: List[CanadianMarketRate] = []
        total_rates = 0
        sum_rates = 0.0
        for corridor_key, data in market_data.items():
            rates.append(
                CanadianMarketRate(
                    corridor_id=data.get("corridor_id", ""),
                    name=data.get("name", ""),
                    origin=data.get("origin", ""),
                    origin_province=data.get("origin_province", ""),
                    destination=data.get("destination", ""),
                    destination_province=data.get("destination_province", ""),
                    highway=data.get("highway", ""),
                    distance_km=data.get("distance_km", 0),
                    rate_per_km=data.get("rate_per_km", 0),
                    total_trip_cost=data.get("total_trip_cost", 0),
                    currency="CAD",
                    unit="kilometer",
                    base_rate_per_km=data.get("base_rate_per_km", 0),
                    trend=data.get("trend", {}),
                    volatility_index=data.get("volatility_index", 0),
                    data_quality=data.get("data_quality", "estimated"),
                    cargo_types=data.get("cargo_types", []),
                    typical_transit_days=data.get("typical_transit_days", 0),
                    seasonal_adjustment=data.get("seasonal_adjustment", 1.0),
                    updated_at=data.get("updated_at", datetime.now(timezone.utc).isoformat()),
                    data_sources=data.get("data_sources", [])
                )
            )
            total_rates += 1
            sum_rates += data.get("rate_per_km", 0)
        # Get market intelligence
        intelligence_report = await market_service.generate_intelligence_report()
        # Calculate average rate
        avg_rate = sum_rates / total_rates if total_rates > 0 else 0
        return MarketRatesResponse(
            rates=rates,
            timestamp=datetime.now(timezone.utc).isoformat(),
            market_intelligence=intelligence_report.get("market_overview", {}),
            service_version="2.0",
            data_coverage="Canada National",
            next_update=(datetime.now(timezone.utc) + timedelta(seconds=market_service.cache_duration)).isoformat(),
            anomalies_detected=len(intelligence_report.get("anomalies_detected", {}).get("details", {})),
            average_rate_per_km=round(avg_rate, 3)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching market rates: {str(e)}"
        )

@router.get("/canadian-market-rates/{corridor_id}")
async def get_market_rate_by_corridor(
    corridor_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """Get market rate for a specific Canadian freight corridor"""
    try:
        market_data = await market_service.get_current_market_data()
        # Find corridor by ID
        corridor_data = None
        for key, data in market_data.items():
            if data.get("corridor_id") == corridor_id:
                corridor_data = data
                break
        if not corridor_data:
            # Try to find by name
            for key, data in market_data.items():
                if corridor_id.lower() in data.get("name", "").lower():
                    corridor_data = data
                    break
        if not corridor_data:
            # Get list of available corridors
            available_corridors = [
                {
                    "corridor_id": data.get("corridor_id"),
                    "name": data.get("name"),
                    "origin": data.get("origin"),
                    "destination": data.get("destination")
                }
                for data in market_data.values()
            ]
            return {
                "ok": False,
                "error": "Corridor not found",
                "available_corridors": available_corridors,
            }
        return {
            "ok": True,
            "corridor_id": corridor_data.get("corridor_id"),
            "name": corridor_data.get("name"),
            "origin": corridor_data.get("origin"),
            "origin_province": corridor_data.get("origin_province"),
            "destination": corridor_data.get("destination"),
            "destination_province": corridor_data.get("destination_province"),
            "highway": corridor_data.get("highway"),
            "distance_km": corridor_data.get("distance_km"),
            "rate_per_km": corridor_data.get("rate_per_km"),
            "total_trip_cost": corridor_data.get("total_trip_cost"),
            "currency": "CAD",
            "unit": "kilometer",
            "base_rate_per_km": corridor_data.get("base_rate_per_km"),
            "trend": corridor_data.get("trend"),
            "volatility_index": corridor_data.get("volatility_index"),
            "data_quality": corridor_data.get("data_quality"),
            "cargo_types": corridor_data.get("cargo_types"),
            "typical_transit_days": corridor_data.get("typical_transit_days"),
            "seasonal_adjustment": corridor_data.get("seasonal_adjustment"),
            "updated_at": corridor_data.get("updated_at"),
            "data_sources": corridor_data.get("data_sources"),
            "profitability_score": await market_service.calculate_profitability_score(corridor_data)
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching corridor data: {str(e)}"
        )

@router.post("/analyze-route", response_model=RouteAnalysisResponse)
async def analyze_route(
    request: RouteAnalysisRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> RouteAnalysisResponse:
    """
    Analyze a specific freight route with detailed costing

    Uses Canadian market data to provide accurate estimates including:
    - Distance calculation
    - Market rate analysis
    - Seasonal adjustments
    - Truck type recommendations
    """
    try:
        # Get current market data
        market_data = await market_service.get_current_market_data()
        # Find the best matching corridor
        best_match = None
        best_score = 0
        for corridor_key, data in market_data.items():
            score = 0
            # Check origin and destination matches
            origin_lower = request.origin.lower()
            dest_lower = request.destination.lower()
            data_origin_lower = data.get("origin", "").lower()
            data_dest_lower = data.get("destination", "").lower()
            if origin_lower in data_origin_lower:
                score += 2
            elif request.origin.lower().split(",")[0] in data_origin_lower:
                score += 1
            if dest_lower in data_dest_lower:
                score += 2
            elif request.destination.lower().split(",")[0] in data_dest_lower:
                score += 1
            # Check cargo type match
            if request.cargo_type:
                cargo_types = data.get("cargo_types", [])
                if any(request.cargo_type.lower() in ct.lower() for ct in cargo_types):
                    score += 1
            if score > best_score:
                best_score = score
                best_match = data
        if not best_match:
            # Use default or calculate from scratch
            return await _calculate_route_from_scratch(request)
        # Calculate adjusted rate based on request parameters
        base_rate = best_match.get("rate_per_km", 0)
        adjusted_rate = base_rate
        # Apply truck type adjustment
        if request.truck_type:
            truck_adjustment = await market_service.get_truck_type_adjustment(request.truck_type)
            adjusted_rate *= truck_adjustment
        # Apply urgency adjustment
        if request.urgency == "expedited":
            adjusted_rate *= 1.25  # 25% premium for expedited
        # Apply weight/volume adjustments
        weight_volume_adjustment = await market_service.calculate_weight_volume_adjustment(
            request.weight_kg,
            request.volume_m3
        )
        adjusted_rate *= weight_volume_adjustment
        # Calculate total cost
        distance = best_match.get("distance_km", 0)
        total_cost = adjusted_rate * distance
        # Find alternative routes
        alternatives = []
        for corridor_key, data in market_data.items():
            if corridor_key != list(market_data.keys())[list(market_data.values()).index(best_match)]:
                # Calculate score for this alternative
                alt_score = 0
                if request.origin.lower().split(",")[0] in data.get("origin", "").lower():
                    alt_score += 1
                if request.destination.lower().split(",")[0] in data.get("destination", "").lower():
                    alt_score += 1
                if alt_score > 0:
                    alternatives.append({
                        "corridor_id": data.get("corridor_id"),
                        "name": data.get("name"),
                        "distance_km": data.get("distance_km"),
                        "rate_per_km": data.get("rate_per_km"),
                        "total_cost": data.get("total_trip_cost"),
                        "typical_transit_days": data.get("typical_transit_days"),
                        "match_score": alt_score
                    })
        # Sort alternatives by match score and cost
        alternatives.sort(key=lambda x: (-x["match_score"], x["total_cost"]))
        return RouteAnalysisResponse(
            origin=request.origin,
            destination=request.destination,
            estimated_distance_km=distance,
            market_rate_per_km=round(adjusted_rate, 3),
            total_estimated_cost=round(total_cost, 2),
            currency="CAD",
            typical_transit_days=best_match.get("typical_transit_days", 0),
            recommended_truck_type=request.truck_type or await market_service.recommend_truck_type(request.cargo_type),
            seasonal_adjustment=best_match.get("seasonal_adjustment", 1.0),
            market_trend=best_match.get("trend", {}),
            confidence_score=min(0.95, best_score / 5),  # Convert score to 0-1 scale
            alternative_routes=alternatives[:3],  # Top 3 alternatives
            updated_at=datetime.now(timezone.utc).isoformat()
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing route: {str(e)}"
        )

@router.get("/market-intelligence")
async def get_market_intelligence(
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Get comprehensive Canadian freight market intelligence

    Includes:
    - Market trends and analysis
    - Anomaly detection
    - Seasonal adjustments
    - Regional insights
    - Future predictions
    """
    try:
        report = await market_service.generate_intelligence_report()
        # Add additional insights
        market_data = await market_service.get_current_market_data()
        # Calculate regional averages
        regional_stats = {}
        for data in market_data.values():
            province = data.get("origin_province")
            if province not in regional_stats:
                regional_stats[province] = {
                    "total_routes": 0,
                    "total_rate": 0,
                    "total_distance": 0
                }
            regional_stats[province]["total_routes"] += 1
            regional_stats[province]["total_rate"] += data.get("rate_per_km", 0)
            regional_stats[province]["total_distance"] += data.get("distance_km", 0)
        # Convert to averages
        for province, stats in regional_stats.items():
            if stats["total_routes"] > 0:
                stats["average_rate"] = stats["total_rate"] / stats["total_routes"]
                stats["average_distance"] = stats["total_distance"] / stats["total_routes"]
            else:
                stats["average_rate"] = 0
                stats["average_distance"] = 0
        # Add seasonal insights
        current_season = await market_service.get_current_season()
        seasonal_factors = await market_service.get_seasonal_factors()
        report["regional_insights"] = regional_stats
        report["seasonal_analysis"] = {
            "current_season": current_season,
            "seasonal_factors": seasonal_factors,
            "next_season": await market_service.predict_next_season(),
            "seasonal_impact": "Significant winter adjustments currently applied" if current_season == "winter" else "Normal seasonal operations"
        }
        # Add fuel price impact
        fuel_impact = await market_service.get_fuel_price_impact()
        report["fuel_analysis"] = {
            "current_impact_factor": fuel_impact,
            "trend": "stable" if 0.98 < fuel_impact < 1.02 else "increasing" if fuel_impact > 1.02 else "decreasing",
            "recommendation": "Monitor fuel prices closely" if fuel_impact > 1.05 else "Normal operations"
        }
        return report
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating market intelligence: {str(e)}"
        )

@router.get("/historical-rates/{corridor_id}")
async def get_historical_rates(
    corridor_id: str,
    days: int = 30,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Get historical market rates for a specific corridor

    Parameters:
    - corridor_id: Corridor identifier
    - days: Number of days of history to retrieve (max 90)
    """
    try:
        if days > 90:
            days = 90
        history = await market_service.get_price_history(corridor_id, days)
        if not history:
            # Try to find by name
            market_data = await market_service.get_current_market_data()
            for key, data in market_data.items():
                if corridor_id.lower() in data.get("name", "").lower():
                    corridor_id = key
                    history = await market_service.get_price_history(corridor_id, days)
                    break
        if not history:
            return {
                "ok": False,
                "error": "No historical data available for this corridor",
                "available_corridors": list(market_data.keys())
            }
        # Calculate statistics
        rates = [h["rate"] for h in history]
        if rates:
            import statistics
            stats = {
                "average_rate": round(statistics.mean(rates), 3),
                "median_rate": round(statistics.median(rates), 3),
                "min_rate": round(min(rates), 3),
                "max_rate": round(max(rates), 3),
                "standard_deviation": round(statistics.stdev(rates), 4) if len(rates) > 1 else 0,
                "data_points": len(rates)
            }
            # Calculate trend
            if len(rates) >= 2:
                oldest = rates[0]
                newest = rates[-1]
                percent_change = ((newest - oldest) / oldest) * 100 if oldest > 0 else 0
                stats["trend"] = {
                    "percent_change": round(percent_change, 2),
                    "direction": "up" if percent_change > 2 else "down" if percent_change < -2 else "stable",
                    "strength": "strong" if abs(percent_change) > 5 else "moderate" if abs(percent_change) > 2 else "weak"
                }
        else:
            stats = {}
        return {
            "ok": True,
            "corridor_id": corridor_id,
            "history": history,
            "statistics": stats,
            "period_days": days,
            "currency": "CAD",
            "unit": "kilometer"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching historical rates: {str(e)}"
        )

async def _calculate_route_from_scratch(request: RouteAnalysisRequest) -> RouteAnalysisResponse:
    """Calculate route analysis from scratch when no direct match is found"""
    # This is a simplified calculation - in production, this would use
    # geocoding APIs and more sophisticated distance calculations
    province_distances = {
        ("ON", "QC"): 500,
        ("ON", "BC"): 4350,
        ("ON", "AB"): 3400,
        ("ON", "MB"): 2000,
        ("QC", "BC"): 4800,
        ("QC", "AB"): 3700,
        ("AB", "BC"): 850,
        ("AB", "SK"): 600,
        ("SK", "MB"): 700,
        ("MB", "ON"): 2000,
    }
    # Try to extract provinces
    origin_province = request.origin.split(",")[-1].strip().upper()[-2:]
    dest_province = request.destination.split(",")[-1].strip().upper()[-2:]
    # Get base market rate
    market_data = await market_service.get_current_market_data()
    avg_rate = sum(d.get("rate_per_km", 0) for d in market_data.values()) / len(market_data) if market_data else 2.5
    # Apply adjustments
    adjusted_rate = avg_rate
    if request.truck_type == "reefer":
        adjusted_rate *= 1.15
    elif request.truck_type == "flatbed":
        adjusted_rate *= 1.10
    if request.urgency == "expedited":
        adjusted_rate *= 1.25
    # Calculate distance
    distance = province_distances.get((origin_province, dest_province), 1000)
    # Calculate transit days (approx 500km per day)
    transit_days = max(1, round(distance / 500, 1))
    return RouteAnalysisResponse(
        origin=request.origin,
        destination=request.destination,
        estimated_distance_km=distance,
        market_rate_per_km=round(adjusted_rate, 3),
        total_estimated_cost=round(adjusted_rate * distance, 2),
        currency="CAD",
        typical_transit_days=transit_days,
        recommended_truck_type=request.truck_type or "dry_van",
        seasonal_adjustment=1.0,
        market_trend={"direction": "stable", "strength": "low", "confidence": 0.5},
        confidence_score=0.6,
        alternative_routes=[],
        updated_at=datetime.now(timezone.utc).isoformat()
    )
