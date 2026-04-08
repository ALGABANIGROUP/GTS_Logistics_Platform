# backend/routes/marketing_bot.py
from fastapi import APIRouter, HTTPException, Depends, status, Query
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging
from pydantic import BaseModel, Field

from backend.database.session import get_async_session
from backend.security.auth import get_current_user

router = APIRouter(prefix="/api/v1/marketing", tags=["Marketing Bot"])
logger = logging.getLogger(__name__)


# ==================== Models ====================
class CampaignData(BaseModel):
    id: str
    name: str
    type: str  # email, social, ppc, seo, content
    status: str  # active, paused, completed, draft
    budget: float
    spent: float
    impressions: int
    clicks: int
    conversions: int
    revenue: float
    start_date: str
    end_date: Optional[str]
    roi: float


class LeadData(BaseModel):
    id: str
    name: str
    email: str
    phone: Optional[str]
    company: str
    status: str  # new, contacted, qualified, lost, converted
    source: str
    value: float
    created_at: str
    assigned_to: Optional[str]


# ==================== Mock Data ====================
MARKETING_METRICS = {
    "summary": {
        "total_campaigns": 12,
        "active_campaigns": 5,
        "total_leads": 245,
        "converted_leads": 78,
        "conversion_rate": 31.8,
        "total_revenue": 284500,
        "total_spent": 45600,
        "roi": 524,
        "email_open_rate": 42.5,
        "click_through_rate": 8.3,
        "social_engagement": 15234
    },
    "trends": {
        "revenue_last_30_days": [12500, 15800, 14200, 16800, 19200, 21500, 23400, 25100, 26800, 28400],
        "leads_last_30_days": [12, 15, 14, 18, 22, 25, 28, 32, 35, 38],
        "dates": [f"2026-03-{i+1:02d}" for i in range(10)]
    }
}

CAMPAIGNS = [
    {
        "id": "cam_001",
        "name": "Spring Logistics Campaign",
        "type": "email",
        "status": "active",
        "budget": 15000,
        "spent": 8750,
        "impressions": 125000,
        "clicks": 6250,
        "conversions": 312,
        "revenue": 46800,
        "start_date": "2026-03-01T00:00:00",
        "end_date": "2026-04-15T00:00:00",
        "roi": 435
    },
    {
        "id": "cam_002",
        "name": "LinkedIn Freight Broker Ads",
        "type": "social",
        "status": "active",
        "budget": 8000,
        "spent": 4200,
        "impressions": 45000,
        "clicks": 2250,
        "conversions": 89,
        "revenue": 17800,
        "start_date": "2026-03-10T00:00:00",
        "end_date": "2026-04-10T00:00:00",
        "roi": 324
    },
    {
        "id": "cam_003",
        "name": "Google PPC - Logistics Keywords",
        "type": "ppc",
        "status": "active",
        "budget": 12000,
        "spent": 6800,
        "impressions": 89000,
        "clicks": 4450,
        "conversions": 178,
        "revenue": 35600,
        "start_date": "2026-03-05T00:00:00",
        "end_date": "2026-04-05T00:00:00",
        "roi": 424
    },
    {
        "id": "cam_004",
        "name": "SEO Optimization - Transport",
        "type": "seo",
        "status": "completed",
        "budget": 5000,
        "spent": 5000,
        "impressions": 234000,
        "clicks": 11700,
        "conversions": 468,
        "revenue": 70200,
        "start_date": "2026-02-01T00:00:00",
        "end_date": "2026-03-15T00:00:00",
        "roi": 1304
    },
    {
        "id": "cam_005",
        "name": "Winter Trucking Campaign",
        "type": "email",
        "status": "completed",
        "budget": 10000,
        "spent": 10000,
        "impressions": 98000,
        "clicks": 4900,
        "conversions": 245,
        "revenue": 36750,
        "start_date": "2026-01-15T00:00:00",
        "end_date": "2026-02-15T00:00:00",
        "roi": 268
    }
]

LEADS = [
    {
        "id": "lead_001",
        "name": "John Smith",
        "email": "john.smith@fastfreight.com",
        "phone": "+1-800-555-0100",
        "company": "Fast Freight Inc.",
        "status": "qualified",
        "source": "LinkedIn Ads",
        "value": 25000,
        "created_at": "2026-04-01T10:30:00",
        "assigned_to": "Sarah (Sales)"
    },
    {
        "id": "lead_002",
        "name": "Maria Garcia",
        "email": "maria@mapleload.ca",
        "phone": "+1-800-555-0200",
        "company": "Maple Load Canada",
        "status": "contacted",
        "source": "Google PPC",
        "value": 18000,
        "created_at": "2026-04-02T14:15:00",
        "assigned_to": "Mike (Sales)"
    },
    {
        "id": "lead_003",
        "name": "David Chen",
        "email": "david@abcmfg.com",
        "phone": "+1-800-555-0300",
        "company": "ABC Manufacturing",
        "status": "converted",
        "source": "Email Campaign",
        "value": 42000,
        "created_at": "2026-03-28T09:00:00",
        "assigned_to": "Sarah (Sales)"
    },
    {
        "id": "lead_004",
        "name": "Lisa Wong",
        "email": "lisa@globallogistics.com",
        "phone": "+1-800-555-0400",
        "company": "Global Logistics",
        "status": "new",
        "source": "Referral",
        "value": 35000,
        "created_at": "2026-04-03T11:45:00",
        "assigned_to": None
    },
    {
        "id": "lead_005",
        "name": "Robert Brown",
        "email": "robert@premiumsuppliers.com",
        "phone": "+1-800-555-0500",
        "company": "Premium Suppliers",
        "status": "qualified",
        "source": "SEO",
        "value": 15000,
        "created_at": "2026-04-01T08:00:00",
        "assigned_to": "Mike (Sales)"
    }
]

