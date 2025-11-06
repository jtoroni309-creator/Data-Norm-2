#!/bin/bash
# Master script to generate, combine, and validate OpenAPI specifications

set -e  # Exit on error

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Directories
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
OPENAPI_DIR="$ROOT_DIR/openapi"
GENERATED_DIR="$OPENAPI_DIR/generated"
DOCS_DIR="$ROOT_DIR/docs/api"

echo "=========================================="
echo "OpenAPI Specification Generation"
echo "=========================================="
echo ""

# Parse arguments
MODE="code"  # Default to code mode
VALIDATE=true
COMBINE=true
DOCS=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --mode)
            MODE="$2"
            shift 2
            ;;
        --no-validate)
            VALIDATE=false
            shift
            ;;
        --no-combine)
            COMBINE=false
            shift
            ;;
        --docs)
            DOCS=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--mode running|code] [--no-validate] [--no-combine] [--docs]"
            exit 1
            ;;
    esac
done

echo -e "${BLUE}Mode: $MODE${NC}"
echo -e "${BLUE}Validate: $VALIDATE${NC}"
echo -e "${BLUE}Combine: $COMBINE${NC}"
echo -e "${BLUE}Generate Docs: $DOCS${NC}"
echo ""

# Ensure Python environment
if [ ! -d "$ROOT_DIR/venv" ]; then
    echo -e "${YELLOW}Virtual environment not found. Creating...${NC}"
    python3 -m venv "$ROOT_DIR/venv"
fi

# Activate virtual environment
source "$ROOT_DIR/venv/bin/activate"

# Install dependencies if needed
echo "Checking dependencies..."
pip install -q httpx pyyaml 2>/dev/null || true

# Step 1: Generate individual service specs
echo ""
echo "=========================================="
echo "Step 1: Generating Service Specifications"
echo "=========================================="
echo ""

python3 "$SCRIPT_DIR/generate_service_specs.py" \
    --mode "$MODE" \
    --format both \
    --services-dir "$ROOT_DIR/services"

if [ $? -ne 0 ]; then
    echo -e "${RED}✗ Failed to generate service specifications${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Service specifications generated${NC}"

# Step 2: Combine specifications
if [ "$COMBINE" = true ]; then
    echo ""
    echo "=========================================="
    echo "Step 2: Combining Specifications"
    echo "=========================================="
    echo ""

    python3 "$SCRIPT_DIR/combine_specs.py" \
        --input-dir "$GENERATED_DIR" \
        --output "$OPENAPI_DIR/atlas-combined.yaml"

    if [ $? -ne 0 ]; then
        echo -e "${RED}✗ Failed to combine specifications${NC}"
        exit 1
    fi

    # Also create JSON version
    python3 -c "
import yaml, json
with open('$OPENAPI_DIR/atlas-combined.yaml') as f:
    spec = yaml.safe_load(f)
with open('$OPENAPI_DIR/atlas-combined.json', 'w') as f:
    json.dump(spec, f, indent=2)
"

    echo -e "${GREEN}✓ Specifications combined${NC}"
fi

# Step 3: Validate specifications
if [ "$VALIDATE" = true ]; then
    echo ""
    echo "=========================================="
    echo "Step 3: Validating Specifications"
    echo "=========================================="
    echo ""

    # Validate combined spec
    if [ -f "$OPENAPI_DIR/atlas-combined.yaml" ]; then
        python3 "$SCRIPT_DIR/validate_spec.py" \
            "$OPENAPI_DIR/atlas-combined.yaml" \
            --verbose

        if [ $? -ne 0 ]; then
            echo -e "${YELLOW}⚠️  Combined specification has validation issues${NC}"
        else
            echo -e "${GREEN}✓ Combined specification is valid${NC}"
        fi
    fi

    echo ""
    echo "Validating individual service specifications..."
    echo ""

    # Validate individual specs
    VALID_COUNT=0
    TOTAL_COUNT=0

    for spec_file in "$GENERATED_DIR"/*.yaml; do
        if [ -f "$spec_file" ]; then
            TOTAL_COUNT=$((TOTAL_COUNT + 1))
            SERVICE_NAME=$(basename "$spec_file" .yaml)

            echo "Validating $SERVICE_NAME..."

            if python3 "$SCRIPT_DIR/validate_spec.py" "$spec_file" > /dev/null 2>&1; then
                echo -e "  ${GREEN}✓ Valid${NC}"
                VALID_COUNT=$((VALID_COUNT + 1))
            else
                echo -e "  ${YELLOW}⚠️  Has issues${NC}"
            fi
        fi
    done

    echo ""
    echo -e "${BLUE}Validation Summary: $VALID_COUNT/$TOTAL_COUNT valid${NC}"
fi

# Step 4: Generate API documentation (optional)
if [ "$DOCS" = true ]; then
    echo ""
    echo "=========================================="
    echo "Step 4: Generating API Documentation"
    echo "=========================================="
    echo ""

    # Check if redoc-cli or swagger-ui-cli is available
    if command -v redoc-cli &> /dev/null; then
        mkdir -p "$DOCS_DIR"

        echo "Generating ReDoc HTML documentation..."
        redoc-cli bundle "$OPENAPI_DIR/atlas-combined.yaml" \
            -o "$DOCS_DIR/index.html" \
            --title "Aura Audit AI API Documentation"

        echo -e "${GREEN}✓ API documentation generated at $DOCS_DIR/index.html${NC}"
    else
        echo -e "${YELLOW}⚠️  redoc-cli not found. Install with: npm install -g redoc-cli${NC}"
        echo "Skipping documentation generation"
    fi
fi

# Summary
echo ""
echo "=========================================="
echo "✓ OpenAPI Generation Complete"
echo "=========================================="
echo ""
echo "Generated files:"
echo "  - Individual specs: $GENERATED_DIR/*.{json,yaml}"
if [ "$COMBINE" = true ]; then
    echo "  - Combined spec: $OPENAPI_DIR/atlas-combined.{json,yaml}"
fi
if [ "$DOCS" = true ] && [ -f "$DOCS_DIR/index.html" ]; then
    echo "  - Documentation: $DOCS_DIR/index.html"
fi
echo ""
echo "Next steps:"
echo "  1. Review generated specifications"
echo "  2. Update any service-specific documentation"
echo "  3. Commit changes to version control"
if [ ! -f "$DOCS_DIR/index.html" ]; then
    echo "  4. (Optional) Generate docs: $0 --docs"
fi
echo ""
