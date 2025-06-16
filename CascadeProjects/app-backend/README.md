# Africa Product Peers Backend

This repository contains the backend infrastructure for the Africa Product Peers MVP project.

## Setup Instructions

1. Clone the repository

2. Create a `.env` file with the following variables:
```bash
cp .env.example .env
```

3. Update `.env` with your configuration:
```env
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
REDIS_URL=redis://localhost:6379
SMTP_USER=your_smtp_user
SMTP_PASSWORD=your_smtp_password
OPENAI_API_KEY=your_openai_api_key
```

4. Run with Docker:
```bash
docker-compose up --build
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
