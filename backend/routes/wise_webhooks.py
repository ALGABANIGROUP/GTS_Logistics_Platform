"""
Wise Webhook Handler - Process transfer events
"""

from fastapi import APIRouter, Request, HTTPException, Depends
import logging
import os
from typing import Dict, Any

from backend.database.session import get_async_session
from backend.security.webhook_signatures import verify_hmac_sha256_signature

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/webhooks/wise", tags=["Wise Webhooks"])

webhook_secret = os.getenv("WISE_WEBHOOK_SECRET", "")


def verify_signature(payload: bytes, signature: str) -> bool:
    """Verify webhook signature"""
    return verify_hmac_sha256_signature(
        secret=webhook_secret,
        payload=payload,
        signature_header=signature,
        app_env=os.getenv("ENVIRONMENT"),
    )


@router.post("/")
async def wise_webhook(
    request: Request,
    session=Depends(get_async_session)
):
    """Handle Wise webhook events"""
    payload = await request.body()
    signature = request.headers.get("x-signature", "")

    if not verify_signature(payload, signature):
        logger.warning("Invalid webhook signature")
        raise HTTPException(status_code=401, detail="Invalid signature")

    try:
        data = await request.json()
    except Exception as e:
        logger.error(f"Invalid JSON payload: {e}")
        raise HTTPException(status_code=400, detail="Invalid payload")

    event_type = data.get("event_type")
    resource = data.get("resource", {})

    logger.info(f"Wise webhook: {event_type}")

    if event_type == "transfers#status-change":
        await handle_transfer_status_change(resource, session)
    elif event_type == "transfers#funded":
        await handle_transfer_funded(resource, session)
    elif event_type == "transfers#paid":
        await handle_transfer_paid(resource, session)
    elif event_type == "balances#deposit":
        await handle_balance_deposit(resource, session)

    return {"status": "success"}


async def handle_transfer_status_change(transfer: Dict[str, Any], session):
    """Handle transfer status change"""
    transfer_id = transfer.get("id")
    status = transfer.get("status")
    logger.info(f"Transfer {transfer_id} status changed to {status}")


async def handle_transfer_funded(transfer: Dict[str, Any], session):
    """Handle transfer funded"""
    transfer_id = transfer.get("id")
    logger.info(f"Transfer {transfer_id} funded")


async def handle_transfer_paid(transfer: Dict[str, Any], session):
    """Handle transfer paid"""
    transfer_id = transfer.get("id")
    logger.info(f"Transfer {transfer_id} paid")


async def handle_balance_deposit(deposit: Dict[str, Any], session):
    """Handle balance deposit"""
    amount = deposit.get("amount", {}).get("value")
    currency = deposit.get("amount", {}).get("currency")
    logger.info(f"Deposit received: {amount} {currency}")
