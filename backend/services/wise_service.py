"""
Wise API Service - International payments and transfers
"""

import os
import logging
import httpx
from typing import Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)


class WiseService:
    """Wise API integration for international payments"""

    def __init__(self):
        self.api_key = os.getenv("WISE_API_KEY", "")
        self.profile_id = os.getenv("WISE_PROFILE_ID", "")
        self.api_url = "https://api.transferwise.com"
        self.enabled = bool(self.api_key)

        if self.enabled:
            logger.info("Wise service initialized")
        else:
            logger.warning("Wise service disabled - no API key")

    async def create_quote(
        self,
        source_currency: str,
        target_currency: str,
        source_amount: Optional[float] = None,
        target_amount: Optional[float] = None
    ) -> Dict[str, Any]:
        """Create a quote for transfer"""
        if not self.enabled:
            return {"success": False, "error": "Wise not configured"}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.api_url}/v3/profiles/{self.profile_id}/quotes",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    json={
                        "sourceCurrency": source_currency,
                        "targetCurrency": target_currency,
                        "sourceAmount": source_amount,
                        "targetAmount": target_amount
                    }
                )

                if response.status_code == 200:
                    data = response.json()
                    return {
                        "success": True,
                        "quote_id": data.get("id"),
                        "rate": data.get("rate"),
                        "expiration": data.get("expirationTime"),
                        "source_amount": source_amount,
                        "target_amount": data.get("targetAmount")
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Wise API error: {response.status_code}",
                        "details": response.text
                    }

        except Exception as e:
            logger.error(f"Wise quote creation failed: {e}")
            return {"success": False, "error": str(e)}

    async def create_transfer(
        self,
        quote_id: str,
        customer_transaction_id: str,
        recipient_id: str
    ) -> Dict[str, Any]:
        """Create a transfer"""
        if not self.enabled:
            return {"success": False, "error": "Wise not configured"}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.api_url}/v3/profiles/{self.profile_id}/transfers",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    json={
                        "quoteId": quote_id,
                        "customerTransactionId": customer_transaction_id,
                        "targetAccountId": recipient_id
                    }
                )

                if response.status_code == 200:
                    data = response.json()
                    return {
                        "success": True,
                        "transfer_id": data.get("id"),
                        "status": data.get("status"),
                        "quote_id": quote_id
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Wise API error: {response.status_code}",
                        "details": response.text
                    }

        except Exception as e:
            logger.error(f"Wise transfer creation failed: {e}")
            return {"success": False, "error": str(e)}

    async def get_transfer_status(self, transfer_id: str) -> Dict[str, Any]:
        """Get transfer status"""
        if not self.enabled:
            return {"success": False, "error": "Wise not configured"}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.api_url}/v3/transfers/{transfer_id}",
                    headers={"Authorization": f"Bearer {self.api_key}"}
                )

                if response.status_code == 200:
                    data = response.json()
                    return {
                        "success": True,
                        "transfer_id": transfer_id,
                        "status": data.get("status"),
                        "details": data
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Wise API error: {response.status_code}"
                    }

        except Exception as e:
            logger.error(f"Wise transfer status failed: {e}")
            return {"success": False, "error": str(e)}

    async def get_balance(self, currency: str = "CAD") -> Dict[str, Any]:
        """Get account balance for a currency"""
        if not self.enabled:
            return {"success": False, "error": "Wise not configured"}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.api_url}/v4/profiles/{self.profile_id}/balances",
                    headers={"Authorization": f"Bearer {self.api_key}"}
                )

                if response.status_code == 200:
                    balances = response.json()
                    for balance in balances:
                        if balance.get("currency") == currency:
                            return {
                                "success": True,
                                "currency": currency,
                                "amount": balance.get("amount", {}).get("value", 0)
                            }
                    return {"success": True, "currency": currency, "amount": 0}
                else:
                    return {"success": False, "error": f"Wise API error: {response.status_code}"}

        except Exception as e:
            logger.error(f"Wise balance check failed: {e}")
            return {"success": False, "error": str(e)}


# Singleton instance
_wise_service = None


def get_wise_service() -> WiseService:
    """Get Wise service instance"""
    global _wise_service
    if _wise_service is None:
        _wise_service = WiseService()
    return _wise_service