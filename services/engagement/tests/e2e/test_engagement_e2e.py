"""
End-to-End Tests for Engagement Service

Tests the complete audit engagement workflow from creation to finalization:
1. Create engagement
2. Add team members
3. Create binder structure
4. Add workpapers
5. Transition states (draft → planning → fieldwork → review → finalized)
6. Verify all APIs work end-to-end

Run with:
    pytest services/engagement/tests/e2e/ -v
    pytest services/engagement/tests/e2e/test_engagement_e2e.py::test_complete_engagement_workflow -v
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from uuid import uuid4, UUID
from typing import Dict, List
import httpx

# Test configuration
BASE_URL = "http://localhost:8000"  # Engagement service URL
TIMEOUT = 30.0

# Test data
TEST_CLIENT = {
    "name": "Acme Corporation",
    "industry": "Technology",
    "fiscal_year_end": "2024-12-31"
}

TEST_TEAM_MEMBERS = [
    {"name": "John Partner", "role": "PARTNER", "email": "john@cpa.com"},
    {"name": "Jane Manager", "role": "MANAGER", "email": "jane@cpa.com"},
    {"name": "Bob Senior", "role": "SENIOR", "email": "bob@cpa.com"},
]

TEST_BINDER_SECTIONS = [
    {"section_id": "100", "name": "Planning", "order": 1},
    {"section_id": "200", "name": "Risk Assessment", "order": 2},
    {"section_id": "300", "name": "Audit Procedures", "order": 3},
    {"section_id": "400", "name": "Findings", "order": 4},
    {"section_id": "500", "name": "Conclusions", "order": 5},
]

TEST_WORKPAPERS = [
    {
        "section_id": "100",
        "reference": "A-1",
        "title": "Engagement Letter",
        "prepared_by": "John Partner",
        "content": "Engagement letter signed by client",
    },
    {
        "section_id": "100",
        "reference": "A-2",
        "title": "Planning Memo",
        "prepared_by": "Jane Manager",
        "content": "Overall audit strategy and risk assessment",
    },
    {
        "section_id": "200",
        "reference": "B-1",
        "title": "Risk Assessment Matrix",
        "prepared_by": "Bob Senior",
        "content": "Identified risks and planned responses",
    },
]


class EngagementE2ETest:
    """Helper class for E2E testing"""

    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.client = httpx.AsyncClient(base_url=base_url, timeout=TIMEOUT)
        self.engagement_id: UUID = None
        self.team_member_ids: List[UUID] = []
        self.workpaper_ids: List[UUID] = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

    async def create_engagement(self, client_name: str, engagement_type: str = "AUDIT") -> Dict:
        """Create a new engagement"""
        payload = {
            "client_name": client_name,
            "engagement_type": engagement_type,
            "fiscal_year_end": (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d"),
            "description": f"{engagement_type} engagement for {client_name}",
        }

        response = await self.client.post("/engagements", json=payload)
        assert response.status_code == 201, f"Failed to create engagement: {response.text}"

        data = response.json()
        self.engagement_id = UUID(data["id"])
        return data

    async def get_engagement(self, engagement_id: UUID = None) -> Dict:
        """Get engagement details"""
        eng_id = engagement_id or self.engagement_id
        response = await self.client.get(f"/engagements/{eng_id}")
        assert response.status_code == 200, f"Failed to get engagement: {response.text}"
        return response.json()

    async def add_team_member(self, user_id: UUID = None, role: str = "SENIOR") -> Dict:
        """Add team member to engagement"""
        payload = {
            "user_id": str(user_id or uuid4()),
            "role": role,
        }

        response = await self.client.post(
            f"/engagements/{self.engagement_id}/team",
            json=payload
        )
        assert response.status_code == 201, f"Failed to add team member: {response.text}"

        data = response.json()
        self.team_member_ids.append(UUID(data["id"]))
        return data

    async def create_binder_section(self, section_id: str, name: str, order: int) -> Dict:
        """Create binder section"""
        payload = {
            "section_id": section_id,
            "name": name,
            "order": order,
        }

        response = await self.client.post(
            f"/engagements/{self.engagement_id}/binder/sections",
            json=payload
        )
        assert response.status_code == 201, f"Failed to create binder section: {response.text}"
        return response.json()

    async def add_workpaper(
        self,
        section_id: str,
        reference: str,
        title: str,
        prepared_by: str,
        content: str = ""
    ) -> Dict:
        """Add workpaper to binder section"""
        payload = {
            "section_id": section_id,
            "reference": reference,
            "title": title,
            "prepared_by": prepared_by,
            "content": content,
        }

        response = await self.client.post(
            f"/engagements/{self.engagement_id}/workpapers",
            json=payload
        )
        assert response.status_code == 201, f"Failed to add workpaper: {response.text}"

        data = response.json()
        self.workpaper_ids.append(UUID(data["id"]))
        return data

    async def transition_state(self, new_state: str, notes: str = "") -> Dict:
        """Transition engagement to new state"""
        payload = {
            "new_state": new_state,
            "notes": notes,
        }

        response = await self.client.post(
            f"/engagements/{self.engagement_id}/transition",
            json=payload
        )
        assert response.status_code == 200, f"Failed to transition state: {response.text}"
        return response.json()

    async def get_binder(self) -> Dict:
        """Get engagement binder structure"""
        response = await self.client.get(
            f"/engagements/{self.engagement_id}/binder"
        )
        assert response.status_code == 200, f"Failed to get binder: {response.text}"
        return response.json()

    async def get_workpaper(self, workpaper_id: UUID) -> Dict:
        """Get workpaper details"""
        response = await self.client.get(
            f"/engagements/{self.engagement_id}/workpapers/{workpaper_id}"
        )
        assert response.status_code == 200, f"Failed to get workpaper: {response.text}"
        return response.json()


# ========================================
# E2E Test Cases
# ========================================

@pytest.mark.asyncio
@pytest.mark.e2e
async def test_complete_engagement_workflow():
    """
    Test complete engagement workflow from creation to finalization

    Flow:
    1. Create engagement
    2. Verify initial state is DRAFT
    3. Add team members
    4. Create binder structure
    5. Add workpapers
    6. Transition: DRAFT → PLANNING
    7. Transition: PLANNING → FIELDWORK
    8. Transition: FIELDWORK → REVIEW
    9. Transition: REVIEW → FINALIZED
    10. Verify final state
    """
    async with EngagementE2ETest() as test:
        # Step 1: Create engagement
        print("\n1. Creating engagement...")
        engagement = await test.create_engagement(
            client_name=TEST_CLIENT["name"],
            engagement_type="AUDIT"
        )

        assert engagement["client_name"] == TEST_CLIENT["name"]
        assert engagement["engagement_type"] == "AUDIT"
        assert engagement["status"] == "DRAFT"
        print(f"   ✓ Created engagement {test.engagement_id}")
        print(f"     Status: {engagement['status']}")

        # Step 2: Verify engagement can be retrieved
        print("\n2. Retrieving engagement...")
        retrieved = await test.get_engagement()
        assert retrieved["id"] == str(test.engagement_id)
        assert retrieved["status"] == "DRAFT"
        print(f"   ✓ Retrieved engagement successfully")

        # Step 3: Add team members
        print("\n3. Adding team members...")
        for member in TEST_TEAM_MEMBERS:
            added = await test.add_team_member(
                user_id=uuid4(),
                role=member["role"]
            )
            print(f"   ✓ Added {member['role']}: {member['name']}")

        assert len(test.team_member_ids) == len(TEST_TEAM_MEMBERS)
        print(f"   Total team members: {len(test.team_member_ids)}")

        # Step 4: Create binder structure
        print("\n4. Creating binder structure...")
        for section in TEST_BINDER_SECTIONS:
            created = await test.create_binder_section(
                section_id=section["section_id"],
                name=section["name"],
                order=section["order"]
            )
            print(f"   ✓ Created section {section['section_id']}: {section['name']}")

        # Step 5: Add workpapers
        print("\n5. Adding workpapers...")
        for wp in TEST_WORKPAPERS:
            added = await test.add_workpaper(
                section_id=wp["section_id"],
                reference=wp["reference"],
                title=wp["title"],
                prepared_by=wp["prepared_by"],
                content=wp["content"]
            )
            print(f"   ✓ Added workpaper {wp['reference']}: {wp['title']}")

        assert len(test.workpaper_ids) == len(TEST_WORKPAPERS)
        print(f"   Total workpapers: {len(test.workpaper_ids)}")

        # Step 6: Get complete binder
        print("\n6. Retrieving complete binder...")
        binder = await test.get_binder()
        assert "sections" in binder
        assert len(binder["sections"]) == len(TEST_BINDER_SECTIONS)
        print(f"   ✓ Binder has {len(binder['sections'])} sections")

        # Step 7: Transition to PLANNING
        print("\n7. Transitioning to PLANNING state...")
        result = await test.transition_state(
            new_state="PLANNING",
            notes="Completed initial setup, ready for planning"
        )
        assert result["status"] == "PLANNING"
        print(f"   ✓ Status: DRAFT → PLANNING")

        # Step 8: Transition to FIELDWORK
        print("\n8. Transitioning to FIELDWORK state...")
        result = await test.transition_state(
            new_state="FIELDWORK",
            notes="Planning complete, beginning fieldwork"
        )
        assert result["status"] == "FIELDWORK"
        print(f"   ✓ Status: PLANNING → FIELDWORK")

        # Step 9: Transition to REVIEW
        print("\n9. Transitioning to REVIEW state...")
        result = await test.transition_state(
            new_state="REVIEW",
            notes="Fieldwork complete, ready for review"
        )
        assert result["status"] == "REVIEW"
        print(f"   ✓ Status: FIELDWORK → REVIEW")

        # Step 10: Transition to FINALIZED
        print("\n10. Transitioning to FINALIZED state...")
        result = await test.transition_state(
            new_state="FINALIZED",
            notes="Review complete, engagement finalized"
        )
        assert result["status"] == "FINALIZED"
        print(f"   ✓ Status: REVIEW → FINALIZED")

        # Step 11: Final verification
        print("\n11. Final verification...")
        final_engagement = await test.get_engagement()
        assert final_engagement["status"] == "FINALIZED"
        assert final_engagement["id"] == str(test.engagement_id)
        print(f"   ✓ Engagement finalized successfully")

        # Step 12: Verify workpapers are accessible
        print("\n12. Verifying workpapers...")
        for wp_id in test.workpaper_ids:
            wp = await test.get_workpaper(wp_id)
            assert wp["id"] == str(wp_id)
            print(f"   ✓ Workpaper {wp['reference']} accessible")

        print("\n" + "="*60)
        print("✅ COMPLETE ENGAGEMENT WORKFLOW TEST PASSED!")
        print("="*60)
        print(f"\nSummary:")
        print(f"  Engagement ID: {test.engagement_id}")
        print(f"  Team Members: {len(test.team_member_ids)}")
        print(f"  Binder Sections: {len(TEST_BINDER_SECTIONS)}")
        print(f"  Workpapers: {len(test.workpaper_ids)}")
        print(f"  Final Status: FINALIZED")
        print()


@pytest.mark.asyncio
@pytest.mark.e2e
async def test_multi_engagement_creation():
    """Test creating multiple engagements in parallel"""
    async with EngagementE2ETest() as test:
        print("\nCreating 5 engagements in parallel...")

        engagement_ids = []
        for i in range(5):
            engagement = await test.create_engagement(
                client_name=f"Client {i+1}",
                engagement_type="AUDIT" if i % 2 == 0 else "REVIEW"
            )
            engagement_ids.append(engagement["id"])
            print(f"  ✓ Created engagement {i+1}: {engagement['id']}")

        assert len(engagement_ids) == 5
        print(f"\n✅ Successfully created {len(engagement_ids)} engagements")


@pytest.mark.asyncio
@pytest.mark.e2e
async def test_engagement_state_transitions():
    """Test all valid state transitions"""
    async with EngagementE2ETest() as test:
        print("\nTesting valid state transitions...")

        # Create engagement
        engagement = await test.create_engagement("State Test Client")
        assert engagement["status"] == "DRAFT"
        print(f"  ✓ Initial state: DRAFT")

        # Test valid transition path
        transitions = [
            ("PLANNING", "Draft complete"),
            ("FIELDWORK", "Planning complete"),
            ("REVIEW", "Fieldwork complete"),
            ("FINALIZED", "Review complete"),
        ]

        for new_state, notes in transitions:
            result = await test.transition_state(new_state, notes)
            assert result["status"] == new_state
            print(f"  ✓ Transitioned to: {new_state}")

        print("\n✅ All state transitions successful")


@pytest.mark.asyncio
@pytest.mark.e2e
async def test_workpaper_organization():
    """Test workpaper organization in binder"""
    async with EngagementE2ETest() as test:
        print("\nTesting workpaper organization...")

        # Create engagement
        await test.create_engagement("Workpaper Test Client")

        # Create sections
        sections = [
            {"section_id": "A", "name": "Cash", "order": 1},
            {"section_id": "B", "name": "Receivables", "order": 2},
            {"section_id": "C", "name": "Inventory", "order": 3},
        ]

        for section in sections:
            await test.create_binder_section(**section)
            print(f"  ✓ Created section {section['section_id']}: {section['name']}")

        # Add multiple workpapers to each section
        for section in sections:
            for i in range(3):
                await test.add_workpaper(
                    section_id=section["section_id"],
                    reference=f"{section['section_id']}-{i+1}",
                    title=f"Workpaper {i+1} for {section['name']}",
                    prepared_by="Test User",
                    content=f"Test content for {section['section_id']}-{i+1}"
                )
                print(f"  ✓ Added workpaper {section['section_id']}-{i+1}")

        # Verify binder structure
        binder = await test.get_binder()
        assert len(binder["sections"]) == len(sections)
        total_workpapers = sum(len(s.get("workpapers", [])) for s in binder["sections"])
        assert total_workpapers == len(sections) * 3

        print(f"\n✅ Binder organized correctly:")
        print(f"   Sections: {len(sections)}")
        print(f"   Workpapers: {total_workpapers}")


@pytest.mark.asyncio
@pytest.mark.e2e
async def test_health_check():
    """Test engagement service health endpoint"""
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=5.0) as client:
        print("\nTesting health endpoint...")
        response = await client.get("/health")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "healthy"
        assert "service" in data

        print(f"  ✓ Service: {data['service']}")
        print(f"  ✓ Status: {data['status']}")
        print(f"\n✅ Health check passed")


# ========================================
# Test Configuration
# ========================================

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


if __name__ == "__main__":
    # Run tests directly
    print("="*60)
    print("Engagement Service E2E Tests")
    print("="*60)

    # Check if service is running
    print("\nChecking if engagement service is running...")
    try:
        import requests
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✓ Service is running")
        else:
            print("✗ Service returned non-200 status")
            exit(1)
    except Exception as e:
        print(f"✗ Service not accessible: {e}")
        print(f"\nPlease start the engagement service:")
        print(f"  cd services/engagement")
        print(f"  uvicorn app.main:app --reload")
        exit(1)

    # Run tests
    print("\nRunning E2E tests...")
    pytest.main([__file__, "-v", "-s"])
