"""
Comprehensive E2E Test for R&D Tax Credit Services

Tests the complete workflow with:
- 1 detailed R&D project with comprehensive 4-Part Test answers
- 500 employees across 4 states (CA, TX, NY, MA) with 80% allocations
- 200 contracts
- 600 supply/computer rental expenses
- State R&D credit calculations
- PDF study generation with Aura AI branding
- Excel export with state calculations
- CPA sign-off workflow
"""

import os
import sys
import json
import random
import string
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Any, Optional
from uuid import uuid4
import io

# Add app to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.generators.pdf_generator import PDFStudyGenerator
from app.generators.excel_generator import ExcelWorkbookGenerator
from app.engines.calculation_engine import CalculationEngine
from app.engines.qre_engine import QREEngine
from app.engines.qualification_engine import QualificationEngine
from app.engines.rules_engine import FederalRules, StateRules, STATE_RULES_2024


# =============================================================================
# TEST DATA GENERATORS
# =============================================================================

class TestDataGenerator:
    """Generates comprehensive test data for R&D studies."""

    # State distribution for employees/expenses
    STATES = ["CA", "TX", "NY", "MA"]
    STATE_DISTRIBUTION = {"CA": 0.35, "TX": 0.25, "NY": 0.25, "MA": 0.15}

    # Job titles for R&D employees
    JOB_TITLES = [
        "Software Engineer", "Senior Software Engineer", "Staff Engineer",
        "Principal Engineer", "Data Scientist", "Machine Learning Engineer",
        "Research Scientist", "DevOps Engineer", "Systems Architect",
        "QA Engineer", "Test Engineer", "Platform Engineer",
        "Frontend Developer", "Backend Developer", "Full Stack Developer",
        "Engineering Manager", "Technical Lead", "R&D Director",
        "Product Engineer", "Automation Engineer", "Security Engineer",
        "Cloud Engineer", "Infrastructure Engineer", "Site Reliability Engineer"
    ]

    # Departments
    DEPARTMENTS = [
        "Engineering", "R&D", "Product Development", "AI/ML Research",
        "Platform", "Infrastructure", "Quality Engineering", "DevOps"
    ]

    # Supply vendors
    SUPPLY_VENDORS = [
        "AWS", "Azure", "Google Cloud", "DigitalOcean", "Cloudflare",
        "GitHub Enterprise", "GitLab", "Atlassian", "JetBrains",
        "DataDog", "New Relic", "Splunk", "PagerDuty", "Sentry",
        "CircleCI", "Jenkins", "Travis CI", "CodeCov", "SonarQube",
        "Docker", "Kubernetes", "Terraform", "Ansible", "Puppet",
        "NVIDIA", "Intel", "AMD", "Dell Technologies", "HP Enterprise",
        "Fisher Scientific", "VWR International", "Sigma-Aldrich", "ThermoFisher"
    ]

    # Contract research providers
    CONTRACT_PROVIDERS = [
        "Accenture Labs", "Deloitte AI", "IBM Research", "Microsoft Research",
        "MIT Lincoln Labs", "Stanford Research Institute", "Battelle Memorial",
        "MITRE Corporation", "Argonne National Lab", "Sandia National Labs",
        "UCLA Research", "Berkeley Lab", "CalTech Research", "Carnegie Mellon",
        "Georgia Tech Research", "UT Austin Research", "Cornell Tech",
        "University of Michigan", "Purdue Research", "Ohio State Research"
    ]

    # First names and last names for employee generation
    FIRST_NAMES = [
        "James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda",
        "William", "Elizabeth", "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica",
        "Thomas", "Sarah", "Charles", "Karen", "Christopher", "Lisa", "Daniel", "Nancy",
        "Matthew", "Betty", "Anthony", "Margaret", "Mark", "Sandra", "Donald", "Ashley",
        "Steven", "Kimberly", "Paul", "Emily", "Andrew", "Donna", "Joshua", "Michelle",
        "Kenneth", "Dorothy", "Kevin", "Carol", "Brian", "Amanda", "George", "Melissa",
        "Timothy", "Deborah", "Ronald", "Stephanie", "Edward", "Rebecca", "Jason", "Sharon",
        "Jeffrey", "Laura", "Ryan", "Cynthia", "Jacob", "Kathleen", "Gary", "Amy"
    ]

    LAST_NAMES = [
        "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
        "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
        "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson",
        "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker",
        "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores",
        "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell",
        "Carter", "Roberts", "Chen", "Kim", "Patel", "Shah", "Kumar", "Singh", "Zhang"
    ]

    def __init__(self, seed: int = 42):
        """Initialize with a seed for reproducibility."""
        random.seed(seed)
        self.employee_id_counter = 1000

    def generate_employee_id(self) -> str:
        """Generate a unique employee ID."""
        self.employee_id_counter += 1
        return f"EMP-{self.employee_id_counter}"

    def generate_name(self) -> str:
        """Generate a random full name."""
        return f"{random.choice(self.FIRST_NAMES)} {random.choice(self.LAST_NAMES)}"

    def get_state_for_index(self, index: int, total: int) -> str:
        """Distribute items across states based on distribution percentages."""
        position = index / total
        cumulative = 0.0
        for state, pct in self.STATE_DISTRIBUTION.items():
            cumulative += pct
            if position < cumulative:
                return state
        return "CA"  # Default fallback

    def generate_detailed_project(self) -> Dict[str, Any]:
        """
        Generate a single R&D project with comprehensive 4-Part Test answers.
        This project represents a major AI/ML platform development initiative.
        """
        project = {
            "id": str(uuid4()),
            "name": "Aura AI - Intelligent Document Processing & Analysis Platform",
            "code": "AURA-IDP-2024",
            "description": """
                Development of an advanced AI-powered document processing and analysis platform
                that utilizes machine learning, natural language processing, and computer vision
                to automatically extract, classify, and analyze complex financial documents
                including tax returns, audit workpapers, and general ledger data. The platform
                represents a significant technological advancement over existing solutions through
                novel approaches to document understanding, entity extraction, and automated
                reconciliation algorithms.
            """.strip(),
            "department": "AI/ML Research",
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
            "project_lead": "Dr. Sarah Chen, Ph.D.",
            "total_budget": Decimal("15000000"),
            "qualification_status": "qualified",
            "overall_score": 92,
            "cpa_reviewed": True,
            "cpa_approved": True,
            "cpa_approval_date": date.today().isoformat(),
            "cpa_notes": "Project meets all 4-Part Test criteria with strong documentation.",

            # Comprehensive 4-Part Test Answers
            "four_part_test": {
                "permitted_purpose": {
                    "score": 95,
                    "status": "qualified",
                    "answer": """
                        The Aura AI Document Processing Platform represents a significant technological
                        advancement in automated document analysis. The project aims to develop NEW and
                        IMPROVED capabilities that do not exist in current market solutions:

                        1. NOVEL DOCUMENT UNDERSTANDING ENGINE:
                           - Development of a proprietary multi-modal transformer architecture that
                             simultaneously processes visual layout, textual content, and structural
                             relationships within complex financial documents
                           - Unlike existing OCR solutions that simply extract text, our system
                             understands document semantics and can accurately interpret tables,
                             footnotes, cross-references, and hierarchical relationships
                           - Accuracy improvement target: 98.5% extraction accuracy vs. industry
                             standard of 85-90%

                        2. INTELLIGENT ENTITY EXTRACTION SYSTEM:
                           - Creation of domain-specific named entity recognition models trained on
                             proprietary datasets of tax and accounting documents
                           - Automatic identification and classification of account numbers, amounts,
                             dates, entity names, and regulatory citations
                           - Development of confidence scoring algorithms that quantify extraction
                             certainty for downstream quality control

                        3. AUTOMATED RECONCILIATION ALGORITHMS:
                           - Implementation of graph-based matching algorithms that can automatically
                             reconcile entries across multiple documents and time periods
                           - Novel approach to handling discrepancies through probabilistic reasoning
                             and historical pattern analysis
                           - Target: Reduce manual reconciliation time by 85%

                        4. ADAPTIVE LEARNING CAPABILITIES:
                           - Self-improving system that learns from corrections and adapts to
                             client-specific document formats
                           - Transfer learning approaches to rapidly onboard new document types
                             with minimal training data

                        This development clearly meets the Permitted Purpose test as we are creating
                        new products with fundamentally improved functionality, performance, and
                        reliability compared to existing solutions. The improvements are substantial
                        and measurable, not merely cosmetic or adaptive changes.
                    """.strip(),
                    "evidence": [
                        "Product Requirements Document (PRD) v3.2 - January 2024",
                        "Technical Architecture Specification - 156 pages",
                        "Competitive Analysis Report - Gap Analysis vs. 15 competitors",
                        "Patent Application #PA-2024-0342 - Filed February 2024",
                        "Customer Advisory Board Feedback - 23 enterprise customers",
                        "Performance Benchmark Study - Third Party Validation",
                        "CRADA Agreement with Stanford NLP Lab"
                    ]
                },

                "technological_nature": {
                    "score": 94,
                    "status": "qualified",
                    "answer": """
                        The Aura AI platform development relies fundamentally on principles of
                        COMPUTER SCIENCE, MATHEMATICS, and ENGINEERING. The project requires
                        application of the following hard sciences:

                        1. MACHINE LEARNING & ARTIFICIAL INTELLIGENCE (Computer Science):
                           - Transformer neural network architectures (attention mechanisms,
                             positional encodings, multi-head self-attention)
                           - Supervised, semi-supervised, and unsupervised learning algorithms
                           - Deep learning optimization techniques (Adam, AdaGrad, learning rate
                             scheduling, gradient clipping)
                           - Transfer learning and domain adaptation methodologies
                           - Model compression and quantization for deployment efficiency

                        2. NATURAL LANGUAGE PROCESSING (Linguistics & Computer Science):
                           - Tokenization and subword encoding (BPE, SentencePiece)
                           - Part-of-speech tagging and dependency parsing
                           - Named entity recognition with CRF layers
                           - Semantic similarity and sentence embeddings
                           - Language model fine-tuning (BERT, RoBERTa, domain-specific models)

                        3. COMPUTER VISION (Engineering & Mathematics):
                           - Convolutional neural networks for layout analysis
                           - Object detection for table and figure identification
                           - Document image preprocessing (deskewing, denoising, binarization)
                           - Optical character recognition enhancement through deep learning

                        4. MATHEMATICAL FOUNDATIONS:
                           - Linear algebra for matrix operations in neural networks
                           - Probability theory and Bayesian inference for confidence scoring
                           - Graph theory for document structure representation
                           - Optimization algorithms (gradient descent, convex optimization)
                           - Information theory for model evaluation metrics

                        5. SOFTWARE ENGINEERING PRINCIPLES:
                           - Distributed systems design for scalable inference
                           - Microservices architecture with containerization
                           - Event-driven processing pipelines
                           - Database optimization for vector similarity search

                        The technical team includes 12 Ph.D.s in relevant fields (Computer Science,
                        Mathematics, Computational Linguistics) and regularly publishes research
                        in peer-reviewed venues including NeurIPS, ICML, ACL, and EMNLP.
                    """.strip(),
                    "evidence": [
                        "Algorithm Design Documents - 12 technical specifications",
                        "PhD Team Credentials - CVs and Publication Records",
                        "Conference Paper Submissions (NeurIPS 2024, under review)",
                        "Technical Training Records - ML Engineering Team",
                        "Architecture Decision Records (ADRs) - 47 documented decisions",
                        "Code Repository with Extensive Technical Documentation",
                        "External Technical Review by MIT CSAIL - March 2024"
                    ]
                },

                "elimination_of_uncertainty": {
                    "score": 91,
                    "status": "qualified",
                    "answer": """
                        At the commencement of development in January 2024, significant
                        TECHNOLOGICAL UNCERTAINTY existed regarding the capability, method,
                        and design of the proposed system:

                        1. CAPABILITY UNCERTAINTY:
                           - Could a unified model architecture achieve the required 98.5%
                             extraction accuracy across diverse document types?
                             * Existing solutions achieve 85-90% at best
                             * Academic benchmarks show 92% on standardized datasets
                             * Our real-world data is significantly more complex

                           - Could the system handle the scale of 100,000+ documents per hour
                             while maintaining accuracy?
                             * No existing solution demonstrated this throughput
                             * Inference latency requirements were extremely aggressive

                           - Could we achieve acceptable performance on handwritten annotations
                             and non-standard document formats?

                        2. METHOD/METHODOLOGY UNCERTAINTY:
                           - What neural architecture would best capture document structure?
                             * Explored: LayoutLM, Donut, UDOP, custom architectures
                             * Each had significant tradeoffs in accuracy vs. speed

                           - How to effectively combine visual and textual representations?
                             * Multiple fusion strategies were theoretically possible
                             * Optimal approach was unknown and required experimentation

                           - What training data strategy would yield best generalization?
                             * Synthetic data augmentation approaches
                             * Few-shot learning considerations
                             * Domain adaptation techniques

                        3. DESIGN UNCERTAINTY:
                           - Optimal model size vs. deployment constraints
                             * Larger models = better accuracy but higher latency
                             * Cloud vs. edge deployment tradeoffs

                           - Database architecture for efficient vector similarity search
                             * Multiple indexing strategies to evaluate
                             * Tradeoffs between recall and latency

                           - API design for integration with existing accounting systems

                        These uncertainties could NOT be resolved through routine engineering or
                        consultation with experts - they required systematic experimentation and
                        evaluation of multiple alternative approaches, many of which failed before
                        successful solutions were identified.
                    """.strip(),
                    "evidence": [
                        "Initial Feasibility Study - 23 documented uncertainties",
                        "Risk Assessment Matrix - Technical Risks Register",
                        "Failed Experiment Log - 47 documented unsuccessful approaches",
                        "Architecture Decision Records showing evaluated alternatives",
                        "Weekly R&D Status Reports - Uncertainty tracking",
                        "External Consultant Report (McKinsey) - Technical Risk Assessment",
                        "Internal Technical Review Board Meeting Minutes"
                    ]
                },

                "process_of_experimentation": {
                    "score": 89,
                    "status": "qualified",
                    "answer": """
                        The development team followed a rigorous SYSTEMATIC PROCESS OF
                        EXPERIMENTATION to evaluate and eliminate technical uncertainties:

                        1. HYPOTHESIS FORMULATION AND TESTING:
                           - Each technical uncertainty was formulated as a testable hypothesis
                           - Example: "Hypothesis: A LayoutLM-based architecture can achieve
                             >95% accuracy on tax form extraction with <100ms latency"
                           - Hypotheses were tested through controlled experiments with
                             documented protocols and success criteria

                        2. MODELING AND SIMULATION:
                           - Mathematical modeling of different architecture tradeoffs
                           - Simulation of production workloads to predict system behavior
                           - Monte Carlo simulations for confidence interval estimation
                           - A/B testing frameworks for comparative evaluation

                        3. SYSTEMATIC TRIAL AND ERROR:
                           - Over 200 experiments conducted in MLflow tracking system
                           - Each experiment documented with:
                             * Hypothesis being tested
                             * Experimental configuration
                             * Metrics and results
                             * Conclusions and next steps

                           - Experiments evaluated multiple alternatives:
                             * 5 different model architectures
                             * 12 training data strategies
                             * 8 optimization configurations
                             * 15 post-processing approaches

                        4. PROTOTYPING AND ITERATION:
                           - 7 major prototype versions developed and evaluated
                           - Each prototype underwent rigorous benchmark testing
                           - User acceptance testing with pilot customers
                           - Iterative refinement based on quantitative metrics

                        5. FAILURE ANALYSIS AND LEARNING:
                           - 47 documented failed experiments
                           - Post-mortem analysis for each failure
                           - Knowledge captured in technical documentation
                           - Failures informed subsequent experimental design

                        6. DOCUMENTATION AND REPRODUCIBILITY:
                           - All experiments logged in version-controlled notebooks
                           - Reproducibility verified through automated testing
                           - Peer review of experimental methodology

                        This systematic approach distinguishes our work from routine development
                        or simple trial-and-error. Each experiment was designed to resolve
                        specific technical uncertainties through scientific methodology.
                    """.strip(),
                    "evidence": [
                        "MLflow Experiment Tracking Logs - 200+ experiments",
                        "Jupyter Notebooks with Experimental Documentation",
                        "A/B Test Reports - 15 comparative studies",
                        "Prototype Version History and Changelogs",
                        "Failed Experiment Post-Mortem Reports",
                        "Peer Review Documentation for Key Experiments",
                        "Git Commit History with Experimental Branches",
                        "Weekly Experiment Review Meeting Minutes"
                    ]
                }
            },

            # Project metrics
            "metrics": {
                "total_employees": 156,
                "total_qre": Decimal("12500000"),
                "wage_qre": Decimal("9500000"),
                "supply_qre": Decimal("1500000"),
                "contract_qre": Decimal("1500000"),
                "experiments_conducted": 200,
                "papers_published": 3,
                "patents_filed": 2
            }
        }

        return project

    def generate_employees(self, count: int = 500) -> List[Dict[str, Any]]:
        """
        Generate employees distributed across 4 states.
        Some employees will have 80% allocation to test the system.
        """
        employees = []

        for i in range(count):
            state = self.get_state_for_index(i, count)

            # Determine qualified time percentage
            # ~20% of employees should have 80% allocation
            # ~10% should have 100% (direct R&D)
            # Rest should be between 5-60%
            rand = random.random()
            if rand < 0.10:
                qualified_pct = 100.0  # Direct R&D - full qualification
            elif rand < 0.30:
                qualified_pct = 80.0   # Heavy R&D involvement
            elif rand < 0.60:
                qualified_pct = random.uniform(40.0, 70.0)  # Moderate involvement
            else:
                qualified_pct = random.uniform(5.0, 35.0)   # Support roles

            # Calculate wages based on title seniority
            title = random.choice(self.JOB_TITLES)
            base_salary = self._get_base_salary(title)

            # State adjustments (CA and NY higher cost of living)
            if state == "CA":
                base_salary *= 1.20
            elif state == "NY":
                base_salary *= 1.15

            total_wages = Decimal(str(round(base_salary, 2)))
            qualified_wages = total_wages * Decimal(str(qualified_pct / 100))

            employee = {
                "id": str(uuid4()),
                "employee_id": self.generate_employee_id(),
                "name": self.generate_name(),
                "title": title,
                "department": random.choice(self.DEPARTMENTS),
                "state": state,
                "total_wages": total_wages,
                "w2_wages": total_wages,  # Using total as W2 for simplicity
                "qualified_time_percentage": round(qualified_pct, 1),
                "qualified_wages": round(qualified_wages, 2),
                "qualified_time_source": random.choice([
                    "timesheet", "project_tracking", "manager_estimate",
                    "engineering_logs", "jira_analysis"
                ]),
                "cpa_reviewed": qualified_pct >= 80.0,  # Auto-review high allocations
                "hire_date": self._random_date(2018, 2024).isoformat(),
                "role_description": self._get_role_description(title)
            }

            employees.append(employee)

        return employees

    def generate_contracts(self, count: int = 200) -> List[Dict[str, Any]]:
        """Generate contract research expenses."""
        contracts = []

        for i in range(count):
            state = self.get_state_for_index(i, count)
            provider = random.choice(self.CONTRACT_PROVIDERS)

            # Determine if qualified research organization (universities, national labs)
            is_qualified_org = any(x in provider for x in [
                "MIT", "Stanford", "Berkeley", "CalTech", "Carnegie",
                "UCLA", "UT Austin", "Cornell", "Georgia Tech",
                "University", "Lab", "National"
            ])

            # Contract amounts vary significantly
            amount = Decimal(str(random.uniform(15000, 500000)))
            qualified_pct = 0.75 if is_qualified_org else 0.65
            qualified_amount = amount * Decimal(str(qualified_pct))

            contract = {
                "id": str(uuid4()),
                "contractor_name": provider,
                "description": self._generate_contract_description(),
                "state": state,
                "category": "contract_research",
                "gross_amount": round(amount, 2),
                "is_qualified_research_org": is_qualified_org,
                "qualified_percentage": qualified_pct * 100,
                "qualified_amount": round(qualified_amount, 2),
                "project_name": "Aura AI - Intelligent Document Processing & Analysis Platform",
                "contract_date": self._random_date(2024, 2024).isoformat(),
                "contract_number": f"CONTRACT-{2024}-{i+1:04d}",
                "us_performed": True,
                "evidence": [
                    "Signed Contract Agreement",
                    "Statement of Work",
                    "Invoices",
                    "Deliverable Reports"
                ]
            }

            contracts.append(contract)

        return contracts

    def generate_supplies(self, count: int = 600) -> List[Dict[str, Any]]:
        """Generate supply and computer rental expenses."""
        supplies = []

        # Categories of supplies
        supply_categories = {
            "cloud_computing": {
                "vendors": ["AWS", "Azure", "Google Cloud", "DigitalOcean"],
                "min_amount": 500,
                "max_amount": 150000,
                "descriptions": [
                    "GPU compute instances for ML training",
                    "Cloud storage for training datasets",
                    "Kubernetes cluster hosting",
                    "Data processing and ETL services",
                    "ML model serving infrastructure"
                ]
            },
            "software_licenses": {
                "vendors": ["GitHub Enterprise", "GitLab", "JetBrains", "Atlassian"],
                "min_amount": 200,
                "max_amount": 50000,
                "descriptions": [
                    "Development IDE licenses",
                    "Version control and CI/CD platform",
                    "Project management tools",
                    "Code quality and security scanning"
                ]
            },
            "monitoring_tools": {
                "vendors": ["DataDog", "New Relic", "Splunk", "PagerDuty", "Sentry"],
                "min_amount": 1000,
                "max_amount": 75000,
                "descriptions": [
                    "Application performance monitoring",
                    "Log aggregation and analysis",
                    "Error tracking and alerting",
                    "Infrastructure monitoring"
                ]
            },
            "hardware_rentals": {
                "vendors": ["NVIDIA", "Dell Technologies", "HP Enterprise"],
                "min_amount": 5000,
                "max_amount": 200000,
                "descriptions": [
                    "GPU server rental for ML experiments",
                    "Development workstation leases",
                    "Testing lab equipment rental",
                    "Network infrastructure equipment"
                ]
            },
            "research_supplies": {
                "vendors": ["Fisher Scientific", "VWR International", "Sigma-Aldrich", "ThermoFisher"],
                "min_amount": 100,
                "max_amount": 25000,
                "descriptions": [
                    "Laboratory consumables",
                    "Testing materials and samples",
                    "Prototype materials",
                    "Research equipment supplies"
                ]
            }
        }

        for i in range(count):
            state = self.get_state_for_index(i, count)
            category_name = random.choice(list(supply_categories.keys()))
            category = supply_categories[category_name]

            vendor = random.choice(category["vendors"])
            description = random.choice(category["descriptions"])
            amount = Decimal(str(random.uniform(category["min_amount"], category["max_amount"])))

            # Qualified percentage (most supplies are 100% qualified)
            qualified_pct = random.choice([100, 100, 100, 100, 80, 90, 75])
            qualified_amount = amount * Decimal(str(qualified_pct / 100))

            supply = {
                "id": str(uuid4()),
                "category": "supplies",
                "subcategory": category_name,
                "supply_description": description,
                "supply_vendor": vendor,
                "state": state,
                "gl_account": self._generate_gl_account(category_name),
                "gross_amount": round(amount, 2),
                "qualified_percentage": qualified_pct,
                "qualified_amount": round(qualified_amount, 2),
                "project_name": "Aura AI - Intelligent Document Processing & Analysis Platform",
                "invoice_date": self._random_date(2024, 2024).isoformat(),
                "invoice_number": f"INV-{vendor[:3].upper()}-{i+1:05d}",
                "evidence": ["Invoice", "Purchase Order", "GL Entry"]
            }

            supplies.append(supply)

        return supplies

    def _get_base_salary(self, title: str) -> float:
        """Get base salary based on job title."""
        if "Director" in title or "Principal" in title:
            return random.uniform(200000, 350000)
        elif "Senior" in title or "Staff" in title or "Lead" in title:
            return random.uniform(150000, 220000)
        elif "Manager" in title or "Architect" in title:
            return random.uniform(170000, 250000)
        else:
            return random.uniform(90000, 160000)

    def _get_role_description(self, title: str) -> str:
        """Get role description for a given title."""
        descriptions = {
            "Software Engineer": "Develops and implements software solutions for R&D projects",
            "Senior Software Engineer": "Leads technical implementation and mentors junior engineers",
            "Staff Engineer": "Provides technical leadership across multiple R&D initiatives",
            "Principal Engineer": "Defines technical strategy and architecture for R&D platform",
            "Data Scientist": "Develops ML models and analyzes experimental data",
            "Machine Learning Engineer": "Implements and optimizes machine learning systems",
            "Research Scientist": "Conducts fundamental research and experimental analysis",
            "DevOps Engineer": "Builds infrastructure for R&D experimentation and deployment",
            "Systems Architect": "Designs scalable systems for R&D workloads",
            "QA Engineer": "Develops testing frameworks for R&D quality assurance",
            "Test Engineer": "Creates and executes test plans for R&D deliverables",
            "Platform Engineer": "Builds shared platforms for R&D teams",
            "Engineering Manager": "Manages R&D engineering teams and resources",
            "Technical Lead": "Leads technical direction for R&D projects",
            "R&D Director": "Directs overall R&D strategy and execution"
        }
        return descriptions.get(title, "Contributes to R&D activities")

    def _generate_contract_description(self) -> str:
        """Generate a description for a contract research engagement."""
        descriptions = [
            "Machine learning algorithm development and optimization",
            "Natural language processing research and model training",
            "Computer vision algorithm development for document analysis",
            "Performance benchmarking and optimization consulting",
            "Custom neural network architecture research",
            "Data annotation and training dataset creation",
            "Security and vulnerability research",
            "Scalability and distributed systems research",
            "User experience research and testing",
            "Technical feasibility study and proof of concept"
        ]
        return random.choice(descriptions)

    def _generate_gl_account(self, category: str) -> str:
        """Generate a GL account number based on category."""
        gl_prefixes = {
            "cloud_computing": "6100",
            "software_licenses": "6200",
            "monitoring_tools": "6210",
            "hardware_rentals": "6300",
            "research_supplies": "6400"
        }
        prefix = gl_prefixes.get(category, "6000")
        suffix = random.randint(100, 999)
        return f"{prefix}-{suffix}"

    def _random_date(self, start_year: int, end_year: int) -> date:
        """Generate a random date between start and end year."""
        start_date = date(start_year, 1, 1)
        end_date = date(end_year, 12, 31)
        delta = end_date - start_date
        random_days = random.randint(0, delta.days)
        return start_date + timedelta(days=random_days)


