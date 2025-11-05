#!/bin/bash

# Create remaining service skeletons
for service in normalize analytics llm engagement reporting qc identity connectors; do
    mkdir -p services/$service/app
    
    # Create Dockerfile
    cat > services/$service/Dockerfile << DOCKERFILE
FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY ./app /app
HEALTHCHECK CMD curl -f http://localhost:8000/health || exit 1
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
DOCKERFILE
    
    # Create requirements.txt
    cat > services/$service/requirements.txt << REQS
fastapi==0.109.0
uvicorn[standard]==0.27.0
pydantic==2.5.3
sqlalchemy==2.0.25
asyncpg==0.29.0
httpx==0.26.0
REQS
    
    # Create basic main.py
    cat > services/$service/app/main.py << PYFILE
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Aura Audit AI - ${service^} Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "$service", "version": "1.0.0"}

@app.get("/")
async def root():
    return {"service": "$service", "status": "ready"}
PYFILE

    echo "Created service: $service"
done

echo "All services created successfully!"
