"""Unit tests for QC policies"""
import pytest
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock

from app.policies import (
    PolicyRegistry,
    AS1215_AuditDocumentation,
    SAS142_AuditEvidence,
    SAS145_RiskAssessment,
    PartnerSignOffPolicy,
    ReviewNotesPolicy,
    MaterialAccountsCoveragePolicy,
    SubsequentEventsPolicy
)


class TestPolicyRegistry:
    """Test policy registry functionality"""

    def test_register_policy(self):
        """Test registering a policy"""
        registry = PolicyRegistry()
        policy = AS1215_AuditDocumentation()

        registry.register(policy)

        assert "AS1215_DOCUMENTATION" in registry.policies
        assert registry.policies["AS1215_DOCUMENTATION"] == policy

    def test_get_policy(self):
        """Test retrieving a policy"""
        registry = PolicyRegistry()
        policy = AS1215_AuditDocumentation()
        registry.register(policy)

        retrieved = registry.get("AS1215_DOCUMENTATION")

        assert retrieved is not None
        assert retrieved.policy_code == "AS1215_DOCUMENTATION"

    def test_get_nonexistent_policy(self):
        """Test retrieving nonexistent policy returns None"""
        registry = PolicyRegistry()

        retrieved = registry.get("NONEXISTENT")

        assert retrieved is None

    def test_list_all_policies(self):
        """Test listing all policies"""
        registry = PolicyRegistry()
        policy1 = AS1215_AuditDocumentation()
        policy2 = SAS142_AuditEvidence()

        registry.register(policy1)
        registry.register(policy2)

        all_policies = registry.list_all()

        assert len(all_policies) == 2
        assert policy1 in all_policies
        assert policy2 in all_policies


class TestAS1215_AuditDocumentation:
    """Test PCAOB AS 1215 policy"""

    def test_policy_attributes(self):
        """Test policy has correct attributes"""
        policy = AS1215_AuditDocumentation()

        assert policy.policy_code == "AS1215_DOCUMENTATION"
        assert policy.policy_name == "PCAOB AS 1215 - Audit Documentation Complete"
        assert policy.is_blocking is True
        assert policy.standard_reference == "PCAOB AS 1215"
        assert "workpapers" in policy.description.lower()

    @pytest.mark.asyncio
    async def test_evaluate_passes_when_all_documented(self):
        """Test policy passes when all procedures documented"""
        policy = AS1215_AuditDocumentation()
        engagement_id = uuid4()
        db = AsyncMock()

        # Mock database response: 10 procedures, 0 without workpapers
        mock_result = MagicMock()
        mock_result.fetchone.return_value = (10, 0)  # total_procedures, procedures_without_workpapers
        db.execute = AsyncMock(return_value=mock_result)

        result = await policy.evaluate(engagement_id, db)

        assert result["passed"] is True
        assert "evidence" in result
        assert result["evidence"]["total_procedures"] == 10
        assert result["evidence"]["documented_procedures"] == 10
        assert result["remediation"] == ""

    @pytest.mark.asyncio
    async def test_evaluate_fails_when_undocumented_procedures(self):
        """Test policy fails when procedures lack workpapers"""
        policy = AS1215_AuditDocumentation()
        engagement_id = uuid4()
        db = AsyncMock()

        # Mock database response: 10 procedures, 3 without workpapers
        mock_result = MagicMock()
        mock_result.fetchone.return_value = (10, 3)  # total_procedures, procedures_without_workpapers
        db.execute = AsyncMock(return_value=mock_result)

        result = await policy.evaluate(engagement_id, db)

        assert result["passed"] is False
        assert "3 procedure(s) lack supporting workpapers" in result["details"]
        assert "PCAOB AS 1215" in result["remediation"]
        assert result["evidence"]["procedures_without_workpapers"] == 3


