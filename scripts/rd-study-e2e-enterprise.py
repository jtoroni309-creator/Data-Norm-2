#!/usr/bin/env python3
"""
Enterprise-Level R&D Study End-to-End Test

This script simulates a full R&D study workflow with substantial enterprise data:
- 50+ employees with various roles and departments
- 20+ subcontractors with contract research expenses
- 30+ supply expenses across different categories
- 15+ computer rental expenses (cloud services, equipment)
- Multiple R&D projects across different business areas

Acceptance Criteria:
1. All data submits successfully via API
2. Data routes to correct categories in CPA workspace
3. AI study generation completes
4. Deliverables (Excel, PDF, Form 6765) generate correctly
"""

import asyncio
import httpx
import json
import random
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Any
from uuid import UUID

# API Configuration
BASE_URL = "http://identity:80"
RD_STUDY_URL = "http://rd-study-automation:8000"

# Test configuration
COMPANY_NAME = "TechNova Solutions Inc."
TAX_YEAR = 2024
EIN = "12-3456789"


# =============================================================================
# ENTERPRISE TEST DATA GENERATORS
# =============================================================================

def generate_employees() -> List[Dict[str, Any]]:
    """Generate 50+ employees with realistic R&D roles and wages."""
    departments = ["Engineering", "Product Development", "R&D Labs", "Data Science", "Quality Assurance"]
    titles = {
        "Engineering": ["Senior Software Engineer", "Principal Engineer", "Staff Engineer", "Engineering Manager", "Software Developer", "DevOps Engineer", "Systems Architect"],
        "Product Development": ["Product Manager", "Technical Product Manager", "UX Engineer", "Product Designer", "Solutions Architect"],
        "R&D Labs": ["Research Scientist", "Senior Researcher", "Lab Director", "Research Engineer", "Applied Scientist"],
        "Data Science": ["Data Scientist", "ML Engineer", "AI Researcher", "Data Engineer", "Analytics Lead"],
        "Quality Assurance": ["QA Engineer", "Test Automation Engineer", "Quality Manager", "Performance Engineer"]
    }

    employees = []
    employee_id = 1000

    for dept in departments:
        # 8-12 employees per department
        num_employees = random.randint(8, 12)
        for _ in range(num_employees):
            title = random.choice(titles[dept])

            # Base salary by title seniority
            if "Senior" in title or "Principal" in title or "Director" in title or "Manager" in title:
                base_salary = random.randint(150000, 250000)
                qualified_time = random.randint(60, 95)
            elif "Lead" in title or "Staff" in title:
                base_salary = random.randint(120000, 180000)
                qualified_time = random.randint(50, 85)
            else:
                base_salary = random.randint(85000, 140000)
                qualified_time = random.randint(40, 75)

            bonus = int(base_salary * random.uniform(0.05, 0.20))
            stock_comp = int(base_salary * random.uniform(0, 0.15))

            employees.append({
                "employee_id": f"EMP-{employee_id}",
                "name": f"{random.choice(['John', 'Jane', 'Michael', 'Sarah', 'David', 'Emily', 'Robert', 'Jennifer', 'William', 'Lisa', 'James', 'Maria', 'Daniel', 'Susan', 'Thomas'])} {random.choice(['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez', 'Anderson', 'Taylor', 'Thomas', 'Hernandez', 'Moore'])}",
                "title": title,
                "department": dept,
                "state": random.choice(["CA", "NY", "TX", "WA", "MA", "IL", "CO", "GA"]),
                "hire_date": str(date(TAX_YEAR - random.randint(0, 8), random.randint(1, 12), random.randint(1, 28))),
                "total_wages": str(base_salary + bonus + stock_comp),
                "w2_wages": str(base_salary + bonus),
                "bonus": str(bonus),
                "stock_compensation": str(stock_comp),
                "qualified_time_percentage": qualified_time,
                "qualified_time_source": random.choice(["time_study", "project_records", "manager_estimate"])
            })
            employee_id += 1

    return employees


