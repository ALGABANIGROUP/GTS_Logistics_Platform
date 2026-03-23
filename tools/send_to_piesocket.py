# E:/GTS Logistics/tools/send_to_gts_websocket.py

import asyncio
import websockets
import json
import random
import time

async def send_truck_data():
    uri = "ws://localhost:8000/ws/truck-locations?token=your_jwt_token_here"

    async with websockets.connect(uri) as websocket:
        while True:
            truck_data = {
                "truck_id": random.randint(1000, 9999),
                "latitude": round(random.uniform(24.0, 26.0), 6),
                "longitude": round(random.uniform(54.0, 56.0), 6),
                "status": random.choice(["Loading", "In Transit", "Delivered"])
            }
            await websocket.send(json.dumps(truck_data))
            print("✅ Sent:", truck_data)
            await asyncio.sleep(3)

if __name__ == "__main__":
    asyncio.run(send_truck_data())
