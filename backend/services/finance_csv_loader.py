# backend/services/finance_csv_loader.py
from __future__ import annotations

import csv
import hashlib
import json
import logging
from datetime import datetime
from io import StringIO
from typing import Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from backend.database.connection import get_async_engine_from_env
from backend.models.financial import Expense

log = logging.getLogger(__name__)

# Use the same unified async engine as finance_routes
_engine = get_async_engine_from_env()
_SessionLocal = async_sessionmaker(bind=_engine, expire_on_commit=False)


def _make_dedupe_key(
    *,
    category: str,
    amount: float,
    description: str,
    vendor: str,
    created_at_iso: str,
) -> str:
    """Create a deterministic hash to avoid inserting duplicate rows."""
    payload = {
        "category": category or "",
        "amount": round(float(amount), 4),
        "description": description or "",
        "vendor": vendor or "",
        "created_at": created_at_iso,
    }
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


async def import_expenses_from_csv_text(csv_text: str) -> Dict[str, Any]:
    """
    Load expenses from a CSV text payload.

    Expected columns (flexible):
      - category
      - amount or amount_usd
      - description (optional)
      - vendor (optional)
      - date or created_at (optional, many formats supported)
      - status (optional: PENDING / PAID)

    Returns:
      {
        "inserted": int,
        "duplicates": int,
        "skipped": int,
      }
    """
    inserted = 0
    duplicates = 0
    skipped = 0

    reader = csv.DictReader(StringIO(csv_text))

    async with _SessionLocal() as db:  # db is AsyncSession
        for row in reader:
            try:
                category = (row.get("category") or "").strip() or "Uncategorized"
                amount_raw = row.get("amount_usd") or row.get("amount") or "0"
                amount = float(amount_raw)

                description = (row.get("description") or "").strip()
                vendor = (row.get("vendor") or "").strip()

                date_raw = (row.get("date") or row.get("created_at") or "").strip()
                created_at = None
                for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%m/%d/%Y"):
                    try:
                        created_at = datetime.strptime(date_raw, fmt)
                        break
                    except Exception:
                        continue
                created_at = created_at or datetime.utcnow()

                status_raw = (row.get("status") or "PENDING").strip().upper()
                status_label = status_raw if status_raw in ("PENDING", "PAID") else "PENDING"

                dkey = _make_dedupe_key(
                    category=category,
                    amount=amount,
                    description=description,
                    vendor=vendor,
                    created_at_iso=created_at.isoformat(),
                )

                exp = Expense(
                    category=category,
                    amount=amount,
                    description=description or None,
                    vendor=vendor or None,
                    status=status_label,
                    created_at=created_at,
                    updated_at=datetime.utcnow(),
                    dedupe_key=dkey,
                )
                db.add(exp)

                try:
                    await db.commit()
                    inserted += 1
                except IntegrityError:
                    await db.rollback()
                    # Check if the dedupe_key already exists
                    existing = await db.execute(
                        select(Expense).where(Expense.dedupe_key == dkey)
                    )
                    if existing.scalar_one_or_none():
                        duplicates += 1
                    else:
                        skipped += 1  # some other DB error

            except Exception as e:
                log.warning("CSV row import error: %s => %s", row, e)
                skipped += 1

    return {
        "inserted": inserted,
        "duplicates": duplicates,
        "skipped": skipped,
    }


async def import_expenses_from_file(path: str) -> Dict[str, Any]:
    """
    Convenience wrapper to import from a CSV file path on disk.
    """
    with open(path, "r", encoding="utf-8-sig") as f:
        csv_text = f.read()
    return await import_expenses_from_csv_text(csv_text)

