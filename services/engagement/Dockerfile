FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy shared service client library
COPY lib/service_client /tmp/service_client
RUN pip install --no-cache-dir /tmp/service_client && rm -rf /tmp/service_client

# Copy requirements
COPY services/engagement/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY services/engagement/app /app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
