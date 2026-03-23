"""
Support System Models
Complete ticketing system with SLA management
Defines ticket, agent, SLA, comments, and analytics entities.
"""

from datetime import datetime, timedelta
from sqlalchemy import (
    Column, String, Integer, Text, DateTime, 
    ForeignKey, Boolean, Enum, Float, JSON
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from backend.database.base import Base


# ============================================
# ENUMS
# ============================================

class TicketStatus(str, enum.Enum):
    """Ticket status enumeration"""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    WAITING_CUSTOMER = "waiting_customer"
    RESOLVED = "resolved"
    CLOSED = "closed"
    REOPENED = "reopened"


class TicketPriority(str, enum.Enum):
    """Ticket priority levels"""
    CRITICAL = "critical"      # 1 hour response, 4 hours resolution
    HIGH = "high"              # 2 hours response, 8 hours resolution
    MEDIUM = "medium"          # 4 hours response, 24 hours resolution
    LOW = "low"                # 8 hours response, 48 hours resolution


class TicketCategory(str, enum.Enum):
    """Ticket categories"""
    TECHNICAL = "technical"
    BILLING = "billing"
    ACCOUNT = "account"
    GENERAL = "general"
    FEATURE_REQUEST = "feature_request"
    BUG_REPORT = "bug_report"


class SLAStatus(str, enum.Enum):
    """SLA compliance status"""
    COMPLIANT = "compliant"
    AT_RISK = "at_risk"
    BREACHED = "breached"


class ChannelType(str, enum.Enum):
    """Support channel types"""
    EMAIL = "email"
    LIVE_CHAT = "live_chat"
    PHONE = "phone"
    WHATSAPP = "whatsapp"
    TELEGRAM = "telegram"
    PORTAL = "portal"


# ============================================
# MAIN MODELS
# ============================================

class SupportTicket(Base):
    """Support ticket model"""
    __tablename__ = "support_tickets"

    id = Column(Integer, primary_key=True, index=True)
    ticket_number = Column(String(20), unique=True, index=True)  # e.g., "TK-001234"
    
    # Customer info
    customer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    customer = relationship("backend.models.user.User", foreign_keys=[customer_id], backref="support_tickets")
    customer_email = Column(String(255), nullable=False)
    customer_name = Column(String(255), nullable=False)
    
    # Ticket details
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(50), nullable=False, default=TicketCategory.GENERAL)
    priority = Column(String(20), nullable=False, default=TicketPriority.MEDIUM)
    status = Column(String(20), nullable=False, default=TicketStatus.OPEN)
    
    # Assignment
    assigned_to = Column(Integer, ForeignKey("support_agents.id"), nullable=True)
    assigned_agent = relationship("SupportAgent", foreign_keys=[assigned_to], backref="assigned_tickets")
    
    # Channels
    channel = Column(String(20), nullable=False, default=ChannelType.PORTAL)
    original_channel_id = Column(String(255), nullable=True)  # e.g., email ID, chat ID
    
    # SLA
    sla_level_id = Column(Integer, ForeignKey("sla_levels.id"), nullable=False)
    sla_level = relationship("SLALevel", backref="tickets")
    
    sla_response_due = Column(DateTime, nullable=True)
    sla_resolution_due = Column(DateTime, nullable=True)
    sla_status = Column(String(20), nullable=False, default=SLAStatus.COMPLIANT)
    
    # Time tracking
    first_response_at = Column(DateTime, nullable=True)
    last_update_at = Column(DateTime, nullable=True, onupdate=func.now())
    resolved_at = Column(DateTime, nullable=True)
    closed_at = Column(DateTime, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())
    
    # Tags and custom fields
    tags = Column(JSON, nullable=True, default=[])
    custom_fields = Column(JSON, nullable=True, default={})
    
    # Satisfaction
    satisfaction_score = Column(Integer, nullable=True)  # 1-5
    satisfaction_comment = Column(Text, nullable=True)
    
    # Attachments count
    attachment_count = Column(Integer, default=0)
    
    # Activity tracking
    activity_log = relationship("TicketActivity", cascade="all, delete-orphan", back_populates="ticket")
    comments = relationship("TicketComment", cascade="all, delete-orphan", back_populates="ticket")
    history = relationship("TicketHistory", cascade="all, delete-orphan", back_populates="ticket")
    
    def __repr__(self):
        return f"<SupportTicket {self.ticket_number}: {self.title}>"


