FROM python:3.11-slim as base

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Production stage
FROM base as production

WORKDIR /app

# Copy only what's needed from base stage
COPY --from=base /app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY --from=base /app/app ./app
COPY --from=base /app/main.py .
COPY --from=base /app/.env .

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
