#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("Testing imports...")

try:
    from database.session import get_async_session
    print('database.session imported successfully')
except Exception as e:
    print('database.session import failed:', e)

try:
    from models.user import User
    print('models.user imported successfully')
except Exception as e:
    print('models.user import failed:', e)

try:
    from config import Settings
    print('config imported successfully')
except Exception as e:
    print('config import failed:', e)