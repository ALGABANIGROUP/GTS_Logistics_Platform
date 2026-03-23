"""Add social media tables

Revision ID: sm_002_social_media
Revises: c1c4546306e6
Create Date: 2026-01-08

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'sm_002_social_media'
down_revision = 'c1c4546306e6'
branch_labels = None
depends_on = None


def upgrade():
    """Create social media tables"""
    
    # Create social_media_accounts table
    op.create_table(
        'social_media_accounts',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('platform', sa.String(50), nullable=False),
        sa.Column('account_name', sa.String(255), nullable=False),
        sa.Column('account_id', sa.String(255), nullable=True),
        sa.Column('display_name', sa.String(255), nullable=True),
        sa.Column('profile_url', sa.String(512), nullable=True),
        
        # API credentials (encrypt in production)
        sa.Column('api_key', sa.Text(), nullable=True),
        sa.Column('api_secret', sa.Text(), nullable=True),
        sa.Column('access_token', sa.Text(), nullable=True),
        sa.Column('access_token_secret', sa.Text(), nullable=True),
        sa.Column('refresh_token', sa.Text(), nullable=True),
        
        # Status
        sa.Column('is_connected', sa.Boolean(), default=False),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('last_sync', sa.DateTime(), nullable=True),
        sa.Column('last_post', sa.DateTime(), nullable=True),
        
        # Metrics
        sa.Column('followers_count', sa.Integer(), default=0),
        sa.Column('following_count', sa.Integer(), default=0),
        sa.Column('posts_count', sa.Integer(), default=0),
        
        # Settings
        sa.Column('auto_posting_enabled', sa.Boolean(), default=False),
        sa.Column('posting_schedule', postgresql.JSON(), nullable=True),
        sa.Column('default_hashtags', postgresql.JSON(), nullable=True),
        
        # Metadata
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('created_by', sa.Integer(), sa.ForeignKey('users.id'), nullable=True)
    )
    
    # Create social_media_posts table
    op.create_table(
        'social_media_posts',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        
        # Account info
        sa.Column('account_id', sa.Integer(), sa.ForeignKey('social_media_accounts.id'), nullable=True),
        sa.Column('platform', sa.String(50), nullable=False),
        
        # Content
        sa.Column('title', sa.String(500), nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('content_type', sa.String(50), default='text'),
        sa.Column('media_urls', postgresql.JSON(), nullable=True),
        sa.Column('link_url', sa.String(512), nullable=True),
        sa.Column('hashtags', postgresql.JSON(), nullable=True),
        
        # Scheduling
        sa.Column('status', sa.String(50), default='draft'),
        sa.Column('scheduled_time', sa.DateTime(), nullable=True),
        sa.Column('published_time', sa.DateTime(), nullable=True),
        
        # Platform-specific
        sa.Column('platform_post_id', sa.String(255), nullable=True),
        sa.Column('platform_url', sa.String(512), nullable=True),
        
        # Engagement metrics
        sa.Column('likes_count', sa.Integer(), default=0),
        sa.Column('comments_count', sa.Integer(), default=0),
        sa.Column('shares_count', sa.Integer(), default=0),
        sa.Column('clicks_count', sa.Integer(), default=0),
        sa.Column('impressions', sa.Integer(), default=0),
        sa.Column('reach', sa.Integer(), default=0),
        sa.Column('engagement_rate', sa.Float(), default=0.0),
        
        # Error handling
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('retry_count', sa.Integer(), default=0),
        
        # Metadata
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('created_by', sa.Integer(), sa.ForeignKey('users.id'), nullable=True)
    )
    
    # Create social_media_analytics table
    op.create_table(
        'social_media_analytics',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        
        # Account
        sa.Column('account_id', sa.Integer(), sa.ForeignKey('social_media_accounts.id'), nullable=False),
        sa.Column('platform', sa.String(50), nullable=False),
        
        # Time period
        sa.Column('date', sa.DateTime(), nullable=False),
        sa.Column('period_type', sa.String(20), default='daily'),
        
        # Audience metrics
        sa.Column('followers_count', sa.Integer(), default=0),
        sa.Column('followers_change', sa.Integer(), default=0),
        sa.Column('following_count', sa.Integer(), default=0),
        
        # Engagement metrics
        sa.Column('total_likes', sa.Integer(), default=0),
        sa.Column('total_comments', sa.Integer(), default=0),
        sa.Column('total_shares', sa.Integer(), default=0),
        sa.Column('total_clicks', sa.Integer(), default=0),
        sa.Column('total_impressions', sa.Integer(), default=0),
        sa.Column('total_reach', sa.Integer(), default=0),
        
        # Calculated metrics
        sa.Column('engagement_rate', sa.Float(), default=0.0),
        sa.Column('growth_rate', sa.Float(), default=0.0),
        sa.Column('avg_engagement_per_post', sa.Float(), default=0.0),
        
        # Post metrics
        sa.Column('posts_count', sa.Integer(), default=0),
        sa.Column('best_post_id', sa.Integer(), sa.ForeignKey('social_media_posts.id'), nullable=True),
        sa.Column('best_post_engagement', sa.Float(), default=0.0),
        
        # Metadata
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now())
    )
    
    # Create social_media_templates table
    op.create_table(
        'social_media_templates',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('category', sa.String(100), nullable=True),
        
        # Template content
        sa.Column('content_template', sa.Text(), nullable=False),
        sa.Column('variables', postgresql.JSON(), nullable=True),
        
        # Target platforms
        sa.Column('platforms', postgresql.JSON(), nullable=True),
        
        # Settings
        sa.Column('default_hashtags', postgresql.JSON(), nullable=True),
        sa.Column('include_link', sa.Boolean(), default=False),
        sa.Column('include_image', sa.Boolean(), default=False),
        
        # Usage tracking
        sa.Column('usage_count', sa.Integer(), default=0),
        sa.Column('last_used', sa.DateTime(), nullable=True),
        
        # Metadata
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('created_by', sa.Integer(), sa.ForeignKey('users.id'), nullable=True)
    )
    
    # Create social_media_settings table
    op.create_table(
        'social_media_settings',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        
        # Auto-posting settings
        sa.Column('auto_posting_enabled', sa.Boolean(), default=False),
        sa.Column('auto_post_new_blogs', sa.Boolean(), default=True),
        sa.Column('auto_post_new_services', sa.Boolean(), default=True),
        sa.Column('auto_post_company_updates', sa.Boolean(), default=True),
        
        # Default scheduling
        sa.Column('default_posting_times', postgresql.JSON(), nullable=True),
        sa.Column('optimal_posting_enabled', sa.Boolean(), default=True),
        
        # Content rules
        sa.Column('min_content_length', sa.Integer(), default=50),
        sa.Column('max_content_length', sa.Integer(), default=280),
        sa.Column('require_hashtags', sa.Boolean(), default=True),
        sa.Column('max_hashtags', sa.Integer(), default=5),
        
        # Rate limiting
        sa.Column('max_posts_per_day', sa.Integer(), default=10),
        sa.Column('min_post_interval_minutes', sa.Integer(), default=60),
        
        # Monitoring
        sa.Column('analytics_enabled', sa.Boolean(), default=True),
        sa.Column('daily_reports_enabled', sa.Boolean(), default=True),
        sa.Column('report_recipients', postgresql.JSON(), nullable=True),
        
        # Metadata
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('updated_by', sa.Integer(), sa.ForeignKey('users.id'), nullable=True)
    )
    
    # Create indexes
    op.create_index('idx_social_accounts_platform', 'social_media_accounts', ['platform'])
    op.create_index('idx_social_accounts_connected', 'social_media_accounts', ['is_connected'])
    
    op.create_index('idx_social_posts_platform', 'social_media_posts', ['platform'])
    op.create_index('idx_social_posts_status', 'social_media_posts', ['status'])
    op.create_index('idx_social_posts_scheduled', 'social_media_posts', ['scheduled_time'])
    op.create_index('idx_social_posts_published', 'social_media_posts', ['published_time'])
    
    op.create_index('idx_social_analytics_platform', 'social_media_analytics', ['platform'])
    op.create_index('idx_social_analytics_date', 'social_media_analytics', ['date'])


def downgrade():
    """Drop social media tables"""
    
    op.drop_index('idx_social_analytics_date')
    op.drop_index('idx_social_analytics_platform')
    op.drop_index('idx_social_posts_published')
    op.drop_index('idx_social_posts_scheduled')
    op.drop_index('idx_social_posts_status')
    op.drop_index('idx_social_posts_platform')
    op.drop_index('idx_social_accounts_connected')
    op.drop_index('idx_social_accounts_platform')
    
    op.drop_table('social_media_settings')
    op.drop_table('social_media_templates')
    op.drop_table('social_media_analytics')
    op.drop_table('social_media_posts')
    op.drop_table('social_media_accounts')
