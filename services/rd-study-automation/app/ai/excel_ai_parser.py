"""
AI-Powered Excel Parser

Uses Claude AI to intelligently analyze spreadsheet data and automatically
map columns to the correct R&D study fields.
"""

import io
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from decimal import Decimal
from datetime import datetime
from enum import Enum

import pandas as pd
from openpyxl import load_workbook

logger = logging.getLogger(__name__)


class DataCategory(str, Enum):
    """Categories for imported data."""
    EMPLOYEES = "employees"
    PAYROLL = "payroll"
    PROJECTS = "projects"
    TIME_TRACKING = "time_tracking"
    SUPPLIES = "supplies"
    CONTRACTS = "contracts"
    GENERAL_LEDGER = "general_ledger"
    UNKNOWN = "unknown"


@dataclass
class ColumnMapping:
    """Mapping of source column to target field."""
    source_column: str
    target_field: str
    confidence: float
    data_type: str
    sample_values: List[Any]
    transformation: Optional[str] = None


@dataclass
class SheetAnalysis:
    """Analysis results for a single sheet."""
    sheet_name: str
    category: DataCategory
    category_confidence: float
    row_count: int
    column_mappings: List[ColumnMapping]
    data_quality_score: float
    issues: List[str]
    preview_data: List[Dict[str, Any]]


@dataclass
class ExcelAnalysisResult:
    """Complete analysis of an Excel file."""
    filename: str
    sheets: List[SheetAnalysis]
    overall_quality_score: float
    missing_data_types: List[str]
    recommendations: List[str]
    raw_data: Dict[str, pd.DataFrame]


