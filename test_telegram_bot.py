#!/usr/bin/env python3
"""
Test script for Telegram Bot integration
"""

import sys
import os
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.services.telegram_service import telegram_service

def test_telegram_configuration():
    """Test Telegram bot configuration"""
    print("🧪 Testing Telegram Bot Configuration")
    print("=" * 50)

    # Check if configured
    is_configured = telegram_service.is_configured()
    can_send_alerts = telegram_service.can_send_alerts()
    print(f"Bot configured: {'✅' if is_configured else '❌'}")
    print(f"Alert destination configured: {'✅' if can_send_alerts else '❌'}")

    if not is_configured:
        print("\n❌ Telegram bot is not configured!")
        print("\nTo configure:")
        print("1. Create a bot with @BotFather on Telegram")
        print("2. Get your BOT_TOKEN")
        print("3. Send /start to your bot and get your CHAT_ID")
        print("4. Add to .env:")
        print("   TELEGRAM_BOT_TOKEN=your_token_here")
        print("   TELEGRAM_CHAT_ID=your_chat_id_here")
        print("   TELEGRAM_ENABLED=true")
        return False

    # Test connection
    print("\n🔍 Testing connection...")
    test_result = telegram_service.test_connection()

    if test_result['success']:
        print("✅ Connection successful!")
        print(f"🤖 Bot: @{test_result.get('bot_username', 'Unknown')}")
        return True
    else:
        print(f"❌ Connection failed: {test_result['message']}")
        return False

def test_incident_alert():
    """Test sending incident alert"""
    print("\n🚨 Testing Incident Alert")
    print("-" * 30)

    if not telegram_service.can_send_alerts():
        print("❌ Telegram not configured, skipping alert test")
        return

    # Sample incident data
    incident_data = {
        'id': 'TEST-INC-001',
        'severity': 'HIGH',
        'service': 'Test Service',
        'error_message': 'This is a test incident alert from GTS system',
        'timestamp': '2026-03-22T10:30:00Z'
    }

    success = telegram_service.send_incident_alert(incident_data)

    if success:
        print("✅ Incident alert sent successfully!")
        print("📱 Check your Telegram for the test message")
    else:
        print("❌ Failed to send incident alert")

def test_system_status():
    """Test sending system status"""
    print("\n📊 Testing System Status Message")
    print("-" * 35)

    if not telegram_service.can_send_alerts():
        print("❌ Telegram not configured, skipping status test")
        return

    success = telegram_service.send_system_status(
        "online",
        "All systems operational - Test message from GTS"
    )

    if success:
        print("✅ System status sent successfully!")
    else:
        print("❌ Failed to send system status")

def main():
    """Main test function"""
    print("📱 GTS Telegram Bot Integration Test")
    print("=" * 50)

    # Test configuration
    config_ok = test_telegram_configuration()

    if not config_ok:
        print("\n💡 Tip: You can still use the Dashboard Chat feature!")
        print("   It's integrated within the system and doesn't require external services.")
        return

    # Test features
    test_incident_alert()
    test_system_status()

    print("\n🎉 Telegram integration test completed!")
    print("\n📋 Next steps:")
    print("1. Configure your bot token and chat ID in .env")
    print("2. Test with real incidents")
    print("3. Consider using Dashboard Chat for team communication")

if __name__ == "__main__":
    main()
