# 📁 D:\GTS Logistics MVP\backend\integrations\loadboards\mock_truckerpath.py

from typing import List


def get_mock_loads() -> List[dict]:
    return [
        {
            "origin": "Chicago, IL",
            "destination": "Atlanta, GA",
            "equipment_type": "Van",
            "price": 1400.0,
            "weight": "20000 lbs",
            "length": 53,
            "notes": "Urgent delivery, must arrive within 2 days",
            "latitude": 41.8781,
            "longitude": -87.6298
        },
        {
            "origin": "Dallas, TX",
            "destination": "Phoenix, AZ",
            "equipment_type": "Flatbed",
            "price": 1700.0,
            "weight": "22000 lbs",
            "length": 48,
            "notes": "Can be grouped with other partials",
            "latitude": 32.7767,
            "longitude": -96.7970
        },
        {
            "origin": "New York, NY",
            "destination": "Boston, MA",
            "equipment_type": "Reefer",
            "price": 900.0,
            "weight": "15000 lbs",
            "length": 53,
            "notes": "Frozen food, requires temperature control",
            "latitude": 40.7128,
            "longitude": -74.0060
        }
    ]
