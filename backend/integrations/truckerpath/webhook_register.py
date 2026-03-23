# 📁 Suggested path: backend/integrations/truckerpath/webhook_register.py
import requests

API_URL = "https://test-api.truckerpath.com/truckload/api/webhooks/add"
API_TOKEN = "put_your_access_token_here"

headers = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}

payload = {
    "url": "https://gabanilogistics.com/api/webhook/receive",  # ← Your webhook endpoint to receive events
    "type": "BOOK"  # or "BID"
}

response = requests.post(API_URL, headers=headers, json=payload)
print(response.status_code, response.json())