class TestSAS142_AuditEvidence:
    """Test AICPA SAS 142 policy"""

    def test_policy_attributes(self):
        """Test policy has correct attributes"""
        policy = SAS142_AuditEvidence()

        assert policy.policy_code == "SAS142_EVIDENCE"
        assert policy.policy_name == "AICPA SAS 142 - Sufficient Appropriate Evidence"
        assert policy.is_blocking is True
        assert policy.standard_reference == "AICPA SAS 142"
        assert "evidence" in policy.description.lower()

    @pytest.mark.asyncio
    async def test_evaluate_structure(self):
        """Test policy evaluation returns proper structure"""
        policy = SAS142_AuditEvidence()
        engagement_id = uuid4()
        db = AsyncMock()

        # Mock database response: materiality_threshold, material_accounts_total, accounts_without_evidence, total_evidence_links
        mock_result = MagicMock()
        mock_result.fetchone.return_value = (100000.0, 5, 0, 15)
        db.execute = AsyncMock(return_value=mock_result)

        result = await policy.evaluate(engagement_id, db)

        assert "passed" in result
        assert isinstance(result["passed"], bool)
        assert "details" in result
        assert isinstance(result["details"], str)
        assert "remediation" in result
        assert "evidence" in result
        assert isinstance(result["evidence"], dict)

    @pytest.mark.asyncio
    async def test_evaluate_passes_with_evidence(self):
        """Test policy passes when all material accounts have evidence"""
        policy = SAS142_AuditEvidence()
        engagement_id = uuid4()
        db = AsyncMock()

        # Mock: 100k materiality, 5 material accounts, 0 without evidence, 15 evidence links
        mock_result = MagicMock()
        mock_result.fetchone.return_value = (100000.0, 5, 0, 15)
        db.execute = AsyncMock(return_value=mock_result)

        result = await policy.evaluate(engagement_id, db)

        assert result["passed"] is True
        assert result["evidence"]["material_accounts_checked"] == 5
        assert result["evidence"]["evidence_links_total"] == 15

    @pytest.mark.asyncio
    async def test_evaluate_fails_without_evidence(self):
        """Test policy fails when material accounts lack evidence"""
        policy = SAS142_AuditEvidence()
        engagement_id = uuid4()
        db = AsyncMock()

        # Mock: 100k materiality, 5 material accounts, 2 without evidence, 10 evidence links
        mock_result = MagicMock()
        mock_result.fetchone.return_value = (100000.0, 5, 2, 10)
        db.execute = AsyncMock(return_value=mock_result)

        result = await policy.evaluate(engagement_id, db)

        assert result["passed"] is False
        assert "2 of 5 material account(s) lack" in result["details"]
        assert result["evidence"]["material_accounts_without_evidence"] == 2


class TestSAS145_RiskAssessment:
    """Test AICPA SAS 145 policy"""

    def test_policy_attributes(self):
        """Test policy has correct attributes"""
        policy = SAS145_RiskAssessment()

        assert policy.policy_code == "SAS145_RISK_ASSESSMENT"
        assert policy.policy_name == "AICPA SAS 145 - Risk Assessment Documentation"
        assert policy.is_blocking is True
        assert policy.standard_reference == "AICPA SAS 145"

    @pytest.mark.asyncio
    async def test_evaluate_checks_risk_linkage(self):
        """Test policy checks risks have procedures"""
        policy = SAS145_RiskAssessment()
        engagement_id = uuid4()
        db = AsyncMock()

        # Mock: 8 total risks, 0 without procedures, 2 fraud risks, 15 procedures linked
        mock_result = MagicMock()
        mock_result.fetchone.return_value = (8, 0, 2, 15)
        db.execute = AsyncMock(return_value=mock_result)

        result = await policy.evaluate(engagement_id, db)

        assert result["passed"] is True
        assert result["evidence"]["total_risks"] == 8
        assert result["evidence"]["fraud_risks"] == 2

    @pytest.mark.asyncio
    async def test_evaluate_checks_fraud_risks(self):
        """Test policy requires fraud risk documentation"""
        policy = SAS145_RiskAssessment()
        engagement_id = uuid4()
        db = AsyncMock()

        # Mock: 5 risks, 0 without procedures, but 0 fraud risks documented
        mock_result = MagicMock()
        mock_result.fetchone.return_value = (5, 0, 0, 10)
        db.execute = AsyncMock(return_value=mock_result)

        result = await policy.evaluate(engagement_id, db)

        assert result["passed"] is False
        assert "fraud risk" in result["details"].lower()
        assert result["evidence"]["fraud_risks_documented"] == 0

    @pytest.mark.asyncio
    async def test_evaluate_fails_when_risks_lack_procedures(self):
        """Test policy fails when risks lack procedures"""
        policy = SAS145_RiskAssessment()
        engagement_id = uuid4()
        db = AsyncMock()

        # Mock: 8 risks, 2 without procedures, 1 fraud risk, 10 procedures
        mock_result = MagicMock()
        mock_result.fetchone.return_value = (8, 2, 1, 10)
        db.execute = AsyncMock(return_value=mock_result)

        result = await policy.evaluate(engagement_id, db)

        assert result["passed"] is False
        assert "2 risk(s) lack responsive audit procedures" in result["details"]


