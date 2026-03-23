#!/usr/bin/env python3
"""
Transport Tracking System - Test & Demo Script

Run this script to test the transport API endpoints and WebSocket connections.
Requires: requests, websocket-client

Installation:
    pip install requests websocket-client
"""

import requests
import json
import asyncio
import websockets
from datetime import datetime, timedelta

# Configuration
BASE_URL = "http://localhost:8000"
API_VERSION = "v1"
API_BASE = f"{BASE_URL}/api/{API_VERSION}/transport"
WS_BASE = f"ws://localhost:8000/api/{API_VERSION}/transport"

# Sample data generators
def get_sample_shipment():
    return {
        "shipment_number": f"SHP-{datetime.now().timestamp()}",
        "origin_latitude": 40.7128,
        "origin_longitude": -74.0060,
        "origin_address": "123 Main St, New York, NY 10001",
        "destination_latitude": 34.0522,
        "destination_longitude": -118.2437,
        "destination_address": "456 Park Ave, Los Angeles, CA 90001",
        "shipment_type": "full_truckload",
        "weight_kg": 5000,
        "goods_description": "Electronics and components",
        "base_price": 2500.00,
        "total_price": 2750.00,
        "status": "pending"
    }


def get_sample_truck():
    return {
        "license_plate": f"TEST-{int(datetime.now().timestamp())}",
        "truck_number": "TRUCK-001",
        "latitude": 35.5353,
        "longitude": -97.4867,
        "speed": 65.5,
        "heading": 45,
        "status": "moving",
        "driver_name": "John Smith",
        "driver_id": 1
    }


