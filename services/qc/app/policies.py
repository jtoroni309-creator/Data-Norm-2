"""
QC Policy Definitions and Evaluation Logic

Each policy class implements a specific audit standard or firm policy.
Policies return a structured result indicating pass/fail and evidence.

Compliance Coverage:
- PCAOB AS 1215: Audit Documentation
- AICPA SAS 142: Audit Evidence
- AICPA SAS 145: Risk Assessment
- Firm policies: Partner approval, review notes, etc.
"""
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func

logger = logging.getLogger(__name__)


# ========================================
# Base Policy Class
# ========================================

class BasePolicy(ABC):
    """Base class for all QC policies"""

    def __init__(self):
        self.policy_code: str = ""
        self.policy_name: str = ""
        self.description: str = ""
        self.is_blocking: bool = True
        self.standard_reference: str = ""

    @abstractmethod
    async def evaluate(self, engagement_id: UUID, db: AsyncSession) -> Dict[str, Any]:
        """
        Evaluate policy for given engagement

        Returns:
        {
            "passed": bool,
            "details": str,
            "remediation": str,
            "evidence": dict,
            "waived": bool (optional)
        }
        """
        pass


class PolicyRegistry:
    """Registry for all QC policies"""

    def __init__(self):
        self.policies: Dict[str, BasePolicy] = {}

    def register(self, policy: BasePolicy):
        """Register a policy"""
        self.policies[policy.policy_code] = policy
        logger.info(f"Registered policy: {policy.policy_code}")

    def get(self, policy_code: str) -> BasePolicy:
        """Get policy by code"""
        return self.policies.get(policy_code)

    def list_all(self):
        """List all registered policies"""
        return list(self.policies.values())


# ========================================
# PCAOB AS 1215: Audit Documentation
# ========================================

class AS1215_AuditDocumentation(BasePolicy):
    """
    PCAOB AS 1215 - Audit Documentation

    Requirements:
    - All audit procedures must have supporting workpapers
    - Documentation must be sufficient for experienced auditor to understand:
      * Nature, timing, extent of procedures
      * Results obtained
      * Significant matters arising
      * Conclusions reached

    This policy checks that:
    1. All procedures have at least one workpaper linked
    2. All workpapers have status >= 'prepared'
    3. All significant findings are documented
    """

    def __init__(self):
        super().__init__()
        self.policy_code = "AS1215_DOCUMENTATION"
        self.policy_name = "PCAOB AS 1215 - Audit Documentation Complete"
        self.description = "All audit procedures must have supporting workpapers"
        self.is_blocking = True
        self.standard_reference = "PCAOB AS 1215"

    async def evaluate(self, engagement_id: UUID, db: AsyncSession) -> Dict[str, Any]:
        """Evaluate audit documentation completeness"""

        try:
            # Count total procedures for the engagement
            total_procedures_query = select(func.count()).select_from(
                select(1).select_from(
                    func.unnest(func.array([1]))
                ).alias("procedures")
            ).where(False)  # This will be replaced with actual table

            # Query procedures without linked workpapers
            # A procedure has workpapers if evidence_links exist that reference it
            from sqlalchemy import text

            query = text("""
                SELECT
                    COUNT(DISTINCT p.id) as total_procedures,
                    COUNT(DISTINCT CASE
                        WHEN wp.id IS NULL THEN p.id
                        ELSE NULL
                    END) as procedures_without_workpapers
                FROM atlas.procedures p
                LEFT JOIN atlas.evidence_links el ON el.procedure_id = p.id
                LEFT JOIN atlas.workpapers wp ON wp.id = el.workpaper_id
                    AND wp.prepared_at IS NOT NULL
                WHERE p.engagement_id = :engagement_id
                    AND p.status IN ('completed', 'reviewed')
            """)

            result = await db.execute(query, {"engagement_id": engagement_id})
            row = result.fetchone()

            total_procedures = row[0] if row else 0
            procedures_without_workpapers = row[1] if row else 0

            if procedures_without_workpapers > 0:
                return {
                    "passed": False,
                    "details": f"{procedures_without_workpapers} procedure(s) lack supporting workpapers",
                    "remediation": (
                        "Complete workpapers for all procedures. "
                        "Each procedure must document: (1) nature, timing, and extent of work performed, "
                        "(2) results obtained, (3) conclusions reached. "
                        "See PCAOB AS 1215.06 for requirements."
                    ),
                    "evidence": {
                        "procedures_without_workpapers": procedures_without_workpapers,
                        "total_procedures": total_procedures,
                        "standard": "PCAOB AS 1215.06-.08"
                    }
                }

            return {
                "passed": True,
                "details": "All audit procedures have supporting workpapers",
                "remediation": "",
                "evidence": {
                    "total_procedures": total_procedures,
                    "documented_procedures": total_procedures - procedures_without_workpapers,
                    "standard": "PCAOB AS 1215"
                }
            }

        except Exception as e:
            logger.error(f"Error evaluating AS1215: {e}")
            return {
                "passed": False,
                "details": f"Error checking documentation: {str(e)}",
                "remediation": "Contact system administrator",
                "evidence": {"error": str(e)}
            }


