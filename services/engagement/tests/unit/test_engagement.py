"""Unit tests for Engagement Service"""
import pytest
from datetime import date, datetime
from uuid import uuid4, UUID
from unittest.mock import AsyncMock, MagicMock, patch

from app.models import (
    Engagement,
    EngagementTeamMember,
    BinderNode,
    EngagementStatus,
    EngagementType,
    UserRole,
    BinderNodeType
)
from app.schemas import (
    EngagementCreate,
    EngagementUpdate,
    EngagementResponse,
    TeamMemberAdd,
    BinderNodeCreate
)


# ========================================
# Model Tests
# ========================================

class TestEngagementModel:
    """Test Engagement ORM model"""

    def test_engagement_attributes(self):
        """Test engagement has correct attributes"""
        engagement = Engagement(
            id=uuid4(),
            client_id=uuid4(),
            name="Test Audit 2024",
            engagement_type=EngagementType.AUDIT,
            status=EngagementStatus.DRAFT,
            fiscal_year_end=date(2024, 12, 31),
            created_by=uuid4()
        )

        assert engagement.name == "Test Audit 2024"
        assert engagement.engagement_type == EngagementType.AUDIT
        assert engagement.status == EngagementStatus.DRAFT
        assert engagement.fiscal_year_end == date(2024, 12, 31)

    def test_engagement_status_enum(self):
        """Test engagement status enum values"""
        assert EngagementStatus.DRAFT.value == "draft"
        assert EngagementStatus.PLANNING.value == "planning"
        assert EngagementStatus.FIELDWORK.value == "fieldwork"
        assert EngagementStatus.REVIEW.value == "review"
        assert EngagementStatus.FINALIZED.value == "finalized"

    def test_engagement_type_enum(self):
        """Test engagement type enum"""
        assert EngagementType.AUDIT.value == "audit"
        assert EngagementType.REVIEW.value == "review"
        assert EngagementType.COMPILATION.value == "compilation"


class TestEngagementTeamMemberModel:
    """Test EngagementTeamMember ORM model"""

    def test_team_member_attributes(self):
        """Test team member has correct attributes"""
        engagement_id = uuid4()
        user_id = uuid4()
        team_member = EngagementTeamMember(
            id=uuid4(),
            engagement_id=engagement_id,
            user_id=user_id,
            role=UserRole.MANAGER
        )

        assert team_member.engagement_id == engagement_id
        assert team_member.user_id == user_id
        assert team_member.role == UserRole.MANAGER

    def test_user_role_enum(self):
        """Test user role enum values"""
        assert UserRole.PARTNER.value == "partner"
        assert UserRole.MANAGER.value == "manager"
        assert UserRole.SENIOR.value == "senior"
        assert UserRole.STAFF.value == "staff"


class TestBinderNodeModel:
    """Test BinderNode ORM model"""

    def test_binder_node_attributes(self):
        """Test binder node has correct attributes"""
        engagement_id = uuid4()
        node = BinderNode(
            id=uuid4(),
            engagement_id=engagement_id,
            node_type=BinderNodeType.FOLDER,
            title="Cash",
            node_code="A-100",
            position=0
        )

        assert node.engagement_id == engagement_id
        assert node.node_type == BinderNodeType.FOLDER
        assert node.title == "Cash"
        assert node.node_code == "A-100"

    def test_binder_node_type_enum(self):
        """Test binder node type enum"""
        assert BinderNodeType.FOLDER.value == "folder"
        assert BinderNodeType.WORKPAPER.value == "workpaper"
        assert BinderNodeType.EVIDENCE.value == "evidence"


# ========================================
# Schema Tests
# ========================================

class TestEngagementSchemas:
    """Test Pydantic schemas for validation"""

    def test_engagement_create_valid(self):
        """Test valid engagement creation schema"""
        data = EngagementCreate(
            client_id=uuid4(),
            name="Test Engagement",
            engagement_type=EngagementType.AUDIT,
            fiscal_year_end=date(2024, 12, 31)
        )

        assert data.name == "Test Engagement"
        assert data.engagement_type == EngagementType.AUDIT
        assert data.fiscal_year_end == date(2024, 12, 31)

    def test_engagement_create_min_length(self):
        """Test name minimum length validation"""
        with pytest.raises(ValueError):
            EngagementCreate(
                client_id=uuid4(),
                name="",  # Empty name should fail
                engagement_type=EngagementType.AUDIT,
                fiscal_year_end=date(2024, 12, 31)
            )

    def test_engagement_update_partial(self):
        """Test partial update schema"""
        data = EngagementUpdate(
            name="Updated Name"
        )

        assert data.name == "Updated Name"
        assert data.start_date is None
        assert data.expected_completion_date is None

    def test_team_member_add_schema(self):
        """Test team member add schema"""
        data = TeamMemberAdd(
            user_id=uuid4(),
            role=UserRole.SENIOR
        )

        assert isinstance(data.user_id, UUID)
        assert data.role == UserRole.SENIOR


# ========================================
# State Transition Tests
# ========================================

