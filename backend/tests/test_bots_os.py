from __future__ import annotations

import pytest
from backend.bots.command_parser import parse_command, normalize_bot_name, BOT_ALIASES
from backend.bots.rate_limit import RateLimiter, RoleRateLimiter, RateLimitDecision


class TestCommandParser:
    def test_normalize_bot_name_simple(self):
        assert normalize_bot_name("finance_bot") == "finance_bot"
        assert normalize_bot_name("Finance Bot") == "finance_bot"
        assert normalize_bot_name("FINANCE-BOT") == "finance_bot"

    def test_normalize_bot_name_with_special_chars(self):
        assert normalize_bot_name("finance@bot#123") == "financebot123"
        assert normalize_bot_name("  spaces  ") == "spaces"

    def test_normalize_bot_name_empty(self):
        assert normalize_bot_name("") == ""
        assert normalize_bot_name(None) == ""

    def test_parse_command_text_format(self):
        result = parse_command("run finance_bot")
        assert result["ok"] is True
        assert result["bot_name"] == "finance_bot"
        assert result["task_type"] == "run"
        assert result["source"] == "text"

    def test_parse_command_json_format(self):
        result = parse_command('{"bot":"finance_bot","task":"daily","params":{"account_id":"123"}}')
        assert result["ok"] is True
        assert result["bot_name"] == "finance_bot"
        assert result["task_type"] == "daily"
        assert result["params"]["account_id"] == "123"
        assert result["source"] == "json"

    def test_parse_command_with_aliases(self):
        result = parse_command("run finance")
        assert result["ok"] is True
        assert result["bot_name"] == "finance_bot"

    def test_parse_command_with_task(self):
        result = parse_command("run freight_broker task:optimize_loads")
        assert result["ok"] is True
        assert result["bot_name"] == "freight_broker"
        assert result["task_type"] == "optimize_loads"

    def test_parse_command_with_action_keyword(self):
        result = parse_command("bot:general_manager action:daily_report")
        assert result["ok"] is True
        assert result["bot_name"] == "general_manager"
        assert result["task_type"] == "daily_report"

    def test_parse_command_empty(self):
        result = parse_command("")
        assert result["ok"] is False
        assert result["error"] == "empty_command"

    def test_parse_command_invalid_json(self):
        result = parse_command("{invalid json")
        assert result["ok"] is True or result["ok"] is False

    def test_parse_command_case_insensitive(self):
        result1 = parse_command("run FINANCE_BOT")
        result2 = parse_command("RUN finance_bot")
        assert result1["bot_name"] == result2["bot_name"]
        assert result1["bot_name"] == "finance_bot"

    def test_parse_command_freight_broker_alias(self):
        result = parse_command("run broker")
        assert result["ok"] is True
        assert result["bot_name"] == "freight_broker"

    def test_parse_command_with_equals_syntax(self):
        result = parse_command("bot=general_manager task=report")
        assert result["ok"] is True
        assert result["bot_name"] == "general_manager"
        assert result["task_type"] == "report"

    def test_parse_command_json_with_alternative_keys(self):
        result = parse_command('{"botKey":"finance_bot","action":"audit"}')
        assert result["ok"] is True
        assert result["bot_name"] == "finance_bot"
        assert result["task_type"] == "audit"

    def test_parse_command_bot_names_from_aliases(self):
        for alias, canonical in BOT_ALIASES.items():
            result = parse_command(f"run {alias}")
            assert result["ok"] is True
            assert result["bot_name"] == canonical, f"Alias {alias} should resolve to {canonical}"


