"""
API Connections Model
For managing external platform integrations (Social Media, Payment, ERP, etc.)
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Enum as SQLEnum, JSON
from sqlalchemy.sql import func
from datetime import datetime
import enum

from backend.database.config import Base


class ConnectionType(str, enum.Enum):
    """Types of API connection authentication"""
    API_KEY = "api_key"
    OAUTH2 = "oauth2"
    BASIC_AUTH = "basic_auth"
    BEARER_TOKEN = "bearer_token"
    JWT = "jwt"
    CUSTOM = "custom"


class PlatformCategory(str, enum.Enum):
    """Categories of platform integrations"""
    SOCIAL_MEDIA = "social_media"
    PAYMENT = "payment"
    ERP = "erp"
    CRM = "crm"
    LOGISTICS = "logistics"
    ANALYTICS = "analytics"
    COMMUNICATION = "communication"
    STORAGE = "storage"
    OTHER = "other"


class APIConnection(Base):
    """Model for storing external API connections"""
    
    __tablename__ = "api_connections"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Platform information
    platform_name = Column(String(255), nullable=False, index=True)
    platform_category = Column(SQLEnum(PlatformCategory), nullable=False, default=PlatformCategory.OTHER)
    description = Column(Text, nullable=True)
    
    # API configuration
    api_url = Column(String(500), nullable=False)
    connection_type = Column(SQLEnum(ConnectionType), nullable=False, default=ConnectionType.API_KEY)
    
    # Authentication details (encrypted in production)
    api_key = Column(Text, nullable=True)
    api_secret = Column(Text, nullable=True)
    access_token = Column(Text, nullable=True)
    refresh_token = Column(Text, nullable=True)
    
    # OAuth specific
    client_id = Column(String(255), nullable=True)
    client_secret = Column(Text, nullable=True)
    oauth_callback_url = Column(String(500), nullable=True)
    
    # Additional configuration
    headers = Column(JSON, nullable=True)  # Custom headers as JSON
    query_params = Column(JSON, nullable=True)  # Default query params as JSON
    extra_config = Column(JSON, nullable=True)  # Any additional config as JSON
    
    # Status and health
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    last_tested_at = Column(DateTime, nullable=True)
    last_test_status = Column(String(50), nullable=True)  # success, failed, pending
    last_test_message = Column(Text, nullable=True)
    
    # Usage tracking
    total_requests = Column(Integer, default=0, nullable=False)
    successful_requests = Column(Integer, default=0, nullable=False)
    failed_requests = Column(Integer, default=0, nullable=False)
    last_used_at = Column(DateTime, nullable=True)
    
    # Metadata
    created_by = Column(Integer, nullable=True)  # User ID
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    def to_dict(self, include_secrets: bool = False) -> dict:
        """Convert to dictionary with optional secret masking"""
        data = {
            "id": self.id,
            "platform_name": self.platform_name,
            "platform_category": self.platform_category.value if self.platform_category else None,
            "description": self.description,
            "api_url": self.api_url,
            "connection_type": self.connection_type.value if self.connection_type else None,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "last_tested_at": self.last_tested_at.isoformat() if self.last_tested_at else None,
            "last_test_status": self.last_test_status,
            "last_test_message": self.last_test_message,
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "last_used_at": self.last_used_at.isoformat() if self.last_used_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "headers": self.headers,
            "query_params": self.query_params,
            "extra_config": self.extra_config,
        }
        
        if include_secrets:
            # Only include secrets if explicitly requested (for super admin)
            data.update({
                "api_key": self.api_key,
                "api_secret": self.api_secret,
                "access_token": self.access_token,
                "refresh_token": self.refresh_token,
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "oauth_callback_url": self.oauth_callback_url,
            })
        else:
            # Mask secrets
            data.update({
                "api_key": self._mask_secret(self.api_key),
                "api_secret": self._mask_secret(self.api_secret),
                "access_token": self._mask_secret(self.access_token),
                "refresh_token": self._mask_secret(self.refresh_token),
                "client_id": self.client_id,  # Client ID is not secret
                "client_secret": self._mask_secret(self.client_secret),
                "oauth_callback_url": self.oauth_callback_url,
            })
        
        return data
    
    @staticmethod
    def _mask_secret(value: str) -> str:
        """Mask secret values for display"""
        if not value:
            return None
        if len(value) <= 8:
            return "****"
        return value[:4] + "****" + value[-4:]
    
    def get_success_rate(self) -> float:
        """Calculate API success rate"""
        if self.total_requests == 0:
            return 0.0
        return (self.successful_requests / self.total_requests) * 100
