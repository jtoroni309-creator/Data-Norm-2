"""
Disclosure Notes Extraction and Generation Service

Extracts disclosure notes from SEC EDGAR filings and generates compliant
disclosure notes following GAAP, FASB, PCAOB, GAAS, and AICPA standards.
"""

import asyncio
import logging
import re
from datetime import datetime
from typing import Any, Dict, List, Optional
from enum import Enum

from bs4 import BeautifulSoup
from openai import AsyncOpenAI

from .config import settings
from .edgar_service import edgar_service

logger = logging.getLogger(__name__)


class DisclosureCategory(str, Enum):
    """ASC Topics for disclosure note categorization."""

    # General Topics
    ACCOUNTING_POLICIES = "accounting_policies"  # ASC 235
    ACCOUNTING_CHANGES = "accounting_changes"  # ASC 250
    RISKS_UNCERTAINTIES = "risks_uncertainties"  # ASC 275
    SUBSEQUENT_EVENTS = "subsequent_events"  # ASC 855

    # Revenue & Income
    REVENUE_RECOGNITION = "revenue_recognition"  # ASC 606
    SEGMENT_REPORTING = "segment_reporting"  # ASC 280
    EARNINGS_PER_SHARE = "earnings_per_share"  # ASC 260
    INCOME_TAXES = "income_taxes"  # ASC 740

    # Assets
    CASH_EQUIVALENTS = "cash_equivalents"  # ASC 305
    RECEIVABLES = "receivables"  # ASC 310
    INVENTORY = "inventory"  # ASC 330
    INVESTMENTS_DEBT = "investments_debt"  # ASC 320
    INVESTMENTS_EQUITY = "investments_equity"  # ASC 321
    EQUITY_METHOD = "equity_method"  # ASC 323
    CREDIT_LOSSES = "credit_losses"  # ASC 326
    PROPERTY_PLANT_EQUIPMENT = "property_plant_equipment"  # ASC 360
    INTANGIBLES_GOODWILL = "intangibles_goodwill"  # ASC 350

    # Liabilities & Equity
    DEBT = "debt"  # ASC 470
    LEASES = "leases"  # ASC 842
    EQUITY = "equity"  # ASC 505
    COMMITMENTS = "commitments"  # ASC 440
    CONTINGENCIES = "contingencies"  # ASC 450

    # Compensation & Benefits
    STOCK_COMPENSATION = "stock_compensation"  # ASC 718
    RETIREMENT_BENEFITS = "retirement_benefits"  # ASC 715
    COMPENSATION_GENERAL = "compensation_general"  # ASC 710

    # Complex Transactions
    BUSINESS_COMBINATIONS = "business_combinations"  # ASC 805
    DERIVATIVES_HEDGING = "derivatives_hedging"  # ASC 815
    FAIR_VALUE = "fair_value"  # ASC 820
    FINANCIAL_INSTRUMENTS = "financial_instruments"  # ASC 825
    RELATED_PARTY = "related_party"  # ASC 850

    # Other
    OTHER = "other"


class DisclosureStandard(str, Enum):
    """Accounting and auditing standards."""

    GAAP = "gaap"  # Generally Accepted Accounting Principles
    FASB = "fasb"  # Financial Accounting Standards Board
    PCAOB = "pcaob"  # Public Company Accounting Oversight Board
    GAAS = "gaas"  # Generally Accepted Auditing Standards
    AICPA = "aicpa"  # American Institute of CPAs
    SEC = "sec"  # Securities and Exchange Commission


