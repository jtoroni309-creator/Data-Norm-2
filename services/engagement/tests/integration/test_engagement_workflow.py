"""
End-to-End Engagement Workflow Integration Tests

Tests the complete engagement lifecycle:
Draft → Planning → Fieldwork → Review → Finalized

Verifies:
- State transitions work correctly
- QC gates block finalization when policies fail
- Partner signature requirement blocks finalization
- Data flows correctly through all services
- Engagement locking works on finalization
"""

import pytest
from datetime import date, datetime
from uuid import uuid4, UUID
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

from app.main import app
from app.database import get_db, Base
from app.models import EngagementStatus, EngagementType, UserRole


# Test database configuration
TEST_DATABASE_URL = "postgresql+asyncpg://atlas:atlas_secret@db:5432/atlas_test"


@pytest.fixture
async def test_db():
    """Create test database engine and session"""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Create session
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        yield session

    # Cleanup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
async def test_client(test_db):
    """Create test client with database override"""
    async def override_get_db():
        yield test_db

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
async def test_data(test_db):
    """Create test data: user, client, engagement"""
    user_id = uuid4()
    client_id = uuid4()
    partner_id = uuid4()

    # Create test user
    await test_db.execute(
        text("""
            INSERT INTO atlas.users (id, email, first_name, last_name, role)
            VALUES (:user_id, 'test@example.com', 'Test', 'User', 'manager')
        """),
        {"user_id": user_id}
    )

    # Create partner user
    await test_db.execute(
        text("""
            INSERT INTO atlas.users (id, email, first_name, last_name, role)
            VALUES (:partner_id, 'partner@example.com', 'Partner', 'User', 'partner')
        """),
        {"partner_id": partner_id}
    )

    # Create test client
    await test_db.execute(
        text("""
            INSERT INTO atlas.clients (
                id, client_name, primary_contact_name, primary_contact_email,
                fiscal_year_end, is_active
            )
            VALUES (
                :client_id, 'Test Client Inc', 'John Doe', 'john@testclient.com',
                '12-31', TRUE
            )
        """),
        {"client_id": client_id}
    )

    await test_db.commit()

    return {
        "user_id": user_id,
        "client_id": client_id,
        "partner_id": partner_id,
    }


