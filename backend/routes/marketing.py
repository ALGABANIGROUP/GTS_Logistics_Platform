from fastapi import APIRouter
from datetime import datetime, timedelta
import random

router = APIRouter(prefix="/ai/marketing", tags=["AI Marketing"])

@router.get("/overview")
async def marketing_overview():
    campaigns = random.randint(5, 20)
    leads = random.randint(1000, 5000)
    conversion_rate = random.uniform(2.0, 5.0)
    budget = random.randint(5000, 20000)
    campaign_types = [
        {"type": "Social Media", "value": random.randint(100, 500)},
        {"type": "Email", "value": random.randint(50, 300)},
        {"type": "PPC", "value": random.randint(80, 400)},
        {"type": "Content", "value": random.randint(30, 200)},
        {"type": "SEO", "value": random.randint(40, 250)},
    ]
    performance = []
    for i in range(7):
        date = (datetime.now() - timedelta(days=6 - i)).strftime("%Y-%m-%d")
        performance.append({
            "date": date,
            "clicks": random.randint(100, 1000),
            "conversions": random.randint(10, 100),
        })
    recommendations = [
        "Increase budget on Social Media campaigns by 15% for better ROI.",
        "Optimize email campaign subject lines to improve open rates.",
        "Consider retargeting visitors who abandoned their carts.",
        "Test new ad creatives for PPC campaigns to reduce cost per click.",
        "Focus on long-tail keywords for SEO to capture niche markets.",
    ]
    return {
        "campaigns": campaigns,
        "leads": leads,
        "conversion_rate": round(conversion_rate, 2),
        "budget": budget,
        "campaign_types": campaign_types,
        "performance": performance,
        "recommendations": recommendations,
    }
