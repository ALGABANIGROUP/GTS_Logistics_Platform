from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from backend.integrations.loadboards.registry import get_provider, list_providers

router = APIRouter(prefix="/loadboards", tags=["Loadboards"])


@router.get("/")
async def list_boards():
    providers = list_providers()
    return {
        "ok": True,
        "boards": sorted(providers.keys()),
        "providers": providers,
    }


@router.get("/ping")
async def ping(provider: str = Query(..., description="Provider name, e.g., truckerpath")):
    try:
        instance = get_provider(provider)()
        return await instance.ping()
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ImportError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.post("/{provider}/company")
async def create_company(provider: str, payload: dict):
    try:
        instance = get_provider(provider)()
        return await instance.create_company(payload)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ImportError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.post("/{provider}/loads")
async def post_load(provider: str, payload: dict):
    try:
        instance = get_provider(provider)()
        return await instance.post_load(payload)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ImportError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.post("/{provider}/webhook")
async def register_webhook(provider: str, payload: dict):
    try:
        instance = get_provider(provider)()
        return await instance.register_webhook(payload)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ImportError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.post("/{provider}/webhook/add")
async def register_webhook_add(provider: str, payload: dict):
    try:
        instance = get_provider(provider)()
        return await instance.register_webhook_add(payload)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ImportError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.post("/{provider}/tracking")
async def tracking_create(provider: str, payload: dict):
    try:
        instance = get_provider(provider)()
        return await instance.tracking_create(payload)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ImportError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.post("/{provider}/tracking/points")
async def push_tracking_points(provider: str, payload: dict):
    try:
        instance = get_provider(provider)()
        return await instance.push_tracking_points(payload)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ImportError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
