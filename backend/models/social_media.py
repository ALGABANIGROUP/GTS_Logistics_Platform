"""
Social Media Models
Database models for social media integration and management
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Float, JSON, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum
from backend.database.base import Base


class SocialPlatform(str, Enum):
    """Social media platforms"""
    LINKEDIN = "linkedin"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"
    YOUTUBE = "youtube"


class PostStatus(str, Enum):
    """Post status"""
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    PUBLISHING = "publishing"
    PUBLISHED = "published"
    FAILED = "failed"
    DELETED = "deleted"


class SocialMediaAccount(Base):
    """Social media account connections"""
    __tablename__: str = "social_media_accounts"

    id = Column(Integer, primary_key=True, index=True)
    platform = Column(SQLEnum(SocialPlatform), nullable=False, index=True)
    account_name = Column(String(255), nullable=False)
    account_id = Column(String(255), nullable=True)
    display_name = Column(String(255), nullable=True)
    profile_url = Column(String(512), nullable=True)
    
    # API credentials (encrypted in production)
    api_key = Column(Text, nullable=True)
    api_secret = Column(Text, nullable=True)
    access_token = Column(Text, nullable=True)
    access_token_secret = Column(Text, nullable=True)
    refresh_token = Column(Text, nullable=True)
    
    # Status
    is_connected = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    last_sync = Column(DateTime, nullable=True)
    last_post = Column(DateTime, nullable=True)
    
    # Metrics
    followers_count = Column(Integer, default=0)
    following_count = Column(Integer, default=0)
    posts_count = Column(Integer, default=0)
    
    # Settings
    auto_posting_enabled = Column(Boolean, default=False)
    posting_schedule = Column(JSON, nullable=True)  # {"time": "09:00", "days": ["monday", "wednesday"]}
    default_hashtags = Column(JSON, nullable=True)  # ["logistics", "freight"]
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    
    # Relationships
    posts = relationship("SocialMediaPost", back_populates="account")
    analytics = relationship("SocialMediaAnalytics", back_populates="account")


class SocialMediaPost(Base):
    """Social media posts"""
    __tablename__: str = "social_media_posts"

    id = Column(Integer, primary_key=True, index=True)
    
    # Account
    account_id = Column(Integer, ForeignKey('social_media_accounts.id'), nullable=False)
    platform = Column(SQLEnum(SocialPlatform), nullable=False, index=True)
    
    # Content
    title = Column(String(500), nullable=True)
    content = Column(Text, nullable=False)
    content_type = Column(String(50), default="text")  # text, image, video, link
    media_urls = Column(JSON, nullable=True)  # ["url1", "url2"]
    link_url = Column(String(512), nullable=True)
    hashtags = Column(JSON, nullable=True)  # ["tag1", "tag2"]
    
    # Scheduling
    status = Column(SQLEnum(PostStatus), default=PostStatus.DRAFT, index=True)
    scheduled_time = Column(DateTime, nullable=True)
    published_time = Column(DateTime, nullable=True)
    
    # Platform-specific IDs
    platform_post_id = Column(String(255), nullable=True)
    platform_url = Column(String(512), nullable=True)
    
    # Engagement metrics
    likes_count = Column(Integer, default=0)
    comments_count = Column(Integer, default=0)
    shares_count = Column(Integer, default=0)
    clicks_count = Column(Integer, default=0)
    impressions = Column(Integer, default=0)
    reach = Column(Integer, default=0)
    engagement_rate = Column(Float, default=0.0)
    
    # Error handling
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    
    # Relationships
    account = relationship("SocialMediaAccount", back_populates="posts")


class SocialMediaAnalytics(Base):
    """Social media analytics and metrics"""
    __tablename__: str = "social_media_analytics"

    id = Column(Integer, primary_key=True, index=True)
    
    # Account
    account_id = Column(Integer, ForeignKey('social_media_accounts.id'), nullable=False)
    platform = Column(SQLEnum(SocialPlatform), nullable=False, index=True)
    
    # Time period
    date = Column(DateTime, nullable=False, index=True)
    period_type = Column(String(20), default="daily")  # daily, weekly, monthly
    
    # Audience metrics
    followers_count = Column(Integer, default=0)
    followers_change = Column(Integer, default=0)
    following_count = Column(Integer, default=0)
    
    # Engagement metrics
    total_likes = Column(Integer, default=0)
    total_comments = Column(Integer, default=0)
    total_shares = Column(Integer, default=0)
    total_clicks = Column(Integer, default=0)
    total_impressions = Column(Integer, default=0)
    total_reach = Column(Integer, default=0)
    
    # Calculated metrics
    engagement_rate = Column(Float, default=0.0)
    growth_rate = Column(Float, default=0.0)
    avg_engagement_per_post = Column(Float, default=0.0)
    
    # Post metrics
    posts_count = Column(Integer, default=0)
    best_post_id = Column(Integer, ForeignKey('social_media_posts.id'), nullable=True)
    best_post_engagement = Column(Float, default=0.0)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    account = relationship("SocialMediaAccount", back_populates="analytics")


class SocialMediaTemplate(Base):
    """Content templates for social media posts"""
    __tablename__: str = "social_media_templates"

    id = Column(Integer, primary_key=True, index=True)
    
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True)  # announcement, promotion, news, etc.
    
    # Template content
    content_template = Column(Text, nullable=False)
    variables = Column(JSON, nullable=True)  # ["company_name", "service_name", "url"]
    
    # Target platforms
    platforms = Column(JSON, nullable=True)  # ["linkedin", "twitter"]
    
    # Settings
    default_hashtags = Column(JSON, nullable=True)
    include_link = Column(Boolean, default=False)
    include_image = Column(Boolean, default=False)
    
    # Usage tracking
    usage_count = Column(Integer, default=0)
    last_used = Column(DateTime, nullable=True)
    
    # Metadata
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'), nullable=True)


class SocialMediaSettings(Base):
    """Global social media settings"""
    __tablename__: str = "social_media_settings"

    id = Column(Integer, primary_key=True, index=True)
    
    # Auto-posting settings
    auto_posting_enabled = Column(Boolean, default=False)
    auto_post_new_blogs = Column(Boolean, default=True)
    auto_post_new_services = Column(Boolean, default=True)
    auto_post_company_updates = Column(Boolean, default=True)
    
    # Default scheduling
    default_posting_times = Column(JSON, nullable=True)  # {"morning": "09:00", "afternoon": "14:00"}
    optimal_posting_enabled = Column(Boolean, default=True)
    
    # Content rules
    min_content_length = Column(Integer, default=50)
    max_content_length = Column(Integer, default=280)
    require_hashtags = Column(Boolean, default=True)
    max_hashtags = Column(Integer, default=5)
    
    # Rate limiting
    max_posts_per_day = Column(Integer, default=10)
    min_post_interval_minutes = Column(Integer, default=60)
    
    # Monitoring
    analytics_enabled = Column(Boolean, default=True)
    daily_reports_enabled = Column(Boolean, default=True)
    report_recipients = Column(JSON, nullable=True)  # ["admin@example.com"]
    
    # Metadata
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = Column(Integer, ForeignKey('users.id'), nullable=True)

