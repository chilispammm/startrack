# Africa Product Peers Backend

This repository contains the backend infrastructure for the Africa Product Peers MVP project.

## Setup Instructions

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up SendGrid:
   - Create a SendGrid account
   - Set up Single Sender Authentication
   - Create a `.env` file with:
     ```
     SENDGRID_API_KEY=your_api_key_here
     FROM_EMAIL=your_verified_sender@example.com
     ```

3. Set up Google Sheets:
   - Create a Google Cloud Project
   - Enable Google Sheets API
   - Create service account credentials
   - Download credentials as `credentials.json`
   - Place `credentials.json` in the project root

4. Run test scripts:
```bash
python send_email.py
python log_submission.py
```

## Project Structure

- `send_email.py`: Email sending functionality using SendGrid
- `log_submission.py`: Google Sheets logging functionality
- `requirements.txt`: Project dependencies
- `logs/`: Directory for log files

## Testing

To test the system:
1. Run `send_email.py` to test email sending
2. Run `log_submission.py` to test Google Sheets logging
3. Verify logs in `logs/` directory
4. Check Google Sheets for test entries

## Documentation

Detailed documentation is available in Notion. Make sure to:
1. Update API keys and credentials
2. Document any changes or issues
3. Share access details with team members
