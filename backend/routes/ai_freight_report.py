from fastapi import APIRouter, Depends, Response, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime, timedelta
from importlib import import_module
from importlib.util import find_spec
from backend.database.config import get_db_async
from backend.models.models import Shipment, MessageLog

pdf_spec = find_spec("fpdf")
if pdf_spec is None:
    raise RuntimeError("The `fpdf` package is required for /ai/freight report.")

FPDF = import_module("fpdf").FPDF

router = APIRouter(prefix="/ai/freight")


@router.get("/reports/weekly/pdf")
async def generate_weekly_pdf_report(db: AsyncSession = Depends(get_db_async)):
    start = datetime.utcnow() - timedelta(days=7)
    result = await db.execute(
        select(Shipment).where(Shipment.status == "delayed", Shipment.updated_at >= start)
    )
    delayed_shipments = result.scalars().all()

    insights_result = await db.execute(
        select(MessageLog).where(
            MessageLog.sender == "AI Freight Advisor",
            MessageLog.context.like("shipment:%"),
        )
    )
    insights = {
        log.context.split(":", 1)[1]: log.message for log in insights_result.scalars().all()
    }

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Weekly Delayed Shipments Report", ln=1, align="C")
    pdf.ln(5)

    for shipment in delayed_shipments:
        sid = str(shipment.id)
        pdf.set_font("Arial", "B", 11)
        pdf.cell(0, 10, f"Shipment #{sid}", ln=1)
        pdf.set_font("Arial", size=10)
        pdf.multi_cell(
            0,
            8,
            f"From: {shipment.origin} | To: {shipment.destination} | Customer: {shipment.customer_name}",
        )
        gpt = insights.get(sid, "No AI insight available.")
        pdf.set_text_color(0, 0, 128)
        pdf.multi_cell(0, 8, f"AI Insight: {gpt}")
        pdf.set_text_color(0, 0, 0)
        pdf.ln(5)

    pdf_content = pdf.output(dest="S").encode("latin1")
    response = Response(content=pdf_content, media_type="application/pdf")
    response.headers["Content-Disposition"] = "attachment; filename=delayed_shipments_report.pdf"
    return response

