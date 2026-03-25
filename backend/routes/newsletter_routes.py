"""
Newsletter Routes - Subscribe, Unsubscribe, and Admin Management
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, EmailStr
from typing import Optional
import logging

from backend.database.session import get_async_session
from backend.security.auth import get_current_user
from backend.services.newsletter_service import get_newsletter_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/newsletter", tags=["Newsletter"])


class SubscribeRequest(BaseModel):
    email: EmailStr
    source: str = "website"
    consent: bool = True


class UnsubscribeRequest(BaseModel):
    email: EmailStr
    token: Optional[str] = None


class NewsletterRequest(BaseModel):
    subject: str
    content: str
    html_content: Optional[str] = None


@router.post("/subscribe")
async def subscribe_to_newsletter(
    request: SubscribeRequest,
    background_tasks: BackgroundTasks,
    session=Depends(get_async_session)
):
    """Subscribe to newsletter"""
    service = get_newsletter_service(session)
    result = await service.subscribe(
        email=request.email,
        source=request.source,
        consent=request.consent
    )

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])

    return result


@router.post("/unsubscribe")
async def unsubscribe_from_newsletter(
    request: UnsubscribeRequest,
    session=Depends(get_async_session)
):
    """Unsubscribe from newsletter"""
    service = get_newsletter_service(session)
    result = await service.unsubscribe(
        email=request.email,
        token=request.token
    )

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])

    return result


@router.get("/subscribers")
async def get_subscribers(
    active_only: bool = True,
    limit: int = 100,
    session=Depends(get_async_session),
    current_user=Depends(get_current_user)
):
    """Get newsletter subscribers (admin only)"""
    service = get_newsletter_service(session)
    subscribers = await service.get_subscribers(active_only, limit)
    count = await service.get_subscriber_count(active_only)

    return {
        "success": True,
        "subscribers": subscribers,
        "count": count,
        "active_only": active_only
    }


@router.post("/send")
async def send_newsletter(
    request: NewsletterRequest,
    background_tasks: BackgroundTasks,
    session=Depends(get_async_session),
    current_user=Depends(get_current_user)
):
    """Send newsletter to all subscribers (admin only)"""
    service = get_newsletter_service(session)

    # Send in background to avoid timeout
    background_tasks.add_task(
        service.send_newsletter,
        request.subject,
        request.content,
        request.html_content
    )

    return {
        "success": True,
        "message": "Newsletter sending started. You will receive a report shortly."
    }


@router.get("/stats")
async def get_newsletter_stats(
    session=Depends(get_async_session),
    current_user=Depends(get_current_user)
):
    """Get newsletter statistics (admin only)"""
    service = get_newsletter_service(session)
    active_count = await service.get_subscriber_count(active_only=True)
    total_count = await service.get_subscriber_count(active_only=False)

    return {
        "success": True,
        "stats": {
            "active_subscribers": active_count,
            "total_subscribers": total_count,
            "inactive_subscribers": total_count - active_count
        }
    }