class SupportAgent(Base):
    """Support team agent model"""
    __tablename__ = "support_agents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    user = relationship("backend.models.user.User", backref="support_agent_profile")
    
    # Profile
    employee_id = Column(String(50), unique=True, nullable=False)
    phone = Column(String(20), nullable=True)
    timezone = Column(String(50), default="UTC")
    language = Column(String(10), default="en")
    
    # Skills and expertise
    specializations = Column(JSON, nullable=True, default=[])  # e.g., ["technical", "billing"]
    
    # Status
    is_available = Column(Boolean, default=True)
    is_online = Column(Boolean, default=False)
    
    # Performance metrics
    total_tickets_resolved = Column(Integer, default=0)
    average_resolution_time = Column(Float, default=0.0)  # in hours
    average_satisfaction_score = Column(Float, default=0.0)  # 1-5
    
    # Workload
    max_concurrent_tickets = Column(Integer, default=10)
    current_ticket_count = Column(Integer, default=0)
    
    # Availability
    working_hours_start = Column(String(5), default="09:00")  # HH:MM
    working_hours_end = Column(String(5), default="18:00")
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())
    last_active_at = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<SupportAgent {self.user.email}>"


class SLALevel(Base):
    """Service Level Agreement configuration"""
    __tablename__ = "sla_levels"

    id = Column(Integer, primary_key=True, index=True)
    
    # SLA Mapping
    priority = Column(String(20), unique=True, nullable=False)  # critical, high, medium, low
    
    # Response and Resolution times (in hours)
    response_time = Column(Integer, nullable=False)  # Max hours to first response
    resolution_time = Column(Integer, nullable=False)  # Max hours to resolution
    
    # Business hour
    apply_business_hours_only = Column(Boolean, default=False)
    
    # Escalation
    escalation_threshold = Column(Float, default=0.75)  # 75% through SLA triggers escalation
    
    # Created
    created_at = Column(DateTime, nullable=False, default=func.now())
    
    def __repr__(self):
        return f"<SLALevel {self.priority}>"


class TicketComment(Base):
    """Comment on a support ticket"""
    __tablename__ = "ticket_comments"

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("support_tickets.id"), nullable=False)
    ticket = relationship("SupportTicket", back_populates="comments")
    
    # Author
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    author = relationship("backend.models.user.User", backref="support_comments")
    author_type = Column(String(20), nullable=False)  # "customer" or "agent"
    
    # Content
    content = Column(Text, nullable=False)
    is_internal = Column(Boolean, default=False)  # Internal notes (not visible to customer)
    
    # Attachments
    attachments = relationship("TicketAttachment", cascade="all, delete-orphan", back_populates="comment")
    
    # Metadata
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<TicketComment on ticket {self.ticket_id}>"


class TicketActivity(Base):
    """Activity log for ticket changes"""
    __tablename__ = "ticket_activities"

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("support_tickets.id"), nullable=False)
    ticket = relationship("SupportTicket", back_populates="activity_log")
    
    # Activity details
    action = Column(String(100), nullable=False)  # "assigned", "status_changed", "priority_changed", etc.
    description = Column(Text, nullable=False)
    
    # Actor
    actor_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    actor = relationship("backend.models.user.User", backref="support_activities")
    
    # Change details
    old_value = Column(String(255), nullable=True)
    new_value = Column(String(255), nullable=True)
    
    # Timestamp
    created_at = Column(DateTime, nullable=False, default=func.now())
    
    def __repr__(self):
        return f"<TicketActivity {self.action} on ticket {self.ticket_id}>"


class TicketHistory(Base):
    """Complete history of ticket states"""
    __tablename__ = "ticket_history"

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("support_tickets.id"), nullable=False)
    ticket = relationship("SupportTicket", back_populates="history")
    
    # Status history
    old_status = Column(String(20), nullable=True)
    new_status = Column(String(20), nullable=False)
    
    # Priority history
    old_priority = Column(String(20), nullable=True)
    new_priority = Column(String(20), nullable=True)
    
    # Assignment history
    old_agent_id = Column(Integer, nullable=True)
    new_agent_id = Column(Integer, nullable=True)
    
    # Changed by
    changed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Timestamp
    created_at = Column(DateTime, nullable=False, default=func.now())
    
    def __repr__(self):
        return f"<TicketHistory {self.id}>"


class TicketAttachment(Base):
    """Attachments to tickets and comments"""
    __tablename__ = "ticket_attachments"

    id = Column(Integer, primary_key=True, index=True)
    
    # Relations
    ticket_id = Column(Integer, ForeignKey("support_tickets.id"), nullable=True)
    comment_id = Column(Integer, ForeignKey("ticket_comments.id"), nullable=True)
    ticket = relationship("SupportTicket")
    comment = relationship("TicketComment", back_populates="attachments")
    
    # File info
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)  # in bytes
    file_type = Column(String(100), nullable=False)  # MIME type
    
    # Uploader
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    uploader = relationship("backend.models.user.User", backref="support_attachments")
    
    # Timestamp
    created_at = Column(DateTime, nullable=False, default=func.now())
    
    def __repr__(self):
        return f"<TicketAttachment {self.filename}>"


