from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from backend.database.config import get_db_async  # type: ignore[import]
from backend.models.financial import FinancialTransaction, TransactionType  # type: ignore[import]
from backend.models.models import Shipment  # type: ignore[import]
from backend.models.carrier import Carrier  # type: ignore[import]
from backend.models.ai_reports import AIReport  # type: ignore[import]
from backend.utils.email_utils import send_bot_email  # type: ignore[import]

router = APIRouter()


@router.get("/ai/general/overview")
async def get_ai_overview(
    db: AsyncSession = Depends(get_db_async),
):
    # Finance: income and expense
    income_result = await db.execute(
        select(FinancialTransaction.amount).where(
            FinancialTransaction.type == TransactionType.INCOME  # type: ignore[attr-defined]
        )
    )
    income_values = list(income_result.scalars().all())
    income = float(sum(income_values)) if income_values else 0.0

    expense_result = await db.execute(
        select(FinancialTransaction.amount).where(
            FinancialTransaction.type == TransactionType.EXPENSE  # type: ignore[attr-defined]
        )
    )
    expense_values = list(expense_result.scalars().all())
    expense = float(sum(expense_values)) if expense_values else 0.0

    # Shipments
    shipment_result = await db.execute(select(Shipment))
    shipments = shipment_result.scalars().all()
    total_shipments = len(shipments)
    delayed_shipments = len(
        [s for s in shipments if getattr(s, "status", None) != "completed"]
    )

    # Carriers
    carrier_result = await db.execute(select(Carrier))
    carriers = carrier_result.scalars().all()
    top_carriers = [c.name for c in carriers[:3]]

    # Simple recommendation logic
    recommendation = "All systems are stable."
    if income - expense < 1000:
        recommendation = "Review your expenses, profit margin is low."
    if delayed_shipments > 5:
        recommendation += " Investigate delayed shipments."

    return {
        "finance": {
            "income": income,
            "expense": expense,
            "net": income - expense,
        },
        "operations": {
            "shipments": total_shipments,
            "delayed": delayed_shipments,
        },
        "carriers": top_carriers,
        "recommendation": recommendation,
    }


@router.get("/ai/general/reports/weekly")
async def get_weekly_reports(
    db: AsyncSession = Depends(get_db_async),
):
    start_of_week = datetime.utcnow() - timedelta(days=7)
    result = await db.execute(
        select(AIReport).where(
            AIReport.created_at >= start_of_week  # type: ignore[attr-defined]
        )
    )
    reports = result.scalars().all()

    return [
        {
            "bot": r.bot_name,
            "type": r.report_type,
            "summary": r.summary,
            "status": r.status,
            "created_at": r.created_at.strftime("%Y-%m-%d"),
        }
        for r in reports
    ]


@router.post("/ai/general/reports/email")
async def send_weekly_summary_email(
    db: AsyncSession = Depends(get_db_async),
):
    # Reuse the weekly reports function as an internal call
    reports = await get_weekly_reports(db=db)

    summary_lines = ["AI Weekly Summary:", ""]
    for r in reports:
        summary_lines.append(f"[{r['bot']}] - {r['summary']} ({r['type']})")

    summary = "\n".join(summary_lines)

    # send_email is synchronous
    send_bot_email(
        bot_name="general_manager",
        subject="GTS AI Weekly Summary",
        body=summary,
        to=["operations@gabanilogistics.com"],
    )

    return {"status": "Email sent"}

