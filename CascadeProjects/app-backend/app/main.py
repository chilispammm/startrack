from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from app.services.email_service import EmailService
from app.core.logger import logger
from app.core.config import settings
import tempfile

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Initialize services
email_service = EmailService()

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/submit")
async def submit_form(
    name: str = Form(...),
    email: str = Form(...),
    cv: UploadFile = File(None)
):
    """
    Handle form submission.
    
    Args:
        name: Applicant's name
        email: Applicant's email
        cv: Optional CV file
    """
    try:
        # Prepare data for logging
        data = {
            "name": name,
            "email": email,
            "submission_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Save CV if provided
        cv_path = None
        if cv:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                content = await cv.read()
                temp_file.write(content)
                cv_path = temp_file.name
        
        # Send confirmation email
        success, msg = email_service.send_email(
            recipient_email=email,
            subject="Application Received",
            body=f"Thank you {name} for your application. We have received your submission.",
            cv_path=cv_path
        )
        
        if not success:
            raise HTTPException(status_code=500, detail=msg)
            
        return {"message": "Application submitted successfully", "data": data}
        
    except Exception as e:
        logger.error(f"Error processing form submission: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
