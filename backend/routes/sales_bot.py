# backend/routes/sales_bot.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any
from datetime import datetime

from backend.database.session import get_async_session
from backend.security.auth import get_current_user

router = APIRouter(prefix="/api/v1/sales", tags=["Sales Bot"])


@router.get("/dashboard")
async def get_sales_dashboard(
    current_user: Dict[str, Any] = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """Get sales dashboard data"""
    try:
        # Seed data for sales dashboard
        return {
            "summary": {
                "total_revenue": 284500,
                "total_orders": 156,
                "active_customers": 42,
                "conversion_rate": 24.5,
                "average_order_value": 1824,
                "revenue_growth": 15.5,
                "monthly_target": 300000,
                "monthly_achieved": 284500
            },
            "recent_activities": [
                {
                    "id": 1,
                    "action": "New lead acquired",
                    "customer": "Fast Freight Inc.",
                    "value": 12500,
                    "status": "qualified",
                    "date": datetime.now().isoformat()
                },
                {
                    "id": 2,
                    "action": "Quote sent",
                    "customer": "Maple Load Canada",
                    "value": 8750,
                    "status": "pending",
                    "date": datetime.now().isoformat()
                },
                {
                    "id": 3,
                    "action": "Deal closed",
                    "customer": "GTS Logistics",
                    "value": 34200,
                    "status": "won",
                    "date": (datetime.now().replace(day=datetime.now().day - 1)).isoformat()
                },
                {
                    "id": 4,
                    "action": "Follow-up call",
                    "customer": "ABC Manufacturing",
                    "value": 5600,
                    "status": "in_progress",
                    "date": (datetime.now().replace(day=datetime.now().day - 2)).isoformat()
                }
            ],
            "pipeline": [
                {"stage": "Lead", "count": 23, "value": 184000},
                {"stage": "Qualified", "count": 15, "value": 125000},
                {"stage": "Proposal", "count": 8, "value": 89000},
                {"stage": "Negotiation", "count": 5, "value": 67000},
                {"stage": "Closed Won", "count": 12, "value": 245000}
            ],
            "top_customers": [
                {
                    "id": 1,
                    "name": "Fast Freight Inc.",
                    "revenue": 125000,
                    "orders": 28,
                    "last_order": "2026-04-01"
                },
                {
                    "id": 2,
                    "name": "Maple Load Canada",
                    "revenue": 89000,
                    "orders": 19,
                    "last_order": "2026-03-28"
                },
                {
                    "id": 3,
                    "name": "GTS Logistics",
                    "revenue": 67000,
                    "orders": 15,
                    "last_order": "2026-03-25"
                },
                {
                    "id": 4,
                    "name": "ABC Manufacturing",
                    "revenue": 34000,
                    "orders": 8,
                    "last_order": "2026-03-20"
                }
            ],
            "performance_metrics": [
                {
                    "metric": "Calls Made",
                    "target": 200,
                    "achieved": 185,
                    "percentage": 92.5
                },
                {
                    "metric": "Meetings Scheduled",
                    "target": 50,
                    "achieved": 42,
                    "percentage": 84
                },
                {
                    "metric": "Proposals Sent",
                    "target": 30,
                    "achieved": 28,
                    "percentage": 93.3
                },
                {
                    "metric": "Deals Closed",
                    "target": 20,
                    "achieved": 18,
                    "percentage": 90
                }
            ],
            "bot_status": {
                "name": "AI Sales Bot",
                "status": "active",
                "last_run": datetime.now().isoformat(),
                "tasks_completed": 156,
                "success_rate": 94.5
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sales dashboard error: {str(e)}")


@router.post("/leads")
async def create_lead(
    lead_data: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """Create a new sales lead"""
    try:
        # Reference implementation - in real app this would save to database
        return {
            "id": 123,
            "name": lead_data.get("name", ""),
            "email": lead_data.get("email", ""),
            "company": lead_data.get("company", ""),
            "status": "NEW",
            "created_at": datetime.now().isoformat(),
            "created_by": current_user.get("id")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Create lead error: {str(e)}")


@router.put("/leads/{lead_id}/status")
async def update_lead_status(
    lead_id: int,
    status_data: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """Update lead status"""
    try:
        # Reference implementation
        return {
            "id": lead_id,
            "status": status_data.get("status", "NEW"),
            "updated_at": datetime.now().isoformat(),
            "updated_by": current_user.get("id")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Update lead status error: {str(e)}")


@router.post("/deals")
async def create_deal(
    deal_data: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """Create a new sales deal"""
    try:
        # Reference implementation
        return {
            "id": 456,
            "customer": deal_data.get("customer", ""),
            "value": deal_data.get("value", 0),
            "stage": deal_data.get("stage", "DISCOVERY"),
            "probability": deal_data.get("probability", 50),
            "expected_close": deal_data.get("close_date", ""),
            "created_at": datetime.now().isoformat(),
            "created_by": current_user.get("id")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Create deal error: {str(e)}")


@router.put("/deals/{deal_id}/stage")
async def update_deal_stage(
    deal_id: int,
    stage_data: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """Update deal stage"""
    try:
        # Reference implementation
        return {
            "id": deal_id,
            "stage": stage_data.get("stage", "DISCOVERY"),
            "updated_at": datetime.now().isoformat(),
            "updated_by": current_user.get("id")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Update deal stage error: {str(e)}")


@router.post("/optimize")
async def optimize_sales(
    current_user: Dict[str, Any] = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """Trigger AI sales optimization"""
    try:
        # Reference AI optimization response
        return {
            "status": "success",
            "message": "AI Sales optimization triggered",
            "recommendations": [
                "Focus on high-value leads in the pipeline",
                "Schedule follow-ups for deals in negotiation stage",
                "Target customers with lifetime value > $50K"
            ],
            "executed_at": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sales optimization error: {str(e)}")