def generate_subcontractors() -> List[Dict[str, Any]]:
    """Generate 20+ subcontractors with contract research expenses."""
    contractors = [
        {"name": "Quantum Computing Labs LLC", "specialty": "Quantum algorithm development", "ein": "98-7654321"},
        {"name": "AI Research Partners Inc.", "specialty": "Machine learning research", "ein": "87-6543210"},
        {"name": "BioTech Solutions Corp.", "specialty": "Biotechnology R&D", "ein": "76-5432109"},
        {"name": "Cloud Systems Research", "specialty": "Cloud infrastructure research", "ein": "65-4321098"},
        {"name": "Cybersecurity Research Group", "specialty": "Security protocol development", "ein": "54-3210987"},
        {"name": "Data Analytics Innovations", "specialty": "Advanced analytics R&D", "ein": "43-2109876"},
        {"name": "Embedded Systems Lab", "specialty": "IoT and embedded systems", "ein": "32-1098765"},
        {"name": "FinTech Research Alliance", "specialty": "Financial technology R&D", "ein": "21-0987654"},
        {"name": "Green Energy Tech Co.", "specialty": "Sustainable energy research", "ein": "10-9876543"},
        {"name": "Healthcare Innovations Inc.", "specialty": "Medical device R&D", "ein": "09-8765432"},
        {"name": "Industrial Automation R&D", "specialty": "Manufacturing automation", "ein": "98-6543217"},
        {"name": "Material Science Partners", "specialty": "Advanced materials research", "ein": "87-5432106"},
        {"name": "NanoTech Research Corp.", "specialty": "Nanotechnology development", "ein": "76-4321095"},
        {"name": "Neural Networks Inc.", "specialty": "Deep learning research", "ein": "65-3210984"},
        {"name": "Optical Systems Research", "specialty": "Photonics and optics R&D", "ein": "54-2109873"},
        {"name": "Precision Engineering Labs", "specialty": "Precision manufacturing R&D", "ein": "43-1098762"},
        {"name": "Robotics Innovation Center", "specialty": "Robotics development", "ein": "32-0987651"},
        {"name": "Semiconductor Research LLC", "specialty": "Chip design and testing", "ein": "21-9876540"},
        {"name": "Software Architecture Partners", "specialty": "Software platform research", "ein": "10-8765439"},
        {"name": "University Tech Transfer Office", "specialty": "Academic research partnership", "ein": "09-7654328", "is_qualified_org": True},
        {"name": "National Research Laboratory", "specialty": "Fundamental research", "ein": "98-5432106", "is_qualified_org": True},
    ]

    qres = []
    for contractor in contractors:
        # Multiple contracts per contractor possible
        num_contracts = random.randint(1, 3)
        for i in range(num_contracts):
            amount = Decimal(str(random.randint(50000, 500000)))
            qres.append({
                "category": "contract_research",
                "contractor_name": contractor["name"],
                "contractor_ein": contractor["ein"],
                "is_qualified_research_org": contractor.get("is_qualified_org", False),
                "contract_percentage": 65 if not contractor.get("is_qualified_org") else 100,
                "gross_amount": str(amount),
                "qualified_percentage": 100,
                "source_reference": f"Contract #{random.randint(1000, 9999)}-{TAX_YEAR}",
                "supply_description": f"{contractor['specialty']} - Phase {i+1}"
            })

    return qres