class TestEngagementWorkflow:
    """Test complete engagement workflow from Draft to Finalized"""

    @pytest.mark.asyncio
    async def test_complete_engagement_lifecycle(self, test_client, test_data):
        """
        Test complete engagement lifecycle: Draft → Planning → Fieldwork → Review → Finalized

        This is the core workflow that all audit engagements follow.
        """
        user_id = test_data["user_id"]
        client_id = test_data["client_id"]

        # Step 1: Create engagement in DRAFT status
        create_response = await test_client.post(
            "/engagements",
            json={
                "client_id": str(client_id),
                "name": "2024 Audit - Test Client Inc",
                "engagement_type": "audit",
                "fiscal_year_end": "2024-12-31",
            },
            headers={"X-User-ID": str(user_id)}
        )

        assert create_response.status_code == 201
        engagement = create_response.json()
        engagement_id = engagement["id"]
        assert engagement["status"] == "draft"

        # Step 2: Transition to PLANNING
        planning_response = await test_client.post(
            f"/engagements/{engagement_id}/transition",
            params={"new_status": "planning"},
            headers={"X-User-ID": str(user_id)}
        )

        assert planning_response.status_code == 200

        # Verify status changed
        get_response = await test_client.get(
            f"/engagements/{engagement_id}",
            headers={"X-User-ID": str(user_id)}
        )
        assert get_response.json()["status"] == "planning"

        # Step 3: Transition to FIELDWORK
        fieldwork_response = await test_client.post(
            f"/engagements/{engagement_id}/transition",
            params={"new_status": "fieldwork"},
            headers={"X-User-ID": str(user_id)}
        )

        assert fieldwork_response.status_code == 200

        # Step 4: Transition to REVIEW
        review_response = await test_client.post(
            f"/engagements/{engagement_id}/transition",
            params={"new_status": "review"},
            headers={"X-User-ID": str(user_id)}
        )

        assert review_response.status_code == 200

        # Step 5: Attempt to finalize (should fail - QC not passed)
        finalize_response = await test_client.post(
            f"/engagements/{engagement_id}/transition",
            params={"new_status": "finalized"},
            headers={"X-User-ID": str(user_id)}
        )

        # Should fail due to QC checks or signature missing
        assert finalize_response.status_code == 400
        assert "Cannot finalize" in finalize_response.json()["detail"]

    @pytest.mark.asyncio
    async def test_invalid_state_transition(self, test_client, test_data):
        """Test that invalid state transitions are rejected"""
        user_id = test_data["user_id"]
        client_id = test_data["client_id"]

        # Create engagement in DRAFT
        create_response = await test_client.post(
            "/engagements",
            json={
                "client_id": str(client_id),
                "name": "Test Engagement",
                "engagement_type": "audit",
                "fiscal_year_end": "2024-12-31",
            },
            headers={"X-User-ID": str(user_id)}
        )

        engagement_id = create_response.json()["id"]

        # Try to go directly from DRAFT to REVIEW (invalid)
        invalid_response = await test_client.post(
            f"/engagements/{engagement_id}/transition",
            params={"new_status": "review"},
            headers={"X-User-ID": str(user_id)}
        )

        assert invalid_response.status_code == 400
        assert "Invalid transition" in invalid_response.json()["detail"]

    @pytest.mark.asyncio
    async def test_backward_transitions(self, test_client, test_data):
        """Test backward state transitions (e.g., Review back to Fieldwork)"""
        user_id = test_data["user_id"]
        client_id = test_data["client_id"]

        # Create and advance to REVIEW
        create_response = await test_client.post(
            "/engagements",
            json={
                "client_id": str(client_id),
                "name": "Test Engagement",
                "engagement_type": "audit",
                "fiscal_year_end": "2024-12-31",
            },
            headers={"X-User-ID": str(user_id)}
        )

        engagement_id = create_response.json()["id"]

        # Advance through states
        await test_client.post(
            f"/engagements/{engagement_id}/transition",
            params={"new_status": "planning"},
            headers={"X-User-ID": str(user_id)}
        )

        await test_client.post(
            f"/engagements/{engagement_id}/transition",
            params={"new_status": "fieldwork"},
            headers={"X-User-ID": str(user_id)}
        )

        await test_client.post(
            f"/engagements/{engagement_id}/transition",
            params={"new_status": "review"},
            headers={"X-User-ID": str(user_id)}
        )

        # Go back from REVIEW to FIELDWORK (valid)
        backward_response = await test_client.post(
            f"/engagements/{engagement_id}/transition",
            params={"new_status": "fieldwork"},
            headers={"X-User-ID": str(user_id)}
        )

        assert backward_response.status_code == 200


