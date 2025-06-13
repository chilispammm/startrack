from pydantic_settings import BaseSettings
import os
from typing import Optional

class Settings(BaseSettings):
    # Email settings
    SENDER_EMAIL: Optional[str] = None
    SENDER_PASSWORD: Optional[str] = None
    
    # API settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Africa Product Peers Backend"
    
    # Logging settings
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = 'allow'  # Allow extra fields from .env file

settings = Settings()