class TestPartnerSignOffPolicy:
    """Test partner sign-off policy"""

    def test_policy_attributes(self):
        """Test policy has correct attributes"""
        policy = PartnerSignOffPolicy()

        assert policy.policy_code == "PARTNER_SIGN_OFF"
        assert policy.policy_name == "Partner Approval Required"
        assert policy.is_blocking is True
        assert policy.standard_reference == "Firm Policy"

    @pytest.mark.asyncio
    async def test_evaluate_fails_without_signature(self):
        """Test policy fails when no partner signature"""
        policy = PartnerSignOffPolicy()
        engagement_id = uuid4()
        db = AsyncMock()

        # Mock: No signature found (None result)
        mock_result = MagicMock()
        mock_result.fetchone.return_value = None
        db.execute = AsyncMock(return_value=mock_result)

        result = await policy.evaluate(engagement_id, db)

        assert result["passed"] is False
        assert "sign-off" in result["details"].lower()
        assert len(result["remediation"]) > 0
        assert result["evidence"]["signature_exists"] is False

    @pytest.mark.asyncio
    async def test_evaluate_passes_with_signature(self):
        """Test policy passes when partner has signed"""
        from datetime import datetime
        policy = PartnerSignOffPolicy()
        engagement_id = uuid4()
        db = AsyncMock()

        # Mock: Partner signature found (id, signed_at, cert_fingerprint, partner_name, role)
        mock_result = MagicMock()
        mock_result.fetchone.return_value = (
            uuid4(),
            datetime(2024, 1, 15, 10, 30),
            "SHA256:abc123...",
            "Jane Partner, CPA",
            "partner"
        )
        db.execute = AsyncMock(return_value=mock_result)

        result = await policy.evaluate(engagement_id, db)

        assert result["passed"] is True
        assert "Jane Partner, CPA" in result["details"]
        assert result["evidence"]["partner"] == "Jane Partner, CPA"

    @pytest.mark.asyncio
    async def test_remediation_explains_requirements(self):
        """Test remediation provides clear instructions"""
        policy = PartnerSignOffPolicy()
        engagement_id = uuid4()
        db = AsyncMock()

        # Mock: No signature
        mock_result = MagicMock()
        mock_result.fetchone.return_value = None
        db.execute = AsyncMock(return_value=mock_result)

        result = await policy.evaluate(engagement_id, db)

        remediation = result["remediation"].lower()
        assert "partner" in remediation
        assert "review" in remediation or "signature" in remediation or "electronic" in remediation