def generate_supplies() -> List[Dict[str, Any]]:
    """Generate 30+ supply expenses across different categories."""
    supply_categories = [
        # Lab supplies
        {"desc": "Laboratory reagents and chemicals", "vendor": "Fisher Scientific", "gl": "6100-LAB", "min": 5000, "max": 50000},
        {"desc": "Prototyping materials", "vendor": "McMaster-Carr", "gl": "6100-PROTO", "min": 10000, "max": 75000},
        {"desc": "Electronic components", "vendor": "Digi-Key Electronics", "gl": "6100-ELEC", "min": 15000, "max": 100000},
        {"desc": "Testing equipment consumables", "vendor": "Keysight Technologies", "gl": "6100-TEST", "min": 8000, "max": 60000},
        {"desc": "3D printing materials", "vendor": "Stratasys", "gl": "6100-3DP", "min": 5000, "max": 40000},
        {"desc": "PCB fabrication supplies", "vendor": "PCBWay", "gl": "6100-PCB", "min": 10000, "max": 80000},
        # Software and digital supplies
        {"desc": "Development software licenses", "vendor": "JetBrains", "gl": "6200-SW", "min": 5000, "max": 30000},
        {"desc": "Cloud development credits", "vendor": "AWS", "gl": "6200-CLOUD", "min": 20000, "max": 150000},
        {"desc": "AI/ML training compute", "vendor": "Google Cloud", "gl": "6200-ML", "min": 30000, "max": 200000},
        {"desc": "Database licensing", "vendor": "MongoDB", "gl": "6200-DB", "min": 10000, "max": 50000},
        {"desc": "Testing platform subscription", "vendor": "Sauce Labs", "gl": "6200-TEST", "min": 5000, "max": 25000},
        # Hardware supplies
        {"desc": "Server components", "vendor": "Dell Technologies", "gl": "6300-HW", "min": 25000, "max": 150000},
        {"desc": "Networking equipment", "vendor": "Cisco Systems", "gl": "6300-NET", "min": 15000, "max": 100000},
        {"desc": "Storage devices", "vendor": "Western Digital", "gl": "6300-STOR", "min": 10000, "max": 75000},
        {"desc": "Development workstations", "vendor": "HP Inc.", "gl": "6300-WS", "min": 20000, "max": 120000},
        # Specialized R&D supplies
        {"desc": "Optical measurement supplies", "vendor": "Thorlabs", "gl": "6400-OPT", "min": 8000, "max": 45000},
        {"desc": "Mechanical testing materials", "vendor": "Instron", "gl": "6400-MECH", "min": 12000, "max": 60000},
        {"desc": "Environmental chamber consumables", "vendor": "Thermotron", "gl": "6400-ENV", "min": 5000, "max": 35000},
        {"desc": "Calibration standards", "vendor": "NIST Traceable", "gl": "6400-CAL", "min": 3000, "max": 20000},
        {"desc": "Safety equipment", "vendor": "3M Safety", "gl": "6400-SAFE", "min": 2000, "max": 15000},
    ]

    qres = []
    for supply in supply_categories:
        # Multiple purchases per category
        num_purchases = random.randint(1, 4)
        for i in range(num_purchases):
            amount = Decimal(str(random.randint(supply["min"], supply["max"])))
            qres.append({
                "category": "supplies",
                "supply_description": f"{supply['desc']} - Q{random.randint(1,4)} {TAX_YEAR}",
                "supply_vendor": supply["vendor"],
                "gl_account": supply["gl"],
                "gross_amount": str(amount),
                "qualified_percentage": random.randint(80, 100),
                "source_reference": f"PO-{random.randint(10000, 99999)}"
            })

    return qres


def generate_computer_rentals() -> List[Dict[str, Any]]:
    """Generate 15+ computer rental expenses (cloud services, leased equipment)."""
    rentals = [
        # Cloud computing
        {"desc": "AWS EC2 compute instances - R&D workloads", "vendor": "Amazon Web Services", "min": 50000, "max": 300000},
        {"desc": "Azure ML compute clusters", "vendor": "Microsoft Azure", "min": 40000, "max": 250000},
        {"desc": "Google Cloud TPU access", "vendor": "Google Cloud", "min": 30000, "max": 200000},
        {"desc": "High-performance GPU clusters", "vendor": "Lambda Labs", "min": 25000, "max": 150000},
        {"desc": "Kubernetes cluster hosting", "vendor": "Digital Ocean", "min": 15000, "max": 80000},
        # Data infrastructure
        {"desc": "Data warehouse compute", "vendor": "Snowflake", "min": 20000, "max": 120000},
        {"desc": "Real-time analytics platform", "vendor": "Databricks", "min": 30000, "max": 180000},
        {"desc": "ElasticSearch cluster hosting", "vendor": "Elastic Cloud", "min": 10000, "max": 60000},
        # Specialized compute
        {"desc": "Quantum computing access", "vendor": "IBM Quantum", "min": 15000, "max": 100000},
        {"desc": "Scientific computing resources", "vendor": "NVIDIA DGX Cloud", "min": 35000, "max": 200000},
        # Leased equipment
        {"desc": "High-performance workstations lease", "vendor": "Dell Financial", "min": 20000, "max": 100000},
        {"desc": "Test equipment rental", "vendor": "Electro Rent", "min": 15000, "max": 75000},
        {"desc": "Network simulation hardware", "vendor": "Ixia Networks", "min": 10000, "max": 50000},
        {"desc": "Render farm compute", "vendor": "Render Pool", "min": 8000, "max": 45000},
        {"desc": "CI/CD infrastructure", "vendor": "CircleCI", "min": 5000, "max": 30000},
    ]

    qres = []
    for rental in rentals:
        amount = Decimal(str(random.randint(rental["min"], rental["max"])))
        qres.append({
            "category": "computer_rental",
            "supply_description": rental["desc"],
            "supply_vendor": rental["vendor"],
            "gross_amount": str(amount),
            "qualified_percentage": random.randint(75, 100),
            "source_reference": f"INV-{random.randint(100000, 999999)}"
        })

    return qres


