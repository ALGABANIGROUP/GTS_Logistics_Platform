"""
MapleLoad Canada Bot Routes - Unified Canadian Logistics Platform
Endpoints for market intelligence, carrier discovery, freight sourcing, and outreach automation.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime

# Import the bot
from backend.bots.mapleload_canada import MapleLoadCanadaBot
from backend.bots.mapleload_bot import MatchingAlgorithm, OptimizationGoal
from backend.security.auth import get_current_user

# Create router
router = APIRouter(
    prefix="/api/v1/ai/bots/mapleload-canada",
    tags=["MapleLoad Canada Bot"]
)

# Store bot instance
_bot_instance = None

def get_bot() -> MapleLoadCanadaBot:
    """Get or create bot instance"""
    global _bot_instance
    if _bot_instance is None:
        _bot_instance = MapleLoadCanadaBot()
    return _bot_instance


# ==================== REQUEST MODELS ====================

class MarketIntelligenceRequest(BaseModel):
    """Market intelligence analysis request"""
    analysis_type: str = Field(default="comprehensive", description="Type of market analysis")
    regions: Optional[List[str]] = Field(default=None, description="Target regions")


class CarrierDiscoveryRequest(BaseModel):
    """Carrier discovery request"""
    province: Optional[str] = Field(default=None, description="Target province")
    equipment_type: Optional[str] = Field(default="any", description="Equipment type filter")
    min_rating: Optional[float] = Field(default=4.0, description="Minimum rating filter")


class FreightSourcingRequest(BaseModel):
    """Freight sourcing request"""
    equipment: Optional[str] = Field(default="any", description="Equipment type")
    origin: Optional[str] = Field(default=None, description="Origin region")
    destination: Optional[str] = Field(default=None, description="Destination region")
    max_results: Optional[int] = Field(default=15, description="Max results to return")


class OutreachCampaignRequest(BaseModel):
    """Outreach campaign creation request"""
    name: str = Field(description="Campaign name")
    target: str = Field(default="all_carriers", description="Target audience")
    message_type: Optional[str] = Field(default="standard", description="Message type")


class LeadGenerationRequest(BaseModel):
    """Lead generation request"""
    industry: str = Field(default="manufacturing", description="Target industry")
    region: Optional[str] = Field(default=None, description="Target region")
    min_volume: Optional[int] = Field(default=50, description="Minimum monthly volume")


class PredictiveAnalyticsRequest(BaseModel):
    """Predictive analytics request"""
    forecast_type: str = Field(default="demand", description="Forecast type")
    time_range: str = Field(default="30days", description="Time range")
    confidence_level: int = Field(default=85, description="Confidence level (70-95)")


class SmartMatchingRequest(BaseModel):
    """Smart matching request"""
    algorithm: str = Field(default="hybrid", description="Matching algorithm")
    optimization_goal: str = Field(default="balanced", description="Optimization goal")
    min_match_score: Optional[int] = Field(default=85, description="Minimum match score")


class AdvancedReportRequest(BaseModel):
    """Advanced report generation request"""
    report_type: str = Field(default="performance", description="Report type")
    output_format: str = Field(default="json", description="Output format")
    period: Optional[str] = Field(default="last_30_days", description="Report period")


class BotResponse(BaseModel):
    """Standard bot response model"""
    ok: bool = True
    data: Dict[str, Any]
    execution_id: Optional[int] = None
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    error: Optional[str] = None


class FreightSearchRequest(BaseModel):
    """Freight search request for UI dashboard"""
    origin: Optional[str] = None
    destination: Optional[str] = None
    weight: Optional[str] = None
    commodity: Optional[str] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    max_rate: Optional[str] = None


# ==================== PUBLIC ENDPOINTS ====================

@router.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint (public)"""
    bot = get_bot()
    return {
        "status": "healthy",
        "bot": bot.name,
        "version": bot.version,
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/status", tags=["Status"])
async def get_status():
    """Get bot status and capabilities"""
    bot = get_bot()
    status = await bot.status()
    return BotResponse(
        ok=status.get("ok", True),
        data=status
    )


@router.get("/capabilities", tags=["Status"])
async def get_capabilities():
    """Get bot capabilities"""
    bot = get_bot()
    config = await bot.config()
    return BotResponse(
        ok=True,
        data=config
    )


# ==================== MARKET INTELLIGENCE ====================

@router.post("/market-intelligence", tags=["Market Intelligence"])
async def market_intelligence(
    request: MarketIntelligenceRequest
):
    """Get Canadian logistics market intelligence"""
    bot = get_bot()
    result = await bot.get_market_intelligence()
    return BotResponse(
        ok=result.get("ok", True),
        data=result.get("intelligence", result)
    )


# ==================== UI DASHBOARD SUPPORT ====================

@router.get("/incoming-emails", tags=["Dashboard"])
async def get_incoming_emails():
    return {
        "emails": [],
        "count": 0,
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/database-records", tags=["Dashboard"])
async def get_database_records():
    return {
        "records": [],
        "count": 0,
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/learning-stats", tags=["Dashboard"])
async def get_learning_stats():
    return {
        "stats": {
            "total_processed": 0,
            "successful_matches": 0,
            "failed_matches": 0,
            "avg_match_rate": 0,
            "system_learning": 0,
        }
    }


@router.get("/suppliers", tags=["Dashboard"])
async def get_suppliers():
    return {
        "suppliers": [],
        "count": 0,
    }


@router.post("/search-freight", tags=["Dashboard"])
async def search_freight(
    request: FreightSearchRequest
):
    origin = request.origin or "Toronto, ON"
    destination = request.destination or "Vancouver, BC"
    return {
        "loads": [
            {
                "id": "LOAD-ML-001",
                "origin": origin,
                "destination": destination,
                "weight": request.weight or "24000",
                "commodity": request.commodity or "Freight",
                "rate": "$2,150",
                "pickup_date": request.date_from or "2026-02-10",
                "delivery_date": request.date_to or "2026-02-14",
                "posted_by": "MapleLoad Canada",
                "distance": "3,100 km",
            }
        ]
    }


@router.post("/process-email-shipment", tags=["Dashboard"])
async def process_email_shipment(
    payload: Dict[str, Any]
):
    return {
        "success": True,
        "record_id": f"REC-{int(datetime.utcnow().timestamp())}",
        "matched_carriers": [],
        "status": "pending",
        "learning_score": 0,
        "payload": payload,
    }


# ==================== CARRIER DISCOVERY ====================

@router.post("/carrier-discovery", tags=["Carrier Discovery"])
async def carrier_discovery(
    request: CarrierDiscoveryRequest
):
    """Discover Canadian carriers"""
    bot = get_bot()
    result = await bot.discover_carriers(request.province)
    return BotResponse(
        ok=result.get("ok", True),
        data=result.get("discovery", result)
    )


@router.get("/carriers/{province}", tags=["Carrier Discovery"])
async def get_carriers_by_province(
    province: str
):
    """Get carriers in a specific province"""
    bot = get_bot()
    result = await bot.discover_carriers(province)
    return BotResponse(
        ok=result.get("ok", True),
        data=result.get("discovery", result)
    )


# ==================== FREIGHT SOURCING ====================

@router.post("/freight-sourcing", tags=["Freight Sourcing"])
async def freight_sourcing(
    request: FreightSourcingRequest
):
    """Find available freight loads"""
    bot = get_bot()
    result = await bot.source_freight()
    return BotResponse(
        ok=result.get("ok", True),
        data=result.get("sourcing", result)
    )


@router.get("/available-loads", tags=["Freight Sourcing"])
async def get_available_loads(
    equipment: Optional[str] = Query(None, description="Equipment type")
):
    """Get available freight loads"""
    bot = get_bot()
    result = await bot.source_freight()
    return BotResponse(
        ok=result.get("ok", True),
        data=result.get("sourcing", result)
    )


# ==================== OUTREACH AUTOMATION ====================

@router.post("/outreach-campaign", tags=["Outreach Automation"])
async def create_outreach_campaign(
    request: OutreachCampaignRequest
):
    """Create automated outreach campaign"""
    bot = get_bot()
    result = await bot.create_outreach_campaign(request.dict())
    return BotResponse(
        ok=result.get("ok", True),
        data=result.get("campaign", result)
    )


# ==================== LEAD GENERATION ====================

@router.post("/lead-generation", tags=["Lead Generation"])
async def generate_leads(
    request: LeadGenerationRequest
):
    """Generate qualified leads"""
    bot = get_bot()
    result = await bot.generate_leads(request.dict())
    return BotResponse(
        ok=result.get("ok", True),
        data=result.get("leads", result)
    )


# ==================== PREDICTIVE ANALYTICS ====================

@router.post("/predictive-analytics", tags=["Predictive Analytics"])
async def predictive_analytics(
    request: PredictiveAnalyticsRequest
):
    """Run AI-powered predictive analytics"""
    bot = get_bot()
    result = await bot.run_predictive_analytics(request.dict())
    return BotResponse(
        ok=result.get("ok", True),
        data=result.get("predictions", result)
    )


# ==================== SMART MATCHING ====================

@router.post("/smart-matching", tags=["Smart Matching"])
async def smart_matching(
    request: SmartMatchingRequest
):
    """Run AI-powered smart matching"""
    bot = get_bot()
    result = await bot.run_smart_matching(request.dict())
    return BotResponse(
        ok=result.get("ok", True),
        data=result.get("matching", result)
    )


# ==================== ADVANCED REPORTING ====================

@router.post("/advanced-report", tags=["Advanced Reporting"])
async def advanced_report(
    request: AdvancedReportRequest
):
    """Generate comprehensive advanced report"""
    bot = get_bot()
    result = await bot.generate_advanced_report(request.dict())
    return BotResponse(
        ok=result.get("ok", True),
        data=result.get("report", result)
    )


# ==================== RATE ANALYSIS ====================

@router.get("/rate-analysis", tags=["Market Analysis"])
async def rate_analysis(
    lane: Optional[str] = Query(None, description="Specific lane")
):
    """Analyze freight rates"""
    bot = get_bot()
    result = await bot.analyze_rates(lane)
    return BotResponse(
        ok=result.get("ok", True),
        data=result.get("rate_analysis", result)
    )


# ==================== CAPACITY FORECASTING ====================

@router.get("/capacity-forecast", tags=["Market Analysis"])
async def capacity_forecast():
    """Get capacity forecast"""
    bot = get_bot()
    result = await bot.forecast_capacity()
    return BotResponse(
        ok=result.get("ok", True),
        data=result.get("capacity_forecast", result)
    )


# ==================== CROSS-BORDER ANALYSIS ====================

@router.get("/cross-border-analysis", tags=["Market Analysis"])
async def cross_border_analysis():
    """Get cross-border freight analysis"""
    bot = get_bot()
    result = await bot.analyze_cross_border()
    return BotResponse(
        ok=result.get("ok", True),
        data=result.get("cross_border_analysis", result)
    )


# ==================== INTEGRATIONS ====================

@router.get("/integrations", tags=["Integrations"])
async def get_integrations():
    """Get integrations status"""
    bot = get_bot()
    result = await bot.get_integrations_status()
    return BotResponse(
        ok=result.get("ok", True),
        data=result.get("integrations", result)
    )


# ==================== DASHBOARD ENDPOINTS ====================

@router.get("/dashboard", tags=["Dashboard"])
async def get_dashboard():
    """Get unified dashboard data"""
    bot = get_bot()
    
    # Gather all dashboard data
    status = await bot.status()
    market_intel = await bot.get_market_intelligence()
    
    return BotResponse(
        ok=True,
        data={
            "status": status,
            "market_intelligence": market_intel.get("intelligence"),
            "metrics": {
                "message": "No real-time metrics available. Connect a real data source."
            }
        }
    )


# ==================== BATCH OPERATIONS ====================

@router.post("/batch-operation", tags=["Batch Operations"])
async def batch_operation(
    operations: List[Dict[str, Any]]
):
    """Execute multiple bot operations in batch"""
    bot = get_bot()
    results = []
    
    for operation in operations:
        action = operation.get("action", "status")
        params = operation.get("params", {})
        
        try:
            result = await bot.run({"action": action, **params})
            results.append({
                "action": action,
                "ok": result.get("ok", True),
                "data": result.get("data", result)
            })
        except Exception as e:
            results.append({
                "action": action,
                "ok": False,
                "error": str(e)
            })
    
    return BotResponse(
        ok=True,
        data={"operations": results, "total": len(results)}
    )


# ==================== MARKET MONITORING & DAILY UPDATES ====================

@router.get("/market-rates/daily-report")
async def get_daily_report(
    days: int = Query(1, ge=1, le=30)
):
    """
    Get daily market reports for freight routes
    
    Parameters:
    - days: Number of days to retrieve (1-30)
    
    Returns:
    - List of daily reports with rate changes and market analysis
    """
    from backend.bots.mapleload_canada import mapleload_bot
    
    if not mapleload_bot.daily_reports:
        return {
            "status": "no_reports",
            "message": "No daily reports available yet",
            "reports": []
        }
    
    # Return last N days of reports
    num_reports = min(days, len(mapleload_bot.daily_reports))
    reports = mapleload_bot.daily_reports[-num_reports:]
    
    return {
        "status": "success",
        "count": len(reports),
        "reports": reports,
    }


@router.get("/market-rates/alerts")
async def get_rate_alerts(
    limit: int = Query(20, ge=1, le=100)
):
    """
    Get recent rate change alerts
    
    Parameters:
    - limit: Maximum number of alerts to retrieve (1-100)
    
    Returns:
    - List of rate alerts with route, change percentage, and priority
    """
    from backend.bots.mapleload_canada import mapleload_bot
    
    alerts = mapleload_bot.rate_alerts[-limit:]
    
    return {
        "status": "success",
        "count": len(alerts),
        "alerts": alerts,
    }


@router.post("/market-rates/trigger-update")
async def trigger_market_update():
    """
    Manually trigger a market rate update
    
    Returns:
    - Update status and results
    """
    from backend.bots.mapleload_canada import mapleload_bot
    
    try:
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"[MapleLoadAPI] Manual market update triggered by {current_user.get('email')}")
        
        # Run daily update
        await mapleload_bot.daily_market_update()
        
        return {
            "status": "success",
            "message": "Market update completed",
            "bot_status": mapleload_bot.get_status(),
        }
        
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"[MapleLoadAPI] Error triggering update: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to trigger market update"
        )


@router.get("/market-rates/history/{route}")
async def get_rate_history(
    route: str
):
    """
    Get price history for a specific route
    
    Parameters:
    - route: Route name (e.g., "Toronto-Vancouver")
    
    Returns:
    - Historical rate data with trend analysis
    """
    from backend.services.market_data_service import market_fetcher
    
    if route not in market_fetcher.price_history:
        raise HTTPException(
            status_code=404,
            detail=f"No history found for route: {route}"
        )
    
    history = market_fetcher.price_history[route]
    
    if not history:
        return {
            "route": route,
            "status": "no_history",
            "history": []
        }
    
    # Calculate statistics
    prices = [h["rate"] for h in history]
    avg_price = sum(prices) / len(prices)
    
    return {
        "route": route,
        "status": "success",
        "data_points": len(history),
        "current_rate": prices[-1],
        "average_rate": round(avg_price, 2),
        "min_rate": min(prices),
        "max_rate": max(prices),
        "volatility": round(max(prices) - min(prices), 2),
        "history": [
            {
                "rate": h["rate"],
                "timestamp": h["timestamp"].isoformat(),
            }
            for h in history
        ],
    }


@router.get("/market-rates/snapshot")
async def get_market_snapshot():
    """
    Get current snapshot of all market rates
    
    Returns:
    - All routes with current rates and trends
    """
    from backend.services.market_data_service import market_fetcher
    
    try:
        rates = await market_fetcher.fetch_real_market_data()
        
        return {
            "status": "success",
            "timestamp": str(__import__('datetime').datetime.utcnow()),
            "routes": len(rates),
            "rates": rates,
        }
        
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"[MapleLoadAPI] Error getting market snapshot: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve market snapshot"
        )


