#!/bin/bash
#
# Test Runner Script
# Runs tests for all services or a specific service
#

set -e

# Colors
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m'

# Parse arguments
SERVICE=""
COVERAGE=true
FAST=false
MARKERS=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --service)
            SERVICE="$2"
            shift 2
            ;;
        --no-coverage)
            COVERAGE=false
            shift
            ;;
        --fast)
            FAST=true
            shift
            ;;
        --unit)
            MARKERS="unit"
            shift
            ;;
        --integration)
            MARKERS="integration"
            shift
            ;;
        --help)
            echo "Usage: $0 [options]"
            echo ""
            echo "Options:"
            echo "  --service <name>    Run tests for specific service"
            echo "  --no-coverage       Skip coverage reporting"
            echo "  --fast              Run fast tests (no coverage, exit on first failure)"
            echo "  --unit              Run only unit tests"
            echo "  --integration       Run only integration tests"
            echo "  --help              Show this help message"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

# Build pytest command
PYTEST_ARGS="-v --tb=short"

if [ "$FAST" = true ]; then
    PYTEST_ARGS="$PYTEST_ARGS -x"
    COVERAGE=false
    echo -e "${YELLOW}Running fast tests (no coverage, exit on first failure)${NC}"
fi

if [ "$COVERAGE" = true ]; then
    PYTEST_ARGS="$PYTEST_ARGS --cov=services --cov-report=term-missing --cov-report=html --cov-report=xml"
fi

if [ -n "$MARKERS" ]; then
    PYTEST_ARGS="$PYTEST_ARGS -m $MARKERS"
    echo -e "${BLUE}Running tests with marker: $MARKERS${NC}"
fi

# Run tests
if [ -n "$SERVICE" ]; then
    echo -e "${BLUE}Running tests for service: $SERVICE${NC}"

    if [ ! -d "services/$SERVICE" ]; then
        echo -e "${RED}Error: Service '$SERVICE' not found${NC}"
        exit 1
    fi

    cd "services/$SERVICE"

    if [ ! -d "tests" ]; then
        echo -e "${YELLOW}Warning: No tests directory found for $SERVICE${NC}"
        exit 0
    fi

    pytest tests/ $PYTEST_ARGS --cov=app

else
    echo -e "${BLUE}Running tests for all services${NC}"
    pytest services/ $PYTEST_ARGS
fi

# Report results
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed!${NC}"

    if [ "$COVERAGE" = true ]; then
        echo -e "${YELLOW}Coverage report: htmlcov/index.html${NC}"
    fi
else
    echo -e "${RED}✗ Some tests failed${NC}"
    exit 1
fi