class DisclosureNotesService:
    """
    Service for extracting and generating disclosure notes.

    Provides methods for:
    - Extracting disclosure notes from EDGAR filings
    - Categorizing notes by ASC topic
    - Analyzing compliance with standards
    - Generating AI-powered disclosure notes
    """

    def __init__(self):
        """Initialize disclosure notes service."""
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

        # ASC Topic keywords for categorization
        self.category_keywords = {
            DisclosureCategory.ACCOUNTING_POLICIES: [
                "accounting policies", "significant accounting policies", "basis of presentation",
                "summary of significant accounting policies", "principles of consolidation"
            ],
            DisclosureCategory.REVENUE_RECOGNITION: [
                "revenue", "revenue recognition", "customer contracts", "performance obligations",
                "asc 606", "contract assets", "contract liabilities", "deferred revenue"
            ],
            DisclosureCategory.INCOME_TAXES: [
                "income taxes", "tax", "deferred tax", "tax benefit", "effective tax rate",
                "tax provision", "valuation allowance", "uncertain tax positions"
            ],
            DisclosureCategory.LEASES: [
                "leases", "lease", "operating lease", "finance lease", "right-of-use",
                "rou asset", "lease liability", "asc 842"
            ],
            DisclosureCategory.DEBT: [
                "debt", "borrowings", "credit facility", "notes payable", "bonds",
                "long-term debt", "short-term debt", "debt covenant", "interest expense"
            ],
            DisclosureCategory.EQUITY: [
                "stockholders equity", "shareholders equity", "common stock", "preferred stock",
                "treasury stock", "retained earnings", "accumulated other comprehensive"
            ],
            DisclosureCategory.PROPERTY_PLANT_EQUIPMENT: [
                "property plant equipment", "ppe", "fixed assets", "depreciation",
                "useful life", "capital expenditure", "capitalized"
            ],
            DisclosureCategory.INTANGIBLES_GOODWILL: [
                "goodwill", "intangible", "amortization", "impairment", "intellectual property",
                "patents", "trademarks", "customer relationships"
            ],
            DisclosureCategory.STOCK_COMPENSATION: [
                "stock-based compensation", "stock compensation", "stock options", "rsus",
                "restricted stock", "employee stock", "share-based payment", "asc 718"
            ],
            DisclosureCategory.FAIR_VALUE: [
                "fair value", "level 1", "level 2", "level 3", "valuation technique",
                "fair value measurement", "asc 820"
            ],
            DisclosureCategory.DERIVATIVES_HEDGING: [
                "derivatives", "hedging", "hedge accounting", "interest rate swap",
                "foreign currency", "forward contract", "asc 815"
            ],
            DisclosureCategory.BUSINESS_COMBINATIONS: [
                "business combination", "acquisition", "merger", "purchase price allocation",
                "contingent consideration", "asc 805"
            ],
            DisclosureCategory.SEGMENT_REPORTING: [
                "segment", "operating segment", "reportable segment", "segment information",
                "geographic", "asc 280"
            ],
            DisclosureCategory.EARNINGS_PER_SHARE: [
                "earnings per share", "eps", "basic eps", "diluted eps", "asc 260",
                "weighted average shares"
            ],
            DisclosureCategory.COMMITMENTS: [
                "commitments", "purchase commitments", "contractual obligations",
                "unconditional purchase"
            ],
            DisclosureCategory.CONTINGENCIES: [
                "contingencies", "litigation", "legal proceedings", "loss contingency",
                "environmental", "warranty"
            ],
            DisclosureCategory.RELATED_PARTY: [
                "related party", "related-party", "affiliate", "asc 850"
            ],
            DisclosureCategory.SUBSEQUENT_EVENTS: [
                "subsequent events", "events after", "post-balance sheet", "asc 855"
            ],
            DisclosureCategory.RETIREMENT_BENEFITS: [
                "pension", "retirement", "defined benefit", "defined contribution",
                "401k", "postretirement", "asc 715"
            ],
            DisclosureCategory.INVESTMENTS_DEBT: [
                "debt securities", "available-for-sale", "held-to-maturity", "asc 320"
            ],
            DisclosureCategory.INVESTMENTS_EQUITY: [
                "equity securities", "marketable securities", "equity investments", "asc 321"
            ],
            DisclosureCategory.EQUITY_METHOD: [
                "equity method", "joint venture", "unconsolidated", "asc 323"
            ],
            DisclosureCategory.CREDIT_LOSSES: [
                "credit losses", "allowance for credit losses", "expected credit loss",
                "cecl", "asc 326"
            ],
        }

        logger.info("Disclosure notes service initialized")

    async def extract_disclosure_notes_from_filing(
        self,
        cik: str,
        accession_number: str,
        filing_html: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Extract all disclosure notes from an EDGAR filing.

        Args:
            cik: Central Index Key
            accession_number: Filing accession number
            filing_html: Optional pre-downloaded HTML content

        Returns:
            List of disclosure notes with categorization
        """
        try:
            # Download filing if not provided
            if not filing_html:
                # Get filing info to find document
                filings = await edgar_service.get_company_filings(
                    cik=cik,
                    limit=100
                )

                filing = next(
                    (f for f in filings if f["accession_number"] == accession_number),
                    None
                )

                if not filing:
                    raise ValueError(f"Filing {accession_number} not found")

                filing_html = await edgar_service.download_filing(
                    cik=cik,
                    accession_number=accession_number,
                    document=filing["primary_document"]
                )

            # Parse HTML
            soup = BeautifulSoup(filing_html, "html.parser")

            # Extract notes section
            notes = []
            note_number = 1

            # Method 1: Look for "Notes to Financial Statements" section
            notes_section = self._find_notes_section(soup)

            if notes_section:
                # Extract individual notes
                extracted_notes = self._parse_notes_section(notes_section)
                notes.extend(extracted_notes)
            else:
                # Method 2: Look for individual note patterns
                notes = self._find_individual_notes(soup)

            # Categorize each note
            categorized_notes = []
            for note in notes:
                category = self._categorize_note(note)

                categorized_notes.append({
                    "note_number": note.get("number", note_number),
                    "title": note.get("title", ""),
                    "content": note.get("content", ""),
                    "category": category,
                    "html": note.get("html", ""),
                    "tables": note.get("tables", []),
                    "word_count": len(note.get("content", "").split()),
                })

                note_number += 1

            logger.info(f"Extracted {len(categorized_notes)} disclosure notes from filing {accession_number}")

            return categorized_notes

        except Exception as e:
            logger.error(f"Error extracting disclosure notes: {e}")
            raise

    def _find_notes_section(self, soup: BeautifulSoup) -> Optional[BeautifulSoup]:
        """Find the main notes to financial statements section."""

        # Look for common heading patterns
        patterns = [
            r"notes?\s+to\s+(consolidated\s+)?financial\s+statements?",
            r"notes?\s+to\s+(consolidated\s+)?balance\s+sheets?",
            r"financial\s+statement\s+notes?",
        ]

        for pattern in patterns:
            # Try to find as heading
            for tag in ["h1", "h2", "h3", "h4", "p", "div"]:
                elements = soup.find_all(tag)
                for elem in elements:
                    text = elem.get_text().strip().lower()
                    if re.search(pattern, text):
                        # Found the notes section heading
                        # Return the parent section or following siblings
                        parent = elem.find_parent(["div", "section", "body"])
                        if parent:
                            return parent

                        # Or collect all following siblings
                        return elem.parent

        return None

    def _parse_notes_section(self, notes_section: BeautifulSoup) -> List[Dict[str, Any]]:
        """Parse individual notes from the notes section."""
        notes = []

        # Look for note headings (usually numbered)
        note_patterns = [
            r"note\s+(\d+)[:\.\-\s]*(.+?)$",
            r"(\d+)\.\s+(.+?)$",
        ]

        current_note = None
        current_content = []

        # Iterate through all elements
        for elem in notes_section.find_all(["h1", "h2", "h3", "h4", "h5", "p", "table", "div"]):
            text = elem.get_text().strip()

            # Check if this is a note heading
            is_heading = False
            for pattern in note_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match and elem.name in ["h1", "h2", "h3", "h4", "h5"]:
                    is_heading = True

                    # Save previous note
                    if current_note:
                        current_note["content"] = "\n".join(current_content)
                        notes.append(current_note)

                    # Start new note
                    current_note = {
                        "number": match.group(1) if match.group(1).isdigit() else len(notes) + 1,
                        "title": match.group(2).strip() if len(match.groups()) > 1 else text,
                        "html": str(elem),
                        "tables": [],
                    }
                    current_content = []
                    break

            # Add content to current note
            if not is_heading and current_note:
                if elem.name == "table":
                    current_note["tables"].append(str(elem))
                else:
                    current_content.append(text)

        # Save last note
        if current_note:
            current_note["content"] = "\n".join(current_content)
            notes.append(current_note)

        return notes

    def _find_individual_notes(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Find individual notes when there's no clear notes section."""
        notes = []

        # This is a fallback method - look for common note titles
        common_notes = [
            "Summary of Significant Accounting Policies",
            "Revenue Recognition",
            "Income Taxes",
            "Leases",
            "Debt",
            "Stockholders' Equity",
            "Stock-Based Compensation",
            "Fair Value Measurements",
            "Business Combinations",
            "Goodwill and Intangible Assets",
            "Property, Plant and Equipment",
            "Commitments and Contingencies",
            "Related Party Transactions",
            "Subsequent Events",
        ]

        for note_title in common_notes:
            # Search for this title
            for elem in soup.find_all(["h1", "h2", "h3", "h4", "h5"]):
                text = elem.get_text().strip()
                if note_title.lower() in text.lower():
                    # Extract content following this heading
                    content = []
                    tables = []

                    for sibling in elem.find_next_siblings():
                        if sibling.name in ["h1", "h2", "h3", "h4", "h5"]:
                            break

                        if sibling.name == "table":
                            tables.append(str(sibling))
                        else:
                            content.append(sibling.get_text().strip())

                    notes.append({
                        "number": len(notes) + 1,
                        "title": text,
                        "content": "\n".join(content),
                        "html": str(elem),
                        "tables": tables,
                    })
                    break

        return notes

    def _categorize_note(self, note: Dict[str, Any]) -> DisclosureCategory:
        """Categorize a disclosure note by ASC topic."""

        # Combine title and content for analysis
        text = f"{note.get('title', '')} {note.get('content', '')}".lower()

        # Score each category
        category_scores = {}
        for category, keywords in self.category_keywords.items():
            score = sum(1 for keyword in keywords if keyword.lower() in text)
            if score > 0:
                category_scores[category] = score

        # Return highest scoring category
        if category_scores:
            return max(category_scores, key=category_scores.get)

        return DisclosureCategory.OTHER

    async def analyze_disclosure_completeness(
        self,
        disclosure_notes: List[Dict[str, Any]],
        financial_statements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze whether all required disclosure notes are present.

        Args:
            disclosure_notes: Extracted disclosure notes
            financial_statements: Company's financial statements

        Returns:
            Completeness analysis with missing disclosures
        """
        try:
            # Required disclosure categories for most public companies
            required_categories = [
                DisclosureCategory.ACCOUNTING_POLICIES,
                DisclosureCategory.REVENUE_RECOGNITION,
                DisclosureCategory.INCOME_TAXES,
                DisclosureCategory.EARNINGS_PER_SHARE,
                DisclosureCategory.PROPERTY_PLANT_EQUIPMENT,
            ]

            # Check what we have
            present_categories = set(note["category"] for note in disclosure_notes)
            missing_categories = set(required_categories) - present_categories

            # Build analysis
            analysis = {
                "total_notes": len(disclosure_notes),
                "categories_present": len(present_categories),
                "categories_by_count": {},
                "required_present": len(required_categories) - len(missing_categories),
                "required_missing": len(missing_categories),
                "missing_categories": [cat.value for cat in missing_categories],
                "completeness_score": (len(required_categories) - len(missing_categories)) / len(required_categories),
                "notes_by_category": {},
            }

            # Count notes per category
            for note in disclosure_notes:
                category = note["category"]
                if category not in analysis["notes_by_category"]:
                    analysis["notes_by_category"][category] = []
                analysis["notes_by_category"][category].append(note["title"])

            return analysis

        except Exception as e:
            logger.error(f"Error analyzing disclosure completeness: {e}")
            raise

    async def generate_disclosure_note(
        self,
        category: DisclosureCategory,
        company_name: str,
        financial_data: Dict[str, Any],
        year: int,
        additional_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate AI-powered disclosure note following all standards.

        Args:
            category: Disclosure category (ASC topic)
            company_name: Company name
            financial_data: Relevant financial data
            year: Fiscal year
            additional_context: Optional additional context

        Returns:
            Generated disclosure note with compliance information
        """
        try:
            # Build prompt based on category
            prompt = self._build_disclosure_prompt(
                category=category,
                company_name=company_name,
                financial_data=financial_data,
                year=year,
                additional_context=additional_context
            )

            # Generate disclosure with GPT-4
            response = await self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert CPA and financial reporting specialist with 20+ years of experience
                        preparing disclosure notes for public companies. You have deep expertise in GAAP, FASB standards,
                        PCAOB requirements, GAAS, and AICPA guidelines. You prepare disclosure notes that are:

                        1. Fully compliant with all applicable ASC topics
                        2. Clear and understandable to investors
                        3. Comprehensive and complete
                        4. Properly formatted with appropriate headings
                        5. Include all required elements per FASB guidance

                        Your disclosure notes follow the style and structure of Fortune 500 companies' 10-K filings."""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,  # Lower temperature for consistency
                max_tokens=3000,
            )

            generated_content = response.choices[0].message.content

            # Check compliance
            compliance_check = await self._check_disclosure_compliance(
                category=category,
                content=generated_content,
                financial_data=financial_data
            )

            return {
                "category": category.value,
                "title": self._get_disclosure_title(category),
                "content": generated_content,
                "compliance": compliance_check,
                "applicable_standards": self._get_applicable_standards(category),
                "asc_topic": self._get_asc_topic(category),
                "generated_at": datetime.utcnow().isoformat(),
                "model": "gpt-4-turbo-preview",
            }

        except Exception as e:
            logger.error(f"Error generating disclosure note: {e}")

            # Return fallback disclosure
            return {
                "category": category.value,
                "title": self._get_disclosure_title(category),
                "content": f"[Disclosure note for {category.value} - Generation unavailable]",
                "compliance": {"status": "unknown", "checks": []},
                "applicable_standards": self._get_applicable_standards(category),
                "asc_topic": self._get_asc_topic(category),
                "generated_at": datetime.utcnow().isoformat(),
                "error": str(e),
            }

    def _build_disclosure_prompt(
        self,
        category: DisclosureCategory,
        company_name: str,
        financial_data: Dict[str, Any],
        year: int,
        additional_context: Optional[Dict[str, Any]]
    ) -> str:
        """Build prompt for disclosure note generation."""

        asc_topic = self._get_asc_topic(category)
        standards = self._get_applicable_standards(category)

        prompt = f"""Generate a comprehensive disclosure note for {company_name}'s {year} 10-K filing.

DISCLOSURE CATEGORY: {category.value}
ASC TOPIC: {asc_topic}
APPLICABLE STANDARDS: {', '.join(standards)}

FINANCIAL DATA:
{self._format_financial_data(financial_data)}

REQUIREMENTS:
1. Follow {asc_topic} disclosure requirements exactly
2. Include all required elements per FASB Accounting Standards Codification
3. Comply with PCAOB auditing standards
4. Follow SEC Regulation S-X and S-K guidance
5. Use clear, professional language appropriate for public company filings
6. Include specific numerical data from the financial statements
7. Provide all required reconciliations and explanations

STRUCTURE:
- Start with an introductory paragraph explaining the accounting policy
- Include all required disclosures for this ASC topic
- Provide detailed explanations of significant items
- Include forward-looking disclosures if required
- Format with appropriate headings and subheadings

Generate a complete, compliant disclosure note that would be suitable for inclusion in a Form 10-K filed with the SEC."""

        if additional_context:
            prompt += f"\n\nADDITIONAL CONTEXT:\n{self._format_additional_context(additional_context)}"

        return prompt

    def _format_financial_data(self, financial_data: Dict[str, Any]) -> str:
        """Format financial data for prompt."""
        formatted = []
        for key, value in financial_data.items():
            if isinstance(value, (int, float)):
                formatted.append(f"  {key}: ${value:,.2f}" if value >= 0 else f"  {key}: (${abs(value):,.2f})")
            else:
                formatted.append(f"  {key}: {value}")
        return "\n".join(formatted)

    def _format_additional_context(self, context: Dict[str, Any]) -> str:
        """Format additional context for prompt."""
        formatted = []
        for key, value in context.items():
            formatted.append(f"  {key}: {value}")
        return "\n".join(formatted)

    async def _check_disclosure_compliance(
        self,
        category: DisclosureCategory,
        content: str,
        financial_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check if disclosure note meets compliance requirements."""

        checks = []

        # Check 1: Minimum length (substantive content)
        if len(content) < 200:
            checks.append({
                "check": "minimum_length",
                "status": "warning",
                "message": "Disclosure may be too brief"
            })
        else:
            checks.append({
                "check": "minimum_length",
                "status": "pass",
                "message": "Adequate disclosure length"
            })

        # Check 2: Includes numerical data
        has_numbers = bool(re.search(r'\$[\d,]+|\d+\.\d+%', content))
        if has_numbers:
            checks.append({
                "check": "numerical_data",
                "status": "pass",
                "message": "Includes numerical data"
            })
        else:
            checks.append({
                "check": "numerical_data",
                "status": "warning",
                "message": "May need more numerical data"
            })

        # Check 3: Category-specific requirements
        category_check = self._check_category_requirements(category, content)
        checks.append(category_check)

        # Overall status
        status = "pass"
        if any(c["status"] == "fail" for c in checks):
            status = "fail"
        elif any(c["status"] == "warning" for c in checks):
            status = "warning"

        return {
            "status": status,
            "checks": checks,
            "checked_at": datetime.utcnow().isoformat()
        }

    def _check_category_requirements(
        self,
        category: DisclosureCategory,
        content: str
    ) -> Dict[str, Any]:
        """Check category-specific requirements."""

        content_lower = content.lower()

        # Define required elements per category
        requirements = {
            DisclosureCategory.ACCOUNTING_POLICIES: ["basis", "consolidation", "measurement"],
            DisclosureCategory.REVENUE_RECOGNITION: ["performance obligations", "timing", "contract"],
            DisclosureCategory.INCOME_TAXES: ["effective tax rate", "deferred", "provision"],
            DisclosureCategory.LEASES: ["lessee", "lease term", "discount rate"],
            DisclosureCategory.DEBT: ["maturity", "interest rate", "covenant"],
        }

        if category in requirements:
            required_terms = requirements[category]
            found_terms = [term for term in required_terms if term in content_lower]

            if len(found_terms) >= len(required_terms) * 0.6:  # 60% threshold
                return {
                    "check": f"{category.value}_requirements",
                    "status": "pass",
                    "message": f"Includes required elements: {', '.join(found_terms)}"
                }
            else:
                return {
                    "check": f"{category.value}_requirements",
                    "status": "warning",
                    "message": f"May be missing required elements"
                }

        return {
            "check": f"{category.value}_requirements",
            "status": "pass",
            "message": "Basic requirements met"
        }

    def _get_disclosure_title(self, category: DisclosureCategory) -> str:
        """Get standard title for disclosure category."""

        titles = {
            DisclosureCategory.ACCOUNTING_POLICIES: "Summary of Significant Accounting Policies",
            DisclosureCategory.REVENUE_RECOGNITION: "Revenue Recognition",
            DisclosureCategory.INCOME_TAXES: "Income Taxes",
            DisclosureCategory.LEASES: "Leases",
            DisclosureCategory.DEBT: "Debt",
            DisclosureCategory.EQUITY: "Stockholders' Equity",
            DisclosureCategory.STOCK_COMPENSATION: "Stock-Based Compensation",
            DisclosureCategory.FAIR_VALUE: "Fair Value Measurements",
            DisclosureCategory.DERIVATIVES_HEDGING: "Derivatives and Hedging Activities",
            DisclosureCategory.BUSINESS_COMBINATIONS: "Business Combinations",
            DisclosureCategory.INTANGIBLES_GOODWILL: "Goodwill and Intangible Assets",
            DisclosureCategory.PROPERTY_PLANT_EQUIPMENT: "Property, Plant and Equipment",
            DisclosureCategory.SEGMENT_REPORTING: "Segment Information",
            DisclosureCategory.EARNINGS_PER_SHARE: "Earnings Per Share",
            DisclosureCategory.COMMITMENTS: "Commitments",
            DisclosureCategory.CONTINGENCIES: "Contingencies",
            DisclosureCategory.RELATED_PARTY: "Related Party Transactions",
            DisclosureCategory.SUBSEQUENT_EVENTS: "Subsequent Events",
        }

        return titles.get(category, category.value.replace("_", " ").title())

    def _get_applicable_standards(self, category: DisclosureCategory) -> List[str]:
        """Get applicable accounting/auditing standards for category."""

        # All disclosures must follow these
        base_standards = ["GAAP", "FASB ASC", "SEC Regulation S-X"]

        # Add category-specific standards
        category_standards = {
            DisclosureCategory.REVENUE_RECOGNITION: ["ASC 606"],
            DisclosureCategory.LEASES: ["ASC 842"],
            DisclosureCategory.CREDIT_LOSSES: ["ASC 326 (CECL)"],
            DisclosureCategory.STOCK_COMPENSATION: ["ASC 718"],
            DisclosureCategory.BUSINESS_COMBINATIONS: ["ASC 805"],
            DisclosureCategory.FAIR_VALUE: ["ASC 820"],
            DisclosureCategory.DERIVATIVES_HEDGING: ["ASC 815"],
        }

        standards = base_standards.copy()
        if category in category_standards:
            standards.extend(category_standards[category])

        return standards

    def _get_asc_topic(self, category: DisclosureCategory) -> str:
        """Get ASC topic number for category."""

        asc_topics = {
            DisclosureCategory.ACCOUNTING_POLICIES: "ASC 235",
            DisclosureCategory.ACCOUNTING_CHANGES: "ASC 250",
            DisclosureCategory.EARNINGS_PER_SHARE: "ASC 260",
            DisclosureCategory.RISKS_UNCERTAINTIES: "ASC 275",
            DisclosureCategory.SEGMENT_REPORTING: "ASC 280",
            DisclosureCategory.CASH_EQUIVALENTS: "ASC 305",
            DisclosureCategory.RECEIVABLES: "ASC 310",
            DisclosureCategory.INVESTMENTS_DEBT: "ASC 320",
            DisclosureCategory.INVESTMENTS_EQUITY: "ASC 321",
            DisclosureCategory.EQUITY_METHOD: "ASC 323",
            DisclosureCategory.CREDIT_LOSSES: "ASC 326",
            DisclosureCategory.INVENTORY: "ASC 330",
            DisclosureCategory.INTANGIBLES_GOODWILL: "ASC 350",
            DisclosureCategory.PROPERTY_PLANT_EQUIPMENT: "ASC 360",
            DisclosureCategory.COMMITMENTS: "ASC 440",
            DisclosureCategory.CONTINGENCIES: "ASC 450",
            DisclosureCategory.DEBT: "ASC 470",
            DisclosureCategory.EQUITY: "ASC 505",
            DisclosureCategory.REVENUE_RECOGNITION: "ASC 606",
            DisclosureCategory.COMPENSATION_GENERAL: "ASC 710",
            DisclosureCategory.RETIREMENT_BENEFITS: "ASC 715",
            DisclosureCategory.STOCK_COMPENSATION: "ASC 718",
            DisclosureCategory.INCOME_TAXES: "ASC 740",
            DisclosureCategory.BUSINESS_COMBINATIONS: "ASC 805",
            DisclosureCategory.DERIVATIVES_HEDGING: "ASC 815",
            DisclosureCategory.FAIR_VALUE: "ASC 820",
            DisclosureCategory.FINANCIAL_INSTRUMENTS: "ASC 825",
            DisclosureCategory.LEASES: "ASC 842",
            DisclosureCategory.RELATED_PARTY: "ASC 850",
            DisclosureCategory.SUBSEQUENT_EVENTS: "ASC 855",
        }

        return asc_topics.get(category, "ASC Topic")

    async def generate_complete_disclosure_notes(
        self,
        company_name: str,
        cik: str,
        fiscal_year: int,
        financial_statements: Dict[str, Any],
        existing_notes: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Generate complete set of disclosure notes for a company.

        Args:
            company_name: Company name
            cik: Central Index Key
            fiscal_year: Fiscal year
            financial_statements: Complete financial statements
            existing_notes: Optional existing notes to analyze

        Returns:
            Complete disclosure notes package
        """
        try:
            # Analyze existing notes if provided
            completeness = None
            if existing_notes:
                completeness = await self.analyze_disclosure_completeness(
                    disclosure_notes=existing_notes,
                    financial_statements=financial_statements
                )

            # Generate notes for all major categories
            generated_notes = []

            # Core required disclosures
            core_categories = [
                DisclosureCategory.ACCOUNTING_POLICIES,
                DisclosureCategory.REVENUE_RECOGNITION,
                DisclosureCategory.INCOME_TAXES,
                DisclosureCategory.EARNINGS_PER_SHARE,
                DisclosureCategory.PROPERTY_PLANT_EQUIPMENT,
            ]

            for category in core_categories:
                note = await self.generate_disclosure_note(
                    category=category,
                    company_name=company_name,
                    financial_data=financial_statements,
                    year=fiscal_year
                )
                generated_notes.append(note)

            return {
                "company_name": company_name,
                "cik": cik,
                "fiscal_year": fiscal_year,
                "generated_notes": generated_notes,
                "existing_notes_analysis": completeness,
                "total_notes_generated": len(generated_notes),
                "generated_at": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error generating complete disclosure notes: {e}")
            raise


# Singleton instance
disclosure_notes_service = DisclosureNotesService()