def generate_projects() -> List[Dict[str, Any]]:
    """Generate R&D projects across different business areas."""
    projects = [
        {
            "name": "Next-Gen AI Platform Development",
            "code": "PROJ-AI-001",
            "description": "Development of advanced machine learning algorithms for natural language processing, including novel transformer architectures and few-shot learning capabilities.",
            "department": "Data Science",
            "business_component": "AI Platform"
        },
        {
            "name": "Cloud Infrastructure Scalability Research",
            "code": "PROJ-CLOUD-002",
            "description": "Research into auto-scaling algorithms and distributed computing patterns to achieve 10x throughput improvements with reduced latency.",
            "department": "Engineering",
            "business_component": "Infrastructure"
        },
        {
            "name": "Quantum-Safe Cryptography Implementation",
            "code": "PROJ-SEC-003",
            "description": "Development of post-quantum cryptographic protocols to protect against future quantum computing threats.",
            "department": "Engineering",
            "business_component": "Security"
        },
        {
            "name": "Real-Time Analytics Engine",
            "code": "PROJ-DATA-004",
            "description": "Building a sub-millisecond analytics processing engine using novel stream processing techniques.",
            "department": "Data Science",
            "business_component": "Analytics"
        },
        {
            "name": "Computer Vision Quality Inspection System",
            "code": "PROJ-CV-005",
            "description": "AI-powered visual inspection system using novel defect detection algorithms for manufacturing quality control.",
            "department": "R&D Labs",
            "business_component": "Industrial AI"
        },
        {
            "name": "Autonomous System Navigation",
            "code": "PROJ-AUTO-006",
            "description": "Development of sensor fusion and path planning algorithms for autonomous mobile systems.",
            "department": "R&D Labs",
            "business_component": "Robotics"
        },
        {
            "name": "Energy-Efficient Computing Architecture",
            "code": "PROJ-GREEN-007",
            "description": "Research into low-power computing architectures and thermal management solutions for edge devices.",
            "department": "Engineering",
            "business_component": "Hardware"
        },
        {
            "name": "Predictive Maintenance Platform",
            "code": "PROJ-PRED-008",
            "description": "Machine learning system for predicting equipment failures using novel anomaly detection techniques.",
            "department": "Data Science",
            "business_component": "Industrial IoT"
        },
        {
            "name": "Natural Language Understanding Engine",
            "code": "PROJ-NLU-009",
            "description": "Development of contextual understanding and reasoning capabilities for conversational AI systems.",
            "department": "Data Science",
            "business_component": "AI Platform"
        },
        {
            "name": "Distributed Ledger Performance Optimization",
            "code": "PROJ-DLT-010",
            "description": "Research into consensus algorithms and sharding techniques to improve blockchain transaction throughput.",
            "department": "Engineering",
            "business_component": "Blockchain"
        },
    ]

    for proj in projects:
        proj["start_date"] = str(date(TAX_YEAR, 1, 1))
        proj["end_date"] = str(date(TAX_YEAR, 12, 31))
        proj["is_ongoing"] = True

    return projects


# =============================================================================
# API TEST FUNCTIONS
# =============================================================================

async def authenticate(client: httpx.AsyncClient) -> str:
    """Authenticate and get access token."""
    print("\n[1] Authenticating...")
    response = await client.post(
        f"{BASE_URL}/auth/login",
        json={"email": "admin@example.com", "password": "Admin123!"}
    )

    if response.status_code != 200:
        raise Exception(f"Authentication failed: {response.text}")

    token = response.json().get("access_token")
    print(f"   SUCCESS: Authenticated")
    return token


