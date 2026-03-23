from __future__ import annotations

import asyncio
import csv
import hashlib
import json
import logging
from collections.abc import AsyncGenerator
from datetime import datetime
from io import StringIO
from typing import List, Optional, Dict, Protocol, runtime_checkable, cast, Union, Any, Callable

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel, Field
from sqlalchemy import select, func, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from backend.models.financial import Expense, ExpenseStatus  # type: ignore[import]

log = logging.getLogger(__name__)
router = APIRouter(prefix="/finance", tags=["Finance"])

_import_lock = asyncio.Lock()

# ---- unified DB session dependency (project-wide) ----
try:
    from backend.database.connection import get_db as _get_db  # type: ignore
except Exception:  # pragma: no cover
    _get_db = None  # type: ignore

try:
    from backend.database.session import get_async_session  # type: ignore
except Exception:  # pragma: no cover
    from backend.database.session import get_async_session  # type: ignore


async def get_finance_db(db: AsyncSession = Depends(get_async_session)) -> AsyncGenerator[AsyncSession, None]:
    if _get_db is not None:
        async for session in _get_db():  # type: ignore[misc]
            yield session
        return
    yield db


def _local_dedupe_key(
    *,
    category: str,
    amount: float,
    description: Optional[str],
    vendor: Optional[str],
    created_at_iso: str,
) -> str:
    payload = {
        "category": category or "",
        "amount": round(float(amount), 4),
        "description": (description or ""),
        "vendor": (vendor or ""),
        "created_at": created_at_iso,
    }
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _make_dedupe_key(
    category: str,
    amount: float,
    description: Optional[str],
    vendor: Optional[str],
    created_at_iso: str,
) -> str:
    maker = getattr(Expense, "make_dedupe_key", None)
    if callable(maker):
        try:
            return maker(  # type: ignore[misc]
                category=category,
                amount=amount,
                description=description,
                vendor=vendor,
                created_at_iso=created_at_iso,
            )
        except Exception as e:
            log.warning("Expense.make_dedupe_key raised %s; falling back to local hasher.", e)
    return _local_dedupe_key(
        category=category,
        amount=amount,
        description=description,
        vendor=vendor,
        created_at_iso=created_at_iso,
    )


def _status_name(val: Union[str, ExpenseStatus, None]) -> str:
    if isinstance(val, ExpenseStatus):
        name = getattr(val, "name", None) or getattr(val, "value", None)
        if isinstance(name, str) and name:
            return name.upper()
    if isinstance(val, str) and val.strip():
        s = val.strip().upper()
        return s if s in ("PENDING", "PAID") else "PENDING"
    return "PENDING"


def _to_out(obj: Expense) -> "ExpenseOut":
    """
    Convert ORM -> Pydantic response model.
    Supports Pydantic v2 (model_validate) with fallback to v1 (from_orm).
    """
    mv = getattr(ExpenseOut, "model_validate", None)
    if callable(mv):
        return mv(obj)  # type: ignore[misc]
    fo = getattr(ExpenseOut, "from_orm", None)
    if callable(fo):
        return fo(obj)  # type: ignore[misc]
    # Last resort (should not happen)
    return ExpenseOut(
        id=int(getattr(obj, "id")),
        category=str(getattr(obj, "category")),
        amount=float(getattr(obj, "amount")),
        description=getattr(obj, "description"),
        vendor=getattr(obj, "vendor"),
        created_at=getattr(obj, "created_at"),
        status=str(getattr(obj, "status")),
    )


# Import unified expense schemas
from backend.schemas.expense_schemas import ExpenseCreate, ExpenseOut


@runtime_checkable
class ExpenseMutable(Protocol):
    id: int
    category: str
    amount: float
    description: Optional[str]
    vendor: Optional[str]
    status: Union[str, ExpenseStatus]
    created_at: datetime
    updated_at: datetime
    dedupe_key: str


