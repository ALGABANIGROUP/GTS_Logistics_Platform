# -*- coding: utf-8 -*-
"""Deprecated Sudapay webhook endpoint."""

from __future__ import annotations

import logging
from typing import Dict

from fastapi import APIRouter, HTTPException, status

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/webhooks",
    tags=["webhooks"],
    responses={404: {"description": "Not found"}},
)


@router.post("/sudapay/payment", status_code=status.HTTP_410_GONE)
async def sudapay_payment_webhook() -> Dict[str, str]:
    """Reject legacy Sudapay webhook calls after gateway removal."""
    logger.warning("Rejected deprecated Sudapay webhook call")
    raise HTTPException(
        status_code=status.HTTP_410_GONE,
        detail="Sudapay webhook has been removed from GTS",
    )
