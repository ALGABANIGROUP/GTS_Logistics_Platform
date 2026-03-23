"""Unit tests for support models and enums."""

from __future__ import annotations

from backend.models.support_models import (
    ChannelType,
    EmailTemplate,
    KnowledgeBase,
    SLALevel,
    SLAStatus,
    SupportAgent,
    SupportFeedback,
    SupportStats,
    SupportTicket,
    TicketActivity,
    TicketAttachment,
    TicketCategory,
    TicketComment,
    TicketHistory,
    TicketPriority,
    TicketStatus,
)


class TestSupportTickets:
    def test_create_ticket_defaults(self):
        ticket = SupportTicket(
            customer_id=1,
            customer_email="test@example.com",
            customer_name="Test User",
            title="Test Ticket",
            description="This is a test ticket",
            category=TicketCategory.TECHNICAL.value,
            priority=TicketPriority.HIGH.value,
            sla_level_id=1,
        )

        assert ticket.title == "Test Ticket"
        assert ticket.status is None or ticket.status == TicketStatus.OPEN.value
        assert ticket.priority == TicketPriority.HIGH.value

    def test_ticket_repr_contains_number(self):
        ticket = SupportTicket(
            ticket_number="TK-001234",
            customer_id=1,
            customer_email="test@example.com",
            customer_name="Test User",
            title="Printer issue",
            description="Paper jam",
            sla_level_id=1,
        )
        assert "TK-001234" in repr(ticket)


class TestTicketComments:
    def test_add_comment_fields(self):
        comment = TicketComment(
            ticket_id=10,
            author_id=1,
            author_type="customer",
            content="This is a test comment",
            is_internal=False,
        )

        assert comment.ticket_id == 10
        assert comment.content == "This is a test comment"
        assert comment.is_internal is False

    def test_ticket_activity_repr(self):
        activity = TicketActivity(
            ticket_id=11,
            action="status_changed",
            description="Changed from open to resolved",
        )
        assert "status_changed" in repr(activity)


class TestKnowledgeBase:
    def test_list_kb_article_fields(self):
        article = KnowledgeBase(
            title="Test Article",
            slug="test-article",
            content="This is test content",
            summary="Short summary",
            category="technical",
            author_id=1,
        )

        assert article.slug == "test-article"
        assert article.is_published is None or article.is_published is True

    def test_email_template_repr(self):
        template = EmailTemplate(
            name="Welcome",
            slug="welcome",
            subject="Hello",
            body="World",
            created_by=1,
        )
        assert "Welcome" in repr(template)


class TestSLACompliance:
    def test_sla_level_fields(self):
        sla = SLALevel(
            priority=TicketPriority.CRITICAL.value,
            response_time=1,
            resolution_time=4,
            escalation_threshold=0.75,
        )

        assert sla.priority == "critical"
        assert sla.response_time == 1
        assert sla.resolution_time == 4

    def test_sla_status_enum_values(self):
        assert SLAStatus.COMPLIANT.value == "compliant"
        assert SLAStatus.BREACHED.value == "breached"


class TestSupportFeedback:
    def test_submit_feedback_fields(self):
        feedback = SupportFeedback(
            ticket_id=22,
            overall_rating=5,
            response_time_rating=4,
            solution_quality_rating=5,
            agent_professionalism_rating=5,
            comments="Excellent support!",
        )

        assert feedback.overall_rating == 5
        assert feedback.comments == "Excellent support!"

    def test_support_stats_defaults(self):
        stats = SupportStats(date="2026-03-11")
        assert stats.date == "2026-03-11"
        assert stats.sla_compliance_rate is None or stats.sla_compliance_rate == 100.0


class TestAgentOperations:
    def test_support_agent_defaults(self):
        agent = SupportAgent(user_id=1, employee_id="EMP-1")
        assert agent.employee_id == "EMP-1"
        assert agent.timezone is None or agent.timezone == "UTC"

    def test_channel_enum_contains_portal(self):
        assert ChannelType.PORTAL.value == "portal"


class TestErrorHandling:
    def test_priority_enum_values(self):
        assert TicketPriority.CRITICAL.value == "critical"
        assert TicketPriority.LOW.value == "low"

    def test_status_enum_values(self):
        assert TicketStatus.OPEN.value == "open"
        assert TicketStatus.RESOLVED.value == "resolved"

    def test_category_enum_values(self):
        assert TicketCategory.BILLING.value == "billing"
        assert TicketCategory.BUG_REPORT.value == "bug_report"

    def test_ticket_history_fields(self):
        history = TicketHistory(
            ticket_id=15,
            old_status="open",
            new_status="resolved",
            old_priority="high",
            new_priority="medium",
        )
        assert history.new_status == "resolved"
        assert history.new_priority == "medium"

    def test_attachment_repr(self):
        attachment = TicketAttachment(
            ticket_id=1,
            filename="invoice.pdf",
            file_path="/tmp/invoice.pdf",
            file_size=1024,
            file_type="application/pdf",
            uploaded_by=1,
        )
        assert "invoice.pdf" in repr(attachment)
