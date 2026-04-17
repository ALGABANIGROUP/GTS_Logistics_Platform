# 📁 Suggested Path: backend/integrations/truckerpath/tracking.py
import requests

API_URL = "https://test-api.truckerpath.com/truckload/api/tracking/"
API_TOKEN = "put_your_access_token_here"

headers = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}

payload = {
    "carrier_name": "Example Carrier",
    "carrier_phone": "+13463263104",
    "carrier_email": "operations@gabanilogistics.com",
    "pick_up": {
        "state": "TX",
        "city": "Austin",
        "address": "14205 N Mo Pac Expy Ste 570",
        "lat": 30.2672,
        "lng": -97.7431,
        "date_local": "2025-04-22T10:00:00"
    },
    "drop_off": {
        "state": "CA",
        "city": "Los Angeles",
        "address": "500 Delivery Blvd",
        "lat": 34.0522,
        "lng": -118.2437,
        "date_local": "2025-04-24T15:00:00"
    },
    "note": "Fragile items, handle with care",
    "shipper_notify_email": "freight@gabanilogistics.com",
    "is_arrival_notified": True
}

response = requests.post(API_URL, headers=headers, json=payload)
print(response.status_code, response.json())
