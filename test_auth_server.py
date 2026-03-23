import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
import asyncio

# Mock database dependency
async def mock_get_db():
    raise RuntimeError("DB dependency is not available")

# Override the get_db_async in auth
import backend.security.auth as auth_module
auth_module.get_db_async = mock_get_db

from backend.security.auth import router as auth_router

app = FastAPI()

app.include_router(auth_router, prefix="/auth")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)