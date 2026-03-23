"""
Support Email Service
Email integration for ticket creation and notifications
Includes inbound parsing and outbound support messaging.
"""

import asyncio
import email
import imaplib
from datetime import datetime, timedelta
from typing import Optional, List
import logging
import os
from jinja2 import Template
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, select
from backend.utils.email_utils import send_email
from backend.models.support_models import (
    SupportTicket, TicketComment, SupportEmail, 
    EmailTemplate, SLALevel, TicketStatus, ChannelType
)
from backend.database.config import AsyncSessionLocal

logger = logging.getLogger(__name__)


class SupportEmailService:
    """Handle support ticket email operations"""
    
    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", 587))
        self.smtp_user = os.getenv("SMTP_USER")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.support_email = os.getenv("SUPPORT_EMAIL", "support@gabanilogistics.com")
        
        self.imap_host = os.getenv("IMAP_HOST", "imap.gmail.com")
        self.imap_user = os.getenv("IMAP_USER")
        self.imap_password = os.getenv("IMAP_PASSWORD")
    
    # ============================================
    # OUTGOING EMAILS
    # ============================================
    
    async def send_ticket_created_email(
        self,
        ticket: SupportTicket,
        db: AsyncSession
    ):
        """Send confirmation email when ticket is created"""
        
        subject = f"Support Ticket Created: {ticket.ticket_number}"
        
        template_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif;">
                <h2>Your Support Ticket Has Been Created</h2>
                <p>Dear {ticket.customer_name},</p>
                <p>Thank you for contacting us. Your support ticket has been created and assigned a reference number.</p>
                
                <div style="background-color: #f5f5f5; padding: 15px; margin: 20px 0; border-radius: 5px;">
                    <p><strong>Ticket Number:</strong> {ticket.ticket_number}</p>
                    <p><strong>Title:</strong> {ticket.title}</p>
                    <p><strong>Priority:</strong> {ticket.priority.upper()}</p>
                    <p><strong>Status:</strong> {ticket.status.upper()}</p>
                </div>
                
                <h3>SLA Information</h3>
                <p><strong>Expected Response Time:</strong> {ticket.sla_level.response_time} hours</p>
                <p><strong>Expected Resolution Time:</strong> {ticket.sla_level.resolution_time} hours</p>
                
                <p>You can track your ticket at: {os.getenv('FRONTEND_URL')}/support/tickets/{ticket.id}</p>
                
                <p>Best regards,<br/>
                The Support Team</p>
            </body>
        </html>
        """
        
        await self._send_email(
            to_email=ticket.customer_email,
            subject=subject,
            body=template_content,
            ticket_id=ticket.id
        )
    
    async def send_ticket_assigned_email(
        self,
        ticket: SupportTicket,
        agent_email: str,
        db: AsyncSession
    ):
        """Send email to agent when ticket is assigned"""
        
        subject = f"New Ticket Assigned: {ticket.ticket_number}"
        
        template_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif;">
                <h2>New Ticket Assigned to You</h2>
                
                <div style="background-color: #f5f5f5; padding: 15px; margin: 20px 0; border-radius: 5px;">
                    <p><strong>Ticket Number:</strong> {ticket.ticket_number}</p>
                    <p><strong>Title:</strong> {ticket.title}</p>
                    <p><strong>Priority:</strong> {ticket.priority.upper()}</p>
                    <p><strong>Customer:</strong> {ticket.customer_name}</p>
                    <p><strong>Due (Response):</strong> {ticket.sla_response_due.strftime('%Y-%m-%d %H:%M')}</p>
                    <p><strong>Due (Resolution):</strong> {ticket.sla_resolution_due.strftime('%Y-%m-%d %H:%M')}</p>
                </div>
                
                <h3>Ticket Description</h3>
                <p>{ticket.description}</p>
                
                <p><a href="{os.getenv('FRONTEND_URL')}/admin/support/tickets/{ticket.id}" style="background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">View Ticket</a></p>
                
                <p>Best regards,<br/>
                The Support System</p>
            </body>
        </html>
        """
        
        await self._send_email(
            to_email=agent_email,
            subject=subject,
            body=template_content,
            ticket_id=ticket.id
        )
    
    async def send_ticket_updated_email(
        self,
        ticket: SupportTicket,
        update_message: str,
        recipient_email: str,
        db: AsyncSession
    ):
        """Send email when ticket is updated"""
        
        subject = f"Ticket Updated: {ticket.ticket_number}"
        
        template_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif;">
                <h2>Your Support Ticket Has Been Updated</h2>
                <p>Dear {ticket.customer_name if recipient_email == ticket.customer_email else 'Agent'},</p>
                
                <p><strong>Ticket Number:</strong> {ticket.ticket_number}</p>
                
                <h3>Update:</h3>
                <p>{update_message}</p>
                
                <p><strong>Current Status:</strong> {ticket.status.upper()}</p>
                
                <p>View your ticket: {os.getenv('FRONTEND_URL')}/support/tickets/{ticket.id}</p>
                
                <p>Best regards,<br/>
                The Support Team</p>
            </body>
        </html>
        """
        
        await self._send_email(
            to_email=recipient_email,
            subject=subject,
            body=template_content,
            ticket_id=ticket.id
        )
    
    async def send_ticket_resolved_email(
        self,
        ticket: SupportTicket,
        resolution_message: str,
        db: AsyncSession
    ):
        """Send email when ticket is resolved"""
        
        subject = f"Your Support Ticket Has Been Resolved: {ticket.ticket_number}"
        
        template_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif;">
                <h2>Your Support Ticket Has Been Resolved</h2>
                <p>Dear {ticket.customer_name},</p>
                
                <p>We're happy to inform you that your support ticket has been resolved.</p>
                
                <div style="background-color: #f5f5f5; padding: 15px; margin: 20px 0; border-radius: 5px;">
                    <p><strong>Ticket Number:</strong> {ticket.ticket_number}</p>
                    <p><strong>Title:</strong> {ticket.title}</p>
                    <p><strong>Resolved Date:</strong> {ticket.resolved_at.strftime('%Y-%m-%d %H:%M')}</p>
                </div>
                
                <h3>Resolution:</h3>
                <p>{resolution_message}</p>
                
                <p>Please rate your experience: <a href="{os.getenv('FRONTEND_URL')}/support/tickets/{ticket.id}/feedback">Provide Feedback</a></p>
                
                <p>Best regards,<br/>
                The Support Team</p>
            </body>
        </html>
        """
        
        await self._send_email(
            to_email=ticket.customer_email,
            subject=subject,
            body=template_content,
            ticket_id=ticket.id
        )
    
    async def send_sla_warning_email(
        self,
        ticket: SupportTicket,
        time_remaining_hours: float,
        db: AsyncSession
    ):
        """Send SLA breach warning email"""
        
        subject = f"⚠️ SLA Warning: {ticket.ticket_number} - {int(time_remaining_hours)}h remaining"
        
        template_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif;">
                <h2>⚠️ SLA Breach Warning</h2>
                
                <div style="background-color: #fff3cd; border: 1px solid #ffc107; padding: 15px; margin: 20px 0; border-radius: 5px;">
                    <p><strong style="color: #856404;">Ticket {ticket.ticket_number} is at risk of SLA breach!</strong></p>
                    <p><strong>Time Remaining:</strong> {int(time_remaining_hours)} hours</p>
                    <p><strong>Priority:</strong> {ticket.priority.upper()}</p>
                    <p><strong>Customer:</strong> {ticket.customer_name}</p>
                </div>
                
                <p><a href="{os.getenv('FRONTEND_URL')}/admin/support/tickets/{ticket.id}" style="background-color: #ffc107; color: #000; padding: 10px 20px; text-decoration: none; border-radius: 5px;">View Ticket</a></p>
                
                <p>Please prioritize this ticket to avoid SLA breach.</p>
            </body>
        </html>
        """
        
        # Send to assigned agent
        if ticket.assigned_agent:
            await self._send_email(
                to_email=ticket.assigned_agent.user.email,
                subject=subject,
                body=template_content,
                ticket_id=ticket.id
            )
    
    async def _send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        ticket_id: Optional[int] = None
    ):
        """Internal method to send email via SMTP"""
        
        try:
            sent = await asyncio.to_thread(
                send_email,
                subject,
                body,
                [to_email],
                True,
                None,
                self.support_email,
                self.smtp_user,
                self.smtp_password,
                self.smtp_host,
                self.smtp_port,
                True,
            )
            if not sent:
                raise RuntimeError("send_email returned False")
            
            # Log sent email
            async with AsyncSessionLocal() as db:
                email_log = SupportEmail(
                    ticket_id=ticket_id,
                    from_email=self.support_email,
                    to_email=to_email,
                    subject=subject,
                    body=body,
                    status="sent"
                )
                db.add(email_log)
                await db.commit()
            
            logger.info(f"Email sent to {to_email}")
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            
            # Log failed email
            async with AsyncSessionLocal() as db:
                email_log = SupportEmail(
                    ticket_id=ticket_id,
                    from_email=self.support_email,
                    to_email=to_email,
                    subject=subject,
                    body=body,
                    status="failed",
                    error_message=str(e)
                )
                db.add(email_log)
                await db.commit()
    
    # ============================================
    # INCOMING EMAILS
    # ============================================
    
    async def check_support_mailbox(self):
        """Check support mailbox for incoming emails and create tickets"""
        
        try:
            # Connect to IMAP
            mail = imaplib.IMAP4_SSL(self.imap_host)
            mail.login(self.imap_user, self.imap_password)
            mail.select("INBOX")
            
            # Search for unread emails
            status, messages = mail.search(None, "UNSEEN")
            
            if status == "OK":
                email_ids = messages[0].split()
                
                async with AsyncSessionLocal() as db:
                    for email_id in email_ids:
                        await self._process_email(email_id, mail, db)
            
            mail.close()
            mail.logout()
            
        except Exception as e:
            logger.error(f"Error checking support mailbox: {str(e)}")
    
    async def _process_email(self, email_id: bytes, mail: imaplib.IMAP4_SSL, db: AsyncSession):
        """Process incoming email and create ticket if needed"""
        
        try:
            status, msg_data = mail.fetch(email_id, "(RFC822)")
            
            if status == "OK":
                msg = email.message_from_bytes(msg_data[0][1])
                
                # Extract email details
                from_email = msg.get("From")
                subject = msg.get("Subject")
                message_id = msg.get("Message-ID")
                
                # Get email body
                body = ""
                if msg.is_multipart():
                    for part in msg.get_payload():
                        if part.get_content_type() == "text/plain":
                            body = part.get_payload(decode=True).decode()
                else:
                    body = msg.get_payload(decode=True).decode()
                
                # Check if email already processed
                existing = await db.execute(
                    select(SupportEmail).where(SupportEmail.message_id == message_id)
                )
                
                if existing.scalar_one_or_none():
                    logger.info(f"Email {message_id} already processed")
                    return
                
                # Find or create user
                # TODO: Implement user lookup/creation
                
                # Create ticket
                sla_query = select(SLALevel).where(SLALevel.priority == "medium")
                sla_result = await db.execute(sla_query)
                sla_level = sla_result.scalar_one()
                
                now = datetime.utcnow()
                ticket = SupportTicket(
                    ticket_number=f"TK-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
                    customer_email=from_email,
                    customer_name=from_email.split("@")[0],
                    customer_id=1,  # TODO: Get actual customer ID
                    title=subject,
                    description=body,
                    category="general",
                    priority="medium",
                    channel=ChannelType.EMAIL,
                    original_channel_id=message_id,
                    sla_level_id=sla_level.id,
                    sla_response_due=now + timedelta(hours=sla_level.response_time),
                    sla_resolution_due=now + timedelta(hours=sla_level.resolution_time),
                )
                
                db.add(ticket)
                await db.commit()
                await db.refresh(ticket)
                
                # Log the email
                email_log = SupportEmail(
                    message_id=message_id,
                    ticket_id=ticket.id,
                    from_email=from_email,
                    to_email=self.support_email,
                    subject=subject,
                    body=body,
                    status="processed"
                )
                db.add(email_log)
                await db.commit()
                
                # Send confirmation email
                await self.send_ticket_created_email(ticket, db)
                
                logger.info(f"Ticket created from email: {ticket.ticket_number}")
                
        except Exception as e:
            logger.error(f"Error processing email {email_id}: {str(e)}")
    
    # ============================================
    # SCHEDULED TASKS
    # ============================================
    
    async def check_sla_breaches(self):
        """Check for SLA breaches and send warnings"""
        
        try:
            async with AsyncSessionLocal() as db:
                # Find at-risk tickets
                now = datetime.utcnow()
                
                # Tickets within 25% of SLA time
                at_risk_query = select(SupportTicket).where(
                    and_(
                        SupportTicket.status.in_([TicketStatus.OPEN, TicketStatus.IN_PROGRESS]),
                        SupportTicket.sla_resolution_due <= now + timedelta(hours=1)
                    )
                )
                
                result = await db.execute(at_risk_query)
                at_risk_tickets = result.scalars().all()
                
                for ticket in at_risk_tickets:
                    time_remaining = (ticket.sla_resolution_due - now).total_seconds() / 3600
                    await self.send_sla_warning_email(ticket, time_remaining, db)
                    
        except Exception as e:
            logger.error(f"Error checking SLA breaches: {str(e)}")


# Create singleton instance
support_email_service = SupportEmailService()

