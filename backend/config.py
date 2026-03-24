from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv


_BACKEND_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _BACKEND_DIR.parent

# Load local environment files if present (without overriding already-set env vars)
for _env_path in (_PROJECT_ROOT / ".env", _BACKEND_DIR / ".env"):
    if _env_path.exists():
        load_dotenv(dotenv_path=_env_path, override=False)


@dataclass
class Settings:
    APP_ENV: str = os.getenv("APP_ENV", "development")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() in ("1", "true", "yes")

    ASYNC_DATABASE_URL: Optional[str] = os.getenv("ASYNC_DATABASE_URL")
    DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL")
    SQLALCHEMY_DATABASE_URL: Optional[str] = os.getenv("SQLALCHEMY_DATABASE_URL")

    PG_USER: str = os.getenv("PG_USER", "")
    PG_PASSWORD: str = os.getenv("PG_PASSWORD", "")
    PG_HOST: str = os.getenv("PG_HOST", "127.0.0.1")
    PG_PORT: int = int(os.getenv("PG_PORT", "5432"))
    PG_DB: str = os.getenv("PG_DB", "")

    DATABASE_POOL_SIZE: int = int(os.getenv("DATABASE_POOL_SIZE", "5"))
    DATABASE_MAX_OVERFLOW: int = int(os.getenv("DATABASE_MAX_OVERFLOW", "10"))

    # CORS Configuration - STRICT in production
    ALLOWED_ORIGINS: str = os.getenv(
        "ALLOWED_ORIGINS", 
        "http://localhost:5173,http://localhost:3000" if os.getenv("APP_ENV") != "production" else ""
    )
    GTS_CORS_ORIGINS: str = os.getenv(
        "GTS_CORS_ORIGINS",
        "http://localhost:5173,http://localhost:3000" if os.getenv("APP_ENV") != "production" else ""
    )
    
    ADMIN_EMAIL: str = os.getenv("ADMIN_EMAIL", "")
    SUPPORT_EMAIL: str = os.getenv("SUPPORT_EMAIL", "")
    MAIL_FROM: str = os.getenv("MAIL_FROM", "")

    SMTP_HOST: str = os.getenv("SMTP_HOST", "")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "465"))
    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    SMTP_FROM: str = (
        os.getenv("SMTP_FROM", "")
        or os.getenv("MAIL_FROM", "")
        or os.getenv("SMTP_USER", "")
    )
    SMTP_SECURE: bool = os.getenv("SMTP_SECURE", "true").lower() in ("1", "true", "yes")

    IMAP_HOST: str = os.getenv("IMAP_HOST", "")
    IMAP_PORT: int = int(os.getenv("IMAP_PORT", "993"))
    IMAP_USER: str = os.getenv("IMAP_USER", "")
    IMAP_PASSWORD: str = os.getenv("IMAP_PASSWORD", "")
    IMAP_SSL: bool = os.getenv("IMAP_SSL", "true").lower() in ("1", "true", "yes")

    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_URL: str = os.getenv("REDIS_URL", "")

    QUO_API_KEY: str = os.getenv("QUO_API_KEY", "")
    QUO_BASE_URL: str = os.getenv("QUO_BASE_URL", "https://api.openphone.com/v1")
    QUO_AUTH_SCHEME: str = os.getenv("QUO_AUTH_SCHEME", "bearer")
    QUO_WEBHOOK_SECRET: str = os.getenv("QUO_WEBHOOK_SECRET", "")
    API_BASE_URL: str = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")
    DEFAULT_CALLER_ID: str = os.getenv("DEFAULT_CALLER_ID", "")

    TWILIO_ACCOUNT_SID: str = os.getenv("TWILIO_ACCOUNT_SID", "")
    TWILIO_AUTH_TOKEN: str = os.getenv("TWILIO_AUTH_TOKEN", "")
    TWILIO_WHATSAPP_NUMBER: str = os.getenv("TWILIO_WHATSAPP_NUMBER", "")
    TWILIO_SMS_NUMBER: str = os.getenv("TWILIO_SMS_NUMBER", "")

    FIREBASE_CREDENTIALS_PATH: str = os.getenv("FIREBASE_CREDENTIALS_PATH", "")

    POP3_HOST: str = os.getenv("POP3_HOST", "")
    POP3_PORT: int = int(os.getenv("POP3_PORT", "995"))
    POP3_USER: str = os.getenv("POP3_USER", "")
    POP3_PASSWORD: str = os.getenv("POP3_PASSWORD", "")
    POP3_SSL: bool = os.getenv("POP3_SSL", "true").lower() in ("1", "true", "yes")

    EMAIL_MAILBOXES: str = os.getenv("EMAIL_MAILBOXES", "")
    EMAIL_DEFAULT_MODE: str = os.getenv("EMAIL_DEFAULT_MODE", "BOT")
    EMAIL_CREDENTIALS_KEY: str = os.getenv("EMAIL_CREDENTIALS_KEY", "")

    HCAPTCHA_SECRET: Optional[str] = os.getenv("HCAPTCHA_SECRET")
    HCAPTCHA_SITEKEY: Optional[str] = os.getenv("HCAPTCHA_SITEKEY")
    HCAPTCHA_DISABLED: bool = os.getenv("HCAPTCHA_DISABLED", "").lower() in ("1", "true", "yes")

    # External API Keys for AI Bots
    OPENWEATHER_API_KEY: str = os.getenv("OPENWEATHER_API_KEY", "")
    ALPHA_VANTAGE_KEY: str = os.getenv("ALPHA_VANTAGE_KEY", "")
    MARKETAUX_KEY: str = os.getenv("MARKETAUX_KEY", "")
    GOV_API_KEY: str = os.getenv("GOV_API_KEY", "")

    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:5173")
    ADMIN_URL: str = os.getenv("ADMIN_URL", "http://localhost:5173")

    # JWT / Auth - CRITICAL: Must be changed in production
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-change-me")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", os.getenv("GTS_JWT_SECRET", SECRET_KEY))
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", ALGORITHM)
    REFRESH_TOKEN_SECRET: str = os.getenv("REFRESH_TOKEN_SECRET", JWT_SECRET_KEY)
    DEFAULT_SIGNUP_TENANT_ID: str = os.getenv(
        "DEFAULT_SIGNUP_TENANT_ID",
        "01014c0f-cc06-44e4-a27a-8275adf901d6",
    )
    
    # Security validation
    def __post_init__(self):
        """Validate security configuration on startup"""
        # CRITICAL: Validate SECRET_KEY in production
        if self.APP_ENV == "production":
            if not self.SECRET_KEY or self.SECRET_KEY == "dev-secret-change-me":
                raise ValueError(
                    "CRITICAL SECURITY ERROR: SECRET_KEY must be changed in production! "
                    "Set a strong SECRET_KEY in environment variables."
                )
            if len(self.SECRET_KEY) < 32:
                raise ValueError(
                    "CRITICAL SECURITY ERROR: SECRET_KEY must be at least 32 characters long in production!"
                )
            
            # Validate CORS is configured
            if not self.ALLOWED_ORIGINS and not self.GTS_CORS_ORIGINS:
                raise ValueError(
                    "SECURITY WARNING: CORS origins not configured in production! "
                    "Set ALLOWED_ORIGINS or GTS_CORS_ORIGINS environment variable."
                )
        
        # Warning for development
        elif self.SECRET_KEY == "dev-secret-change-me":
            import warnings
            warnings.warn(
                "Using default SECRET_KEY in development. This is fine for dev but never use in production!",
                UserWarning
            )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15")  # Session timeout: 15 minutes of inactivity
    )
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "30"))

    # Extended JWT settings used by core.security
    jwt_secret: str = (
        os.getenv("JWT_SECRET")
        or os.getenv("JWT_SECRET_KEY")
        or os.getenv("GTS_JWT_SECRET")
        or SECRET_KEY
    )
    jwt_access_ttl_minutes: int = int(os.getenv("JWT_ACCESS_TTL_MINUTES", str(ACCESS_TOKEN_EXPIRE_MINUTES)))
    jwt_issuer: str = os.getenv("JWT_ISSUER", "gts")
    jwt_audience: str = os.getenv("JWT_AUDIENCE", "gts-users")
    jwt_active_kid: str = os.getenv("JWT_ACTIVE_KID", "default")
    jwt_private_key_pem: str = os.getenv("JWT_PRIVATE_KEY_PEM", "")
    jwt_public_key_pem: str = os.getenv("JWT_PUBLIC_KEY_PEM", "")

    # Rate Limiting - Increased for production
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = int(
        os.getenv(
            "RATE_LIMIT_REQUESTS_PER_MINUTE",
            "1000" if os.getenv("APP_ENV") == "production" else "120"
        )
    )
    
    # Security Settings
    ENFORCE_HTTPS: bool = os.getenv("ENFORCE_HTTPS", "true" if os.getenv("APP_ENV") == "production" else "false").lower() in ("1", "true", "yes")
    ENABLE_SECURITY_HEADERS: bool = os.getenv("ENABLE_SECURITY_HEADERS", "true").lower() in ("1", "true", "yes")
    
    # Monitoring & Error Tracking
    SENTRY_DSN: Optional[str] = os.getenv("SENTRY_DSN")
    SENTRY_ENVIRONMENT: str = os.getenv("SENTRY_ENVIRONMENT", "development")
    SENTRY_TRACES_SAMPLE_RATE: float = float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.1"))
    ENABLE_SENTRY: bool = os.getenv("ENABLE_SENTRY", "false").lower() in ("1", "true", "yes")

    REGISTRATION_DISABLED: bool = os.getenv("REGISTRATION_DISABLED", "false").lower() in (
        "1",
        "true",
        "yes",
    )
    REGISTRATION_DISABLED_DETAIL: str = os.getenv(
        "REGISTRATION_DISABLED_DETAIL",
        "Registration is temporarily closed. Please contact the administrator.",
    ).strip()
    REGISTRATION_REOPEN_DATE: Optional[str] = os.getenv("REGISTRATION_REOPEN_DATE")
    REGISTRATION_CONTACT_EMAIL: str = os.getenv("REGISTRATION_CONTACT_EMAIL", "")

    # Social media auto-posting settings
    auto_posting_enabled: bool = os.getenv("AUTO_POSTING_ENABLED", "false").lower() in ("1", "true", "yes")
    auto_post_new_blogs: bool = os.getenv("AUTO_POST_NEW_BLOGS", "false").lower() in ("1", "true", "yes")
    auto_post_new_services: bool = os.getenv("AUTO_POST_NEW_SERVICES", "false").lower() in ("1", "true", "yes")
    optimal_posting_enabled: bool = os.getenv("OPTIMAL_POSTING_ENABLED", "false").lower() in ("1", "true", "yes")
    max_posts_per_day: int = int(os.getenv("MAX_POSTS_PER_DAY", "5"))


settings = Settings()

__all__ = ["Settings", "settings"]
        async def init_db():
    """
    Initialize database connection and create tables if needed.
    This function is called during pre-deploy on Render.
    """
    import logging
    from sqlalchemy.ext.asyncio import create_async_engine
    from sqlalchemy import text
    
    logger = logging.getLogger(__name__)
    
    # Get database URL
    db_url = settings.ASYNC_DATABASE_URL or settings.DATABASE_URL
    
    if not db_url:
        logger.warning("No database URL found, skipping database initialization")
        return
    
    logger.info(f"Initializing database connection to: {db_url.split('@')[-1] if '@' in db_url else db_url}")
    
    # Create engine
    engine = create_async_engine(db_url, echo=False)
    
    try:
        # Test connection
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
            logger.info("✅ Database connection successful")
        
        # Optionally create tables if using SQLAlchemy models
        # from backend.database.base import Base
        # async with engine.begin() as conn:
        #     await conn.run_sync(Base.metadata.create_all)
        
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise
    finally:
        await engine.dispose()