class ExcelAIParser:
    """
    AI-powered Excel parser that intelligently maps spreadsheet data
    to R&D study data structures.

    Features:
    - Automatic column mapping using AI
    - Data category detection (payroll, projects, time tracking, etc.)
    - Data quality scoring
    - Missing data detection
    - Smart data transformations
    """

    # Known field patterns for R&D studies
    FIELD_PATTERNS = {
        "employees": {
            "name": ["name", "employee name", "full name", "emp name", "employee", "staff"],
            "employee_id": ["id", "employee id", "emp id", "emp #", "employee #", "ssn", "ein"],
            "title": ["title", "job title", "position", "role", "job"],
            "department": ["department", "dept", "division", "group", "team", "org"],
            "hire_date": ["hire date", "start date", "date hired", "employed since"],
            "email": ["email", "e-mail", "mail", "email address"],
        },
        "payroll": {
            "name": ["name", "employee name", "employee"],
            "total_wages": ["total wages", "wages", "total pay", "gross pay", "salary", "earnings", "compensation"],
            "w2_wages": ["w2 wages", "w-2 wages", "w2", "box 1", "federal wages"],
            "bonus": ["bonus", "bonuses", "incentive", "commission"],
            "period": ["period", "pay period", "date", "year"],
        },
        "time_tracking": {
            "employee_name": ["employee", "name", "resource", "worker"],
            "project_name": ["project", "task", "activity", "job", "engagement"],
            "hours": ["hours", "time", "duration", "qty", "quantity"],
            "date": ["date", "week", "period", "time period"],
            "description": ["description", "notes", "comments", "work description"],
        },
        "projects": {
            "name": ["project", "project name", "name", "title"],
            "code": ["code", "project code", "id", "project id"],
            "department": ["department", "dept", "division", "owner"],
            "description": ["description", "desc", "summary", "overview"],
            "start_date": ["start date", "start", "begin date", "commenced"],
            "status": ["status", "state", "active"],
        },
        "supplies": {
            "description": ["description", "item", "supply", "material", "product"],
            "vendor": ["vendor", "supplier", "payee", "from"],
            "amount": ["amount", "cost", "total", "price", "value"],
            "gl_account": ["account", "gl", "gl account", "acct"],
            "date": ["date", "purchase date", "invoice date"],
        },
        "contracts": {
            "contractor_name": ["contractor", "vendor", "company", "firm", "name"],
            "amount": ["amount", "value", "cost", "total", "contract value"],
            "description": ["description", "scope", "services", "work"],
            "start_date": ["start date", "effective date", "begin"],
            "end_date": ["end date", "expiration", "terminate"],
        },
        "general_ledger": {
            "account": ["account", "gl account", "acct", "account number"],
            "description": ["description", "desc", "memo", "detail", "name"],
            "debit": ["debit", "dr", "debit amount"],
            "credit": ["credit", "cr", "credit amount"],
            "amount": ["amount", "total", "balance", "net"],
            "date": ["date", "trans date", "posting date", "period"],
        }
    }

    def __init__(self, anthropic_client=None, config: Optional[Dict] = None):
        self.anthropic_client = anthropic_client
        self.config = config or {}
        self.ai_model = self.config.get("ai_model", "claude-sonnet-4-20250514")

    async def analyze_excel(
        self,
        file_content: bytes,
        filename: str,
        study_context: Optional[Dict] = None
    ) -> ExcelAnalysisResult:
        """
        Analyze an Excel file and intelligently map columns to R&D study fields.

        Args:
            file_content: Raw Excel file bytes
            filename: Original filename
            study_context: Optional context about the study (entity name, tax year, etc.)

        Returns:
            ExcelAnalysisResult with analysis and mappings for all sheets
        """
        logger.info(f"Analyzing Excel file: {filename}")

        # Load the workbook
        buffer = io.BytesIO(file_content)

        try:
            # Try reading as Excel
            xlsx = pd.ExcelFile(buffer)
            sheet_names = xlsx.sheet_names
        except Exception:
            # Try reading as CSV
            buffer.seek(0)
            try:
                df = pd.read_csv(buffer)
                sheet_names = ["Sheet1"]
                xlsx = None
            except Exception as e:
                raise ValueError(f"Unable to parse file: {e}")

        sheets = []
        raw_data = {}

        for sheet_name in sheet_names:
            if xlsx:
                df = pd.read_excel(xlsx, sheet_name=sheet_name)

            # Skip empty sheets
            if df.empty:
                continue

            raw_data[sheet_name] = df

            # Analyze this sheet
            analysis = await self._analyze_sheet(df, sheet_name, study_context)
            sheets.append(analysis)

        # Calculate overall quality and recommendations
        overall_quality = self._calculate_overall_quality(sheets)
        missing_types = self._identify_missing_data_types(sheets)
        recommendations = self._generate_recommendations(sheets, missing_types)

        return ExcelAnalysisResult(
            filename=filename,
            sheets=sheets,
            overall_quality_score=overall_quality,
            missing_data_types=missing_types,
            recommendations=recommendations,
            raw_data=raw_data
        )

    async def _analyze_sheet(
        self,
        df: pd.DataFrame,
        sheet_name: str,
        study_context: Optional[Dict]
    ) -> SheetAnalysis:
        """Analyze a single sheet."""
        # Get column info
        columns = list(df.columns)
        sample_data = df.head(10).to_dict('records')

        # Step 1: Detect category
        category, category_confidence = await self._detect_category(
            columns, sample_data, sheet_name
        )

        # Step 2: Map columns
        mappings = await self._map_columns(columns, sample_data, category)

        # Step 3: Calculate data quality
        quality_score, issues = self._assess_data_quality(df, mappings, category)

        # Step 4: Create preview
        preview = self._create_preview(df, mappings)

        return SheetAnalysis(
            sheet_name=sheet_name,
            category=category,
            category_confidence=category_confidence,
            row_count=len(df),
            column_mappings=mappings,
            data_quality_score=quality_score,
            issues=issues,
            preview_data=preview
        )

    async def _detect_category(
        self,
        columns: List[str],
        sample_data: List[Dict],
        sheet_name: str
    ) -> Tuple[DataCategory, float]:
        """Detect the data category of a sheet using AI."""
        # First try rule-based detection
        column_lower = [c.lower() for c in columns]
        sheet_lower = sheet_name.lower()

        # Check sheet name hints
        name_hints = {
            DataCategory.PAYROLL: ["payroll", "wages", "w2", "w-2", "salary"],
            DataCategory.EMPLOYEES: ["employee", "staff", "roster", "personnel"],
            DataCategory.TIME_TRACKING: ["time", "hours", "timesheet"],
            DataCategory.PROJECTS: ["project", "initiative", "rd", "r&d"],
            DataCategory.SUPPLIES: ["supplies", "materials", "purchases"],
            DataCategory.CONTRACTS: ["contract", "vendor", "contractor"],
            DataCategory.GENERAL_LEDGER: ["gl", "ledger", "journal", "trial balance"],
        }

        for category, hints in name_hints.items():
            if any(hint in sheet_lower for hint in hints):
                return category, 0.85

        # Check column patterns
        category_scores = {}
        for category, fields in self.FIELD_PATTERNS.items():
            score = 0
            for field, patterns in fields.items():
                for pattern in patterns:
                    if any(pattern.lower() in col for col in column_lower):
                        score += 1
                        break
            category_scores[category] = score

        if category_scores:
            best_category = max(category_scores, key=category_scores.get)
            if category_scores[best_category] >= 2:
                confidence = min(0.9, 0.5 + category_scores[best_category] * 0.1)
                return DataCategory(best_category), confidence

        # Use AI if available and rule-based detection is inconclusive
        if self.anthropic_client:
            try:
                return await self._ai_detect_category(columns, sample_data)
            except Exception as e:
                logger.warning(f"AI category detection failed: {e}")

        return DataCategory.UNKNOWN, 0.3

    async def _ai_detect_category(
        self,
        columns: List[str],
        sample_data: List[Dict]
    ) -> Tuple[DataCategory, float]:
        """Use AI to detect data category."""
        sample_json = json.dumps(sample_data[:3], indent=2, default=str)

        prompt = f"""Analyze this spreadsheet data and determine what type of data it contains.

Columns: {columns}

Sample data (first 3 rows):
{sample_json}

Classify this data into ONE of these categories:
- employees: Employee roster/list with names, titles, departments
- payroll: Payroll data with wages, salaries, W-2 information
- time_tracking: Time tracking data showing hours worked on projects
- projects: Project information with names, descriptions, status
- supplies: Supply/material purchases
- contracts: Contract/vendor information
- general_ledger: Accounting GL entries with debits/credits
- unknown: Cannot determine

Respond with JSON only: {{"category": "category_name", "confidence": 0.0-1.0, "reasoning": "brief explanation"}}"""

        response = await self.anthropic_client.messages.create(
            model=self.ai_model,
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}]
        )

        result = json.loads(response.content[0].text)
        category = DataCategory(result.get("category", "unknown"))
        confidence = float(result.get("confidence", 0.5))

        return category, confidence

    async def _map_columns(
        self,
        columns: List[str],
        sample_data: List[Dict],
        category: DataCategory
    ) -> List[ColumnMapping]:
        """Map source columns to target fields."""
        mappings = []

        # Get the field patterns for this category
        patterns = self.FIELD_PATTERNS.get(category.value, {})

        for col in columns:
            col_lower = col.lower().strip()

            # Find best matching field
            best_field = None
            best_confidence = 0.0

            for field, field_patterns in patterns.items():
                for pattern in field_patterns:
                    # Exact match
                    if col_lower == pattern:
                        best_field = field
                        best_confidence = 0.95
                        break
                    # Contains match
                    elif pattern in col_lower:
                        if best_confidence < 0.8:
                            best_field = field
                            best_confidence = 0.8

                if best_confidence >= 0.95:
                    break

            # Get sample values for this column
            sample_values = []
            for row in sample_data[:5]:
                if col in row and row[col] is not None and pd.notna(row[col]):
                    sample_values.append(row[col])

            # Detect data type
            data_type = self._detect_data_type(sample_values)

            # Determine transformation if needed
            transformation = self._determine_transformation(best_field, data_type, sample_values)

            mappings.append(ColumnMapping(
                source_column=col,
                target_field=best_field or col_lower.replace(" ", "_"),
                confidence=best_confidence if best_field else 0.3,
                data_type=data_type,
                sample_values=sample_values[:3],
                transformation=transformation
            ))

        return mappings

    def _detect_data_type(self, sample_values: List[Any]) -> str:
        """Detect the data type of a column."""
        if not sample_values:
            return "unknown"

        # Check for numeric
        numeric_count = 0
        currency_count = 0
        date_count = 0

        for val in sample_values:
            val_str = str(val)

            # Check for currency
            if '$' in val_str or val_str.replace(',', '').replace('.', '').replace('-', '').isdigit():
                currency_count += 1

            # Check for date
            if any(c in val_str for c in ['/', '-']) and len(val_str) <= 10:
                date_count += 1

            # Check for numeric
            try:
                float(str(val).replace(',', '').replace('$', ''))
                numeric_count += 1
            except ValueError:
                pass

        total = len(sample_values)

        if currency_count > total * 0.5:
            return "currency"
        if date_count > total * 0.5:
            return "date"
        if numeric_count > total * 0.7:
            return "number"

        return "text"

    def _determine_transformation(
        self,
        target_field: Optional[str],
        data_type: str,
        sample_values: List[Any]
    ) -> Optional[str]:
        """Determine if any transformation is needed for the data."""
        if not target_field:
            return None

        # Currency fields should be cleaned
        if target_field in ["total_wages", "w2_wages", "amount", "bonus", "cost", "value"]:
            if data_type == "currency" or data_type == "text":
                return "clean_currency"

        # Date fields should be parsed
        if target_field in ["hire_date", "start_date", "end_date", "date"]:
            return "parse_date"

        # Percentage fields
        if target_field in ["qualified_percentage", "rd_percentage"]:
            return "parse_percentage"

        return None

    def _assess_data_quality(
        self,
        df: pd.DataFrame,
        mappings: List[ColumnMapping],
        category: DataCategory
    ) -> Tuple[float, List[str]]:
        """Assess the quality of the data."""
        issues = []
        scores = []

        # Check for required fields
        required_fields = {
            DataCategory.PAYROLL: ["name", "total_wages"],
            DataCategory.EMPLOYEES: ["name"],
            DataCategory.TIME_TRACKING: ["employee_name", "hours"],
            DataCategory.PROJECTS: ["name"],
            DataCategory.SUPPLIES: ["amount"],
            DataCategory.CONTRACTS: ["contractor_name", "amount"],
        }

        mapped_fields = [m.target_field for m in mappings if m.confidence > 0.5]

        for required in required_fields.get(category, []):
            if required not in mapped_fields:
                issues.append(f"Missing required field: {required}")
                scores.append(0.5)
            else:
                scores.append(1.0)

        # Check for data completeness
        for mapping in mappings:
            if mapping.confidence > 0.5:
                col = mapping.source_column
                if col in df.columns:
                    null_pct = df[col].isnull().sum() / len(df)
                    if null_pct > 0.3:
                        issues.append(f"Column '{col}' has {null_pct*100:.0f}% missing values")
                        scores.append(1 - null_pct)
                    else:
                        scores.append(1.0)

        # Check for duplicate rows
        if len(df) > 0:
            dup_pct = df.duplicated().sum() / len(df)
            if dup_pct > 0.1:
                issues.append(f"{dup_pct*100:.0f}% duplicate rows detected")
                scores.append(1 - dup_pct)

        # Calculate overall quality score
        quality_score = sum(scores) / len(scores) if scores else 0.5

        return quality_score, issues

    def _create_preview(
        self,
        df: pd.DataFrame,
        mappings: List[ColumnMapping]
    ) -> List[Dict[str, Any]]:
        """Create a preview of the mapped data."""
        preview = []

        for _, row in df.head(5).iterrows():
            mapped_row = {}
            for mapping in mappings:
                if mapping.source_column in row:
                    value = row[mapping.source_column]

                    # Apply transformation if specified
                    if mapping.transformation == "clean_currency":
                        value = self._clean_currency(value)
                    elif mapping.transformation == "parse_date":
                        value = self._parse_date(value)
                    elif mapping.transformation == "parse_percentage":
                        value = self._parse_percentage(value)

                    mapped_row[mapping.target_field] = value

            preview.append(mapped_row)

        return preview

    def _clean_currency(self, value: Any) -> Optional[float]:
        """Clean currency value to float."""
        if pd.isna(value):
            return None

        try:
            cleaned = str(value).replace('$', '').replace(',', '').strip()
            # Handle parentheses for negative
            if cleaned.startswith('(') and cleaned.endswith(')'):
                cleaned = '-' + cleaned[1:-1]
            return float(cleaned)
        except (ValueError, TypeError):
            return None

    def _parse_date(self, value: Any) -> Optional[str]:
        """Parse date value to ISO format."""
        if pd.isna(value):
            return None

        try:
            if isinstance(value, datetime):
                return value.date().isoformat()

            # Try common formats
            for fmt in ['%m/%d/%Y', '%Y-%m-%d', '%m-%d-%Y', '%d/%m/%Y']:
                try:
                    return datetime.strptime(str(value), fmt).date().isoformat()
                except ValueError:
                    continue

            return str(value)
        except Exception:
            return None

    def _parse_percentage(self, value: Any) -> Optional[float]:
        """Parse percentage value."""
        if pd.isna(value):
            return None

        try:
            cleaned = str(value).replace('%', '').strip()
            pct = float(cleaned)
            # If > 1, assume it's already a percentage
            return pct if pct <= 1 else pct / 100
        except (ValueError, TypeError):
            return None

    def _calculate_overall_quality(self, sheets: List[SheetAnalysis]) -> float:
        """Calculate overall quality score across all sheets."""
        if not sheets:
            return 0.0

        scores = [s.data_quality_score for s in sheets]
        return sum(scores) / len(scores)

    def _identify_missing_data_types(self, sheets: List[SheetAnalysis]) -> List[str]:
        """Identify what data types are missing for a complete R&D study."""
        found_categories = {s.category for s in sheets if s.category != DataCategory.UNKNOWN}

        # Required for a complete study
        required = {
            DataCategory.PAYROLL,
            DataCategory.EMPLOYEES,
            DataCategory.PROJECTS,
        }

        # Optional but helpful
        helpful = {
            DataCategory.TIME_TRACKING,
            DataCategory.SUPPLIES,
            DataCategory.CONTRACTS,
        }

        missing = []

        for cat in required:
            if cat not in found_categories:
                missing.append(f"{cat.value} (required)")

        for cat in helpful:
            if cat not in found_categories:
                missing.append(f"{cat.value} (recommended)")

        return missing

    def _generate_recommendations(
        self,
        sheets: List[SheetAnalysis],
        missing_types: List[str]
    ) -> List[str]:
        """Generate recommendations for improving data quality."""
        recommendations = []

        # Missing data recommendations
        for missing in missing_types:
            if "required" in missing:
                recommendations.append(f"Please provide {missing.split(' ')[0]} data to complete the study")

        # Quality issue recommendations
        for sheet in sheets:
            for issue in sheet.issues:
                if "missing values" in issue.lower():
                    recommendations.append(f"Review sheet '{sheet.sheet_name}': {issue}")
                elif "duplicate" in issue.lower():
                    recommendations.append(f"Remove duplicates in '{sheet.sheet_name}'")

        # Low confidence mapping recommendations
        for sheet in sheets:
            low_conf = [m for m in sheet.column_mappings if m.confidence < 0.5]
            if low_conf:
                recommendations.append(
                    f"Review column mappings in '{sheet.sheet_name}' - "
                    f"{len(low_conf)} columns need manual mapping"
                )

        return recommendations

    async def import_data(
        self,
        analysis: ExcelAnalysisResult,
        approved_mappings: Optional[Dict[str, Dict[str, str]]] = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Import data using the analyzed mappings.

        Args:
            analysis: The analysis result from analyze_excel()
            approved_mappings: Optional overrides for column mappings
                Format: {sheet_name: {source_column: target_field}}

        Returns:
            Dictionary of imported data by category
        """
        imported = {
            "employees": [],
            "payroll": [],
            "projects": [],
            "time_entries": [],
            "supplies": [],
            "contracts": [],
            "gl_entries": [],
        }

        for sheet in analysis.sheets:
            df = analysis.raw_data.get(sheet.sheet_name)
            if df is None:
                continue

            # Get mappings (with any approved overrides)
            mappings = sheet.column_mappings
            if approved_mappings and sheet.sheet_name in approved_mappings:
                overrides = approved_mappings[sheet.sheet_name]
                for mapping in mappings:
                    if mapping.source_column in overrides:
                        mapping.target_field = overrides[mapping.source_column]
                        mapping.confidence = 1.0

            # Import data based on category
            category_key = self._get_category_key(sheet.category)

            for _, row in df.iterrows():
                record = {}
                for mapping in mappings:
                    if mapping.confidence >= 0.3 and mapping.source_column in row:
                        value = row[mapping.source_column]

                        # Apply transformation
                        if mapping.transformation == "clean_currency":
                            value = self._clean_currency(value)
                        elif mapping.transformation == "parse_date":
                            value = self._parse_date(value)
                        elif mapping.transformation == "parse_percentage":
                            value = self._parse_percentage(value)

                        if value is not None and not (isinstance(value, float) and pd.isna(value)):
                            record[mapping.target_field] = value

                if record:
                    record["_source_sheet"] = sheet.sheet_name
                    imported[category_key].append(record)

        return imported

    def _get_category_key(self, category: DataCategory) -> str:
        """Get the import dictionary key for a category."""
        category_keys = {
            DataCategory.EMPLOYEES: "employees",
            DataCategory.PAYROLL: "payroll",
            DataCategory.PROJECTS: "projects",
            DataCategory.TIME_TRACKING: "time_entries",
            DataCategory.SUPPLIES: "supplies",
            DataCategory.CONTRACTS: "contracts",
            DataCategory.GENERAL_LEDGER: "gl_entries",
            DataCategory.UNKNOWN: "gl_entries",
        }
        return category_keys.get(category, "gl_entries")
