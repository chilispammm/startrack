from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import smtplib
import os
from typing import Tuple
from app.core.logger import logger
from app.core.config import settings

class EmailService:
    def __init__(self):
        self.sender_email = settings.SENDER_EMAIL
        self.sender_password = settings.SENDER_PASSWORD

    def send_email(self, recipient_email: str, subject: str, body: str, cv_path: str = None) -> Tuple[bool, str]:
        """
        Send an email with optional CV attachment.
        
        Args:
            recipient_email: Recipient's email address
            subject: Email subject
            body: Email body content
            cv_path: Optional path to CV file
            
        Returns:
            Tuple of (success, message)
        """
        try:
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = recipient_email
            msg['Subject'] = subject
            
            # Attach body
            msg.attach(MIMEText(body, 'plain'))
            
            # Attach CV if provided
            if cv_path and os.path.exists(cv_path):
                with open(cv_path, 'rb') as f:
                    cv_attachment = MIMEApplication(f.read(), _subtype='pdf')
                    cv_attachment.add_header('Content-Disposition', 'attachment', filename=os.path.basename(cv_path))
                    msg.attach(cv_attachment)
            
            # Send email
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            
            logger.info(f"Email sent successfully to {recipient_email}")
            return True, "Email sent successfully"
            
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            return False, f"Failed to send email: {str(e)}"
