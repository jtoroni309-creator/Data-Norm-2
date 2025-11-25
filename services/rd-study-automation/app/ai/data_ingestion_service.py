"""
AI Data Ingestion Service

Handles document processing with OCR, classification, table extraction,
entity resolution, normalization, and confidence scoring.
"""

import logging
import json
import re
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from decimal import Decimal
from uuid import UUID
from datetime import datetime, date
from enum import Enum

logger = logging.getLogger(__name__)


class DocumentCategory(str, Enum):
    """Document categories for classification."""
    GENERAL_LEDGER = "general_ledger"
    TRIAL_BALANCE = "trial_balance"
    PAYROLL = "payroll"
    TIME_TRACKING = "time_tracking"
    PROJECT_MANAGEMENT = "project_management"
    ENGINEERING_DOC = "engineering_doc"
    CONTRACT = "contract"
    INVOICE = "invoice"
    EMPLOYEE_LIST = "employee_list"
    GITHUB_DATA = "github_data"
    JIRA_DATA = "jira_data"
    INTERVIEW = "interview"
    OTHER = "other"


@dataclass
class ExtractionResult:
    """Result of data extraction from a document."""
    document_id: UUID
    document_type: DocumentCategory
    classification_confidence: float

    # Extracted entities
    employees: List[Dict[str, Any]]
    projects: List[Dict[str, Any]]
    expenses: List[Dict[str, Any]]
    time_entries: List[Dict[str, Any]]
    contracts: List[Dict[str, Any]]

    # Tables extracted
    tables: List[Dict[str, Any]]

    # Normalized data
    normalized_data: Dict[str, Any]

    # Quality metrics
    overall_confidence: float
    missing_fields: List[str]
    data_quality_issues: List[str]

    # Follow-up questions
    follow_up_questions: List[Dict[str, Any]]


@dataclass
class IngestionSummary:
    """Summary of data ingestion for a study."""
    study_id: UUID
    documents_processed: int
    documents_failed: int

    # Entity counts
    employees_found: int
    projects_found: int
    expenses_found: int
    time_entries_found: int
    contracts_found: int

    # Quality metrics
    overall_confidence: float
    data_coverage: float  # % of expected data found

    # Issues
    missing_data: List[Dict[str, Any]]
    follow_up_questions: List[Dict[str, Any]]
    warnings: List[str]

    # Processing time
    processing_time_seconds: float


