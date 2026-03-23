"""
Communication Automation Service
Handles automated emails, SMS, and notifications
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import asyncio
from enum import Enum
from backend.utils.email_utils import send_bot_email

logger = logging.getLogger(__name__)


class CommunicationType(str, Enum):
    EMAIL = "email"
    SMS = "sms"
    PHONE_CALL = "phone_call"
    PUSH_NOTIFICATION = "push_notification"
    WHATSAPP = "whatsapp"


class MessageTemplate(str, Enum):
    SHIPMENT_CREATED = "shipment_created"
    SHIPMENT_IN_TRANSIT = "shipment_in_transit"
    SHIPMENT_DELIVERED = "shipment_delivered"
    SHIPMENT_DELAYED = "shipment_delayed"
    DRIVER_ASSIGNED = "driver_assigned"
    CUSTOMER_OFFER = "customer_offer"
    PAYMENT_REMINDER = "payment_reminder"
    SAFETY_ALERT = "safety_alert"
    WEATHER_WARNING = "weather_warning"


class CommunicationAutomationService:
    """Automates communication with customers and drivers"""
    
    def __init__(self):
        self.message_queue = []
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict[str, Dict[str, str]]:
        """Load message templates for different scenarios"""
        return {
            MessageTemplate.SHIPMENT_CREATED: {
                "subject": "Shipment #{shipment_id} Created Successfully",
                "email_body": """
                Dear {customer_name},
                
                Your shipment has been created successfully.
                
                Shipment ID: {shipment_id}
                Origin: {origin}
                Destination: {destination}
                Estimated Delivery: {estimated_delivery}
                
                You can track your shipment at: {tracking_url}
                
                Best regards,
                Gabani Transport Solutions
                """,
                "sms_body": "Your shipment #{shipment_id} is confirmed. Track: {tracking_url}",
            },
            MessageTemplate.SHIPMENT_IN_TRANSIT: {
                "subject": "Shipment #{shipment_id} In Transit",
                "email_body": """
                Dear {customer_name},
                
                Your shipment is now in transit.
                
                Current Location: {current_location}
                Driver: {driver_name}
                Expected Arrival: {expected_arrival}
                
                Track live: {tracking_url}
                
                Best regards,
                Gabani Transport Solutions
                """,
                "sms_body": "Your shipment #{shipment_id} is on the way. ETA: {expected_arrival}",
            },
            MessageTemplate.SHIPMENT_DELIVERED: {
                "subject": "Shipment #{shipment_id} Delivered",
                "email_body": """
                Dear {customer_name},
                
                Great news! Your shipment has been delivered.
                
                Delivered at: {delivered_at}
                Received by: {received_by}
                
                Thank you for choosing Gabani Transport Solutions!
                
                Please rate your experience: {feedback_url}
                """,
                "sms_body": "Shipment #{shipment_id} delivered successfully. Rate us: {feedback_url}",
            },
            MessageTemplate.SHIPMENT_DELAYED: {
                "subject": "Important: Shipment #{shipment_id} Delayed",
                "email_body": """
                Dear {customer_name},
                
                We regret to inform you that your shipment has been delayed.
                
                Reason: {delay_reason}
                New Estimated Delivery: {new_estimated_delivery}
                
                We apologize for the inconvenience.
                
                Support: support@gabanitransport.com
                """,
                "sms_body": "Shipment #{shipment_id} delayed. New ETA: {new_estimated_delivery}. Sorry!",
            },
            MessageTemplate.CUSTOMER_OFFER: {
                "subject": "Special Offer Just for You!",
                "email_body": """
                Dear {customer_name},
                
                As one of our valued customers, we have a special offer for you:
                
                {offer_details}
                
                Valid until: {offer_expiry}
                Use code: {promo_code}
                
                Don't miss out!
                
                Best regards,
                Gabani Transport Solutions
                """,
                "sms_body": "Special offer! {offer_summary} Use code {promo_code}. Valid: {offer_expiry}",
            },
            MessageTemplate.SAFETY_ALERT: {
                "subject": "Safety Alert: {alert_title}",
                "email_body": """
                SAFETY ALERT
                
                {alert_message}
                
                Affected Routes: {affected_routes}
                Recommended Action: {recommended_action}
                
                Stay safe!
                Gabani Transport Solutions Safety Team
                """,
                "sms_body": "SAFETY ALERT: {alert_message}. Stay safe!",
            },
            MessageTemplate.WEATHER_WARNING: {
                "subject": "Weather Warning: {weather_condition}",
                "email_body": """
                Weather Warning
                
                Condition: {weather_condition}
                Affected Areas: {affected_areas}
                Duration: {duration}
                
                Drivers, please take necessary precautions.
                
                Safety Team
                """,
                "sms_body": "Weather Warning: {weather_condition} in {affected_areas}. Drive safe!",
            },
        }
    
    async def send_automated_message(
        self,
        recipient: Dict[str, str],
        template: MessageTemplate,
        data: Dict[str, str],
        communication_type: CommunicationType = CommunicationType.EMAIL
    ) -> Dict[str, Any]:
        """
        Send automated message using template
        
        Args:
            recipient: {"email": "...", "phone": "...", "name": "..."}
            template: Message template to use
            data: Template variables
            communication_type: Type of communication
        """
        try:
            template_data = self.templates.get(template)
            if not template_data:
                raise ValueError(f"Template {template} not found")
            
            # Format message with data
            if communication_type == CommunicationType.EMAIL:
                subject = template_data["subject"].format(**data)
                body = template_data["email_body"].format(**data)
                
                # Send email (integrate with your email service)
                result = await self._send_email(
                    to=recipient.get("email"),
                    subject=subject,
                    body=body
                )
                
            elif communication_type == CommunicationType.SMS:
                message = template_data["sms_body"].format(**data)
                
                # Send SMS (integrate with SMS service like Twilio)
                result = await self._send_sms(
                    to=recipient.get("phone"),
                    message=message
                )
            
            logger.info(f"Sent {communication_type} to {recipient.get('name')}")
            return {
                "status": "sent",
                "timestamp": datetime.utcnow().isoformat(),
                "recipient": recipient.get("name"),
                "type": communication_type
            }
            
        except Exception as e:
            logger.error(f"Error sending automated message: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }
    
    async def _send_email(self, to: str, subject: str, body: str) -> bool:
        """Send email from customer service bot mailbox."""
        try:
            result = await asyncio.to_thread(
                send_bot_email,
                "customer_service",
                subject,
                body,
                to,
            )
            logger.info(f"Email sent to {to}: {subject}")
            return bool(result)
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return False
    
    async def _send_sms(self, to: str, message: str) -> bool:
        """Send SMS (placeholder - integrate with SMS service)"""
        try:
            # TODO: Integrate with SMS service (Twilio, AWS SNS, etc.)
            logger.info(f"SMS sent to {to}: {message}")
            await asyncio.sleep(0.1)  # Simulate sending
            return True
        except Exception as e:
            logger.error(f"Error sending SMS: {e}")
            return False
    
    async def send_bulk_notifications(
        self,
        recipients: List[Dict[str, str]],
        template: MessageTemplate,
        data: Dict[str, str],
        communication_type: CommunicationType = CommunicationType.EMAIL
    ) -> Dict[str, Any]:
        """Send notifications to multiple recipients"""
        results = {
            "total": len(recipients),
            "sent": 0,
            "failed": 0,
            "details": []
        }
        
        for recipient in recipients:
            result = await self.send_automated_message(
                recipient=recipient,
                template=template,
                data=data,
                communication_type=communication_type
            )
            
            if result.get("status") == "sent":
                results["sent"] += 1
            else:
                results["failed"] += 1
            
            results["details"].append(result)
        
        return results
    
    async def schedule_reminder(
        self,
        recipient: Dict[str, str],
        template: MessageTemplate,
        data: Dict[str, str],
        send_at: datetime,
        communication_type: CommunicationType = CommunicationType.EMAIL
    ) -> str:
        """Schedule a message to be sent at a specific time"""
        try:
            reminder_id = f"reminder_{datetime.utcnow().timestamp()}"
            
            # TODO: Integrate with task queue (Celery, RQ, etc.)
            # For now, just log the scheduling
            logger.info(f"Scheduled {template} for {recipient.get('name')} at {send_at}")
            
            return reminder_id
            
        except Exception as e:
            logger.error(f"Error scheduling reminder: {e}")
            return None
    
    async def send_personalized_offer(
        self,
        customer: Dict[str, Any],
        offer_details: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Send personalized offer to customer based on ML recommendations
        """
        try:
            recipient = {
                "email": customer.get("email"),
                "phone": customer.get("phone"),
                "name": customer.get("name")
            }
            
            data = {
                "customer_name": customer.get("name"),
                "offer_details": offer_details.get("description"),
                "offer_summary": offer_details.get("summary"),
                "offer_expiry": offer_details.get("expiry"),
                "promo_code": offer_details.get("promo_code")
            }
            
            result = await self.send_automated_message(
                recipient=recipient,
                template=MessageTemplate.CUSTOMER_OFFER,
                data=data,
                communication_type=CommunicationType.EMAIL
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error sending personalized offer: {e}")
            return {"status": "failed", "error": str(e)}


# Singleton instance
communication_service = CommunicationAutomationService()
