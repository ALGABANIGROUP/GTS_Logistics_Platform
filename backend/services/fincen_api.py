"""
FinCEN API Service - Financial Crimes Enforcement Network reporting
"""

from __future__ import annotations

import logging
import os
from datetime import datetime
from typing import Any, Dict

import httpx

logger = logging.getLogger(__name__)


class FincenService:
    """Financial Crimes Enforcement Network reporting service."""

    def __init__(self) -> None:
        self.api_key = os.getenv("FINCEN_API_KEY", "")
        self.api_secret = os.getenv("FINCEN_API_SECRET", "")
        self.base_url = os.getenv("FINCEN_API_URL", "https://api.fincen.gov/v1")
        self.enabled = bool(self.api_key and self.api_secret)
        self.sandbox_mode = os.getenv("FINCEN_SANDBOX_MODE", "true").lower() in ("1", "true", "yes")

        if not self.enabled:
            logger.warning("FinCEN API credentials not configured. Service disabled.")

    def _missing_credentials_response(self) -> Dict[str, Any]:
        return {
            "status": "error",
            "error_code": 503,
            "detail": "Service unavailable - missing FinCEN API credentials",
            "submitted_at": datetime.now().isoformat(),
        }

    async def submit_transaction_report(
        self,
        transaction_data: Dict[str, Any],
        report_type: str = "ctr",
    ) -> Dict[str, Any]:
        """Submit a transaction report to FinCEN."""
        if not self.enabled:
            return self._missing_credentials_response()

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/reports/{report_type}",
                    json=transaction_data,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "X-API-Secret": self.api_secret,
                        "Content-Type": "application/json",
                    },
                    timeout=30.0,
                )

            if response.status_code == 200:
                data = response.json()
                logger.info("FinCEN report submitted: %s", data.get("report_id"))
                return {
                    "status": "success",
                    "report_id": data.get("report_id"),
                    "submitted_at": datetime.now().isoformat(),
                    "acknowledgment": data,
                }

            logger.error("FinCEN API error: %s - %s", response.status_code, response.text)
            return {
                "status": "error",
                "error_code": response.status_code,
                "detail": response.text,
                "submitted_at": datetime.now().isoformat(),
            }
        except Exception as exc:
            logger.error("FinCEN submission failed: %s", exc)
            return {
                "status": "error",
                "error_code": 500,
                "detail": str(exc),
                "submitted_at": datetime.now().isoformat(),
            }

    async def get_report_status(self, report_id: str) -> Dict[str, Any]:
        """Get status of a submitted report."""
        if not self.enabled:
            response = self._missing_credentials_response()
            response["report_id"] = report_id
            return response

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/reports/{report_id}",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "X-API-Secret": self.api_secret,
                    },
                    timeout=30.0,
                )

            if response.status_code == 200:
                return {
                    "status": "success",
                    "report_id": report_id,
                    "report_data": response.json(),
                }

            return {
                "status": "error",
                "report_id": report_id,
                "error_code": response.status_code,
                "detail": response.text,
            }
        except Exception as exc:
            logger.error("Failed to get report status: %s", exc)
            return {
                "status": "error",
                "report_id": report_id,
                "error_code": 500,
                "detail": str(exc),
            }

    async def validate_transaction(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate transaction data before submission."""
        errors = []
        warnings = []

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
            "requires_reporting": amount > 10000 or transaction_data.get("suspicious", False),
        }

    def _has_currency_threshold_checks(self, transaction_data: Dict[str, Any]) -> bool:
        """Check if transaction has required threshold reporting."""
        return bool(transaction_data.get("ctr_filed") or transaction_data.get("exemption_applies"))


_fincen_service = None


def get_fincen_service() -> FincenService:
    """Get or create FinCEN service instance."""
    global _fincen_service
    if _fincen_service is None:
        _fincen_service = FincenService()
    return _fincen_service
