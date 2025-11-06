#!/bin/bash
# Setup script for pre-commit hooks
# Run this after cloning the repository to enable automated code quality checks

set -e  # Exit on error

echo "=========================================="
echo "Pre-commit Hooks Setup"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Python 3 found${NC}"

# Check Python version
PYTHON_VERSION=$(python3 --version | awk '{print $2}')
echo "Python version: $PYTHON_VERSION"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo ""
    echo "Creating Python virtual environment..."
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${YELLOW}Virtual environment already exists${NC}"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1
echo -e "${GREEN}✓ pip upgraded${NC}"

# Install pre-commit
echo ""
echo "Installing pre-commit..."
pip install pre-commit > /dev/null 2>&1
echo -e "${GREEN}✓ pre-commit installed${NC}"

# Install development dependencies
echo ""
echo "Installing development dependencies..."
pip install -e ".[dev]" > /dev/null 2>&1
echo -e "${GREEN}✓ Development dependencies installed${NC}"

# Install pre-commit hooks
echo ""
echo "Installing pre-commit hooks..."
pre-commit install
pre-commit install --hook-type commit-msg
echo -e "${GREEN}✓ Pre-commit hooks installed${NC}"

# Create secrets baseline if it doesn't exist
if [ ! -f ".secrets.baseline" ]; then
    echo ""
    echo "Creating secrets baseline..."
    detect-secrets scan > .secrets.baseline 2>/dev/null || echo '{"version": "1.4.0", "filters_used": [], "results": {}}' > .secrets.baseline
    echo -e "${GREEN}✓ Secrets baseline created${NC}"
fi

# Install Node.js dependencies for frontend hooks (if Node is available)
if command -v npm &> /dev/null; then
    echo ""
    echo "Node.js found, installing frontend dependencies..."

    # Frontend
    if [ -d "frontend" ]; then
        echo "  - Installing frontend dependencies..."
        cd frontend && npm install > /dev/null 2>&1 && cd ..
        echo -e "${GREEN}  ✓ frontend dependencies installed${NC}"
    fi

    # Admin portal
    if [ -d "admin-portal" ]; then
        echo "  - Installing admin-portal dependencies..."
        cd admin-portal && npm install > /dev/null 2>&1 && cd ..
        echo -e "${GREEN}  ✓ admin-portal dependencies installed${NC}"
    fi

    # Client portal
    if [ -d "client-portal" ]; then
        echo "  - Installing client-portal dependencies..."
        cd client-portal && npm install > /dev/null 2>&1 && cd ..
        echo -e "${GREEN}  ✓ client-portal dependencies installed${NC}"
    fi
else
    echo -e "${YELLOW}Node.js not found, skipping frontend dependency installation${NC}"
    echo "Frontend hooks will be skipped until Node.js is installed"
fi

# Run pre-commit on all files (optional, can take time)
echo ""
echo "Testing pre-commit hooks..."
echo "(This may take a few minutes on first run)"
pre-commit run --all-files || echo -e "${YELLOW}Some hooks failed, but that's okay for initial setup${NC}"

echo ""
echo "=========================================="
echo -e "${GREEN}✓ Pre-commit Setup Complete!${NC}"
echo "=========================================="
echo ""
echo "Hooks are now enabled for:"
echo "  • Code formatting (Black, Prettier)"
echo "  • Linting (Ruff, ESLint)"
echo "  • Type checking (Mypy)"
echo "  • Security scanning (Bandit, detect-secrets)"
echo "  • Commit message validation (Commitizen)"
echo "  • And more..."
echo ""
echo "To manually run hooks:"
echo "  pre-commit run --all-files"
echo ""
echo "To skip hooks (not recommended):"
echo "  git commit --no-verify"
echo ""
echo "For more information:"
echo "  pre-commit run --help"
echo ""
