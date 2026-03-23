"""
Subscription system models
"""
from sqlalchemy import Column, String, Boolean, DateTime, JSON, ForeignKey, Integer, UUID, DECIMAL, TEXT
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.database.base import Base
import uuid



# ✅ Plan Model - REMOVED (use canonical from backend/billing/models.py)
# The Plan model was moved to backend/billing/models.py with PlanEntitlement relationships
# for subscription system management. Do not redefine here.


class Role(Base):
    """User roles model"""
    __tablename__ = "roles"

    key = Column(String(50), primary_key=True)
    name = Column(String(100), nullable=True)  # For compatibility with existing table
    name_ar = Column(String(100), nullable=False)
    name_en = Column(String(100), nullable=False)
    permissions = Column(JSON, default=list)
    # NOTE: features and data_scope columns not yet added to production database
    # features = Column(JSON, default=list, nullable=True)  # Feature flags for UI access
    # data_scope = Column(String(20), default="tenant_only", nullable=True)  # "global" or "tenant_only"
    is_system = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=True)

    # Relationships
    # DEV: Disabled - User.role is a string field, not a ForeignKey relationship
    # users = relationship("User", back_populates="role")

    def __repr__(self):
        return f"<Role {self.key}>"


# Tenant is now defined in backend/models/tenant.py - this copy is removed to avoid conflicts
# The canonical Tenant model is in backend/models/tenant.py



# ✅ User Model - REMOVED (use canonical from backend/models/user.py)
# The User model was moved to backend/models/user.py with proper tenant scoping
# for multi-tenant SaaS architecture. Do not redefine here.


class Bot(Base):
    """AI Bots model"""
    __tablename__ = "ai_bots"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    key = Column(String(50), unique=True, nullable=False)
    name_ar = Column(String(100), nullable=False)
    name_en = Column(String(100), nullable=False)
    description = Column(TEXT, nullable=True)
    type = Column(String(20), default='user')  # 'user' or 'system'
    category = Column(String(50), nullable=True)
    icon = Column(String(10), nullable=True)
    email_local_part = Column(String(100), nullable=True)
    version = Column(String(20), default='1.0.0')
    status = Column(String(20), default='active')
    availability = Column(String(50), default='all')
    endpoints = Column(JSON, default=dict)
    features = Column(JSON, default=list)
    dependencies = Column(JSON, default=list)
    config = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    # DEV: Disabled - BotRun table uses bot_registry FK, not ai_bots
    # bot_runs = relationship("BotRun", back_populates="bot")
    policies = relationship("BotPolicy", back_populates="bot")
    email_identities = relationship("BotEmailIdentity", back_populates="bot")
    email_logs = relationship("EmailLog", back_populates="bot")

    def __repr__(self):
        return f"<Bot {self.key}>"


class BotPolicy(Base):
    """Bot policies model"""
    __tablename__ = "bot_policies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    bot_key = Column(String(50), ForeignKey("ai_bots.key"), nullable=False)
    required_features = Column(JSON, default=list)
    allowed_roles = Column(JSON, default=list)
    required_plan_keys = Column(JSON, default=list)
    max_runs_per_day = Column(Integer, default=100)
    requires_approval = Column(Boolean, default=False)
    cost_per_run = Column(DECIMAL(10, 2), nullable=True)
    visibility = Column(String(20), default='visible')
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    bot = relationship("Bot", back_populates="policies")

    def __repr__(self):
        return f"<BotPolicy {self.bot_key}>"



# ✅ BotRun Model - REMOVED (use canonical from backend/models/bot_os.py)
# The BotRun model was moved to backend/models/bot_os.py for bot orchestration
# This file should NOT redefine it. It has different schema than the canonical one.


class TenantEmailConfig(Base):
    """Tenant email configuration model"""
    __tablename__ = "tenant_email_config"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, unique=True)
    email_mode = Column(String(20), default='managed')  # 'byod' or 'managed'
    smtp_config = Column(JSON, nullable=True)
    domain = Column(String(255), nullable=True)
    aliases = Column(JSON, default=list)
    mailboxes = Column(JSON, default=list)
    daily_limit = Column(Integer, default=1000)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    tenant = relationship("Tenant")  # No back_populates - Tenant.email_config_rel not defined

    def __repr__(self):
        return f"<TenantEmailConfig {self.tenant_id} - {self.email_mode}>"


class BotEmailIdentity(Base):
    """Bot email identities model"""
    __tablename__ = "bot_email_identities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    bot_key = Column(String(50), ForeignKey("ai_bots.key"), nullable=False)
    email_address = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    tenant = relationship("Tenant")  # No back_populates - Tenant.bot_email_identities not defined
    bot = relationship("Bot", back_populates="email_identities")

    __table_args__ = (
        __import__('sqlalchemy').UniqueConstraint('tenant_id', 'bot_key', name='uq_tenant_bot_email'),
    )

    def __repr__(self):
        return f"<BotEmailIdentity {self.bot_key} - {self.email_address}>"


class EmailLog(Base):
    """Email logs model"""
    __tablename__ = "email_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    bot_key = Column(String(50), ForeignKey("ai_bots.key"), nullable=True)
    from_email = Column(String(255), nullable=True)
    to_email = Column(String(255), nullable=True)
    subject = Column(String(500), nullable=True)
    status = Column(String(20), default='sent')
    error_message = Column(TEXT, nullable=True)
    sent_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    tenant = relationship("Tenant")  # No back_populates - Tenant.email_logs not defined
    bot = relationship("Bot", back_populates="email_logs")

    def __repr__(self):
        return f"<EmailLog {self.from_email} -> {self.to_email}>"


# Import existing models for relationships
# (No external relationships needed for subscription system)
