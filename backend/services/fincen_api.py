# backend/services/fincen_api.py
from __future__ import annotations

from typing import Optional, Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession


class FincenService:
    """
    Placeholder service for FinCEN / AML reporting.

    In this version of GTS Logistics, the real integration with
    external FinCEN APIs is **disabled**. This service keeps a
    clean interface so that any calling code does not break.
    """

    def __init__(self) -> None:
        # In the future, you can add API keys, base URLs, etc. here.
        self.enabled: bool = False

    async def submit_transaction_report(
        self,
        transaction_id: int,
        db: Optional[AsyncSession] = None,
    ) -> Dict[str, Any]:
        """
        Fake implementation used for now.

        Parameters
        ----------
        transaction_id: int
            Internal ID of a financial transaction (not used yet).
        db: Optional[AsyncSession]
            Optional database session, kept for future real implementation.

        Returns
        -------
        dict
            Simple status payload indicating that FinCEN is disabled.
        """
        # We don't do any real work here – just return a clear status.
        return {
            "status": "disabled",
            "detail": "FinCEN API integration is currently disabled in this environment.",
            "transaction_id": transaction_id,
        }


# Singleton instance that other modules can import
fincen_service = FincenService()

__all__ = ["FincenService", "fincen_service"]