class TestQCGates:
    """Test QC gates block finalization when policies fail"""

    @pytest.mark.asyncio
    async def test_finalization_blocked_by_failed_qc_policy(self, test_client, test_data, test_db):
        """Test that finalization is blocked when blocking QC policies fail"""
        user_id = test_data["user_id"]
        client_id = test_data["client_id"]

        # Create engagement and advance to REVIEW
        create_response = await test_client.post(
            "/engagements",
            json={
                "client_id": str(client_id),
                "name": "Test Engagement",
                "engagement_type": "audit",
                "fiscal_year_end": "2024-12-31",
            },
            headers={"X-User-ID": str(user_id)}
        )

        engagement_id = UUID(create_response.json()["id"])

        # Advance to REVIEW
        for status in ["planning", "fieldwork", "review"]:
            await test_client.post(
                f"/engagements/{engagement_id}/transition",
                params={"new_status": status},
                headers={"X-User-ID": str(user_id)}
            )

        # Create a blocking QC policy
        policy_id = uuid4()
        await test_db.execute(
            text("""
                INSERT INTO atlas.qc_policies (
                    id, policy_code, policy_name, description,
                    is_blocking, check_logic, is_active
                )
                VALUES (
                    :policy_id, 'TEST_001', 'Test QC Policy',
                    'Test blocking policy', TRUE, '{}', TRUE
                )
            """),
            {"policy_id": policy_id}
        )

        # Create a failed QC check for this engagement
        await test_db.execute(
            text("""
                INSERT INTO atlas.qc_checks (
                    id, engagement_id, policy_id, status, executed_at
                )
                VALUES (
                    :check_id, :engagement_id, :policy_id, 'failed', NOW()
                )
            """),
            {
                "check_id": uuid4(),
                "engagement_id": engagement_id,
                "policy_id": policy_id,
            }
        )

        await test_db.commit()

        # Attempt to finalize (should fail due to failed QC check)
        finalize_response = await test_client.post(
            f"/engagements/{engagement_id}/transition",
            params={"new_status": "finalized"},
            headers={"X-User-ID": str(user_id)}
        )

        assert finalize_response.status_code == 400
        assert "blocking QC policies not passed" in finalize_response.json()["detail"]
        assert "Test QC Policy" in finalize_response.json()["detail"]

    @pytest.mark.asyncio
    async def test_finalization_allowed_with_passed_qc_policies(self, test_client, test_data, test_db):
        """Test that finalization proceeds when all blocking QC policies pass"""
        user_id = test_data["user_id"]
        client_id = test_data["client_id"]
        partner_id = test_data["partner_id"]

        # Create engagement and advance to REVIEW
        create_response = await test_client.post(
            "/engagements",
            json={
                "client_id": str(client_id),
                "name": "Test Engagement",
                "engagement_type": "audit",
                "fiscal_year_end": "2024-12-31",
            },
            headers={"X-User-ID": str(user_id)}
        )

        engagement_id = UUID(create_response.json()["id"])

        # Advance to REVIEW
        for status in ["planning", "fieldwork", "review"]:
            await test_client.post(
                f"/engagements/{engagement_id}/transition",
                params={"new_status": status},
                headers={"X-User-ID": str(user_id)}
            )

        # Create a blocking QC policy
        policy_id = uuid4()
        await test_db.execute(
            text("""
                INSERT INTO atlas.qc_policies (
                    id, policy_code, policy_name, description,
                    is_blocking, check_logic, is_active
                )
                VALUES (
                    :policy_id, 'TEST_001', 'Test QC Policy',
                    'Test blocking policy', TRUE, '{}', TRUE
                )
            """),
            {"policy_id": policy_id}
        )

        # Create a PASSED QC check
        await test_db.execute(
            text("""
                INSERT INTO atlas.qc_checks (
                    id, engagement_id, policy_id, status, executed_at
                )
                VALUES (
                    :check_id, :engagement_id, :policy_id, 'passed', NOW()
                )
            """),
            {
                "check_id": uuid4(),
                "engagement_id": engagement_id,
                "policy_id": policy_id,
            }
        )

        # Create report and signature envelope
        report_id = uuid4()
        await test_db.execute(
            text("""
                INSERT INTO atlas.reports (
                    id, engagement_id, report_type, title,
                    report_data, status, created_by
                )
                VALUES (
                    :report_id, :engagement_id, 'audit_opinion',
                    'Audit Opinion', '{}', 'finalized', :user_id
                )
            """),
            {
                "report_id": report_id,
                "engagement_id": engagement_id,
                "user_id": user_id,
            }
        )

        # Create completed signature envelope
        await test_db.execute(
            text("""
                INSERT INTO atlas.signature_envelopes (
                    id, report_id, subject, status, signers
                )
                VALUES (
                    :envelope_id, :report_id, 'Partner Signature',
                    'completed', '[]'
                )
            """),
            {
                "envelope_id": uuid4(),
                "report_id": report_id,
            }
        )

        await test_db.commit()

        # Attempt to finalize (should succeed)
        finalize_response = await test_client.post(
            f"/engagements/{engagement_id}/transition",
            params={"new_status": "finalized"},
            headers={"X-User-ID": str(user_id)}
        )

        assert finalize_response.status_code == 200

        # Verify engagement is finalized and locked
        get_response = await test_client.get(
            f"/engagements/{engagement_id}",
            headers={"X-User-ID": str(user_id)}
        )

        engagement = get_response.json()
        assert engagement["status"] == "finalized"
        assert engagement["locked_at"] is not None
        assert engagement["locked_by"] == str(user_id)


