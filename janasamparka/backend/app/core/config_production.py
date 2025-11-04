"""
Production environment configuration with enhanced security
"""
from pydantic_settings import BaseSettings, Field
from typing import List, Optional
import secrets
from pathlib import Path


class ProductionSettings(BaseSettings):
    """Production environment settings with security best practices"""
    
    # Application
    APP_NAME: str = "Janasamparka API"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "production"
    DEBUG: bool = False
    
    # Database - Production with connection pooling
    DATABASE_URL: str = Field(..., env="DATABASE_URL")
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 30
    DATABASE_POOL_TIMEOUT: int = 30
    DATABASE_POOL_RECYCLE: int = 3600
    
    # Enhanced Security
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30  # Shorter for production
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # OTP Settings - Production
    OTP_EXPIRY_MINUTES: int = 5
    OTP_LENGTH: int = 6
    OTP_MAX_ATTEMPTS: int = 3
    SMS_PROVIDER_API_KEY: str = Field(..., env="SMS_PROVIDER_API_KEY")
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60  # seconds
    
    # CORS - Production restrictive settings
    CORS_ORIGINS: List[str] = Field(
        default=["https://janasamparka.karnataka.gov.in"],
        env="CORS_ORIGINS"
    )
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["GET", "POST", "PUT", "PATCH", "DELETE"]
    CORS_ALLOW_HEADERS: List[str] = [
        "Content-Type", 
        "Authorization", 
        "X-Requested-With"
    ]
    
    # External APIs - Production
    BHOOMI_API_URL: Optional[str] = Field(None, env="BHOOMI_API_URL")
    BHOOMI_API_KEY: Optional[str] = Field(None, env="BHOOMI_API_KEY")
    KSNDMC_API_URL: Optional[str] = Field(None, env="KSNDMC_API_URL")
    KSNDMC_API_KEY: Optional[str] = Field(None, env="KSNDMC_API_KEY")
    APMC_API_URL: Optional[str] = Field(None, env="APMC_API_URL")
    APMC_API_KEY: Optional[str] = Field(None, env="APMC_API_KEY")
    
    # Google Cloud Services
    GOOGLE_CLOUD_PROJECT: str = Field(..., env="GOOGLE_CLOUD_PROJECT")
    GOOGLE_APPLICATION_CREDENTIALS: str = Field(..., env="GOOGLE_APPLICATION_CREDENTIALS")
    
    # Firebase - Production
    FIREBASE_CREDENTIALS_PATH: str = Field(..., env="FIREBASE_CREDENTIALS_PATH")
    FIREBASE_PROJECT_ID: str = Field(..., env="FIREBASE_PROJECT_ID")
    
    # File Uploads - Production with S3
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    UPLOAD_PROVIDER: str = "s3"  # local, s3, gcs
    AWS_ACCESS_KEY_ID: str = Field(..., env="AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: str = Field(..., env="AWS_SECRET_ACCESS_KEY")
    AWS_S3_BUCKET: str = Field(..., env="AWS_S3_BUCKET")
    AWS_REGION: str = "ap-south-1"
    
    # Redis - Production
    REDIS_URL: str = Field(..., env="REDIS_URL")
    REDIS_PASSWORD: Optional[str] = Field(None, env="REDIS_PASSWORD")
    
    # Monitoring & Logging
    SENTRY_DSN: Optional[str] = Field(None, env="SENTRY_DSN")
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    # Email - Production
    SMTP_HOST: str = Field(..., env="SMTP_HOST")
    SMTP_PORT: int = Field(587, env="SMTP_PORT")
    SMTP_USERNAME: str = Field(..., env="SMTP_USERNAME")
    SMTP_PASSWORD: str = Field(..., env="SMTP_PASSWORD")
    SMTP_USE_TLS: bool = True
    
    # Security Headers
    SECURITY_SSL_REDIRECT: bool = True
    SECURITY_HSTS_SECONDS: int = 31536000
    SECURITY_HSTS_INCLUDE_SUBDOMAINS: bool = True
    SECURITY_HSTS_PRELOAD: bool = True
    
    # Backup Configuration
    BACKUP_SCHEDULE: str = "0 2 * * *"  # Daily at 2 AM
    BACKUP_RETENTION_DAYS: int = 30
    BACKUP_S3_BUCKET: Optional[str] = Field(None, env="BACKUP_S3_BUCKET")
    
    # Performance
    ENABLE_CACHING: bool = True
    CACHE_TTL_DEFAULT: int = 300  # 5 minutes
    CACHE_TTL_LONG: int = 3600  # 1 hour
    
    class Config:
        env_file = ".env.production"
        env_file_encoding = "utf-8"
        case_sensitive = True
        
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._validate_security_settings()
    
    def _validate_security_settings(self):
        """Validate critical security settings"""
        if self.SECRET_KEY == "your-secret-key-change-this-in-production":
            raise ValueError("SECRET_KEY must be set to a secure value in production")
        
        if self.ENVIRONMENT == "production" and self.DEBUG:
            raise ValueError("DEBUG must be False in production")
        
        if not self.CORS_ORIGINS:
            raise ValueError("CORS_ORIGINS must be configured in production")


class StagingSettings(ProductionSettings):
    """Staging environment settings"""
    ENVIRONMENT: str = "staging"
    DEBUG: bool = True
    LOG_LEVEL: str = "DEBUG"
    
    # More permissive CORS for staging
    CORS_ORIGINS: List[str] = [
        "https://staging.janasamparka.karnataka.gov.in",
        "http://localhost:3000",
        "http://localhost:8080"
    ]


class DevelopmentSettings(BaseSettings):
    """Development environment settings"""
    APP_NAME: str = "Janasamparka API (Dev)"
    APP_VERSION: str = "1.0.0-dev"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Database - Docker development
    DATABASE_URL: str = "postgresql://janasamparka:janasamparka123@localhost:5433/janasamparka_db"
    
    # Security - Development defaults
    SECRET_KEY: str = "dev-secret-key-not-for-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours for dev
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # OTP - Mock for development
    OTP_EXPIRY_MINUTES: int = 5
    OTP_LENGTH: int = 6
    SMS_PROVIDER_API_KEY: str = "mock-key"
    
    # CORS - Permissive for development
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8080",
        "http://localhost:5173",
    ]
    
    # File uploads - Local for development
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024
    UPLOAD_PROVIDER: str = "local"
    UPLOAD_DIR: str = "./uploads"
    
    # Redis - Local for development
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Logging
    LOG_LEVEL: str = "DEBUG"
    LOG_FORMAT: str = "console"
    
    # Email - Mock for development
    SMTP_HOST: str = "localhost"
    SMTP_PORT: int = 1025
    SMTP_USERNAME: str = "dev"
    SMTP_PASSWORD: str = "dev"
    SMTP_USE_TLS: bool = False
    
    class Config:
        env_file = ".env.development"
        case_sensitive = True


def get_settings() -> BaseSettings:
    """Get settings based on environment"""
    env = Path(".env").name if Path(".env").exists() else "development"
    
    if "production" in env:
        return ProductionSettings()
    elif "staging" in env:
        return StagingSettings()
    else:
        return DevelopmentSettings()


# Settings instance based on environment
settings = get_settings()
