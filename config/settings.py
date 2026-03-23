import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", 8000))
    API_TITLE = "Global Transport Laws Management System"
    API_VERSION = "1.0.0"

    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./transport_laws.db")

    UPDATE_CHECK_INTERVAL = int(os.getenv("UPDATE_CHECK_INTERVAL", 24))
    UPDATE_NOTICE_DAYS = int(os.getenv("UPDATE_NOTICE_DAYS", 90))

    SECRET_KEY = os.getenv("SECRET_KEY", "transport-laws-secret-key-2024")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 15  # Session timeout: 15 minutes of inactivity

    LEGAL_API_ENDPOINT = os.getenv("LEGAL_API_ENDPOINT", "")
    SAFETY_API_KEY = os.getenv("SAFETY_API_KEY", "")

    UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads")
    EXPORT_DIR = os.getenv("EXPORT_DIR", "./exports")

    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", "transport_laws.log")


settings = Settings()
