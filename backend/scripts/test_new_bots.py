# backend/scripts/test_new_bots.py
"""
Test script for new intelligence mode bots:
- SafeManagerBot
- SalesIntelligenceBot
- LegalCounselBot
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# Import directly to avoid __init__ issues
import importlib.util

def import_bot_module(module_name, file_path):
    """Import bot module directly from file path"""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

# Import bots directly
safe_manager_module = import_bot_module("safe_manager", backend_dir / "bots" / "safe_manager.py")
sales_intelligence_module = import_bot_module("sales_intelligence", backend_dir / "bots" / "sales_intelligence.py")
legal_counsel_module = import_bot_module("legal_counsel", backend_dir / "bots" / "legal_counsel.py")

SafeManagerBot = safe_manager_module.SafeManagerBot
SalesIntelligenceBot = sales_intelligence_module.SalesIntelligenceBot
LegalCounselBot = legal_counsel_module.LegalCounselBot


async def test_safe_manager():
    """Test Safety Manager Bot"""
    print("\n" + "=" * 60)
    print("🔒 Testing SafeManagerBot")
    print("=" * 60)
    
    bot = SafeManagerBot()
    
    # Test status
    print("\n1️⃣ Testing status...")
    status = await bot.status()
    print(f"   Status: {status}")
    assert status["ok"], "Status should be OK"
    assert status["bot"] == "safe_manager", "Bot name should be safe_manager"
    
    # Test config
    print("\n2️⃣ Testing config...")
    config = await bot.config()
    print(f"   Config: {config}")
    assert "capabilities" in config, "Config should include capabilities"
    
    # Test track incident
    print("\n3️⃣ Testing track_incident...")
    incident_result = await bot.track_incident({
        "type": "vehicle_accident",
        "severity": "medium",
        "location": "Highway 401, Toronto",
        "description": "Minor collision during lane change",
        "reported_by": "Driver John Doe"
    })
    print(f"   Result: {incident_result}")
    assert incident_result["ok"], "Track incident should succeed"
    assert "incident" in incident_result, "Should return incident details"
    
    # Test compliance check
    print("\n4️⃣ Testing check_compliance...")
    compliance_result = await bot.check_compliance("driver")
    print(f"   Result: {compliance_result}")
    assert compliance_result["ok"], "Compliance check should succeed"
    assert "compliance_score" in compliance_result, "Should return compliance score"
    
    # Test report generation
    print("\n5️⃣ Testing generate_safety_report...")
    report = await bot.generate_safety_report("monthly")
    print(f"   Report: {report}")
    assert report["ok"], "Report generation should succeed"
    
    print("\n✅ SafeManagerBot tests passed!")
    return True


async def test_sales_intelligence():
    """Test Sales Intelligence Bot"""
    print("\n" + "=" * 60)
    print("💰 Testing SalesIntelligenceBot")
    print("=" * 60)
    
    bot = SalesIntelligenceBot()
    
    # Test status
    print("\n1️⃣ Testing status...")
    status = await bot.status()
    print(f"   Status: {status}")
    assert status["ok"], "Status should be OK"
    assert status["bot"] == "sales_intelligence", "Bot name should be sales_intelligence"
    
    # Test config
    print("\n2️⃣ Testing config...")
    config = await bot.config()
    print(f"   Config: {config}")
    assert "capabilities" in config, "Config should include capabilities"
    
    # Test customer analysis
    print("\n3️⃣ Testing analyze_customer_behavior...")
    analysis = await bot.analyze_customer_behavior()
    print(f"   Analysis: {analysis}")
    assert analysis["ok"], "Customer analysis should succeed"
    assert "analysis" in analysis, "Should return analysis data"
    
    # Test revenue forecast
    print("\n4️⃣ Testing predict_revenue_growth...")
    forecast = await bot.predict_revenue_growth(6)
    print(f"   Forecast (6 months): {forecast}")
    assert forecast["ok"], "Revenue forecast should succeed"
    assert "forecast" in forecast, "Should return forecast data"
    
    # Test sales optimization
    print("\n5️⃣ Testing optimize_sales_process...")
    optimization = await bot.optimize_sales_process()
    print(f"   Optimization: {optimization}")
    assert optimization["ok"], "Sales optimization should succeed"
    
    print("\n✅ SalesIntelligenceBot tests passed!")
    return True


async def test_legal_counsel():
    """Test Legal Counsel Bot"""
    print("\n" + "=" * 60)
    print("⚖️  Testing LegalCounselBot")
    print("=" * 60)
    
    bot = LegalCounselBot()
    
    # Test status
    print("\n1️⃣ Testing status...")
    status = await bot.status()
    print(f"   Status: {status}")
    assert status["ok"], "Status should be OK"
    assert status["bot"] == "legal_counsel", "Bot name should be legal_counsel"
    
    # Test config
    print("\n2️⃣ Testing config...")
    config = await bot.config()
    print(f"   Config: {config}")
    assert "capabilities" in config, "Config should include capabilities"
    assert "legal_domains" in config, "Should include legal domains"
    
    # Test contract review
    print("\n3️⃣ Testing review_contract...")
    contract_text = """
    SERVICE AGREEMENT
    
    This Agreement is entered into between GTS Logistics Inc. ("Company")
    and ABC Carrier Inc. ("Carrier") for the provision of transportation services.
    
    1. TERM: This agreement shall commence on January 1, 2026
    2. PAYMENT TERMS: Net 30 days from invoice date
    3. LIABILITY: Carrier agrees to maintain minimum $1M liability insurance
    """
    review = await bot.review_contract(contract_text)
    print(f"   Review: {review}")
    assert review["ok"], "Contract review should succeed"
    assert "analysis" in review, "Should return analysis"
    
    # Test deadline tracking
    print("\n4️⃣ Testing track_deadlines...")
    deadlines = await bot.track_deadlines()
    print(f"   Deadlines: {deadlines}")
    assert deadlines["ok"], "Deadline tracking should succeed"
    assert "deadlines" in deadlines, "Should return deadlines"
    
    # Test compliance check
    print("\n5️⃣ Testing check_legal_compliance...")
    compliance = await bot.check_legal_compliance("corporate_law")
    print(f"   Compliance: {compliance}")
    assert compliance["ok"], "Compliance check should succeed"
    assert "compliance_rate" in compliance, "Should return compliance rate"
    
    print("\n✅ LegalCounselBot tests passed!")
    return True


async def main():
    """Run all bot tests"""
    print("\n" + "🚀 " * 15)
    print("🚀 NEW INTELLIGENCE BOTS TEST SUITE")
    print("🚀 " * 15)
    
    try:
        # Test each bot
        await test_safe_manager()
        await test_sales_intelligence()
        await test_legal_counsel()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        print("\n📋 Summary:")
        print("   🔒 SafeManagerBot - Operational")
        print("   💰 SalesIntelligenceBot - Operational")
        print("   ⚖️  LegalCounselBot - Operational")
        print("\n🎯 Next steps:")
        print("   1. Register bots in main.py (✅ Done)")
        print("   2. Add bot policies (✅ Done)")
        print("   3. Test via API endpoints")
        print("   4. Update frontend to display new bots")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
