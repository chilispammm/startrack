import pdfplumber
from typing import Dict, Any
import logging
from app.core.config import settings
from openai import OpenAI

logger = logging.getLogger(__name__)

class EmailGenerator:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

    def extract_cv_text(self, file_path: str) -> str:
        """
        Extract text from PDF CV using pdfplumber
        """
        try:
            with pdfplumber.open(file_path) as pdf:
                text = ""
                for page in pdf.pages:
                    text += page.extract_text() + "\n"
                return text
        except Exception as e:
            logger.error(f"Error extracting CV text: {str(e)}")
            raise

    def generate_email_content(self, cv_text: str, full_name: str, job_title: str, company_email: str) -> Dict[str, str]:
        """
        Generate professional email subject and body using AI
        """
        try:
            prompt = f"""
            You are a professional recruiter. Generate a professional email to apply for the position of {job_title}.
            
            CV Text:
            {cv_text}
            
            Requirements:
            1. Create a compelling subject line
            2. Write a professional email body that highlights relevant experience from the CV
            3. Keep it concise and professional
            4. Address it to {company_email}
            5. Sign off with {full_name}
            """

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a professional recruiter."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )

            content = response.choices[0].message.content
            parts = content.split("\n\n")
            
            # Extract subject and body
            subject = parts[0].strip()
            body = "\n\n".join(parts[1:]).strip()
            
            return {
                "subject": subject,
                "body": body
            }
        except Exception as e:
            logger.error(f"Error generating email content: {str(e)}")
            # Fallback to default content
            return {
                "subject": f"Application for {job_title} Position",
                "body": f"Dear Hiring Manager,\n\nI am writing to express my interest in the {job_title} position.\n\nBest regards,\n{full_name}"
            }