class DataIngestionService:
    """
    AI-powered data ingestion service.

    Processes uploaded documents to extract:
    - Employee information and wages
    - Project data
    - Expense records (supplies, contracts)
    - Time tracking data
    - Technical documentation

    Uses AI for:
    - Document classification
    - Table extraction
    - Entity resolution (matching employees/projects across docs)
    - Data normalization
    - Missing data detection
    """

    def __init__(self, openai_client=None, config: Optional[Dict] = None):
        self.openai_client = openai_client
        self.config = config or {}
        self.classification_model = self.config.get("classification_model", "gpt-4-turbo-preview")
        self.extraction_model = self.config.get("extraction_model", "gpt-4-turbo-preview")

    async def process_document(
        self,
        document_id: UUID,
        file_content: bytes,
        filename: str,
        mime_type: str,
        ocr_text: Optional[str] = None,
        existing_entities: Optional[Dict[str, List]] = None
    ) -> ExtractionResult:
        """
        Process a single document and extract relevant data.

        Args:
            document_id: Document identifier
            file_content: Raw file content
            filename: Original filename
            mime_type: File MIME type
            ocr_text: Pre-processed OCR text (if available)
            existing_entities: Existing employees/projects for entity resolution

        Returns:
            Extraction result with all identified entities
        """
        logger.info(f"Processing document: {filename}")

        # Step 1: Classify document
        doc_type, classification_confidence = await self._classify_document(
            filename, mime_type, ocr_text
        )

        # Step 2: Extract tables (for structured documents)
        tables = []
        if doc_type in [
            DocumentCategory.GENERAL_LEDGER,
            DocumentCategory.TRIAL_BALANCE,
            DocumentCategory.PAYROLL,
            DocumentCategory.TIME_TRACKING
        ]:
            tables = await self._extract_tables(ocr_text or "", doc_type)

        # Step 3: Extract entities based on document type
        employees = []
        projects = []
        expenses = []
        time_entries = []
        contracts = []

        if doc_type == DocumentCategory.PAYROLL:
            employees = await self._extract_payroll_data(tables, ocr_text)
        elif doc_type == DocumentCategory.EMPLOYEE_LIST:
            employees = await self._extract_employee_list(tables, ocr_text)
        elif doc_type == DocumentCategory.GENERAL_LEDGER:
            expenses = await self._extract_gl_data(tables, ocr_text)
        elif doc_type == DocumentCategory.TIME_TRACKING:
            time_entries = await self._extract_time_data(tables, ocr_text)
        elif doc_type == DocumentCategory.PROJECT_MANAGEMENT:
            projects = await self._extract_project_data(ocr_text)
        elif doc_type == DocumentCategory.CONTRACT:
            contracts = await self._extract_contract_data(ocr_text)
        elif doc_type == DocumentCategory.GITHUB_DATA:
            projects, time_entries = await self._extract_github_data(ocr_text)
        elif doc_type == DocumentCategory.JIRA_DATA:
            projects, time_entries = await self._extract_jira_data(ocr_text)
        elif doc_type == DocumentCategory.ENGINEERING_DOC:
            projects = await self._extract_engineering_doc_data(ocr_text)

        # Step 4: Entity resolution (match to existing)
        if existing_entities:
            employees = self._resolve_employees(employees, existing_entities.get("employees", []))
            projects = self._resolve_projects(projects, existing_entities.get("projects", []))

        # Step 5: Normalize data
        normalized_data = self._normalize_extracted_data(
            employees, projects, expenses, time_entries, contracts
        )

        # Step 6: Identify missing data and generate follow-up questions
        missing_fields = self._identify_missing_fields(normalized_data, doc_type)
        follow_up_questions = self._generate_follow_up_questions(missing_fields, doc_type)

        # Step 7: Calculate confidence and quality metrics
        overall_confidence = self._calculate_extraction_confidence(
            classification_confidence,
            employees, projects, expenses, time_entries, contracts,
            missing_fields
        )

        data_quality_issues = self._identify_quality_issues(
            employees, projects, expenses, time_entries
        )

        return ExtractionResult(
            document_id=document_id,
            document_type=doc_type,
            classification_confidence=classification_confidence,
            employees=employees,
            projects=projects,
            expenses=expenses,
            time_entries=time_entries,
            contracts=contracts,
            tables=tables,
            normalized_data=normalized_data,
            overall_confidence=overall_confidence,
            missing_fields=missing_fields,
            data_quality_issues=data_quality_issues,
            follow_up_questions=follow_up_questions
        )

    async def _classify_document(
        self,
        filename: str,
        mime_type: str,
        text_content: Optional[str]
    ) -> Tuple[DocumentCategory, float]:
        """Classify document type using AI."""
        # Rule-based pre-classification from filename
        filename_lower = filename.lower()

        # Check filename patterns
        filename_patterns = {
            DocumentCategory.PAYROLL: ["payroll", "w2", "w-2", "wages", "salary"],
            DocumentCategory.GENERAL_LEDGER: ["gl", "general ledger", "ledger", "journal"],
            DocumentCategory.TRIAL_BALANCE: ["trial balance", "tb", "balance"],
            DocumentCategory.TIME_TRACKING: ["time", "timesheet", "hours", "timecard"],
            DocumentCategory.PROJECT_MANAGEMENT: ["project", "milestone", "task"],
            DocumentCategory.CONTRACT: ["contract", "agreement", "sow", "msa"],
            DocumentCategory.INVOICE: ["invoice", "bill", "receipt"],
            DocumentCategory.EMPLOYEE_LIST: ["employee", "roster", "headcount", "staff"],
            DocumentCategory.GITHUB_DATA: ["github", "commit", "repository", "pull request"],
            DocumentCategory.JIRA_DATA: ["jira", "sprint", "story", "epic"],
        }

        for category, patterns in filename_patterns.items():
            if any(p in filename_lower for p in patterns):
                return category, 0.85

        # If no filename match and we have text content, use AI
        if text_content and self.openai_client:
            try:
                classification = await self._ai_classify_document(text_content[:5000])
                return classification
            except Exception as e:
                logger.error(f"AI classification failed: {e}")

        # Default to OTHER with low confidence
        return DocumentCategory.OTHER, 0.30

    async def _ai_classify_document(
        self,
        text_sample: str
    ) -> Tuple[DocumentCategory, float]:
        """Use AI to classify document content."""
        prompt = f"""Classify this document into one of these categories:
- general_ledger: Financial accounting records, GL entries
- trial_balance: Trial balance reports
- payroll: Payroll records, W-2s, wage reports
- time_tracking: Timesheets, time tracking data
- project_management: Project plans, milestones, task lists
- engineering_doc: Technical specifications, design documents
- contract: Contracts, agreements, SOWs
- invoice: Vendor invoices, bills
- employee_list: Employee rosters, org charts
- github_data: GitHub commits, pull requests
- jira_data: Jira tickets, sprint data
- interview: Interview transcripts
- other: Cannot determine

Document text sample:
{text_sample}

Respond with JSON: {{"category": "category_name", "confidence": 0.0-1.0}}"""

        if self.openai_client:
            response = await self.openai_client.chat.completions.create(
                model=self.classification_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=100
            )

            try:
                result = json.loads(response.choices[0].message.content)
                category = DocumentCategory(result.get("category", "other"))
                confidence = float(result.get("confidence", 0.5))
                return category, confidence
            except (json.JSONDecodeError, ValueError):
                pass

        return DocumentCategory.OTHER, 0.30

    async def _extract_tables(
        self,
        text_content: str,
        doc_type: DocumentCategory
    ) -> List[Dict[str, Any]]:
        """Extract tabular data from document text."""
        tables = []

        # Look for common table patterns
        lines = text_content.split('\n')
        current_table = []
        in_table = False

        for line in lines:
            # Detect table rows (multiple columns separated by tabs or multiple spaces)
            if '\t' in line or re.search(r'\s{2,}', line):
                if not in_table:
                    in_table = True
                    current_table = []
                current_table.append(self._parse_table_row(line))
            else:
                if in_table and current_table:
                    if len(current_table) > 1:  # At least header + 1 row
                        tables.append({
                            "rows": current_table,
                            "headers": current_table[0] if current_table else [],
                            "row_count": len(current_table)
                        })
                    current_table = []
                    in_table = False

        # Don't forget the last table
        if current_table and len(current_table) > 1:
            tables.append({
                "rows": current_table,
                "headers": current_table[0] if current_table else [],
                "row_count": len(current_table)
            })

        return tables

    def _parse_table_row(self, line: str) -> List[str]:
        """Parse a single table row into cells."""
        # Try tab separation first
        if '\t' in line:
            return [cell.strip() for cell in line.split('\t')]

        # Fall back to multiple space separation
        cells = re.split(r'\s{2,}', line)
        return [cell.strip() for cell in cells if cell.strip()]

    async def _extract_payroll_data(
        self,
        tables: List[Dict],
        text_content: Optional[str]
    ) -> List[Dict[str, Any]]:
        """Extract employee wage data from payroll documents."""
        employees = []

        # Common payroll column headers
        name_columns = ["name", "employee", "employee name", "full name"]
        wage_columns = ["wages", "salary", "gross pay", "total wages", "w2 wages", "earnings"]
        id_columns = ["id", "employee id", "emp id", "ssn"]

        for table in tables:
            headers = [h.lower() for h in table.get("headers", [])]

            # Find relevant column indices
            name_idx = self._find_column_index(headers, name_columns)
            wage_idx = self._find_column_index(headers, wage_columns)
            id_idx = self._find_column_index(headers, id_columns)

            if name_idx is None:
                continue

            # Extract employee data from rows
            for row in table.get("rows", [])[1:]:  # Skip header row
                if len(row) > name_idx:
                    employee = {
                        "name": row[name_idx],
                        "source": "payroll"
                    }

                    if wage_idx is not None and len(row) > wage_idx:
                        employee["total_wages"] = self._parse_currency(row[wage_idx])

                    if id_idx is not None and len(row) > id_idx:
                        employee["employee_id"] = row[id_idx]

                    employees.append(employee)

        return employees

    async def _extract_employee_list(
        self,
        tables: List[Dict],
        text_content: Optional[str]
    ) -> List[Dict[str, Any]]:
        """Extract employee information from employee lists."""
        employees = []

        name_columns = ["name", "employee", "employee name", "full name"]
        title_columns = ["title", "job title", "position", "role"]
        dept_columns = ["department", "dept", "division", "group"]
        hire_columns = ["hire date", "start date", "hired"]

        for table in tables:
            headers = [h.lower() for h in table.get("headers", [])]

            name_idx = self._find_column_index(headers, name_columns)
            title_idx = self._find_column_index(headers, title_columns)
            dept_idx = self._find_column_index(headers, dept_columns)
            hire_idx = self._find_column_index(headers, hire_columns)

            if name_idx is None:
                continue

            for row in table.get("rows", [])[1:]:
                if len(row) > name_idx:
                    employee = {
                        "name": row[name_idx],
                        "source": "employee_list"
                    }

                    if title_idx is not None and len(row) > title_idx:
                        employee["title"] = row[title_idx]

                    if dept_idx is not None and len(row) > dept_idx:
                        employee["department"] = row[dept_idx]

                    if hire_idx is not None and len(row) > hire_idx:
                        employee["hire_date"] = self._parse_date(row[hire_idx])

                    employees.append(employee)

        return employees

    async def _extract_gl_data(
        self,
        tables: List[Dict],
        text_content: Optional[str]
    ) -> List[Dict[str, Any]]:
        """Extract expense data from general ledger."""
        expenses = []

        account_columns = ["account", "gl account", "account number", "acct"]
        desc_columns = ["description", "desc", "memo", "detail"]
        amount_columns = ["amount", "debit", "total", "balance"]
        vendor_columns = ["vendor", "payee", "supplier"]

        for table in tables:
            headers = [h.lower() for h in table.get("headers", [])]

            account_idx = self._find_column_index(headers, account_columns)
            desc_idx = self._find_column_index(headers, desc_columns)
            amount_idx = self._find_column_index(headers, amount_columns)
            vendor_idx = self._find_column_index(headers, vendor_columns)

            for row in table.get("rows", [])[1:]:
                if amount_idx is not None and len(row) > amount_idx:
                    expense = {
                        "amount": self._parse_currency(row[amount_idx]),
                        "source": "general_ledger"
                    }

                    if account_idx is not None and len(row) > account_idx:
                        expense["gl_account"] = row[account_idx]

                    if desc_idx is not None and len(row) > desc_idx:
                        expense["description"] = row[desc_idx]

                    if vendor_idx is not None and len(row) > vendor_idx:
                        expense["vendor"] = row[vendor_idx]

                    if expense.get("amount", 0) > 0:
                        expenses.append(expense)

        return expenses

    async def _extract_time_data(
        self,
        tables: List[Dict],
        text_content: Optional[str]
    ) -> List[Dict[str, Any]]:
        """Extract time tracking data."""
        time_entries = []

        employee_columns = ["employee", "name", "resource"]
        project_columns = ["project", "task", "activity", "job"]
        hours_columns = ["hours", "time", "duration", "qty"]

        for table in tables:
            headers = [h.lower() for h in table.get("headers", [])]

            emp_idx = self._find_column_index(headers, employee_columns)
            proj_idx = self._find_column_index(headers, project_columns)
            hours_idx = self._find_column_index(headers, hours_columns)

            for row in table.get("rows", [])[1:]:
                if hours_idx is not None and len(row) > hours_idx:
                    entry = {
                        "hours": self._parse_number(row[hours_idx]),
                        "source": "time_tracking"
                    }

                    if emp_idx is not None and len(row) > emp_idx:
                        entry["employee_name"] = row[emp_idx]

                    if proj_idx is not None and len(row) > proj_idx:
                        entry["project_name"] = row[proj_idx]

                    if entry.get("hours", 0) > 0:
                        time_entries.append(entry)

        return time_entries

    async def _extract_project_data(
        self,
        text_content: Optional[str]
    ) -> List[Dict[str, Any]]:
        """Extract project information from project documents."""
        projects = []

        if not text_content:
            return projects

        # Use AI to extract project information
        if self.openai_client:
            prompt = f"""Extract project information from this document.
Look for:
- Project names
- Project descriptions
- Technical objectives
- Technical challenges/uncertainties
- Experimentation activities

Document text:
{text_content[:8000]}

Return JSON array of projects with fields: name, description, objectives, challenges, activities"""

            try:
                response = await self.openai_client.chat.completions.create(
                    model=self.extraction_model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.1,
                    max_tokens=2000
                )

                result = json.loads(response.choices[0].message.content)
                if isinstance(result, list):
                    projects = result
            except Exception as e:
                logger.error(f"AI project extraction failed: {e}")

        return projects

    async def _extract_contract_data(
        self,
        text_content: Optional[str]
    ) -> List[Dict[str, Any]]:
        """Extract contract research information."""
        contracts = []

        if not text_content:
            return contracts

        if self.openai_client:
            prompt = f"""Extract contract research information from this document.
Look for:
- Contractor/vendor name
- Contract value/amount
- Scope of research work
- Whether research is performed in the US
- Whether contractor is a qualified research organization

Document text:
{text_content[:8000]}

Return JSON array of contracts with fields: contractor_name, amount, description, performed_in_us, is_qualified_org"""

            try:
                response = await self.openai_client.chat.completions.create(
                    model=self.extraction_model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.1,
                    max_tokens=1000
                )

                result = json.loads(response.choices[0].message.content)
                if isinstance(result, list):
                    contracts = result
            except Exception as e:
                logger.error(f"AI contract extraction failed: {e}")

        return contracts

    async def _extract_github_data(
        self,
        text_content: Optional[str]
    ) -> Tuple[List[Dict], List[Dict]]:
        """Extract project and time data from GitHub exports."""
        projects = []
        time_entries = []

        if not text_content:
            return projects, time_entries

        # Parse GitHub commit data
        commit_pattern = r'commit\s+([a-f0-9]+).*?Author:\s*([^<]+)'
        commits = re.findall(commit_pattern, text_content, re.IGNORECASE | re.DOTALL)

        for commit_hash, author in commits:
            time_entries.append({
                "employee_name": author.strip(),
                "activity": "development",
                "source": "github",
                "reference": commit_hash[:8]
            })

        # Extract repository/project names
        repo_pattern = r'repository[:\s]+([^\n]+)'
        repos = re.findall(repo_pattern, text_content, re.IGNORECASE)

        for repo in repos:
            projects.append({
                "name": repo.strip(),
                "source": "github",
                "type": "software_development"
            })

        return projects, time_entries

    async def _extract_jira_data(
        self,
        text_content: Optional[str]
    ) -> Tuple[List[Dict], List[Dict]]:
        """Extract project and time data from Jira exports."""
        projects = []
        time_entries = []

        if not text_content:
            return projects, time_entries

        # Parse Jira ticket patterns
        ticket_pattern = r'([A-Z]+-\d+)'
        tickets = set(re.findall(ticket_pattern, text_content))

        # Extract project codes from ticket prefixes
        project_codes = set(t.split('-')[0] for t in tickets)

        for code in project_codes:
            projects.append({
                "name": code,
                "source": "jira",
                "ticket_count": len([t for t in tickets if t.startswith(code)])
            })

        return projects, time_entries

    async def _extract_engineering_doc_data(
        self,
        text_content: Optional[str]
    ) -> List[Dict[str, Any]]:
        """Extract R&D relevant information from engineering documents."""
        projects = []

        if not text_content or not self.openai_client:
            return projects

        prompt = f"""Analyze this engineering document for R&D tax credit relevance.
Extract:
- Technical objectives being pursued
- Technological uncertainties being addressed
- Experimentation or testing activities
- Innovation beyond routine engineering

Document text:
{text_content[:8000]}

Return JSON with fields: objectives, uncertainties, experiments, innovation_summary"""

        try:
            response = await self.openai_client.chat.completions.create(
                model=self.extraction_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=1500
            )

            result = json.loads(response.choices[0].message.content)
            projects.append({
                "source": "engineering_doc",
                "rd_analysis": result
            })
        except Exception as e:
            logger.error(f"AI engineering doc extraction failed: {e}")

        return projects

    def _resolve_employees(
        self,
        new_employees: List[Dict],
        existing_employees: List[Dict]
    ) -> List[Dict]:
        """Match new employees to existing records."""
        for new_emp in new_employees:
            new_name = new_emp.get("name", "").lower().strip()

            for existing in existing_employees:
                existing_name = existing.get("name", "").lower().strip()

                # Check for name match
                if self._names_match(new_name, existing_name):
                    new_emp["matched_id"] = existing.get("id")
                    new_emp["match_confidence"] = 0.9
                    break

        return new_employees

    def _resolve_projects(
        self,
        new_projects: List[Dict],
        existing_projects: List[Dict]
    ) -> List[Dict]:
        """Match new projects to existing records."""
        for new_proj in new_projects:
            new_name = new_proj.get("name", "").lower().strip()

            for existing in existing_projects:
                existing_name = existing.get("name", "").lower().strip()

                if new_name == existing_name or new_name in existing_name or existing_name in new_name:
                    new_proj["matched_id"] = existing.get("id")
                    new_proj["match_confidence"] = 0.85
                    break

        return new_projects

    def _names_match(self, name1: str, name2: str) -> bool:
        """Check if two names likely refer to the same person."""
        if name1 == name2:
            return True

        # Check if one name contains the other
        if name1 in name2 or name2 in name1:
            return True

        # Check first and last name match
        parts1 = name1.split()
        parts2 = name2.split()

        if len(parts1) >= 2 and len(parts2) >= 2:
            # Check if first and last names match
            if parts1[0] == parts2[0] and parts1[-1] == parts2[-1]:
                return True

        return False

    def _normalize_extracted_data(
        self,
        employees: List[Dict],
        projects: List[Dict],
        expenses: List[Dict],
        time_entries: List[Dict],
        contracts: List[Dict]
    ) -> Dict[str, Any]:
        """Normalize all extracted data into standard format."""
        return {
            "employees": [
                {
                    "name": e.get("name", ""),
                    "employee_id": e.get("employee_id"),
                    "title": e.get("title"),
                    "department": e.get("department"),
                    "total_wages": e.get("total_wages"),
                    "hire_date": e.get("hire_date"),
                    "source": e.get("source"),
                    "matched_id": e.get("matched_id"),
                    "confidence": e.get("match_confidence", 0.5)
                }
                for e in employees
            ],
            "projects": [
                {
                    "name": p.get("name", ""),
                    "description": p.get("description"),
                    "objectives": p.get("objectives"),
                    "challenges": p.get("challenges"),
                    "source": p.get("source"),
                    "matched_id": p.get("matched_id")
                }
                for p in projects
            ],
            "expenses": [
                {
                    "description": ex.get("description"),
                    "amount": ex.get("amount"),
                    "gl_account": ex.get("gl_account"),
                    "vendor": ex.get("vendor"),
                    "source": ex.get("source")
                }
                for ex in expenses
            ],
            "time_entries": [
                {
                    "employee_name": t.get("employee_name"),
                    "project_name": t.get("project_name"),
                    "hours": t.get("hours"),
                    "source": t.get("source")
                }
                for t in time_entries
            ],
            "contracts": [
                {
                    "contractor_name": c.get("contractor_name"),
                    "amount": c.get("amount"),
                    "description": c.get("description"),
                    "performed_in_us": c.get("performed_in_us", True),
                    "is_qualified_org": c.get("is_qualified_org", False)
                }
                for c in contracts
            ]
        }

    def _identify_missing_fields(
        self,
        normalized_data: Dict,
        doc_type: DocumentCategory
    ) -> List[str]:
        """Identify missing required fields."""
        missing = []

        expected_fields = {
            DocumentCategory.PAYROLL: ["employees.name", "employees.total_wages"],
            DocumentCategory.EMPLOYEE_LIST: ["employees.name", "employees.title"],
            DocumentCategory.GENERAL_LEDGER: ["expenses.amount", "expenses.description"],
            DocumentCategory.TIME_TRACKING: ["time_entries.employee_name", "time_entries.hours"],
            DocumentCategory.CONTRACT: ["contracts.contractor_name", "contracts.amount"]
        }

        required = expected_fields.get(doc_type, [])

        for field in required:
            parts = field.split(".")
            data = normalized_data.get(parts[0], [])

            if not data:
                missing.append(field)
            elif parts[1]:
                # Check if any record has this field
                if not any(item.get(parts[1]) for item in data):
                    missing.append(field)

        return missing

    def _generate_follow_up_questions(
        self,
        missing_fields: List[str],
        doc_type: DocumentCategory
    ) -> List[Dict[str, Any]]:
        """Generate follow-up questions for missing data."""
        questions = []

        field_questions = {
            "employees.total_wages": {
                "question": "Please provide W-2 wage data for employees",
                "priority": "high",
                "category": "payroll"
            },
            "employees.title": {
                "question": "What are the job titles for each employee?",
                "priority": "medium",
                "category": "employee_info"
            },
            "time_entries.hours": {
                "question": "Can you provide time tracking data showing hours by project?",
                "priority": "high",
                "category": "time_tracking"
            },
            "contracts.amount": {
                "question": "What are the contract amounts for research agreements?",
                "priority": "high",
                "category": "contracts"
            }
        }

        for field in missing_fields:
            if field in field_questions:
                questions.append(field_questions[field])

        return questions

    def _calculate_extraction_confidence(
        self,
        classification_confidence: float,
        employees: List,
        projects: List,
        expenses: List,
        time_entries: List,
        contracts: List,
        missing_fields: List
    ) -> float:
        """Calculate overall extraction confidence."""
        base_confidence = classification_confidence

        # Boost for successful extractions
        extraction_count = sum([
            len(employees) > 0,
            len(projects) > 0,
            len(expenses) > 0,
            len(time_entries) > 0,
            len(contracts) > 0
        ])

        extraction_bonus = extraction_count * 0.05

        # Penalty for missing fields
        missing_penalty = len(missing_fields) * 0.10

        confidence = base_confidence + extraction_bonus - missing_penalty

        return max(0.1, min(0.95, confidence))

    def _identify_quality_issues(
        self,
        employees: List,
        projects: List,
        expenses: List,
        time_entries: List
    ) -> List[str]:
        """Identify data quality issues."""
        issues = []

        # Check for duplicate employees
        names = [e.get("name", "").lower() for e in employees]
        if len(names) != len(set(names)):
            issues.append("Possible duplicate employee records detected")

        # Check for outlier wages
        wages = [e.get("total_wages", 0) for e in employees if e.get("total_wages")]
        if wages:
            avg_wage = sum(wages) / len(wages)
            for i, w in enumerate(wages):
                if w > avg_wage * 5 or w < avg_wage * 0.1:
                    issues.append(f"Outlier wage value detected: ${w:,.2f}")

        # Check for negative amounts
        for ex in expenses:
            if ex.get("amount", 0) < 0:
                issues.append("Negative expense amount detected")

        return issues

    def _find_column_index(
        self,
        headers: List[str],
        column_names: List[str]
    ) -> Optional[int]:
        """Find column index matching any of the column names."""
        for i, header in enumerate(headers):
            for name in column_names:
                if name in header:
                    return i
        return None

    def _parse_currency(self, value: str) -> Decimal:
        """Parse currency string to Decimal."""
        if not value:
            return Decimal("0")

        # Remove currency symbols and commas
        cleaned = re.sub(r'[$,\s]', '', str(value))

        # Handle parentheses for negative
        if cleaned.startswith('(') and cleaned.endswith(')'):
            cleaned = '-' + cleaned[1:-1]

        try:
            return Decimal(cleaned)
        except Exception:
            return Decimal("0")

    def _parse_number(self, value: str) -> float:
        """Parse number string to float."""
        if not value:
            return 0.0

        cleaned = re.sub(r'[,\s]', '', str(value))

        try:
            return float(cleaned)
        except Exception:
            return 0.0

    def _parse_date(self, value: str) -> Optional[str]:
        """Parse date string to ISO format."""
        if not value:
            return None

        # Common date patterns
        patterns = [
            (r'(\d{1,2})/(\d{1,2})/(\d{4})', '%m/%d/%Y'),
            (r'(\d{4})-(\d{2})-(\d{2})', '%Y-%m-%d'),
            (r'(\d{1,2})-(\d{1,2})-(\d{4})', '%m-%d-%Y'),
        ]

        for pattern, fmt in patterns:
            if re.match(pattern, value):
                try:
                    parsed = datetime.strptime(value, fmt)
                    return parsed.date().isoformat()
                except Exception:
                    pass

        return None
