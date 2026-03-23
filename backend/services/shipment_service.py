from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete
from backend.models import Shipment, MessageLog
from datetime import datetime
from backend.utils.email_utils import send_bot_email
from backend.schemas.shipment_schema import ShipmentCreate
from backend.database.session import get_async_session
from backend.models.user import User
import asyncio
import os
import re
from dotenv import load_dotenv
from backend.config import settings
from backend.services.notification_service import notification_service

load_dotenv()

router = APIRouter()


async def _get_shipment_recipient(db: AsyncSession, user_id: int | None) -> tuple[str | None, str]:
    if user_id is not None:
        user = await db.get(User, int(user_id))
        if user and getattr(user, "email", None):
            return str(user.email), str(getattr(user, "full_name", None) or user.email)
    fallback = settings.ADMIN_EMAIL or settings.SUPPORT_EMAIL or settings.SMTP_FROM or settings.SMTP_USER
    return fallback or None, "Operations Team"


async def create_shipment(db: AsyncSession, shipment_data: ShipmentCreate) -> Shipment:
    shipment_dict = shipment_data.dict()

    if "weight" in shipment_dict:
        try:
            shipment_dict["weight"] = float(
                re.sub(r"[^\d.]", "", str(shipment_dict["weight"]))
            )
        except Exception:
            raise HTTPException(
                status_code=400,
                detail="Weight must be a numeric value.",
            )

    if "length" in shipment_dict and shipment_dict["length"] is not None:
        try:
            shipment_dict["length"] = float(
                re.sub(r"[^\d.]", "", str(shipment_dict["length"]))
            )
        except Exception:
            raise HTTPException(
                status_code=400,
                detail="Length must be a numeric value.",
            )

    if "rate" in shipment_dict:
        try:
            shipment_dict["rate"] = float(
                re.sub(r"[^\d.]", "", str(shipment_dict["rate"]))
            )
        except Exception:
            raise HTTPException(
                status_code=400,
                detail="Rate must be a numeric value.",
            )

    shipment_obj = Shipment(**shipment_dict)
    db.add(shipment_obj)
    await db.commit()
    await db.refresh(shipment_obj)
    try:
        from backend.services.platform_webhook_dispatcher import dispatch_from_platform_settings

        await dispatch_from_platform_settings(
            db=db,
            event_type="shipment.created",
            data={
                "shipment_id": shipment_obj.id,
                "status": shipment_obj.status,
                "pickup_location": shipment_obj.pickup_location,
                "dropoff_location": shipment_obj.dropoff_location,
                "rate": shipment_obj.rate,
            },
        )
    except Exception:
        pass
    try:
        recipient_email, recipient_name = await _get_shipment_recipient(db, getattr(shipment_obj, "user_id", None))
        asyncio.create_task(
            notification_service.send_shipment_notification(
                event_type="created",
                user_email=recipient_email,
                user_name=recipient_name,
                shipment_data={
                    "shipment_id": shipment_obj.id,
                    "origin": shipment_obj.pickup_location,
                    "destination": shipment_obj.dropoff_location,
                    "estimated_delivery": "Pending scheduling",
                    "tracking_url": f"{settings.FRONTEND_URL}/shipments/{shipment_obj.id}",
                },
            )
        )
    except Exception:
        pass
    return shipment_obj


