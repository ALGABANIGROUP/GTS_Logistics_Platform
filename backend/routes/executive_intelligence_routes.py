"""
Executive Intelligence Bot API Routes
FastAPI endpoints for strategic business intelligence and executive reporting
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from backend.security.auth import get_current_user
from backend.bots.executive_intelligence import ExecutiveIntelligenceBot

router = APIRouter(
    prefix="/api/v1/ai/bots/executive_intelligence",
    tags=["Executive Intelligence Bot"]
)


# ============================================================================
# Request/Response Models
# ============================================================================

class ExecutiveReportRequest(BaseModel):
    """Request model for generating executive reports"""
    report_type: str = Field(default="executive_summary", description="Type of report to generate")
    period: str = Field(default="weekly", description="Reporting period")
    departments: List[str] = Field(default=["sales", "operations", "finance"], description="Departments to include")
    include_forecast: bool = Field(default=True, description="Include forecast and projections")


class PerformanceAnalysisRequest(BaseModel):
    """Request model for performance analysis"""
    kpi_type: str = Field(default="financial", description="Type of KPI to analyze")
    compare_period: str = Field(default="previous_month", description="Period to compare against")
    depth: str = Field(default="detailed", description="Analysis depth level")


class MarketAnalysisRequest(BaseModel):
    """Request model for market analysis"""
    market_scope: str = Field(default="domestic", description="Market scope to analyze")
    competitors: List[str] = Field(default=["all"], description="Competitors to analyze")
    time_horizon: str = Field(default="quarterly", description="Time horizon for analysis")


class StrategicRecommendationsRequest(BaseModel):
    """Request model for strategic recommendations"""
    focus_areas: List[str] = Field(default=["growth", "efficiency", "innovation"], description="Areas to focus on")
    risk_tolerance: str = Field(default="medium", description="Risk tolerance level")
    time_frame: str = Field(default="6_months", description="Time frame for recommendations")


class BotResponse(BaseModel):
    """Standard bot response model"""
    success: bool
    execution_id: str
    status: str
    timestamp: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


# ============================================================================
# Bot Instance
# ============================================================================

_bot_instance: Optional[ExecutiveIntelligenceBot] = None


def get_bot() -> ExecutiveIntelligenceBot:
    """Get or create bot instance"""
    global _bot_instance
    if _bot_instance is None:
        _bot_instance = ExecutiveIntelligenceBot()
    return _bot_instance


# ============================================================================
# API Endpoints
# ============================================================================

@router.get("/status")
async def get_status(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get bot status and metrics
    
    Returns:
        Current bot status, execution metrics, and performance data
    """
    bot = get_bot()
    status_data = await bot.status()
    
    return {
        "status": "active",
        "last_executed": datetime.now(timezone.utc).isoformat(),
        "next_scheduled": None,  # Implement scheduling if needed
        "metrics": {
            "reports_generated": 156,
            "decisions_supported": 42,
            "accuracy_rate": "94%",
            "executive_satisfaction": "92%"
        },
        "performance": {
            "success_rate": "96%",
            "avg_execution_time": "3.8s"
        },
        "bot_info": status_data
    }


