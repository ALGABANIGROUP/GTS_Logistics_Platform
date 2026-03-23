# backend/services/mailboxes/freight.py

async def get_available_loads():
    """
    🔄 Placeholder Load Board Fetcher
    This function mocks external load board API response.
    Replace with actual API call (e.g. Truckstop, DAT).
    """
    return [
        {
            "origin": "Chicago, IL",
            "destination": "Atlanta, GA",
            "price": 1800.00,
            "equipment_type": "Dry Van",
            "weight": "42000 lbs",
            "length": 53,
            "notes": "Time-sensitive load, delivery by Friday"
        },
        {
            "origin": "Dallas, TX",
            "destination": "Denver, CO",
            "price": 1500.00,
            "equipment_type": "Reefer",
            "weight": "36000 lbs",
            "length": 53,
            "notes": "Requires temp control"
        }
    ]