# Test Functions
def test_shipments_endpoints():
    """Test shipment-related endpoints"""
    print("\n" + "="*50)
    print("TESTING SHIPMENT ENDPOINTS")
    print("="*50)
    
    # Get all shipments
    print("\n1. GET /shipments")
    try:
        response = requests.get(f"{API_BASE}/shipments")
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Shipments: {data.get('total', 0)} total")
        if data.get('data'):
            print(f"First shipment: {data['data'][0].get('name', 'N/A')}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Get shipment with specific ID
    print("\n2. GET /shipments/1")
    try:
        response = requests.get(f"{API_BASE}/shipments/1")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(json.dumps(response.json(), indent=2))
    except Exception as e:
        print(f"Error: {e}")
    
    # Track specific shipment
    print("\n3. GET /shipments/1/track")
    try:
        response = requests.get(f"{API_BASE}/shipments/1/track")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Progress: {data.get('progress')}%")
            print(f"Distance remaining: {data.get('distance_remaining')} km")
            print(f"ETA: {data.get('estimated_arrival')}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Update location
    print("\n4. POST /shipments/1/update-location")
    try:
        location = {"lat": 35.7, "lng": -97.5}
        response = requests.post(
            f"{API_BASE}/shipments/1/update-location",
            json=location
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")


def test_truck_endpoints():
    """Test truck-related endpoints"""
    print("\n" + "="*50)
    print("TESTING TRUCK ENDPOINTS")
    print("="*50)
    
    # Get all trucks
    print("\n1. GET /trucks")
    try:
        response = requests.get(f"{API_BASE}/trucks")
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Active trucks: {data.get('total', 0)}")
        if data.get('data'):
            truck = data['data'][0]
            print(f"First truck: {truck.get('license_plate', 'N/A')}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Get specific truck
    print("\n2. GET /trucks/1")
    try:
        response = requests.get(f"{API_BASE}/trucks/1")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(json.dumps(response.json(), indent=2))
    except Exception as e:
        print(f"Error: {e}")
    
    # Update truck location
    print("\n3. POST /trucks/1/location")
    try:
        location_data = {
            "latitude": 35.6,
            "longitude": -97.4,
            "speed": 68.5,
            "heading": 50,
            "status": "moving"
        }
        response = requests.post(
            f"{API_BASE}/trucks/1/location",
            json=location_data
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")


def test_route_optimization():
    """Test route optimization"""
    print("\n" + "="*50)
    print("TESTING ROUTE OPTIMIZATION")
    print("="*50)
    
    print("\n1. GET /routes/optimize")
    try:
        params = {
            "origin": "New York, NY",
            "destination": "Los Angeles, CA",
        }
        response = requests.get(
            f"{API_BASE}/routes/optimize",
            params=params
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Distance: {data.get('total_distance')}")
            print(f"Estimated time: {data.get('estimated_time')}")
            print(f"Fuel estimate: {data.get('fuel_estimate')}")
    except Exception as e:
        print(f"Error: {e}")


def test_analytics():
    """Test analytics endpoints"""
    print("\n" + "="*50)
    print("TESTING ANALYTICS")
    print("="*50)
    
    # Statistics
    print("\n1. GET /statistics")
    try:
        response = requests.get(f"{API_BASE}/statistics")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Total shipments: {data.get('total_shipments')}")
            print(f"In transit: {data.get('in_transit')}")
            print(f"Delivered: {data.get('delivered')}")
            print(f"Active trucks: {data.get('active_trucks')}")
            print(f"Avg speed: {data.get('avg_speed'):.1f} mph")
    except Exception as e:
        print(f"Error: {e}")
    
    # Performance
    print("\n2. GET /performance")
    try:
        response = requests.get(f"{API_BASE}/performance")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"On-time delivery: {data.get('on_time_delivery')}%")
            print(f"Fuel efficiency: {data.get('fuel_efficiency')} km/liter")
            print(f"Driver safety score: {data.get('driver_safety_score')}")
            print(f"Customer satisfaction: {data.get('customer_satisfaction')}/5")
    except Exception as e:
        print(f"Error: {e}")


async def test_websocket_tracking():
    """Test WebSocket tracking connection"""
    print("\n" + "="*50)
    print("TESTING WEBSOCKET - TRACKING")
    print("="*50)
    
    try:
        ws_url = f"{WS_BASE}/ws/tracking"
        print(f"\nConnecting to: {ws_url}")
        
        async with websockets.connect(ws_url) as websocket:
            print("✓ Connected!")
            
            # Subscribe to updates
            subscribe_msg = {
                "type": "subscribe",
                "channel": "all"
            }
            await websocket.send(json.dumps(subscribe_msg))
            print("→ Sent subscription request")
            
            # Receive initial response
            response = await asyncio.wait_for(websocket.recv(), timeout=5)
            print(f"← Received: {response}")
            
            # Keep connection open for a few seconds
            for i in range(3):
                try:
                    ping = {"type": "ping"}
                    await websocket.send(json.dumps(ping))
                    print(f"→ Ping {i+1}")
                    
                    msg = await asyncio.wait_for(websocket.recv(), timeout=2)
                    print(f"← {msg}")
                except asyncio.TimeoutError:
                    print("  (no message)")
                except Exception as e:
                    print(f"Error: {e}")
                    
                await asyncio.sleep(1)
    
    except Exception as e:
        print(f"WebSocket Error: {e}")


def main():
    """Run all tests"""
    print("\n" + "="*50)
    print("TRANSPORT TRACKING SYSTEM - TEST SUITE")
    print("="*50)
    print(f"API Base: {API_BASE}")
    print(f"WS Base: {WS_BASE}")
    
    # Check if backend is running
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=2)
        if response.status_code != 200:
            print(f"\n⚠ Backend might not be running properly")
    except:
        print(f"\n⚠ Cannot connect to backend at {BASE_URL}")
        print("  Make sure FastAPI is running: uvicorn backend.main:app --reload")
        return
    
    # Run all tests
    test_shipments_endpoints()
    test_truck_endpoints()
    test_route_optimization()
    test_analytics()
    
    # Test WebSocket
    print("\nTesting WebSocket (requires Python 3.7+)...")
    try:
        asyncio.run(test_websocket_tracking())
    except Exception as e:
        print(f"WebSocket test skipped: {e}")
    
    print("\n" + "="*50)
    print("TEST SUITE COMPLETED")
    print("="*50)


if __name__ == "__main__":
    main()