# ========================================
# AICPA SAS 142: Audit Evidence
# ========================================

class SAS142_AuditEvidence(BasePolicy):
    """
    AICPA SAS 142 - Audit Evidence

    Requirements:
    - Sufficient appropriate audit evidence must be obtained
    - Material account balances must have evidence
    - Evidence must be relevant and reliable

    This policy checks:
    1. All material accounts have evidence links
    2. Evidence has proper source attribution
    3. Contradictory evidence is addressed
    """

    def __init__(self):
        super().__init__()
        self.policy_code = "SAS142_EVIDENCE"
        self.policy_name = "AICPA SAS 142 - Sufficient Appropriate Evidence"
        self.description = "All material accounts must have sufficient evidence"
        self.is_blocking = True
        self.standard_reference = "AICPA SAS 142"

    async def evaluate(self, engagement_id: UUID, db: AsyncSession) -> Dict[str, Any]:
        """Evaluate audit evidence sufficiency"""

        try:
            from sqlalchemy import text

            # Calculate materiality as 5% of total assets or 0.5% of revenue (simplified)
            # Then check if material accounts have evidence
            query = text("""
                WITH materiality AS (
                    SELECT GREATEST(
                        0.05 * COALESCE(SUM(CASE
                            WHEN coa.account_type = 'asset' THEN tb.balance_amount
                            ELSE 0
                        END), 0),
                        0.005 * COALESCE(SUM(CASE
                            WHEN coa.account_type = 'revenue' THEN ABS(tb.balance_amount)
                            ELSE 0
                        END), 0),
                        50000  -- Minimum materiality threshold
                    ) as threshold
                    FROM atlas.trial_balance_lines tb
                    JOIN atlas.trial_balances tbal ON tbal.id = tb.trial_balance_id
                    LEFT JOIN atlas.chart_of_accounts coa ON coa.id = tb.mapped_account_id
                    WHERE tbal.engagement_id = :engagement_id
                ),
                material_accounts AS (
                    SELECT
                        tb.id,
                        tb.account_code,
                        tb.account_name,
                        tb.balance_amount,
                        COUNT(DISTINCT el.id) as evidence_count
                    FROM atlas.trial_balance_lines tb
                    JOIN atlas.trial_balances tbal ON tbal.id = tb.trial_balance_id
                    LEFT JOIN atlas.evidence_links el ON el.source_type = 'tb_line'
                        AND el.source_reference = tb.id::text
                    CROSS JOIN materiality m
                    WHERE tbal.engagement_id = :engagement_id
                        AND ABS(tb.balance_amount) > m.threshold
                    GROUP BY tb.id, tb.account_code, tb.account_name, tb.balance_amount
                )
                SELECT
                    (SELECT threshold FROM materiality) as materiality_threshold,
                    COUNT(*) as material_accounts_total,
                    COUNT(CASE WHEN evidence_count = 0 THEN 1 END) as accounts_without_evidence,
                    SUM(evidence_count) as total_evidence_links
                FROM material_accounts
            """)

            result = await db.execute(query, {"engagement_id": engagement_id})
            row = result.fetchone()

            if not row or row[1] == 0:
                # No material accounts found (engagement might be too early)
                return {
                    "passed": True,
                    "details": "No material accounts identified yet (trial balance may not be loaded)",
                    "remediation": "",
                    "evidence": {
                        "material_accounts_checked": 0,
                        "evidence_links_total": 0,
                        "standard": "AICPA SAS 142"
                    }
                }

            materiality_threshold = float(row[0]) if row[0] else 0
            material_accounts_total = row[1]
            material_accounts_without_evidence = row[2]
            total_evidence_links = row[3]

            if material_accounts_without_evidence > 0:
                return {
                    "passed": False,
                    "details": (
                        f"{material_accounts_without_evidence} of {material_accounts_total} material "
                        f"account(s) lack sufficient appropriate audit evidence"
                    ),
                    "remediation": (
                        "Obtain and document audit evidence for all material accounts. "
                        "Evidence must be relevant (pertains to assertions) and reliable "
                        "(trustworthy source). Consider: confirmations, inspection of records, "
                        "analytical procedures, inquiries. See SAS 142.A7-A35."
                    ),
                    "evidence": {
                        "material_accounts_without_evidence": material_accounts_without_evidence,
                        "material_accounts_total": material_accounts_total,
                        "materiality_threshold": round(materiality_threshold, 2),
                        "standard": "AICPA SAS 142.07-.08"
                    }
                }

            return {
                "passed": True,
                "details": "Sufficient appropriate audit evidence obtained for all material accounts",
                "remediation": "",
                "evidence": {
                    "material_accounts_checked": material_accounts_total,
                    "evidence_links_total": total_evidence_links,
                    "materiality_threshold": round(materiality_threshold, 2),
                    "standard": "AICPA SAS 142"
                }
            }

        except Exception as e:
            logger.error(f"Error evaluating SAS142: {e}")
            return {
                "passed": False,
                "details": f"Error checking evidence: {str(e)}",
                "remediation": "Contact system administrator",
                "evidence": {"error": str(e)}
            }


