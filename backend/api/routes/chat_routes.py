"""
Chat API Routes for Dashboard Communication
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import logging

from ..services.chat_service import chat_service
from ..services.auth_service import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])

# Pydantic Models
class MessageRequest(BaseModel):
    channel: str
    message: str
    message_type: Optional[str] = "text"

class MarkReadRequest(BaseModel):
    message_id: int

class ChannelInfo(BaseModel):
    name: str
    message_count: int
    unread_count: int

@router.get("/channels")
async def get_channels(current_user: Dict = Depends(get_current_user)) -> Dict[str, Any]:
    """
    Get all channels with their information
    """
    try:
        channels = chat_service.get_all_channels()
        result = {}

        for channel_name, count in channels.items():
            unread = chat_service.get_unread_count(channel_name, current_user.get('username', 'unknown'))
            result[channel_name] = {
                "name": channel_name,
                "message_count": count,
                "unread_count": unread
            }

        return {"channels": result}

    except Exception as e:
        logger.error(f"Error getting channels: {e}")
        raise HTTPException(status_code=500, detail="Failed to get channels")

@router.get("/{channel}/messages")
async def get_messages(
    channel: str,
    limit: int = Query(50, ge=1, le=200),
    since: Optional[str] = None,
    current_user: Dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get channel messages
    """
    try:
        if channel not in ["general", "incidents", "alerts", "system"]:
            raise HTTPException(status_code=400, detail="Invalid channel")

        messages = chat_service.get_messages(channel, limit, since)

        return {
            "channel": channel,
            "messages": messages,
            "count": len(messages)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting messages for channel {channel}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get messages")

@router.post("/send")
async def send_message(
    request: MessageRequest,
    current_user: Dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Send a new message
    """
    try:
        if request.channel not in ["general", "incidents", "alerts"]:
            raise HTTPException(status_code=400, detail="Invalid channel")

        if not request.message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")

        # Send the message
        message = chat_service.send_message(
            request.channel,
            current_user.get('username', 'unknown'),
            request.message.strip(),
            request.message_type or 'text'
        )

        return {
            "success": True,
            "message": message
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        raise HTTPException(status_code=500, detail="Failed to send message")

@router.post("/mark-read")
async def mark_message_read(
    request: MarkReadRequest,
    current_user: Dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Mark message as read
    """
    try:
        result = chat_service.mark_read(
            request.message_id,
            current_user.get('username', 'unknown')
        )

        if not result["success"]:
            raise HTTPException(status_code=404, detail=result["error"])

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error marking message as read: {e}")
        raise HTTPException(status_code=500, detail="Failed to mark message as read")

@router.get("/unread/{channel}")
async def get_unread_count(
    channel: str,
    current_user: Dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get the number of unread messages in a channel
    """
    try:
        if channel not in ["general", "incidents", "alerts", "system"]:
            raise HTTPException(status_code=400, detail="Invalid channel")

        count = chat_service.get_unread_count(
            channel,
            current_user.get('username', 'unknown')
        )

        return {
            "channel": channel,
            "unread_count": count
        }

    except Exception as e:
        logger.error(f"Error getting unread count for channel {channel}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get unread count")

@router.post("/system-message")
async def send_system_message(
    channel: str,
    message: str,
    current_user: Dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Send system message (admins only)
    """
    try:
        # Check user permissions (must be admin or manager)
        if not current_user.get('is_admin', False):
            raise HTTPException(status_code=403, detail="Admin access required")

        if channel not in ["general", "incidents", "alerts", "system"]:
            raise HTTPException(status_code=400, detail="Invalid channel")

        if not message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")

        result = chat_service.send_system_message(channel, message.strip())

        return {
            "success": True,
            "message": result
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending system message: {e}")
        raise HTTPException(status_code=500, detail="Failed to send system message")

@router.post("/incident-notification")
async def send_incident_notification(
    incident_data: Dict[str, Any],
    current_user: Dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Send incident notification (system only)
    """
    try:
        # This can be used by the system or admins
        if not current_user.get('is_admin', False) and current_user.get('username') != 'system':
            raise HTTPException(status_code=403, detail="System access required")

        result = chat_service.send_incident_notification(incident_data)

        return {
            "success": True,
            "message": result
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending incident notification: {e}")
        raise HTTPException(status_code=500, detail="Failed to send incident notification")

@router.delete("/cleanup")
async def cleanup_old_messages(
    days: int = Query(30, ge=1, le=365),
    current_user: Dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Clean up old messages (admins only)
    """
    try:
        if not current_user.get('is_admin', False):
            raise HTTPException(status_code=403, detail="Admin access required")

        original_count = len(chat_service.messages)
        chat_service.cleanup_old_messages(days)
        new_count = len(chat_service.messages)
        removed = original_count - new_count

        return {
            "success": True,
            "message": f"Cleaned up {removed} old messages",
            "removed_count": removed,
            "remaining_count": new_count
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cleaning up messages: {e}")
        raise HTTPException(status_code=500, detail="Failed to cleanup messages")

@router.get("/export/{channel}")
async def export_channel_messages(
    channel: str,
    current_user: Dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Export channel messages (for managers only)
    """
    try:
        if not current_user.get('is_admin', False):
            raise HTTPException(status_code=403, detail="Admin access required")

        if channel not in ["general", "incidents", "alerts", "system"]:
            raise HTTPException(status_code=400, detail="Invalid channel")

        export_data = chat_service.export_messages(channel)

        return {
            "channel": channel,
            "export_data": export_data,
            "format": "json"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting messages for channel {channel}: {e}")
        raise HTTPException(status_code=500, detail="Failed to export messages")