# Smoke Tests for Aura Audit AI Platform

## Overview

Smoke tests are critical post-deployment validation tests that verify the system's core integration points are functioning correctly. These tests catch integration issues early, before they impact users.

### What Smoke Tests Cover

1. **Database Transactions** (`test_database_transactions.py`)
   - Database connectivity and version verification
   - Transaction commit and rollback behavior
   - Concurrent transaction handling
   - Constraint enforcement
   - Connection pooling
   - Row-Level Security (RLS) context
   - JSONB and pgvector support

2. **Event Bus Flows** (`test_event_bus_flows.py`)
   - Redis connectivity
   - Event publishing and subscription
   - Multiple subscribers per channel
   - Event persistence and TTL
   - Retry logic and error handling
   - Dead Letter Queue (DLQ)
   - End-to-end event flows between services

3. **Service-to-Service Communication** (`test_service_communication.py`)
   - Service health checks
   - API Gateway routing
   - User authentication and authorization
   - Engagement CRUD operations
   - Pagination and filtering
   - Error handling (404, 401, 422)
   - Rate limiting
   - Concurrent request handling
   - Response times

## Running Smoke Tests

### Quick Start

```bash
# From project root
cd /home/user/Data-Norm-2

# Run all smoke tests
./tests/smoke/run_smoke_tests.sh

# Run with specific environment
./tests/smoke/run_smoke_tests.sh --env staging

# Quick mode (critical tests only)
./tests/smoke/run_smoke_tests.sh --quick

# Generate HTML report
./tests/smoke/run_smoke_tests.sh --report

# Parallel execution (faster)
./tests/smoke/run_smoke_tests.sh --parallel

# Verbose output
./tests/smoke/run_smoke_tests.sh --verbose
```

### Manual Execution with pytest

```bash
# Run all smoke tests
pytest tests/smoke -m smoke -v

# Run specific test category
pytest tests/smoke/test_database_transactions.py -v
pytest tests/smoke/test_event_bus_flows.py -v
pytest tests/smoke/test_service_communication.py -v

# Run tests matching a keyword
pytest tests/smoke -k "health" -v
pytest tests/smoke -k "connectivity" -v

# Run with coverage
pytest tests/smoke -m smoke --cov=services --cov-report=html

# Run in parallel (requires pytest-xdist)
pytest tests/smoke -m smoke -n auto
```

### Using Markers

Tests are organized with pytest markers:

```bash
# Run only database tests
pytest tests/smoke -m database

# Run only Redis/event bus tests
pytest tests/smoke -m redis

# Run only service communication tests
pytest tests/smoke -m service

# Combine markers
pytest tests/smoke -m "smoke and database"
```

## Environment Configuration

Smoke tests require environment variables to connect to services:

### Required Environment Variables

```bash
# Database
SMOKE_TEST_DATABASE_URL="postgresql+asyncpg://atlas:password@localhost:5432/atlas_test"

# Redis
SMOKE_TEST_REDIS_URL="redis://localhost:6379/1"

# API Gateway
GATEWAY_URL="http://localhost:8000"

# Timeouts
SMOKE_TEST_TIMEOUT=30
```

### Environment Files

Create environment-specific files:

- `.env.dev` - Development environment
- `.env.staging` - Staging environment
- `.env.production` - Production environment

Example `.env.staging`:

```bash
SMOKE_TEST_DATABASE_URL="postgresql+asyncpg://atlas:stagingpass@staging-db:5432/atlas"
SMOKE_TEST_REDIS_URL="redis://staging-redis:6379/0"
GATEWAY_URL="https://api.staging.auraaudit.ai"
```

## Test Architecture

### Fixtures (`conftest.py`)

Shared fixtures provide common test resources:

- `db_engine` - SQLAlchemy async engine
- `db_session` - Database session with rollback
- `redis_client` - Redis client
- `event_bus` - EventBus instance
- `http_client` - HTTP client for API calls
- `test_user_token` - Authentication token
- `auth_headers` - Pre-configured auth headers
- `test_engagement_id` - Test engagement for operations

### Test Organization

```
tests/smoke/
├── conftest.py                      # Shared fixtures and configuration
├── test_database_transactions.py    # Database integration tests
├── test_event_bus_flows.py          # Event bus integration tests
├── test_service_communication.py    # Service API integration tests
├── run_smoke_tests.sh              # Test runner script
└── README.md                        # This file
```

## Writing New Smoke Tests

### Guidelines

1. **Keep tests independent** - Each test should be able to run in isolation
2. **Use fixtures for setup** - Leverage shared fixtures from `conftest.py`
3. **Mark tests appropriately** - Use `@pytest.mark.smoke` and specific markers
4. **Document impact** - Include docstrings explaining what each test validates
5. **Fast execution** - Smoke tests should complete within 5 minutes
6. **Clean up resources** - Always clean up test data
7. **Handle missing services gracefully** - Use `pytest.skip()` if service unavailable

### Example Test

