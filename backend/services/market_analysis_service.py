import aiohttp
from typing import Dict, List, Optional
import logging
from datetime import datetime
from backend.core.settings import settings

logger = logging.getLogger(__name__)

class MarketAnalysisService:
    """
    خدمة تحليل السوق - متصلة بـ APIs خارجية
    """

    def __init__(self):
        self.alpha_vantage_key = settings.ALPHA_VANTAGE_KEY
        self.marketaux_key = settings.MARKETAUX_KEY

        logger.info("✅ Market Analysis Service initialized")

    async def get_market_trends(self, sector: str = "transportation") -> Dict:
        """
        Get market trends from Alpha Vantage
        """
        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    "function": "SECTOR",
                    "apikey": self.alpha_vantage_key
                }
                async with session.get("https://www.alphavantage.co/query", params=params) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return {
                            "success": True,
                            "sector": sector,
                            "trends": data.get("Rank A: Real-Time Performance", {}),
                            "timestamp": datetime.now().isoformat()
                        }
                    else:
                        return {"success": False, "error": f"API error: {resp.status}"}
        except Exception as e:
            logger.error(f"Error fetching market trends: {e}")
            return {"success": False, "error": str(e)}

    async def get_competitor_news(self, company: str = "GTS Logistics") -> Dict:
        """
        Get competitor news
        """
        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    "api_token": self.marketaux_key,
                    "search": company,
                    "language": "en",
                    "limit": 10
                }
                async with session.get("https://api.marketaux.com/v1/news/all", params=params) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return {
                            "success": True,
                            "news": data.get("data", []),
                            "total": data.get("meta", {}).get("total", 0),
                            "timestamp": datetime.now().isoformat()
                        }
                    else:
                        return {"success": False, "error": f"API error: {resp.status}"}
        except Exception as e:
            logger.error(f"Error fetching competitor news: {e}")
            return {"success": False, "error": str(e)}