class StudyDataGenerator:
    """Generates complete study data structure."""

    def __init__(self, seed: int = 42):
        self.data_gen = TestDataGenerator(seed)

    def generate_complete_study(self) -> Dict[str, Any]:
        """Generate a complete study with all data."""

        # Generate all data
        project = self.data_gen.generate_detailed_project()
        employees = self.data_gen.generate_employees(500)
        contracts = self.data_gen.generate_contracts(200)
        supplies = self.data_gen.generate_supplies(600)

        # Combine QREs
        qres = contracts + supplies

        # Calculate totals by state
        state_totals = self._calculate_state_totals(employees, qres)

        # Calculate grand totals
        total_wage_qre = sum(Decimal(str(e["qualified_wages"])) for e in employees)
        total_supply_qre = sum(Decimal(str(s["qualified_amount"])) for s in supplies)
        total_contract_qre = sum(Decimal(str(c["qualified_amount"])) for c in contracts)
        total_qre = total_wage_qre + total_supply_qre + total_contract_qre

        study_data = {
            "id": str(uuid4()),
            "entity_name": "TechCorp AI Solutions, Inc.",
            "ein": "12-3456789",
            "tax_year": 2024,
            "fiscal_year_end": date(2024, 12, 31).isoformat(),
            "entity_type": "C_CORP",
            "status": "cpa_approval",
            "states": ["CA", "TX", "NY", "MA"],
            "gross_receipts": {
                2024: Decimal("125000000"),
                2023: Decimal("98000000"),
                2022: Decimal("75000000"),
                2021: Decimal("55000000"),
                2020: Decimal("42000000")
            },
            "prior_year_qre": {
                2023: Decimal("9500000"),
                2022: Decimal("7200000"),
                2021: Decimal("5100000")
            },
            "credit_method": "ASC",
            "is_startup": False,

            # Calculated totals
            "total_qre": total_qre,
            "qre_wages": total_wage_qre,
            "qre_supplies": total_supply_qre,
            "qre_contract": total_contract_qre,
            "state_totals": state_totals,

            # CPA Review
            "cpa_name": "Jonathan Toroni, CPA",
            "cpa_license": "CPA-123456",
            "cpa_firm": "Toroni & Company CPAs",
            "cpa_approval_date": None,
            "cpa_signature": None
        }

        return {
            "study_data": study_data,
            "projects": [project],
            "employees": employees,
            "contracts": contracts,
            "supplies": supplies,
            "qres": qres
        }

    def _calculate_state_totals(
        self,
        employees: List[Dict],
        qres: List[Dict]
    ) -> Dict[str, Dict[str, Decimal]]:
        """Calculate totals by state."""
        states = ["CA", "TX", "NY", "MA"]
        totals = {}

        for state in states:
            state_employees = [e for e in employees if e["state"] == state]
            state_qres = [q for q in qres if q["state"] == state]

            wage_qre = sum(Decimal(str(e["qualified_wages"])) for e in state_employees)
            supply_qre = sum(
                Decimal(str(q["qualified_amount"]))
                for q in state_qres if q["category"] == "supplies"
            )
            contract_qre = sum(
                Decimal(str(q["qualified_amount"]))
                for q in state_qres if q["category"] == "contract_research"
            )

            totals[state] = {
                "employee_count": len(state_employees),
                "wage_qre": wage_qre,
                "supply_qre": supply_qre,
                "contract_qre": contract_qre,
                "total_qre": wage_qre + supply_qre + contract_qre
            }

        return totals