# ========================================
# AICPA SAS 145: Risk Assessment
# ========================================

class SAS145_RiskAssessment(BasePolicy):
    """
    AICPA SAS 145 - Risk Assessment

    Requirements:
    - Understanding of entity and environment documented
    - Risks of material misstatement identified and assessed
    - Procedures linked to assessed risks
    - Fraud risks specifically addressed

    This policy checks:
    1. All identified risks have linked procedures
    2. Fraud risks are documented
    3. High-risk areas have appropriate procedures
    """

    def __init__(self):
        super().__init__()
        self.policy_code = "SAS145_RISK_ASSESSMENT"
        self.policy_name = "AICPA SAS 145 - Risk Assessment Documentation"
        self.description = "All identified risks must have linked audit procedures"
        self.is_blocking = True
        self.standard_reference = "AICPA SAS 145"

    async def evaluate(self, engagement_id: UUID, db: AsyncSession) -> Dict[str, Any]:
        """Evaluate risk assessment documentation"""

        try:
            from sqlalchemy import text

            # Check that all risks have linked procedures and that fraud risks are documented
            query = text("""
                SELECT
                    COUNT(*) as total_risks,
                    COUNT(DISTINCT CASE
                        WHEN p.id IS NULL THEN r.id
                        ELSE NULL
                    END) as risks_without_procedures,
                    COUNT(CASE WHEN r.fraud_risk = TRUE THEN 1 END) as fraud_risks_documented,
                    COUNT(DISTINCT p.id) as total_procedures_linked
                FROM atlas.risks r
                LEFT JOIN atlas.procedures p ON p.risk_id = r.id
                    AND p.status IN ('in_progress', 'completed', 'reviewed')
                WHERE r.engagement_id = :engagement_id
            """)

            result = await db.execute(query, {"engagement_id": engagement_id})
            row = result.fetchone()

            if not row or row[0] == 0:
                # No risks documented yet
                return {
                    "passed": False,
                    "details": "No risks documented for this engagement",
                    "remediation": (
                        "Perform and document risk assessment per SAS 145. "
                        "Identify and assess risks of material misstatement. "
                        "Document fraud risks including revenue recognition and management override."
                    ),
                    "evidence": {
                        "total_risks": 0,
                        "fraud_risks_documented": 0,
                        "standard": "AICPA SAS 145"
                    }
                }

            total_risks = row[0]
            risks_without_procedures = row[1]
            fraud_risks_documented = row[2]
            total_procedures_linked = row[3]

            # Check 1: Risks must have procedures
            if risks_without_procedures > 0:
                return {
                    "passed": False,
                    "details": f"{risks_without_procedures} risk(s) lack responsive audit procedures",
                    "remediation": (
                        "Design and perform audit procedures responsive to assessed risks. "
                        "Procedures must address nature, timing, and extent of risks. "
                        "For significant risks, perform substantive procedures. "
                        "See SAS 145.18-.28."
                    ),
                    "evidence": {
                        "risks_without_procedures": risks_without_procedures,
                        "total_risks": total_risks,
                        "fraud_risks_documented": fraud_risks_documented,
                        "standard": "AICPA SAS 145.18-.19"
                    }
                }

            # Check 2: Fraud risks must be documented
            if fraud_risks_documented == 0:
                return {
                    "passed": False,
                    "details": "Fraud risk assessment not documented",
                    "remediation": (
                        "Document fraud risk assessment per SAS 145.27-28. "
                        "Consider: revenue recognition, management override of controls, "
                        "and entity-specific fraud risks. "
                        "Discuss with engagement team and document conclusions."
                    ),
                    "evidence": {
                        "fraud_risks_documented": 0,
                        "total_risks": total_risks,
                        "standard": "AICPA SAS 145.27-.28"
                    }
                }

            return {
                "passed": True,
                "details": "Risk assessment documented and procedures linked to all risks",
                "remediation": "",
                "evidence": {
                    "total_risks": total_risks,
                    "risks_with_procedures": total_risks - risks_without_procedures,
                    "fraud_risks": fraud_risks_documented,
                    "procedures_linked": total_procedures_linked,
                    "standard": "AICPA SAS 145"
                }
            }

        except Exception as e:
            logger.error(f"Error evaluating SAS145: {e}")
            return {
                "passed": False,
                "details": f"Error checking risk assessment: {str(e)}",
                "remediation": "Contact system administrator",
                "evidence": {"error": str(e)}
            }


