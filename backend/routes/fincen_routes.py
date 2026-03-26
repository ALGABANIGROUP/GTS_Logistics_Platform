from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException

from backend.security.auth import get_current_user
from backend.services.fincen_api import FincenService, get_fincen_service

router = APIRouter(prefix="/api/v1/fincen", tags=["FinCEN"])


def _raise_if_service_unavailable(result: Dict[str, Any]) -> None:
    if result.get("error_code") == 503:
        raise HTTPException(status_code=503, detail=result.get("detail"))


@router.post("/reports/{report_type}")
async def submit_report(
    report_type: str,
    payload: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user),
    service: FincenService = Depends(get_fincen_service),
) -> Dict[str, Any]:
    del current_user
    result = await service.submit_transaction_report(payload, report_type=report_type)
    _raise_if_service_unavailable(result)
    return result


@router.get("/reports/{report_id}")
async def get_report_status(
    report_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    service: FincenService = Depends(get_fincen_service),
) -> Dict[str, Any]:
    del current_user
    result = await service.get_report_status(report_id)
    _raise_if_service_unavailable(result)
    return result
