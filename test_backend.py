#!/usr/bin/env python3
"""Simple test script to check if the backend is running."""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

try:
    import requests
    response = requests.get('http://localhost:8000/api/v1/health', timeout=5)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    print("✅ Backend is running successfully!")
except Exception as e:
    print(f"❌ Error: {e}")
    print("Backend may not be running or there are connection issues.")