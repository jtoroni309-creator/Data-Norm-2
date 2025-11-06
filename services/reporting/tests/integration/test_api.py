"""Integration tests for Reporting Service API"""
import pytest
from uuid import uuid4


class TestTemplateAPI:
    """Test report template endpoints"""

    @pytest.mark.asyncio
    async def test_create_template(self, client, sample_template):
        """Test creating report template"""
        response = await client.post("/templates", json=sample_template)

        assert response.status_code == 201
        data = response.json()

        assert data["name"] == sample_template["name"]
        assert data["report_type"] == sample_template["report_type"]
        assert "id" in data

    @pytest.mark.asyncio
    async def test_list_templates(self, client, db_template):
        """Test listing templates"""
        response = await client.get("/templates")

        assert response.status_code == 200
        data = response.json()

        assert isinstance(data, list)
        assert len(data) >= 1

        # Find our template
        template = next((t for t in data if t["id"] == str(db_template.id)), None)
        assert template is not None

    @pytest.mark.asyncio
    async def test_list_templates_filtered(self, client, db_template):
        """Test listing templates with filters"""
        # Filter by report type
        response = await client.get(
            "/templates",
            params={"report_type": "audit_report"}
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1

        # Filter by non-matching type
        response = await client.get(
            "/templates",
            params={"report_type": "financial_statement"}
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0

    @pytest.mark.asyncio
    async def test_get_template(self, client, db_template):
        """Test getting single template"""
        response = await client.get(f"/templates/{db_template.id}")

        assert response.status_code == 200
        data = response.json()

        assert data["id"] == str(db_template.id)
        assert data["name"] == db_template.name

    @pytest.mark.asyncio
    async def test_get_nonexistent_template(self, client):
        """Test getting template that doesn't exist"""
        fake_id = uuid4()
        response = await client.get(f"/templates/{fake_id}")

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_template(self, client, db_template):
        """Test updating template"""
        update_data = {
            "name": "Updated Template Name",
            "description": "Updated description"
        }

        response = await client.patch(
            f"/templates/{db_template.id}",
            json=update_data
        )

        assert response.status_code == 200
        data = response.json()

        assert data["name"] == "Updated Template Name"
        assert data["description"] == "Updated description"

    @pytest.mark.asyncio
    async def test_delete_template(self, client, db_template):
        """Test deleting template (soft delete)"""
        response = await client.delete(f"/templates/{db_template.id}")

        assert response.status_code == 204

        # Template should still exist but be inactive
        get_response = await client.get(f"/templates/{db_template.id}")
        assert get_response.status_code == 200

        data = get_response.json()
        assert data["is_active"] == False


class TestReportAPI:
    """Test report endpoints"""

    @pytest.mark.asyncio
    async def test_create_report(self, client, sample_report):
        """Test creating report"""
        response = await client.post("/reports", json=sample_report)

        assert response.status_code == 201
        data = response.json()

        assert data["title"] == sample_report["title"]
        assert data["report_type"] == sample_report["report_type"]
        assert data["status"] == "draft"
        assert "id" in data

    @pytest.mark.asyncio
    async def test_list_reports(self, client, db_report):
        """Test listing reports"""
        response = await client.get("/reports")

        assert response.status_code == 200
        data = response.json()

        assert isinstance(data, list)
        assert len(data) >= 1

    @pytest.mark.asyncio
    async def test_list_reports_filtered(self, client, db_report):
        """Test listing reports with filters"""
        # Filter by engagement
        response = await client.get(
            "/reports",
            params={"engagement_id": str(db_report.engagement_id)}
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1

        # Filter by report type
        response = await client.get(
            "/reports",
            params={"report_type": "audit_report"}
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1

    @pytest.mark.asyncio
    async def test_get_report(self, client, db_report):
        """Test getting single report"""
        response = await client.get(f"/reports/{db_report.id}")

        assert response.status_code == 200
        data = response.json()

        assert data["id"] == str(db_report.id)
        assert data["title"] == db_report.title

    @pytest.mark.asyncio
    async def test_get_nonexistent_report(self, client):
        """Test getting report that doesn't exist"""
        fake_id = uuid4()
        response = await client.get(f"/reports/{fake_id}")

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_generate_report(self, client, db_report):
        """Test report generation"""
        # Note: This will start background task
        # In real tests, you might want to mock the PDF/storage services

        request_data = {
            "report_id": str(db_report.id),
            "regenerate": False
        }

        response = await client.post("/reports/generate", json=request_data)

        assert response.status_code == 200
        data = response.json()

        assert data["report_id"] == str(db_report.id)
        assert data["status"] in ["generating", "generated"]


class TestSignatureAPI:
    """Test e-signature endpoints"""

    @pytest.mark.asyncio
    async def test_create_signature_envelope_no_file(self, client, db_report):
        """Test creating signature envelope without generated report"""
        envelope_data = {
            "report_id": str(db_report.id),
            "subject": "Please sign this report",
            "message": "Please review and sign the attached report",
            "signers": [
                {
                    "name": "John Doe",
                    "email": "john@example.com",
                    "routing_order": 1
                },
                {
                    "name": "Jane Smith",
                    "email": "jane@example.com",
                    "routing_order": 2
                }
            ],
            "expires_in_days": 30,
            "send_immediately": False
        }

        response = await client.post("/signatures", json=envelope_data)

        # Should fail because report hasn't been generated yet
        assert response.status_code == 400
        assert "not yet generated" in response.json()["detail"].lower()


class TestStatsAPI:
    """Test statistics endpoints"""

    @pytest.mark.asyncio
    async def test_get_stats(self, client):
        """Test getting reporting statistics"""
        response = await client.get("/stats")

        assert response.status_code == 200
        data = response.json()

        assert "total_reports" in data
        assert "reports_by_type" in data
        assert "reports_by_status" in data
        assert "total_templates" in data
        assert "active_templates" in data
        assert "pending_signatures" in data
        assert "completed_signatures" in data
        assert "avg_generation_time_ms" in data
        assert "total_storage_bytes" in data

        # Verify data types
        assert isinstance(data["total_reports"], int)
        assert isinstance(data["reports_by_type"], dict)
        assert isinstance(data["avg_generation_time_ms"], (int, float))


class TestHealthCheck:
    """Test health check endpoint"""

    @pytest.mark.asyncio
    async def test_health_check(self, client):
        """Test health check endpoint"""
        response = await client.get("/health")

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "healthy"
        assert "service" in data
        assert "version" in data


class TestReportWorkflow:
    """Test complete report workflow"""

    @pytest.mark.asyncio
    async def test_complete_workflow(self, client, sample_template, sample_report):
        """Test complete report generation workflow"""
        # 1. Create template
        template_response = await client.post("/templates", json=sample_template)
        assert template_response.status_code == 201
        template = template_response.json()

        # 2. Create report
        report_data = sample_report.copy()
        report_data["template_id"] = template["id"]

        report_response = await client.post("/reports", json=report_data)
        assert report_response.status_code == 201
        report = report_response.json()

        assert report["status"] == "draft"

        # 3. Get report
        get_response = await client.get(f"/reports/{report['id']}")
        assert get_response.status_code == 200

        # 4. List reports
        list_response = await client.get("/reports")
        assert list_response.status_code == 200
        reports = list_response.json()
        assert any(r["id"] == report["id"] for r in reports)

        # 5. Get stats
        stats_response = await client.get("/stats")
        assert stats_response.status_code == 200
        stats = stats_response.json()
        assert stats["total_reports"] > 0
