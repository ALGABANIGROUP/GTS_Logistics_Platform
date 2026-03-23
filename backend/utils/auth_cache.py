# backend/utils/auth_cache.py
"""
Phase 3 Optimization: In-memory auth token caching
Reduces database load for frequently accessed tokens
"""

from __future__ import annotations

import time
from typing import Optional, Dict, Tuple
from datetime import datetime, timedelta
import logging

log = logging.getLogger("gts.auth_cache")


class TokenCache:
    """Simple in-memory cache for JWT tokens and user data"""
    
    def __init__(self, ttl_seconds: int = 300):  # 5 minutes default
        self._cache: Dict[str, Tuple[dict, float]] = {}
        self._ttl = ttl_seconds
        self._hits = 0
        self._misses = 0
        log.info(f"TokenCache initialized with TTL={ttl_seconds}s")
    
    def get(self, token: str) -> Optional[dict]:
        """Get cached user data for token"""
        if token not in self._cache:
            self._misses += 1
            return None
        
        user_data, expiry = self._cache[token]
        
        # Check if expired
        if time.time() > expiry:
            del self._cache[token]
            self._misses += 1
            return None
        
        self._hits += 1
        log.debug(f"Cache HIT for token (hits={self._hits}, misses={self._misses})")
        return user_data
    
    def set(self, token: str, user_data: dict) -> None:
        """Cache user data for token"""
        expiry = time.time() + self._ttl
        self._cache[token] = (user_data, expiry)
        log.debug(f"Cached token data for user {user_data.get('email', 'unknown')}")
    
    def invalidate(self, token: str) -> None:
        """Remove token from cache"""
        if token in self._cache:
            del self._cache[token]
            log.debug("Invalidated cached token")
    
    def clear(self) -> None:
        """Clear entire cache"""
        count = len(self._cache)
        self._cache.clear()
        log.info(f"Cache cleared ({count} entries removed)")
    
    def get_stats(self) -> dict:
        """Get cache statistics"""
        total = self._hits + self._misses
        hit_rate = (self._hits / total * 100) if total > 0 else 0
        
        return {
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate_percent": round(hit_rate, 2),
            "cached_tokens": len(self._cache),
            "ttl_seconds": self._ttl
        }
    
    def cleanup_expired(self) -> int:
        """Remove expired entries, return count removed"""
        now = time.time()
        expired = [token for token, (_, expiry) in self._cache.items() if now > expiry]
        
        for token in expired:
            del self._cache[token]
        
        if expired:
            log.info(f"Cleaned up {len(expired)} expired cache entries")
        
        return len(expired)


# Global cache instance
_token_cache: Optional[TokenCache] = None


def get_token_cache(ttl_seconds: int = 300) -> TokenCache:
    """Get or create global token cache instance"""
    global _token_cache
    if _token_cache is None:
        _token_cache = TokenCache(ttl_seconds=ttl_seconds)
    return _token_cache


def cache_user_data(token: str, user_data: dict) -> None:
    """Helper to cache user data"""
    cache = get_token_cache()
    cache.set(token, user_data)


def get_cached_user(token: str) -> Optional[dict]:
    """Helper to retrieve cached user data"""
    cache = get_token_cache()
    return cache.get(token)


def invalidate_token(token: str) -> None:
    """Helper to invalidate cached token"""
    cache = get_token_cache()
    cache.invalidate(token)


def get_cache_stats() -> dict:
    """Helper to get cache statistics"""
    cache = get_token_cache()
    return cache.get_stats()


__all__ = [
    "TokenCache",
    "get_token_cache",
    "cache_user_data",
    "get_cached_user",
    "invalidate_token",
    "get_cache_stats"
]
