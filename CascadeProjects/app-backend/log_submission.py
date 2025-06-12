import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    filename='logs/submission_log.txt',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def setup_logging_sheet():
    """
    Set up Google Sheets API connection
    Returns:
        gspread worksheet object
    """
    try:
        # Define the scope
        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
        
        # Add your credentials file path here
        creds = ServiceAccountCredentials.from_json_keyfile_name(
            'credentials.json', scope
        )
        
        client = gspread.authorize(creds)
        # Open or create the spreadsheet
        try:
            sheet = client.open("Opportunity AI Logs")
        except gspread.exceptions.SpreadsheetNotFound:
            sheet = client.create("Opportunity AI Logs")
        
        # Get the first worksheet
        worksheet = sheet.sheet1
        
        # Create header if it doesn't exist
        headers = ['Timestamp', 'User Email', 'Job Title', 'Company Email', 
                  'Claude Status', 'Send Status', 'Errors']
        if not worksheet.row_values(1):
            worksheet.insert_row(headers, 1)
        
        return worksheet
    except Exception as e:
        logging.error(f"Error setting up Google Sheets: {str(e)}")
        raise

def log_submission(user_email, job_title, company_email, 
                  claude_status="Pending", send_status="Pending", error=""):
    """
    Log a submission to Google Sheets
    
    Args:
        user_email (str): User's email address
        job_title (str): Job position title
        company_email (str): Company's email address
        claude_status (str): Status of Claude processing
        send_status (str): Status of email sending
        error (str): Any error message
    """
    try:
        worksheet = setup_logging_sheet()
        
        # Prepare data
        data = [
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            user_email,
            job_title,
            company_email,
            claude_status,
            send_status,
            error
        ]
        
        # Append row
        worksheet.append_row(data)
        logging.info(f"Logged submission for {user_email}")
        
    except Exception as e:
        logging.error(f"Error logging submission: {str(e)}")
        raise

if __name__ == "__main__":
    # Test logging
    test_data = {
        "user_email": "test@example.com",
        "job_title": "Software Engineer",
        "company_email": "hr@company.com"
    }
    
    log_submission(**test_data)
    print("Test submission logged successfully!")
