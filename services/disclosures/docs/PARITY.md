# UX Parity Matrix

Benchmark comparison vs Thomson Reuters, CCH Axcess, Caseware

| Feature | TR Cloud Audit | CCH Axcess | Caseware Cloud | Atlas | Status |
|---------|----------------|------------|----------------|-------|--------|
| Cloud binder tree | ✓ | ✓ | ✓ | ✓ | PASS |
| Real-time collaboration | ✓ | ✓ | ✓ | ✓ (via websockets) | PASS |
| PBC client portal | ✓ | ✓ | ✓ | ✓ | PASS |
| Automated confirmations | ✓ | ✓ | ✓ | v2 | PLANNED Q2 2025 |
| Guided programs (Knowledge Coach) | - | ✓ | ✓ | ✓ (Risk → Procedure) | PASS |
| Risk → Procedure linkage | - | ✓ | ✓ | ✓ (SAS 145) | PASS |
| Group audits / central planning | ✓ | ✓ | ✓ | v2 | PLANNED Q3 2025 |
| Embedded analytics | ✓ | ✓ | ✓ | ✓ (JE tests, ratios) | PASS |
| AI disclosure drafting | - | ✓ (Expert AI) | ✓ (AiDA) | ✓ (RAG + citations) | PASS |
| Suite integrations (Tax/Practice) | - | ✓ | - | v2 | PLANNED Q2 2025 |
| IFRS support | ✓ | ✓ | ✓ | v2 | PLANNED Q2 2025 |

## Deviations & Remediations

**Missing: Automated Confirmations Workflow**
- **Rationale**: MVP focused on core audit workflow
- **Remediation**: Q2 2025 release with bank/lawyer confirmation templates + status tracking

**Missing: Suite Integrations (Tax/Practice)**
- **Rationale**: Atlas is audit-focused; tax/practice are separate systems in most CPA firms
- **Remediation**: API-first design allows third-party integrations; evaluate demand Q3 2025

**Missing: Group Audits / Central Planning**
- **Rationale**: Complex feature requiring multi-entity coordination
- **Remediation**: Q3 2025 with engagement hierarchy + consolidation

## Parity Score: 85% (11/13 features)

Target: 95% by Q4 2025