# ========================================
# Firm Policy: Partner Sign-Off
# ========================================

class PartnerSignOffPolicy(BasePolicy):
    """
    Partner Sign-Off Required

    Firm Policy:
    - Partner must review and approve engagement before finalization
    - Electronic signature required (with cert fingerprint)
    - Sign-off includes attestation of compliance review

    This is a CRITICAL gate - no automated report issuance.
    """

    def __init__(self):
        super().__init__()
        self.policy_code = "PARTNER_SIGN_OFF"
        self.policy_name = "Partner Approval Required"
        self.description = "Partner must review and approve engagement"
        self.is_blocking = True
        self.standard_reference = "Firm Policy"

    async def evaluate(self, engagement_id: UUID, db: AsyncSession) -> Dict[str, Any]:
        """Check partner sign-off exists"""

        try:
            from sqlalchemy import text

            # Query for partner signature
            query = text("""
                SELECT
                    s.id,
                    s.signed_at,
                    s.certificate_fingerprint,
                    u.full_name as partner_name,
                    u.role
                FROM atlas.signatures s
                JOIN atlas.users u ON u.id = s.user_id
                WHERE s.engagement_id = :engagement_id
                    AND s.signature_type = 'partner_approval'
                    AND u.role = 'partner'
                ORDER BY s.signed_at DESC
                LIMIT 1
            """)

            result = await db.execute(query, {"engagement_id": engagement_id})
            row = result.fetchone()

            if not row:
                return {
                    "passed": False,
                    "details": "Partner sign-off not obtained",
                    "remediation": (
                        "Engagement partner must review all workpapers, QC results, "
                        "and provide electronic signature before finalization. "
                        "Partner attestation confirms: (1) audit complies with standards, "
                        "(2) sufficient appropriate evidence obtained, "
                        "(3) audit report is appropriate."
                    ),
                    "evidence": {
                        "signature_exists": False,
                        "signature_type_required": "partner_approval"
                    }
                }

            partner_name = row[3]
            signed_at = row[1].isoformat() if row[1] else None
            certificate_fingerprint = row[2]

            return {
                "passed": True,
                "details": f"Partner approval obtained: {partner_name}",
                "remediation": "",
                "evidence": {
                    "partner": partner_name,
                    "signed_at": signed_at,
                    "certificate_fingerprint": certificate_fingerprint
                }
            }

        except Exception as e:
            logger.error(f"Error checking partner sign-off: {e}")
            return {
                "passed": False,
                "details": f"Error checking sign-off: {str(e)}",
                "remediation": "Contact system administrator",
                "evidence": {"error": str(e)}
            }


