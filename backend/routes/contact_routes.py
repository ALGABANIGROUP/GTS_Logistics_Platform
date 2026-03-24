"""
Contact Routes - Email and Chat endpoints
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Request
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
import logging
import os
import smtplib
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import httpx
from slowapi import Limiter
from slowapi.util import get_remote_address

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["Contact"])

# Rate limiter for contact endpoints
limiter = Limiter(key_func=get_remote_address)


# ============================================================
# Pydantic Models
# ============================================================
class ContactForm(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=20)
    company: Optional[str] = Field(None, max_length=100)
    message: str = Field(..., min_length=1, max_length=5000)
    inquiryType: str = Field(default="general", pattern="^(general|sales|support|partnership|billing)$")


class ChatMessage(BaseModel):
    message: str = Field(..., min_length=1, max_length=500)
    context: str = Field(default="general", pattern="^(general|sales|marketing|support)$")


class EmailConfig(BaseModel):
    smtp_host: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port: int = int(os.getenv("SMTP_PORT", "587"))
    smtp_user: str = os.getenv("SMTP_USER", "")
    smtp_password: str = os.getenv("SMTP_PASSWORD", "")
    from_email: str = os.getenv("SMTP_FROM", "no-reply@gabanilogistics.com")
    support_email: str = os.getenv("SUPPORT_EMAIL", "support@gabanistore.com")
    admin_email: str = os.getenv("ADMIN_EMAIL", "admin@gabanilogistics.com")


# ============================================================
# AI Bot Responses (Enhanced)
# ============================================================
BOT_RESPONSES = {
    "pricing": [
        "Our pricing plans start at $19/month for carriers and $29/month for brokers and shippers. The Pro plan at $49/month is our most popular!",
        "We offer flexible plans starting from $19/month. Would you like a detailed quote based on your fleet size?",
        "You can see all our pricing details on the Pricing page. We also offer volume discounts for larger fleets and annual billing with 15% savings."
    ],
    "demo": [
        "I'd be happy to schedule a demo for you! Please provide your email and preferred date, and our sales team will reach out within 24 hours.",
        "We'd love to show you the platform in action! Our team typically schedules demos within 1-2 business days. What time works best for you?"
    ],
    "trial": [
        "Yes! All new users get a 14-day free trial with full access to all features. No credit card required.",
        "Absolutely! You can start your free trial directly on the pricing page. The trial includes all Pro features."
    ],
    "features": [
        "Our platform includes real-time load matching, AI-powered rate insights, automated dispatch, and a full suite of AI bots for operations, finance, safety, and customer service.",
        "We have 20+ AI bots including Freight Broker, Operations Manager, Finance Bot, Safety Manager, Legal Consultant, and more. The full bot package is available for $8/month."
    ],
    "canada": [
        "Yes! We have full support for Canadian freight with MapleLoad Canada integration. We handle cross-border shipments between Canada and the US, including customs documentation.",
        "Our MapleLoad Canada bot specializes in Canadian freight, including Canadian market rates, carrier verification, and cross-border compliance."
    ],
    "payment": [
        "We accept all major credit cards, bank transfers, and factoring services. SUDAPAY is available for Sudanese Pound (SDG) payments with real-time settlement.",
        "You can pay via credit card, bank transfer, or factoring. All payments are processed securely through our PCI-compliant gateway."
    ],
    "support": [
        "Our customer support team is available 24/7. You can email support@gtslogistics.com, call +1 (888) 364-1189, or use the chat for immediate assistance.",
        "We're here to help! Average response time is under 2 hours for email, and under 5 minutes for chat during business hours."
    ],
    "integration": [
        "We integrate with QuickBooks, Salesforce, Google Maps, SUDAPAY, and FMCSA systems. API access is included with Pro and Premium plans.",
        "Yes! Our platform offers API integration for custom workflows. API access is available on Pro and Premium plans starting at $49/month."
    ],
    "fleet": [
        "Our TMS platform supports fleets of all sizes. The Professional plan supports up to 40 vehicles, and Enterprise supports unlimited fleets with custom pricing.",
        "We offer vehicle-based pricing: $2/vehicle for up to 5 vehicles, $1.5/vehicle for 6-20 vehicles, and $1/vehicle for 20+ vehicles."
    ],
    "general": [
        "Thanks for reaching out! Our team will get back to you shortly. In the meantime, you can also email sales@gtslogistics.com for immediate assistance.",
        "I'm here to help! Could you tell me more about what you're looking for? Are you a carrier, broker, or shipper?",
        "Great question! Let me connect you with the right team member. What's the best way to reach you?"
    ]
}


def get_bot_response(message: str) -> str:
    """Intelligent bot response based on message content"""
    message_lower = message.lower()
    
    # Check for multiple keywords to improve accuracy
    if any(k in message_lower for k in ["price", "pricing", "cost", "plan", "subscription", "monthly", "annual", "fee", "rate"]):
        responses = BOT_RESPONSES["pricing"]
    elif any(k in message_lower for k in ["demo", "show", "see", "walkthrough", "presentation", "tour"]):
        responses = BOT_RESPONSES["demo"]
    elif any(k in message_lower for k in ["trial", "free", "test", "try", "sample"]):
        responses = BOT_RESPONSES["trial"]
    elif any(k in message_lower for k in ["feature", "load board", "ai bot", "bot", "automation", "tool", "capability"]):
        responses = BOT_RESPONSES["features"]
    elif any(k in message_lower for k in ["canada", "mapleload", "cross-border", "international", "customs"]):
        responses = BOT_RESPONSES["canada"]
    elif any(k in message_lower for k in ["payment", "pay", "credit card", "invoice", "billing", "factoring", "card"]):
        responses = BOT_RESPONSES["payment"]
    elif any(k in message_lower for k in ["support", "help", "issue", "problem", "error", "trouble", "assist"]):
        responses = BOT_RESPONSES["support"]
    elif any(k in message_lower for k in ["integration", "api", "connect", "sync", "third-party", "software"]):
        responses = BOT_RESPONSES["integration"]
    elif any(k in message_lower for k in ["fleet", "vehicle", "truck", "carrier fleet", "fleet size"]):
        responses = BOT_RESPONSES["fleet"]
    else:
        responses = BOT_RESPONSES["general"]
    
    return random.choice(responses)


# ============================================================
# Email Functions
# ============================================================
def send_email_notification(form: ContactForm) -> bool:
    """Send email notification for contact form submission"""
    config = EmailConfig()
    
    if not config.smtp_user or not config.smtp_password:
        logger.warning("SMTP not configured. Email will not be sent.")
        return False
    
    try:
        # Create HTML email
        msg = MIMEMultipart("alternative")
        msg['From'] = config.from_email
        msg['To'] = config.support_email
        msg['Subject'] = f"[GTS Contact] {form.inquiryType.upper()} - {form.name}"
        msg['Reply-To'] = form.email
        
        # Plain text version
        text_body = f"""
        New contact form submission from {form.name}
        
        ========================================
        CONTACT DETAILS
        ========================================
        Name: {form.name}
        Email: {form.email}
        Phone: {form.phone or 'Not provided'}
        Company: {form.company or 'Not provided'}
        Inquiry Type: {form.inquiryType}
        Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        
        ========================================
        MESSAGE
        ========================================
        {form.message}
        
        ---
        This message was sent from the GTS Logistics contact form.
        """
        
        # HTML version
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #d32f2f;">New Contact Form Submission</h2>
            
            <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                <tr style="background: #f5f5f5;">
                    <th style="padding: 10px; text-align: left;">Field</th>
                    <th style="padding: 10px; text-align: left;">Value</th>
                </tr>
                <tr>
                    <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Name</strong></td>
                    <td style="padding: 8px; border-bottom: 1px solid #ddd;">{form.name}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Email</strong></td>
                    <td style="padding: 8px; border-bottom: 1px solid #ddd;"><a href="mailto:{form.email}">{form.email}</a></td>
                </tr>
                <tr>
                    <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Phone</strong></td>
                    <td style="padding: 8px; border-bottom: 1px solid #ddd;">{form.phone or 'Not provided'}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Company</strong></td>
                    <td style="padding: 8px; border-bottom: 1px solid #ddd;">{form.company or 'Not provided'}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Inquiry Type</strong></td>
                    <td style="padding: 8px; border-bottom: 1px solid #ddd;">
                        <span style="background: #d32f2f20; color: #d32f2f; padding: 3px 8px; border-radius: 12px;">
                            {form.inquiryType.upper()}
                        </span>
                    </td>
                </tr>
                <tr>
                    <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Time</strong></td>
                    <td style="padding: 8px; border-bottom: 1px solid #ddd;">{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</td>
                </tr>
            </table>
            
            <div style="background: #f9f9f9; padding: 15px; border-radius: 8px; margin: 20px 0;">
                <h3 style="margin-top: 0;">Message:</h3>
                <p style="white-space: pre-wrap;">{form.message}</p>
            </div>
            
            <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
            <p style="color: #666; font-size: 12px;">
                This message was sent from the GTS Logistics contact form.
                <br>Reply to: <a href="mailto:{form.email}">{form.email}</a>
            </p>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(text_body, 'plain'))
        msg.attach(MIMEText(html_body, 'html'))
        
        # Send email
        with smtplib.SMTP(config.smtp_host, config.smtp_port) as server:
            server.starttls()
            server.login(config.smtp_user, config.smtp_password)
            server.send_message(msg)
        
        logger.info(f"Contact form email sent for {form.email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send contact email: {e}")
        return False


def send_auto_reply(form: ContactForm) -> bool:
    """Send auto-reply to the user"""
    config = EmailConfig()
    
    if not config.smtp_user or not config.smtp_password:
        return False
    
    try:
        msg = MIMEMultipart("alternative")
        msg['From'] = config.from_email
        msg['To'] = form.email
        msg['Subject'] = "Thank you for contacting GTS Logistics"
        
        text_body = f"""
        Hello {form.name},
        
        Thank you for reaching out to GTS Logistics. We have received your message and will get back to you within 24 hours.
        
        Your reference: {datetime.now().strftime('%Y%m%d')}-{form.name[:3].upper()}
        
        In the meantime, you can:
        - Visit our Pricing page for plan details: https://gtslogistics.com/pricing
        - Check our Resources for guides and tutorials: https://gtslogistics.com/resources
        - Chat with our AI assistant on our website
        
        Best regards,
        GTS Logistics Support Team
        """
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #d32f2f;">Thank You for Contacting GTS Logistics</h2>
            <p>Hello <strong>{form.name}</strong>,</p>
            <p>Thank you for reaching out. We have received your message and will respond within <strong>24 hours</strong>.</p>
            
            <div style="background: #f5f5f5; padding: 10px; border-radius: 5px; margin: 20px 0;">
                <p><strong>Reference:</strong> {datetime.now().strftime('%Y%m%d')}-{form.name[:3].upper()}</p>
                <p><strong>Inquiry Type:</strong> {form.inquiryType}</p>
            </div>
            
            <p>In the meantime, here are some helpful resources:</p>
            <ul>
                <li><a href="https://gtslogistics.com/pricing">Pricing Plans</a> - Compare our plans</li>
                <li><a href="https://gtslogistics.com/resources">Resources</a> - Guides and tutorials</li>
                <li><a href="https://gtslogistics.com/ai-bots">AI Bots</a> - Learn about our AI tools</li>
            </ul>
            
            <p>You can also chat with our AI assistant on our website for immediate answers.</p>
            
            <hr style="border: none; border-top: 1px solid #ddd;">
            <p style="color: #666; font-size: 12px;">
                GTS Logistics - Gabani Transport Solutions<br>
                <a href="https://gtslogistics.com">gtslogistics.com</a> | support@gtslogistics.com | +1 (888) 364-1189
            </p>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(text_body, 'plain'))
        msg.attach(MIMEText(html_body, 'html'))
        
        with smtplib.SMTP(config.smtp_host, config.smtp_port) as server:
            server.starttls()
            server.login(config.smtp_user, config.smtp_password)
            server.send_message(msg)
        
        logger.info(f"Auto-reply sent to {form.email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send auto-reply: {e}")
        return False


# ============================================================
# API Endpoints
# ============================================================
@router.post("/contact")
@limiter.limit("5/minute")
async def submit_contact(
    form: ContactForm,
    background_tasks: BackgroundTasks,
    request: Request
):
    """Submit contact form and send email notifications"""
    try:
        # Log the submission
        logger.info(f"Contact form submission from {form.email} - Type: {form.inquiryType}")
        
        # Send email to support in background
        background_tasks.add_task(send_email_notification, form)
        
        # Send auto-reply to user in background
        background_tasks.add_task(send_auto_reply, form)
        
        # Return success response
        return {
            "success": True,
            "message": "Your message has been sent. We'll get back to you within 24 hours.",
            "data": {
                "name": form.name,
                "email": form.email,
                "inquiryType": form.inquiryType,
                "submitted_at": datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Contact form error: {e}")
        raise HTTPException(status_code=500, detail="Failed to send message. Please try again later.")


@router.post("/chat")
@limiter.limit("10/minute")
async def chat_bot(chat: ChatMessage):
    """AI bot chat endpoint"""
    try:
        # Get intelligent response
        response = get_bot_response(chat.message)
        
        # Log the interaction
        logger.info(f"Chat interaction: {chat.message[:50]}... -> {response[:50]}...")
        
        return {
            "success": True,
            "reply": response,
            "context": chat.context,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        return {
            "success": False,
            "reply": "Sorry, I'm having trouble connecting. Please try again or email us directly at support@gtslogistics.com."
        }


@router.get("/contact/config")
@limiter.limit("30/minute")
async def get_contact_config():
    """Get contact configuration (for frontend)"""
    return {
        "support_email": "support@gtslogistics.com",
        "sales_email": "sales@gtslogistics.com",
        "marketing_email": "marketing@gtslogistics.com",
        "phone": "+1 (888) 364-1189",
        "business_hours": "Monday-Friday, 9:00 AM - 6:00 PM EST",
        "response_time": "24 hours",
        "emergency_support": "24/7 for active customers"
    }
        "We have AI bots for operations, finance, safety, and customer service. The full bot package is available for $8/month."
    ],
    "canada": [
        "Yes, we have full support for Canadian freight with MapleLoad Canada integration. We handle cross-border shipments!",
        "Our MapleLoad Canada bot specializes in Canadian freight, including cross-border shipments and Canadian market rates."
    ],
    "payment": [
        "We accept all major credit cards, bank transfers, and factoring services. SUDAPAY is available for Sudanese Pound payments.",
        "You can pay via credit card, bank transfer, or factoring. All payments are processed securely."
    ],
    "support": [
        "Our customer support team is available 24/7. You can email support@gtslogistics.com or call +1 (888) 364-1189.",
        "We're here to help! You can reach us via email, phone, or chat. Our average response time is under 2 hours."
    ],
    "general": [
        "Thanks for reaching out! Our team will get back to you shortly. In the meantime, you can also email sales@gtslogistics.com.",
        "I'm here to help! Could you tell me more about what you're looking for?",
        "Great question! Let me connect you with the right team member."
    ]
}

def get_bot_response(message: str) -> str:
    """Get AI bot response based on keywords"""
    import random
    message_lower = message.lower()
    
    # Check for keywords
    if any(k in message_lower for k in ["price", "pricing", "cost", "plan", "subscription", "monthly", "annual"]):
        responses = BOT_RESPONSES["pricing"]
    elif any(k in message_lower for k in ["demo", "show", "see", "walkthrough"]):
        responses = BOT_RESPONSES["demo"]
    elif any(k in message_lower for k in ["trial", "free", "test"]):
        responses = BOT_RESPONSES["trial"]
    elif any(k in message_lower for k in ["feature", "load board", "ai bot", "bot", "automation"]):
        responses = BOT_RESPONSES["features"]
    elif any(k in message_lower for k in ["canada", "mapleload", "cross-border"]):
        responses = BOT_RESPONSES["canada"]
    elif any(k in message_lower for k in ["payment", "pay", "credit card", "invoice", "billing"]):
        responses = BOT_RESPONSES["payment"]
    elif any(k in message_lower for k in ["support", "help", "issue", "problem", "error"]):
        responses = BOT_RESPONSES["support"]
    else:
        responses = BOT_RESPONSES["general"]
    
    return random.choice(responses)

def send_email_notification(form: ContactForm):
    """Send email notification for contact form submission"""
    try:
        # Create email message
        msg = MIMEMultipart()
        msg['From'] = SMTP_FROM
        msg['To'] = SUPPORT_EMAIL
        msg['Subject'] = f"[GTS Contact] {form.inquiryType.upper()} - {form.name}"
        
        body = f"""
        New contact form submission from {form.name}
        
        Name: {form.name}
        Email: {form.email}
        Phone: {form.phone or 'Not provided'}
        Company: {form.company or 'Not provided'}
        Inquiry Type: {form.inquiryType}
        
        Message:
        {form.message}
        
        ---
        This message was sent from the GTS Logistics contact form.
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Send email
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
        
        logger.info(f"Contact form email sent for {form.email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send contact email: {e}")
        return False

@router.post("/contact")
async def submit_contact(form: ContactForm, background_tasks: BackgroundTasks):
    """Submit contact form and send email notification"""
    try:
        # Send email in background
        background_tasks.add_task(send_email_notification, form)
        
        # Return success response
        return {
            "success": True,
            "message": "Your message has been sent. We'll get back to you within 24 hours.",
            "data": {
                "name": form.name,
                "email": form.email,
                "inquiryType": form.inquiryType
            }
        }
    except Exception as e:
        logger.error(f"Contact form error: {e}")
        raise HTTPException(status_code=500, detail="Failed to send message")

@router.post("/chat")
async def chat_bot(chat: ChatMessage):
    """AI bot chat endpoint"""
    try:
        response = get_bot_response(chat.message)
        return {
            "success": True,
            "reply": response,
            "context": chat.context
        }
    except Exception as e:
        logger.error(f"Chat error: {e}")
        return {
            "success": False,
            "reply": "Sorry, I'm having trouble connecting. Please try again or email us directly."
        }