"""
SEC EDGAR Scraper for Financial Statement Data Acquisition

This module scrapes financial statements, audit opinions, and disclosures from SEC EDGAR.
It normalizes the data for training CPA-level AI models.

Features:
- Download 10-K, 10-Q, 8-K, S-1, DEF 14A filings
- Parse XBRL financial statements
- Extract audit opinions and disclosure notes
- Store in Azure Blob Storage
- Index in Azure Cognitive Search
"""

import asyncio
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, asdict
import json

import httpx
from bs4 import BeautifulSoup
from lxml import etree
from loguru import logger
from azure.storage.blob import BlobServiceClient
from azure.identity import DefaultAzureCredential
import pandas as pd
from tenacity import retry, stop_after_attempt, wait_exponential

from ..config import settings


@dataclass
class Filing:
    """Represents an SEC filing"""
    cik: str
    company_name: str
    form_type: str
    filing_date: datetime
    accession_number: str
    filing_url: str
    document_url: str
    xbrl_url: Optional[str] = None
    size_bytes: Optional[int] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        data['filing_date'] = self.filing_date.isoformat()
        return data


@dataclass
class FinancialStatement:
    """Normalized financial statement data"""
    cik: str
    company_name: str
    ticker: Optional[str]
    fiscal_year: int
    fiscal_period: str  # FY, Q1, Q2, Q3, Q4
    filing_date: datetime
    period_end_date: datetime
    form_type: str

    # Financial data (all amounts in dollars)
    revenue: Optional[float] = None
    cost_of_revenue: Optional[float] = None
    gross_profit: Optional[float] = None
    operating_expenses: Optional[float] = None
    operating_income: Optional[float] = None
    net_income: Optional[float] = None
    eps_basic: Optional[float] = None
    eps_diluted: Optional[float] = None

    total_assets: Optional[float] = None
    current_assets: Optional[float] = None
    total_liabilities: Optional[float] = None
    current_liabilities: Optional[float] = None
    stockholders_equity: Optional[float] = None

    cash_from_operations: Optional[float] = None
    cash_from_investing: Optional[float] = None
    cash_from_financing: Optional[float] = None

    # Metadata
    auditor: Optional[str] = None
    audit_opinion: Optional[str] = None  # Unqualified, Qualified, Adverse, Disclaimer

    # Raw XBRL data
    xbrl_facts: Optional[Dict] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        data['filing_date'] = self.filing_date.isoformat()
        data['period_end_date'] = self.period_end_date.isoformat()
        return data


@dataclass
class AuditOpinion:
    """Extracted audit opinion"""
    cik: str
    company_name: str
    fiscal_year: int
    auditor: str
    opinion_type: str  # Unqualified, Qualified, Adverse, Disclaimer
    going_concern_emphasis: bool
    internal_control_opinion: Optional[str]  # Effective, Material Weakness, etc.
    key_audit_matters: List[str]
    opinion_text: str
    opinion_date: datetime
    filing_date: datetime
    source_filing: str  # Accession number

    def to_dict(self) -> Dict:
        data = asdict(self)
        data['opinion_date'] = self.opinion_date.isoformat()
        data['filing_date'] = self.filing_date.isoformat()
        return data


@dataclass
class DisclosureNote:
    """Extracted disclosure note"""
    cik: str
    company_name: str
    fiscal_year: int
    fiscal_period: str
    note_title: str
    note_number: Optional[int]
    asc_topic: Optional[str]  # e.g., "ASC 606", "ASC 842"
    note_text: str
    tables: List[Dict]  # Extracted tables
    filing_date: datetime
    source_filing: str

    def to_dict(self) -> Dict:
        data = asdict(self)
        data['filing_date'] = self.filing_date.isoformat()
        return data