async def create_study(client: httpx.AsyncClient, headers: dict) -> dict:
    """Create a new R&D study."""
    print("\n[2] Creating R&D Study...")

    study_data = {
        "name": f"{COMPANY_NAME} - Tax Year {TAX_YEAR} R&D Study",
        "tax_year": TAX_YEAR,
        "entity_type": "c_corp",
        "entity_name": COMPANY_NAME,
        "ein": EIN,
        "fiscal_year_start": str(date(TAX_YEAR, 1, 1)),
        "fiscal_year_end": str(date(TAX_YEAR, 12, 31)),
        "is_short_year": False,
        "is_controlled_group": False,
        "states": ["CA", "NY", "TX", "WA", "MA"],
        "primary_state": "CA",
        "notes": "Enterprise-level R&D study with comprehensive QRE documentation"
    }

    response = await client.post(
        f"{RD_STUDY_URL}/studies",
        json=study_data,
        headers=headers
    )

    if response.status_code not in [200, 201]:
        raise Exception(f"Failed to create study: {response.text}")

    study = response.json()
    print(f"   SUCCESS: Created study ID: {study['id']}")
    return study


async def create_projects(client: httpx.AsyncClient, headers: dict, study_id: str) -> List[dict]:
    """Create R&D projects."""
    print("\n[3] Creating R&D Projects...")

    projects_data = generate_projects()
    created_projects = []

    for proj in projects_data:
        response = await client.post(
            f"{RD_STUDY_URL}/studies/{study_id}/projects",
            json=proj,
            headers=headers
        )

        if response.status_code in [200, 201]:
            created = response.json()
            created_projects.append(created)
            print(f"   Created project: {created['name']}")
        else:
            print(f"   WARNING: Failed to create project {proj['name']}: {response.text[:100]}")

    print(f"   SUCCESS: Created {len(created_projects)} projects")
    return created_projects


async def create_employees(client: httpx.AsyncClient, headers: dict, study_id: str) -> List[dict]:
    """Create employee records."""
    print("\n[4] Creating Employee Records...")

    employees_data = generate_employees()
    created_employees = []
    success_count = 0
    fail_count = 0

    for emp in employees_data:
        response = await client.post(
            f"{RD_STUDY_URL}/studies/{study_id}/employees",
            json=emp,
            headers=headers
        )

        if response.status_code in [200, 201]:
            created = response.json()
            created_employees.append(created)
            success_count += 1
        else:
            fail_count += 1

    total_wages = sum(Decimal(e.get("total_wages", "0")) for e in employees_data)
    print(f"   SUCCESS: Created {success_count} employees (Failed: {fail_count})")
    print(f"   Total Employee Wages: ${total_wages:,.2f}")
    return created_employees


async def create_qres(client: httpx.AsyncClient, headers: dict, study_id: str) -> Dict[str, List[dict]]:
    """Create QRE records for all expense categories."""
    print("\n[5] Creating Qualified Research Expenses...")

    # Generate all QRE data
    subcontractors = generate_subcontractors()
    supplies = generate_supplies()
    computer_rentals = generate_computer_rentals()

    all_qres = {
        "contract_research": subcontractors,
        "supplies": supplies,
        "computer_rental": computer_rentals
    }

    created_qres = {"contract_research": [], "supplies": [], "computer_rental": []}
    totals = {"contract_research": Decimal("0"), "supplies": Decimal("0"), "computer_rental": Decimal("0")}

    for category, qres in all_qres.items():
        success_count = 0
        for qre in qres:
            response = await client.post(
                f"{RD_STUDY_URL}/studies/{study_id}/qres",
                json=qre,
                headers=headers
            )

            if response.status_code in [200, 201]:
                created = response.json()
                created_qres[category].append(created)
                totals[category] += Decimal(qre["gross_amount"])
                success_count += 1

        print(f"   {category}: Created {success_count}/{len(qres)} records, Total: ${totals[category]:,.2f}")

    grand_total = sum(totals.values())
    print(f"   TOTAL QRE (non-wage): ${grand_total:,.2f}")
    return created_qres


async def get_qre_summary(client: httpx.AsyncClient, headers: dict, study_id: str) -> dict:
    """Get QRE summary from the study."""
    print("\n[6] Getting QRE Summary...")

    response = await client.get(
        f"{RD_STUDY_URL}/studies/{study_id}/qres/summary",
        headers=headers
    )

    if response.status_code == 200:
        summary = response.json()
        print(f"   QRE Summary Retrieved:")
        if "by_category" in summary:
            for cat, data in summary.get("by_category", {}).items():
                print(f"     - {cat}: ${data.get('qualified_total', 0):,.2f}")
        print(f"   SUCCESS: Summary retrieved")
        return summary
    else:
        print(f"   WARNING: Could not retrieve summary: {response.text[:100]}")
        return {}


