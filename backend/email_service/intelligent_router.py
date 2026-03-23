"""Compatibility wrapper for the current email router implementation."""

from backend.email_bot.intelligent_router import IntelligentEmailRouter as CoreIntelligentEmailRouter


class IntelligentEmailRouter(CoreIntelligentEmailRouter):
    """Backward-compatible alias for the current email router."""

    def route_email(self, email_dict):
        """Preserve the old API used by some callers."""
        return self.route_and_process(email_dict)
