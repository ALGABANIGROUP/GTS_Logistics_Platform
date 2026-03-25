"""
FinCEN API Service - Financial Crimes Enforcement Network reporting
"""

import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import httpx

logger = logging.getLogger(__name__)


class FincenService:
    """Financial Crimes Enforcement Network reporting service"""

    def __init__(self) -> None:
        # Enable service by default, check API key
        self.api_key = os.getenv("FINCEN_API_KEY", "")
        self.base_url = os.getenv("FINCEN_API_URL", "https://api.fincen.gov/v1")
        self.enabled = bool(self.api_key)  # ✅ Enable if API key exists
        self.sandbox_mode = os.getenv("FINCEN_SANDBOX_MODE", "true").lower() in ("1", "true", "yes")

        if not self.api_key:
            logger.warning("FinCEN API key not configured. Service will run in mock mode.")
            self.enabled = False

    async def submit_transaction_report(
        self,
        transaction_data: Dict[str, Any],
        report_type: str = "ctr"
    ) -> Dict[str, Any]:
        """Submit a transaction report to FinCEN"""
        
        if not self.enabled:
            # Return mock response for development
            return {
                "status": "mock",
                "detail": "FinCEN API is running in mock mode. Set FINCEN_API_KEY to enable real reporting.",
                "report_id": f"MOCK-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "submitted_at": datetime.now().isoformat(),
                "report_type": report_type
            }

        try:
            async with httpx.AsyncClient() as client:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                
                url = f"{self.base_url}/reports/{report_type}"
                
                response = await client.post(
                    url,
                    json=transaction_data,
                    headers=headers,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"FinCEN report submitted: {data.get('report_id')}")
                    return {
                        "status": "success",
                        "report_id": data.get("report_id"),
                        "submitted_at": datetime.now().isoformat(),
                        "acknowledgment": data
                    }
                else:
                    logger.error(f"FinCEN API error: {response.status_code} - {response.text}")
                    return {
                        "status": "error",
                        "error_code": response.status_code,
                        "detail": response.text,
                        "submitted_at": datetime.now().isoformat()
                    }
                    
        except Exception as e:
            logger.error(f"FinCEN submission failed: {e}")
            return {
                "status": "error",
                "detail": str(e),
                "submitted_at": datetime.now().isoformat()
            }

    async def get_report_status(self, report_id: str) -> Dict[str, Any]:
        """Get status of a submitted report"""
        
        if not self.enabled:
            return {
                "status": "mock",
                "report_id": report_id,
                "processing_status": "completed",
                "detail": "Mock response - API not enabled"
            }

        try:
            async with httpx.AsyncClient() as client:
                headers = {
                    "Authorization": f"Bearer {self.api_key}"
                }
                
                url = f"{self.base_url}/reports/{report_id}"
                response = await client.get(url, headers=headers, timeout=30.0)
                
                if response.status_code == 200:
                    return {
                        "status": "success",
                        "report_id": report_id,
                        "report_data": response.json()
                    }
                else:
                    return {
                        "status": "error",
                        "report_id": report_id,
                        "error_code": response.status_code,
                        "detail": response.text
                    }
                    
        except Exception as e:
            logger.error(f"Failed to get report status: {e}")
            return {
                "status": "error",
                "report_id": report_id,
                "detail": str(e)
            }

    async def validate_transaction(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate transaction data before submission"""
        errors = []
        warnings = []

        # Basic validation
        if not transaction_data.get("amount"):
            errors.append("Transaction amount is required")

        if not transaction_data.get("currency"):
            errors.append("Currency is required")

        amount = transaction_data.get("amount", 0)
        if amount > 10000 and not self._has_currency_threshold_checks(transaction_data):
            warnings.append("Transaction exceeds $10,000 - requires CTR filing")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "requires_reporting": amount > 10000 or transaction_data.get("suspicious", False)
        }

    def _has_currency_threshold_checks(self, transaction_data: Dict[str, Any]) -> bool:
        """Check if transaction has required threshold reporting"""
        return bool(transaction_data.get("ctr_filed") or transaction_data.get("exemption_applies"))


# Singleton instance
_fincen_service = None


def get_fincen_service() -> FincenService:
    """Get or create FinCEN service instance"""
    global _fincen_service
    if _fincen_service is None:
        _fincen_service = FincenService()
    return _fincen_service
