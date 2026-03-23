# 📁 Suggested path: backend/integrations/truckerpath/post_load.py
import requests

API_URL = "https://test-api.truckerpath.com/truckload/api/shipments/v2"
API_TOKEN = "insert_access_token_here"  # 🔐 Insert the actual token here

headers = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}

payload = {
    "company_id": "1684192",  # ← Use MC Number as the company ID
    "contact_info": {
        "contact_email": "freight@gabanilogistics.com",
        "contact_first_name": "Yassir",
        "contact_last_name": "Mossttafa",
        "contact_phone_number": "+13463263104",
        "contact_phone_ext": ""
    },
    "shipment_info": {
        "equipment": ["Dry Van"],
        "load_size": "FULL",
        "description": "Office Furniture",
        "shipment_weight": 30000,
        "shipment_dimensions": {},
        "requirements": "Must call before pickup",
        "stop_list": [
            {
                "type": "PICKUP",
                "state": "TX",
                "city": "Austin",
                "address": "1000 Pickup St",
                "lat": 30.2672,
                "lng": -97.7431,
                "date_local": "2025-04-22T10:00:00"
            },
            {
                "type": "DROPOFF",
                "state": "CA",
                "city": "Los Angeles",
                # ... complete the rest of the payload as needed
            }
        ]
    }
}

response = requests.post(API_URL, headers=headers, json=payload)

print("Status Code:", response.status_code)
print("Response:", response.json())
