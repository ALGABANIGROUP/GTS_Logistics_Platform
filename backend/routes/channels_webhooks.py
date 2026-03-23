from __future__ import annotations

import logging
from typing import Any, Dict

from fastapi import APIRouter, HTTPException, Request

from backend.services.push_service import push_service
from backend.services.sms_service import sms_service
from backend.services.whatsapp_service import whatsapp_service

router = APIRouter(prefix="/api/v1/webhooks/channels", tags=["Channels Webhooks"])
logger = logging.getLogger(__name__)


@router.post("/whatsapp")
async def whatsapp_webhook(request: Request) -> Dict[str, Any]:
    form_data = await request.form()
    payload = dict(form_data)
    logger.info("WhatsApp webhook received from %s", payload.get("From"))
    return {"status": "processed", "result": await whatsapp_service.handle_incoming(payload)}


@router.post("/sms")
async def sms_webhook(request: Request) -> Dict[str, Any]:
    form_data = await request.form()
    payload = dict(form_data)
    logger.info("SMS webhook received from %s", payload.get("From"))
    return {"status": "processed", "result": await sms_service.handle_incoming(payload)}


@router.post("/push/register")
async def register_push_device(request: Request) -> Dict[str, Any]:
    data = await request.json()
    user_id = data.get("user_id")
    device_token = data.get("device_token")
    device_type = data.get("device_type", "android")
    if not user_id or not device_token:
        raise HTTPException(status_code=400, detail="Missing user_id or device_token")
    result = await push_service.register_device(int(user_id), str(device_token), str(device_type))
    return {"success": result, "message": "Device registered"}


@router.post("/push/unregister")
async def unregister_push_device(request: Request) -> Dict[str, Any]:
    data = await request.json()
    user_id = data.get("user_id")
    device_token = data.get("device_token")
    if not user_id or not device_token:
        raise HTTPException(status_code=400, detail="Missing user_id or device_token")
    result = await push_service.unregister_device(int(user_id), str(device_token))
    return {"success": result, "message": "Device unregistered"}
