import os
from dotenv import load_dotenv
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import logging

# Configure logging
logging.basicConfig(
    filename='email_log.txt',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def send_email(to_email, subject, content):
    """
    Send an email using SendGrid API
    
    Args:
        to_email (str): Recipient email address
        subject (str): Email subject
        content (str): Email content
    
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        # Load environment variables
        load_dotenv()
        sg = SendGridAPIClient(os.getenv('SENDGRID_API_KEY'))
        
        # Create message
        message = Mail(
            from_email=os.getenv('FROM_EMAIL', 'noreply@app.com'),
            to_emails=to_email,
            subject=subject,
            html_content=content
        )
        
        # Send email
        response = sg.send(message)
        logging.info(f"Email sent successfully to {to_email}")
        logging.info(f"Response status code: {response.status_code}")
        return True
        
    except Exception as e:
        logging.error(f"Error sending email to {to_email}: {str(e)}")
        return False

if __name__ == "__main__":
    # Test email sending
    test_email = "test@example.com"
    test_subject = "Test Email from APP Backend"
    test_content = "<h1>This is a test email</h1><p>Sent from the APP backend system</p>"
    
    success = send_email(test_email, test_subject, test_content)
    if success:
        print("Test email sent successfully!")
    else:
        print("Failed to send test email. Check email_log.txt for details.")
