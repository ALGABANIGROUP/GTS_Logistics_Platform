from typing import Dict, List
import logging
from datetime import datetime
from backend.database import async_session
from backend.models.marketing import Campaign, CampaignStatus

logger = logging.getLogger(__name__)

class CampaignService:
    """
    Marketing campaigns management service - real data
    """

    async def create_campaign(self, campaign_data: Dict) -> Dict:
        """
        Create a new marketing campaign
        """
        async with async_session() as session:
            campaign = Campaign(
                name=campaign_data["name"],
                description=campaign_data.get("description"),
                type=campaign_data["type"],
                target_audience=campaign_data.get("target_audience"),
                budget=campaign_data.get("budget", 0),
                start_date=campaign_data.get("start_date", datetime.now().date()),
                end_date=campaign_data.get("end_date"),
                status=CampaignStatus.DRAFT,
                created_by=campaign_data.get("created_by", "system")
            )
            session.add(campaign)
            await session.commit()
            await session.refresh(campaign)

            return {
                "success": True,
                "campaign_id": campaign.id,
                "message": "Campaign created successfully"
            }

    async def get_active_campaigns(self) -> List[Dict]:
        """
        Get active campaigns
        """
        async with async_session() as session:
            from sqlalchemy import select
            query = select(Campaign).where(
                Campaign.status == CampaignStatus.ACTIVE,
                Campaign.start_date <= datetime.now().date(),
                (Campaign.end_date >= datetime.now().date()) | (Campaign.end_date == None)
            )
            result = await session.execute(query)
            campaigns = result.scalars().all()

            return [
                {
                    "id": c.id,
                    "name": c.name,
                    "description": c.description,
                    "type": c.type,
                    "budget": c.budget,
                    "start_date": c.start_date.isoformat(),
                    "end_date": c.end_date.isoformat() if c.end_date else None,
                    "status": c.status.value
                }
                for c in campaigns
            ]