class TestPartnerSignatureGate:
    """Test partner signature requirement blocks finalization"""

    @pytest.mark.asyncio
    async def test_finalization_blocked_without_partner_signature(self, test_client, test_data, test_db):
        """Test that finalization is blocked without completed partner signature"""
        user_id = test_data["user_id"]
        client_id = test_data["client_id"]

        # Create engagement and advance to REVIEW
        create_response = await test_client.post(
            "/engagements",
            json={
                "client_id": str(client_id),
                "name": "Test Engagement",
                "engagement_type": "audit",
                "fiscal_year_end": "2024-12-31",
            },
            headers={"X-User-ID": str(user_id)}
        )

        engagement_id = UUID(create_response.json()["id"])

        # Advance to REVIEW
        for status in ["planning", "fieldwork", "review"]:
            await test_client.post(
                f"/engagements/{engagement_id}/transition",
                params={"new_status": status},
                headers={"X-User-ID": str(user_id)}
            )

        # Create passed QC check (so only signature is missing)
        policy_id = uuid4()
        await test_db.execute(
            text("""
                INSERT INTO atlas.qc_policies (
                    id, policy_code, policy_name, is_blocking, check_logic, is_active
                )
                VALUES (:policy_id, 'TEST_001', 'Test Policy', TRUE, '{}', TRUE)
            """),
            {"policy_id": policy_id}
        )

        await test_db.execute(
            text("""
                INSERT INTO atlas.qc_checks (
                    id, engagement_id, policy_id, status, executed_at
                )
                VALUES (:check_id, :engagement_id, :policy_id, 'passed', NOW())
            """),
            {
                "check_id": uuid4(),
                "engagement_id": engagement_id,
                "policy_id": policy_id,
            }
        )

        await test_db.commit()

        # Attempt to finalize (should fail - no signature)
        finalize_response = await test_client.post(
            f"/engagements/{engagement_id}/transition",
            params={"new_status": "finalized"},
            headers={"X-User-ID": str(user_id)}
        )

        assert finalize_response.status_code == 400
        assert "partner signature not completed" in finalize_response.json()["detail"]

    @pytest.mark.asyncio
    async def test_finalization_blocked_with_pending_signature(self, test_client, test_data, test_db):
        """Test that finalization is blocked when signature is pending (not completed)"""
        user_id = test_data["user_id"]
        client_id = test_data["client_id"]

        # Create engagement and advance to REVIEW
        create_response = await test_client.post(
            "/engagements",
            json={
                "client_id": str(client_id),
                "name": "Test Engagement",
                "engagement_type": "audit",
                "fiscal_year_end": "2024-12-31",
            },
            headers={"X-User-ID": str(user_id)}
        )

        engagement_id = UUID(create_response.json()["id"])

        # Advance to REVIEW
        for status in ["planning", "fieldwork", "review"]:
            await test_client.post(
                f"/engagements/{engagement_id}/transition",
                params={"new_status": status},
                headers={"X-User-ID": str(user_id)}
            )

        # Create passed QC check
        policy_id = uuid4()
        await test_db.execute(
            text("""
                INSERT INTO atlas.qc_policies (
                    id, policy_code, policy_name, is_blocking, check_logic, is_active
                )
                VALUES (:policy_id, 'TEST_001', 'Test Policy', TRUE, '{}', TRUE)
            """),
            {"policy_id": policy_id}
        )

        await test_db.execute(
            text("""
                INSERT INTO atlas.qc_checks (
                    id, engagement_id, policy_id, status, executed_at
                )
                VALUES (:check_id, :engagement_id, :policy_id, 'passed', NOW())
            """),
            {
                "check_id": uuid4(),
                "engagement_id": engagement_id,
                "policy_id": policy_id,
            }
        )

        # Create report with PENDING signature (not completed)
        report_id = uuid4()
        await test_db.execute(
            text("""
                INSERT INTO atlas.reports (
                    id, engagement_id, report_type, title, report_data, status, created_by
                )
                VALUES (
                    :report_id, :engagement_id, 'audit_opinion',
                    'Audit Opinion', '{}', 'draft', :user_id
                )
            """),
            {
                "report_id": report_id,
                "engagement_id": engagement_id,
                "user_id": user_id,
            }
        )

        await test_db.execute(
            text("""
                INSERT INTO atlas.signature_envelopes (
                    id, report_id, subject, status, signers
                )
                VALUES (
                    :envelope_id, :report_id, 'Partner Signature', 'pending', '[]'
                )
            """),
            {
                "envelope_id": uuid4(),
                "report_id": report_id,
            }
        )

        await test_db.commit()

        # Attempt to finalize (should fail - signature pending, not completed)
        finalize_response = await test_client.post(
            f"/engagements/{engagement_id}/transition",
            params={"new_status": "finalized"},
            headers={"X-User-ID": str(user_id)}
        )

        assert finalize_response.status_code == 400
        assert "partner signature not completed" in finalize_response.json()["detail"]


