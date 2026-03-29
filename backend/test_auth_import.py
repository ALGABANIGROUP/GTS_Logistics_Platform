#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

try:
    from routes.auth import router as auth_router
    print('auth_router imported successfully:', auth_router is not None)
    if auth_router:
        print('Router routes:', [route.path for route in auth_router.routes])
except Exception as e:
    print('Import failed:', e)
    import traceback
    traceback.print_exc()