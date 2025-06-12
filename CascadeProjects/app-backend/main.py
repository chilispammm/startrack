from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from transformers import pipeline
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI()

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Email sending
def send_email(sender_email: str, sender_password: str, recipient_email: str, subject: str, body: str, cv_path: str):
    try:
        msg = MIMEMultipart()
        msg['From'] = sender_email   
        msg['To'] = recipient_email  
        msg['Subject'] = subject 
        msg.attach(MIMEText(body, 'plain'))

        if cv_path and os.path.exists(cv_path):
            with open(cv_path, 'rb') as f:
                cv_attachment = MIMEApplication(f.read(), _subtype='pdf')
                cv_attachment.add_header('Content-Disposition', 'attachment', filename=os.path.basename(cv_path))
                msg.attach(cv_attachment)

        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
        return True, "Email sent successfully"
    except Exception as e:
        return False, f"Failed to send email: {str(e)}"

# Google Sheets logging
def setup_google_sheets_logging(credentials_json: str, sheet_name: str = "OpportunityAI_Logs"):
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name(credentials_json, scope)
        client = gspread.authorize(creds)
        try:
            sheet = client.open(sheet_name).sheet1
        except gspread.exceptions.SpreadsheetNotFound:
            sheet = client.create(sheet_name).sheet1
            sheet.append_row(["Timestamp", "Full Name", "User Email", "Company Email", "Job Title"])
        return sheet
    except Exception as e:
        logger.error(f"Failed to setup sheet: {e}")
        return None

def log_application(sheet, full_name: str, user_email: str, company_email: str, job_title: str):
    try:
        timestamp = datetime.now().isoformat()
        sheet.append_row([timestamp, full_name, user_email, company_email, job_title])
        return True, "Logged successfully"
    except Exception as e:
        return False, f"Failed to log: {str(e)}"

# Email content generation
def generate_email_content(full_name: str, job_title: str, company_name: str):
    try:
        generator = pipeline('text-generation', model='distilgpt2')
        subject = f"Application for {job_title} at {company_name}"
        body_prompt = (
            f"Generate a short, professional email for a job application. Address it to the hiring manager at {company_name}, "
            f"applying for the {job_title} position. Mention the applicant's name, {full_name}. Keep it under 150 words. Use a professional tone."
        )
        try:
            body = generator(body_prompt, max_length=100, num_return_sequences=1, pad_token_id=generator.tokenizer.eos_token_id)[0]['generated_text']
            body = body.split('\n')[0].strip()
            body = f"Dear Hiring Manager,\n\n{body}\n\nBest regards,\n{full_name}"
        except Exception as e:
            logger.error(f"Error generating email body: {e}")
            body = (
                f"Dear Hiring Manager,\n\n"
                f"I am excited to apply for the {job_title} position at {company_name}. "
                f"With my skills and passion, I believe I can contribute significantly to your team. "
                f"Please find my CV attached for your review.\n\n"
                f"Best regards,\n{full_name}"
            )
        return {"subject": subject, "body": body}
    except Exception as e:
        logger.error(f"Failed to generate email content: {str(e)}")
        return {"subject": f"Application for {job_title}", "body": f"Dear Hiring Manager,\n\nPlease find my application.\n\nBest,\n{full_name}"}

@app.post("/send-application")
async def send_application(
    full_name: str = Form(...),
    user_email: str = Form(...),
    company_email: str = Form(...),
    job_title: str = Form(...),
    cv_file: UploadFile = File(...)
):
    # Validate file
    if not cv_file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    if cv_file.size > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File size must be less than 5MB")

    # Save CV temporarily
    cv_path = f"temp_{cv_file.filename}"
    with open(cv_path, "wb") as f:
        f.write(await cv_file.read())

    # Generate email content
    company_name = company_email.split('@')[1].split('.')[0].capitalize()
    content = generate_email_content(full_name, job_title, company_name)

    # Send email
    sender_email = os.getenv("SENDER_EMAIL", "waynechilionje@gmail.com")
    sender_password = os.getenv("SENDER_PASSWORD", "your-app-password") ###
    success, message = send_email(
        sender_email=sender_email,
        sender_password=sender_password,
        recipient_email=company_email,
        subject=content['subject'],
        body=content['body'],
        cv_path=cv_path
    )

    # Clean up
    if os.path.exists(cv_path):
        os.remove(cv_path)

    if not success:
        logger.error(message)
        raise HTTPException(status_code=500, detail=message)

    # Log to Google Sheets
    sheet = setup_google_sheets_logging("credentials.json")
    if sheet:
        log_success, log_message = log_application(
            sheet=sheet,
            full_name=full_name,
            user_email=user_email,
            company_email=company_email,
            job_title=job_title
        )
        if not log_success:
            logger.error(log_message)

    # Return response with feedback link
    feedback_url = "https://forms.gle/xyz123"  # Replace with your form URL ###
    return {
        "message": "Application sent successfully",
        "feedback_url": feedback_url
    }
