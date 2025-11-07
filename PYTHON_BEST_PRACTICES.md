# Python Best Practices for Aura Audit AI

This document outlines the best practices, conventions, and guidelines for managing the Aura Audit AI Python codebase. Following these practices ensures code quality, maintainability, and scalability across all 25 microservices.

## Table of Contents

1. [Repository Structure](#repository-structure)
2. [Shared Libraries](#shared-libraries)
3. [Code Quality & Standards](#code-quality--standards)
4. [Testing Practices](#testing-practices)
5. [Development Workflow](#development-workflow)
6. [CI/CD Pipeline](#cicd-pipeline)
7. [Service Development](#service-development)
8. [Database Practices](#database-practices)
9. [Security Guidelines](#security-guidelines)
10. [Performance Considerations](#performance-considerations)

---

## Repository Structure

### Monorepo Organization

Aura Audit AI uses a **monorepo structure** with 25 microservices:

```
Data-Norm-2/
├── services/               # 25 microservices
│   ├── identity/          # Authentication & authorization
│   ├── analytics/         # Journal entry testing
│   ├── engagement/        # Engagement management
│   └── .../              # 22 more services
├── lib/                   # Shared libraries
│   ├── common_core/       # Common utilities (NEW)
│   ├── service_client/    # Service-to-service communication
│   └── event_bus/         # Event-driven communication
├── frontend/              # Next.js main app
├── admin-portal/          # React admin interface
├── client-portal/         # React client interface
├── database/              # Database migrations
├── infra/                 # Infrastructure as Code
├── scripts/               # Development scripts
├── pyproject.toml         # Root project configuration
├── Makefile               # Development automation
└── .pre-commit-config.yaml # Pre-commit hooks

```

### Service Structure

Each microservice follows a consistent structure:

```
services/<service-name>/
├── app/
│   ├── __init__.py
│   ├── main.py           # FastAPI application
│   ├── config.py         # Configuration management
│   ├── database.py       # Database connection
│   ├── models.py         # SQLAlchemy models
│   ├── schemas.py        # Pydantic schemas
│   └── <feature>.py      # Feature modules
├── tests/
│   ├── __init__.py
│   ├── conftest.py       # Pytest fixtures
│   ├── test_*.py         # Test files
│   └── unit/             # Unit tests
│       └── integration/  # Integration tests
├── Dockerfile            # Container definition
└── requirements.txt      # Python dependencies
```

---

## Shared Libraries

### 1. Common Core (`lib/common_core/`)

**NEW LIBRARY** - Provides standardized patterns for all services:

```python
from lib.common_core import (
    # Exceptions
    AuraException, NotFoundError, ValidationError,
    AuthenticationError, AuthorizationError,

    # Schemas
    HealthResponse, PaginatedResponse, ErrorResponse,

    # Middleware
    setup_cors_middleware, setup_error_handlers,
    setup_logging_middleware,

    # Logging
    setup_logging,

    # Dependencies
    get_current_user_from_token, require_roles,
)
```

**Usage Example:**

```python
# services/my-service/app/main.py
from fastapi import FastAPI, Depends
from lib.common_core import (
    setup_all_middleware,
    setup_logging,
    HealthResponse,
    NotFoundError,
    require_roles,
)

# Setup logging
logger = setup_logging("my-service", log_level="INFO")

app = FastAPI(title="My Service")

# Setup all middleware (CORS, error handlers, logging)
setup_all_middleware(app, allowed_origins=["*"])

@app.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(
        status="healthy",
        service="my-service",
        version="1.0.0"
    )

@app.get("/protected")
async def protected_route(
    user: dict = Depends(require_roles(
        allowed_roles=["partner", "manager"],
        jwt_secret=settings.JWT_SECRET
    ))
):
    return {"message": "Authenticated!"}
```

### 2. Service Client (`lib/service_client/`)

For service-to-service HTTP communication with circuit breaker and retry logic:

```python
from lib.service_client import ServiceClient, ServiceRegistry

# Create client
client = ServiceClient("analytics", auth_token="Bearer ...")

# Make requests
response = await client.get("/je-testing/engagement-123")
response = await client.post("/anomalies/detect", json={"method": "zscore"})

# Check health
is_healthy = await client.health_check()
```

### 3. Event Bus (`lib/event_bus/`)

For asynchronous event-driven communication via Redis:

```python
from lib.event_bus import EventBus, get_event_bus
from lib.event_bus.schemas import EngagementCreatedEvent

# Get event bus
event_bus = await get_event_bus()

# Publish event
event = EngagementCreatedEvent(
    event_id=str(uuid4()),
    service="engagement",
    engagement_id=engagement_id,
    client_id=client_id
)
await event_bus.publish("engagement.created", event)

# Subscribe to events
async def handle_engagement_created(event: EngagementCreatedEvent):
    logger.info(f"New engagement: {event.engagement_id}")

await event_bus.subscribe(
    "engagement.created",
    EngagementCreatedEvent,
    handle_engagement_created
)
```

---

## Code Quality & Standards

### Python Version

- **Minimum:** Python 3.11+
- **Recommended:** Python 3.11 for all services

### Code Formatting

We use **Black** with a line length of 100:

```bash
# Format all code
make format

# Or directly
black services/ lib/ --line-length 100
```

### Import Sorting

We use **isort** with the black profile:

```bash
# Sort imports
isort services/ lib/ --profile black
```

### Linting

We use **Ruff** as our primary linter:

```bash
# Run linter
make lint

# Or directly
ruff check services/ lib/ --fix
```

**Configuration:** See `pyproject.toml`:

```toml
[tool.ruff]
line-length = 120
target-version = "py311"
select = ["E", "F", "I", "N", "W", "UP"]
ignore = ["E501"]
```

### Type Checking

We use **MyPy** for type checking:

```bash
# Run type checker
make type-check

# Or directly
mypy services/ --ignore-missing-imports
```

### Security Scanning

We use **Bandit** for security scanning:

```bash
# Run security scanner
make security-check

# Or directly
bandit -r services/ lib/ -c pyproject.toml
```

---

## Testing Practices

### Test Framework

We use **pytest** with async support:

```python
# tests/test_example.py
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
```

### Test Organization

```
tests/
├── conftest.py          # Shared fixtures
├── unit/                # Unit tests (fast, isolated)
│   ├── test_models.py
│   └── test_schemas.py
└── integration/         # Integration tests (DB, API)
    └── test_api.py
```

### Coverage Requirements

- **Minimum coverage:** 70% (enforced in CI)
- **Target coverage:** 80%+

```bash
# Run tests with coverage
make test

# Run tests for specific service
make test-service SERVICE=identity

# Run fast tests (no coverage)
make test-fast
```

### Test Markers

Use markers to categorize tests:

```python
@pytest.mark.unit
def test_simple_function():
    assert add(2, 2) == 4

@pytest.mark.integration
@pytest.mark.asyncio
async def test_database_query(db_session):
    result = await db_session.execute(select(User))
    assert result is not None

@pytest.mark.slow
def test_long_running_process():
    # Test that takes >5 seconds
    pass
```

Run specific markers:

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Skip slow tests
pytest -m "not slow"
```

### Test Fixtures

**Example `conftest.py`:**

```python
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from httpx import AsyncClient

from app.main import app
from app.database import Base, get_db

TEST_DATABASE_URL = "postgresql+asyncpg://test:test@localhost:5432/test_db"

@pytest_asyncio.fixture(scope="function")
async def test_db() -> AsyncSession:
    """Create test database and session"""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSession(engine) as session:
        yield session

    await engine.dispose()


@pytest_asyncio.fixture
async def client(test_db: AsyncSession) -> AsyncClient:
    """Create test client with database override"""

    async def override_get_db():
        yield test_db

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()
```

---

## Development Workflow

### Initial Setup

```bash
# 1. Clone repository
git clone <repo-url>
cd Data-Norm-2

# 2. Run development setup script
./scripts/dev-setup.sh

# 3. Configure environment
cp .env.example .env
# Edit .env with your configuration

# 4. Start services
make docker-up

# 5. Run migrations
make db-migrate

# 6. Run tests
make test
```

### Daily Development

```bash
# Format and lint before committing
make format lint

# Run tests
make test

# Run all quality checks
make check

# View service logs
make docker-logs
```

### Pre-Commit Hooks

Pre-commit hooks run automatically on `git commit`. To run manually:

```bash
# Run all hooks
make pre-commit

# Or directly
pre-commit run --all-files
```

**Hooks configured:**
- Black (code formatting)
- isort (import sorting)
- Ruff (linting with auto-fix)
- MyPy (type checking)
- Bandit (security scanning)
- Trailing whitespace removal
- JSON/YAML validation
- Large file detection
- Private key detection

### Creating a New Service

```bash
# 1. Create service directory
mkdir -p services/my-new-service/app services/my-new-service/tests

# 2. Create main.py
cat > services/my-new-service/app/main.py <<EOF
from fastapi import FastAPI
from lib.common_core import setup_all_middleware, setup_logging, HealthResponse

logger = setup_logging("my-new-service")
app = FastAPI(title="My New Service")
setup_all_middleware(app)

@app.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(status="healthy", service="my-new-service", version="1.0.0")
EOF

# 3. Create requirements.txt
cat > services/my-new-service/requirements.txt <<EOF
fastapi==0.109.0
uvicorn[standard]==0.27.0
pydantic==2.5.3
pydantic-settings==2.1.0
EOF

# 4. Create Dockerfile
cat > services/my-new-service/Dockerfile <<EOF
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY app/ ./app/
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF

# 5. Create tests
mkdir services/my-new-service/tests
touch services/my-new-service/tests/__init__.py
touch services/my-new-service/tests/conftest.py
touch services/my-new-service/tests/test_health.py

# 6. Add to CI/CD matrix (edit .github/workflows/ci.yml)
```

---

## CI/CD Pipeline

### GitHub Actions Workflows

**1. Continuous Integration (`.github/workflows/ci.yml`)**

Runs on every push and PR:

- ✅ Backend tests (matrix for 11 services)
- ✅ Frontend tests (linting, type checking, unit tests)
- ✅ Code quality checks (Ruff linting)
- ✅ **Dependency security audit (pip-audit, safety, npm audit)**

**2. Azure Deployment (`.github/workflows/deploy-azure.yml`)**

Runs on push to main:

- 🚀 Build and push Docker images
- 🔒 Security scanning
- ☁️ Terraform infrastructure deployment
- ⚙️ Kubernetes rollout

**3. OpenAPI Documentation (`.github/workflows/openapi.yml`)**

Updates API docs on spec changes

### Running CI Locally

```bash
# Run complete CI pipeline locally
make ci
```

This runs:
1. Code formatting
2. Linting
3. Type checking
4. Security scanning
5. Tests with coverage

---

## Service Development

### Configuration Management

Use **Pydantic Settings** for configuration:

```python
# app/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Service
    SERVICE_NAME: str = "my-service"
    LOG_LEVEL: str = "INFO"

    # Database
    DATABASE_URL: str
    DATABASE_POOL_SIZE: int = 20

    # Security
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
```

### Database Models

Use **SQLAlchemy 2.0** with async:

```python
# app/models.py
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base
import uuid
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

### Pydantic Schemas

```python
# app/schemas.py
from pydantic import BaseModel, EmailStr, Field
from uuid import UUID
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=1, max_length=255)
    password: str = Field(..., min_length=8)


class UserResponse(BaseModel):
    id: UUID
    email: str
    full_name: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
```

### Error Handling

Use common exceptions from `lib.common_core`:

```python
from lib.common_core import NotFoundError, ValidationError, AuthenticationError

@app.get("/users/{user_id}")
async def get_user(user_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise NotFoundError("User", str(user_id))

    return UserResponse.model_validate(user)
```

---

## Database Practices

### Migrations

Use SQL migration files in `database/migrations/`:

```sql
-- database/migrations/0001_init.sql
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) NOT NULL UNIQUE,
    full_name VARCHAR(255) NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);
```

Run migrations:

```bash
make db-migrate
```

### Row-Level Security (RLS)

Enable RLS for multi-tenant isolation:

```sql
ALTER TABLE engagements ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation ON engagements
    USING (organization_id = current_setting('app.current_organization_id')::UUID);
```

### Connection Pooling

Configure appropriate pool sizes:

```python
engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=20,          # Maximum concurrent connections
    max_overflow=10,       # Additional overflow connections
    pool_pre_ping=True,    # Test connections before use
    echo=False             # Disable SQL logging in production
)
```

---

## Security Guidelines

### Authentication

- Use JWT tokens from the `identity` service
- Token validation with `lib.common_core.dependencies`
- Always validate tokens in protected routes

### Password Hashing

Use bcrypt with appropriate cost factor:

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

hashed_password = pwd_context.hash("plain_password")
is_valid = pwd_context.verify("plain_password", hashed_password)
```

### Secrets Management

- **NEVER** commit secrets to git
- Use `.env` files (gitignored)
- Use environment variables in production
- Rotate secrets regularly

### Input Validation

- Use Pydantic for request validation
- Validate all user inputs
- Sanitize inputs for SQL, XSS, command injection

### SQL Injection Prevention

- **ALWAYS** use parameterized queries
- Never concatenate user input into SQL

```python
# ✅ GOOD - Parameterized
result = await db.execute(
    select(User).where(User.email == email)
)

# ❌ BAD - SQL injection risk
query = f"SELECT * FROM users WHERE email = '{email}'"  # NEVER DO THIS
```

---

## Performance Considerations

### Async/Await

Use async for all I/O operations:

```python
# ✅ GOOD - Async I/O
async def get_user(user_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()

# ❌ BAD - Blocking I/O
def get_user_sync(user_id: UUID):
    # This blocks the event loop
    pass
```

### Database Queries

- Use `select()` instead of `Query`
- Use `scalar_one_or_none()` for single results
- Use `scalars().all()` for multiple results
- Add indexes for frequently queried columns
- Use `EXPLAIN ANALYZE` for slow queries

### Caching

Use Redis for caching:

```python
import redis.asyncio as redis

# Cache expensive operations
cache_key = f"user:{user_id}"
cached = await redis_client.get(cache_key)

if cached:
    return json.loads(cached)

# Expensive operation
user = await db.execute(select(User).where(User.id == user_id))

# Cache result
await redis_client.set(cache_key, json.dumps(user), ex=3600)  # 1 hour TTL
```

### Background Tasks

Use FastAPI's background tasks for non-blocking operations:

```python
from fastapi import BackgroundTasks

async def send_email(email: str, subject: str, body: str):
    # Email sending logic
    pass

@app.post("/users")
async def create_user(
    user_data: UserCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    user = User(**user_data.dict())
    db.add(user)
    await db.commit()

    # Send welcome email in background
    background_tasks.add_task(send_email, user.email, "Welcome", "Welcome to Aura!")

    return UserResponse.model_validate(user)
```

---

## Development Commands Reference

### Makefile Commands

```bash
# Installation
make install              # Install all dependencies
make install-dev          # Install development dependencies
make install-libs         # Install shared libraries only

# Code Quality
make format               # Format code with black and isort
make lint                 # Run ruff linter
make type-check           # Run mypy type checker
make security-check       # Run bandit security scanner
make pre-commit           # Run all pre-commit hooks

# Testing
make test                 # Run all tests with coverage
make test-service SERVICE=identity  # Test specific service
make test-fast            # Run tests without coverage (faster)
make test-unit            # Run only unit tests
make test-integration     # Run only integration tests

# Docker
make docker-build         # Build all Docker images
make docker-up            # Start all services
make docker-down          # Stop all services
make docker-logs          # View logs

# Database
make db-migrate           # Run database migrations
make db-reset             # Reset database (⚠️  DESTRUCTIVE)

# Utilities
make clean                # Clean build artifacts and cache
make check                # Run all quality checks
make ci                   # Run CI pipeline locally
make dev-setup            # Complete development setup
make help                 # Show all commands
```

### Scripts

```bash
# Development setup
./scripts/dev-setup.sh

# Run tests with options
./scripts/run-tests.sh --service identity --no-coverage
./scripts/run-tests.sh --unit
./scripts/run-tests.sh --fast

# Format code
./scripts/format-code.sh
```

---

## Additional Resources

- **Architecture Documentation:** `ARCHITECTURE.md`
- **API Documentation:** http://localhost:8000/docs (when running)
- **Test Report:** `TEST_REPORT.md`
- **Azure Deployment:** `AZURE_DEPLOYMENT.md`
- **OpenAPI Specs:** `openapi/`

---

## Questions or Issues?

- Create an issue in the repository
- Contact the development team
- Review existing documentation

**Last Updated:** November 2025
**Version:** 1.0.0
