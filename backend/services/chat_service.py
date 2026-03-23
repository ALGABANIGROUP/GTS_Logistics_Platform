"""
Dashboard Chat Service for GTS Communication System
"""

from datetime import datetime
from typing import List, Dict, Any, Optional
import json
import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class ChatService:
    """
    Integrated chat service in the system
    """

    def __init__(self, storage_path: Optional[str] = None):
        self.storage_path = storage_path or os.path.join(
            Path(__file__).parent.parent.parent, 'data', 'chat_messages.json'
        )
        self.messages: List[Dict[str, Any]] = []
        self.channels = {
            "general": [],
            "incidents": [],
            "alerts": [],
            "system": []
        }
        self._ensure_storage_dir()
        self._load_messages()

    def _ensure_storage_dir(self):
        """Create storage directory if it doesn't exist"""
        storage_dir = os.path.dirname(self.storage_path)
        os.makedirs(storage_dir, exist_ok=True)

    def _load_messages(self):
        """Load messages from file"""
        try:
            if os.path.exists(self.storage_path):
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.messages = data.get('messages', [])
                    self.channels = data.get('channels', {
                        "general": [],
                        "incidents": [],
                        "alerts": [],
                        "system": []
                    })
                logger.info(f"✅ Loaded {len(self.messages)} chat messages")
        except Exception as e:
            logger.error(f"❌ Error loading chat messages: {e}")
            # Reinitialize data in case of error
            self.messages = []
            self.channels = {
                "general": [],
                "incidents": [],
                "alerts": [],
                "system": []
            }

    def _save_messages(self):
        """Save messages to file"""
        try:
            data = {
                'messages': self.messages,
                'channels': self.channels,
                'last_updated': datetime.now().isoformat()
            }
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"❌ Error saving chat messages: {e}")

    def send_message(self, channel: str, user: str, message: str,
                    message_type: str = 'text') -> Dict[str, Any]:
        """
        Send message to channel

        Args:
            channel: Channel name
            user: User name
            message: Message text
            message_type: Message type (text, system, alert)

        Returns:
            Dict: Sent message data
        """
        if channel not in self.channels:
            self.channels[channel] = []

        msg = {
            "id": len(self.messages) + 1,
            "channel": channel,
            "user": user,
            "message": message,
            "message_type": message_type,
            "timestamp": datetime.now().isoformat(),
            "read": False,
            "read_by": []
        }

        self.messages.append(msg)
        self.channels[channel].append(msg)

        # Save messages
        self._save_messages()

        logger.info(f"💬 New message in #{channel} from {user}: {message[:50]}...")

        return msg

    def get_messages(self, channel: str, limit: int = 50,
                    since: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get channel messages

        Args:
            channel: Channel name
            limit: Number of messages requested
            since: Get messages after a certain date

        Returns:
            List: List of messages
        """
        if channel not in self.channels:
            return []

        messages = self.channels[channel]

        # Filter by date if specified
        if since:
            try:
                since_dt = datetime.fromisoformat(since)
                messages = [msg for msg in messages
                          if datetime.fromisoformat(msg['timestamp']) > since_dt]
            except:
                pass

        return messages[-limit:]

    def get_all_channels(self) -> Dict[str, int]:
        """
        Get all channels with message count

        Returns:
            Dict: Channels with message count
        """
        return {channel: len(messages) for channel, messages in self.channels.items()}

    def mark_read(self, message_id: int, user: str) -> Dict[str, Any]:
        """
        Mark message as read

        Args:
            message_id: Message ID
            user: User name

        Returns:
            Dict: Operation result
        """
        for msg in self.messages:
            if msg["id"] == message_id:
                if user not in msg.get("read_by", []):
                    msg["read_by"].append(user)
                    msg["read"] = True  # For compatibility with the old interface
                self._save_messages()
                return {"success": True, "message": "Marked as read"}

        return {"success": False, "error": "Message not found"}

    def get_unread_count(self, channel: str, user: str) -> int:
        """
        Get the number of unread messages in a channel

        Args:
            channel: Channel name
            user: User name

        Returns:
            int: Number of unread messages
        """
        if channel not in self.channels:
            return 0

        return sum(1 for msg in self.channels[channel]
                  if user not in msg.get("read_by", []))

    def send_system_message(self, channel: str, message: str) -> Dict[str, Any]:
        """
        Send system message

        Args:
            channel: Channel name
            message: Message text

        Returns:
            Dict: Message data
        """
        return self.send_message(channel, "system", message, "system")

    def send_incident_notification(self, incident: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send incident notification

        Args:
            incident: incident data

        Returns:
            Dict: message data
        """
        message = f"""🚨 INCIDENT DETECTED

ID: {incident.get('id', 'UNKNOWN')}
Severity: {incident.get('severity', 'unknown').upper()}
Service: {incident.get('service', 'Unknown')}
Error: {incident.get('error_message', 'No details')[:200]}"""

        return self.send_message("incidents", "incident_bot", message, "alert")

    def cleanup_old_messages(self, days: int = 30):
        """
        Clean up old messages

        Args:
            days: number of days to keep messages
        """
        from datetime import timedelta
        cutoff_date = datetime.now() - timedelta(days=days)

        original_count = len(self.messages)

        # Filter messages
        self.messages = [
            msg for msg in self.messages
            if datetime.fromisoformat(msg['timestamp']) > cutoff_date
        ]

        # Rebuild channels
        self.channels = {
            "general": [],
            "incidents": [],
            "alerts": [],
            "system": []
        }

        for msg in self.messages:
            channel = msg['channel']
            if channel in self.channels:
                self.channels[channel].append(msg)

        # Save changes
        self._save_messages()

        removed_count = original_count - len(self.messages)
        logger.info(f"🧹 Cleaned up {removed_count} old chat messages")

    def export_messages(self, channel: Optional[str] = None) -> str:
        """
        Export messages to JSON

        Args:
            channel: specific channel or all channels

        Returns:
            str: data in JSON format
        """
        if channel:
            data = {
                'channel': channel,
                'messages': self.channels.get(channel, []),
                'exported_at': datetime.now().isoformat()
            }
        else:
            data = {
                'channels': self.channels,
                'total_messages': len(self.messages),
                'exported_at': datetime.now().isoformat()
            }

        return json.dumps(data, ensure_ascii=False, indent=2)


# Create single instance of the service
chat_service = ChatService()