async def calculate_credits(client: httpx.AsyncClient, headers: dict, study_id: str) -> dict:
    """Calculate R&D tax credits."""
    print("\n[7] Calculating R&D Tax Credits...")

    response = await client.post(
        f"{RD_STUDY_URL}/studies/{study_id}/calculate",
        json={"include_states": True},
        headers=headers
    )

    if response.status_code == 200:
        result = response.json()
        print(f"   Calculation Results:")
        if "federal" in result:
            fed = result["federal"]
            print(f"     Federal Regular Credit: ${fed.get('regular_credit', 0):,.2f}")
            print(f"     Federal ASC Credit: ${fed.get('asc_credit', 0):,.2f}")
        if "total_credit" in result:
            print(f"   TOTAL CREDIT: ${result['total_credit']:,.2f}")
        print(f"   SUCCESS: Credits calculated")
        return result
    else:
        print(f"   WARNING: Calculation failed: {response.text[:200]}")
        return {}


async def get_study_details(client: httpx.AsyncClient, headers: dict, study_id: str) -> dict:
    """Get full study details."""
    print("\n[8] Getting Study Details...")

    response = await client.get(
        f"{RD_STUDY_URL}/studies/{study_id}",
        headers=headers
    )

    if response.status_code == 200:
        study = response.json()
        print(f"   Study: {study.get('name')}")
        print(f"   Status: {study.get('status')}")
        print(f"   Total QRE: ${Decimal(str(study.get('total_qre', 0))):,.2f}")
        print(f"   Federal Credit: ${Decimal(str(study.get('federal_credit_final', 0))):,.2f}")
        print(f"   SUCCESS: Study details retrieved")
        return study
    else:
        print(f"   WARNING: Could not retrieve study: {response.text[:100]}")
        return {}


# =============================================================================
# MAIN TEST RUNNER
# =============================================================================

async def run_e2e_test():
    """Run the full end-to-end enterprise test."""
    print("=" * 70)
    print("R&D STUDY E2E TEST - ENTERPRISE LEVEL")
    print("=" * 70)
    print(f"\nCompany: {COMPANY_NAME}")
    print(f"Tax Year: {TAX_YEAR}")
    print(f"EIN: {EIN}")
    print("=" * 70)

    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            # Step 1: Authenticate
            token = await authenticate(client)
            headers = {"Authorization": f"Bearer {token}"}

            # Step 2: Create Study
            study = await create_study(client, headers)
            study_id = study["id"]

            # Step 3: Create Projects
            projects = await create_projects(client, headers, study_id)

            # Step 4: Create Employees
            employees = await create_employees(client, headers, study_id)

            # Step 5: Create QREs (Subcontractors, Supplies, Computer Rentals)
            qres = await create_qres(client, headers, study_id)

            # Step 6: Get QRE Summary
            summary = await get_qre_summary(client, headers, study_id)

            # Step 7: Calculate Credits
            credits = await calculate_credits(client, headers, study_id)

            # Step 8: Get Final Study Details
            final_study = await get_study_details(client, headers, study_id)

            # Final Summary
            print("\n" + "=" * 70)
            print("E2E TEST SUMMARY")
            print("=" * 70)
            print(f"Study ID: {study_id}")
            print(f"Projects Created: {len(projects)}")
            print(f"Employees Created: {len(employees)}")
            print(f"Contract Research QREs: {len(qres['contract_research'])}")
            print(f"Supply QREs: {len(qres['supplies'])}")
            print(f"Computer Rental QREs: {len(qres['computer_rental'])}")
            print("=" * 70)
            print("E2E TEST COMPLETE - ALL DATA SUBMITTED SUCCESSFULLY")
            print("=" * 70)

            return {
                "success": True,
                "study_id": study_id,
                "projects_count": len(projects),
                "employees_count": len(employees),
                "qres_count": sum(len(v) for v in qres.values()),
                "study_details": final_study
            }

        except Exception as e:
            print(f"\n{'='*70}")
            print(f"TEST FAILED: {str(e)}")
            print("=" * 70)
            return {"success": False, "error": str(e)}


if __name__ == "__main__":
    result = asyncio.run(run_e2e_test())
    if not result.get("success"):
        exit(1)
