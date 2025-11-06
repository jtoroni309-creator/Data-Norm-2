# Contributing to Aura Audit AI

Thank you for your interest in contributing to Aura Audit AI! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Commit Message Guidelines](#commit-message-guidelines)
- [Pull Request Process](#pull-request-process)
- [Issue Reporting](#issue-reporting)

## Code of Conduct

By participating in this project, you agree to:

- Be respectful and inclusive
- Accept constructive criticism gracefully
- Focus on what is best for the community
- Show empathy towards other community members

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker and Docker Compose
- Git
- PostgreSQL 15 (for local development)

### Setup Development Environment

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-org/Data-Norm-2.git
   cd Data-Norm-2
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your local configuration
   ```

3. **Start services with Docker Compose**
   ```bash
   docker-compose up -d
   ```

4. **Install Python dependencies**
   ```bash
   pip install -e ".[dev]"
   ```

5. **Install frontend dependencies**
   ```bash
   cd frontend && npm install
   cd ../admin-portal && npm install
   cd ../client-portal && npm install
   ```

6. **Run database migrations**
   ```bash
   psql -U postgres -d aura_audit -f db/migrations/0001_init.sql
   psql -U postgres -d aura_audit -f db/migrations/0002_reg_ab_audit.sql
   ```

7. **Verify setup**
   ```bash
   ./demo_platform.sh
   ```

## Development Workflow

### Branch Naming Convention

- `feature/short-description` - New features
- `fix/short-description` - Bug fixes
- `docs/short-description` - Documentation updates
- `refactor/short-description` - Code refactoring
- `test/short-description` - Test additions/updates
- `chore/short-description` - Maintenance tasks

### Workflow Steps

1. **Create a new branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write code following our [coding standards](#coding-standards)
   - Add tests for new functionality
   - Update documentation as needed

3. **Test your changes**
   ```bash
   # Python tests
   pytest services/[service-name]/tests

   # Frontend tests
   cd frontend && npm test

   # Linting
   ruff check services/
   npm run lint
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add new feature description"
   ```

5. **Push and create PR**
   ```bash
   git push origin feature/your-feature-name
   ```

## Coding Standards

### Python

- **Style Guide**: PEP 8
- **Formatter**: Black (line length: 100)
- **Linter**: Ruff
- **Type Checking**: Mypy (strict mode)

```bash
# Format code
black services/

# Lint code
ruff check services/

# Type check
mypy services/
```

**Python Best Practices:**
- Use type hints for all function parameters and return values
- Write docstrings for all public functions and classes
- Use Pydantic for data validation
- Follow async/await patterns for I/O operations
- Use SQLAlchemy ORM for database operations

### TypeScript/JavaScript

- **Style Guide**: ESLint with Airbnb config
- **Formatter**: Prettier
- **Type Checking**: TypeScript strict mode

```bash
# Format code
npm run format

# Lint code
npm run lint

# Type check
npm run type-check
```

**TypeScript Best Practices:**
- Use TypeScript strict mode
- Define interfaces for all data structures
- Use React hooks appropriately
- Implement proper error boundaries
- Use meaningful component and variable names

### File Organization

```
services/[service-name]/
├── Dockerfile
├── requirements.txt
├── README.md
├── app/
│   ├── main.py           # FastAPI app entry point
│   ├── models.py         # SQLAlchemy models
│   ├── schemas.py        # Pydantic schemas
│   ├── config.py         # Configuration
│   ├── database.py       # Database connection
│   └── routers/          # API route handlers
└── tests/
    ├── conftest.py       # Pytest fixtures
    ├── unit/             # Unit tests
    └── integration/      # Integration tests
```

## Testing Guidelines

### Test Coverage Requirements

- **Minimum Coverage**: 70% overall
- **Critical Paths**: 90%+ coverage
- **New Features**: Must include tests

### Python Testing

```bash
# Run all tests
pytest

# Run specific service tests
pytest services/analytics/tests

# Run with coverage
pytest --cov=services --cov-report=html

# Run specific test types
pytest -m unit
pytest -m integration
```

**Test Structure:**
```python
def test_function_name():
    # Arrange - Set up test data
    # Act - Execute the function
    # Assert - Verify the results
    pass
```

### Frontend Testing

```bash
# Run tests
npm test

# Run with coverage
npm test -- --coverage

# Run in watch mode
npm test -- --watch
```

**Test Structure:**
```typescript
describe('Component Name', () => {
  it('should do something', () => {
    // Arrange
    // Act
    // Assert
  });
});
```

## Commit Message Guidelines

We follow [Conventional Commits](https://www.conventionalcommits.org/):

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks
- `perf`: Performance improvements
- `ci`: CI/CD changes

### Examples

```
feat(engagement): add engagement creation API endpoint

Implement POST /api/engagements endpoint with validation
and database persistence.

Closes #123
```

```
fix(auth): resolve token expiration issue

Fixed bug where JWT tokens were not properly validated
for expiration time.

Fixes #456
```

## Pull Request Process

### Before Submitting

- [ ] Code follows style guidelines
- [ ] Tests pass locally
- [ ] New tests added for new features
- [ ] Documentation updated
- [ ] Commit messages follow guidelines
- [ ] No merge conflicts

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
Describe testing performed

## Checklist
- [ ] Tests pass
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
```

### Review Process

1. **Automated Checks**: CI/CD pipeline must pass
2. **Code Review**: At least one approval required
3. **Testing**: QA testing for significant changes
4. **Documentation**: Verify docs are updated
5. **Merge**: Squash and merge to main branch

### After Merge

- Delete feature branch
- Update related issues
- Monitor deployment
- Update changelog

## Issue Reporting

### Bug Reports

```markdown
**Description**
Clear description of the bug

**Steps to Reproduce**
1. Step one
2. Step two
3. ...

**Expected Behavior**
What should happen

**Actual Behavior**
What actually happens

**Environment**
- OS: [e.g., Ubuntu 22.04]
- Browser: [e.g., Chrome 120]
- Version: [e.g., 1.0.0]

**Screenshots**
If applicable

**Additional Context**
Any other relevant information
```

### Feature Requests

```markdown
**Problem Description**
What problem does this solve?

**Proposed Solution**
How should it work?

**Alternatives Considered**
Other approaches

**Additional Context**
Any other relevant information
```

## Project Structure

### Services Architecture

- **ingestion**: EDGAR/XBRL data fetching
- **normalize**: Taxonomy mapping and COA alignment
- **analytics**: Financial analysis and ratio testing
- **llm**: AI/RAG inference engine
- **engagement**: Workpaper and binder management
- **identity**: Authentication and authorization
- **qc**: Quality control and compliance gates
- **reporting**: PDF generation and e-signature
- **connectors**: ERP/payroll integrations
- **disclosures**: Disclosure note drafting

### Frontend Applications

- **frontend**: Main Next.js SaaS application
- **client-portal**: CPA firm dashboard (Vite + React)
- **admin-portal**: Administrative control panel (Vite + React)

## Resources

- [Documentation](README.md)
- [Quick Start Guide](QUICKSTART.md)
- [Architecture Overview](IMPLEMENTATION_STATUS.md)
- [API Documentation](openapi/atlas.yaml)
- [Deployment Guide](AZURE_DEPLOYMENT.md)

## Questions?

- **GitHub Issues**: For bugs and feature requests
- **Discussions**: For questions and community interaction
- **Email**: dev@aura-audit.ai

## License

By contributing, you agree that your contributions will be licensed under the project's license.

Thank you for contributing to Aura Audit AI!
