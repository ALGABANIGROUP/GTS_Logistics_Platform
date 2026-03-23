import os
from pydantic import EmailStr
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Core Application Settings
    app_env: str = os.getenv("APP_ENV", "production")
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8000"))
    app_name: str = os.getenv("APP_NAME", "GTS Logistics Platform")
    app_version: str = os.getenv("APP_VERSION", "1.0.0")
    
    # Database Configuration
    database_url: str = os.getenv("DATABASE_URL", "")
    async_database_url: str = os.getenv("ASYNC_DATABASE_URL", "")
    alembic_sync_database_url: str = os.getenv("ALEMBIC_SYNC_DATABASE_URL", "")
    
    # Security & Authentication
    secret_key: str = os.getenv("SECRET_KEY", "your-super-secret-jwt-key-change-in-production-2024")
    algorithm: str = os.getenv("ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))
    
    # CORS & Email
    cors_origins: list = os.getenv("CORS_ORIGINS", "http://localhost:3000, http://127.0.0.1:3000, https://your-frontend-domain.vercel.app").split(",")
    email_from_address: EmailStr = os.getenv("EMAIL_FROM_ADDRESS", "noreply@gts-logistics.com")
    
    # SMTP Config
    smtp_server: str = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port: int = int(os.getenv("SMTP_PORT", "587"))
    smtp_username: str = os.getenv("SMTP_USERNAME", "your-email@gmail.com")
    smtp_password: str = os.getenv("SMTP_PASSWORD", "your-app-password")
    
    # Internal & External URL for AI Bots
    internal_base_url: str = os.getenv("INTERNAL_BASE_URL", "http://127.0.0.1:8000")
    external_base_url: str = os.getenv("EXTERNAL_BASE_URL", "https://gts-logistics-api.onrender.com")
    
    # AI / OpenAI Mode
    offline: bool = os.getenv("OFFLINE", "true") == "true"
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "sk-dummy-key-for-development-only")
    
    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"

# Export settings instance
settings = Settings()