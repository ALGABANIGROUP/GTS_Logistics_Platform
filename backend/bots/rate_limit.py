from __future__ import annotations

import time
from collections import deque
from dataclasses import dataclass
from typing import Deque, Dict, Tuple


@dataclass(frozen=True)
class RateLimitDecision:
    allowed: bool
    remaining: int
    reset_in: int


class RateLimiter:
    def __init__(self, limit: int, window_seconds: int) -> None:
        self.limit = max(1, int(limit))
        self.window_seconds = max(1, int(window_seconds))
        self._hits: Dict[str, Deque[float]] = {}

    def _purge(self, key: str, now: float) -> Deque[float]:
        hits = self._hits.setdefault(key, deque())
        cutoff = now - self.window_seconds
        while hits and hits[0] < cutoff:
            hits.popleft()
        return hits

    def allow(self, key: str, now: float | None = None) -> RateLimitDecision:
        now = now or time.time()
        hits = self._purge(key, now)
        if len(hits) >= self.limit:
            reset_in = int(self.window_seconds - (now - hits[0]))
            return RateLimitDecision(False, 0, max(reset_in, 1))

        hits.append(now)
        remaining = max(self.limit - len(hits), 0)
        return RateLimitDecision(True, remaining, self.window_seconds)


class RoleRateLimiter:
    DEFAULT_LIMITS: Dict[str, Tuple[int, int]] = {
        "super_admin": (30, 60),
        "admin": (20, 60),
        "manager": (10, 60),
        "user": (5, 60),
    }

    def __init__(self, limits: Dict[str, Tuple[int, int]] | None = None) -> None:
        self._limits = limits or dict(self.DEFAULT_LIMITS)
        self._limiters: Dict[str, RateLimiter] = {}

    def _get_limiter(self, role: str) -> RateLimiter:
        role_key = (role or "user").lower()
        limit, window = self._limits.get(role_key, self._limits["user"])
        limiter = self._limiters.get(role_key)
        if limiter is None or limiter.limit != limit or limiter.window_seconds != window:
            limiter = RateLimiter(limit=limit, window_seconds=window)
            self._limiters[role_key] = limiter
        return limiter

    def check(self, role: str, key: str, now: float | None = None) -> RateLimitDecision:
        limiter = self._get_limiter(role)
        return limiter.allow(key, now=now)
