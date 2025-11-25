"""
Tests for R&D Study Automation API Endpoints

Covers:
- Study CRUD operations
- Project qualification endpoints
- QRE management
- Calculation endpoints
- Output generation
- Review console functionality
"""

import pytest
from fastapi.testclient import TestClient
from decimal import Decimal
from datetime import date
from uuid import uuid4

from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def sample_study_data():
    return {
        "entity_name": "Test Corporation",
        "entity_type": "c_corp",
        "ein": "12-3456789",
        "tax_year": 2024,
        "fiscal_year_start": "2024-01-01",
        "fiscal_year_end": "2024-12-31",
        "nexus_states": ["CA", "TX", "NY"],
        "controlled_group": False,
    }


@pytest.fixture
def sample_project_data():
    return {
        "name": "AI Model Development",
        "description": "Development of machine learning models for predictive analytics",
        "business_component": "Analytics Platform",
        "start_date": "2024-01-15",
        "end_date": "2024-12-01",
        "technological_uncertainty": "Uncertain whether neural network architecture would achieve required accuracy",
        "process_of_experimentation": "Iterative testing of multiple model architectures and hyperparameters",
    }


class TestStudyEndpoints:
    """Test study CRUD endpoints."""

    def test_create_study(self, client, sample_study_data):
        """Create a new R&D study."""
        response = client.post("/api/v1/studies", json=sample_study_data)

        assert response.status_code == 201
        data = response.json()
        assert data["entity_name"] == "Test Corporation"
        assert data["status"] == "intake"
        assert "id" in data

    def test_get_study(self, client, sample_study_data):
        """Retrieve study by ID."""
        # Create study first
        create_response = client.post("/api/v1/studies", json=sample_study_data)
        study_id = create_response.json()["id"]

        # Get study
        response = client.get(f"/api/v1/studies/{study_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == study_id
        assert data["entity_name"] == "Test Corporation"

    def test_list_studies(self, client, sample_study_data):
        """List all studies with pagination."""
        # Create multiple studies
        client.post("/api/v1/studies", json=sample_study_data)
        client.post("/api/v1/studies", json={**sample_study_data, "entity_name": "Test Corp 2"})

        response = client.get("/api/v1/studies?page=1&page_size=10")

        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert len(data["items"]) >= 2

    def test_update_study(self, client, sample_study_data):
        """Update existing study."""
        # Create study
        create_response = client.post("/api/v1/studies", json=sample_study_data)
        study_id = create_response.json()["id"]

        # Update
        update_data = {"entity_name": "Updated Corporation"}
        response = client.patch(f"/api/v1/studies/{study_id}", json=update_data)

        assert response.status_code == 200
        assert response.json()["entity_name"] == "Updated Corporation"

    def test_study_status_transition(self, client, sample_study_data):
        """Test study status transitions."""
        # Create study
        create_response = client.post("/api/v1/studies", json=sample_study_data)
        study_id = create_response.json()["id"]

        # Transition to qualification
        response = client.post(f"/api/v1/studies/{study_id}/transition", json={"status": "qualification"})

        assert response.status_code == 200
        assert response.json()["status"] == "qualification"

    def test_invalid_status_transition(self, client, sample_study_data):
        """Invalid status transition should fail."""
        create_response = client.post("/api/v1/studies", json=sample_study_data)
        study_id = create_response.json()["id"]

        # Try to jump to completed (invalid)
        response = client.post(f"/api/v1/studies/{study_id}/transition", json={"status": "completed"})

        assert response.status_code == 400


class TestProjectEndpoints:
    """Test project management endpoints."""

    @pytest.fixture
    def study_with_project(self, client, sample_study_data, sample_project_data):
        """Create study with a project."""
        study_response = client.post("/api/v1/studies", json=sample_study_data)
        study_id = study_response.json()["id"]

        project_response = client.post(
            f"/api/v1/studies/{study_id}/projects",
            json=sample_project_data
        )
        project_id = project_response.json()["id"]

        return {"study_id": study_id, "project_id": project_id}

    def test_create_project(self, client, sample_study_data, sample_project_data):
        """Create project within study."""
        study_response = client.post("/api/v1/studies", json=sample_study_data)
        study_id = study_response.json()["id"]

        response = client.post(
            f"/api/v1/studies/{study_id}/projects",
            json=sample_project_data
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "AI Model Development"
        assert data["qualification_status"] == "pending"

    def test_qualify_project_with_ai(self, study_with_project, client):
        """Run AI qualification on project."""
        study_id = study_with_project["study_id"]
        project_id = study_with_project["project_id"]

        response = client.post(
            f"/api/v1/studies/{study_id}/projects/{project_id}/qualify"
        )

        assert response.status_code == 200
        data = response.json()
        assert "four_part_test" in data
        assert "permitted_purpose" in data["four_part_test"]
        assert "ai_confidence" in data

    def test_project_cpa_review(self, study_with_project, client):
        """CPA review and approval of project."""
        study_id = study_with_project["study_id"]
        project_id = study_with_project["project_id"]

        # First qualify
        client.post(f"/api/v1/studies/{study_id}/projects/{project_id}/qualify")

        # CPA review
        review_data = {
            "status": "approved",
            "reviewer_notes": "Project clearly meets 4-part test",
        }
        response = client.post(
            f"/api/v1/studies/{study_id}/projects/{project_id}/review",
            json=review_data
        )

        assert response.status_code == 200
        assert response.json()["qualification_status"] == "qualified"

    def test_project_override(self, study_with_project, client):
        """CPA override of AI qualification score."""
        study_id = study_with_project["study_id"]
        project_id = study_with_project["project_id"]

        # Qualify first
        client.post(f"/api/v1/studies/{study_id}/projects/{project_id}/qualify")

        # Override a specific element
        override_data = {
            "element": "elimination_of_uncertainty",
            "score": 0.85,
            "notes": "Strong evidence in design documents supports higher score",
        }
        response = client.post(
            f"/api/v1/studies/{study_id}/projects/{project_id}/override",
            json=override_data
        )

        assert response.status_code == 200
        data = response.json()
        assert data["four_part_test"]["elimination_of_uncertainty"]["cpa_override"] is not None


class TestEmployeeEndpoints:
    """Test employee and wage QRE endpoints."""

    @pytest.fixture
    def study_id(self, client, sample_study_data):
        response = client.post("/api/v1/studies", json=sample_study_data)
        return response.json()["id"]

    def test_add_employee(self, client, study_id):
        """Add employee to study."""
        employee_data = {
            "name": "Jane Engineer",
            "title": "Senior Software Engineer",
            "department": "Engineering",
            "total_compensation": 180000,
            "rd_allocation_percent": 75,
        }

        response = client.post(
            f"/api/v1/studies/{study_id}/employees",
            json=employee_data
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Jane Engineer"
        assert data["total_compensation"] == 180000

    def test_update_employee_allocation(self, client, study_id):
        """Update employee R&D allocation."""
        # Add employee
        emp_response = client.post(
            f"/api/v1/studies/{study_id}/employees",
            json={
                "name": "Test Employee",
                "title": "Engineer",
                "total_compensation": 100000,
                "rd_allocation_percent": 50,
            }
        )
        emp_id = emp_response.json()["id"]

        # Update allocation
        response = client.put(
            f"/api/v1/studies/{study_id}/employees/{emp_id}",
            json={"rd_allocation_percent": 80}
        )

        assert response.status_code == 200
        assert response.json()["rd_allocation_percent"] == 80

    def test_employee_project_assignment(self, client, study_id, sample_project_data):
        """Assign employee to projects."""
        # Add project
        proj_response = client.post(
            f"/api/v1/studies/{study_id}/projects",
            json=sample_project_data
        )
        project_id = proj_response.json()["id"]

        # Add employee
        emp_response = client.post(
            f"/api/v1/studies/{study_id}/employees",
            json={
                "name": "Test Employee",
                "title": "Engineer",
                "total_compensation": 100000,
                "rd_allocation_percent": 100,
            }
        )
        emp_id = emp_response.json()["id"]

        # Assign to project
        assignment = {
            "project_id": project_id,
            "allocation_percent": 60,
        }
        response = client.post(
            f"/api/v1/studies/{study_id}/employees/{emp_id}/projects",
            json=assignment
        )

        assert response.status_code == 200


class TestCalculationEndpoints:
    """Test calculation endpoints."""

    @pytest.fixture
    def populated_study(self, client, sample_study_data, sample_project_data):
        """Create study with projects and employees."""
        # Create study
        study_response = client.post("/api/v1/studies", json=sample_study_data)
        study_id = study_response.json()["id"]

        # Add project
        proj_response = client.post(
            f"/api/v1/studies/{study_id}/projects",
            json=sample_project_data
        )
        project_id = proj_response.json()["id"]

        # Qualify project
        client.post(f"/api/v1/studies/{study_id}/projects/{project_id}/qualify")
        client.post(
            f"/api/v1/studies/{study_id}/projects/{project_id}/review",
            json={"status": "approved"}
        )

        # Add employees
        for i in range(3):
            emp_response = client.post(
                f"/api/v1/studies/{study_id}/employees",
                json={
                    "name": f"Engineer {i}",
                    "title": "Software Engineer",
                    "total_compensation": 100000 + i * 20000,
                    "rd_allocation_percent": 80,
                }
            )
            emp_id = emp_response.json()["id"]
            client.post(
                f"/api/v1/studies/{study_id}/employees/{emp_id}/projects",
                json={"project_id": project_id, "allocation_percent": 80}
            )

        return study_id

    def test_calculate_qre(self, client, populated_study):
        """Calculate total QRE."""
        response = client.post(f"/api/v1/studies/{populated_study}/calculate/qre")

        assert response.status_code == 200
        data = response.json()
        assert "total_qre" in data
        assert "breakdown" in data
        assert data["total_qre"] > 0

    def test_calculate_federal_credit(self, client, populated_study):
        """Calculate federal R&D tax credit."""
        # Calculate QRE first
        client.post(f"/api/v1/studies/{populated_study}/calculate/qre")

        # Calculate credit
        response = client.post(
            f"/api/v1/studies/{populated_study}/calculate/federal",
            json={
                "method": "asc",
                "section_280c": True,
                "prior_year_qre": [500000, 450000, 400000],
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "federal_credit" in data
        assert "method" in data
        assert data["method"] == "asc"

    def test_calculate_state_credits(self, client, populated_study):
        """Calculate state R&D credits."""
        client.post(f"/api/v1/studies/{populated_study}/calculate/qre")

        response = client.post(
            f"/api/v1/studies/{populated_study}/calculate/states",
            json={
                "state_allocations": {"CA": 0.6, "TX": 0.4}
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "CA" in data
        assert "TX" in data

    def test_compare_methods(self, client, populated_study):
        """Compare Regular vs ASC credit methods."""
        client.post(f"/api/v1/studies/{populated_study}/calculate/qre")

        response = client.get(f"/api/v1/studies/{populated_study}/calculate/compare")

        assert response.status_code == 200
        data = response.json()
        assert "regular_credit" in data
        assert "asc_credit" in data
        assert "recommended_method" in data


class TestOutputGeneration:
    """Test output generation endpoints."""

    @pytest.fixture
    def completed_study(self, client, populated_study):
        """Study with completed calculations."""
        # Run calculations
        client.post(f"/api/v1/studies/{populated_study}/calculate/qre")
        client.post(
            f"/api/v1/studies/{populated_study}/calculate/federal",
            json={"method": "asc", "section_280c": True, "prior_year_qre": []}
        )
        return populated_study

    def test_generate_pdf_report(self, client, completed_study):
        """Generate PDF study report."""
        response = client.post(
            f"/api/v1/studies/{completed_study}/outputs/pdf",
            json={"include_appendix": True}
        )

        assert response.status_code == 200
        data = response.json()
        assert "file_id" in data
        assert data["file_type"] == "pdf"

    def test_generate_excel_workbook(self, client, completed_study):
        """Generate Excel workbook."""
        response = client.post(
            f"/api/v1/studies/{completed_study}/outputs/excel"
        )

        assert response.status_code == 200
        data = response.json()
        assert "file_id" in data
        assert data["file_type"] == "xlsx"

    def test_generate_form_6765(self, client, completed_study):
        """Generate Form 6765 data."""
        response = client.post(
            f"/api/v1/studies/{completed_study}/outputs/form-6765"
        )

        assert response.status_code == 200
        data = response.json()
        assert "form_number" in data
        assert data["form_number"] == "6765"
        assert "section_a" in data
        assert "section_b" in data

    def test_download_output(self, client, completed_study):
        """Download generated output file."""
        # Generate file
        gen_response = client.post(
            f"/api/v1/studies/{completed_study}/outputs/excel"
        )
        file_id = gen_response.json()["file_id"]

        # Download
        response = client.get(
            f"/api/v1/studies/{completed_study}/outputs/{file_id}/download"
        )

        assert response.status_code == 200
        assert "application" in response.headers.get("content-type", "")


class TestReviewConsole:
    """Test CPA review console endpoints."""

    def test_get_review_queue(self, client, populated_study):
        """Get projects pending review."""
        response = client.get(
            f"/api/v1/studies/{populated_study}/review/queue"
        )

        assert response.status_code == 200
        data = response.json()
        assert "pending_projects" in data
        assert "risk_flags" in data

    def test_bulk_approve(self, client, populated_study):
        """Bulk approve multiple items."""
        # Get projects
        queue = client.get(f"/api/v1/studies/{populated_study}/review/queue").json()
        project_ids = [p["id"] for p in queue.get("pending_projects", [])][:2]

        if project_ids:
            response = client.post(
                f"/api/v1/studies/{populated_study}/review/bulk-approve",
                json={"project_ids": project_ids}
            )

            assert response.status_code == 200

    def test_get_risk_summary(self, client, populated_study):
        """Get study risk summary."""
        response = client.get(
            f"/api/v1/studies/{populated_study}/review/risks"
        )

        assert response.status_code == 200
        data = response.json()
        assert "high_risk_count" in data
        assert "risk_items" in data


class TestAuditTrail:
    """Test audit trail endpoints."""

    def test_get_audit_log(self, client, sample_study_data):
        """Get audit log for study."""
        # Create study (generates audit entry)
        study_response = client.post("/api/v1/studies", json=sample_study_data)
        study_id = study_response.json()["id"]

        response = client.get(f"/api/v1/studies/{study_id}/audit-log")

        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
        assert data[0]["action"] == "study_created"

    def test_calculation_audit_trail(self, client, populated_study):
        """Verify calculation audit trail."""
        # Run calculation
        client.post(f"/api/v1/studies/{populated_study}/calculate/qre")
        calc_response = client.post(
            f"/api/v1/studies/{populated_study}/calculate/federal",
            json={"method": "asc", "section_280c": True, "prior_year_qre": []}
        )

        # Check audit trail
        calc_id = calc_response.json().get("calculation_id")
        if calc_id:
            response = client.get(
                f"/api/v1/studies/{populated_study}/calculations/{calc_id}/audit-trail"
            )

            assert response.status_code == 200
            data = response.json()
            assert "steps" in data
            # Each step should have IRC citation
            for step in data["steps"]:
                assert "irc_citation" in step or "formula" in step


class TestNarrativeGeneration:
    """Test AI narrative generation endpoints."""

    def test_generate_project_narrative(self, client, sample_study_data, sample_project_data):
        """Generate AI narrative for project."""
        study_response = client.post("/api/v1/studies", json=sample_study_data)
        study_id = study_response.json()["id"]

        proj_response = client.post(
            f"/api/v1/studies/{study_id}/projects",
            json=sample_project_data
        )
        project_id = proj_response.json()["id"]

        response = client.post(
            f"/api/v1/studies/{study_id}/projects/{project_id}/narratives/generate"
        )

        assert response.status_code == 200
        data = response.json()
        assert "narrative" in data
        assert "citations" in data
        assert data["ai_generated"] is True

    def test_edit_narrative(self, client, sample_study_data, sample_project_data):
        """Edit generated narrative."""
        study_response = client.post("/api/v1/studies", json=sample_study_data)
        study_id = study_response.json()["id"]

        proj_response = client.post(
            f"/api/v1/studies/{study_id}/projects",
            json=sample_project_data
        )
        project_id = proj_response.json()["id"]

        # Generate narrative
        gen_response = client.post(
            f"/api/v1/studies/{study_id}/projects/{project_id}/narratives/generate"
        )
        narrative_id = gen_response.json().get("id")

        if narrative_id:
            # Edit
            response = client.put(
                f"/api/v1/studies/{study_id}/narratives/{narrative_id}",
                json={"content": "Updated narrative content by CPA."}
            )

            assert response.status_code == 200
            assert response.json()["cpa_edited"] is True