SOCIAL_MEDIA = {
    "linkedin": {"followers": 3420, "engagement": 5.2, "posts": 45, "clicks": 2340},
    "twitter": {"followers": 1890, "engagement": 3.8, "posts": 78, "clicks": 1245},
    "facebook": {"followers": 2560, "engagement": 4.5, "posts": 32, "clicks": 1890}
}

CONTENT_PERFORMANCE = [
    {"title": "10 Ways to Optimize Your Freight Costs", "views": 3450, "clicks": 890, "conversions": 45, "type": "blog"},
    {"title": "Cross-Border Shipping Guide 2026", "views": 2890, "clicks": 756, "conversions": 38, "type": "guide"},
    {"title": "How AI is Transforming Logistics", "views": 4230, "clicks": 1120, "conversions": 56, "type": "blog"},
    {"title": "Winter Trucking Safety Tips", "views": 1870, "clicks": 456, "conversions": 23, "type": "video"}
]


# ==================== API Endpoints ====================

@router.get("/dashboard")
async def get_marketing_dashboard(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get marketing dashboard data"""
    return {
        "metrics": MARKETING_METRICS["summary"],
        "trends": MARKETING_METRICS["trends"],
        "active_campaigns": [c for c in CAMPAIGNS if c["status"] == "active"],
        "recent_leads": LEADS[:5],
        "social_media": SOCIAL_MEDIA,
        "content_performance": CONTENT_PERFORMANCE
    }


@router.get("/campaigns")
async def get_campaigns(
    status: Optional[str] = None,
    type: Optional[str] = None,
    limit: int = 20,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get marketing campaigns"""
    campaigns = CAMPAIGNS.copy()
    
    if status:
        campaigns = [c for c in campaigns if c["status"] == status]
    if type:
        campaigns = [c for c in campaigns if c["type"] == type]
    
    campaigns.sort(key=lambda x: x["start_date"], reverse=True)
    
    return {
        "campaigns": campaigns[:limit],
        "total": len(campaigns)
    }


@router.get("/campaigns/{campaign_id}")
async def get_campaign_details(
    campaign_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get campaign details"""
    campaign = next((c for c in CAMPAIGNS if c["id"] == campaign_id), None)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign


@router.post("/campaigns")
async def create_campaign(
    campaign: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Create a new marketing campaign"""
    new_id = f"cam_{len(CAMPAIGNS) + 1:03d}"
    new_campaign = {
        "id": new_id,
        **campaign,
        "created_at": datetime.now().isoformat()
    }
    CAMPAIGNS.append(new_campaign)
    logger.info(f"Campaign created: {new_id} by {current_user.get('email')}")
    return new_campaign


@router.get("/leads")
async def get_leads(
    status: Optional[str] = None,
    source: Optional[str] = None,
    limit: int = 50,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get marketing leads"""
    leads = LEADS.copy()
    
    if status:
        leads = [l for l in leads if l["status"] == status]
    if source:
        leads = [l for l in leads if l["source"] == source]
    
    leads.sort(key=lambda x: x["created_at"], reverse=True)
    
    return {
        "leads": leads[:limit],
        "total": len(leads),
        "by_status": {
            "new": len([l for l in leads if l["status"] == "new"]),
            "contacted": len([l for l in leads if l["status"] == "contacted"]),
            "qualified": len([l for l in leads if l["status"] == "qualified"]),
            "converted": len([l for l in leads if l["status"] == "converted"]),
            "lost": len([l for l in leads if l["status"] == "lost"])
        }
    }


@router.post("/leads")
async def create_lead(
    lead: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Create a new lead"""
    new_id = f"lead_{len(LEADS) + 1:03d}"
    new_lead = {
        "id": new_id,
        **lead,
        "created_at": datetime.now().isoformat(),
        "status": "new"
    }
    LEADS.append(new_lead)
    logger.info(f"Lead created: {new_id} by {current_user.get('email')}")
    return new_lead


@router.patch("/leads/{lead_id}/status")
async def update_lead_status(
    lead_id: str,
    status: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Update lead status"""
    lead = next((l for l in LEADS if l["id"] == lead_id), None)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    lead["status"] = status
    lead["updated_at"] = datetime.now().isoformat()
    
    return {"message": f"Lead status updated to {status}", "lead": lead}


@router.get("/social")
async def get_social_metrics(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get social media metrics"""
    return SOCIAL_MEDIA


@router.get("/content")
async def get_content_performance(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get content performance metrics"""
    return CONTENT_PERFORMANCE


@router.get("/metrics")
async def get_marketing_metrics(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get marketing metrics summary"""
    return MARKETING_METRICS


@router.get("/roi")
async def get_roi_analysis(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get ROI analysis"""
    total_spent = sum(c["spent"] for c in CAMPAIGNS)
    total_revenue = sum(c["revenue"] for c in CAMPAIGNS)
    
    return {
        "total_spent": total_spent,
        "total_revenue": total_revenue,
        "roi_percentage": ((total_revenue - total_spent) / total_spent * 100) if total_spent > 0 else 0,
        "campaigns_roi": [{"name": c["name"], "roi": c["roi"]} for c in CAMPAIGNS]
    }


@router.get("/forecast")
async def get_marketing_forecast(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get marketing forecast"""
    return {
        "predicted_revenue_next_month": 325000,
        "predicted_leads_next_month": 85,
        "recommended_budget": 25000,
        "optimization_suggestions": [
            "Increase budget for LinkedIn Ads - highest ROI",
            "Optimize email subject lines for better open rates",
            "Target mid-sized logistics companies",
            "Create case studies from converted leads"
        ]
    }