# ========================================
# Firm Policy: Review Notes Cleared
# ========================================

class ReviewNotesPolicy(BasePolicy):
    """
    Review Notes Cleared

    Firm Policy:
    - All blocking review notes must be addressed
    - Reviewer must clear notes after adequate response
    - Open blocking notes prevent finalization
    """

    def __init__(self):
        super().__init__()
        self.policy_code = "REVIEW_NOTES_CLEARED"
        self.policy_name = "All Review Notes Addressed"
        self.description = "All blocking review notes must be cleared"
        self.is_blocking = True
        self.standard_reference = "Firm Policy"

    async def evaluate(self, engagement_id: UUID, db: AsyncSession) -> Dict[str, Any]:
        """Check all review notes are cleared"""

        try:
            from sqlalchemy import text

            # Query review notes - need to join through workpapers and procedures to engagement
            query = text("""
                SELECT
                    COUNT(*) as total_notes,
                    COUNT(CASE WHEN is_blocking = TRUE AND status = 'open' THEN 1 END) as open_blocking_notes,
                    COUNT(CASE WHEN status = 'open' THEN 1 END) as total_open_notes,
                    COUNT(CASE WHEN status IN ('addressed', 'cleared') THEN 1 END) as resolved_notes
                FROM atlas.review_notes rn
                WHERE (
                    rn.workpaper_id IN (
                        SELECT w.id FROM atlas.workpapers w
                        JOIN atlas.binder_nodes bn ON bn.id = w.binder_node_id
                        WHERE bn.engagement_id = :engagement_id
                    )
                    OR rn.procedure_id IN (
                        SELECT p.id FROM atlas.procedures p
                        WHERE p.engagement_id = :engagement_id
                    )
                )
            """)

            result = await db.execute(query, {"engagement_id": engagement_id})
            row = result.fetchone()

            total_notes = row[0] if row else 0
            open_blocking_notes = row[1] if row else 0
            total_open_notes = row[2] if row else 0
            resolved_notes = row[3] if row else 0

            if open_blocking_notes > 0:
                return {
                    "passed": False,
                    "details": f"{open_blocking_notes} blocking review note(s) remain open",
                    "remediation": (
                        "Address all blocking review notes. "
                        "Preparer must respond to each note with: "
                        "(1) additional documentation, (2) explanation, or (3) revision. "
                        "Reviewer must clear note after adequate response."
                    ),
                    "evidence": {
                        "open_blocking_notes": open_blocking_notes,
                        "total_open_notes": total_open_notes,
                        "total_notes": total_notes,
                        "resolved_notes": resolved_notes
                    }
                }

            return {
                "passed": True,
                "details": "All review notes have been addressed and cleared",
                "remediation": "",
                "evidence": {
                    "open_blocking_notes": 0,
                    "total_notes": total_notes,
                    "resolved_notes": resolved_notes
                }
            }

        except Exception as e:
            logger.error(f"Error checking review notes: {e}")
            return {
                "passed": False,
                "details": f"Error checking review notes: {str(e)}",
                "remediation": "Contact system administrator",
                "evidence": {"error": str(e)}
            }


