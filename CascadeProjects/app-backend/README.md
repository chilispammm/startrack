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
│   ├── api/           # API routes
│   ├── core/          # Core application code
│   ├── models/        # Data models and schemas
│   ├── services/      # Business logic
│   │   ├── supabase_service.py  # Database operations
│   │   ├── email_generator.py   # AI email generation
│   │   ├── cache_service.py     # Redis caching
│   │   └── email_service.py     # Email sending
│   └── tests/         # Test files
├── alembic/           # Database migrations
├── tests/             # Additional test files
├── docker/           # Docker configuration
└── app/database/     # Database schema
```

## Development

### Running Tests

```bash
pytest
```

### Running with Docker

```bash
docker-compose up --build
```

### Testing Locally

1. Start Redis:
```bash
docker-compose up redis
```

2. Start Supabase:
```bash
docker-compose up supabase
```

3. Start the application:
```bash
docker-compose up app
```

## Rate Limiting

- 100 requests per hour per IP
- 5 requests per minute per IP
- Rate limit headers in responses:
  - X-RateLimit-Limit: 100
  - X-RateLimit-Remaining: 99
  - X-RateLimit-Reset: 3600

## Error Handling

- All errors are logged with full context
- User-friendly error messages
- Detailed error objects in API responses
- Rate limit handling with retry-after headers

## Caching

- AI-generated email content is cached for 24 hours
- Frequently accessed data is cached
- Cache invalidation based on content changes

## Contributing

1. Fork the repository
2. Create your feature branch
3. Add tests for new features
4. Update documentation
5. Commit your changes
6. Push to the branch
7. Create a Pull Request

## License

MIT License

## Support

For support, please open an issue in the GitHub repository.
This project is licensed under the MIT License - see the LICENSE file for details

## Acknowledgments

- FastAPI for the web framework
- Supabase for database and storage
- OpenAI for AI capabilities
- Redis for rate limiting and caching