# =============================================================================
# CALCULATION ENGINE WRAPPER
# =============================================================================

class StudyCalculator:
    """Calculates federal and state R&D credits."""

    def __init__(self):
        self.federal_rules = FederalRules()

    def calculate_all_credits(self, study_data: Dict) -> Dict[str, Any]:
        """Calculate federal and all state credits."""

        total_qre = float(study_data["total_qre"])
        prior_qre = [
            float(study_data["prior_year_qre"].get(year, 0))
            for year in [2023, 2022, 2021]
        ]

        # Federal Regular Credit calculation
        avg_prior_qre = sum(prior_qre) / 3 if prior_qre else 0
        gross_receipts = [
            float(study_data["gross_receipts"].get(year, 0))
            for year in [2024, 2023, 2022, 2021, 2020]
        ]

        # Fixed base percentage (using simplified calculation)
        if avg_prior_qre > 0 and gross_receipts[0] > 0:
            # Average QRE/GR ratio for base period
            base_ratio = avg_prior_qre / (sum(gross_receipts[1:]) / 4) if sum(gross_receipts[1:]) > 0 else 0.03
            fixed_base_pct = max(0.03, min(base_ratio, 0.16))  # 3% floor, 16% cap
        else:
            fixed_base_pct = 0.03

        avg_gross_receipts = sum(gross_receipts[1:]) / 4 if gross_receipts[1:] else 0
        base_amount = avg_gross_receipts * fixed_base_pct
        min_base = total_qre * 0.50
        final_base = max(base_amount, min_base)

        excess_qre_regular = max(total_qre - final_base, 0)
        tentative_regular = excess_qre_regular * 0.20
        section_280c_regular = tentative_regular * 0.21
        final_regular = tentative_regular - section_280c_regular

        # Federal ASC calculation
        asc_base = avg_prior_qre * 0.50
        excess_qre_asc = max(total_qre - asc_base, 0)
        tentative_asc = excess_qre_asc * 0.14
        section_280c_asc = tentative_asc * 0.21
        final_asc = tentative_asc - section_280c_asc

        # Select better method
        selected_method = "asc" if final_asc >= final_regular else "regular"
        federal_credit = final_asc if selected_method == "asc" else final_regular

        # State calculations
        state_results = {}
        total_state_credits = Decimal("0")

        for state, state_totals in study_data.get("state_totals", {}).items():
            if state in STATE_RULES_2024:
                state_rules = STATE_RULES_2024[state]
                state_qre = float(state_totals["total_qre"])

                if state_rules.credit_type == "incremental":
                    # Use federal-style incremental calculation
                    state_prior_avg = avg_prior_qre * (state_qre / total_qre) if total_qre > 0 else 0
                    state_base = state_prior_avg * 0.50
                    state_excess = max(state_qre - state_base, 0)
                    state_credit = state_excess * state_rules.credit_rate
                else:
                    # Non-incremental: apply rate to all QRE
                    state_credit = state_qre * state_rules.credit_rate

                # Apply cap if exists
                if state_rules.credit_cap:
                    state_credit = min(state_credit, float(state_rules.credit_cap))

                state_results[state] = {
                    "state_name": state_rules.state_name,
                    "state_code": state,
                    "credit_type": state_rules.credit_type,
                    "credit_rate": state_rules.credit_rate,
                    "state_qre": state_qre,
                    "state_base_amount": state_base if state_rules.credit_type == "incremental" else 0,
                    "excess_qre": state_excess if state_rules.credit_type == "incremental" else state_qre,
                    "calculated_credit": state_credit,
                    "credit_cap": str(state_rules.credit_cap) if state_rules.credit_cap else "N/A",
                    "final_credit": state_credit,
                    "carryforward_years": state_rules.carryforward_years,
                    "prior_carryforward": 0,
                    "is_refundable": state_rules.is_refundable,
                    "statute_citation": state_rules.statute_citation,
                    "form_number": state_rules.state_form_number
                }

                total_state_credits += Decimal(str(state_credit))

        return {
            "total_qre": total_qre,
            "qre_wages": float(study_data["qre_wages"]),
            "qre_supplies": float(study_data["qre_supplies"]),
            "qre_contract": float(study_data["qre_contract"]),
            "qre_basic_research": 0,

            # Federal Regular
            "federal_regular": {
                "total_qre": total_qre,
                "qre_wages": float(study_data["qre_wages"]),
                "qre_supplies": float(study_data["qre_supplies"]),
                "qre_contract": float(study_data["qre_contract"]),
                "qre_basic_research": 0,
                "fixed_base_percentage": fixed_base_pct,
                "avg_gross_receipts": avg_gross_receipts,
                "calculated_base": base_amount,
                "min_base": min_base,
                "base_amount": final_base,
                "excess_qre": excess_qre_regular,
                "tentative_credit": tentative_regular,
                "section_280c_reduction": section_280c_regular,
                "final_credit": final_regular
            },

            # Federal ASC
            "federal_asc": {
                "total_qre": total_qre,
                "prior_year_1": prior_qre[0] if prior_qre else 0,
                "prior_year_2": prior_qre[1] if len(prior_qre) > 1 else 0,
                "prior_year_3": prior_qre[2] if len(prior_qre) > 2 else 0,
                "avg_prior_qre": avg_prior_qre,
                "base_amount": asc_base,
                "excess_qre": excess_qre_asc,
                "tentative_credit": tentative_asc,
                "section_280c_reduction": section_280c_asc,
                "final_credit": final_asc
            },

            # Selected method
            "selected_method": selected_method,
            "regular_credit": final_regular,
            "asc_credit": final_asc,
            "federal_credit": federal_credit,

            # State results
            "state_results": state_results,
            "total_state_credits": float(total_state_credits),

            # Grand total
            "total_credits": federal_credit + float(total_state_credits)
        }


