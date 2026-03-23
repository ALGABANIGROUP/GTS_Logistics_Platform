import asyncio
from datetime import datetime, timedelta
from backend.services.campaign_service import CampaignService

async def seed_campaigns():
    """
    إدخال حملات تسويقية حقيقية
    """
    service = CampaignService()

    campaigns = [
        {
            "name": "تخفيضات الربيع - شحن مجاني",
            "description": "عرض خاص: شحن مجاني لأول 100 عميل",
            "type": "promotion",
            "target_audience": "new_customers",
            "budget": 5000,
            "start_date": datetime.now().date(),
            "end_date": (datetime.now() + timedelta(days=30)).date()
        },
        {
            "name": "برنامج ولاء العملاء",
            "description": "خصم 10% للعملاء الدائمين",
            "type": "loyalty",
            "target_audience": "existing_customers",
            "budget": 3000,
            "start_date": datetime.now().date(),
            "end_date": (datetime.now() + timedelta(days=60)).date()
        },
        {
            "name": "حملة رمضان المبارك",
            "description": "عروض خاصة بمناسبة الشهر الكريم",
            "type": "seasonal",
            "target_audience": "all",
            "budget": 10000,
            "start_date": (datetime.now() + timedelta(days=7)).date(),
            "end_date": (datetime.now() + timedelta(days=37)).date()
        }
    ]

    for campaign in campaigns:
        result = await service.create_campaign(campaign)
        if result["success"]:
            print(f"✅ Created campaign: {campaign['name']}")
        else:
            print(f"❌ Failed to create: {campaign['name']}")

if __name__ == "__main__":
    asyncio.run(seed_campaigns())