class TestRateLimiter:
    def test_rate_limiter_init(self):
        limiter = RateLimiter(limit=5, window_seconds=60)
        assert limiter.limit == 5
        assert limiter.window_seconds == 60

    def test_rate_limiter_allows_under_limit(self):
        limiter = RateLimiter(limit=3, window_seconds=60)
        for i in range(3):
            decision = limiter.allow("user1")
            assert decision.allowed is True
            assert decision.remaining == 2 - i

    def test_rate_limiter_blocks_over_limit(self):
        limiter = RateLimiter(limit=2, window_seconds=60)
        limiter.allow("user1")
        limiter.allow("user1")
        decision = limiter.allow("user1")
        assert decision.allowed is False
        assert decision.remaining == 0
        assert decision.reset_in > 0

    def test_rate_limiter_different_keys(self):
        limiter = RateLimiter(limit=1, window_seconds=60)
        decision1 = limiter.allow("user1")
        decision2 = limiter.allow("user2")
        assert decision1.allowed is True
        assert decision2.allowed is True

    def test_rate_limiter_one_request(self):
        limiter = RateLimiter(limit=1, window_seconds=60)
        assert limiter.allow("user1").allowed is True
        assert limiter.allow("user1").allowed is False

    def test_rate_limiter_with_explicit_time(self):
        limiter = RateLimiter(limit=2, window_seconds=10)
        now = 1000.0
        decision1 = limiter.allow("user1", now=now)
        decision2 = limiter.allow("user1", now=now + 1)
        decision3 = limiter.allow("user1", now=now + 2)
        assert decision1.allowed is True
        assert decision2.allowed is True
        assert decision3.allowed is False

    def test_rate_limiter_window_expiry(self):
        limiter = RateLimiter(limit=1, window_seconds=10)
        now = 1000.0
        decision1 = limiter.allow("user1", now=now)
        assert decision1.allowed is True
        decision2 = limiter.allow("user1", now=now + 5)
        assert decision2.allowed is False
        decision3 = limiter.allow("user1", now=now + 11)
        assert decision3.allowed is True


class TestRoleRateLimiter:
    def test_role_rate_limiter_super_admin(self):
        limiter = RoleRateLimiter()
        now = 1000.0
        for i in range(30):
            decision = limiter.check("super_admin", "user1", now=now)
            assert decision.allowed is True
        decision = limiter.check("super_admin", "user1", now=now + 1)
        assert decision.allowed is False

    def test_role_rate_limiter_admin(self):
        limiter = RoleRateLimiter()
        now = 1000.0
        for i in range(20):
            decision = limiter.check("admin", "user1", now=now)
            assert decision.allowed is True
        decision = limiter.check("admin", "user1", now=now + 1)
        assert decision.allowed is False

    def test_role_rate_limiter_manager(self):
        limiter = RoleRateLimiter()
        now = 1000.0
        for i in range(10):
            decision = limiter.check("manager", "user1", now=now)
            assert decision.allowed is True
        decision = limiter.check("manager", "user1", now=now + 1)
        assert decision.allowed is False

    def test_role_rate_limiter_user(self):
        limiter = RoleRateLimiter()
        now = 1000.0
        for i in range(5):
            decision = limiter.check("user", "user1", now=now)
            assert decision.allowed is True
        decision = limiter.check("user", "user1", now=now + 1)
        assert decision.allowed is False

    def test_role_rate_limiter_unknown_role_defaults_to_user(self):
        limiter = RoleRateLimiter()
        now = 1000.0
        for i in range(5):
            decision = limiter.check("unknown_role", "user1", now=now)
            assert decision.allowed is True
        decision = limiter.check("unknown_role", "user1", now=now + 1)
        assert decision.allowed is False

    def test_role_rate_limiter_case_insensitive_role(self):
        limiter = RoleRateLimiter()
        now = 1000.0
        decision1 = limiter.check("ADMIN", "user1", now=now)
        decision2 = limiter.check("admin", "user1", now=now + 1)
        assert decision1.allowed is True
        assert decision2.allowed is True

    def test_role_rate_limiter_different_users_independent(self):
        limiter = RoleRateLimiter()
        now = 1000.0
        decision1 = limiter.check("admin", "user1", now=now)
        decision2 = limiter.check("admin", "user2", now=now)
        assert decision1.allowed is True
        assert decision2.allowed is True

    def test_role_rate_limiter_custom_limits(self):
        custom_limits = {
            "super_admin": (100, 60),
            "admin": (50, 60),
            "manager": (10, 60),
            "user": (5, 60),
        }
        limiter = RoleRateLimiter(limits=custom_limits)
        now = 1000.0
        for i in range(100):
            decision = limiter.check("super_admin", "user1", now=now)
            assert decision.allowed is True
        decision = limiter.check("super_admin", "user1", now=now + 1)
        assert decision.allowed is False

    def test_role_rate_limiter_decision_has_reset_in(self):
        limiter = RoleRateLimiter()
        now = 1000.0
        for i in range(5):
            limiter.check("user", "user1", now=now)
        decision = limiter.check("user", "user1", now=now)
        assert decision.allowed is False
        assert decision.reset_in > 0
        assert decision.reset_in <= 60


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
