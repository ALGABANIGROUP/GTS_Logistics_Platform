from __future__ import annotations
import logging
from typing import Any, Dict, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from backend.services.truckerpath_service import TruckerPathService
try:
    from backend.utils.role_protected import RoleChecker
    admin_required = RoleChecker(['admin'])
except Exception:
    admin_required = None
logger = logging.getLogger('truckerpath.routes')
router = APIRouter(prefix='/integrations/truckerpath', tags=['TruckerPath'])

@router.get('/ping')
async def tp_ping():
    try:
        return await TruckerPathService.ping()
    except Exception as e:
        logger.exception('Ping failed: %s', e)
        raise HTTPException(status_code=502, detail='Provider ping failed')

@router.post('/company', dependencies=[Depends(admin_required)] if admin_required else None)
async def tp_create_company(payload: Dict[str, Any]):
    """
    Create/register your company at TruckerPath.
    Request body should match provider spec (company_name/dot/mc/email/company_id...).
    """
    try:
        res = await TruckerPathService.create_company(payload)
        return JSONResponse(res, status_code=200 if res.get('ok', True) else 502)
    except Exception as e:
        logger.exception('Create company failed: %s', e)
        raise HTTPException(status_code=502, detail='Create company failed')

@router.post('/load', dependencies=[Depends(admin_required)] if admin_required else None)
async def tp_post_load(payload: Dict[str, Any]):
    """
    Post a load to TruckerPath.
    Body should include company_id, contact_info, shipment_info...
    """
    try:
        res = await TruckerPathService.post_load(payload)
        return JSONResponse(res, status_code=200 if res.get('ok', True) else 502)
    except Exception as e:
        logger.exception('Post load failed: %s', e)
        raise HTTPException(status_code=502, detail='Post load failed')

@router.get('/loads', dependencies=[Depends(admin_required)] if admin_required else None)
async def tp_list_loads(limit: int=Query(10, ge=1, le=100), company_id: Optional[str]=None, equipment: Optional[str]=None, origin: Optional[str]=None, destination: Optional[str]=None):
    """
    List/search loads via provider helper (shape depends on provider).
    Query params are forwarded when supported.
    """
    try:
        filters: Dict[str, Any] = {}
        if company_id:
            filters['company_id'] = company_id
        if equipment:
            filters['equipment'] = equipment
        if origin:
            filters['origin'] = origin
        if destination:
            filters['destination'] = destination
        res = await TruckerPathService.list_loads(limit=limit, **filters)
        return JSONResponse(res, status_code=200 if res.get('ok', True) else 502)
    except Exception as e:
        logger.exception('List loads failed: %s', e)
        raise HTTPException(status_code=502, detail='List loads failed')

@router.post('/webhook/register', dependencies=[Depends(admin_required)] if admin_required else None)
async def tp_register_webhook(payload: Dict[str, Any]):
    """
    Register webhook using provider's generic 'events' style.
    Body example: { "url": "...", "events": ["tracking.update","load.status"] }
    """
    try:
        res = await TruckerPathService.register_webhook(payload)
        return JSONResponse(res, status_code=200 if res.get('ok', True) else 502)
    except Exception as e:
        logger.exception('Register webhook failed: %s', e)
        raise HTTPException(status_code=502, detail='Register webhook failed')

@router.post('/webhook/add', dependencies=[Depends(admin_required)] if admin_required else None)
async def tp_register_webhook_add(payload: Dict[str, Any]):
    """
    Register webhook via /webhooks/add (payload: { "url": "...", "type": "BOOK"|"BID" }).
    """
    try:
        res = await TruckerPathService.register_webhook_add(payload)
        return JSONResponse(res, status_code=200 if res.get('ok', True) else 502)
    except Exception as e:
        logger.exception('Register webhook(add) failed: %s', e)
        raise HTTPException(status_code=502, detail='Register webhook(add) failed')

@router.post('/tracking/create', dependencies=[Depends(admin_required)] if admin_required else None)
async def tp_tracking_create(payload: Dict[str, Any]):
    """
    Create a tracking order/session at TruckerPath.
    Body example mirrors your tracking.py (carrier info + pickup/dropoff).
    """
    try:
        res = await TruckerPathService.tracking_create(payload)
        return JSONResponse(res, status_code=200 if res.get('ok', True) else 502)
    except Exception as e:
        logger.exception('Tracking create failed: %s', e)
        raise HTTPException(status_code=502, detail='Tracking create failed')

@router.post('/tracking/points', dependencies=[Depends(admin_required)] if admin_required else None)
async def tp_push_tracking_points(payload: Dict[str, Any]):
    """
    Push tracking points/locations array.
    Body example: { "company_id": "...", "device_id": "...", "points": [{lat,lng,ts,...}, ...] }
    """
    try:
        res = await TruckerPathService.push_tracking_points(payload)
        return JSONResponse(res, status_code=200 if res.get('ok', True) else 502)
    except Exception as e:
        logger.exception('Push tracking points failed: %s', e)
        raise HTTPException(status_code=502, detail='Push tracking points failed')