class TestEngagementLocking:
    """Test engagement locking on finalization"""

    @pytest.mark.asyncio
    async def test_engagement_locked_on_finalization(self, test_client, test_data, test_db):
        """Test that engagement is locked when finalized"""
        user_id = test_data["user_id"]
        client_id = test_data["client_id"]

        # Create engagement and advance to REVIEW
        create_response = await test_client.post(
            "/engagements",
            json={
                "client_id": str(client_id),
                "name": "Test Engagement",
                "engagement_type": "audit",
                "fiscal_year_end": "2024-12-31",
            },
            headers={"X-User-ID": str(user_id)}
        )

        engagement_id = UUID(create_response.json()["id"])

        # Advance to REVIEW
        for status in ["planning", "fieldwork", "review"]:
            await test_client.post(
                f"/engagements/{engagement_id}/transition",
                params={"new_status": status},
                headers={"X-User-ID": str(user_id)}
            )

        # Setup QC and signature for finalization
        policy_id = uuid4()
        await test_db.execute(
            text("""
                INSERT INTO atlas.qc_policies (
                    id, policy_code, policy_name, is_blocking, check_logic, is_active
                )
                VALUES (:policy_id, 'TEST_001', 'Test Policy', TRUE, '{}', TRUE)
            """),
            {"policy_id": policy_id}
        )

        await test_db.execute(
            text("""
                INSERT INTO atlas.qc_checks (
                    id, engagement_id, policy_id, status, executed_at
                )
                VALUES (:check_id, :engagement_id, :policy_id, 'passed', NOW())
            """),
            {
                "check_id": uuid4(),
                "engagement_id": engagement_id,
                "policy_id": policy_id,
            }
        )

        report_id = uuid4()
        await test_db.execute(
            text("""
                INSERT INTO atlas.reports (
                    id, engagement_id, report_type, title, report_data, status, created_by
                )
                VALUES (
                    :report_id, :engagement_id, 'audit_opinion',
                    'Audit Opinion', '{}', 'finalized', :user_id
                )
            """),
            {
                "report_id": report_id,
                "engagement_id": engagement_id,
                "user_id": user_id,
            }
        )

        await test_db.execute(
            text("""
                INSERT INTO atlas.signature_envelopes (
                    id, report_id, subject, status, signers
                )
                VALUES (:envelope_id, :report_id, 'Partner Signature', 'completed', '[]')
            """),
            {
                "envelope_id": uuid4(),
                "report_id": report_id,
            }
        )

        await test_db.commit()

        # Finalize
        finalize_response = await test_client.post(
            f"/engagements/{engagement_id}/transition",
            params={"new_status": "finalized"},
            headers={"X-User-ID": str(user_id)}
        )

        assert finalize_response.status_code == 200

        # Verify engagement is locked
        get_response = await test_client.get(
            f"/engagements/{engagement_id}",
            headers={"X-User-ID": str(user_id)}
        )

        engagement = get_response.json()
        assert engagement["locked_at"] is not None, "locked_at should be set when finalized"
        assert engagement["locked_by"] == str(user_id), "locked_by should be set to user who finalized"

    @pytest.mark.asyncio
    async def test_finalized_engagement_cannot_transition(self, test_client, test_data, test_db):
        """Test that finalized engagement cannot transition to other states"""
        user_id = test_data["user_id"]
        client_id = test_data["client_id"]

        # Create and finalize engagement (with all gates passed)
        create_response = await test_client.post(
            "/engagements",
            json={
                "client_id": str(client_id),
                "name": "Test Engagement",
                "engagement_type": "audit",
                "fiscal_year_end": "2024-12-31",
            },
            headers={"X-User-ID": str(user_id)}
        )

        engagement_id = UUID(create_response.json()["id"])

        # Advance to REVIEW
        for status in ["planning", "fieldwork", "review"]:
            await test_client.post(
                f"/engagements/{engagement_id}/transition",
                params={"new_status": status},
                headers={"X-User-ID": str(user_id)}
            )

        # Setup QC and signature for finalization
        policy_id = uuid4()
        await test_db.execute(
            text("""
                INSERT INTO atlas.qc_policies (
                    id, policy_code, policy_name, is_blocking, check_logic, is_active
                )
                VALUES (:policy_id, 'TEST_001', 'Test Policy', TRUE, '{}', TRUE)
            """),
            {"policy_id": policy_id}
        )

        await test_db.execute(
            text("""
                INSERT INTO atlas.qc_checks (
                    id, engagement_id, policy_id, status, executed_at
                )
                VALUES (:check_id, :engagement_id, :policy_id, 'passed', NOW())
            """),
            {
                "check_id": uuid4(),
                "engagement_id": engagement_id,
                "policy_id": policy_id,
            }
        )

        report_id = uuid4()
        await test_db.execute(
            text("""
                INSERT INTO atlas.reports (
                    id, engagement_id, report_type, title, report_data, status, created_by
                )
                VALUES (
                    :report_id, :engagement_id, 'audit_opinion',
                    'Audit Opinion', '{}', 'finalized', :user_id
                )
            """),
            {
                "report_id": report_id,
                "engagement_id": engagement_id,
                "user_id": user_id,
            }
        )

        await test_db.execute(
            text("""
                INSERT INTO atlas.signature_envelopes (
                    id, report_id, subject, status, signers
                )
                VALUES (:envelope_id, :report_id, 'Partner Signature', 'completed', '[]')
            """),
            {
                "envelope_id": uuid4(),
                "report_id": report_id,
            }
        )

        await test_db.commit()

        # Finalize
        finalize_response = await test_client.post(
            f"/engagements/{engagement_id}/transition",
            params={"new_status": "finalized"},
            headers={"X-User-ID": str(user_id)}
        )

        assert finalize_response.status_code == 200

        # Try to transition back (should fail - terminal state)
        back_response = await test_client.post(
            f"/engagements/{engagement_id}/transition",
            params={"new_status": "review"},
            headers={"X-User-ID": str(user_id)}
        )

        assert back_response.status_code == 400
        assert "Invalid transition" in back_response.json()["detail"]
