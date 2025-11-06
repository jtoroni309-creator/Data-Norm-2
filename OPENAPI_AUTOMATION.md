# OpenAPI Specification Automation

This document explains the automated OpenAPI specification generation system for Aura Audit AI.

## Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Architecture](#architecture)
- [Scripts](#scripts)
- [Workflow](#workflow)
- [CI/CD Integration](#cicd-integration)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

---

## Overview

The OpenAPI automation system automatically generates, combines, and validates API specifications from FastAPI service code. This ensures:

- ✅ **Always up-to-date documentation** - Generated from actual code
- ✅ **Single source of truth** - Code is the documentation
- ✅ **Consistency** - All services follow the same patterns
- ✅ **Validation** - Catch documentation issues early
- ✅ **Developer productivity** - No manual spec maintenance

### Key Features

- **Auto-generation**: Extract OpenAPI specs from FastAPI applications
- **Combination**: Merge all service specs into unified API
- **Validation**: Check specs against OpenAPI 3.1.0 standard
- **Documentation**: Generate beautiful HTML docs (ReDoc, Swagger UI)
- **CI/CD Integration**: Automatic generation on every commit
- **Pre-commit Hooks**: Validate specs before commit

---

## Quick Start

### Generate All Specifications

```bash
# Generate from code (recommended)
./scripts/openapi/generate_all.sh

# Generate from running services
./scripts/openapi/generate_all.sh --mode running

# Generate with documentation
./scripts/openapi/generate_all.sh --docs
```

###  Output Files

After generation, you'll find:

```
openapi/
├── generated/              # Individual service specs
│   ├── identity.json
│   ├── identity.yaml
│   ├── ingestion.json
│   ├── ingestion.yaml
│   └── ...
├── atlas-combined.json     # Unified specification
├── atlas-combined.yaml     # Unified specification
└── metadata.yaml           # Global metadata config
```

### View Documentation

```bash
# Generate documentation
./scripts/openapi/generate_all.sh --docs

# Open in browser
open docs/api/index.html        # ReDoc
open docs/api/swagger-ui/index.html  # Swagger UI
```

---

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────────┐
│                     FastAPI Services                            │
│  (identity, ingestion, analytics, engagement, etc.)             │
└────────────┬────────────────────────────────────────────────────┘
             │
             │ 1. Extract OpenAPI specs
             ▼
┌─────────────────────────────────────────────────────────────────┐
│            generate_service_specs.py                            │
│  - Fetch from running services OR extract from code            │
│  - Save individual JSON/YAML files                             │
└────────────┬────────────────────────────────────────────────────┘
             │
             │ 2. Combine specs
             ▼
┌─────────────────────────────────────────────────────────────────┐
│                 combine_specs.py                                │
│  - Merge all service specs                                     │
│  - Add path prefixes (/identity/*, /ingestion/*, etc.)        │
│  - Merge schemas, tags, security schemes                       │
│  - Apply global metadata                                       │
└────────────┬────────────────────────────────────────────────────┘
             │
             │ 3. Validate
             ▼
┌─────────────────────────────────────────────────────────────────┐
│                 validate_spec.py                                │
│  - Check OpenAPI 3.1.0 compliance                             │
│  - Validate required fields                                    │
│  - Check for common issues                                     │
│  - Generate statistics                                         │
└────────────┬────────────────────────────────────────────────────┘
             │
             │ 4. Generate docs (optional)
             ▼
┌─────────────────────────────────────────────────────────────────┐
│              Documentation Tools                                │
│  - ReDoc: Beautiful, responsive API docs                       │
│  - Swagger UI: Interactive API explorer                        │
└─────────────────────────────────────────────────────────────────┘
```

### Generation Modes

#### Code Mode (Default, Recommended)

Extracts specs directly from Python code without running services.

**Pros:**
- Fast (no service startup)
- Works offline
- No port conflicts
- Best for development

**Cons:**
- Requires code to be importable
- May miss runtime-configured endpoints

```bash
./scripts/openapi/generate_all.sh --mode code
```

#### Running Mode

Fetches specs from running FastAPI services via HTTP.

**Pros:**
- Captures runtime configuration
- Guaranteed accurate

**Cons:**
- Requires all services running
- Slower
- Port management needed

```bash
# Start services first
docker-compose up -d

# Generate
./scripts/openapi/generate_all.sh --mode running
```

---

## Scripts

### 1. `generate_service_specs.py`

Generates OpenAPI specifications for individual services.

**Usage:**

```bash
# From code (default)
python3 scripts/openapi/generate_service_specs.py

# From running services
python3 scripts/openapi/generate_service_specs.py --mode running --base-url http://localhost

# JSON only
python3 scripts/openapi/generate_service_specs.py --format json

# YAML only
python3 scripts/openapi/generate_service_specs.py --format yaml
```

**Options:**
- `--mode`: `code` or `running` (default: `code`)
- `--base-url`: Base URL for running services (default: `http://localhost`)
- `--format`: `json`, `yaml`, or `both` (default: `both`)
- `--services-dir`: Path to services directory

**Output:**
- Individual service specs in `openapi/generated/`

---

### 2. `combine_specs.py`

Combines individual service specs into unified specification.

**Usage:**

```bash
# Basic usage
python3 scripts/openapi/combine_specs.py

# With custom metadata
python3 scripts/openapi/combine_specs.py --metadata openapi/metadata.yaml

# Custom output location
python3 scripts/openapi/combine_specs.py --output openapi/api.yaml
```

**Options:**
- `--input-dir`: Directory with individual specs (default: `openapi/generated`)
- `--output`: Output file path (default: `openapi/atlas-combined.yaml`)
- `--metadata`: Metadata YAML file to override defaults

**Features:**
- Adds service prefixes to paths (`/identity/*`, `/ingestion/*`, etc.)
- Merges schemas with conflict resolution
- Combines tags, removing duplicates
- Merges security schemes
- Applies global metadata from `openapi/metadata.yaml`

**Output:**
- Combined spec: `openapi/atlas-combined.yaml`
- JSON version: `openapi/atlas-combined.json`

---

### 3. `validate_spec.py`

Validates OpenAPI specifications against OpenAPI 3.1.0 standard.

**Usage:**

```bash
# Validate combined spec
python3 scripts/openapi/validate_spec.py openapi/atlas-combined.yaml

# Verbose output
python3 scripts/openapi/validate_spec.py openapi/atlas-combined.yaml --verbose

# Validate individual service
python3 scripts/openapi/validate_spec.py openapi/generated/identity.yaml
```

**Checks:**
- ✅ Required fields (openapi, info, paths)
- ✅ Path format (must start with `/`)
- ✅ Valid HTTP methods
- ✅ Component structure
- ✅ Security scheme configuration
- ⚠️ Deprecated patterns
- 📊 Specification statistics

**Output:**
```
Validating openapi/atlas-combined.yaml...

Specification Statistics:
  Version: 3.1.0
  Title: Aura Audit AI - Unified API
  Paths: 150
  Operations: 300
  Schemas: 250
  Security Schemes: 2
  Tags: 12
  Servers: 4

✓ OpenAPI specification is valid
```

---

### 4. `generate_all.sh`

Master script orchestrating the entire workflow.

**Usage:**

```bash
# Full generation (code mode)
./scripts/openapi/generate_all.sh

# From running services
./scripts/openapi/generate_all.sh --mode running

# Skip validation
./scripts/openapi/generate_all.sh --no-validate

# Skip combination
./scripts/openapi/generate_all.sh --no-combine

# With documentation
./scripts/openapi/generate_all.sh --docs
```

**Options:**
- `--mode`: `code` or `running` (default: `code`)
- `--no-validate`: Skip validation step
- `--no-combine`: Skip combination step
- `--docs`: Generate HTML documentation

**Workflow:**
1. Generate individual service specs
2. Combine into unified spec
3. Validate all specifications
4. (Optional) Generate HTML documentation

---

## Workflow

### Development Workflow

```bash
# 1. Make changes to FastAPI service code
vim services/identity/app/main.py

# 2. Regenerate specs
./scripts/openapi/generate_all.sh

# 3. Review changes
git diff openapi/

# 4. Commit (pre-commit hooks validate automatically)
git add .
git commit -m "feat(identity): add new endpoint"
```

### Adding New Service

```bash
# 1. Add service to SERVICES list in generate_service_specs.py
vim scripts/openapi/generate_service_specs.py

# Add:
# {"name": "new-service", "port": 8013, "path": "/"},

# 2. Ensure service has proper FastAPI metadata
vim services/new-service/app/main.py

# Add:
# app = FastAPI(
#     title="New Service",
#     description="Service description",
#     version="1.0.0",
#     openapi_tags=[{"name": "NewService", "description": "..."}]
# )

# 3. Generate specs
./scripts/openapi/generate_all.sh

# 4. Verify
python3 scripts/openapi/validate_spec.py openapi/generated/new-service.yaml
```

### Updating Metadata

Edit `openapi/metadata.yaml` to customize:
- API title and description
- Version number
- Contact information
- Servers
- Security schemes
- External documentation links

```bash
vim openapi/metadata.yaml
./scripts/openapi/generate_all.sh
```

---

## CI/CD Integration

### GitHub Actions Workflow

The `.github/workflows/openapi.yml` workflow automatically:

1. **On Push/PR**: Generates and validates specs
2. **On Main/Develop**: Also generates HTML documentation
3. **Uploads Artifacts**: Specs and docs available for 90 days
4. **Comments on PRs**: Summary of API changes

**Triggers:**
- Push to `main`, `develop`, or `claude/**` branches
- Pull requests to `main` or `develop`
- Changes to `services/*/app/**` or `scripts/openapi/**`
- Manual workflow dispatch

**Jobs:**

#### 1. generate-and-validate
- Generates all OpenAPI specs from code
- Validates combined specification
- Uploads artifacts
- Comments on PR with summary

#### 2. validate-consistency
- Checks for breaking changes
- Ensures API consistency

#### 3. generate-docs
- Generates ReDoc HTML
- Generates Swagger UI
- Deploys to GitHub Pages (optional)

### Local CI Simulation

```bash
# Run same checks as CI
./scripts/openapi/generate_all.sh --mode code --docs
python3 scripts/openapi/validate_spec.py openapi/atlas-combined.yaml --verbose
```

---

## Best Practices

### 1. Document All Endpoints

Add detailed descriptions to FastAPI endpoints:

```python
@app.get(
    "/users/{user_id}",
    summary="Get user by ID",
    description="Retrieves a user by their unique identifier. Requires authentication.",
    response_description="User object with all details",
    tags=["Users"],
)
async def get_user(user_id: UUID):
    """
    Get user by ID.

    Args:
        user_id: Unique user identifier

    Returns:
        User object

    Raises:
        HTTPException: 404 if user not found
    """
    pass
```

### 2. Use Pydantic Models

Define clear request/response models:

```python
class UserResponse(BaseModel):
    """User response model."""
    id: UUID
    email: EmailStr
    name: str
    role: RoleEnum
    created_at: datetime

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "user@example.com",
                "name": "John Doe",
                "role": "auditor",
                "created_at": "2024-01-01T00:00:00Z"
            }
        }
    )
```

### 3. Add Tags and Metadata

Organize endpoints with tags:

```python
app = FastAPI(
    title="Identity Service",
    description="Authentication and user management",
    version="1.0.0",
    openapi_tags=[
        {"name": "Authentication", "description": "Login and token operations"},
        {"name": "Users", "description": "User management"},
        {"name": "Organizations", "description": "Organization management"},
    ]
)
```

### 4. Document Security

Specify security requirements:

```python
@app.get("/protected", dependencies=[Depends(verify_token)])
async def protected_endpoint():
    """Protected endpoint requiring authentication."""
    pass
```

### 5. Regular Regeneration

Regenerate specs regularly:

```bash
# Daily/weekly automated job
./scripts/openapi/generate_all.sh
git diff openapi/  # Review changes
```

### 6. Version Control Specs

**DO commit** generated specs:
- ✅ `openapi/atlas-combined.yaml`
- ✅ `openapi/atlas-combined.json`
- ✅ `openapi/generated/*.yaml`

**DON'T commit**:
- ❌ `docs/api/` (generated docs - too large)
- ❌ `.pre-commit-cache/`

---

## Troubleshooting

### Issue: "Failed to generate service specifications"

**Cause**: Service code has import errors or missing dependencies.

**Solution:**
```bash
# Check service can be imported
cd services/identity
python3 -c "from app.main import app"

# Install dependencies
pip install -r requirements.txt
```

### Issue: "Service not found"

**Cause**: Service name in script doesn't match directory name.

**Solution:**
```bash
# Check service exists
ls services/

# Update SERVICES list in generate_service_specs.py
vim scripts/openapi/generate_service_specs.py
```

### Issue: "Validation failed"

**Cause**: OpenAPI spec has errors.

**Solution:**
```bash
# Get detailed errors
python3 scripts/openapi/validate_spec.py openapi/atlas-combined.yaml --verbose

# Check individual service
python3 scripts/openapi/validate_spec.py openapi/generated/identity.yaml --verbose

# Fix FastAPI code based on errors
```

### Issue: "Port already in use" (running mode)

**Cause**: Service port is already bound.

**Solution:**
```bash
# Use code mode instead
./scripts/openapi/generate_all.sh --mode code

# OR check ports
lsof -i :8001
```

### Issue: "Naming conflicts in schemas"

**Cause**: Multiple services define schemas with the same name.

**Solution:**
The combiner automatically handles conflicts by adding suffixes (`ModelName_dup1`, `ModelName_dup2`). To fix properly:

1. Rename schemas to be unique
2. Use service-specific prefixes (`IdentityUser`, `EngagementUser`)

### Issue: "Pre-commit hook fails"

**Cause**: OpenAPI spec validation fails.

**Solution:**
```bash
# Check what's wrong
python3 scripts/openapi/validate_spec.py openapi/atlas-combined.yaml

# Skip hook temporarily (not recommended)
SKIP=openapi-validate git commit -m "message"

# Regenerate specs
./scripts/openapi/generate_all.sh
```

---

## Additional Resources

### Tools

- **ReDoc**: https://github.com/Redocly/redoc
- **Swagger UI**: https://github.com/swagger-api/swagger-ui
- **FastAPI Docs**: https://fastapi.tiangolo.com/advanced/extending-openapi/
- **OpenAPI Spec**: https://spec.openapis.org/oas/v3.1.0

### Scripts Location

```
scripts/openapi/
├── generate_service_specs.py  # Generate individual specs
├── combine_specs.py            # Combine specs
├── validate_spec.py            # Validate specs
└── generate_all.sh             # Master orchestrator
```

### Configuration Files

```
openapi/
├── metadata.yaml               # Global metadata
├── atlas.yaml                  # Original hand-written spec (deprecated)
├── atlas-combined.yaml         # Generated unified spec
└── generated/                  # Individual service specs
```

---

## Summary

The OpenAPI automation system ensures your API documentation is always accurate and up-to-date by:

1. **Generating** specs from actual service code
2. **Combining** all services into unified API
3. **Validating** against OpenAPI standards
4. **Documenting** with beautiful HTML
5. **Integrating** into CI/CD pipeline
6. **Enforcing** quality with pre-commit hooks

**Key Commands:**
```bash
# Generate everything
./scripts/openapi/generate_all.sh

# With docs
./scripts/openapi/generate_all.sh --docs

# Validate
python3 scripts/openapi/validate_spec.py openapi/atlas-combined.yaml
```

**Result:** Single source of truth for API documentation that never gets out of sync with code!
