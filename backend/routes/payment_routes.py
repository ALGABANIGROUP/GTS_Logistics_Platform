"""
Payment Routes - Payment related endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
from backend.auth.dependencies import get_current_user
from backend.services.payment_service import WISE_CAD_ACCOUNT, WISE_USD_ACCOUNT
from backend.services.stripe_service import get_stripe_service

router = APIRouter(prefix="/api/payments", tags=["Payments"])
stripe_service = get_stripe_service()


@router.get("/bank-details")
async def get_bank_details(
    currency: str = "CAD",
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get bank account details for wire transfers"""

    if currency.upper() == "CAD":
        return {
            "success": True,
            "details": {
                "account_holder": WISE_CAD_ACCOUNT["account_holder"],
                "account_number": WISE_CAD_ACCOUNT["account_number"],
                "institution_number": WISE_CAD_ACCOUNT["institution_number"],
                "transit_number": WISE_CAD_ACCOUNT["transit_number"],
                "swift_bic": WISE_CAD_ACCOUNT["swift_bic"],
                "bank_name": WISE_CAD_ACCOUNT["bank_name"],
                "bank_address": WISE_CAD_ACCOUNT["bank_address"],
                "currency": WISE_CAD_ACCOUNT["currency"],
                "instructions": "Please use your invoice number as reference when making the transfer."
            }
        }
    elif currency.upper() == "USD":
        return {
            "success": True,
            "details": {
                "account_holder": WISE_USD_ACCOUNT["account_holder"],
                "routing_number": WISE_USD_ACCOUNT["routing_number"],
                "account_number": WISE_USD_ACCOUNT["account_number"],
                "swift_bic": WISE_USD_ACCOUNT["swift_bic"],
                "bank_name": WISE_USD_ACCOUNT["bank_name"],
                "currency": WISE_USD_ACCOUNT["currency"],
                "instructions": "Please use your invoice number as reference when making the transfer."
            }
        }
    else:
        return {
            "success": False,
            "error": f"Currency {currency} not supported for bank transfers"
        }


@router.get("/stripe/config")
async def get_stripe_config(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get Stripe configuration for frontend"""
    if not stripe_service.is_enabled():
        return {"success": False, "error": "Stripe not configured"}

    return {
        "success": True,
        "publishable_key": stripe_service.get_publishable_key(),
        "enabled": True
    }


@router.post("/stripe/create-intent")
async def create_stripe_payment_intent(
    request: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Create a Stripe payment intent"""
    amount = request.get("amount")
    currency = request.get("currency", "usd")
    invoice_id = request.get("invoice_id")
    description = request.get("description", f"Invoice #{invoice_id} payment")

    if not amount or amount <= 0:
        raise HTTPException(status_code=400, detail="Invalid amount")

    metadata = {"invoice_id": str(invoice_id)} if invoice_id else {}
    metadata["user_id"] = str(current_user["id"])

    result = await stripe_service.create_payment_intent(
        amount=amount,
        currency=currency,
        metadata=metadata,
        description=description
    )

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])

    return result