from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, BackgroundTasks, HTTPException, Query

from backend.models.transport_laws import LawUpdateRequest, TransportLaw, TransportType
from backend.services.law_manager import TransportLawManager
from backend.services.update_scheduler import LawUpdateScheduler

router = APIRouter(prefix="/api/transport-laws", tags=["Transport Laws"])

law_manager = TransportLawManager()
scheduler = LawUpdateScheduler(law_manager)


@router.get("/", response_model=List[TransportLaw])
async def get_all_laws():
    return list(law_manager.laws.values())


@router.get("/search")
async def search_laws(
    country: Optional[str] = Query(None, description="Country code (e.g., US, SA)"),
    type: Optional[TransportType] = Query(None, description="Transport type"),
    year: Optional[int] = Query(None, description="Year of law"),
    safety: Optional[str] = Query(None, description="Safety standard level"),
    tag: Optional[str] = Query(None, description="Tag to filter by"),
):
    tags = [tag] if tag else None
    return law_manager.search_laws(country, type, year, safety, tags)


@router.get("/{law_id}")
async def get_law_by_id(law_id: str):
    if law_id not in law_manager.laws:
        raise HTTPException(status_code=404, detail="Law not found")
    return law_manager.laws[law_id]


@router.post("/update")
async def update_law(update: LawUpdateRequest, background_tasks: BackgroundTasks):
    updated_law = await law_manager.update_law(update.law_id, update)

    if not updated_law:
        raise HTTPException(status_code=404, detail="Law not found")

    background_tasks.add_task(
        log_law_update, update.law_id, updated_law.id, update.update_reason
    )

    return {
        "message": "Law updated successfully",
        "old_id": update.law_id,
        "new_law": updated_law,
    }


@router.get("/compare/{law_ids}")
async def compare_laws(law_ids: str):
    ids = law_ids.split(",")
    return law_manager.get_law_comparison(ids)


@router.get("/updates/due")
async def get_due_updates():
    return await law_manager.check_for_updates()


@router.get("/schedule/upcoming")
async def get_upcoming_schedule():
    return scheduler.get_update_schedule()


@router.post("/export")
async def export_laws(format: str = "json"):
    if format.lower() == "json":
        filepath = law_manager.export_to_json()
        return {"message": f"Laws exported to {filepath}", "format": "json"}
    raise HTTPException(status_code=400, detail="Unsupported format")


async def log_law_update(old_id: str, new_id: str, reason: str):
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "old_law_id": old_id,
        "new_law_id": new_id,
        "reason": reason,
        "action": "law_update",
    }

    print(f"LOG: Law Update - {log_entry}")