class EDGARScraper:
    """
    SEC EDGAR scraper for collecting financial statement data

    Features:
    - Rate limiting (10 requests/second per SEC guidelines)
    - Retry logic with exponential backoff
    - XBRL parsing
    - Azure Blob Storage integration
    - Incremental updates
    """

    BASE_URL = "https://www.sec.gov"
    COMPANY_SEARCH_URL = f"{BASE_URL}/cgi-bin/browse-edgar"
    RSS_URL = f"{BASE_URL}/cgi-bin/browse-edgar"

    # SEC requires User-Agent with company name and email
    HEADERS = {
        "User-Agent": "Aura Audit AI ml-support@aura-audit.ai",
        "Accept-Encoding": "gzip, deflate",
        "Host": "www.sec.gov"
    }

    # Rate limiting: 10 requests per second max per SEC rules
    REQUEST_DELAY = 0.11  # seconds between requests

    # Form types to scrape
    FORM_TYPES = {
        "10-K": "Annual Report",
        "10-Q": "Quarterly Report",
        "8-K": "Current Report",
        "S-1": "Registration Statement",
        "DEF 14A": "Proxy Statement",
        "20-F": "Annual Report (Foreign)",
        "6-K": "Current Report (Foreign)",
    }

    def __init__(
        self,
        azure_storage_connection_string: Optional[str] = None,
        blob_container: str = "edgar-filings",
        output_dir: Path = Path("./data/edgar"),
    ):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Azure Blob Storage for cloud storage
        if azure_storage_connection_string:
            self.blob_service_client = BlobServiceClient.from_connection_string(
                azure_storage_connection_string
            )
            self.container_client = self.blob_service_client.get_container_client(
                blob_container
            )
            # Create container if it doesn't exist
            try:
                self.container_client.create_container()
            except Exception:
                pass  # Container already exists
        else:
            self.blob_service_client = None

        # HTTP client with rate limiting
        self.client = httpx.AsyncClient(
            headers=self.HEADERS,
            timeout=httpx.Timeout(30.0),
            follow_redirects=True,
        )

        # Track scraped CIKs
        self.scraped_ciks: Set[str] = set()

        logger.info(f"EDGAR Scraper initialized. Output dir: {self.output_dir}")

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def _get(self, url: str) -> httpx.Response:
        """HTTP GET with rate limiting and retry logic"""
        await asyncio.sleep(self.REQUEST_DELAY)  # Rate limiting
        response = await self.client.get(url)
        response.raise_for_status()
        return response

    async def get_company_cik(self, ticker: str) -> Optional[str]:
        """Get CIK number for a ticker symbol"""
        # SEC provides a company tickers JSON file
        url = f"{self.BASE_URL}/files/company_tickers.json"
        try:
            response = await self._get(url)
            data = response.json()

            # Search for ticker
            ticker_upper = ticker.upper()
            for item in data.values():
                if item['ticker'] == ticker_upper:
                    # CIK needs to be 10 digits with leading zeros
                    cik = str(item['cik_str']).zfill(10)
                    logger.info(f"Found CIK {cik} for ticker {ticker}")
                    return cik

            logger.warning(f"CIK not found for ticker {ticker}")
            return None
        except Exception as e:
            logger.error(f"Error fetching CIK for {ticker}: {e}")
            return None

    async def get_company_filings(
        self,
        cik: str,
        form_types: Optional[List[str]] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[Filing]:
        """
        Get filings for a company

        Args:
            cik: 10-digit CIK number
            form_types: List of form types (e.g., ["10-K", "10-Q"])
            start_date: Filter filings after this date
            end_date: Filter filings before this date
            limit: Maximum number of filings to return
        """
        if form_types is None:
            form_types = list(self.FORM_TYPES.keys())

        filings = []

        # SEC submissions endpoint (JSON format, much faster than HTML scraping)
        cik_padded = cik.zfill(10)
        url = f"{self.BASE_URL}/cgi-bin/browse-edgar"

        for form_type in form_types:
            params = {
                "action": "getcompany",
                "CIK": cik,
                "type": form_type,
                "dateb": end_date.strftime("%Y%m%d") if end_date else "",
                "owner": "exclude",
                "start": 0,
                "count": limit,
                "output": "atom",
            }

            try:
                response = await self._get(url)
                response_url = str(response.url)

                # Parse Atom feed
                soup = BeautifulSoup(response.text, "xml")
                entries = soup.find_all("entry")

                for entry in entries[:limit]:
                    filing_date_str = entry.find("filing-date").text
                    filing_date = datetime.strptime(filing_date_str, "%Y-%m-%d")

                    # Filter by date range
                    if start_date and filing_date < start_date:
                        continue
                    if end_date and filing_date > end_date:
                        continue

                    accession_number = entry.find("accession-number").text
                    filing_url = entry.find("filing-href").text

                    # Get primary document URL
                    try:
                        # The filing URL points to the index page, we need to get the actual document
                        index_response = await self._get(filing_url)
                        index_soup = BeautifulSoup(index_response.text, "html.parser")

                        # Find the primary document link
                        doc_table = index_soup.find("table", {"class": "tableFile"})
                        if doc_table:
                            rows = doc_table.find_all("tr")[1:]  # Skip header
                            for row in rows:
                                cols = row.find_all("td")
                                if len(cols) >= 4:
                                    doc_type = cols[3].text.strip()
                                    if form_type in doc_type:
                                        doc_link = cols[2].find("a")["href"]
                                        document_url = f"{self.BASE_URL}{doc_link}"
                                        break
                            else:
                                document_url = filing_url
                        else:
                            document_url = filing_url
                    except Exception as e:
                        logger.warning(f"Could not get document URL for {accession_number}: {e}")
                        document_url = filing_url

                    # Check for XBRL
                    xbrl_url = None
                    if form_type in ["10-K", "10-Q", "20-F"]:
                        # XBRL instance document typically ends with _htm.xml
                        accession_no_dashes = accession_number.replace("-", "")
                        xbrl_base = f"{self.BASE_URL}/cgi-bin/viewer?action=view&cik={cik}&accession_number={accession_number}&xbrl_type=v"
                        xbrl_url = xbrl_base

                    company_name = entry.find("company-name").text

                    filing = Filing(
                        cik=cik,
                        company_name=company_name,
                        form_type=form_type,
                        filing_date=filing_date,
                        accession_number=accession_number,
                        filing_url=filing_url,
                        document_url=document_url,
                        xbrl_url=xbrl_url,
                    )

                    filings.append(filing)
                    logger.info(f"Found filing: {company_name} {form_type} {filing_date.strftime('%Y-%m-%d')}")

            except Exception as e:
                logger.error(f"Error fetching {form_type} filings for CIK {cik}: {e}")
                continue

        return filings

    async def download_filing(self, filing: Filing) -> Optional[Path]:
        """Download filing document"""
        try:
            response = await self._get(filing.document_url)

            # Save locally
            filename = f"{filing.cik}_{filing.accession_number}_{filing.form_type}.html"
            filepath = self.output_dir / filename

            with open(filepath, "wb") as f:
                f.write(response.content)

            # Upload to Azure Blob Storage if configured
            if self.blob_service_client:
                blob_name = f"{filing.form_type}/{filing.cik}/{filename}"
                blob_client = self.container_client.get_blob_client(blob_name)
                blob_client.upload_blob(response.content, overwrite=True)
                logger.info(f"Uploaded to Azure Blob: {blob_name}")

            logger.info(f"Downloaded filing: {filename}")
            return filepath

        except Exception as e:
            logger.error(f"Error downloading filing {filing.accession_number}: {e}")
            return None

    async def parse_xbrl(self, filing: Filing) -> Optional[Dict]:
        """
        Parse XBRL financial data

        Returns dictionary with financial facts
        """
        if not filing.xbrl_url:
            return None

        try:
            # Download XBRL instance document
            response = await self._get(filing.xbrl_url)

            # Parse XML
            root = etree.fromstring(response.content)

            # Extract namespaces
            nsmap = root.nsmap

            # Common XBRL namespace prefixes
            gaap_ns = None
            dei_ns = None
            for prefix, uri in nsmap.items():
                if "us-gaap" in uri:
                    gaap_ns = uri
                elif "dei" in uri:
                    dei_ns = uri

            facts = {}

            if gaap_ns:
                # Extract financial facts
                # This is a simplified parser - production would need full XBRL library
                for element in root.iter():
                    if element.tag.startswith(f"{{{gaap_ns}}}"):
                        concept = element.tag.replace(f"{{{gaap_ns}}}", "")
                        value = element.text
                        context_ref = element.get("contextRef")
                        unit_ref = element.get("unitRef")
                        decimals = element.get("decimals")

                        if value:
                            try:
                                facts[concept] = {
                                    "value": float(value) if value.replace("-", "").replace(".", "").isdigit() else value,
                                    "contextRef": context_ref,
                                    "unitRef": unit_ref,
                                    "decimals": decimals,
                                }
                            except ValueError:
                                facts[concept] = {
                                    "value": value,
                                    "contextRef": context_ref,
                                }

            logger.info(f"Parsed XBRL: {len(facts)} facts extracted")
            return facts

        except Exception as e:
            logger.error(f"Error parsing XBRL for {filing.accession_number}: {e}")
            return None

    async def extract_audit_opinion(self, filing: Filing, document_path: Path) -> Optional[AuditOpinion]:
        """
        Extract audit opinion from 10-K filing

        Uses regex and NLP to identify:
        - Auditor name
        - Opinion type (unqualified, qualified, adverse, disclaimer)
        - Going concern emphasis
        - Key audit matters
        """
        if filing.form_type not in ["10-K", "20-F"]:
            return None  # Audit opinions only in annual reports

        try:
            with open(document_path, "r", encoding="utf-8", errors="ignore") as f:
                html_content = f.read()

            soup = BeautifulSoup(html_content, "html.parser")
            text = soup.get_text()

            # Find audit opinion section
            # Common patterns: "Report of Independent", "Auditor's Report", "Opinion on the Financial Statements"
            opinion_patterns = [
                r"Report of Independent (?:Registered Public Accounting Firm|Auditors?)",
                r"Independent Auditor'?s'? Report",
                r"Opinion on the Financial Statements",
            ]

            opinion_text = ""
            for pattern in opinion_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    # Extract next 5000 characters as opinion text
                    start_pos = match.start()
                    opinion_text = text[start_pos:start_pos + 5000]
                    break

            if not opinion_text:
                logger.warning(f"Could not find audit opinion in {filing.accession_number}")
                return None

            # Extract auditor name (Big 4 + others)
            auditors = {
                "Deloitte": ["Deloitte", "Deloitte & Touche", "Deloitte LLP"],
                "PwC": ["PricewaterhouseCoopers", "PwC", "PricewaterhouseCoopers LLP"],
                "EY": ["Ernst & Young", "EY", "Ernst & Young LLP"],
                "KPMG": ["KPMG", "KPMG LLP"],
                "BDO": ["BDO", "BDO USA"],
                "Grant Thornton": ["Grant Thornton"],
                "RSM": ["RSM", "RSM US"],
                "Crowe": ["Crowe", "Crowe LLP"],
            }

            auditor = "Unknown"
            for auditor_name, aliases in auditors.items():
                for alias in aliases:
                    if alias.lower() in opinion_text.lower():
                        auditor = auditor_name
                        break
                if auditor != "Unknown":
                    break

            # Determine opinion type
            opinion_type = "Unknown"
            if re.search(r"in our opinion.*present fairly.*in all material respects", opinion_text, re.IGNORECASE | re.DOTALL):
                opinion_type = "Unqualified"
            elif re.search(r"qualified opinion", opinion_text, re.IGNORECASE):
                opinion_type = "Qualified"
            elif re.search(r"adverse opinion", opinion_text, re.IGNORECASE):
                opinion_type = "Adverse"
            elif re.search(r"disclaimer of opinion", opinion_text, re.IGNORECASE):
                opinion_type = "Disclaimer"

            # Check for going concern emphasis
            going_concern = bool(re.search(
                r"going concern|substantial doubt.*continue.*operations",
                opinion_text,
                re.IGNORECASE
            ))

            # Extract Key Audit Matters (for larger companies post-2019)
            key_audit_matters = []
            kam_match = re.search(
                r"Critical Audit Matters?.*?(?:Basis for Opinion|$)",
                opinion_text,
                re.IGNORECASE | re.DOTALL
            )
            if kam_match:
                kam_text = kam_match.group(0)
                # Simple extraction - would need more sophisticated NLP in production
                kam_bullets = re.findall(r"•\s*(.+?)(?=•|$)", kam_text, re.DOTALL)
                key_audit_matters = [kam.strip()[:200] for kam in kam_bullets]

            # Extract opinion date (typically at the end of opinion)
            date_match = re.search(
                r"(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}",
                opinion_text
            )
            opinion_date = datetime.strptime(date_match.group(0), "%B %d, %Y") if date_match else filing.filing_date

            # Internal control opinion (for accelerated filers)
            internal_control = None
            if re.search(r"internal control over financial reporting.*effective", opinion_text, re.IGNORECASE | re.DOTALL):
                internal_control = "Effective"
            elif re.search(r"material weakness", opinion_text, re.IGNORECASE):
                internal_control = "Material Weakness"

            fiscal_year = filing.filing_date.year
            if filing.filing_date.month <= 3:
                fiscal_year -= 1  # Most 10-Ks filed in Q1 are for previous fiscal year

            audit_opinion = AuditOpinion(
                cik=filing.cik,
                company_name=filing.company_name,
                fiscal_year=fiscal_year,
                auditor=auditor,
                opinion_type=opinion_type,
                going_concern_emphasis=going_concern,
                internal_control_opinion=internal_control,
                key_audit_matters=key_audit_matters,
                opinion_text=opinion_text[:2000],  # Truncate for storage
                opinion_date=opinion_date,
                filing_date=filing.filing_date,
                source_filing=filing.accession_number,
            )

            logger.info(f"Extracted audit opinion: {auditor} - {opinion_type}")
            return audit_opinion

        except Exception as e:
            logger.error(f"Error extracting audit opinion from {filing.accession_number}: {e}")
            return None

    async def extract_disclosure_notes(self, filing: Filing, document_path: Path) -> List[DisclosureNote]:
        """
        Extract disclosure notes from filing

        Identifies:
        - Note titles and numbers
        - ASC topics referenced
        - Tables within notes
        """
        try:
            with open(document_path, "r", encoding="utf-8", errors="ignore") as f:
                html_content = f.read()

            soup = BeautifulSoup(html_content, "html.parser")

            notes = []

            # Find all note sections
            # Common patterns: "Note 1", "NOTE 1:", "1. ", etc.
            note_pattern = re.compile(r"Note\s+(\d+)[:\s\-]+(.+?)(?=Note\s+\d+|$)", re.IGNORECASE | re.DOTALL)

            text = soup.get_text()
            matches = note_pattern.finditer(text)

            fiscal_year = filing.filing_date.year
            fiscal_period = "FY" if filing.form_type in ["10-K", "20-F"] else "Q" + str((filing.filing_date.month - 1) // 3 + 1)

            for match in matches:
                note_number = int(match.group(1))
                note_content = match.group(2)

                # Extract note title (first line)
                title_lines = note_content.strip().split("\n")
                note_title = title_lines[0].strip()[:200] if title_lines else "Untitled"

                # Identify ASC topic
                asc_topics = re.findall(r"ASC\s+(\d+(?:-\d+)*)", note_content, re.IGNORECASE)
                asc_topic = f"ASC {asc_topics[0]}" if asc_topics else None

                # Extract tables (simplified - production would use table parsing library)
                tables = []
                table_elements = soup.find_all("table")
                for table in table_elements[:5]:  # Limit to first 5 tables per note
                    try:
                        df = pd.read_html(str(table))[0]
                        tables.append(df.to_dict())
                    except Exception:
                        pass

                note = DisclosureNote(
                    cik=filing.cik,
                    company_name=filing.company_name,
                    fiscal_year=fiscal_year,
                    fiscal_period=fiscal_period,
                    note_title=note_title,
                    note_number=note_number,
                    asc_topic=asc_topic,
                    note_text=note_content[:5000],  # Truncate for storage
                    tables=tables,
                    filing_date=filing.filing_date,
                    source_filing=filing.accession_number,
                )

                notes.append(note)
                logger.info(f"Extracted note {note_number}: {note_title}")

            return notes

        except Exception as e:
            logger.error(f"Error extracting disclosure notes from {filing.accession_number}: {e}")
            return []

    async def scrape_company(
        self,
        ticker: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict[str, List]:
        """
        Scrape all filings for a company

        Returns:
            Dictionary with lists of filings, financial statements, audit opinions, disclosure notes
        """
        # Get CIK
        cik = await self.get_company_cik(ticker)
        if not cik:
            return {}

        # Get filings
        filings = await self.get_company_filings(
            cik=cik,
            start_date=start_date,
            end_date=end_date,
            limit=100,
        )

        financial_statements = []
        audit_opinions = []
        disclosure_notes = []

        for filing in filings:
            # Download filing
            document_path = await self.download_filing(filing)
            if not document_path:
                continue

            # Parse XBRL if available
            if filing.xbrl_url:
                xbrl_facts = await self.parse_xbrl(filing)
            else:
                xbrl_facts = None

            # Extract audit opinion (10-K only)
            if filing.form_type in ["10-K", "20-F"]:
                audit_opinion = await self.extract_audit_opinion(filing, document_path)
                if audit_opinion:
                    audit_opinions.append(audit_opinion)

            # Extract disclosure notes
            notes = await self.extract_disclosure_notes(filing, document_path)
            disclosure_notes.extend(notes)

        return {
            "filings": filings,
            "financial_statements": financial_statements,
            "audit_opinions": audit_opinions,
            "disclosure_notes": disclosure_notes,
        }

    async def scrape_sp500(self, start_date: Optional[datetime] = None) -> None:
        """
        Scrape all S&P 500 companies

        This is a long-running operation (days to weeks)
        """
        # S&P 500 tickers (would be loaded from a file in production)
        sp500_tickers = [
            "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "BRK.B",
            # ... (500 total tickers)
        ]

        for ticker in sp500_tickers:
            logger.info(f"Scraping {ticker}...")
            try:
                data = await self.scrape_company(ticker, start_date=start_date)

                # Save data
                output_file = self.output_dir / f"{ticker}_data.json"
                with open(output_file, "w") as f:
                    json_data = {
                        "ticker": ticker,
                        "scraped_at": datetime.now().isoformat(),
                        "filings": [f.to_dict() for f in data.get("filings", [])],
                        "financial_statements": [fs.to_dict() for fs in data.get("financial_statements", [])],
                        "audit_opinions": [ao.to_dict() for ao in data.get("audit_opinions", [])],
                        "disclosure_notes": [dn.to_dict() for dn in data.get("disclosure_notes", [])],
                    }
                    json.dump(json_data, f, indent=2)

                logger.info(f"Completed {ticker}. Saved to {output_file}")

            except Exception as e:
                logger.error(f"Error scraping {ticker}: {e}")
                continue


async def main():
    """Main entry point for EDGAR scraper"""
    import argparse

    parser = argparse.ArgumentParser(description="SEC EDGAR Scraper")
    parser.add_argument("--ticker", type=str, help="Ticker symbol to scrape")
    parser.add_argument("--sp500", action="store_true", help="Scrape all S&P 500 companies")
    parser.add_argument("--start-date", type=str, help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end-date", type=str, help="End date (YYYY-MM-DD)")
    parser.add_argument("--output-dir", type=str, default="./data/edgar", help="Output directory")

    args = parser.parse_args()

    start_date = datetime.strptime(args.start_date, "%Y-%m-%d") if args.start_date else None
    end_date = datetime.strptime(args.end_date, "%Y-%m-%d") if args.end_date else None

    async with EDGARScraper(output_dir=Path(args.output_dir)) as scraper:
        if args.ticker:
            data = await scraper.scrape_company(args.ticker, start_date, end_date)
            logger.info(f"Scraped {len(data.get('filings', []))} filings for {args.ticker}")
        elif args.sp500:
            await scraper.scrape_sp500(start_date)
        else:
            logger.error("Please specify --ticker or --sp500")


if __name__ == "__main__":
    asyncio.run(main())
