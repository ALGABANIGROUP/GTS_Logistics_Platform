"""Technical Settings Helper - Read and apply technical configurations"""
import logging
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

# Cache for technical settings (refresh every 60 seconds)
_settings_cache: Optional[Dict[str, Any]] = None
_db_settings_cache: Optional[Dict[str, Any]] = None
_cache_timestamp: float = 0
CACHE_TTL = 60  # seconds

_DB_DEFAULTS: Dict[str, Any] = {
    "dbType": "postgres",
    "backupRetentionDays": 14,
    "cleanupOldDataDays": 90,
    "enableDbLogs": True,
    "backupWindow": "02:00",
}

async def get_technical_settings(db: AsyncSession) -> Dict[str, Any]:
    """Get technical settings from database with caching"""
    global _settings_cache, _db_settings_cache, _cache_timestamp
    
    import time
    current_time = time.time()
    
    # Return cached settings if still valid
    if _settings_cache and (current_time - _cache_timestamp) < CACHE_TTL:
        return _settings_cache
    
    try:
        from backend.services.platform_settings_store import get_platform_settings
        settings = await get_platform_settings(db)
        technical = settings.get("technical", {})
        database = settings.get("database", {})
        
        # Update cache
        _settings_cache = technical
        _db_settings_cache = {**_DB_DEFAULTS, **(database or {})}
        _cache_timestamp = current_time
        
        return technical
    except Exception as e:
        logger.error(f"Failed to load technical settings: {e}")
        
        # Return defaults if something goes wrong
        _db_settings_cache = _DB_DEFAULTS.copy()
        return {
            "sessionTimeout": 30,
            "maxUploadSize": 10,
            "cachingEnabled": True,
            "maintenanceMode": False,
            "apiRateLimit": "100/hour",
            "backupFrequency": "daily"
        }

async def get_session_timeout_minutes() -> int:
    """Get session timeout in minutes (default 30) - uses cache"""
    if _settings_cache:
        return _settings_cache.get("sessionTimeout", 30)
    return 30

async def get_max_upload_size_mb() -> int:
    """Get max upload size in MB (default 10) - uses cache"""
    if _settings_cache:
        return _settings_cache.get("maxUploadSize", 10)
    return 10

async def is_maintenance_mode() -> bool:
    """Check if system is in maintenance mode - uses cache"""
    if _settings_cache:
        return _settings_cache.get("maintenanceMode", False)
    return False

async def is_caching_enabled() -> bool:
    """Check if caching is enabled - uses cache"""
    if _settings_cache:
        return _settings_cache.get("cachingEnabled", True)
    return True

def get_api_rate_limit_sync() -> str:
    """Get API rate limit from cache (sync) - for use in main.py startup"""
    if _settings_cache:
        return _settings_cache.get("apiRateLimit", "100/hour")
    return "100/hour"

def get_backup_frequency_sync() -> str:
    """Get backup frequency from cache (sync) - returns 'daily', 'weekly', 'monthly'"""
    if _settings_cache:
        return _settings_cache.get("backupFrequency", "daily")
    return "daily"

def get_database_settings_sync() -> Dict[str, Any]:
    """Get database settings from cache (sync)."""
    if _db_settings_cache:
        return _db_settings_cache
    return _DB_DEFAULTS.copy()

def invalidate_cache():
    """Force cache refresh on next call"""
    global _settings_cache, _db_settings_cache, _cache_timestamp
    _settings_cache = None
    _db_settings_cache = None
    _cache_timestamp = 0
