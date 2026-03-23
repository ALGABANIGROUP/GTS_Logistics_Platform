#!/usr/bin/env python
import sys
import asyncio
import json
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from backend.database.config import _get_async_dsn
from backend.security.access_context import build_auth_me_payload

async def test_auth_me():
    dsn = _get_async_dsn()
    engine = create_async_engine(dsn)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # Simulate admin user
        claims = {
            "sub": "352",
            "email": "admin@gabanilogistics.com",
            "role": "super_admin",
        }
        
        # Create a mock request
        class MockRequest:
            def __init__(self):
                self.headers = {}
                self.scope = {"method": "GET", "path": "/auth/me"}
        
        request = MockRequest()
        
        try:
            payload = await build_auth_me_payload(request, session, claims)
            print(json.dumps(payload, indent=2, default=str))
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
    
    await engine.dispose()

asyncio.run(test_auth_me())
