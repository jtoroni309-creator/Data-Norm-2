"""
SEC Filing Parser - Extract text content from 10-K/10-Q filings
Parses HTML/XBRL documents to extract narrative disclosures for AI training
"""
import re
import logging
from typing import Dict, List, Optional, Any
from bs4 import BeautifulSoup
import httpx

logger = logging.getLogger(__name__)


class FilingParser:
    """Parse SEC filings to extract text content and sections"""

    # Common section patterns in 10-K filings
    SECTION_PATTERNS_10K = {
        'business': [
            r'(?i)item\s*1\.?\s*business',
            r'(?i)item\s*1\s*-\s*business',
        ],
        'risk_factors': [
            r'(?i)item\s*1a\.?\s*risk\s*factors',
            r'(?i)item\s*1a\s*-\s*risk\s*factors',
        ],
        'properties': [
            r'(?i)item\s*2\.?\s*properties',
        ],
        'legal_proceedings': [
            r'(?i)item\s*3\.?\s*legal\s*proceedings',
        ],
        'mda': [
            r'(?i)item\s*7\.?\s*management.*discussion.*analysis',
            r'(?i)item\s*7\s*-\s*management',
        ],
        'financial_statements': [
            r'(?i)item\s*8\.?\s*financial\s*statements',
        ],
        'changes_disagreements': [
            r'(?i)item\s*9\.?\s*changes.*disagreements',
        ],
        'controls_procedures': [
            r'(?i)item\s*9a\.?\s*controls.*procedures',
        ],
        'directors_officers': [
            r'(?i)item\s*10\.?\s*directors.*officers',
        ],
        'executive_compensation': [
            r'(?i)item\s*11\.?\s*executive\s*compensation',
        ],
        'security_ownership': [
            r'(?i)item\s*12\.?\s*security\s*ownership',
        ],
        'related_party': [
            r'(?i)item\s*13\.?\s*certain.*transactions',
            r'(?i)item\s*13\.?\s*related.*party',
        ],
        'exhibits': [
            r'(?i)item\s*15\.?\s*exhibits',
        ],
    }

    # Common section patterns in 10-Q filings
    SECTION_PATTERNS_10Q = {
        'financial_statements': [
            r'(?i)part\s*i.*item\s*1\.?\s*financial\s*statements',
        ],
        'mda': [
            r'(?i)part\s*i.*item\s*2\.?\s*management.*discussion',
        ],
        'market_risk': [
            r'(?i)item\s*3\.?\s*quantitative.*qualitative.*market\s*risk',
        ],
        'controls_procedures': [
            r'(?i)item\s*4\.?\s*controls.*procedures',
        ],
        'legal_proceedings': [
            r'(?i)part\s*ii.*item\s*1\.?\s*legal\s*proceedings',
        ],
        'risk_factors': [
            r'(?i)part\s*ii.*item\s*1a\.?\s*risk\s*factors',
        ],
    }

    def __init__(self, user_agent: str):
        """
        Initialize filing parser

        Args:
            user_agent: User agent for SEC requests
        """
        self.user_agent = user_agent
        self.client = httpx.AsyncClient(
            headers={"User-Agent": user_agent},
            timeout=60.0,
            follow_redirects=True
        )

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

    async def get_filing_content(self, accession_number: str) -> Optional[str]:
        """
        Fetch raw filing content from SEC

        Args:
            accession_number: SEC accession number (e.g., 0000320193-23-000106)

        Returns:
            Raw HTML content or None
        """
        # Convert accession number format
        # From: 0000320193-23-000106
        # To: 0000320193/000032019323000106
        cik = accession_number.split('-')[0]
        accession_clean = accession_number.replace('-', '')

        # Try primary document first (usually .htm)
        url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession_clean}/{accession_number}.htm"

        try:
            logger.info(f"Fetching filing from {url}")
            response = await self.client.get(url)

            # If .htm doesn't work, try .txt
            if response.status_code == 404:
                url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession_clean}/{accession_number}.txt"
                response = await self.client.get(url)

            response.raise_for_status()
            return response.text

        except httpx.HTTPError as e:
            logger.error(f"Error fetching filing: {e}")
            return None

    async def get_filing_url_from_submission(self, cik: str, accession_number: str) -> Optional[str]:
        """
        Get the primary document URL for a filing

        Args:
            cik: Company CIK
            accession_number: Accession number

        Returns:
            URL to primary filing document
        """
        # Get submission metadata
        cik_padded = f"CIK{int(cik):010d}"
        url = f"https://data.sec.gov/submissions/{cik_padded}.json"

        try:
            response = await self.client.get(url)
            response.raise_for_status()
            data = response.json()

            # Find the filing in recent filings
            recent_filings = data.get('filings', {}).get('recent', {})
            accession_numbers = recent_filings.get('accessionNumber', [])
            primary_documents = recent_filings.get('primaryDocument', [])

            for i, accn in enumerate(accession_numbers):
                if accn == accession_number:
                    primary_doc = primary_documents[i]
                    accession_clean = accession_number.replace('-', '')
                    return f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession_clean}/{primary_doc}"

            return None

        except httpx.HTTPError as e:
            logger.error(f"Error fetching submission data: {e}")
            return None

    def clean_html(self, html_content: str) -> str:
        """
        Clean HTML content and extract text

        Args:
            html_content: Raw HTML

        Returns:
            Cleaned text
        """
        soup = BeautifulSoup(html_content, 'html.parser')

        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()

        # Get text
        text = soup.get_text()

        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)

        return text

    def extract_sections(self, content: str, form_type: str = '10-K') -> Dict[str, str]:
        """
        Extract major sections from filing content

        Args:
            content: Filing text content
            form_type: Form type (10-K or 10-Q)

        Returns:
            Dictionary of section_name: content
        """
        sections = {}
        patterns = self.SECTION_PATTERNS_10K if form_type == '10-K' else self.SECTION_PATTERNS_10Q

        # Find all section headers
        section_positions = []
        for section_name, regexes in patterns.items():
            for regex in regexes:
                match = re.search(regex, content)
                if match:
                    section_positions.append((match.start(), section_name))
                    break

        # Sort by position
        section_positions.sort()

        # Extract content between sections
        for i, (start_pos, section_name) in enumerate(section_positions):
            # Get end position (start of next section or end of content)
            if i + 1 < len(section_positions):
                end_pos = section_positions[i + 1][0]
            else:
                end_pos = len(content)

            # Extract section content
            section_content = content[start_pos:end_pos].strip()

            # Limit section size (first 50,000 chars)
            if len(section_content) > 50000:
                section_content = section_content[:50000] + "\n\n[Content truncated...]"

            sections[section_name] = section_content

        logger.info(f"Extracted {len(sections)} sections from {form_type}")
        return sections

    def extract_notes_to_financial_statements(self, content: str) -> List[Dict[str, str]]:
        """
        Extract individual notes to financial statements

        Args:
            content: Filing text content

        Returns:
            List of notes with title and content
        """
        notes = []

        # Look for notes section
        notes_pattern = r'(?i)notes?\s+to\s+(consolidated\s+)?financial\s+statements'
        notes_match = re.search(notes_pattern, content)

        if not notes_match:
            logger.warning("Notes to financial statements section not found")
            return notes

        # Start from notes section
        notes_start = notes_match.start()
        notes_content = content[notes_start:]

        # Find individual notes (usually numbered or titled)
        note_patterns = [
            r'(?i)note\s+(\d+)[\.:\s]+([^\n]+)\n',  # "Note 1. Summary of Accounting Policies"
            r'(?i)(\d+)\.\s+([A-Z][^\n]+)\n',       # "1. Summary of Accounting Policies"
        ]

        note_positions = []
        for pattern in note_patterns:
            for match in re.finditer(pattern, notes_content):
                note_number = match.group(1)
                note_title = match.group(2).strip()
                note_positions.append((match.start(), note_number, note_title))

        # Sort by position and extract content
        note_positions.sort()

        for i, (start_pos, note_num, note_title) in enumerate(note_positions[:30]):  # Limit to 30 notes
            # Get end position
            if i + 1 < len(note_positions):
                end_pos = note_positions[i + 1][0]
            else:
                # Use a reasonable limit (50k chars)
                end_pos = min(start_pos + 50000, len(notes_content))

            note_content = notes_content[start_pos:end_pos].strip()

            notes.append({
                'note_number': note_num,
                'title': note_title,
                'content': note_content[:20000]  # Limit individual note size
            })

        logger.info(f"Extracted {len(notes)} notes to financial statements")
        return notes

    def extract_accounting_policies(self, content: str) -> Optional[str]:
        """
        Extract summary of significant accounting policies

        Args:
            content: Filing text content

        Returns:
            Accounting policies text
        """
        patterns = [
            r'(?i)(?:note\s+\d+[\.:\s]+)?summary\s+of\s+significant\s+accounting\s+policies',
            r'(?i)(?:note\s+\d+[\.:\s]+)?significant\s+accounting\s+policies',
        ]

        for pattern in patterns:
            match = re.search(pattern, content)
            if match:
                # Extract ~20k characters after the match
                start = match.start()
                end = min(start + 20000, len(content))
                return content[start:end].strip()

        return None

    def extract_risk_factors(self, content: str) -> List[str]:
        """
        Extract individual risk factors

        Args:
            content: Filing text content

        Returns:
            List of risk factor descriptions
        """
        risk_factors = []

        # Find risk factors section
        risk_pattern = r'(?i)item\s+1a\.?\s*risk\s*factors'
        risk_match = re.search(risk_pattern, content)

        if not risk_match:
            return risk_factors

        # Extract risk factors section
        risk_start = risk_match.start()
        # Look for next item (usually Item 1B or Item 2)
        next_item = re.search(r'(?i)item\s+[12]b?\.?\s', content[risk_start + 100:])
        if next_item:
            risk_end = risk_start + 100 + next_item.start()
        else:
            risk_end = risk_start + 50000  # Default limit

        risk_content = content[risk_start:risk_end]

        # Find individual risks (often have headers or are numbered)
        # Look for capitalized sentences or bullet points
        risk_patterns = [
            r'([A-Z][^.!?]*(?:risk|may|could|might|uncertain)[^.!?]*[.!?])',
        ]

        for pattern in risk_patterns:
            matches = re.finditer(pattern, risk_content)
            for match in matches:
                risk_text = match.group(1).strip()
                if len(risk_text) > 50 and len(risk_text) < 2000:  # Reasonable length
                    risk_factors.append(risk_text)

        # Deduplicate
        risk_factors = list(dict.fromkeys(risk_factors))

        logger.info(f"Extracted {len(risk_factors)} risk factors")
        return risk_factors[:50]  # Limit to 50 risk factors

    async def parse_filing(self, cik: str, accession_number: str, form_type: str = '10-K') -> Dict[str, Any]:
        """
        Complete filing parsing workflow

        Args:
            cik: Company CIK
            accession_number: Filing accession number
            form_type: Form type (10-K or 10-Q)

        Returns:
            Dictionary with all extracted content
        """
        logger.info(f"Parsing {form_type} filing: {accession_number}")

        # Fetch filing content
        raw_content = await self.get_filing_content(accession_number)
        if not raw_content:
            logger.error(f"Could not fetch filing content for {accession_number}")
            return {}

        # Clean HTML
        clean_text = self.clean_html(raw_content)

        # Extract sections
        sections = self.extract_sections(clean_text, form_type)

        # Extract notes to financial statements
        notes = self.extract_notes_to_financial_statements(clean_text)

        # Extract accounting policies
        accounting_policies = self.extract_accounting_policies(clean_text)

        # Extract risk factors (for 10-K)
        risk_factors = []
        if form_type == '10-K':
            risk_factors = self.extract_risk_factors(clean_text)

        result = {
            'accession_number': accession_number,
            'form_type': form_type,
            'raw_content_length': len(raw_content),
            'clean_text_length': len(clean_text),
            'sections': sections,
            'notes_to_financial_statements': notes,
            'accounting_policies': accounting_policies,
            'risk_factors': risk_factors,
            'full_text': clean_text[:100000]  # First 100k chars of full text
        }

        logger.info(
            f"Parsed filing: {len(sections)} sections, "
            f"{len(notes)} notes, {len(risk_factors)} risk factors"
        )

        return result
