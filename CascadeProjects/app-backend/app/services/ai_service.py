import openai
from typing import Dict, Optional
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

    def generate_email_subject(self, job_title: str, company_name: str) -> str:
        """
        Generate a personalized email subject.
        """
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional email subject line generator. Create compelling, professional subject lines for job applications."
                    },
                    {
                        "role": "user",
                        "content": f"Generate a professional email subject line for a job application for the position of {job_title} at {company_name}. The subject should be concise, professional, and highlight key qualifications."
                    }
                ],
                temperature=0.7,
                max_tokens=50
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Error generating email subject: {str(e)}")
            return f"Application for {job_title} Position"

    def generate_email_body(self, data: Dict[str, str]) -> str:
        """
        Generate a complete email body using AI.
        """
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional email writer specializing in job applications. Write compelling, professional emails that highlight the applicant's qualifications and enthusiasm for the position."
                    },
                    {
                        "role": "user",
                        "content": f"Write a professional job application email for the following position:\n\n"
                        f"Full Name: {data['full_name']}\n"
                        f"Job Title: {data['job_title']}\n"
                        f"Company: {data['company_email'].split('@')[1]}\n"
                        f"\nPlease write a professional email that:\n"
                        f"1. Introduces the applicant professionally\n"
                        f"2. Expresses enthusiasm for the position\n"
                        f"3. Highlights relevant qualifications\n"
                        f"4. Includes a professional closing\n"
                        f"5. Is concise but complete\n"
                        f"6. Is formatted professionally\n"
                        f"7. Includes a call to action\n"
                        f"8. Is free of errors\n"
                    }
                ],
                temperature=0.7,
                max_tokens=500
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Error generating email body: {str(e)}")
            return self._generate_fallback_email(data)

    def _generate_fallback_email(self, data: Dict[str, str]) -> str:
        """
        Generate a fallback email body if AI generation fails.
        """
        company_name = data['company_email'].split('@')[1].split('.')[0].capitalize()
        return (
            f"Dear Hiring Manager,\n\n"
            f"I am excited to apply for the {data['job_title']} position at {company_name}. "
            f"With my skills and passion, I believe I can contribute significantly to your team. "
            f"Please find my CV attached for your review.\n\n"
            f"Best regards,\n{data['full_name']}"
        )

# Initialize AI service
ai_service = AIService()
