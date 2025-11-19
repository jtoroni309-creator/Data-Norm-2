# Dependency Conflict Resolution

## Issue

The GitHub Actions build is failing with:
```
ERROR: ResolutionImpossible: for help visit https://pip.pypa.io/en/latest/topics/dependency-resolution/#dealing-with-dependency-conflicts
```

## Root Cause

One or more services have conflicting Python package versions that cannot be resolved together. Common conflicts:
- `openai` versions (1.3.7 vs 1.10.0)
- `alembic` versions (1.12.1 vs 1.13.1)
- `aioredis` (deprecated, conflicts with redis 5.x)
- `httpx` versions (0.25.2 vs 0.26.0)

## Identified Conflicts

### 1. aioredis Conflict
**Problem**: `services/reg-ab-audit/requirements.txt:26` uses `aioredis==2.0.1`
- `aioredis` is deprecated and conflicts with `redis==5.0.1`
- Redis 5.x includes async support natively

**Fix**: Remove aioredis, use redis directly

### 2. OpenAI Version Mismatch
- `reg-ab-audit` uses `openai==1.3.7`
- `financial-analysis` uses `openai==1.10.0`
**Fix**: Standardize to latest stable `openai==1.10.0`

### 3. Alembic Version Mismatch
- `reg-ab-audit` uses `alembic==1.12.1`
- `fraud-detection` and `financial-analysis` use `alembic==1.13.1`
**Fix**: Standardize to `alembic==1.13.1`

### 4. HTTPx Version Mismatch
- `reg-ab-audit` uses `httpx==0.25.2`
- `fraud-detection` and `financial-analysis` use `httpx==0.26.0`
**Fix**: Standardize to `httpx==0.26.0`

## Solution

Update the conflicting requirements files to use compatible versions.

### Files to Fix:
1. `services/reg-ab-audit/requirements.txt`
2. Any other services with `aioredis`

## Quick Fix Commands

```bash
# Fix reg-ab-audit requirements
# Remove aioredis line
# Update openai to 1.10.0
# Update alembic to 1.13.1
# Update httpx to 0.26.0
```
