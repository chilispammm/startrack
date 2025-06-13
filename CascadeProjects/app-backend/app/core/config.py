from pydantic_settings import BaseSettings
from typing import Optional, List, Dict
from enum import Enum
import os

class Environment(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"

class Settings(BaseSettings):
    # Environment
    ENVIRONMENT: Environment = Environment.DEVELOPMENT
    
    # API settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Africa Product Peers Backend"
    VERSION: str = "1.0.0"
    
    # Email settings
    SENDER_EMAIL: Optional[str] = None
    SENDER_PASSWORD: Optional[str] = None
    
    # Database settings
    DATABASE_URL: Optional[str] = None
    DATABASE_POOL_SIZE: int = 5
    
    # Redis settings
    REDIS_URL: str = "redis://localhost:6379"
    CACHE_TIMEOUT: int = 300  # 5 minutes
    
    # Rate limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_PERIOD: int = 60  # seconds
    
    # CORS settings
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "https://your-loveable-domain.com"]
    CORS_METHODS: List[str] = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    CORS_HEADERS: List[str] = ["Content-Type", "Authorization"]
    
    # Security settings
    JWT_SECRET_KEY: str = "your-secret-key"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Logging settings
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE: str = "app.log"
    LOG_MAX_BYTES: int = 10485760  # 10MB
    LOG_BACKUP_COUNT: int = 5
    
    # Email templates
    EMAIL_TEMPLATES_DIR: str = "app/templates"
    
    # File upload settings
    MAX_FILE_SIZE: int = 5 * 1024 * 1024  # 5MB
    ALLOWED_FILE_TYPES: List[str] = ["application/pdf"]
    
    # External services
    GOOGLE_SHEETS_CREDENTIALS_PATH: Optional[str] = None
    GOOGLE_SHEETS_NAME: str = "OpportunityAI_Logs"
    
    # Health check settings
    HEALTH_CHECK_PATH: str = "/health"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = 'allow'  # Allow extra fields from .env file

settings = Settings()
