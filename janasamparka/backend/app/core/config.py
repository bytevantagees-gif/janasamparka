"""
Application configuration settings with environment-based management
"""
from pydantic_settings import BaseSettings
from typing import List, Optional
import os
from pathlib import Path


def get_environment() -> str:
    """Determine current environment"""
    env_file = Path(".env")
    if env_file.exists():
        env_name = env_file.name
        if "production" in env_name:
            return "production"
        elif "staging" in env_name:
            return "staging"
    
    # Check environment variable
    env = os.getenv("ENVIRONMENT", "development").lower()
    return env


class Settings(BaseSettings):
    """Base application settings"""
    
    # Application
    APP_NAME: str = "ಜನಮನಾ ಸಂಪರ್ಕ | JanaMana Samparka API"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = get_environment()
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "console"
    SENTRY_DSN: Optional[str] = None
    
    # Database
    DATABASE_URL: str = "postgresql://janasamparka:janasamparka123@localhost:5433/janasamparka_db"
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5433
    POSTGRES_USER: str = "janasamparka"
    POSTGRES_PASSWORD: str = "janasamparka123"
    POSTGRES_DB: str = "janasamparka_db"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # OTP Settings
    OTP_EXPIRY_MINUTES: int = 5
    OTP_LENGTH: int = 6
    
    # Firebase
    FIREBASE_CREDENTIALS_PATH: Optional[str] = None
    
    # External APIs
    BHOOMI_API_URL: Optional[str] = None
    KSNDMC_API_URL: Optional[str] = None
    APMC_API_URL: Optional[str] = None
    
    # Google Cloud
    GOOGLE_CLOUD_PROJECT: Optional[str] = None
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = None
    
    # File uploads
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    UPLOAD_DIR: str = "./uploads"

    # Outbound webhooks
    WEBHOOK_ENDPOINTS: List[str] = []
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8080",
        "http://localhost:5173",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://172.19.0.4:3000",
        "http://janasamparka_frontend:3000",
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._validate_environment_settings()
    
    def _validate_environment_settings(self):
        """Validate settings based on environment"""
        if self.ENVIRONMENT == "production":
            if self.SECRET_KEY == "your-secret-key-change-this-in-production":
                raise ValueError("SECRET_KEY must be set to a secure value in production")
            if self.DEBUG:
                raise ValueError("DEBUG must be False in production")
        elif self.ENVIRONMENT == "staging":
            if self.SECRET_KEY == "your-secret-key-change-this-in-production":
                print("⚠️  Warning: Using default SECRET_KEY in staging")


# Import environment-specific settings if available
try:
    from .config_production import get_settings as get_env_settings
    settings = get_env_settings()
except ImportError:
    # Fallback to base settings
    settings = Settings()
