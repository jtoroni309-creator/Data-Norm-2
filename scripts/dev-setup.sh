#!/bin/bash
#
# Development Environment Setup Script
# Sets up the complete development environment for Aura Audit AI
#

set -e  # Exit on error

# Colors
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}Aura Audit AI - Development Environment Setup${NC}"
echo ""

# Check Python version
echo -e "${BLUE}Checking Python version...${NC}"
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
REQUIRED_VERSION="3.11"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo -e "${RED}Error: Python $REQUIRED_VERSION or higher is required (found $PYTHON_VERSION)${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python $PYTHON_VERSION${NC}"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${BLUE}Creating virtual environment...${NC}"
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${YELLOW}⚠ Virtual environment already exists${NC}"
fi

# Activate virtual environment
echo -e "${BLUE}Activating virtual environment...${NC}"
source venv/bin/activate

# Upgrade pip
echo -e "${BLUE}Upgrading pip...${NC}"
pip install --upgrade pip setuptools wheel
echo -e "${GREEN}✓ pip upgraded${NC}"

# Install shared libraries
echo -e "${BLUE}Installing shared libraries...${NC}"
pip install -e lib/service_client
pip install -e lib/event_bus
pip install -e lib/common_core
echo -e "${GREEN}✓ Shared libraries installed${NC}"

# Install development dependencies
echo -e "${BLUE}Installing development dependencies...${NC}"
pip install -e ".[dev]"
echo -e "${GREEN}✓ Development dependencies installed${NC}"

# Install pre-commit hooks
echo -e "${BLUE}Installing pre-commit hooks...${NC}"
pre-commit install
echo -e "${GREEN}✓ Pre-commit hooks installed${NC}"

# Check for .env file
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠ .env file not found${NC}"
    echo -e "${BLUE}Creating .env from .env.example...${NC}"
    cp .env.example .env
    echo -e "${GREEN}✓ .env file created${NC}"
    echo -e "${YELLOW}⚠ Please update .env with your configuration${NC}"
else
    echo -e "${GREEN}✓ .env file exists${NC}"
fi

# Check Docker
echo -e "${BLUE}Checking Docker...${NC}"
if command -v docker &> /dev/null; then
    echo -e "${GREEN}✓ Docker installed${NC}"
    if docker ps &> /dev/null; then
        echo -e "${GREEN}✓ Docker daemon running${NC}"
    else
        echo -e "${YELLOW}⚠ Docker daemon not running${NC}"
        echo -e "${YELLOW}  Start Docker to run services locally${NC}"
    fi
else
    echo -e "${YELLOW}⚠ Docker not installed${NC}"
    echo -e "${YELLOW}  Install Docker to run services locally${NC}"
fi

# Check Node.js for frontend
echo -e "${BLUE}Checking Node.js...${NC}"
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo -e "${GREEN}✓ Node.js $NODE_VERSION${NC}"
else
    echo -e "${YELLOW}⚠ Node.js not installed${NC}"
    echo -e "${YELLOW}  Install Node.js to work with frontends${NC}"
fi

echo ""
echo -e "${GREEN}✓ Development environment setup complete!${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo "  1. Update .env with your configuration"
echo "  2. Start services: make docker-up"
echo "  3. Run database migrations: make db-migrate"
echo "  4. Run tests: make test"
echo "  5. View API docs: http://localhost:8000/docs"
echo ""
echo -e "${BLUE}Helpful commands:${NC}"
echo "  - make help           # Show all available commands"
echo "  - make test           # Run all tests"
echo "  - make format         # Format code"
echo "  - make lint           # Run linter"
echo "  - make docker-up      # Start all services"
echo "  - make docker-logs    # View service logs"
echo ""
