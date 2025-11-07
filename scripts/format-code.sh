#!/bin/bash
#
# Code Formatter Script
# Formats Python code with black and isort
#

set -e

# Colors
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}Formatting Python code...${NC}"

# Format with black
echo -e "${BLUE}Running black...${NC}"
black services/ lib/ --line-length 100 --exclude '/(\.git|\.venv|venv|node_modules|\.mypy_cache|\.pytest_cache)/'

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Black formatting complete${NC}"
else
    echo -e "${RED}✗ Black formatting failed${NC}"
    exit 1
fi

# Sort imports with isort
echo -e "${BLUE}Running isort...${NC}"
isort services/ lib/ --profile black --skip .venv --skip venv --skip node_modules

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Import sorting complete${NC}"
else
    echo -e "${RED}✗ Import sorting failed${NC}"
    exit 1
fi

# Run linter to check for issues
echo -e "${BLUE}Running ruff linter...${NC}"
ruff check services/ lib/ --fix --exclude .venv --exclude venv --exclude node_modules

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Linting complete${NC}"
else
    echo -e "${YELLOW}⚠ Some linting issues remain${NC}"
fi

echo ""
echo -e "${GREEN}✓ Code formatting complete!${NC}"
echo -e "${BLUE}Files have been formatted with black and isort${NC}"
