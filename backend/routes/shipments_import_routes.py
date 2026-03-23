# backend/routes/shipments_import_routes.py
from __future__ import annotations

import csv
import io
import os
from typing import Any, Dict, List, Optional

import httpx
from fastapi import APIRouter, File, HTTPException, UploadFile

from pydantic import BaseModel, Field

router = APIRouter(
    prefix="/shipments",
    tags=["Shipments Import"],
)


class ImportErrorItem(BaseModel):
    row_index: int = Field(..., description="Zero-based row index in the CSV (excluding header).")
    error: str = Field(..., description="Error message for this row.")
    payload: Dict[str, Any] = Field(default_factory=dict)


class ImportResult(BaseModel):
    ok: bool
    total_rows: int
    created: int
    failed: int
    errors: List[ImportErrorItem] = Field(default_factory=list)


def _normalize_key(key: str) -> str:
    return key.strip().lower().replace(" ", "_")


def _build_shipment_payload(row: Dict[str, Any], default_user_id: int = 1) -> Dict[str, Any]:
    normalized = {_normalize_key(k): (v.strip() if isinstance(v, str) else v) for k, v in row.items()}

    def pick(*candidates: str, default: Optional[str] = None) -> Optional[str]:
        for c in candidates:
            val = normalized.get(c)
            if val not in (None, ""):
                return str(val).strip()
        return default

    def pick_float(*candidates: str) -> Optional[float]:
        raw = pick(*candidates)
        if raw is None:
            return None
        try:
            return float(str(raw).replace(",", "").strip())
        except Exception:
            return None

    pickup = pick("pickup_location", "pickup_city", "origin", "from", default="Unknown Pickup")
    dropoff = pick("dropoff_location", "dropoff_city", "destination", "to", default="Unknown Dropoff")
    trailer_type = pick("trailer_type", "equipment", "equipment_type", "trailer")
    rate = pick_float("rate", "price", "amount", "linehaul_rate")
    weight = pick("weight", "wt")
    length = pick("length", "len")
    load_size = pick("load_size", "size")
    description = pick("description", "notes", "comment")
    status = pick("status") or "Imported"

    lat = pick("latitude", "pickup_latitude", "origin_lat")
    lng = pick("longitude", "pickup_longitude", "origin_lng")
    try:
        lat_f = float(lat) if lat not in (None, "") else None
    except Exception:
        lat_f = None
    try:
        lng_f = float(lng) if lng not in (None, "") else None
    except Exception:
        lng_f = None

    user_id_raw = pick("user_id")
    try:
        user_id = int(user_id_raw) if user_id_raw not in (None, "") else default_user_id
    except Exception:
        user_id = default_user_id

    payload: Dict[str, Any] = {
        "user_id": user_id,
        "pickup_location": pickup,
        "dropoff_location": dropoff,
        "trailer_type": trailer_type or None,
        "rate": rate,
        "weight": weight or None,
        "length": length or None,
        "load_size": load_size or None,
        "description": description or None,
        "status": status,
        "latitude": lat_f,
        "longitude": lng_f,
        "recurring_type": None,
        "days": None,
    }

    return payload


async def _post_shipment(payload: Dict[str, Any]) -> Optional[int]:
    base_url = os.getenv("INTERNAL_BASE_URL", "http://localhost:8000").rstrip("/")
    urls = [
        f"{base_url}/api/v1/shipments/shipments/",
        f"{base_url}/shipments/",
    ]

    async with httpx.AsyncClient(timeout=30) as client:
        last_error: Optional[str] = None
        for url in urls:
            try:
                resp = await client.post(url, json=payload)
                if resp.status_code // 100 == 2:
                    data = resp.json()
                    sid = (
                        data.get("id")
                        or data.get("shipment_id")
                        or data.get("data", {}).get("id")
                    )
                    if sid is not None:
                        try:
                            return int(sid)
                        except Exception:
                            return None
                    return None
                else:
                    last_error = f"{url} -> {resp.status_code}"
            except Exception as e:
                last_error = f"{url} -> {e}"
        if last_error:
            raise HTTPException(status_code=502, detail=f"Failed to create shipment: {last_error}")
    return None


@router.post("/import-csv", response_model=ImportResult)
async def import_shipments_from_csv(
    file: UploadFile = File(...),
    default_user_id: int = 1,
    dry_run: bool = False,
) -> ImportResult:
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported.")

    raw_bytes = await file.read()
    if not raw_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    try:
        decoded = raw_bytes.decode("utf-8-sig")
    except UnicodeDecodeError:
        decoded = raw_bytes.decode("latin-1")

    reader = csv.DictReader(io.StringIO(decoded))
    rows = list(reader)

    if not rows:
        raise HTTPException(status_code=400, detail="CSV has no data rows.")

    total_rows = len(rows)
    created = 0
    failed = 0
    errors: List[ImportErrorItem] = []

    for index, row in enumerate(rows):
        try:
            payload = _build_shipment_payload(row, default_user_id=default_user_id)
            if dry_run:
                continue
            sid = await _post_shipment(payload)
            if sid is None:
                failed += 1
                errors.append(
                    ImportErrorItem(
                        row_index=index,
                        error="Shipment creation returned no ID.",
                        payload=payload,
                    )
                )
            else:
                created += 1
        except HTTPException as http_exc:
            failed += 1
            errors.append(
                ImportErrorItem(
                    row_index=index,
                    error=f"HTTP error: {http_exc.detail}",
                    payload=row,
                )
            )
        except Exception as e:
            failed += 1
            errors.append(
                ImportErrorItem(
                    row_index=index,
                    error=f"Unexpected error: {e}",
                    payload=row,
                )
            )

    ok = failed == 0

    return ImportResult(
        ok=ok,
        total_rows=total_rows,
        created=created,
        failed=failed,
        errors=errors,
    )
