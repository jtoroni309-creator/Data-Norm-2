#!/bin/bash

#
# Smoke Test Runner for Aura Audit AI Platform
#
# This script runs smoke tests after deployment to verify critical integration points.
# Smoke tests cover:
# - Database connectivity and transactions
# - Event bus (Redis) publish/subscribe flows
# - Service-to-service HTTP communication
#
# Usage:
#   ./run_smoke_tests.sh [options]
#
# Options:
#   --env <environment>     Environment to test (dev|staging|production) [default: dev]
#   --parallel              Run tests in parallel (faster but harder to debug)
#   --verbose               Show verbose output
#   --quick                 Run only critical smoke tests (skip comprehensive tests)
#   --report                Generate HTML test report
#   --help                  Show this help message
#

set -e  # Exit on error

# Default configuration
ENVIRONMENT="${ENVIRONMENT:-dev}"
PARALLEL=""
VERBOSE=""
QUICK_MODE=""
GENERATE_REPORT=""
TEST_TIMEOUT=300  # 5 minutes default timeout

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --env)
      ENVIRONMENT="$2"
      shift 2
      ;;
    --parallel)
      PARALLEL="-n auto"
      shift
      ;;
    --verbose)
      VERBOSE="-vv"
      shift
      ;;
    --quick)
      QUICK_MODE="true"
      shift
      ;;
    --report)
      GENERATE_REPORT="true"
      shift
      ;;
    --help)
      grep '^#' "$0" | sed 's/^# \?//'
      exit 0
      ;;
    *)
      echo -e "${RED}Unknown option: $1${NC}"
      echo "Use --help for usage information"
      exit 1
      ;;
  esac
done

# Print banner
echo ""
echo "=========================================="
echo "  Aura Audit AI - Smoke Tests"
echo "=========================================="
echo "Environment: $ENVIRONMENT"
echo "$(date)"
echo "=========================================="
echo ""

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
  echo -e "${RED}Error: Must run from project root directory${NC}"
  exit 1
fi

# Load environment variables based on environment
ENV_FILE=".env.${ENVIRONMENT}"
if [ ! -f "$ENV_FILE" ]; then
  echo -e "${YELLOW}Warning: $ENV_FILE not found, using .env${NC}"
  ENV_FILE=".env"
fi

if [ -f "$ENV_FILE" ]; then
  echo "Loading environment from $ENV_FILE"
  export $(grep -v '^#' "$ENV_FILE" | xargs)
fi

# Verify required services are running
echo ""
echo "Checking service availability..."

check_service() {
  local service_name=$1
  local service_url=$2
  local max_retries=5
  local retry_count=0

  while [ $retry_count -lt $max_retries ]; do
    if curl -s -f -o /dev/null --max-time 5 "$service_url" 2>/dev/null; then
      echo -e "${GREEN}✓${NC} $service_name is available"
      return 0
    fi
    retry_count=$((retry_count + 1))
    if [ $retry_count -lt $max_retries ]; then
      echo "  Waiting for $service_name... (attempt $retry_count/$max_retries)"
      sleep 2
    fi
  done

  echo -e "${RED}✗${NC} $service_name is not available at $service_url"
  return 1
}

# Check critical services
GATEWAY_URL="${GATEWAY_URL:-http://localhost:8000}"
REDIS_HOST="${REDIS_HOST:-localhost}"
REDIS_PORT="${REDIS_PORT:-6379}"
DATABASE_HOST="${DATABASE_HOST:-localhost}"
DATABASE_PORT="${DATABASE_PORT:-5432}"

# Check Gateway
if ! check_service "API Gateway" "$GATEWAY_URL/health"; then
  echo -e "${YELLOW}Warning: API Gateway not available. Service tests will fail.${NC}"
fi

# Check Redis (if redis-cli is available)
if command -v redis-cli &> /dev/null; then
  if redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" ping > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Redis is available"
  else
    echo -e "${YELLOW}Warning: Redis not available. Event bus tests will fail.${NC}"
  fi
fi

# Check PostgreSQL (if psql is available)
if command -v psql &> /dev/null; then
  if pg_isready -h "$DATABASE_HOST" -p "$DATABASE_PORT" > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} PostgreSQL is available"
  else
    echo -e "${YELLOW}Warning: PostgreSQL not available. Database tests will fail.${NC}"
  fi
fi

# Set up pytest arguments
PYTEST_ARGS=(
  "tests/smoke"
  "-m" "smoke"
  "--tb=short"
  "--color=yes"
  $VERBOSE
  $PARALLEL
)

# Add quick mode filter if requested
if [ "$QUICK_MODE" = "true" ]; then
  echo -e "${YELLOW}Running in QUICK mode - only critical tests${NC}"
  PYTEST_ARGS+=("-k" "health or connectivity or authentication")
fi

# Add report generation if requested
if [ "$GENERATE_REPORT" = "true" ]; then
  PYTEST_ARGS+=(
    "--html=smoke-test-report.html"
    "--self-contained-html"
    "--cov=services"
    "--cov-report=html:smoke-coverage"
  )
fi

# Run smoke tests
echo ""
echo "Running smoke tests..."
echo ""

if python -m pytest "${PYTEST_ARGS[@]}"; then
  echo ""
  echo -e "${GREEN}=========================================="
  echo "  ✓ All Smoke Tests Passed!"
  echo -e "==========================================${NC}"
  echo ""

  if [ "$GENERATE_REPORT" = "true" ]; then
    echo "Test report generated: smoke-test-report.html"
    echo "Coverage report: smoke-coverage/index.html"
  fi

  exit 0
else
  EXIT_CODE=$?
  echo ""
  echo -e "${RED}=========================================="
  echo "  ✗ Smoke Tests Failed!"
  echo -e "==========================================${NC}"
  echo ""
  echo "Some critical integration tests failed."
  echo "This indicates issues with the deployment."
  echo ""
  echo "Common issues:"
  echo "  - Database connection failures"
  echo "  - Redis/Event bus not accessible"
  echo "  - Services not properly started"
  echo "  - Network/firewall issues"
  echo "  - Configuration errors"
  echo ""
  echo "Check the test output above for details."

  if [ "$GENERATE_REPORT" = "true" ]; then
    echo "Test report generated: smoke-test-report.html"
  fi

  exit $EXIT_CODE
fi