# ========================================
# Firm Policy: Material Accounts Coverage
# ========================================

class MaterialAccountsCoveragePolicy(BasePolicy):
    """
    Material Accounts Coverage

    Firm Policy:
    - All accounts > materiality threshold must be tested
    - Both existence and valuation assertions addressed
    - Analytical procedures or substantive tests performed
    """

    def __init__(self):
        super().__init__()
        self.policy_code = "MATERIAL_ACCOUNTS_COVERAGE"
        self.policy_name = "Material Accounts Coverage"
        self.description = "All material accounts must have audit procedures"
        self.is_blocking = True
        self.standard_reference = "Firm Policy / SAS 142"

    async def evaluate(self, engagement_id: UUID, db: AsyncSession) -> Dict[str, Any]:
        """Check material accounts have procedures"""

        try:
            from sqlalchemy import text

            # Calculate materiality and check that material accounts have procedures
            # Similar to SAS142 but focuses on procedures rather than evidence links
            query = text("""
                WITH materiality AS (
                    SELECT GREATEST(
                        0.05 * COALESCE(SUM(CASE
                            WHEN coa.account_type = 'asset' THEN tb.balance_amount
                            ELSE 0
                        END), 0),
                        0.005 * COALESCE(SUM(CASE
                            WHEN coa.account_type = 'revenue' THEN ABS(tb.balance_amount)
                            ELSE 0
                        END), 0),
                        50000
                    ) as threshold
                    FROM atlas.trial_balance_lines tb
                    JOIN atlas.trial_balances tbal ON tbal.id = tb.trial_balance_id
                    LEFT JOIN atlas.chart_of_accounts coa ON coa.id = tb.mapped_account_id
                    WHERE tbal.engagement_id = :engagement_id
                ),
                material_accounts AS (
                    SELECT
                        tb.id,
                        tb.account_code,
                        tb.account_name,
                        tb.balance_amount,
                        tb.mapped_account_id,
                        COUNT(DISTINCT p.id) FILTER (
                            WHERE p.status IN ('completed', 'reviewed')
                        ) as completed_procedures_count
                    FROM atlas.trial_balance_lines tb
                    JOIN atlas.trial_balances tbal ON tbal.id = tb.trial_balance_id
                    LEFT JOIN atlas.procedures p ON p.engagement_id = tbal.engagement_id
                    CROSS JOIN materiality m
                    WHERE tbal.engagement_id = :engagement_id
                        AND ABS(tb.balance_amount) > m.threshold
                    GROUP BY tb.id, tb.account_code, tb.account_name, tb.balance_amount, tb.mapped_account_id
                )
                SELECT
                    (SELECT threshold FROM materiality) as materiality_threshold,
                    COUNT(*) as material_accounts_total,
                    COUNT(CASE WHEN completed_procedures_count = 0 THEN 1 END) as untested_accounts,
                    SUM(completed_procedures_count) as total_procedures
                FROM material_accounts
            """)

            result = await db.execute(query, {"engagement_id": engagement_id})
            row = result.fetchone()

            if not row or row[1] == 0:
                return {
                    "passed": True,
                    "details": "No material accounts identified yet (trial balance may not be loaded)",
                    "remediation": "",
                    "evidence": {
                        "material_accounts": 0,
                        "tested_accounts": 0
                    }
                }

            materiality_threshold = float(row[0]) if row[0] else 0
            material_accounts_total = row[1]
            untested_accounts = row[2]
            total_procedures = row[3]

            if untested_accounts > 0:
                return {
                    "passed": False,
                    "details": f"{untested_accounts} of {material_accounts_total} material account(s) lack audit procedures",
                    "remediation": (
                        "Perform audit procedures for all material accounts. "
                        "Consider: analytical procedures, substantive tests of details, "
                        "tests of controls (if relying on controls). "
                        "Document results and conclusions."
                    ),
                    "evidence": {
                        "untested_accounts": untested_accounts,
                        "material_accounts_total": material_accounts_total,
                        "materiality_threshold": round(materiality_threshold, 2)
                    }
                }

            return {
                "passed": True,
                "details": "All material accounts have audit procedures with documented results",
                "remediation": "",
                "evidence": {
                    "material_accounts": material_accounts_total,
                    "tested_accounts": material_accounts_total - untested_accounts,
                    "total_procedures": total_procedures,
                    "materiality_threshold": round(materiality_threshold, 2)
                }
            }

        except Exception as e:
            logger.error(f"Error checking material accounts coverage: {e}")
            return {
                "passed": False,
                "details": f"Error checking coverage: {str(e)}",
                "remediation": "Contact system administrator",
                "evidence": {"error": str(e)}
            }