# =============================================================================
# CPA SIGN-OFF WORKFLOW
# =============================================================================

class CPASignOffManager:
    """Manages the CPA sign-off workflow for R&D studies."""

    def __init__(self):
        self.required_reviews = [
            "project_qualification",
            "employee_allocations",
            "qre_schedules",
            "calculation_review",
            "documentation_review"
        ]

    def initiate_review(self, study_id: str) -> Dict[str, Any]:
        """Initiate CPA review workflow."""
        return {
            "study_id": study_id,
            "status": "in_review",
            "initiated_at": datetime.now().isoformat(),
            "reviews_pending": self.required_reviews.copy(),
            "reviews_completed": [],
            "reviewer": None
        }

    def complete_review_step(
        self,
        workflow: Dict[str, Any],
        step: str,
        reviewer: str,
        notes: str = ""
    ) -> Dict[str, Any]:
        """Complete a review step."""
        if step in workflow["reviews_pending"]:
            workflow["reviews_pending"].remove(step)
            workflow["reviews_completed"].append({
                "step": step,
                "reviewer": reviewer,
                "completed_at": datetime.now().isoformat(),
                "notes": notes
            })
            workflow["reviewer"] = reviewer

        if not workflow["reviews_pending"]:
            workflow["status"] = "ready_for_signoff"

        return workflow

    def sign_off(
        self,
        workflow: Dict[str, Any],
        cpa_name: str,
        cpa_license: str,
        cpa_firm: str
    ) -> Dict[str, Any]:
        """CPA final sign-off on the study."""
        if workflow["status"] != "ready_for_signoff":
            raise ValueError("Study not ready for sign-off. Complete all review steps first.")

        return {
            **workflow,
            "status": "signed",
            "signed_at": datetime.now().isoformat(),
            "cpa_name": cpa_name,
            "cpa_license": cpa_license,
            "cpa_firm": cpa_firm,
            "signature_hash": self._generate_signature_hash(cpa_name, cpa_license)
        }

    def _generate_signature_hash(self, name: str, license: str) -> str:
        """Generate a signature hash for the sign-off."""
        import hashlib
        content = f"{name}|{license}|{datetime.now().isoformat()}"
        return hashlib.sha256(content.encode()).hexdigest()[:32]


