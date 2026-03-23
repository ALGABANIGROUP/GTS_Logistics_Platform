#!/usr/bin/env python3
"""
Test script for Telegram webhook endpoint
"""

import requests
import json

def test_telegram_webhook():
    """Test the Telegram webhook health endpoint"""
    try:
        url = "http://localhost:8000/api/v1/telegram/health"
        response = requests.get(url, timeout=5)

        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")

        if response.status_code == 200:
            print("✅ Telegram webhook health check passed!")
            return True
        else:
            print("❌ Telegram webhook health check failed!")
            return False

    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False

def test_telegram_webhook_with_update():
    """Test the webhook with a sample Telegram update"""
    try:
        url = "http://localhost:8000/api/v1/telegram/webhook"

        # Sample Telegram update
        sample_update = {
            "update_id": 123456789,
            "message": {
                "message_id": 1,
                "from": {
                    "id": 123456789,
                    "is_bot": False,
                    "first_name": "Test",
                    "username": "testuser"
                },
                "chat": {
                    "id": 123456789,
                    "type": "private"
                },
                "date": 1640995200,
                "text": "/start"
            }
        }

        headers = {"Content-Type": "application/json"}
        response = requests.post(url, json=sample_update, headers=headers, timeout=10)

        print(f"Webhook Status Code: {response.status_code}")
        print(f"Webhook Response: {response.text}")

        if response.status_code == 200:
            print("✅ Telegram webhook test passed!")
            return True
        else:
            print("❌ Telegram webhook test failed!")
            return False

    except requests.exceptions.RequestException as e:
        print(f"❌ Webhook test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Telegram Webhook Integration")
    print("=" * 50)

    # Test health endpoint
    print("\n1. Testing health endpoint...")
    health_ok = test_telegram_webhook()

    # Test webhook endpoint
    print("\n2. Testing webhook endpoint...")
    webhook_ok = test_telegram_webhook_with_update()

    print("\n" + "=" * 50)
    if health_ok and webhook_ok:
        print("🎉 All Telegram webhook tests passed!")
    else:
        print("❌ Some tests failed. Check the logs above.")