@router.post("/shipments")
async def create_shipment_route(
    shipment: ShipmentCreate,
    db: AsyncSession = Depends(get_async_session),
):
    try:
        shipment_obj = await create_shipment(db, shipment)

        # Optional AI route optimization logging
        try:
            gpt_response = await openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a logistics advisor.",
                    },
                    {
                        "role": "user",
                        "content": (
                            f"Analyze the route from {shipment.pickup_location} "
                            f"to {shipment.dropoff_location}. "
                            "Suggest 3 improvements for cost or time efficiency."
                        ),
                    },
                ],
                temperature=0.6,
                max_tokens=200,
            )
            content = gpt_response.choices[0].message.content
            ai_response = content.strip() if content else "No response from AI."
            log = MessageLog(
                sender="AI Freight Advisor",
                message=ai_response,
                context=f"shipment:{shipment_obj.id}",
            )
            db.add(log)
            await db.commit()
        except Exception as e:
            log = MessageLog(
                sender="AI Freight Advisor",
                message=f"GPT Error: {str(e)}",
                context=f"shipment:{shipment_obj.id}",
            )
            db.add(log)
            await db.commit()

        # FIX: use 'to=' instead of 'to_email='
        send_bot_email(
            bot_name="freight",
            to="operations@gabanilogistics.com",
            subject=f"📦 New Shipment Registered #{shipment_obj.id}",
            body=(
                f"Shipment #{shipment_obj.id} was created: "
                f"{shipment.pickup_location} ➝ {shipment.dropoff_location}."
            ),
        )

        return {
            "message": "✅ Shipment created successfully",
            "shipment": shipment_obj,
        }
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"❌ Failed to create shipment: {str(e)}",
        )


async def get_all_shipments(db: AsyncSession):
    result = await db.execute(select(Shipment))
    return result.scalars().all()


async def get_shipment_by_id(shipment_id: int, db: AsyncSession):
    result = await db.execute(select(Shipment).where(Shipment.id == shipment_id))
    return result.scalar_one_or_none()


async def update_shipment(shipment_id: int, updated_data: dict, db: AsyncSession):
    existing = await get_shipment_by_id(shipment_id, db)
    stmt = (
        update(Shipment)
        .where(Shipment.id == shipment_id)
        .values(**updated_data, updated_at=datetime.utcnow())
        .execution_options(synchronize_session="fetch")
    )
    await db.execute(stmt)
    await db.commit()
    try:
        from backend.services.platform_webhook_dispatcher import dispatch_from_platform_settings

        event_type = "shipment.status.updated" if "status" in updated_data else "shipment.updated"
        await dispatch_from_platform_settings(
            db=db,
            event_type=event_type,
            data={
                "shipment_id": shipment_id,
                "changes": updated_data,
            },
        )
    except Exception:
        pass
    try:
        recipient_email, recipient_name = await _get_shipment_recipient(db, getattr(existing, "user_id", None))
        if "status" in updated_data:
            status_value = str(updated_data.get("status") or "Updated")
            event_type = "status_changed"
            if status_value.lower() == "delayed":
                event_type = "delayed"
            elif status_value.lower() == "delivered":
                event_type = "delivered"
            asyncio.create_task(
                notification_service.send_shipment_notification(
                    event_type=event_type,
                    user_email=recipient_email,
                    user_name=recipient_name,
                    shipment_data={
                        "shipment_id": shipment_id,
                        "new_status": status_value,
                        "status": status_value,
                        "origin": getattr(existing, "pickup_location", "Unknown"),
                        "destination": getattr(existing, "dropoff_location", "Unknown"),
                        "current_location": "Updated in platform",
                        "estimated_delivery": "Check shipment details",
                        "tracking_url": f"{settings.FRONTEND_URL}/shipments/{shipment_id}",
                        "new_eta": "Check shipment details",
                        "delivery_time": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
                        "confirmation_url": f"{settings.FRONTEND_URL}/shipments/{shipment_id}",
                    },
                )
            )
    except Exception:
        pass
    return {"message": f"Shipment {shipment_id} updated successfully."}


async def delete_shipment(shipment_id: int, db: AsyncSession):
    stmt = delete(Shipment).where(Shipment.id == shipment_id)
    await db.execute(stmt)
    await db.commit()
    return {"message": f"Shipment {shipment_id} deleted successfully."}


async def get_shipment_stats(db: AsyncSession):
    """Get shipment statistics for dashboard"""
    result = await db.execute(select(Shipment))
    shipments = result.scalars().all()
    
    total = len(shipments)
    in_transit = sum(1 for s in shipments if s.status == "In Transit")
    delivered = sum(1 for s in shipments if s.status == "Delivered")
    pending = sum(1 for s in shipments if s.status in ["Pending", "Booked", "Dispatched"])
    
    return {
        "total": total,
        "in_transit": in_transit,
        "delivered": delivered,
        "pending": pending,
        "active": in_transit + pending
    }

