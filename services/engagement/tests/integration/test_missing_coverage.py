"""
Integration Tests for Missing Engagement Workflow Coverage

Tests for:
- Dashboard metrics (completion %, blockers)
- Binder generation (structure, templates)
- Confirmation tracking workflow
- Risk assessment phase
- Analytical procedures phase
"""

import pytest
from datetime import date, datetime, timedelta
from uuid import uuid4, UUID
from decimal import Decimal
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

from app.main import app
from app.database import get_db, Base
from app.models import EngagementStatus, EngagementType
from app.binder_generation_service import BinderNode
from app.confirmation_service import (
    Confirmation,
    ConfirmationType,
    ConfirmationStatus,
    ConfirmationResponseType
)


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
async def test_engagement(test_db):
    """Create test engagement with user and client"""
    user_id = uuid4()
    client_id = uuid4()
    engagement_id = uuid4()

    # Create test user
    await test_db.execute(
        text("""
            INSERT INTO atlas.users (id, email, first_name, last_name, role)
            VALUES (:user_id, 'test@example.com', 'Test', 'User', 'manager')
        """),
        {"user_id": user_id}
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

    # Create test engagement
    await test_db.execute(
        text("""
            INSERT INTO atlas.engagements (
                id, client_id, name, engagement_type, status, current_phase,
                fiscal_year_end, created_by, created_at
            )
            VALUES (
                :engagement_id, :client_id, 'Test Audit 2024', 'audit',
                'planning', 'planning', '2024-12-31', :user_id, NOW()
            )
        """),
        {
            "engagement_id": engagement_id,
            "client_id": client_id,
            "user_id": user_id,
        }
    )

    await test_db.commit()

    return {
        "user_id": user_id,
        "client_id": client_id,
        "engagement_id": engagement_id,
    }


# ========================================
# Binder Generation Tests
# ========================================

class TestBinderGeneration:
    """Test binder generation service"""

    @pytest.mark.asyncio
    async def test_generate_standard_audit_binder_structure(self, test_db, test_engagement):
        """Test generating standard audit binder creates correct structure"""
        from app.binder_generation_service import BinderGenerationService

        engagement_id = test_engagement["engagement_id"]
        user_id = test_engagement["user_id"]

        # Create service
        binder_service = BinderGenerationService(test_db)

        # Generate binder
        result = await binder_service.generate_standard_binder(
            engagement_id=engagement_id,
            engagement_type='audit',
            user_id=user_id
        )

        # Verify counts
        assert result['sections'] > 0, "Should create at least one section"
        assert result['workpapers'] > 0, "Should create at least one workpaper"
        assert result['total_nodes'] == result['sections'] + result['workpapers']

        # Verify nodes in database
        query = text("""
            SELECT COUNT(*) FROM atlas.binder_nodes
            WHERE engagement_id = :engagement_id
        """)
        result_count = await test_db.execute(query, {"engagement_id": engagement_id})
        count = result_count.scalar()

        assert count > 0, "Binder nodes should be created in database"
        assert count == result['total_nodes'], "Database count should match return value"

    @pytest.mark.asyncio
    async def test_binder_has_required_sections(self, test_db, test_engagement):
        """Test binder includes all required audit sections (A-J)"""
        from app.binder_generation_service import BinderGenerationService

        engagement_id = test_engagement["engagement_id"]

        # Generate binder
        binder_service = BinderGenerationService(test_db)
        await binder_service.generate_standard_binder(
            engagement_id=engagement_id,
            engagement_type='audit'
        )

        # Required audit sections
        required_sections = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']

        # Query for sections
        query = text("""
            SELECT section_code FROM atlas.binder_nodes
            WHERE engagement_id = :engagement_id
            AND node_type = 'section'
            ORDER BY position_order
        """)
        result = await test_db.execute(query, {"engagement_id": engagement_id})
        sections = [row[0] for row in result.fetchall()]

        # Verify all required sections exist
        for required_section in required_sections:
            assert required_section in sections, f"Section {required_section} should exist in binder"

    @pytest.mark.asyncio
    async def test_binder_workpapers_have_required_fields(self, test_db, test_engagement):
        """Test workpapers have all required fields populated"""
        from app.binder_generation_service import BinderGenerationService

        engagement_id = test_engagement["engagement_id"]

        # Generate binder
        binder_service = BinderGenerationService(test_db)
        await binder_service.generate_standard_binder(
            engagement_id=engagement_id,
            engagement_type='audit'
        )

        # Query for workpapers
        query = text("""
            SELECT id, section_code, title, status, is_required, is_applicable, position_order
            FROM atlas.binder_nodes
            WHERE engagement_id = :engagement_id
            AND node_type = 'workpaper'
            LIMIT 5
        """)
        result = await test_db.execute(query, {"engagement_id": engagement_id})
        workpapers = result.fetchall()

        assert len(workpapers) > 0, "Should have at least one workpaper"

        for wp in workpapers:
            assert wp[0] is not None, "Workpaper ID should be set"
            assert wp[1] is not None, "Section code should be set"
            assert wp[2] is not None, "Title should be set"
            assert wp[3] in ['not_started', 'in_progress', 'complete', 'reviewed'], "Status should be valid"
            assert wp[4] is not None, "is_required should be set"
            assert wp[5] is not None, "is_applicable should be set"
            assert wp[6] is not None, "position_order should be set"

    @pytest.mark.asyncio
    async def test_get_binder_summary(self, test_db, test_engagement):
        """Test getting binder summary returns correct metrics"""
        from app.binder_generation_service import BinderGenerationService

        engagement_id = test_engagement["engagement_id"]

        # Generate binder
        binder_service = BinderGenerationService(test_db)
        await binder_service.generate_standard_binder(
            engagement_id=engagement_id,
            engagement_type='audit'
        )

        # Mark some workpapers as complete
        await test_db.execute(
            text("""
                UPDATE atlas.binder_nodes
                SET status = 'complete'
                WHERE engagement_id = :engagement_id
                AND node_type = 'workpaper'
                AND position_order <= 2
            """),
            {"engagement_id": engagement_id}
        )
        await test_db.commit()

        # Get summary
        summary = await binder_service.get_binder_summary(engagement_id)

        # Verify summary structure
        assert 'total_workpapers' in summary
        assert 'completed_workpapers' in summary
        assert 'completion_percentage' in summary
        assert 'sections' in summary

        # Verify counts
        assert summary['total_workpapers'] > 0
        assert summary['completed_workpapers'] >= 2
        assert 0 <= summary['completion_percentage'] <= 100

    @pytest.mark.asyncio
    async def test_get_incomplete_workpapers(self, test_db, test_engagement):
        """Test getting incomplete required workpapers"""
        from app.binder_generation_service import BinderGenerationService

        engagement_id = test_engagement["engagement_id"]

        # Generate binder
        binder_service = BinderGenerationService(test_db)
        await binder_service.generate_standard_binder(
            engagement_id=engagement_id,
            engagement_type='audit'
        )

        # Get incomplete workpapers
        incomplete = await binder_service.get_incomplete_workpapers(engagement_id)

        # All should be incomplete initially
        assert len(incomplete) > 0, "Should have incomplete workpapers"

        # Verify structure
        for wp in incomplete:
            assert 'node_id' in wp
            assert 'title' in wp
            assert 'section_title' in wp
            assert 'is_required' in wp


# ========================================
# Confirmation Tracking Tests
# ========================================

class TestConfirmationTracking:
    """Test confirmation tracking workflow"""

    @pytest.mark.asyncio
    async def test_create_confirmation(self, test_db, test_engagement):
        """Test creating a confirmation"""
        from app.confirmation_service import ConfirmationService

        engagement_id = test_engagement["engagement_id"]
        user_id = test_engagement["user_id"]

        # Create service
        conf_service = ConfirmationService(test_db)

        # Create AR confirmation
        confirmation = await conf_service.create_confirmation(
            engagement_id=engagement_id,
            confirmation_type=ConfirmationType.ACCOUNTS_RECEIVABLE,
            entity_name="ABC Corp",
            entity_email="ap@abccorp.com",
            as_of_date=date(2024, 12, 31),
            amount=Decimal("50000.00"),
            account_number="AR-12345",
            user_id=user_id
        )

        # Verify confirmation created
        assert confirmation.id is not None
        assert confirmation.engagement_id == engagement_id
        assert confirmation.confirmation_type == ConfirmationType.ACCOUNTS_RECEIVABLE
        assert confirmation.entity_name == "ABC Corp"
        assert confirmation.status == ConfirmationStatus.NOT_SENT
        assert confirmation.amount == Decimal("50000.00")

    @pytest.mark.asyncio
    async def test_send_confirmation(self, test_db, test_engagement):
        """Test sending a confirmation"""
        from app.confirmation_service import ConfirmationService

        engagement_id = test_engagement["engagement_id"]
        user_id = test_engagement["user_id"]

        # Create confirmation
        conf_service = ConfirmationService(test_db)
        confirmation = await conf_service.create_confirmation(
            engagement_id=engagement_id,
            confirmation_type=ConfirmationType.BANK,
            entity_name="First National Bank",
            entity_email="confirmations@fnb.com",
            as_of_date=date(2024, 12, 31),
            amount=Decimal("100000.00"),
            user_id=user_id
        )

        # Send confirmation
        await conf_service.send_confirmation(
            confirmation_id=confirmation.id,
            user_id=user_id
        )

        # Verify status updated
        await test_db.refresh(confirmation)
        assert confirmation.status == ConfirmationStatus.SENT
        assert confirmation.sent_date is not None

    @pytest.mark.asyncio
    async def test_record_confirmation_response(self, test_db, test_engagement):
        """Test recording confirmation response"""
        from app.confirmation_service import ConfirmationService

        engagement_id = test_engagement["engagement_id"]
        user_id = test_engagement["user_id"]

        # Create and send confirmation
        conf_service = ConfirmationService(test_db)
        confirmation = await conf_service.create_confirmation(
            engagement_id=engagement_id,
            confirmation_type=ConfirmationType.ACCOUNTS_RECEIVABLE,
            entity_name="XYZ Corp",
            entity_email="ar@xyzcorp.com",
            as_of_date=date(2024, 12, 31),
            amount=Decimal("75000.00"),
            user_id=user_id
        )

        await conf_service.send_confirmation(confirmation.id, user_id)

        # Record response
        await conf_service.record_response(
            confirmation_id=confirmation.id,
            response_type=ConfirmationResponseType.POSITIVE,
            confirmed_amount=Decimal("75000.00"),
            received_date=date(2024, 12, 15),
            user_id=user_id
        )

        # Verify response recorded
        await test_db.refresh(confirmation)
        assert confirmation.status == ConfirmationStatus.RECEIVED
        assert confirmation.response_type == ConfirmationResponseType.POSITIVE
        assert confirmation.confirmed_amount == Decimal("75000.00")
        assert confirmation.has_exception is False

    @pytest.mark.asyncio
    async def test_record_confirmation_exception(self, test_db, test_engagement):
        """Test recording confirmation with exception"""
        from app.confirmation_service import ConfirmationService

        engagement_id = test_engagement["engagement_id"]
        user_id = test_engagement["user_id"]

        # Create confirmation
        conf_service = ConfirmationService(test_db)
        confirmation = await conf_service.create_confirmation(
            engagement_id=engagement_id,
            confirmation_type=ConfirmationType.ACCOUNTS_RECEIVABLE,
            entity_name="Problem Corp",
            entity_email="ar@problemcorp.com",
            as_of_date=date(2024, 12, 31),
            amount=Decimal("100000.00"),
            user_id=user_id
        )

        await conf_service.send_confirmation(confirmation.id, user_id)

        # Record exception
        await conf_service.record_response(
            confirmation_id=confirmation.id,
            response_type=ConfirmationResponseType.POSITIVE,
            confirmed_amount=Decimal("95000.00"),
            received_date=date(2024, 12, 15),
            has_exception=True,
            exception_description="Customer shows $5,000 less due to payment in transit",
            user_id=user_id
        )

        # Verify exception recorded
        await test_db.refresh(confirmation)
        assert confirmation.has_exception is True
        assert confirmation.exception_description is not None
        assert confirmation.exception_resolved is False
        assert confirmation.difference_amount == Decimal("5000.00")

    @pytest.mark.asyncio
    async def test_get_confirmation_summary(self, test_db, test_engagement):
        """Test getting confirmation summary"""
        from app.confirmation_service import ConfirmationService

        engagement_id = test_engagement["engagement_id"]
        user_id = test_engagement["user_id"]

        # Create multiple confirmations
        conf_service = ConfirmationService(test_db)

        # Not sent
        await conf_service.create_confirmation(
            engagement_id=engagement_id,
            confirmation_type=ConfirmationType.ACCOUNTS_RECEIVABLE,
            entity_name="Corp A",
            as_of_date=date(2024, 12, 31),
            amount=Decimal("10000.00"),
            user_id=user_id
        )

        # Sent
        conf2 = await conf_service.create_confirmation(
            engagement_id=engagement_id,
            confirmation_type=ConfirmationType.BANK,
            entity_name="Bank B",
            as_of_date=date(2024, 12, 31),
            amount=Decimal("20000.00"),
            user_id=user_id
        )
        await conf_service.send_confirmation(conf2.id, user_id)

        # Received
        conf3 = await conf_service.create_confirmation(
            engagement_id=engagement_id,
            confirmation_type=ConfirmationType.ACCOUNTS_RECEIVABLE,
            entity_name="Corp C",
            as_of_date=date(2024, 12, 31),
            amount=Decimal("30000.00"),
            user_id=user_id
        )
        await conf_service.send_confirmation(conf3.id, user_id)
        await conf_service.record_response(
            conf3.id,
            ConfirmationResponseType.POSITIVE,
            Decimal("30000.00"),
            date(2024, 12, 15),
            user_id=user_id
        )

        # Get summary
        summary = await conf_service.get_confirmation_summary(engagement_id)

        # Verify summary
        assert summary['total'] == 3
        assert summary['by_status']['not_sent'] == 1
        assert summary['by_status']['sent'] == 1
        assert summary['by_status']['received'] == 1
        assert summary['exception_count'] == 0


# ========================================
# Dashboard Metrics Tests
# ========================================

class TestDashboardMetrics:
    """Test engagement dashboard metrics"""

    @pytest.mark.asyncio
    async def test_get_engagement_dashboard_complete_data(self, test_db, test_engagement):
        """Test getting complete dashboard with all metrics"""
        from app.engagement_workflow_service import EngagementWorkflowService

        engagement_id = test_engagement["engagement_id"]
        user_id = test_engagement["user_id"]

        # Create workflow service
        workflow_service = EngagementWorkflowService(test_db)

        # Get dashboard
        dashboard = await workflow_service.get_engagement_dashboard(engagement_id)

        # Verify dashboard structure
        assert 'engagement' in dashboard
        assert 'binder' in dashboard
        assert 'confirmations' in dashboard
        assert 'overall_completion' in dashboard

        # Verify engagement info
        assert dashboard['engagement']['id'] == str(engagement_id)
        assert dashboard['engagement']['status'] == 'planning'
        assert dashboard['engagement']['current_phase'] == 'planning'

    @pytest.mark.asyncio
    async def test_calculate_overall_completion_percentage(self, test_db, test_engagement):
        """Test overall completion percentage calculation"""
        from app.engagement_workflow_service import EngagementWorkflowService
        from app.binder_generation_service import BinderGenerationService

        engagement_id = test_engagement["engagement_id"]

        # Generate binder
        binder_service = BinderGenerationService(test_db)
        await binder_service.generate_standard_binder(
            engagement_id=engagement_id,
            engagement_type='audit'
        )

        # Mark 50% of workpapers complete
        await test_db.execute(
            text("""
                UPDATE atlas.binder_nodes
                SET status = 'complete'
                WHERE engagement_id = :engagement_id
                AND node_type = 'workpaper'
                AND position_order % 2 = 0
            """),
            {"engagement_id": engagement_id}
        )
        await test_db.commit()

        # Get dashboard
        workflow_service = EngagementWorkflowService(test_db)
        dashboard = await workflow_service.get_engagement_dashboard(engagement_id)

        # Verify completion percentage
        completion = dashboard['overall_completion']
        assert isinstance(completion, (int, float))
        assert 0 <= completion <= 100
        # Should be around 20% (40% of binder * 50% completion)
        assert 15 <= completion <= 30, f"Expected completion around 20%, got {completion}"

    @pytest.mark.asyncio
    async def test_get_engagement_blockers_incomplete_workpapers(self, test_db, test_engagement):
        """Test identifying incomplete required workpapers as blockers"""
        from app.engagement_workflow_service import EngagementWorkflowService
        from app.binder_generation_service import BinderGenerationService

        engagement_id = test_engagement["engagement_id"]

        # Generate binder
        binder_service = BinderGenerationService(test_db)
        await binder_service.generate_standard_binder(
            engagement_id=engagement_id,
            engagement_type='audit'
        )

        # Get blockers
        workflow_service = EngagementWorkflowService(test_db)
        blockers = await workflow_service.get_engagement_blockers(engagement_id)

        # Should have blockers for incomplete workpapers
        workpaper_blockers = [b for b in blockers if b['type'] == 'workpaper']
        assert len(workpaper_blockers) > 0, "Should have workpaper blockers"

        # Verify blocker structure
        for blocker in workpaper_blockers[:3]:
            assert 'type' in blocker
            assert 'severity' in blocker
            assert 'description' in blocker
            assert blocker['severity'] in ['high', 'medium', 'low']

    @pytest.mark.asyncio
    async def test_get_engagement_blockers_unresolved_exceptions(self, test_db, test_engagement):
        """Test identifying unresolved confirmation exceptions as blockers"""
        from app.engagement_workflow_service import EngagementWorkflowService
        from app.confirmation_service import ConfirmationService

        engagement_id = test_engagement["engagement_id"]
        user_id = test_engagement["user_id"]

        # Create confirmation with exception
        conf_service = ConfirmationService(test_db)
        confirmation = await conf_service.create_confirmation(
            engagement_id=engagement_id,
            confirmation_type=ConfirmationType.ACCOUNTS_RECEIVABLE,
            entity_name="Problem Corp",
            as_of_date=date(2024, 12, 31),
            amount=Decimal("100000.00"),
            user_id=user_id
        )

        await conf_service.send_confirmation(confirmation.id, user_id)
        await conf_service.record_response(
            confirmation.id,
            ConfirmationResponseType.POSITIVE,
            Decimal("95000.00"),
            date(2024, 12, 15),
            has_exception=True,
            exception_description="Payment timing difference",
            user_id=user_id
        )

        # Get blockers
        workflow_service = EngagementWorkflowService(test_db)
        blockers = await workflow_service.get_engagement_blockers(engagement_id)

        # Should have exception blocker
        exception_blockers = [b for b in blockers if b['type'] == 'confirmation_exception']
        assert len(exception_blockers) > 0, "Should have confirmation exception blocker"
        assert exception_blockers[0]['severity'] == 'high'


# ========================================
# Phase-Specific Tests
# ========================================

class TestPhaseTransitions:
    """Test phase-specific requirements and transitions"""

    @pytest.mark.asyncio
    async def test_planning_phase_completion_requirements(self, test_db, test_engagement):
        """Test planning phase completion requires Section A workpapers complete"""
        from app.engagement_workflow_service import EngagementWorkflowService
        from app.binder_generation_service import BinderGenerationService

        engagement_id = test_engagement["engagement_id"]

        # Generate binder
        binder_service = BinderGenerationService(test_db)
        await binder_service.generate_standard_binder(
            engagement_id=engagement_id,
            engagement_type='audit'
        )

        # Try to advance from planning without completing Section A
        workflow_service = EngagementWorkflowService(test_db)

        # Should fail to advance
        with pytest.raises(ValueError, match="Current phase.*is not complete"):
            await workflow_service.advance_to_next_phase(engagement_id)

        # Complete Section A workpapers
        await test_db.execute(
            text("""
                UPDATE atlas.binder_nodes
                SET status = 'complete'
                WHERE engagement_id = :engagement_id
                AND section_code = 'A'
                AND node_type = 'workpaper'
            """),
            {"engagement_id": engagement_id}
        )
        await test_db.commit()

        # Should now advance successfully
        updated_engagement = await workflow_service.advance_to_next_phase(engagement_id)
        assert updated_engagement.current_phase == 'risk_assessment'

    @pytest.mark.asyncio
    async def test_confirmations_phase_requires_all_sent(self, test_db, test_engagement):
        """Test confirmations phase requires all confirmations sent"""
        from app.engagement_workflow_service import EngagementWorkflowService
        from app.confirmation_service import ConfirmationService

        engagement_id = test_engagement["engagement_id"]
        user_id = test_engagement["user_id"]

        # Update engagement to confirmations phase
        await test_db.execute(
            text("""
                UPDATE atlas.engagements
                SET current_phase = 'confirmations'
                WHERE id = :engagement_id
            """),
            {"engagement_id": engagement_id}
        )
        await test_db.commit()

        # Create confirmation (not sent)
        conf_service = ConfirmationService(test_db)
        await conf_service.create_confirmation(
            engagement_id=engagement_id,
            confirmation_type=ConfirmationType.BANK,
            entity_name="Test Bank",
            as_of_date=date(2024, 12, 31),
            amount=Decimal("50000.00"),
            user_id=user_id
        )

        # Try to advance
        workflow_service = EngagementWorkflowService(test_db)

        with pytest.raises(ValueError, match="Current phase.*is not complete"):
            await workflow_service.advance_to_next_phase(engagement_id)

    @pytest.mark.asyncio
    async def test_fieldwork_phase_requires_core_sections_complete(self, test_db, test_engagement):
        """Test fieldwork phase requires sections B-G complete"""
        from app.engagement_workflow_service import EngagementWorkflowService
        from app.binder_generation_service import BinderGenerationService

        engagement_id = test_engagement["engagement_id"]

        # Generate binder
        binder_service = BinderGenerationService(test_db)
        await binder_service.generate_standard_binder(
            engagement_id=engagement_id,
            engagement_type='audit'
        )

        # Update to fieldwork phase
        await test_db.execute(
            text("""
                UPDATE atlas.engagements
                SET current_phase = 'fieldwork'
                WHERE id = :engagement_id
            """),
            {"engagement_id": engagement_id}
        )
        await test_db.commit()

        # Complete sections B-F but not G
        for section in ['B', 'C', 'D', 'E', 'F']:
            await test_db.execute(
                text(f"""
                    UPDATE atlas.binder_nodes
                    SET status = 'complete'
                    WHERE engagement_id = :engagement_id
                    AND section_code = '{section}'
                    AND node_type = 'workpaper'
                """),
                {"engagement_id": engagement_id}
            )
        await test_db.commit()

        # Should fail to advance (G not complete)
        workflow_service = EngagementWorkflowService(test_db)

        with pytest.raises(ValueError, match="Current phase.*is not complete"):
            await workflow_service.advance_to_next_phase(engagement_id)

        # Complete section G
        await test_db.execute(
            text("""
                UPDATE atlas.binder_nodes
                SET status = 'complete'
                WHERE engagement_id = :engagement_id
                AND section_code = 'G'
                AND node_type = 'workpaper'
            """),
            {"engagement_id": engagement_id}
        )
        await test_db.commit()

        # Should now advance
        updated = await workflow_service.advance_to_next_phase(engagement_id)
        assert updated.current_phase == 'analytical_procedures'


# ========================================
# Complete Stub Test
# ========================================

class TestEngagementLockingComplete:
    """Complete the stub test for engagement locking"""

    @pytest.mark.asyncio
    async def test_engagement_locked_on_finalization_complete(self, test_db, test_engagement):
        """Test that engagement is locked when finalized (complete implementation)"""
        from app.engagement_workflow_service import EngagementWorkflowService

        engagement_id = test_engagement["engagement_id"]
        user_id = test_engagement["user_id"]

        # Advance to review
        await test_db.execute(
            text("""
                UPDATE atlas.engagements
                SET status = 'review', current_phase = 'review'
                WHERE id = :engagement_id
            """),
            {"engagement_id": engagement_id}
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

        # Create report with completed signature
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

        # Finalize engagement
        workflow_service = EngagementWorkflowService(test_db)
        finalized_engagement = await workflow_service.advance_to_next_phase(engagement_id)

        # Verify locked fields are set
        assert finalized_engagement.status == 'finalized'
        assert finalized_engagement.current_phase == 'finalization' or finalized_engagement.current_phase == 'complete'
        assert finalized_engagement.locked_at is not None, "locked_at should be set"
        assert finalized_engagement.locked_by == user_id, "locked_by should be set to user_id"

        # Verify cannot be modified
        query = text("""
            SELECT locked_at, locked_by FROM atlas.engagements
            WHERE id = :engagement_id
        """)
        result = await test_db.execute(query, {"engagement_id": engagement_id})
        row = result.fetchone()

        assert row[0] is not None, "Database locked_at should be set"
        assert row[1] == user_id, "Database locked_by should be set"
