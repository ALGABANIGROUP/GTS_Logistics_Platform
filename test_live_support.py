#!/usr/bin/env python3
"""
Test script for Live Support Assistant
"""

import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

async def test_live_support():
    """Test the Live Support Service"""
    try:
        from backend.services.live_support_service import LiveSupportService

        print("🔧 Testing Live Support Service...")

        # Initialize service
        service = LiveSupportService()
        print("✅ Service initialized")

        # Test different intents
        test_messages = [
            "Show system health",
            "Any recent errors?",
            "Security status",
            "Current weather",
            "Financial summary",
            "Fleet status",
            "Hello"
        ]

        for message in test_messages:
            print(f"\n📤 Testing: {message}")
            try:
                result = await service.process_message(
                    user_id="test_user",
                    message=message
                )
                print("✅ Response received"                print(f"🤖 Intent: {result['intent']}")
                print(f"💬 Response preview: {result['response'][:100]}...")

            except Exception as e:
                print(f"❌ Error: {e}")

        print("\n🎉 Live Support Service test completed!")

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure all dependencies are installed and models exist")
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_live_support())