```python
import pytest
from uuid import uuid4

@pytest.mark.smoke
@pytest.mark.database
@pytest.mark.asyncio
async def test_database_feature(db_session):
    """
    Verify database feature X works correctly.

    Impact: Ensures data persistence for feature X after deployment.
    """
    # Arrange
    test_id = str(uuid4())

    # Act
    # ... perform operation ...

    # Assert
    # ... verify results ...

    # Cleanup
    # ... remove test data ...
```

## Interpreting Results

### Successful Run

```
========================================
  ✓ All Smoke Tests Passed!
========================================

Database: ✓ 12 tests passed
Event Bus: ✓ 15 tests passed
Services: ✓ 20 tests passed

Total: 47 tests passed in 2.45s
```

### Failed Run

When tests fail, check:

1. **Service availability** - Are all services running?
2. **Database connectivity** - Can tests reach PostgreSQL?
3. **Redis connectivity** - Is Redis accessible?
4. **Network issues** - Firewall blocking connections?
5. **Configuration** - Are environment variables correct?
6. **Permissions** - Does test user have proper access?

### Common Failures

#### Database Connection Error

```
ERROR: Could not connect to database
```

**Solution:**
- Verify `SMOKE_TEST_DATABASE_URL` is correct
- Check PostgreSQL is running: `pg_isready -h localhost -p 5432`
- Verify network connectivity
- Check credentials

#### Redis Connection Error

```
ERROR: Redis connection failed
```

**Solution:**
- Verify `SMOKE_TEST_REDIS_URL` is correct
- Check Redis is running: `redis-cli ping`
- Verify network connectivity

#### Service Not Available

```
ERROR: Service health check failed (503)
```

**Solution:**
- Check service logs for errors
- Verify service is running: `docker ps` or `systemctl status`
- Check service configuration
- Verify dependencies (database, Redis) are available

#### Authentication Failures

```
ERROR: 401 Unauthorized
```

**Solution:**
- Check identity service is running
- Verify JWT configuration
- Check token generation logic

## CI/CD Integration

### GitHub Actions

The smoke tests are integrated into the CI/CD pipeline:

```yaml
# .github/workflows/deploy.yml
- name: Run Smoke Tests
  run: |
    ./tests/smoke/run_smoke_tests.sh --env ${{ matrix.environment }}
  env:
    SMOKE_TEST_DATABASE_URL: ${{ secrets.DATABASE_URL }}
    SMOKE_TEST_REDIS_URL: ${{ secrets.REDIS_URL }}
    GATEWAY_URL: ${{ secrets.GATEWAY_URL }}
```

### Deployment Workflow

1. **Deploy** - Deploy new version to environment
2. **Wait** - Allow services to start (30-60 seconds)
3. **Run Smoke Tests** - Execute smoke test suite
4. **Evaluate**:
   - If **PASS** → Continue to next stage (e.g., deploy to production)
   - If **FAIL** → Rollback deployment, alert team
5. **Monitor** - Continue monitoring in production

### Rollback Criteria

Smoke tests failing should trigger automatic rollback if:

- More than 20% of tests fail
- Any critical path test fails (health checks, authentication)
- Database transaction tests fail
- Service communication completely broken

## Performance Benchmarks

Target execution times:

| Test Suite | Target Time | Max Time |
|------------|-------------|----------|
| Database   | < 30s       | 60s      |
| Event Bus  | < 60s       | 120s     |
| Services   | < 60s       | 120s     |
| **Total**  | **< 2min**  | **5min** |

If tests exceed max time, investigate:
- Database query performance
- Network latency
- Service response times
- Resource constraints (CPU, memory)

## Best Practices

### When to Run Smoke Tests

✅ **DO run smoke tests:**
- After every deployment
- After infrastructure changes
- After database migrations
- When debugging integration issues
- Before promoting to production

❌ **DON'T run smoke tests:**
- During local development (use unit tests)
- For testing business logic (use integration tests)
- For load testing (use dedicated load tests)

### Maintaining Smoke Tests

- Review and update tests when adding new services
- Keep test data minimal but representative
- Update fixtures when schemas change
- Monitor test execution time and optimize slow tests
- Remove obsolete tests for deprecated features

## Troubleshooting

### Tests Hanging

If tests hang indefinitely:

```bash
# Add timeout to pytest
pytest tests/smoke -m smoke --timeout=300
```

Check for:
- Infinite loops in event handlers
- Deadlocks in database transactions
- Network timeouts without proper error handling

### Flaky Tests

If tests fail intermittently:

- Increase wait times for async operations
- Add retry logic for network operations
- Check for race conditions
- Verify test isolation (one test affecting another)

### Resource Cleanup

If tests leave behind test data:

```bash
# Manually clean up Redis test keys
redis-cli --scan --pattern "smoke_test*" | xargs redis-cli del

# Manually clean up database
psql -d atlas_test -c "DELETE FROM engagements WHERE name LIKE 'Smoke Test%'"
```

## Support

For issues with smoke tests:

1. Check logs: `pytest tests/smoke -v --log-cli-level=DEBUG`
2. Review recent changes to services
3. Verify environment configuration
4. Check service health manually: `curl http://localhost:8000/health`
5. Contact DevOps team if infrastructure issues

## References

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [SQLAlchemy Async](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [Redis-py](https://redis-py.readthedocs.io/)
- [httpx](https://www.python-httpx.org/)