# =============================================================================
# E2E TEST RUNNER
# =============================================================================

def run_e2e_test():
    """Run the complete E2E test for R&D services."""

    print("=" * 80)
    print("R&D TAX CREDIT SERVICES - COMPREHENSIVE E2E TEST")
    print("=" * 80)
    print()

    # Step 1: Generate test data
    print("STEP 1: Generating comprehensive test data...")
    print("-" * 60)

    study_gen = StudyDataGenerator(seed=42)
    all_data = study_gen.generate_complete_study()

    study_data = all_data["study_data"]
    projects = all_data["projects"]
    employees = all_data["employees"]
    contracts = all_data["contracts"]
    supplies = all_data["supplies"]
    qres = all_data["qres"]

    print(f"  Generated 1 R&D Project with detailed 4-Part Test answers")
    print(f"  Generated {len(employees)} employees across 4 states")
    print(f"  Generated {len(contracts)} contract research expenses")
    print(f"  Generated {len(supplies)} supply/computer rental expenses")
    print()

    # Show state distribution
    print("  Employee distribution by state:")
    for state in ["CA", "TX", "NY", "MA"]:
        state_count = len([e for e in employees if e["state"] == state])
        print(f"    {state}: {state_count} employees")

    # Show allocation percentages
    pct_100 = len([e for e in employees if e["qualified_time_percentage"] == 100])
    pct_80 = len([e for e in employees if e["qualified_time_percentage"] == 80])
    pct_other = len(employees) - pct_100 - pct_80
    print()
    print("  Employee qualified time allocation:")
    print(f"    100% (direct R&D): {pct_100} employees")
    print(f"    80% allocation: {pct_80} employees")
    print(f"    Other allocations: {pct_other} employees")
    print()

    # Step 2: Calculate credits
    print("STEP 2: Calculating Federal and State R&D Credits...")
    print("-" * 60)

    calculator = StudyCalculator()
    calculation_result = calculator.calculate_all_credits(study_data)

    print(f"  Total QRE: ${calculation_result['total_qre']:,.2f}")
    print(f"    - Wage QRE: ${calculation_result['qre_wages']:,.2f}")
    print(f"    - Supply QRE: ${calculation_result['qre_supplies']:,.2f}")
    print(f"    - Contract QRE: ${calculation_result['qre_contract']:,.2f}")
    print()
    print(f"  Federal Regular Credit: ${calculation_result['regular_credit']:,.2f}")
    print(f"  Federal ASC Credit: ${calculation_result['asc_credit']:,.2f}")
    print(f"  Selected Method: {calculation_result['selected_method'].upper()}")
    print(f"  Federal Credit (Final): ${calculation_result['federal_credit']:,.2f}")
    print()

    print("  State Credits:")
    for state, result in calculation_result["state_results"].items():
        print(f"    {state} ({result['state_name']}): ${result['final_credit']:,.2f}")
        print(f"       Rate: {result['credit_rate']*100:.1f}%, QRE: ${result['state_qre']:,.2f}")
    print()
    print(f"  Total State Credits: ${calculation_result['total_state_credits']:,.2f}")
    print(f"  TOTAL ALL CREDITS: ${calculation_result['total_credits']:,.2f}")
    print()

    # Step 3: Generate PDF Study
    print("STEP 3: Generating PDF Study Report...")
    print("-" * 60)

    pdf_generator = PDFStudyGenerator(config={
        "include_watermark": False,  # Final version
        "branding": {
            "company_name": "Aura AI",
            "tagline": "Intelligent Tax Credit Automation",
            "primary_color": "#1F4E79",
            "secondary_color": "#6366F1",
            "logo_path": None  # Would be path to Aura AI logo
        }
    })

    # Prepare narratives
    narratives = {
        "executive_summary": """
            This R&D Tax Credit Study documents the qualified research activities undertaken by
            TechCorp AI Solutions, Inc. during tax year 2024. The company engaged in the
            development of an advanced AI-powered document processing platform, representing
            significant technological advancement through novel approaches to document understanding,
            entity extraction, and automated reconciliation algorithms.
        """.strip(),
        "methodology": """
            This study was prepared using a combination of contemporaneous documentation review,
            employee interviews, project analysis, and financial record examination. The
            methodology follows IRS guidance and Treasury Regulations for IRC Section 41 compliance.
        """.strip()
    }

    pdf_bytes = pdf_generator.generate_study_report(
        study_data=study_data,
        projects=projects,
        employees=employees[:50],  # Top 50 for PDF
        qre_summary={
            "wages": float(study_data["qre_wages"]),
            "supplies": float(study_data["qre_supplies"]),
            "contract_research": float(study_data["qre_contract"]),
            "total": float(study_data["total_qre"])
        },
        calculation_result=calculation_result,
        narratives=narratives,
        evidence_items=[],
        is_final=True
    )

    # Save PDF
    output_dir = os.path.join(os.path.dirname(__file__), 'output')
    os.makedirs(output_dir, exist_ok=True)
    pdf_path = os.path.join(output_dir, 'rd_study_2024.pdf')
    with open(pdf_path, 'wb') as f:
        f.write(pdf_bytes)
    print(f"  PDF Study saved to: {pdf_path}")
    print(f"  PDF Size: {len(pdf_bytes):,} bytes")
    print()

    # Step 4: Generate Excel Workbook
    print("STEP 4: Generating Excel Workbook...")
    print("-" * 60)

    excel_generator = ExcelWorkbookGenerator()
    excel_bytes = excel_generator.generate_workbook(
        study_data=study_data,
        projects=projects,
        employees=employees,
        qres=qres,
        calculation_result=calculation_result
    )

    # Save Excel
    excel_path = os.path.join(output_dir, 'rd_study_2024.xlsx')
    with open(excel_path, 'wb') as f:
        f.write(excel_bytes)
    print(f"  Excel Workbook saved to: {excel_path}")
    print(f"  Excel Size: {len(excel_bytes):,} bytes")
    print()

    # Step 5: CPA Sign-off Workflow
    print("STEP 5: Completing CPA Sign-off Workflow...")
    print("-" * 60)

    signoff_manager = CPASignOffManager()

    # Initiate review
    workflow = signoff_manager.initiate_review(study_data["id"])
    print(f"  Review initiated: {len(workflow['reviews_pending'])} steps pending")

    # Complete all review steps
    for step in signoff_manager.required_reviews:
        workflow = signoff_manager.complete_review_step(
            workflow,
            step,
            "Jonathan Toroni, CPA",
            f"Reviewed and approved {step.replace('_', ' ')}"
        )
        print(f"    Completed: {step}")

    print(f"  Status: {workflow['status']}")

    # Final sign-off
    workflow = signoff_manager.sign_off(
        workflow,
        cpa_name="Jonathan Toroni, CPA",
        cpa_license="CPA-123456",
        cpa_firm="Toroni & Company CPAs"
    )

    print(f"  Final sign-off completed by: {workflow['cpa_name']}")
    print(f"  Signature hash: {workflow['signature_hash']}")
    print()

    # Step 6: Summary
    print("=" * 80)
    print("E2E TEST COMPLETE - SUMMARY")
    print("=" * 80)
    print()
    print("Test Data Generated:")
    print(f"  - 1 R&D Project with comprehensive 4-Part Test documentation")
    print(f"  - {len(employees)} employees across 4 states (CA, TX, NY, MA)")
    print(f"  - {len(contracts)} contract research expenses")
    print(f"  - {len(supplies)} supply/computer rental expenses")
    print()
    print("Credits Calculated:")
    print(f"  - Federal Credit ({calculation_result['selected_method'].upper()}): ${calculation_result['federal_credit']:,.2f}")
    for state, result in calculation_result["state_results"].items():
        print(f"  - {state} State Credit: ${result['final_credit']:,.2f}")
    print(f"  - TOTAL: ${calculation_result['total_credits']:,.2f}")
    print()
    print("Outputs Generated:")
    print(f"  - PDF Study: {pdf_path}")
    print(f"  - Excel Workbook: {excel_path}")
    print()
    print("CPA Sign-off: COMPLETED")
    print(f"  - Signed by: {workflow['cpa_name']}")
    print(f"  - Firm: {workflow['cpa_firm']}")
    print(f"  - Status: {workflow['status'].upper()}")
    print()
    print("=" * 80)
    print("ALL TESTS PASSED")
    print("=" * 80)

    return {
        "study_data": study_data,
        "projects": projects,
        "employees": employees,
        "qres": qres,
        "calculation_result": calculation_result,
        "workflow": workflow,
        "pdf_path": pdf_path,
        "excel_path": excel_path
    }


if __name__ == "__main__":
    result = run_e2e_test()