@router.get("/health")
async def finance_health(db: AsyncSession = Depends(get_finance_db)) -> Dict[str, Any]:
    try:
        row = (await db.execute(text("SELECT 1"))).first()
        return {"ok": True, "db_ok": bool(row and row[0] == 1)}
    except Exception as e:
        log.exception("Finance health failed")
        raise HTTPException(status_code=500, detail=f"finance_health_error: {e!s}")


@router.get("/expenses", response_model=List[ExpenseOut])
async def get_expenses(db: AsyncSession = Depends(get_finance_db)) -> List[ExpenseOut]:
    try:
        result = await db.execute(select(Expense).order_by(Expense.created_at.desc()))
        items = list(result.scalars().all())
        return [_to_out(x) for x in items]
    except Exception as e:
        log.exception("get_expenses failed")
        raise HTTPException(status_code=500, detail=f"get_expenses_error: {e!s}")


@router.post("/expenses", response_model=ExpenseOut)
async def create_expense(expense: ExpenseCreate, db: AsyncSession = Depends(get_finance_db)) -> ExpenseOut:
    try:
        created_at = expense.created_at or datetime.utcnow()
        status_label = _status_name(expense.status)
        dkey = _make_dedupe_key(
            category=expense.category,
            amount=expense.amount,
            description=expense.description,
            vendor=expense.vendor,
            created_at_iso=created_at.isoformat(),
        )

        obj = Expense(
            category=expense.category,
            amount=expense.amount,
            description=expense.description or None,
            vendor=expense.vendor or None,
            status=status_label,
            created_at=created_at,
            updated_at=datetime.utcnow(),
            dedupe_key=dkey,
        )
        db.add(obj)

        try:
            await db.commit()
        except IntegrityError:
            await db.rollback()
            existing = await db.execute(select(Expense).where(Expense.dedupe_key == dkey))
            found = existing.scalar_one_or_none()
            if found:
                return _to_out(found)
            raise HTTPException(status_code=409, detail="Duplicate expense")

        await db.refresh(obj)
        return _to_out(obj)

    except HTTPException:
        raise
    except Exception as e:
        log.exception("create_expense failed")
        raise HTTPException(status_code=500, detail=f"create_expense_error: {e!s}")


@router.put("/expenses/{expense_id}/status", response_model=ExpenseOut)
async def toggle_expense_status(expense_id: int, db: AsyncSession = Depends(get_finance_db)) -> ExpenseOut:
    try:
        result = await db.execute(select(Expense).where(Expense.id == expense_id))
        obj = result.scalar_one_or_none()
        if not obj:
            raise HTTPException(status_code=404, detail="Expense not found")

        exp = cast(ExpenseMutable, obj)
        current = _status_name(exp.status if isinstance(exp.status, str) else getattr(exp, "status", None))
        next_status = "PAID" if current == "PENDING" else "PENDING"

        exp.status = next_status
        exp.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(obj)
        return _to_out(obj)

    except HTTPException:
        raise
    except Exception as e:
        log.exception("toggle_expense_status failed")
        raise HTTPException(status_code=500, detail=f"toggle_expense_status_error: {e!s}")


@router.put("/expenses/{expense_id}", response_model=ExpenseOut)
async def update_expense(expense_id: int, expense: ExpenseCreate, db: AsyncSession = Depends(get_finance_db)) -> ExpenseOut:
    try:
        result = await db.execute(select(Expense).where(Expense.id == expense_id))
        obj = result.scalar_one_or_none()
        if not obj:
            raise HTTPException(status_code=404, detail="Expense not found")

        exp = cast(ExpenseMutable, obj)
        created_at = expense.created_at or exp.created_at or datetime.utcnow()

        exp.category = expense.category
        exp.amount = expense.amount
        exp.description = expense.description or None
        exp.vendor = expense.vendor or None
        exp.status = _status_name(expense.status or exp.status)
        exp.created_at = created_at
        exp.updated_at = datetime.utcnow()
        exp.dedupe_key = _make_dedupe_key(
            category=exp.category,
            amount=exp.amount,
            description=exp.description,
            vendor=exp.vendor,
            created_at_iso=created_at.isoformat(),
        )

        await db.commit()
        await db.refresh(obj)
        return _to_out(obj)

    except HTTPException:
        raise
    except Exception as e:
        log.exception("update_expense failed")
        raise HTTPException(status_code=500, detail=f"update_expense_error: {e!s}")


