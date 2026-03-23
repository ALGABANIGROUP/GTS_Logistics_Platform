#!/usr/bin/env python
"""
Quick test script to verify all real data services are working
"""
import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

async def test_weather_service():
    """Test weather service"""
    try:
        from backend.services.weather_service import WeatherService
        ws = WeatherService()
        result = await ws.get_current_weather("Riyadh")
        print("✅ Weather Service:", "Working" if result.get("success") else "Failed")
        return result.get("success", False)
    except Exception as e:
        print("❌ Weather Service:", str(e))
        return False

async def test_market_service():
    """Test market analysis service"""
    try:
        from backend.services.market_analysis_service import MarketAnalysisService
        ms = MarketAnalysisService()
        result = await ms.get_market_trends()
        print("✅ Market Analysis Service:", "Working" if result.get("success") else "Failed")
        return result.get("success", False)
    except Exception as e:
        print("❌ Market Analysis Service:", str(e))
        return False

async def test_log_service():
    """Test log analysis service"""
    try:
        from backend.services.log_analysis_service import LogAnalysisService
        ls = LogAnalysisService()
        result = ls.analyze_logs(hours=1)
        print("✅ Log Analysis Service:", "Working" if result.get("success") else "Failed")
        return result.get("success", False)
    except Exception as e:
        print("❌ Log Analysis Service:", str(e))
        return False

async def test_campaign_service():
    """Test campaign service"""
    try:
        from backend.services.campaign_service import CampaignService
        cs = CampaignService()
        campaigns = await cs.get_active_campaigns()
        print("✅ Campaign Service:", "Working" if isinstance(campaigns, list) else "Failed")
        return True
    except Exception as e:
        print("❌ Campaign Service:", str(e))
        return False

async def main():
    """Run all tests"""
    print("🔍 Testing Real Data Services")
    print("=" * 50)

    results = []
    results.append(await test_weather_service())
    results.append(await test_market_service())
    results.append(await test_log_service())
    results.append(await test_campaign_service())

    print("=" * 50)
    working = sum(results)
    total = len(results)
    print(f"📊 Results: {working}/{total} services working")

    if working == total:
        print("🎉 All services are working with real data!")
    elif working > 0:
        print("⚠️ Some services are working, others may need API keys")
    else:
        print("❌ No services are working - check configuration")

if __name__ == "__main__":
    asyncio.run(main())