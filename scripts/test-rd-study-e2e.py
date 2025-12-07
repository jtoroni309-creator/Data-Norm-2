#!/usr/bin/env python3
"""
R&D Study E2E Test Script

Tests the complete R&D Study Automation workflow including:
- PA and NY state credit calculations
- AI 4-part test narrative generation
- Excel workbook generation
- PDF study report generation
"""

import requests
import json
import os
import sys
from decimal import Decimal
from typing import Dict, Any, Optional
from dataclasses import dataclass

# Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "https://api.auraai.toroniandcompany.com")
TEST_EMAIL = os.getenv("CPA_TEST_EMAIL", "test.auditor@auraai.test")
TEST_PASSWORD = os.getenv("CPA_TEST_PASSWORD", "TestPassword123!")

# Test data paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SYNTHETIC_DATA_DIR = os.path.join(SCRIPT_DIR, "..", "tests", "rd-study-e2e", "synthetic-data")


@dataclass
class TestResult:
    """Test result data class."""
    name: str
    passed: bool
    message: str
    details: Optional[Dict[str, Any]] = None


class RDStudyE2ETest:
    """R&D Study E2E Test Suite."""

    def __init__(self):
        self.session = requests.Session()
        self.auth_token: Optional[str] = None
        self.study_id: Optional[str] = None
        self.results: list[TestResult] = []

    def log(self, message: str, level: str = "INFO"):
        """Log message with level."""
        prefix = {"INFO": "[INFO]", "PASS": "[PASS]", "FAIL": "[FAIL]", "WARN": "[WARN]"}
        print(f"{prefix.get(level, '[INFO]')} {message}")

    def authenticate(self) -> bool:
        """Authenticate and get JWT token."""
        try:
            response = self.session.post(
                f"{API_BASE_URL}/auth/login",
                json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
            )

            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("access_token")
                self.session.headers["Authorization"] = f"Bearer {self.auth_token}"
                return True
            else:
                self.log(f"Authentication failed: {response.status_code}", "FAIL")
                return False
        except Exception as e:
            self.log(f"Authentication error: {e}", "FAIL")
            return False

    def load_company_info(self) -> Dict[str, Any]:
        """Load company info from synthetic data."""
        with open(os.path.join(SYNTHETIC_DATA_DIR, "company_info.json"), "r") as f:
            return json.load(f)

    def load_projects(self) -> Dict[str, Any]:
        """Load projects from synthetic data."""
        with open(os.path.join(SYNTHETIC_DATA_DIR, "projects.json"), "r") as f:
            return json.load(f)

    def test_create_study(self) -> TestResult:
        """Test creating an R&D study."""
        try:
            company_info = self.load_company_info()
            company = company_info["company"]

            response = self.session.post(
                f"{API_BASE_URL}/rd-studies",
                json={
                    "firm_id": "test-firm-id",
                    "client_id": "test-client-technova",
                    "name": f"TechNova R&D Study - Tax Year {company['tax_year']}",
                    "tax_year": company["tax_year"],
                    "entity_type": company["entity_type"],
                    "entity_name": company["name"],
                    "ein": company["ein"],
                    "fiscal_year_start": company["fiscal_year_start"],
                    "fiscal_year_end": company["fiscal_year_end"],
                    "states": company["states_with_nexus"],
                    "primary_state": "PA"
                }
            )

            if response.status_code == 201:
                data = response.json()
                self.study_id = data["id"]
                return TestResult(
                    name="Create R&D Study",
                    passed=True,
                    message=f"Created study {self.study_id}",
                    details={"study_id": self.study_id}
                )
            else:
                return TestResult(
                    name="Create R&D Study",
                    passed=False,
                    message=f"Failed with status {response.status_code}: {response.text}"
                )
        except Exception as e:
            return TestResult(
                name="Create R&D Study",
                passed=False,
                message=str(e)
            )

    def test_add_projects(self) -> TestResult:
        """Test adding projects to study."""
        try:
            projects = self.load_projects()["projects"]
            added = 0

            for project in projects:
                response = self.session.post(
                    f"{API_BASE_URL}/rd-studies/{self.study_id}/projects",
                    json={
                        "name": project["name"],
                        "code": project["code"],
                        "department": project["department"],
                        "description": project["description"],
                        "start_date": project["start_date"],
                        "is_ongoing": project["is_ongoing"],
                        "business_component": project["business_component"],
                        "state_allocation": project["state_allocation"]
                    }
                )
                if response.status_code == 201:
                    added += 1

            return TestResult(
                name="Add R&D Projects",
                passed=added == len(projects),
                message=f"Added {added}/{len(projects)} projects",
                details={"projects_added": added}
            )
        except Exception as e:
            return TestResult(
                name="Add R&D Projects",
                passed=False,
                message=str(e)
            )

    def test_calculate_credits(self) -> TestResult:
        """Test federal and state credit calculations."""
        try:
            company_info = self.load_company_info()

            response = self.session.post(
                f"{API_BASE_URL}/rd-studies/{self.study_id}/calculate",
                json={
                    "historical_data": company_info["historical_data"],
                    "section_280c": company_info["section_280c_election"],
                    "states": ["PA", "NY", "CA", "TX", "NJ"]
                }
            )

            if response.status_code == 200:
                data = response.json()

                # Verify federal credits
                federal_ok = (
                    data.get("federal_regular_credit", 0) > 0 and
                    data.get("federal_asc_credit", 0) > 0
                )

                # Verify PA credit (10% rate)
                pa_credit = data.get("state_credits", {}).get("PA", {})
                pa_ok = pa_credit.get("rate") == 0.10

                # Verify NY credit (9% rate)
                ny_credit = data.get("state_credits", {}).get("NY", {})
                ny_ok = ny_credit.get("rate") == 0.09

                all_ok = federal_ok and pa_ok and ny_ok

                return TestResult(
                    name="Calculate Credits (Federal + PA + NY)",
                    passed=all_ok,
                    message=f"Federal: ${data.get('final_federal_credit', 0):,.2f}, PA: ${pa_credit.get('credit', 0):,.2f}, NY: ${ny_credit.get('credit', 0):,.2f}",
                    details={
                        "federal_regular": data.get("federal_regular_credit"),
                        "federal_asc": data.get("federal_asc_credit"),
                        "pa_credit": pa_credit,
                        "ny_credit": ny_credit,
                        "total": data.get("total_credits")
                    }
                )
            else:
                return TestResult(
                    name="Calculate Credits",
                    passed=False,
                    message=f"Failed with status {response.status_code}"
                )
        except Exception as e:
            return TestResult(
                name="Calculate Credits",
                passed=False,
                message=str(e)
            )

    def test_generate_excel(self) -> TestResult:
        """Test Excel workbook generation."""
        try:
            response = self.session.post(
                f"{API_BASE_URL}/rd-studies/{self.study_id}/generate/excel"
            )

            if response.status_code == 200:
                data = response.json()
                return TestResult(
                    name="Generate Excel Workbook",
                    passed=True,
                    message=f"Generated workbook: {data.get('file_id')}",
                    details={"file_id": data.get("file_id"), "url": data.get("download_url")}
                )
            else:
                return TestResult(
                    name="Generate Excel Workbook",
                    passed=False,
                    message=f"Failed with status {response.status_code}"
                )
        except Exception as e:
            return TestResult(
                name="Generate Excel Workbook",
                passed=False,
                message=str(e)
            )

    def test_generate_pdf(self) -> TestResult:
        """Test PDF report generation."""
        try:
            response = self.session.post(
                f"{API_BASE_URL}/rd-studies/{self.study_id}/generate/pdf"
            )

            if response.status_code == 200:
                data = response.json()
                return TestResult(
                    name="Generate PDF Report",
                    passed=True,
                    message=f"Generated PDF: {data.get('file_id')}",
                    details={"file_id": data.get("file_id"), "url": data.get("download_url")}
                )
            else:
                return TestResult(
                    name="Generate PDF Report",
                    passed=False,
                    message=f"Failed with status {response.status_code}"
                )
        except Exception as e:
            return TestResult(
                name="Generate PDF Report",
                passed=False,
                message=str(e)
            )

    def test_ai_narrative_generation(self) -> TestResult:
        """Test AI 4-part test narrative generation."""
        try:
            # Get first project
            response = self.session.get(
                f"{API_BASE_URL}/rd-studies/{self.study_id}/projects"
            )

            if response.status_code != 200:
                return TestResult(
                    name="AI Narrative Generation",
                    passed=False,
                    message="Failed to get projects"
                )

            projects = response.json()
            if not projects:
                return TestResult(
                    name="AI Narrative Generation",
                    passed=False,
                    message="No projects found"
                )

            project_id = projects[0]["id"]

            # Generate narratives
            response = self.session.post(
                f"{API_BASE_URL}/rd-studies/{self.study_id}/projects/{project_id}/generate-narratives"
            )

            if response.status_code == 200:
                data = response.json()
                narratives = data.get("narratives", [])

                return TestResult(
                    name="AI 4-Part Test Narrative Generation",
                    passed=len(narratives) > 0,
                    message=f"Generated {len(narratives)} narratives",
                    details={"narrative_count": len(narratives)}
                )
            else:
                return TestResult(
                    name="AI Narrative Generation",
                    passed=False,
                    message=f"Failed with status {response.status_code}"
                )
        except Exception as e:
            return TestResult(
                name="AI Narrative Generation",
                passed=False,
                message=str(e)
            )

    def run_all_tests(self):
        """Run all E2E tests."""
        print("=" * 60)
        print("R&D STUDY AUTOMATION E2E TEST SUITE")
        print("Testing PA and NY State Credits")
        print("=" * 60)
        print()

        # Authenticate
        self.log("Authenticating...")
        if not self.authenticate():
            self.log("Authentication failed. Exiting.", "FAIL")
            return False
        self.log("Authenticated successfully", "PASS")

        # Run tests
        tests = [
            self.test_create_study,
            self.test_add_projects,
            self.test_calculate_credits,
            self.test_ai_narrative_generation,
            self.test_generate_excel,
            self.test_generate_pdf,
        ]

        for test in tests:
            print()
            self.log(f"Running: {test.__name__}")
            result = test()
            self.results.append(result)

            if result.passed:
                self.log(f"{result.name}: {result.message}", "PASS")
            else:
                self.log(f"{result.name}: {result.message}", "FAIL")

        # Summary
        print()
        print("=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)

        passed = sum(1 for r in self.results if r.passed)
        total = len(self.results)

        for result in self.results:
            status = "PASS" if result.passed else "FAIL"
            print(f"  [{status}] {result.name}")
            if result.details:
                for key, value in result.details.items():
                    if isinstance(value, dict):
                        print(f"         {key}:")
                        for k, v in value.items():
                            print(f"           {k}: {v}")
                    else:
                        print(f"         {key}: {value}")

        print()
        print(f"Results: {passed}/{total} tests passed")
        print("=" * 60)

        return passed == total


def main():
    """Main entry point."""
    test = RDStudyE2ETest()
    success = test.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
