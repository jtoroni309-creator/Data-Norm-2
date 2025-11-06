# Security Policy

## Supported Versions

We release security updates for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 1.x.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

We take the security of Aura Audit AI seriously. If you discover a security vulnerability, please follow these steps:

### How to Report

**DO NOT** create a public GitHub issue for security vulnerabilities.

Instead, please report security vulnerabilities by:

1. **Email**: Send details to security@aura-audit.ai
2. **GitHub Security Advisories**: Use the "Security" tab in this repository
3. **Encrypted Communication**: Use our PGP key (available upon request)

### What to Include

Please include the following information in your report:

- Description of the vulnerability
- Steps to reproduce the issue
- Potential impact of the vulnerability
- Any suggested fixes (if available)
- Your contact information

### Response Timeline

- **Initial Response**: Within 24 hours
- **Status Update**: Within 72 hours
- **Fix Timeline**: Varies based on severity
  - Critical: 1-7 days
  - High: 7-14 days
  - Medium: 14-30 days
  - Low: 30-90 days

## Security Best Practices

### For Users

1. **Environment Variables**: Never commit `.env` files containing secrets
2. **API Keys**: Rotate API keys regularly
3. **Access Control**: Follow principle of least privilege
4. **Updates**: Keep all dependencies updated
5. **Monitoring**: Enable security monitoring and logging

### For Contributors

1. **Code Review**: All code must be reviewed before merging
2. **Dependency Scanning**: Use `npm audit` and `pip audit` regularly
3. **Secret Scanning**: Use pre-commit hooks to prevent secret commits
4. **Input Validation**: Always validate and sanitize user inputs
5. **Authentication**: Use strong authentication mechanisms
6. **Encryption**: Encrypt sensitive data at rest and in transit

## Security Features

### Infrastructure Security

- **Encryption**: TLS 1.3 for all network communications
- **Database**: Encrypted at rest with AES-256
- **Storage**: AWS S3 WORM compliance for audit trails
- **Authentication**: OAuth 2.0, OIDC, SAML 2.0 support
- **Authorization**: Role-Based Access Control (RBAC) with Row-Level Security (RLS)

### Application Security

- **Input Validation**: Pydantic schemas for all API inputs
- **SQL Injection Protection**: Parameterized queries via SQLAlchemy ORM
- **XSS Protection**: Content Security Policy headers
- **CSRF Protection**: Token-based protection for state-changing operations
- **Rate Limiting**: API rate limiting to prevent abuse
- **Audit Logging**: Comprehensive audit trails for all operations

### Compliance

- **SOC 2 Type II**: Compliance documentation available
- **AICPA Standards**: Adherence to SSAE 18 and SSARS 21
- **Data Privacy**: GDPR and CCPA compliant
- **Financial Data**: SEC EDGAR data handling compliance

## Security Updates

We announce security updates through:

1. GitHub Security Advisories
2. Release notes
3. Email notifications to registered users
4. Security mailing list (security-announce@aura-audit.ai)

## Scope

The following are **IN SCOPE** for security reports:

- Authentication and authorization bypass
- SQL injection, XSS, CSRF vulnerabilities
- Remote code execution
- Data exposure or leakage
- Cryptographic issues
- Business logic flaws
- Denial of service (with proof of concept)

The following are **OUT OF SCOPE**:

- Social engineering attacks
- Physical security issues
- Attacks requiring physical access to user devices
- Outdated browser/OS vulnerabilities
- Rate limiting issues without demonstrable impact
- Issues in third-party dependencies (report to upstream)

## Acknowledgments

We maintain a list of security researchers who have responsibly disclosed vulnerabilities:

- [Security Researchers Hall of Fame](SECURITY_HALL_OF_FAME.md)

## Contact

- **Security Team**: security@aura-audit.ai
- **General Support**: support@aura-audit.ai
- **Website**: https://aura-audit.ai

Thank you for helping keep Aura Audit AI secure!
