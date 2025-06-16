import pdfplumber
from typing import Dict, Any, Optional
import logging
from app.core.config import settings
from openai import OpenAI
from datetime import datetime
import hashlib
import json
from app.services.cache_service import CacheService

logger = logging.getLogger(__name__)

class EmailGenerator:
    def __init__(self):
        """
        Initialize EmailGenerator with OpenAI and caching
        """
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.cache_service = CacheService()
        self.cache_key_prefix = "email_generator_"

    def _generate_cache_key(self, cv_text: str, job_title: str, full_name: str) -> str:
        """
        Generate a cache key based on input parameters
        """
        key = f"{cv_text}_{job_title}_{full_name}_{datetime.now().strftime('%Y%m%d')}"
        return f"{self.cache_key_prefix}{hashlib.md5(key.encode()).hexdigest()}"

    def extract_cv_text(self, file_path: str) -> str:
        """
        Extract text from PDF CV using pdfplumber with improved error handling
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            str: Extracted text from PDF
            
        Raises:
            ValueError: If file is not a valid PDF or text extraction fails
        """
        try:
            if not file_path.lower().endswith('.pdf'):
                raise ValueError("File must be a PDF")
                
            with pdfplumber.open(file_path) as pdf:
                text = ""
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text.strip() + "\n"
                
                if not text.strip():
                    raise ValueError("No text could be extracted from PDF")
                    
                return text
                
        except Exception as e:
            logger.error(f"Error extracting CV text: {str(e)}")
            raise ValueError(f"Failed to extract text from CV: {str(e)}")

    def _format_ai_prompt(self, cv_text: str, full_name: str, job_title: str, company_email: str) -> str:
        """
        Format the AI prompt with proper structure
        """
        return f"""
        You are a professional recruiter. Generate a professional email to apply for the position of {job_title}.
        
        CV Text:
        {cv_text}
        
        Requirements:
        1. Create a compelling subject line (max 100 characters)
        2. Write a professional email body that highlights relevant experience from the CV
        3. Keep it concise and professional (max 500 words)
        4. Address it to {company_email}
        5. Sign off with {full_name}
        6. Format: 
           Subject: [subject line]
           Body: [email body]
        """

    async def generate_email_content(
        self, 
        cv_text: str, 
        full_name: str, 
        job_title: str, 
        company_email: str,
        use_cache: bool = True
    ) -> Dict[str, str]:
        """
        Generate professional email subject and body using AI with caching
        
        Args:
            cv_text: Extracted text from CV
            full_name: Applicant's full name
            job_title: Job position title
            company_email: Company's email address
            use_cache: Whether to use cached results
            
        Returns:
            Dict[str, str]: Dictionary containing email subject and body
            
        Raises:
            ValueError: If AI response is invalid or cache error occurs
        """
        try:
            cache_key = self._generate_cache_key(cv_text, job_title, full_name)
            
            # Check cache first
            if use_cache:
                cached_result = await self.cache_service.get(cache_key)
                if cached_result:
                    logger.info(f"Using cached email content for {cache_key}")
                    return json.loads(cached_result)
            
            # Generate prompt
            prompt = self._format_ai_prompt(cv_text, full_name, job_title, company_email)
            
            # Generate email content
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a professional recruiter."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000,
                timeout=30  # 30 second timeout
            )

            content = response.choices[0].message.content
            
            # Parse response
            parts = content.split("\n\n")
            if len(parts) < 2:
                raise ValueError("Invalid AI response format")
                
            subject = parts[0].strip()
            body = "\n\n".join(parts[1:]).strip()
            
            # Validate output
            if len(subject) > 100:
                subject = subject[:97] + "..."
            
            if len(body.split()) > 500:
                body = " ".join(body.split()[:497]) + "..."
            
            result = {
                "subject": subject,
                "body": body
            }
            
            # Cache the result
            await self.cache_service.set(cache_key, json.dumps(result), expire=86400)  # Cache for 24 hours
            
            return result
            
        except Exception as e:
            logger.error(f"Error generating email content: {str(e)}")
            # Fallback to default content
            return {
                "subject": f"Application for {job_title} Position",
                "body": f"Dear Hiring Manager,\n\nI am writing to express my interest in the {job_title} position.\n\nBest regards,\n{full_name}"
            }
