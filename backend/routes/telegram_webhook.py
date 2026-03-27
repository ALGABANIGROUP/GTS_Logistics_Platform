"""
Telegram Webhook Router for GTS Logistics Platform

Handles incoming Telegram bot updates via webhook endpoint.
This allows the bot to receive messages without polling.
"""

import logging
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

# Import from parent directory
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

try:
    from telegram_bot import process_update, TELEGRAM_AVAILABLE
except Exception as e:
    process_update = None  # type: ignore[assignment]
    TELEGRAM_AVAILABLE = False
    logging.warning("Telegram webhook disabled: %s", e)

log = logging.getLogger("gts.telegram_webhook")

router = APIRouter(prefix="/api/v1/telegram", tags=["Telegram Webhook"])


class TelegramUpdate(BaseModel):
    """Telegram update model for webhook payload."""
    update_id: int
    message: Dict[str, Any] = None
    callback_query: Dict[str, Any] = None
    inline_query: Dict[str, Any] = None
    # Add other update types as needed


@router.post("/webhook")
async def telegram_webhook(request: Request):
    """
    Handle incoming Telegram webhook updates.

    This endpoint receives updates from Telegram when configured as a webhook.
    The bot processes commands and messages here.
    """
    if not TELEGRAM_AVAILABLE or process_update is None:
        raise HTTPException(status_code=503, detail="Telegram webhook unavailable: python-telegram-bot not installed")

    try:
        # Get raw JSON data
        update_data = await request.json()

        log.info(f"[webhook] Received update: {update_data.get('update_id', 'unknown')}")

        # Process the update using our bot handler
        await process_update(update_data)

        # Return 200 OK to acknowledge receipt
        return {"ok": True, "status": "processed"}

    except Exception as e:
        log.error(f"[webhook] Error processing update: {e}")
        # Still return 200 to prevent Telegram from retrying with the same update
        return {"ok": False, "error": str(e)}


@router.get("/health")
async def telegram_webhook_health():
    """Health check endpoint for Telegram webhook."""
    return {
        "status": "healthy" if TELEGRAM_AVAILABLE else "disabled",
        "service": "telegram_webhook",
        "message": "Telegram webhook endpoint is active" if TELEGRAM_AVAILABLE else "Telegram webhook disabled: python-telegram-bot not installed"
    }


@router.post("/test")
async def test_webhook(update: TelegramUpdate):
    """
    Test endpoint for webhook functionality.

    Accepts a TelegramUpdate model for testing purposes.
    """
    if not TELEGRAM_AVAILABLE or process_update is None:
        raise HTTPException(status_code=503, detail="Telegram webhook unavailable: python-telegram-bot not installed")

    try:
        log.info(f"[test] Processing test update: {update.update_id}")

        # Convert Pydantic model to dict for processing
        update_data = update.model_dump()

        # Process the update
        await process_update(update_data)

        return {"ok": True, "message": "Test update processed successfully"}

    except Exception as e:
        log.error(f"[test] Error processing test update: {e}")
        raise HTTPException(status_code=500, detail=f"Test failed: {str(e)}")
