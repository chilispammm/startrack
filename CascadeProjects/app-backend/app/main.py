from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from app.services.email_service import EmailService
from app.services.ai_service import AIService
from app.services.feedback_service import FeedbackService
from app.services.supabase_service import SupabaseService
from app.core.logger import logger
from app.core.config import settings
from app.middleware.error_handling import ErrorHandlerMiddleware
from app.middleware.rate_limiter import RateLimitMiddleware, RateLimitConfig
from app.middleware.request_logger import RequestLoggerMiddleware
from app.middleware.cache import CacheMiddleware
from app.middleware.session import SessionMiddleware
from app.middleware.security import SecurityHeadersMiddleware
from app.models.schemas import ApplicationCreate, ApplicationResponse
from app.db.database import init_db, check_db_health
import tempfile
from typing import Optional
import redis
import uvicorn

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Initialize database
init_db()

# Initialize Redis client
redis_client = redis.from_url(settings.REDIS_URL)

# Initialize services
email_service = EmailService()
ai_service = AIService()
feedback_service = FeedbackService()
supabase_service = SupabaseService()

# Add middleware in order
# 1. Error handling
app.middleware("http")(ErrorHandlerMiddleware(app))

# 2. Security headers
app.middleware("http")(SecurityHeadersMiddleware(app))

# 3. Session management
app.middleware("http")(SessionMiddleware(app))

# 4. Request logging
app.middleware("http")(RequestLoggerMiddleware(app))

# 5. Rate limiting
rate_limit_config = RateLimitConfig(
    limit=settings.RATE_LIMIT_REQUESTS,
    period=settings.RATE_LIMIT_PERIOD
)
app.middleware("http")(RateLimitMiddleware(app, rate_limit_config, settings.REDIS_URL))

# 6. Cache middleware
app.middleware("http")(CacheMiddleware(app, settings.REDIS_URL, settings.CACHE_TIMEOUT))

# Add health check endpoint
@app.get("/health")
async def health_check():
    """
    Check service health status.
    """
    health = {
        "status": "healthy",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT.value,
        "dependencies": {
            "database": check_db_health(SessionLocal()),
            "redis": redis_client.ping()
        }
    }
    return health

# Add OpenAPI documentation
from app.api.docs import custom_openapi
app.openapi = custom_openapi

# Initialize services
email_service = EmailService()

# Setup CORS
@dataclass
class CORSConfig:
    origins: List[str] = field(default_factory=lambda: ["http://localhost:5173", "https://your-loveable-domain.com"])
    methods: List[str] = field(default_factory=lambda: ["GET", "POST", "PUT", "DELETE", "OPTIONS"])
    headers: List[str] = field(default_factory=lambda: ["Content-Type", "Authorization"])
    credentials: bool = True
    expose_headers: List[str] = field(default_factory=lambda: ["Content-Length", "Content-Type"])
    max_age: int = 600

# Load CORS configuration from settings
cors_config = CORSConfig()
if settings.CORS_ORIGINS:
    cors_config.origins = settings.CORS_ORIGINS

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_config.origins,
    allow_credentials=cors_config.credentials,
    allow_methods=cors_config.methods,
    allow_headers=cors_config.headers,
    expose_headers=cors_config.expose_headers,
    max_age=cors_config.max_age
)

@app.post("/send-application", response_model=ApplicationResponse)
async def send_application(
    full_name: str = Form(..., alias="fullName"),
    user_email: str = Form(..., alias="userEmail"),
    company_email: str = Form(..., alias="companyEmail"),
    job_title: str = Form(..., alias="jobTitle"),
    cv_file: UploadFile = File(None, alias="cvFile")
):
    """
    Handle job application submission.
    
    Args:
        full_name: Applicant's full name
        user_email: Applicant's email
        company_email: Company's email
        job_title: Job position
        cv_file: CV file (PDF)
    """
    try:
        # Validate request data
        application_data = ApplicationCreate(
            full_name=full_name,
            user_email=user_email,
            company_email=company_email,
            job_title=job_title,
            cv_file=cv_file.filename if cv_file else None
        )

        # Log submission to local file
        log_data = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "full_name": full_name,
            "user_email": user_email,
            "company_email": company_email,
            "job_title": job_title
        }
        
        # Write to local JSON file
        log_file = "submissions.json"
        existing_data = []
        if os.path.exists(log_file):
            try:
                with open(log_file, 'r') as f:
                    existing_data = json.load(f)
            except json.JSONDecodeError:
                pass
        
        existing_data.append(log_data)
        
        with open(log_file, 'w') as f:
            json.dump(existing_data, f, indent=2)
            
    except Exception as e:
        logger.error(f"Error logging submission: {str(e)}")

        # Validate file
        if cv_file:
            if not cv_file.filename.endswith('.pdf'):
                raise HTTPException(status_code=400, detail="Only PDF files are allowed")
            if cv_file.size > 5 * 1024 * 1024:
                raise HTTPException(status_code=400, detail="File size must be less than 5MB")

        # Save CV temporarily
        cv_path = None
        if cv_file:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                content = await cv_file.read()
                temp_file.write(content)
                cv_path = temp_file.name

        # Generate email content
        company_name = company_email.split('@')[1].split('.')[0].capitalize()
        
        # Create professional subject
        subject = f"Application for {job_title} at {company_name}"
        
        # Create professional body
        body = (
            f"Dear Hiring Manager,\n\n"
            f"I am excited to apply for the {job_title} position at {company_name}.\n\n"
            f"Please find my CV attached for your review.\n\n"
            f"Best regards,\n{full_name}"
        )
        
        # Send email
        success, msg = email_service.send_email(
            recipient_email=company_email,
            subject=subject,
            body=body,
            cv_path=cv_path
        )
        
        if not success:
            raise HTTPException(status_code=500, detail=msg)
            
        # Create feedback URL
        feedback_url = "https://forms.gle/xyz123"  # Replace with actual feedback form URL
        
        if not success:
            raise HTTPException(status_code=500, detail=msg)
            
        # Log to sheets
        data = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "full_name": full_name,
            "user_email": user_email,
            "company_email": company_email,
            "job_title": job_title
        }
        
        if not sheets_service.log_submission(data):
            logger.error("Failed to log submission to sheets")
            
        # Clean up
        if cv_path and os.path.exists(cv_path):
            os.remove(cv_path)
            
        # Return response in frontend-compatible format
        return ApplicationResponse(
            success=True,
            message="Application sent successfully",
            feedback_url="https://forms.gle/GsT98QMbEYb4HhBA7"
        )
        
    except HTTPException as e:
        logger.error(f"HTTP error: {str(e)}")
        raise
    except ValidationError as e:
        logger.error(f"Validation error: {str(e)}")
        return {
            "success": False,
            "message": "Validation error",
            "errors": {
                "fields": e.errors()
            }
        }
    except Exception as e:
        logger.error(f"Error processing application: {str(e)}")
        return {
            "success": False,
            "message": "Internal server error",
            "errors": {
                "general": str(e)
            }
        }