@router.post("/notifications/enable")
async def enable_notifications():
    """
    Enable email notifications for rate changes
    """
    from backend.bots.mapleload_canada import mapleload_bot
    import logging
    logger = logging.getLogger(__name__)
    
    mapleload_bot.email_enabled = True
    logger.info("[MapleLoadAPI] Email notifications enabled")
    
    return {
        "status": "success",
        "message": "Email notifications enabled",
        "email_enabled": mapleload_bot.email_enabled,
    }


@router.post("/notifications/disable")
async def disable_notifications():
    """
    Disable email notifications for rate changes
    """
    from backend.bots.mapleload_canada import mapleload_bot
    import logging
    logger = logging.getLogger(__name__)
    
    mapleload_bot.email_enabled = False
    logger.info("[MapleLoadAPI] Email notifications disabled")
    
    return {
        "status": "success",
        "message": "Email notifications disabled",
        "email_enabled": mapleload_bot.email_enabled,
    }


# ==================== LOAD SOURCES DISCOVERY ====================

@router.get("/load-sources/search", tags=["Load Sources"])
async def search_load_sources(
    query: Optional[str] = Query(None, description="Search query"),
    source_type: Optional[str] = Query(None, description="Source type filter"),
    country: Optional[str] = Query(None, description="Country filter"),
    verified_only: bool = Query(True, description="Only verified sources"),
    limit: int = Query(20, description="Max results")
):
    """
    Smart search for freight load sources
    
    Search across load boards, warehouses, 3PL providers, and logistics partners.
    Supports filtering by type, country, and verification status.
    
    **Source Types:**
    - load_board: Freight load boards (DAT, Logistware, etc.)
    - warehouse_provider: Warehouse and storage providers
    - warehouse_directory: Warehouse directory services
    - logistics_provider: General logistics providers
    - freight_carrier: Freight carriers
    - shipping_partner: Shipping partners
    - directory: Business directories
    
    **Countries:**
    - Canada: Canadian sources only
    - USA: US sources only
    - North America: Both Canada and USA
    """
    bot = get_bot()
    result = await bot.search_load_sources(
        query=query,
        source_type=source_type,
        country=country,
        verified_only=verified_only,
        limit=limit
    )
    return BotResponse(
        ok=result.get("ok", True),
        data=result
    )


