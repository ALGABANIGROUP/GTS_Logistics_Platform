# 📁 backend/routes/freight_dashboard.py

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from backend.database.connection import get_db
from backend.models.models import Shipment  # ✅ Ensure the Shipment model is defined

router = APIRouter(prefix="/freight-dashboard", tags=["Freight Broker Dashboard"])

@router.get("/summary")
async def get_freight_summary(session: AsyncSession = Depends(get_db)):
    try:
        result = {}

        # ✅ Total shipments
        total_shipments = (await session.execute(
            select(func.count()).select_from(Shipment)
        )).scalar()
        result["total_shipments"] = total_shipments or 0

        # ✅ Delayed shipments
        delayed_shipments = (await session.execute(
            select(func.count()).select_from(Shipment).where(Shipment.description == "delayed")
        )).scalar()
        result["delayed_shipments"] = delayed_shipments or 0

        # ✅ On the way = total - delayed
        result["on_the_way"] = result["total_shipments"] - result["delayed_shipments"]

        # Hardcoded data
        result["active_alerts"] = 4
        result["estimated_time"] = "3h 42m"

        return result

    except Exception as e:
        print("🚨 ERROR:", e)  # ✅ appears in terminal
        return {"error": str(e)}