class TestReviewNotesPolicy:
    """Test review notes policy"""

    def test_policy_attributes(self):
        """Test policy has correct attributes"""
        policy = ReviewNotesPolicy()

        assert policy.policy_code == "REVIEW_NOTES_CLEARED"
        assert policy.policy_name == "All Review Notes Addressed"
        assert policy.is_blocking is True

    @pytest.mark.asyncio
    async def test_evaluate_passes_when_no_open_notes(self):
        """Test policy passes when all notes cleared"""
        policy = ReviewNotesPolicy()
        engagement_id = uuid4()
        db = AsyncMock()

        # Mock: total_notes, open_blocking_notes, total_open_notes, resolved_notes
        mock_result = MagicMock()
        mock_result.fetchone.return_value = (10, 0, 0, 10)
        db.execute = AsyncMock(return_value=mock_result)

        result = await policy.evaluate(engagement_id, db)

        assert result["passed"] is True
        assert "evidence" in result
        assert result["evidence"]["open_blocking_notes"] == 0
        assert result["evidence"]["total_notes"] == 10

    @pytest.mark.asyncio
    async def test_evaluate_fails_with_open_blocking_notes(self):
        """Test policy fails when blocking notes remain open"""
        policy = ReviewNotesPolicy()
        engagement_id = uuid4()
        db = AsyncMock()

        # Mock: 15 total notes, 3 open blocking notes, 4 total open, 11 resolved
        mock_result = MagicMock()
        mock_result.fetchone.return_value = (15, 3, 4, 11)
        db.execute = AsyncMock(return_value=mock_result)

        result = await policy.evaluate(engagement_id, db)

        assert result["passed"] is False
        assert "3 blocking review note(s) remain open" in result["details"]
        assert result["evidence"]["open_blocking_notes"] == 3


class TestMaterialAccountsCoveragePolicy:
    """Test material accounts coverage policy"""

    def test_policy_attributes(self):
        """Test policy has correct attributes"""
        policy = MaterialAccountsCoveragePolicy()

        assert policy.policy_code == "MATERIAL_ACCOUNTS_COVERAGE"
        assert policy.is_blocking is True
        assert "SAS 142" in policy.standard_reference

    @pytest.mark.asyncio
    async def test_evaluate_checks_materiality(self):
        """Test policy considers materiality threshold"""
        policy = MaterialAccountsCoveragePolicy()
        engagement_id = uuid4()
        db = AsyncMock()

        # Mock: materiality_threshold, material_accounts_total, untested_accounts, total_procedures
        mock_result = MagicMock()
        mock_result.fetchone.return_value = (75000.0, 8, 0, 20)
        db.execute = AsyncMock(return_value=mock_result)

        result = await policy.evaluate(engagement_id, db)

        assert result["passed"] is True
        assert "evidence" in result
        assert result["evidence"]["materiality_threshold"] == 75000.0

    @pytest.mark.asyncio
    async def test_evaluate_fails_with_untested_accounts(self):
        """Test policy fails when material accounts lack procedures"""
        policy = MaterialAccountsCoveragePolicy()
        engagement_id = uuid4()
        db = AsyncMock()

        # Mock: 75k materiality, 8 material accounts, 2 untested, 15 procedures
        mock_result = MagicMock()
        mock_result.fetchone.return_value = (75000.0, 8, 2, 15)
        db.execute = AsyncMock(return_value=mock_result)

        result = await policy.evaluate(engagement_id, db)

        assert result["passed"] is False
        assert "2 of 8 material account(s) lack audit procedures" in result["details"]
        assert result["evidence"]["untested_accounts"] == 2


