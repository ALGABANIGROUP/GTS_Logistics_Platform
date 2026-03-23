"""
Redis caching utility for GTS Logistics SaaS platform.
Provides async Redis connection pooling and caching decorators.
"""
from __future__ import annotations

import json
import logging
from functools import wraps
from typing import Any, Callable, Optional
import os

try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None  # type: ignore

log = logging.getLogger(__name__)


class CacheConfig:
    """Redis cache configuration."""
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    DEFAULT_TTL = int(os.getenv("CACHE_TTL", "300"))  # 5 minutes
    ENABLED = os.getenv("CACHE_ENABLED", "true").lower() == "true"


class RedisCache:
    """Async Redis cache manager."""
    
    def __init__(self):
        self.client: Optional[redis.Redis] = None
        self.enabled = CacheConfig.ENABLED and REDIS_AVAILABLE
        
    async def connect(self):
        """Initialize Redis connection pool."""
        if not self.enabled:
            log.warning("Redis cache is disabled or redis package not installed")
            return
            
        try:
            self.client = redis.from_url(
                CacheConfig.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
                max_connections=10
            )
            # Test connection
            await self.client.ping()
            log.info(f"✅ Redis cache connected: {CacheConfig.REDIS_URL}")
        except Exception as e:
            log.warning(f"⚠️ Redis connection failed: {e}. Cache disabled.")
            self.enabled = False
            self.client = None
    
    async def disconnect(self):
        """Close Redis connection."""
        if self.client:
            await self.client.close()
            log.info("Redis cache disconnected")
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if not self.enabled or not self.client:
            return None
            
        try:
            value = await self.client.get(key)
            if value:
                return json.loads(value)
        except Exception as e:
            log.error(f"Cache get error for key '{key}': {e}")
        return None
    
    async def set(self, key: str, value: Any, ttl: int = CacheConfig.DEFAULT_TTL) -> bool:
        """Set value in cache with TTL."""
        if not self.enabled or not self.client:
            return False
            
        try:
            serialized = json.dumps(value, default=str)
            await self.client.setex(key, ttl, serialized)
            return True
        except Exception as e:
            log.error(f"Cache set error for key '{key}': {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache."""
        if not self.enabled or not self.client:
            return False
            
        try:
            await self.client.delete(key)
            return True
        except Exception as e:
            log.error(f"Cache delete error for key '{key}': {e}")
            return False
    
    async def clear_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern."""
        if not self.enabled or not self.client:
            return 0
            
        try:
            keys = []
            async for key in self.client.scan_iter(match=pattern):
                keys.append(key)
            if keys:
                return await self.client.delete(*keys)
        except Exception as e:
            log.error(f"Cache clear pattern error for '{pattern}': {e}")
        return 0


# Global cache instance
cache = RedisCache()


def cached(ttl: int = CacheConfig.DEFAULT_TTL, key_prefix: str = ""):
    """
    Decorator for caching async function results.
    
    Usage:
        @cached(ttl=600, key_prefix="user")
        async def get_user(user_id: int):
            return await db.query(User).filter(User.id == user_id).first()
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Build cache key from function name and arguments
            key_parts = [key_prefix, func.__name__]
            key_parts.extend(str(arg) for arg in args)
            key_parts.extend(f"{k}:{v}" for k, v in sorted(kwargs.items()))
            cache_key = ":".join(filter(None, key_parts))
            
            # Try to get from cache
            cached_value = await cache.get(cache_key)
            if cached_value is not None:
                log.debug(f"Cache HIT: {cache_key}")
                return cached_value
            
            # Execute function
            log.debug(f"Cache MISS: {cache_key}")
            result = await func(*args, **kwargs)
            
            # Store in cache
            await cache.set(cache_key, result, ttl)
            return result
        
        return wrapper
    return decorator


async def invalidate_cache_pattern(pattern: str):
    """
    Utility to invalidate cache by pattern.
    
    Usage:
        await invalidate_cache_pattern("user:*")
    """
    count = await cache.clear_pattern(pattern)
    log.info(f"Invalidated {count} cache keys matching '{pattern}'")
    return count
