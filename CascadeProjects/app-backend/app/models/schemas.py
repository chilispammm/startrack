from pydantic import BaseModel, EmailStr, Field, validator, HttpUrl
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class ApplicationStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    ERROR = "error"
    COMPLETED = "completed"

class ApplicationBase(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    user_email: EmailStr = Field(..., description="User's email address")
    company_email: EmailStr = Field(..., description="Company's email address")
    job_title: str = Field(..., min_length=2, max_length=100)
    cv_url: Optional[HttpUrl] = Field(None, description="URL to CV file")
    status: ApplicationStatus = Field(ApplicationStatus.PENDING, description="Application status")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    @validator('full_name')
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('Full name cannot be empty')
        return v.strip()

    @validator('job_title')
    def validate_job_title(cls, v):
        if not v.strip():
            raise ValueError('Job title cannot be empty')
        return v.strip()

    @validator('cv_url')
    def validate_cv_url(cls, v):
        if v and not v.lower().endswith('.pdf'):
            raise ValueError('CV file must be a PDF')
        return v

class ApplicationCreate(ApplicationBase):
    cv_file: Optional[str] = Field(None, description="Path to CV file")
    
    @validator('cv_file')
    def validate_cv_file(cls, v):
        if v and not v.lower().endswith('.pdf'):
            raise ValueError('CV file must be a PDF')
        return v

class ApplicationUpdate(BaseModel):
    status: Optional[ApplicationStatus] = None
    email_subject: Optional[str] = Field(None, max_length=200)
    email_body: Optional[str] = Field(None, max_length=5000)

class ApplicationResponse(ApplicationBase):
    id: str = Field(..., description="Unique identifier for the application")
    email_subject: Optional[str] = Field(None, max_length=200)
    email_body: Optional[str] = Field(None, max_length=5000)
    feedback_url: Optional[str] = Field(None, description="URL for feedback form")
    errors: Optional[Dict[str, Any]] = None

    class Config:
        schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "full_name": "John Doe",
                "user_email": "john@example.com",
                "company_email": "hr@company.com",
                "job_title": "Software Engineer",
                "cv_url": "https://example.com/cvs/123.pdf",
                "status": "pending",
                "timestamp": "2025-06-16T13:55:34+03:00",
                "email_subject": "Application for Software Engineer Position",
                "email_body": "Dear Hiring Manager,\n\nI am writing to express my interest in the Software Engineer position...",
                "feedback_url": "https://forms.gle/GsT98QMbEYb4HhBA7",
                "errors": None
            }
        }

class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    status_code: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        schema_extra = {
            "example": {
                "error": "Bad Request",
                "detail": "Invalid email address",
                "status_code": 400,
                "timestamp": "2025-06-16T13:55:34+03:00"
            }
        }

class RateLimitResponse(BaseModel):
    error: str = "Rate limit exceeded"
    detail: str = "Too many requests. Please try again later."
    retry_after: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        schema_extra = {
            "example": {
                "error": "Rate limit exceeded",
                "detail": "Too many requests. Please try again later.",
                "retry_after": 60,
                "timestamp": "2025-06-16T13:55:34+03:00"
            }
        }