class TestSubsequentEventsPolicy:
    """Test subsequent events policy"""

    def test_policy_attributes(self):
        """Test policy has correct attributes"""
        policy = SubsequentEventsPolicy()

        assert policy.policy_code == "SUBSEQUENT_EVENTS"
        assert policy.is_blocking is False  # NON-BLOCKING
        assert "SAS 560" in policy.standard_reference

    @pytest.mark.asyncio
    async def test_evaluate_nonblocking(self):
        """Test policy is non-blocking"""
        policy = SubsequentEventsPolicy()

        # Verify it's non-blocking
        assert policy.is_blocking is False

    @pytest.mark.asyncio
    async def test_evaluate_recommends_procedures(self):
        """Test policy recommends specific procedures"""
        policy = SubsequentEventsPolicy()
        engagement_id = uuid4()
        db = AsyncMock()

        # Mock: No subsequent events workpapers/procedures found
        mock_result = MagicMock()
        mock_result.fetchone.return_value = (0, 0, None)
        db.execute = AsyncMock(return_value=mock_result)

        result = await policy.evaluate(engagement_id, db)

        assert result["passed"] is False
        remediation = result["remediation"].lower()
        # Should mention key subsequent events procedures
        assert any(keyword in remediation for keyword in ["minutes", "inquire", "legal", "interim"])

    @pytest.mark.asyncio
    async def test_evaluate_passes_with_documentation(self):
        """Test policy passes when subsequent events documented"""
        from datetime import datetime
        policy = SubsequentEventsPolicy()
        engagement_id = uuid4()
        db = AsyncMock()

        # Mock: workpaper_count, procedure_count, latest_completion
        mock_result = MagicMock()
        mock_result.fetchone.return_value = (1, 2, datetime(2024, 2, 15, 14, 30))
        db.execute = AsyncMock(return_value=mock_result)

        result = await policy.evaluate(engagement_id, db)

        assert result["passed"] is True
        assert result["evidence"]["workpaper_count"] == 1
        assert result["evidence"]["procedure_count"] == 2


class TestPolicyEvaluationErrorHandling:
    """Test error handling in policy evaluation"""

    @pytest.mark.asyncio
    async def test_evaluation_handles_database_errors(self):
        """Test policy gracefully handles database errors"""
        policy = AS1215_AuditDocumentation()
        engagement_id = uuid4()

        # Mock database that raises exception
        db = AsyncMock()
        db.execute.side_effect = Exception("Database connection failed")

        result = await policy.evaluate(engagement_id, db)

        # Should return failed result with error details, not raise exception
        assert result["passed"] is False
        assert "error" in result["details"].lower()
        assert "evidence" in result
        assert "error" in result["evidence"]

    @pytest.mark.asyncio
    async def test_evaluation_includes_error_in_evidence(self):
        """Test errors are captured in evidence"""
        policy = SAS142_AuditEvidence()
        engagement_id = uuid4()

        # Mock database that raises exception
        db = AsyncMock()
        db.execute.side_effect = Exception("Query timeout")

        result = await policy.evaluate(engagement_id, db)

        # Error should be in evidence
        assert result["passed"] is False
        assert "error" in result["evidence"]
        assert "Query timeout" in result["evidence"]["error"]


class TestComplianceStandards:
    """Test compliance with audit standards"""

    def test_blocking_policies_include_critical_standards(self):
        """Test blocking policies cover PCAOB and AICPA requirements"""
        registry = PolicyRegistry()
        registry.register(AS1215_AuditDocumentation())
        registry.register(SAS142_AuditEvidence())
        registry.register(SAS145_RiskAssessment())
        registry.register(PartnerSignOffPolicy())

        blocking = [p for p in registry.policies.values() if p.is_blocking]

        # All four should be blocking
        assert len(blocking) >= 4

        # Verify critical standards are covered
        standards = [p.standard_reference for p in blocking]
        assert any("PCAOB AS 1215" in s for s in standards if s)
        assert any("SAS 142" in s for s in standards if s)
        assert any("SAS 145" in s for s in standards if s)

    def test_all_policies_have_remediation_guidance(self):
        """Test all policies provide remediation guidance"""
        policies = [
            AS1215_AuditDocumentation(),
            SAS142_AuditEvidence(),
            SAS145_RiskAssessment(),
            PartnerSignOffPolicy(),
            ReviewNotesPolicy(),
            MaterialAccountsCoveragePolicy(),
            SubsequentEventsPolicy()
        ]

        # All policies should have description
        for policy in policies:
            assert len(policy.description) > 0, f"{policy.policy_code} lacks description"
            assert len(policy.policy_name) > 0, f"{policy.policy_code} lacks name"
            assert policy.standard_reference is not None, f"{policy.policy_code} lacks standard reference"
