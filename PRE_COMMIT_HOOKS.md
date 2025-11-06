# Pre-commit Hooks Documentation

This document explains the pre-commit hooks configuration for the Aura Audit AI project.

## Table of Contents

- [Quick Start](#quick-start)
- [What are Pre-commit Hooks?](#what-are-pre-commit-hooks)
- [Installed Hooks](#installed-hooks)
- [Usage](#usage)
- [Troubleshooting](#troubleshooting)
- [Configuration](#configuration)

---

## Quick Start

### Installation

```bash
# Run the setup script
./setup-pre-commit.sh
```

That's it! Hooks are now active and will run automatically on every commit.

### Manual Installation

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install
pre-commit install --hook-type commit-msg

# Install dependencies
pip install -e ".[dev]"
```

---

## What are Pre-commit Hooks?

Pre-commit hooks are scripts that run automatically before each commit. They help:

- **Catch errors early** - Find issues before they reach code review
- **Enforce standards** - Ensure consistent code style across the team
- **Improve security** - Detect secrets and vulnerabilities
- **Save time** - Automate repetitive quality checks

---

## Installed Hooks

### 📝 General File Checks

| Hook | Description | When It Runs |
|------|-------------|--------------|
| `trailing-whitespace` | Removes trailing whitespace | On commit |
| `end-of-file-fixer` | Ensures files end with newline | On commit |
| `mixed-line-ending` | Fixes mixed line endings (enforces LF) | On commit |
| `check-json` | Validates JSON syntax | On commit |
| `check-yaml` | Validates YAML syntax | On commit |
| `check-toml` | Validates TOML syntax | On commit |
| `check-merge-conflict` | Detects merge conflict markers | On commit |

### 🔒 Security Checks

| Hook | Description | When It Runs |
|------|-------------|--------------|
| `detect-private-key` | Detects private SSH/SSL keys | On commit |
| `detect-aws-credentials` | Detects AWS credentials | On commit |
| `detect-secrets` | Scans for various secret patterns | On commit |
| `check-added-large-files` | Prevents large files (>1MB) | On commit |
| `bandit` | Python security vulnerability scanner | On commit |

### 🐍 Python Code Quality

| Hook | Description | When It Runs |
|------|-------------|--------------|
| **Black** | Code formatter (enforces 100 char line length) | On commit |
| **isort** | Import sorter (Black-compatible) | On commit |
| **Ruff** | Fast Python linter | On commit |
| **Mypy** | Static type checker | On commit |
| **Bandit** | Security linter | On commit |

**Configuration:** See `pyproject.toml` for Black, isort, Ruff, and Mypy settings.

### 🌐 JavaScript/TypeScript Code Quality

| Hook | Description | When It Runs |
|------|-------------|--------------|
| **Prettier** | Code formatter for JS/TS/JSON/YAML/MD | On commit |
| **ESLint** | JavaScript/TypeScript linter | On commit |

**Applies to:** `frontend/`, `admin-portal/`, `client-portal/`

### 🐳 Docker

| Hook | Description | When It Runs |
|------|-------------|--------------|
| **hadolint** | Dockerfile linter | On commit |

### 📊 SQL

| Hook | Description | When It Runs |
|------|-------------|--------------|
| **sqlfluff** | SQL formatter and linter (PostgreSQL dialect) | On commit |

**Applies to:** `db/migrations/*.sql`

### 📝 Markdown

| Hook | Description | When It Runs |
|------|-------------|--------------|
| **markdownlint** | Markdown linter and formatter | On commit |

### 🧪 Testing

| Hook | Description | When It Runs |
|------|-------------|--------------|
| `pytest-security` | Runs security service tests | On push |
| `pytest-changed-services` | Runs tests for changed services | On commit |

### 🔍 Custom Checks

| Hook | Description | When It Runs |
|------|-------------|--------------|
| `check-todos` | Warns about TODO/FIXME comments | On commit |
| `check-env-example` | Ensures .env.example is updated with .env | On commit |
| `no-console-log` | Blocks console.log in production code | On commit |
| `no-debugger` | Blocks debugger statements | On commit |
| `check-test-coverage-files` | Reminds to add tests for new code | On commit |

### ✉️ Commit Message Validation

| Hook | Description | When It Runs |
|------|-------------|--------------|
| **Commitizen** | Validates conventional commit format | On commit-msg |

**Format:** `<type>(<scope>): <subject>`

**Examples:**
```
feat(auth): add OAuth2 authentication
fix(api): resolve race condition in cache
docs(readme): update installation instructions
chore(deps): upgrade FastAPI to 0.109.0
```

**Valid types:** feat, fix, docs, style, refactor, perf, test, chore, ci

---

## Usage

### Normal Workflow

Pre-commit hooks run automatically:

```bash
git add .
git commit -m "feat: add new feature"
# Hooks run automatically
```

### Running Hooks Manually

```bash
# Run all hooks on all files
pre-commit run --all-files

# Run specific hook
pre-commit run black --all-files
pre-commit run ruff --all-files

# Run hooks on specific files
pre-commit run --files services/security/app/*.py
```

### Skipping Hooks (Not Recommended)

```bash
# Skip all hooks
git commit --no-verify -m "message"

# Skip specific hook using SKIP environment variable
SKIP=mypy git commit -m "message"

# Skip multiple hooks
SKIP=mypy,black git commit -m "message"
```

⚠️ **Warning:** Only skip hooks if absolutely necessary. Skipped checks will still run in CI/CD.

### Updating Hooks

```bash
# Update to latest hook versions
pre-commit autoupdate

# Re-run hooks after update
pre-commit run --all-files
```

---

## Troubleshooting

### Hook Failed - How to Fix?

#### 1. **Black/Prettier formatting failed**

These hooks auto-fix files. Just re-commit:

```bash
git add .
git commit -m "your message"
```

#### 2. **Ruff/ESLint linting failed**

Read the error messages and fix issues manually, or let the hook auto-fix:

```bash
# Ruff auto-fixes many issues
ruff check --fix services/

# ESLint auto-fixes
cd frontend && npm run lint -- --fix
```

#### 3. **Mypy type errors**

Add type hints or use `# type: ignore` for specific lines:

```python
result = some_function()  # type: ignore[attr-defined]
```

#### 4. **Bandit security warnings**

Fix security issues or add `# nosec` comment with justification:

```python
# This is safe because input is validated
subprocess.run(command, shell=True)  # nosec B602
```

#### 5. **detect-secrets failed**

Update the secrets baseline:

```bash
# Add false positive to baseline
detect-secrets scan --baseline .secrets.baseline
```

#### 6. **Test failures**

Fix tests or skip test hooks temporarily:

```bash
SKIP=pytest-changed-services git commit -m "message"
```

### Common Issues

#### "command not found: pre-commit"

```bash
pip install pre-commit
pre-commit install
```

#### "Hook failed: [Errno 2] No such file or directory"

```bash
# Reinstall hooks
pre-commit clean
pre-commit install
```

#### Hooks running too slow

```bash
# Skip slow hooks for quick commits
SKIP=mypy,pytest-changed-services git commit -m "message"

# Or configure to skip certain hooks by default in .pre-commit-config.yaml
```

#### ESLint/Prettier errors in frontend

```bash
# Install Node dependencies
cd frontend && npm install
cd ../admin-portal && npm install
cd ../client-portal && npm install
```

---

## Configuration

### Main Configuration File

**`.pre-commit-config.yaml`** - Defines all hooks and their settings.

### Tool-Specific Configuration

- **Black, isort, Mypy, Ruff, Bandit:** `pyproject.toml`
- **ESLint:** `frontend/.eslintrc.json`, `*-portal/.eslintrc.json`
- **Prettier:** `frontend/.prettierrc`, `*-portal/.prettierrc`
- **detect-secrets:** `.secrets.baseline`
- **Commitizen:** `pyproject.toml` (tool.commitizen section)

### Customizing Hooks

Edit `.pre-commit-config.yaml` to:

- **Disable a hook:** Comment it out or remove it
- **Add arguments:** Modify `args:` list
- **Change when it runs:** Modify `stages:` list
- **Change file patterns:** Modify `files:` regex

Example - disable Mypy:

```yaml
# - repo: https://github.com/pre-commit/mirrors-mypy
#   rev: v1.8.0
#   hooks:
#     - id: mypy
```

Example - add Ruff arguments:

```yaml
- id: ruff
  args: [--fix, --exit-non-zero-on-fix, --ignore=E501]
```

### Project-Specific Exclusions

Some hooks exclude certain paths automatically:

- **Tests:** Type checking and security scanning skip test files
- **Migrations:** Coverage and linting skip migration files
- **Node modules:** All hooks skip `node_modules/`
- **Build artifacts:** Hooks skip `dist/`, `build/`, `htmlcov/`

---

## Best Practices

### 1. Run Hooks Before Pushing

```bash
pre-commit run --all-files
```

### 2. Keep Hooks Updated

```bash
# Weekly or after dependency updates
pre-commit autoupdate
```

### 3. Fix Issues, Don't Skip

Skipping hooks defeats their purpose. Fix issues properly.

### 4. Add False Positives to Baselines

For detect-secrets and similar tools, update baselines instead of skipping.

### 5. Commit Small Changes

Large commits take longer to validate. Commit frequently.

### 6. Use Conventional Commits

Follow the format: `<type>(<scope>): <description>`

This enables automatic changelog generation.

---

## Hook Performance

Typical hook execution times:

| Hook | Time | Notes |
|------|------|-------|
| trailing-whitespace | <1s | Very fast |
| Black | 1-3s | Fast, depends on file count |
| Ruff | 1-2s | Very fast |
| Mypy | 5-10s | Can be slow on first run |
| ESLint | 2-5s | Depends on frontend size |
| pytest-changed-services | 5-30s | Only changed services |
| bandit | 2-5s | Fast |

**Total typical commit time:** 10-30 seconds

**First run:** May take 2-3 minutes while dependencies install.

---

## CI/CD Integration

Pre-commit hooks also run in CI/CD:

- **GitHub Actions:** `.github/workflows/ci.yml`
- **Pre-commit.ci:** Automatically runs and fixes on PRs
- **Coverage enforcement:** Fails if tests don't pass or coverage <70%

Hooks that pass locally will pass in CI/CD.

---

## Support

### Getting Help

1. **Check this documentation**
2. **Check tool-specific docs:**
   - Black: https://black.readthedocs.io
   - Ruff: https://docs.astral.sh/ruff
   - Pre-commit: https://pre-commit.com
3. **Ask the team** in Slack/Discord
4. **Open an issue** in the repository

### Reporting Issues

If a hook is causing problems for everyone:

1. Open an issue describing the problem
2. Suggest configuration changes
3. Tag with `pre-commit` label

---

## Summary

Pre-commit hooks help maintain code quality by:

- ✅ Enforcing consistent code style
- ✅ Catching bugs early
- ✅ Improving security
- ✅ Validating commit messages
- ✅ Running tests before push

They save time in code review and prevent issues from reaching production.

**Remember:** These hooks exist to help you write better code faster!
