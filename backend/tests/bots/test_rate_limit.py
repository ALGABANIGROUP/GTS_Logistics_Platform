from backend.bots.rate_limit import RoleRateLimiter


def test_rate_limit_allows_within_limit():
    limiter = RoleRateLimiter(limits={"admin": (2, 60), "user": (1, 60)})
    decision1 = limiter.check("admin", "user-1", now=1000)
    decision2 = limiter.check("admin", "user-1", now=1001)
    assert decision1.allowed is True
    assert decision2.allowed is True


def test_rate_limit_blocks_after_limit():
    limiter = RoleRateLimiter(limits={"admin": (2, 60), "user": (1, 60)})
    limiter.check("admin", "user-1", now=1000)
    limiter.check("admin", "user-1", now=1001)
    blocked = limiter.check("admin", "user-1", now=1002)
    assert blocked.allowed is False
    assert blocked.reset_in > 0


def test_rate_limit_defaults_to_user_role():
    limiter = RoleRateLimiter(limits={"user": (1, 60)})
    decision1 = limiter.check("unknown", "user-2", now=2000)
    decision2 = limiter.check("unknown", "user-2", now=2001)
    assert decision1.allowed is True
    assert decision2.allowed is False
