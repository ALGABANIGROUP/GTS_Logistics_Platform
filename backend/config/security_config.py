import os
from functools import lru_cache
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings with security"""
    
    # Environment
    environment: str = os.getenv("ENVIRONMENT", "development")
    is_production: bool = environment == "production"
    
    # Database
    database_url: str
    
    # Security
    jwt_secret: str
    encryption_key: str
    
    # API Keys (external services)
    openai_api_key: str
    hcaptcha_secret: str
    hcaptcha_sitekey: str
    
    # Token settings
    access_token_expire_minutes: int = 15  # Session timeout: 15 minutes of inactivity
    refresh_token_expire_days: int = 7
    
    # CORS
    allowed_origins: list = [
        "http://localhost:5173",
        "http://localhost:3000",
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    def __init__(self, **data):
        super().__init__(**data)
        
        # Validate critical secrets in production
        if self.is_production:
            if not self.jwt_secret or len(self.jwt_secret) < 32:
                raise ValueError("JWT_SECRET must be 32+ chars in production")
            if not self.encryption_key or len(self.encryption_key) < 32:
                raise ValueError("ENCRYPTION_KEY must be 32+ chars in production")
            if self.database_url.startswith("postgresql://localhost"):
                raise ValueError("Cannot connect to localhost database in production")

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()

# Usage in FastAPI
from fastapi import FastAPI

settings = get_settings()
app = FastAPI()

try:
    from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware
except Exception:  # pragma: no cover - optional in some boot paths
    HTTPSRedirectMiddleware = None

if settings.is_production and HTTPSRedirectMiddleware is not None:
    app.add_middleware(HTTPSRedirectMiddleware)  # Force HTTPS

# Security remediation checklist moved into a Python structure so this module
# remains importable.
SECURITY_REMEDIATION_CHECKLIST = {
    "immediate": [
        "Revoke PostgreSQL user password",
        "Revoke OpenAI API Key",
        "Regenerate hCaptcha secret",
        "Generate new JWT_SECRET",
        "Generate new ENCRYPTION_KEY",
        "Remove .env from git history",
        "Update .gitignore",
    ],
    "short_term": [
        "Rotate all API keys",
        "Review git logs for secret exposure",
        "Update all documentation",
        "Run security audit",
        "Deploy with new secrets",
    ],
    "long_term": [
        "Implement secrets management",
        "Implement secret rotation schedule",
        "Set up git secret scanning",
        "Run regular security audits",
        "Provide team security training",
    ],
}
