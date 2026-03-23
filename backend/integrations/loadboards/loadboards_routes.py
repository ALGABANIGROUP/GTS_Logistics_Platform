# backend/routes/loadboards_routes.py
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from backend.integrations.loadboards.registry import get_provider

router = APIRouter(prefix="/loadboards", tags=["Load Boards"])

@router.get("/ping")
async def ping(provider: str = Query(..., description="Provider name, e.g., truckerpath")):
    try:
        p = get_provider(provider)
        return await p.ping()
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/{provider}/company")
async def create_company(provider: str, payload: dict):
    try:
        p = get_provider(provider)
        return await p.create_company(payload)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/{provider}/loads")
async def post_load(provider: str, payload: dict):
    try:
        p = get_provider(provider)
        return await p.post_load(payload)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/{provider}/webhook")
async def register_webhook(provider: str, payload: dict):
    try:
        p = get_provider(provider)
        return await p.register_webhook(payload)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/{provider}/webhook/add")
async def register_webhook_add(provider: str, payload: dict):
    try:
        p = get_provider(provider)
        return await p.register_webhook_add(payload)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/{provider}/tracking")
async def tracking_create(provider: str, payload: dict):
    try:
        p = get_provider(provider)
        return await p.tracking_create(payload)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/{provider}/tracking/points")
async def push_tracking_points(provider: str, payload: dict):
    try:
        p = get_provider(provider)
        return await p.push_tracking_points(payload)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
