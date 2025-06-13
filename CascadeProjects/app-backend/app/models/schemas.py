from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime

class ApplicationBase(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    user_email: EmailStr = Field(...)
    company_email: EmailStr = Field(...)
    job_title: str = Field(..., min_length=2, max_length=100)
    cv_file: Optional[str] = None

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

class ApplicationCreate(ApplicationBase):
    cv_file: Optional[str] = Field(None, description="Path to CV file")

class ApplicationResponse(BaseModel):
    success: bool
    message: str
    feedback_url: Optional[str] = None
    errors: Optional[dict] = None

    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "message": "Application sent successfully",
                "feedback_url": "https://forms.gle/GsT98QMbEYb4HhBA7"
            }
        }