@router.get("/load-sources/stats", tags=["Load Sources"])
async def get_load_source_stats():
    """
    Get statistics about available load sources
    
    Returns:
    - Total sources count
    - Breakdown by source type
    - Breakdown by country
    - Verification statistics
    - Contact information availability
    """
    bot = get_bot()
    result = await bot.get_load_source_stats()
    return BotResponse(
        ok=result.get("ok", True),
        data=result
    )


@router.post("/load-sources/recommendations", tags=["Load Sources"])
async def get_load_source_recommendations(
    requirements: Dict[str, Any]
):
    """
    Get smart recommendations for load sources based on requirements
    
    **Request Body Example:**
    ```json
    {
        "need_cold_storage": true,
        "need_3pl": false,
        "need_load_board": true,
        "region": "Canada",
        "equipment_type": "reefer"
    }
    ```
    
    The bot will analyze your requirements and recommend the most suitable sources.
    """
    bot = get_bot()
    result = await bot.get_smart_source_recommendations(requirements)
    return BotResponse(
        ok=result.get("ok", True),
        data=result
    )


@router.get("/load-sources/canadian", tags=["Load Sources"])
async def get_canadian_sources():
    """
    Get all Canadian load sources
    
    Quick access to all verified Canadian freight sources including:
    - Canadian load boards
    - Canadian warehouse providers
    - Canadian 3PL providers
    - Canadian logistics companies
    """
    bot = get_bot()
    result = await bot.search_load_sources(
        country="Canada",
        verified_only=True,
        limit=100
    )
    return BotResponse(
        ok=result.get("ok", True),
        data=result
    )


@router.get("/load-sources/load-boards", tags=["Load Sources"])
async def get_load_boards():
    """
    Get all load board sources
    
    Returns all available load board platforms for freight sourcing.
    """
    bot = get_bot()
    result = await bot.search_load_sources(
        source_type="load_board",
        verified_only=True,
        limit=50
    )
    return BotResponse(
        ok=result.get("ok", True),
        data=result
    )


@router.get("/load-sources/warehouses", tags=["Load Sources"])
async def get_warehouse_sources():
    """
    Get all warehouse-related sources
    
    Includes warehouse providers, warehouse directories, and fulfillment centers.
    """
    bot = get_bot()
    
    # Search for all warehouse-related types
    from backend.services.load_sources_service import load_sources_service
    all_sources = await load_sources_service.search_sources(
        source_type=None,
        country=None,
        verified_only=True,
        limit=100
    )
    
    # Filter warehouse-related
    warehouse_sources = [
        s for s in all_sources.get("sources", [])
        if "warehouse" in s.get("type", "").lower()
    ]
    
    return BotResponse(
        ok=True,
        data={
            "sources": warehouse_sources,
            "total": len(warehouse_sources),
            "timestamp": datetime.utcnow().isoformat()
        }
    )