@router.delete("/expenses/{expense_id}", status_code=204)
async def delete_expense(expense_id: int, db: AsyncSession = Depends(get_finance_db)) -> None:
    try:
        result = await db.execute(select(Expense).where(Expense.id == expense_id))
        obj = result.scalar_one_or_none()
        if not obj:
            raise HTTPException(status_code=404, detail="Expense not found")

        await db.delete(obj)
        await db.commit()
        return None

    except HTTPException:
        raise
    except Exception as e:
        log.exception("delete_expense failed")
        raise HTTPException(status_code=500, detail=f"delete_expense_error: {e!s}")


@router.get("/summary")
async def finance_summary(db: AsyncSession = Depends(get_finance_db)) -> Dict[str, Any]:
    try:
        total_q = await db.execute(select(func.coalesce(func.sum(Expense.amount), 0.0)))
        total_expenses = float(total_q.scalar() or 0.0)

        by_status_q = await db.execute(
            select(Expense.status, func.coalesce(func.sum(Expense.amount), 0.0)).group_by(Expense.status)
        )
        by_status: Dict[str, float] = {str(s): float(a) for (s, a) in by_status_q.all()}

        by_vendor_q = await db.execute(
            select(Expense.vendor, func.coalesce(func.sum(Expense.amount), 0.0)).group_by(Expense.vendor)
        )
        by_vendor: Dict[str, float] = {str(v or "Unknown"): float(a) for (v, a) in by_vendor_q.all()}

        total_revenue = 120000.0
        net_profit = total_revenue - total_expenses

        return {
            "ok": True,
            "total_expenses": round(total_expenses, 2),
            "total_revenue": round(total_revenue, 2),
            "net_profit": round(net_profit, 2),
            "by_status": by_status,
            "by_vendor": by_vendor,
        }
    except Exception as e:
        log.exception("finance_summary failed")
        raise HTTPException(status_code=500, detail=f"finance_summary_error: {e!s}")


@router.post("/upload-csv")
async def upload_csv(file: UploadFile = File(...), db: AsyncSession = Depends(get_finance_db)) -> Dict[str, Any]:
    async with _import_lock:
        contents = await file.read()
        csv_text = contents.decode("utf-8-sig")
        reader = csv.DictReader(StringIO(csv_text))

        inserted, duplicates, skipped = 0, 0, 0

        for row in reader:
            try:
                category = (row.get("category") or "").strip()
                amount = float(row.get("amount_usd") or row.get("amount") or 0)
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
                status_label = _status_name(status_raw)

                dkey = _make_dedupe_key(
                    category=category,
                    amount=amount,
                    description=description,
                    vendor=vendor,
                    created_at_iso=created_at.isoformat(),
                )

                obj = Expense(
                    category=category or "Uncategorized",
                    amount=amount,
                    description=description or None,
                    vendor=vendor or None,
                    status=status_label,
                    created_at=created_at,
                    updated_at=datetime.utcnow(),
                    dedupe_key=dkey,
                )
                db.add(obj)
                try:
                    await db.commit()
                    inserted += 1
                except IntegrityError:
                    await db.rollback()
                    duplicates += 1
            except Exception as e:
                log.warning("CSV row error: %s => %s", row, e)
                skipped += 1

        return {"ok": True, "message": "Upload complete", "inserted": inserted, "duplicates": duplicates, "skipped": skipped}


finance_router = router
__all__ = ["router", "finance_router"]
print("[finance_routes] loaded and aliases exported")