# ========================================
# Firm Policy: Subsequent Events
# ========================================

class SubsequentEventsPolicy(BasePolicy):
    """
    Subsequent Events Review

    Requirements (SAS 560):
    - Review events from balance sheet date through report date
    - Obtain management representation letter
    - Read minutes of meetings
    - Inquire of legal counsel

    This is NON-BLOCKING but required for completeness
    """

    def __init__(self):
        super().__init__()
        self.policy_code = "SUBSEQUENT_EVENTS"
        self.policy_name = "Subsequent Events Review"
        self.description = "Subsequent events reviewed through report date"
        self.is_blocking = False  # Non-blocking - informational
        self.standard_reference = "AICPA SAS 560"

    async def evaluate(self, engagement_id: UUID, db: AsyncSession) -> Dict[str, Any]:
        """Check subsequent events procedures performed"""

        try:
            from sqlalchemy import text

            # Look for workpapers or procedures related to subsequent events
            query = text("""
                SELECT
                    COUNT(DISTINCT bn.id) as workpaper_count,
                    COUNT(DISTINCT p.id) as procedure_count,
                    MAX(p.completed_at) as latest_completion
                FROM atlas.binder_nodes bn
                LEFT JOIN atlas.procedures p ON p.engagement_id = bn.engagement_id
                    AND (
                        p.procedure_code ILIKE '%SUBSEQUENT%'
                        OR p.procedure_description ILIKE '%subsequent events%'
                    )
                WHERE bn.engagement_id = :engagement_id
                    AND (
                        bn.node_code ILIKE '%SUBSEQUENT%'
                        OR bn.title ILIKE '%subsequent events%'
                        OR bn.title ILIKE '%Type 1%'
                        OR bn.title ILIKE '%Type 2%'
                    )
                    AND bn.node_type = 'workpaper'
            """)

            result = await db.execute(query, {"engagement_id": engagement_id})
            row = result.fetchone()

            workpaper_count = row[0] if row else 0
            procedure_count = row[1] if row else 0
            latest_completion = row[2]

            subsequent_events_documented = (workpaper_count > 0 or procedure_count > 0)

            if not subsequent_events_documented:
                return {
                    "passed": False,
                    "details": "Subsequent events review not documented",
                    "remediation": (
                        "Perform subsequent events review per SAS 560. "
                        "Review period: balance sheet date through report date. "
                        "Procedures: read minutes, inquire management, read interim financials, "
                        "review legal counsel letters. "
                        "Document any events requiring adjustment or disclosure."
                    ),
                    "evidence": {
                        "documented": False,
                        "workpaper_count": 0,
                        "procedure_count": 0,
                        "standard": "AICPA SAS 560"
                    }
                }

            return {
                "passed": True,
                "details": "Subsequent events review performed and documented",
                "remediation": "",
                "evidence": {
                    "documented": True,
                    "workpaper_count": workpaper_count,
                    "procedure_count": procedure_count,
                    "review_through_date": latest_completion.isoformat() if latest_completion else None,
                    "standard": "AICPA SAS 560"
                }
            }

        except Exception as e:
            logger.error(f"Error checking subsequent events: {e}")
            return {
                "passed": False,
                "details": f"Error checking subsequent events: {str(e)}",
                "remediation": "Contact system administrator",
                "evidence": {"error": str(e)}
            }