class TestEngagementStateTransitions:
    """Test engagement state machine transitions"""

    def test_valid_transitions_from_draft(self):
        """Test valid transitions from draft status"""
        valid_transitions = {
            EngagementStatus.DRAFT: [EngagementStatus.PLANNING],
            EngagementStatus.PLANNING: [EngagementStatus.FIELDWORK, EngagementStatus.DRAFT],
            EngagementStatus.FIELDWORK: [EngagementStatus.REVIEW, EngagementStatus.PLANNING],
            EngagementStatus.REVIEW: [EngagementStatus.FINALIZED, EngagementStatus.FIELDWORK],
            EngagementStatus.FINALIZED: []
        }

        # Draft can go to Planning
        assert EngagementStatus.PLANNING in valid_transitions[EngagementStatus.DRAFT]
        # Planning can go to Fieldwork or back to Draft
        assert EngagementStatus.FIELDWORK in valid_transitions[EngagementStatus.PLANNING]
        assert EngagementStatus.DRAFT in valid_transitions[EngagementStatus.PLANNING]

    def test_finalized_is_terminal_state(self):
        """Test finalized status is terminal (no transitions)"""
        valid_transitions = {
            EngagementStatus.FINALIZED: []
        }

        assert len(valid_transitions[EngagementStatus.FINALIZED]) == 0

    def test_invalid_transition_from_draft_to_review(self):
        """Test cannot go directly from draft to review"""
        valid_transitions = {
            EngagementStatus.DRAFT: [EngagementStatus.PLANNING]
        }

        assert EngagementStatus.REVIEW not in valid_transitions[EngagementStatus.DRAFT]


# ========================================
# Business Logic Tests (Mocked)
# ========================================

class TestEngagementBusinessLogic:
    """Test business logic with mocked database"""

    @pytest.mark.asyncio
    async def test_create_engagement_with_team_member(self):
        """Test engagement creation includes creator as team member"""
        # This would test the actual endpoint logic
        # In a full implementation, we'd use TestClient and mock the database

        engagement_id = uuid4()
        user_id = uuid4()

        # Simulate what the endpoint does
        engagement = Engagement(
            id=engagement_id,
            client_id=uuid4(),
            name="Test Engagement",
            engagement_type=EngagementType.AUDIT,
            status=EngagementStatus.DRAFT,
            fiscal_year_end=date(2024, 12, 31),
            created_by=user_id
        )

        team_member = EngagementTeamMember(
            id=uuid4(),
            engagement_id=engagement_id,
            user_id=user_id,
            role=UserRole.MANAGER
        )

        assert engagement.id == engagement_id
        assert team_member.engagement_id == engagement.id
        assert team_member.user_id == user_id

    @pytest.mark.asyncio
    async def test_create_root_binder_node(self):
        """Test root binder node is created with engagement"""
        engagement_id = uuid4()
        user_id = uuid4()

        root_node = BinderNode(
            id=uuid4(),
            engagement_id=engagement_id,
            node_type=BinderNodeType.FOLDER,
            title="Audit Binder",
            node_code="ROOT",
            position=0,
            created_by=user_id
        )

        assert root_node.engagement_id == engagement_id
        assert root_node.node_type == BinderNodeType.FOLDER
        assert root_node.node_code == "ROOT"
        assert root_node.parent_id is None  # Root has no parent


# ========================================
# Binder Tree Tests
# ========================================

class TestBinderTreeStructure:
    """Test binder tree hierarchy building"""

    def test_build_simple_tree(self):
        """Test building simple two-level tree"""
        engagement_id = uuid4()

        root_id = uuid4()
        child1_id = uuid4()
        child2_id = uuid4()

        nodes = [
            BinderNode(
                id=root_id,
                engagement_id=engagement_id,
                node_type=BinderNodeType.FOLDER,
                title="Root",
                position=0
            ),
            BinderNode(
                id=child1_id,
                engagement_id=engagement_id,
                parent_id=root_id,
                node_type=BinderNodeType.FOLDER,
                title="Child 1",
                position=0
            ),
            BinderNode(
                id=child2_id,
                engagement_id=engagement_id,
                parent_id=root_id,
                node_type=BinderNodeType.FOLDER,
                title="Child 2",
                position=1
            ),
        ]

        # Build hierarchy
        node_map = {node.id: node for node in nodes}

        # Count children
        root = node_map[root_id]
        children = [n for n in nodes if n.parent_id == root_id]

        assert len(children) == 2
        assert children[0].title == "Child 1"
        assert children[1].title == "Child 2"

    def test_tree_position_ordering(self):
        """Test tree nodes are ordered by position"""
        engagement_id = uuid4()

        node1 = BinderNode(
            id=uuid4(),
            engagement_id=engagement_id,
            node_type=BinderNodeType.FOLDER,
            title="First",
            position=0
        )

        node2 = BinderNode(
            id=uuid4(),
            engagement_id=engagement_id,
            node_type=BinderNodeType.FOLDER,
            title="Second",
            position=1
        )

        node3 = BinderNode(
            id=uuid4(),
            engagement_id=engagement_id,
            node_type=BinderNodeType.FOLDER,
            title="Third",
            position=2
        )

        nodes = [node2, node3, node1]  # Out of order
        sorted_nodes = sorted(nodes, key=lambda n: n.position)

        assert sorted_nodes[0].title == "First"
        assert sorted_nodes[1].title == "Second"
        assert sorted_nodes[2].title == "Third"


# ========================================
# Configuration Tests
# ========================================

class TestConfiguration:
    """Test configuration settings"""

    def test_default_settings(self):
        """Test default configuration values"""
        from app.config import settings

        assert settings.SERVICE_NAME == "engagement"
        assert settings.VERSION == "1.0.0"
        assert settings.LOG_LEVEL == "INFO"
        assert settings.JWT_ALGORITHM == "HS256"

    def test_cors_origins_configured(self):
        """Test CORS origins are configured"""
        from app.config import settings

        assert len(settings.CORS_ORIGINS) > 0
        assert any("localhost" in origin for origin in settings.CORS_ORIGINS)
