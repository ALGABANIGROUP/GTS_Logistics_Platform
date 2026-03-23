"""
Support System Database Migration
Alembic migration for Support ticketing system tables

Run with: python -m alembic -c backend/alembic.ini upgrade head
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic
revision = '550e8400_support_system_001'
down_revision = 'tenant_001'
branch_labels = None
depends_on = None


def upgrade():
    """Create support system tables"""
    
    # Create enum types
    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'support_ticket_status') THEN
            CREATE TYPE support_ticket_status AS ENUM (
                'open', 'in_progress', 'waiting_customer', 'resolved', 'closed', 'reopened'
            );
        END IF;
        IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'support_ticket_priority') THEN
            CREATE TYPE support_ticket_priority AS ENUM (
                'critical', 'high', 'medium', 'low'
            );
        END IF;
        IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'support_ticket_category') THEN
            CREATE TYPE support_ticket_category AS ENUM (
                'technical', 'billing', 'account', 'general', 'feature_request', 'bug_report'
            );
        END IF;
        IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'support_sla_status') THEN
            CREATE TYPE support_sla_status AS ENUM (
                'compliant', 'at_risk', 'breached'
            );
        END IF;
        IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'support_channel_type') THEN
            CREATE TYPE support_channel_type AS ENUM (
                'email', 'live_chat', 'phone', 'whatsapp', 'telegram', 'portal'
            );
        END IF;
    END $$;
    """)

    # SLA Levels Table
    op.create_table(
        'sla_levels',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('priority', sa.String(20), nullable=False, unique=True),
        sa.Column('response_time_hours', sa.Integer(), nullable=False),
        sa.Column('resolution_time_hours', sa.Integer(), nullable=False),
        sa.Column('escalation_after_hours', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )

    # Support Agents Table
    op.create_table(
        'support_agents',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('max_concurrent_tickets', sa.Integer(), default=10),
        sa.Column('current_ticket_count', sa.Integer(), default=0),
        sa.Column('avg_satisfaction', sa.Float(), default=0.0),
        sa.Column('avg_resolution_time', sa.Integer(), default=0),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE')
    )
    op.create_index('ix_support_agents_user_id', 'support_agents', ['user_id'])

    # EN ENUMs EN (create_type=False)
    support_ticket_category_enum = postgresql.ENUM(
        'technical', 'billing', 'account', 'general', 'feature_request', 'bug_report',
        name='support_ticket_category', create_type=False
    )
    support_ticket_priority_enum = postgresql.ENUM(
        'critical', 'high', 'medium', 'low',
        name='support_ticket_priority', create_type=False
    )
    support_ticket_status_enum = postgresql.ENUM(
        'open', 'in_progress', 'waiting_customer', 'resolved', 'closed', 'reopened',
        name='support_ticket_status', create_type=False
    )
    support_channel_type_enum = postgresql.ENUM(
        'email', 'live_chat', 'phone', 'whatsapp', 'telegram', 'portal',
        name='support_channel_type', create_type=False
    )
    support_sla_status_enum = postgresql.ENUM(
        'compliant', 'at_risk', 'breached',
        name='support_sla_status', create_type=False
    )

    # Support Tickets Table
    op.create_table(
        'support_tickets',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('ticket_number', sa.String(20), nullable=False, unique=True),
        sa.Column('customer_id', sa.Integer(), nullable=False),
        sa.Column('agent_id', sa.Integer(), nullable=True),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('category', support_ticket_category_enum, nullable=False),
        sa.Column('priority', support_ticket_priority_enum, nullable=False),
        sa.Column('status', support_ticket_status_enum, default='open'),
        sa.Column('channel', support_channel_type_enum, default='portal'),
        sa.Column('sla_response_due', sa.DateTime(), nullable=False),
        sa.Column('sla_resolution_due', sa.DateTime(), nullable=False),
        sa.Column('sla_status', support_sla_status_enum, default='compliant'),
        sa.Column('first_response_at', sa.DateTime(), nullable=True),
        sa.Column('resolved_at', sa.DateTime(), nullable=True),
        sa.Column('closed_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['customer_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['agent_id'], ['support_agents.id'], ondelete='SET NULL')
    )
    op.create_index('ix_support_tickets_ticket_number', 'support_tickets', ['ticket_number'])
    op.create_index('ix_support_tickets_customer_id', 'support_tickets', ['customer_id'])
    op.create_index('ix_support_tickets_agent_id', 'support_tickets', ['agent_id'])
    op.create_index('ix_support_tickets_status', 'support_tickets', ['status'])
    op.create_index('ix_support_tickets_sla_status', 'support_tickets', ['sla_status'])

    # Ticket Comments Table
    op.create_table(
        'ticket_comments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('ticket_id', sa.Integer(), nullable=False),
        sa.Column('author_id', sa.Integer(), nullable=False),
        sa.Column('author_type', sa.String(20), nullable=False),  # 'agent' or 'customer'
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('is_internal', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['ticket_id'], ['support_tickets.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['author_id'], ['users.id'], ondelete='CASCADE')
    )
    op.create_index('ix_ticket_comments_ticket_id', 'ticket_comments', ['ticket_id'])

    # Ticket Activity (Audit Log) Table
    op.create_table(
        'ticket_activities',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('ticket_id', sa.Integer(), nullable=False),
        sa.Column('action', sa.String(50), nullable=False),
        sa.Column('old_value', sa.Text(), nullable=True),
        sa.Column('new_value', sa.Text(), nullable=True),
        sa.Column('actor_id', sa.Integer(), nullable=False),
        sa.Column('actor_type', sa.String(20), nullable=False),  # 'agent', 'system', 'customer'
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['ticket_id'], ['support_tickets.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['actor_id'], ['users.id'], ondelete='CASCADE')
    )
    op.create_index('ix_ticket_activities_ticket_id', 'ticket_activities', ['ticket_id'])

    # Ticket History Table
    op.create_table(
        'ticket_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('ticket_id', sa.Integer(), nullable=False),
        sa.Column('previous_status', sa.String(50), nullable=True),
        sa.Column('new_status', sa.String(50), nullable=False),
        sa.Column('changed_by_id', sa.Integer(), nullable=False),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('changed_at', sa.DateTime(), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['ticket_id'], ['support_tickets.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['changed_by_id'], ['users.id'], ondelete='CASCADE')
    )
    op.create_index('ix_ticket_history_ticket_id', 'ticket_history', ['ticket_id'])

    # Ticket Attachments Table
    op.create_table(
        'ticket_attachments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('ticket_id', sa.Integer(), nullable=False),
        sa.Column('file_name', sa.String(255), nullable=False),
        sa.Column('file_path', sa.String(500), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('mime_type', sa.String(100), nullable=False),
        sa.Column('uploaded_by_id', sa.Integer(), nullable=False),
        sa.Column('uploaded_at', sa.DateTime(), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['ticket_id'], ['support_tickets.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['uploaded_by_id'], ['users.id'], ondelete='CASCADE')
    )

    # Knowledge Base Table
    op.create_table(
        'knowledge_base_articles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('category', sa.String(50), nullable=False),
        sa.Column('view_count', sa.Integer(), default=0),
        sa.Column('helpful_votes', sa.Integer(), default=0),
        sa.Column('is_published', sa.Boolean(), default=True),
        sa.Column('author_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['author_id'], ['users.id'], ondelete='CASCADE')
    )
    op.create_index('ix_kb_articles_category', 'knowledge_base_articles', ['category'])
    op.create_index('ix_kb_articles_is_published', 'knowledge_base_articles', ['is_published'])

    # Support Feedback Table
    op.create_table(
        'support_feedback',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('ticket_id', sa.Integer(), nullable=False),
        sa.Column('customer_id', sa.Integer(), nullable=False),
        sa.Column('overall_rating', sa.Integer(), nullable=False),  # 1-5
        sa.Column('response_time_rating', sa.Integer(), nullable=True),
        sa.Column('solution_quality_rating', sa.Integer(), nullable=True),
        sa.Column('professionalism_rating', sa.Integer(), nullable=True),
        sa.Column('comments', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['ticket_id'], ['support_tickets.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['customer_id'], ['users.id'], ondelete='CASCADE')
    )
    op.create_index('ix_support_feedback_ticket_id', 'support_feedback', ['ticket_id'])

    # Support Statistics Table
    op.create_table(
        'support_statistics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('date', sa.Date(), nullable=False, unique=True),
        sa.Column('tickets_created', sa.Integer(), default=0),
        sa.Column('tickets_resolved', sa.Integer(), default=0),
        sa.Column('avg_response_time_minutes', sa.Float(), default=0),
        sa.Column('avg_resolution_time_hours', sa.Float(), default=0),
        sa.Column('sla_compliance_rate', sa.Float(), default=0),
        sa.Column('customer_satisfaction_score', sa.Float(), default=0),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )

    # Email Templates Table
    op.create_table(
        'support_email_templates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(100), nullable=False, unique=True),
        sa.Column('subject', sa.String(255), nullable=False),
        sa.Column('body_html', sa.Text(), nullable=False),
        sa.Column('variables', postgresql.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )

    # Email Tracking Table
    op.create_table(
        'support_emails',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('ticket_id', sa.Integer(), nullable=False),
        sa.Column('recipient_email', sa.String(255), nullable=False),
        sa.Column('subject', sa.String(255), nullable=False),
        sa.Column('template_name', sa.String(100), nullable=True),
        sa.Column('status', sa.String(20), default='sent'),  # 'sent', 'failed', 'bounced', 'opened'
        sa.Column('sent_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('opened_at', sa.DateTime(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['ticket_id'], ['support_tickets.id'], ondelete='CASCADE')
    )
    op.create_index('ix_support_emails_ticket_id', 'support_emails', ['ticket_id'])


def downgrade():
    """Drop support system tables and enums"""
    
    # Drop tables
    op.drop_table('support_emails')
    op.drop_table('support_email_templates')
    op.drop_table('support_statistics')
    op.drop_table('support_feedback')
    op.drop_table('knowledge_base_articles')
    op.drop_table('ticket_attachments')
    op.drop_table('ticket_history')
    op.drop_table('ticket_activities')
    op.drop_table('ticket_comments')
    op.drop_table('support_tickets')
    op.drop_table('support_agents')
    op.drop_table('sla_levels')
    
    # Drop enum types
    op.execute("DROP TYPE support_channel_type")
    op.execute("DROP TYPE support_sla_status")
    op.execute("DROP TYPE support_ticket_category")
    op.execute("DROP TYPE support_ticket_priority")
    op.execute("DROP TYPE support_ticket_status")