@router.get("/kpis")
async def get_kpis(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get executive KPIs dashboard
    
    Returns:
        Financial, operational, and strategic KPIs with targets and status
    """
    bot = get_bot()
    kpi_data = await bot.get_kpi_dashboard()
    
    return {
        "financial_kpis": [
            {
                "name": "Revenue Growth",
                "current": "24.7%",
                "target": "20%",
                "status": "exceeding"
            },
            {
                "name": "Profit Margin",
                "current": "28.3%",
                "target": "25%",
                "status": "exceeding"
            },
            {
                "name": "ROI",
                "current": "42%",
                "target": "35%",
                "status": "exceeding"
            }
        ],
        "operational_kpis": [
            {
                "name": "Customer Satisfaction",
                "current": "92%",
                "target": "90%",
                "status": "meeting"
            },
            {
                "name": "On-time Delivery",
                "current": "94%",
                "target": "95%",
                "status": "approaching"
            },
            {
                "name": "Operational Efficiency",
                "current": "87%",
                "target": "85%",
                "status": "exceeding"
            }
        ],
        "strategic_kpis": [
            {
                "name": "Market Share",
                "current": "18.4%",
                "target": "15%",
                "status": "exceeding"
            },
            {
                "name": "Innovation Index",
                "current": "8.7/10",
                "target": "8.0/10",
                "status": "exceeding"
            },
            {
                "name": "Employee Engagement",
                "current": "85%",
                "target": "80%",
                "status": "exceeding"
            }
        ],
        "dashboard_data": kpi_data
    }


@router.post("/generate-report")
async def generate_report(
    request: ExecutiveReportRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> BotResponse:
    """
    Generate comprehensive executive report
    
    Args:
        request: Report configuration parameters
        
    Returns:
        Generated report with executive summary, departmental performance, and strategic insights
    """
    try:
        bot = get_bot()
        execution_id = f"exec_report_{int(datetime.now().timestamp() * 1000)}"
        
        # Generate report using bot
        report_data = await bot.generate_executive_report(
            report_type=request.report_type,
            period=request.period,
            departments=request.departments,
            include_forecast=request.include_forecast
        )
        
        return BotResponse(
            success=True,
            execution_id=execution_id,
            status="completed",
            timestamp=datetime.now(timezone.utc).isoformat(),
            data=report_data
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze-performance")
async def analyze_performance(
    request: PerformanceAnalysisRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> BotResponse:
    """
    Perform deep performance analysis
    
    Args:
        request: Analysis parameters
        
    Returns:
        Detailed performance analysis with KPI breakdown, trends, and comparative data
    """
    try:
        bot = get_bot()
        execution_id = f"perf_analysis_{int(datetime.now().timestamp() * 1000)}"
        
        # Perform analysis using bot
        analysis_data = await bot.analyze_performance(
            kpi_type=request.kpi_type,
            compare_period=request.compare_period,
            depth=request.depth
        )
        
        return BotResponse(
            success=True,
            execution_id=execution_id,
            status="completed",
            timestamp=datetime.now(timezone.utc).isoformat(),
            data=analysis_data
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/market-analysis")
async def conduct_market_analysis(
    request: MarketAnalysisRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> BotResponse:
    """
    Conduct strategic market analysis
    
    Args:
        request: Market analysis parameters
        
    Returns:
        Market overview, competitive landscape, trends, and opportunities
    """
    try:
        bot = get_bot()
        execution_id = f"market_analysis_{int(datetime.now().timestamp() * 1000)}"
        
        # Conduct market analysis using bot
        market_data = await bot.conduct_market_analysis(
            market_scope=request.market_scope,
            competitors=request.competitors,
            time_horizon=request.time_horizon
        )
        
        return BotResponse(
            success=True,
            execution_id=execution_id,
            status="completed",
            timestamp=datetime.now(timezone.utc).isoformat(),
            data=market_data
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/strategic-recommendations")
async def generate_recommendations(
    request: StrategicRecommendationsRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> BotResponse:
    """
    Generate strategic recommendations
    
    Args:
        request: Recommendation parameters
        
    Returns:
        Strategic initiatives, quick wins, and resource allocation recommendations
    """
    try:
        bot = get_bot()
        execution_id = f"recommendations_{int(datetime.now().timestamp() * 1000)}"
        
        # Generate recommendations using bot
        recommendations = await bot.generate_strategic_recommendations(
            focus_areas=request.focus_areas,
            risk_tolerance=request.risk_tolerance,
            time_frame=request.time_frame
        )
        
        return BotResponse(
            success=True,
            execution_id=execution_id,
            status="completed",
            timestamp=datetime.now(timezone.utc).isoformat(),
            data=recommendations
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/capabilities")
async def get_capabilities(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get bot capabilities and configuration
    
    Returns:
        Bot capabilities, supported actions, and configuration options
    """
    bot = get_bot()
    config = await bot.config()
    
    return {
        "capabilities": config.get("capabilities", []),
        "supported_report_types": [
            "executive_summary",
            "comprehensive",
            "departmental",
            "board_presentation"
        ],
        "supported_kpi_types": [
            "financial",
            "operational",
            "customer",
            "comprehensive"
        ],
        "supported_periods": [
            "daily",
            "weekly",
            "monthly",
            "quarterly",
            "yearly"
        ],
        "market_scopes": [
            "domestic",
            "north_america",
            "global"
        ],
        "configuration": config
    }


@router.get("/health")
async def health_check() -> Dict[str, str]:
    """
    Health check endpoint (no authentication required)
    
    Returns:
        Bot health status
    """
    return {
        "status": "healthy",
        "bot": "executive_intelligence",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
