# Opportunity AI Backend

A FastAPI-based backend service for intelligent job application submissions with AI-powered email generation and Supabase integration.

## Features

- 🤖 AI-Powered Email Generation
  - Generates professional email content based on CV content
  - Uses OpenAI for natural language processing
  - Fallback to default templates when needed

- 📦 Supabase Integration
  - PostgreSQL database for application metadata
  - Secure file storage for CV PDFs
  - Real-time updates and subscriptions
  - Row Level Security policies

- 🔐 Security Features
  - Rate limiting with Redis
  - Environment-based configuration
  - Secure file upload validation
  - Input sanitization and validation

- 🚀 Performance Optimizations
  - Multi-stage Docker build
  - Redis caching
  - Optimized database queries
  - Async/await implementation

## Prerequisites

- Python 3.8+
- Docker and Docker Compose
- Supabase account
- OpenAI API key
- Redis instance

## Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/koechsandy/opportunity-ai-send.git
cd opportunity-ai-send
```

### 2. Configuration
Create a `.env` file with the following variables:
```env
# Supabase Configuration
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key

# Redis Configuration
REDIS_URL=redis://localhost:6379

# Email Configuration
SMTP_USER=your_smtp_user
SMTP_PASSWORD=your_smtp_password

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key

# Application Configuration
API_V1_STR=/api/v1
PROJECT_NAME=opportunity-ai
```

### 3. Run with Docker
```bash
docker-compose up --build
```

The application will be available at `http://localhost:8000`

## API Documentation

### Endpoints

#### POST /api/v1/send-application
Send a job application with AI-generated email content.

Request Body:
```json
{
    "full_name": "string",
    "user_email": "string",
    "company_email": "string",
    "job_title": "string",
    "cv_file": "file"
}
```

Response:
```json
{
    "success": boolean,
    "message": "string",
    "feedback_url": "string"
}
```

## Project Structure

```
app-backend/
├── app/
│   ├── core/          # Core application configuration
│   ├── database/      # Database schemas and migrations
│   ├── middleware/    # Custom FastAPI middleware
│   ├── models/        # Pydantic models
│   ├── services/      # Business logic services
│   └── main.py        # FastAPI application entry point
├── tests/            # Test suite
├── docker/           # Docker configuration
├── logs/             # Application logs
└── .env              # Environment variables
```

## Development

### Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
uvicorn app.main:app --reload
```

### Testing

Run tests with:
```bash
pytest
```

Coverage report:
```bash
pytest --cov=app
```

## Deployment

The application is ready for deployment with Docker. Use the `docker-compose.yml` for local development and testing.

For production, modify the Docker configuration as needed and use appropriate environment variables.

## Security

- All sensitive data is stored encrypted
- Row Level Security policies in Supabase
- Environment-based configuration
- Rate limiting to prevent abuse
- Secure file upload validation

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details

## Acknowledgments

- FastAPI for the web framework
- Supabase for database and storage
- OpenAI for AI capabilities
- Redis for rate limiting and caching
