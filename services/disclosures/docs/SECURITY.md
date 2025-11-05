# Security & STRIDE Threat Model

## Threat Model (STRIDE)

| Threat | Mitigation |
|--------|------------|
| **Spoofing** | OIDC + MFA; E-signature with cert fingerprint |
| **Tampering** | WORM storage (S3 Object Lock); SHA-256 hashing |
| **Repudiation** | Complete audit logs (lineage_events table) |
| **Information Disclosure** | VPC/VNet + Private Link; KMS encryption; RLS |
| **Denial of Service** | WAF, rate limits, autoscaling |
| **Elevation of Privilege** | RBAC + RLS; server-side authorization |

## Authentication
- **OIDC Providers**: Azure AD, Okta, Auth0
- **MFA**: Required for partner/QC roles
- **Session**: JWT with 8-hour expiry

## Authorization
- **RBAC**: partner, manager, senior, staff, qc_reviewer, client_contact
- **RLS**: Postgres policies enforce engagement-level isolation
- **API Gateway**: Validates JWT, sets `app.current_user_id` for RLS

## Data Protection
- **In Transit**: TLS 1.3
- **At Rest**: KMS/Key Vault
- **PII**: Redacted from logs; encrypted fields for SSN/bank accounts
- **WORM**: S3 Object Lock (Compliance mode) or Azure Immutable Blobs

## Secrets Management
- **AWS**: Secrets Manager + KMS
- **Azure**: Key Vault
- **Local Dev**: `.env` (gitignored)
- **Rotation**: 90-day policy for service keys

## Vulnerability Management
- **SAST**: Semgrep, CodeQL (CI)
- **DAST**: OWASP ZAP (staging)
- **SCA**: Trivy, Snyk (dependencies)
- **IaC**: tfsec, checkov (Terraform)

## Incident Response
1. Detect (CloudWatch Alarms, Sentry)
2. Contain (isolate affected services)
3. Investigate (audit logs, traces)
4. Remediate (patch, rotate secrets)
5. Post-mortem (blameless)
