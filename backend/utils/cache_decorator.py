"""
Dynamic Cache Decorator
Caching enabled/disabled based on platform technical settings.
"""

import functools
import logging
from typing import Any, Callable, Optional
from cachetools import TTLCache
import hashlib
import json

logger = logging.getLogger(__name__)

# Global in-memory cache (max 1000 items, 5 minutes TTL)
_cache = TTLCache(maxsize=1000, ttl=300)


def cached(ttl: int = 300):
    """
    Cache decorator that respects platform cachingEnabled setting.
    
    Args:
        ttl: Time to live in seconds (default 300 = 5 minutes)
    
    Usage:
        @cached(ttl=60)
        async def my_expensive_function(param1, param2):
            # ... expensive operation
            return result
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Check if caching is enabled in platform settings
            try:
                from backend.utils.technical_settings import is_caching_enabled
                if not await is_caching_enabled():
                    # Caching disabled, call function directly
                    return await func(*args, **kwargs)
            except Exception as e:
                logger.warning(f"Failed to check caching status: {e}, proceeding without cache")
                return await func(*args, **kwargs)
            
            # Generate cache key from function name and arguments
            cache_key = _generate_cache_key(func.__name__, args, kwargs)
            
            # Check if result is in cache
            if cache_key in _cache:
                logger.debug(f"Cache hit for {func.__name__}")
                return _cache[cache_key]
            
            # Call function and cache result
            result = await func(*args, **kwargs)
            _cache[cache_key] = result
            logger.debug(f"Cache miss for {func.__name__}, result cached")
            
            return result
        
        return wrapper
    return decorator


def _generate_cache_key(func_name: str, args: tuple, kwargs: dict) -> str:
    """Generate a unique cache key from function name and arguments"""
    try:
        # Create a string representation of arguments
        args_str = json.dumps({"args": args, "kwargs": kwargs}, sort_keys=True, default=str)
        key_str = f"{func_name}:{args_str}"
        
        # Hash for shorter key
        return hashlib.md5(key_str.encode()).hexdigest()
    except Exception as e:
        logger.warning(f"Failed to generate cache key: {e}")
        # Fallback to string representation
        return f"{func_name}:{str(args)}:{str(kwargs)}"


def clear_cache():
    """Clear all cached items"""
    global _cache
    _cache.clear()
    logger.info("Application cache cleared")


def get_cache_stats():
    """Get cache statistics"""
    return {
        "size": len(_cache),
        "maxsize": _cache.maxsize,
        "ttl": _cache.ttl
    }