class KnowledgeBase(Base):
    """Knowledge base articles"""
    __tablename__ = "knowledge_base"

    id = Column(Integer, primary_key=True, index=True)
    
    # Content
    title = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, index=True, nullable=False)
    content = Column(Text, nullable=False)
    summary = Column(String(500), nullable=False)
    
    # Category
    category = Column(String(100), nullable=False)  # e.g., "Getting Started", "Troubleshooting"
    tags = Column(JSON, nullable=True, default=[])
    
    # Status
    is_published = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)
    
    # Author and metadata
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    author = relationship("backend.models.user.User", backref="kb_articles")
    
    # SEO
    meta_description = Column(String(255), nullable=True)
    keywords = Column(JSON, nullable=True, default=[])
    
    # Traffic
    view_count = Column(Integer, default=0)
    helpful_votes = Column(Integer, default=0)
    unhelpful_votes = Column(Integer, default=0)
    
    # Related tickets
    related_tickets = Column(JSON, nullable=True, default=[])
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<KnowledgeBase {self.title}>"


class SupportFeedback(Base):
    """Customer feedback on support interactions"""
    __tablename__ = "support_feedback"

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("support_tickets.id"), nullable=False)
    ticket = relationship("SupportTicket", backref="feedback")
    
    # Rating
    overall_rating = Column(Integer, nullable=False)  # 1-5
    response_time_rating = Column(Integer, nullable=True)  # 1-5
    solution_quality_rating = Column(Integer, nullable=True)  # 1-5
    agent_professionalism_rating = Column(Integer, nullable=True)  # 1-5
    
    # Feedback
    comments = Column(Text, nullable=True)
    would_recommend = Column(Boolean, nullable=True)
    
    # Tags
    satisfaction_tags = Column(JSON, nullable=True, default=[])
    
    # Timestamp
    created_at = Column(DateTime, nullable=False, default=func.now())
    
    def __repr__(self):
        return f"<SupportFeedback on ticket {self.ticket_id}>"


class SupportStats(Base):
    """Daily support statistics"""
    __tablename__ = "support_stats"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(String(10), unique=True, index=True)  # YYYY-MM-DD
    
    # Ticket metrics
    tickets_created = Column(Integer, default=0)
    tickets_resolved = Column(Integer, default=0)
    tickets_reopened = Column(Integer, default=0)
    average_response_time = Column(Float, default=0.0)  # in minutes
    average_resolution_time = Column(Float, default=0.0)  # in hours
    
    # SLA metrics
    sla_compliant = Column(Integer, default=0)
    sla_breached = Column(Integer, default=0)
    sla_compliance_rate = Column(Float, default=100.0)  # percentage
    
    # Satisfaction
    average_satisfaction_score = Column(Float, default=0.0)  # 1-5
    
    # Agent metrics
    active_agents = Column(Integer, default=0)
    total_agent_hours = Column(Float, default=0.0)
    
    # Channel breakdown
    channel_breakdown = Column(JSON, nullable=True, default={})
    
    # Created
    created_at = Column(DateTime, nullable=False, default=func.now())
    
    def __repr__(self):
        return f"<SupportStats {self.date}>"


class EmailTemplate(Base):
    """Email templates for automated responses"""
    __tablename__ = "email_templates"

    id = Column(Integer, primary_key=True, index=True)
    
    # Template info
    name = Column(String(100), unique=True, nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    description = Column(String(255), nullable=True)
    
    # Template content
    subject = Column(String(255), nullable=False)
    body = Column(Text, nullable=False)
    
    # Template variables (for documentation)
    variables = Column(JSON, nullable=True, default=[])  # e.g., ["{{ticket_number}}", "{{agent_name}}"]
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Created by
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    creator = relationship("backend.models.user.User", backref="email_templates")
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<EmailTemplate {self.name}>"


class SupportEmail(Base):
    """Tracking of support-related emails"""
    __tablename__ = "support_emails"

    id = Column(Integer, primary_key=True, index=True)
    
    # Email info
    message_id = Column(String(255), unique=True, nullable=True)  # Email ID from IMAP
    ticket_id = Column(Integer, ForeignKey("support_tickets.id"), nullable=True)
    
    # Recipients
    from_email = Column(String(255), nullable=False)
    to_email = Column(String(255), nullable=False)
    cc = Column(JSON, nullable=True, default=[])
    bcc = Column(JSON, nullable=True, default=[])
    
    # Content
    subject = Column(String(255), nullable=False)
    body = Column(Text, nullable=False)
    is_html = Column(Boolean, default=True)
    
    # Status
    status = Column(String(20), default="sent")  # sent, failed, bounced
    error_message = Column(Text, nullable=True)
    
    # Attachments
    attachment_count = Column(Integer, default=0)
    
    # Timestamp
    sent_at = Column(DateTime, nullable=False, default=func.now())
    
    def __repr__(self):
        return f"<SupportEmail {self.message_id}>"

