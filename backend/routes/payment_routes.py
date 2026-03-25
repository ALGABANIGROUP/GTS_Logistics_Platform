"""
Payment Routes - Payment related endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
from backend.auth.dependencies import get_current_user
from backend.services.payment_service import WISE_CAD_ACCOUNT, WISE_USD_ACCOUNT

router = APIRouter(prefix="/api/payments", tags=["Payments"])


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