"""
SEC EDGAR Integration Service

Fetches and parses financial statements from SEC EDGAR database.
"""

import asyncio
import logging
import re
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from xml.etree import ElementTree as ET

import aiohttp
from bs4 import BeautifulSoup

from .config import settings

logger = logging.getLogger(__name__)


class EDGARService:
    """
    Service for integrating with SEC EDGAR API.

    Provides methods for:
    - Company lookup by CIK/ticker
    - Filing search and retrieval
    - XBRL parsing
    - Financial statement extraction
    """

    def __init__(self):
        """Initialize EDGAR service with rate limiting."""
        self.base_url = settings.SEC_API_BASE_URL
        self.user_agent = settings.SEC_USER_AGENT
        self.rate_limit = settings.SEC_REQUESTS_PER_SECOND
        self.last_request_time = None

        logger.info(f"EDGAR service initialized with user agent: {self.user_agent}")

    async def _rate_limit(self):
        """Enforce SEC rate limiting (10 requests per second)."""
        if self.last_request_time:
            elapsed = (datetime.now() - self.last_request_time).total_seconds()
            required_delay = 1.0 / self.rate_limit
            if elapsed < required_delay:
                await asyncio.sleep(required_delay - elapsed)

        self.last_request_time = datetime.now()

    async def _make_request(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make HTTP request to SEC with rate limiting."""
        await self._rate_limit()

        headers = {
            "User-Agent": self.user_agent,
            "Accept": "application/json"
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, params=params) as response:
                response.raise_for_status()
                return await response.json()

    async def get_company_info(self, cik: str) -> Dict[str, Any]:
        """
        Get company information by CIK.

        Args:
            cik: Central Index Key (10-digit padded)

        Returns:
            Dictionary containing company information
        """
        # Pad CIK to 10 digits
        cik_padded = cik.zfill(10)

        url = f"{self.base_url}/submissions/CIK{cik_padded}.json"

        try:
            data = await self._make_request(url)

            return {
                "cik": data.get("cik"),
                "name": data.get("name"),
                "ticker": data.get("tickers", [None])[0] if data.get("tickers") else None,
                "sic": data.get("sic"),
                "sic_description": data.get("sicDescription"),
                "entity_type": data.get("entityType"),
                "fiscal_year_end": data.get("fiscalYearEnd"),
                "state_of_incorporation": data.get("stateOfIncorporation"),
                "business_address": data.get("addresses", {}).get("business"),
                "mailing_address": data.get("addresses", {}).get("mailing"),
                "phone": data.get("phone"),
                "category": data.get("category"),
            }

        except Exception as e:
            logger.error(f"Error fetching company info for CIK {cik}: {e}")
            raise

    async def search_companies(self, query: str) -> List[Dict[str, Any]]:
        """
        Search for companies by name or ticker.

        Args:
            query: Company name or ticker symbol

        Returns:
            List of matching companies
        """
        url = f"{settings.SEC_EDGAR_SEARCH_URL}"

        params = {
            "q": query,
            "category": "custom",
            "forms": "10-K,10-Q",
        }

        try:
            data = await self._make_request(url, params=params)

            companies = []
            if "hits" in data and "hits" in data["hits"]:
                for hit in data["hits"]["hits"][:10]:  # Top 10 results
                    source = hit.get("_source", {})
                    companies.append({
                        "cik": source.get("ciks", [None])[0],
                        "name": source.get("display_names", [None])[0],
                        "ticker": source.get("tickers", [None])[0],
                    })

            return companies

        except Exception as e:
            logger.error(f"Error searching companies with query '{query}': {e}")
            return []

    async def get_company_filings(
        self,
        cik: str,
        filing_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get company filings.

        Args:
            cik: Central Index Key
            filing_type: Filter by filing type (10-K, 10-Q, etc.)
            start_date: Filter filings after this date
            end_date: Filter filings before this date
            limit: Maximum number of filings to return

        Returns:
            List of filing dictionaries
        """
        cik_padded = cik.zfill(10)
        url = f"{self.base_url}/submissions/CIK{cik_padded}.json"

        try:
            data = await self._make_request(url)

            filings = []
            recent_filings = data.get("filings", {}).get("recent", {})

            if not recent_filings:
                return []

            # Get arrays
            accession_numbers = recent_filings.get("accessionNumber", [])
            filing_dates = recent_filings.get("filingDate", [])
            report_dates = recent_filings.get("reportDate", [])
            acceptance_dates = recent_filings.get("acceptanceDateTime", [])
            forms = recent_filings.get("form", [])
            primary_docs = recent_filings.get("primaryDocument", [])
            primary_doc_descriptions = recent_filings.get("primaryDocDescription", [])
            is_xbrl_list = recent_filings.get("isXBRL", [])

            for i in range(len(accession_numbers)):
                form = forms[i]
                filing_date_str = filing_dates[i]

                # Filter by filing type
                if filing_type and form != filing_type:
                    continue

                # Parse filing date
                filing_date = datetime.strptime(filing_date_str, "%Y-%m-%d")

                # Filter by date range
                if start_date and filing_date < start_date:
                    continue
                if end_date and filing_date > end_date:
                    continue

                accession = accession_numbers[i].replace("-", "")

                filing = {
                    "accession_number": accession_numbers[i],
                    "filing_type": form,
                    "filing_date": filing_date,
                    "report_date": datetime.strptime(report_dates[i], "%Y-%m-%d") if report_dates[i] else None,
                    "acceptance_date": acceptance_dates[i] if i < len(acceptance_dates) else None,
                    "primary_document": primary_docs[i] if i < len(primary_docs) else None,
                    "primary_doc_description": primary_doc_descriptions[i] if i < len(primary_doc_descriptions) else None,
                    "is_xbrl": is_xbrl_list[i] == 1 if i < len(is_xbrl_list) else False,
                    "filing_url": f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={cik}&type={form}&dateb=&owner=exclude&count=40",
                    "document_url": f"https://www.sec.gov/Archives/edgar/data/{cik}/{accession}/{primary_docs[i] if i < len(primary_docs) else ''}",
                }

                filings.append(filing)

                if len(filings) >= limit:
                    break

            return filings

        except Exception as e:
            logger.error(f"Error fetching filings for CIK {cik}: {e}")
            raise

    async def download_filing(self, cik: str, accession_number: str, document: str) -> str:
        """
        Download filing document.

        Args:
            cik: Central Index Key
            accession_number: Accession number with dashes
            document: Primary document filename

        Returns:
            Document content as string
        """
        accession = accession_number.replace("-", "")
        url = f"{self.base_url}/Archives/edgar/data/{cik}/{accession}/{document}"

        await self._rate_limit()

        headers = {
            "User-Agent": self.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml"
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                response.raise_for_status()
                return await response.text()

    async def get_xbrl_data(
        self,
        cik: str,
        accession_number: str
    ) -> Dict[str, Any]:
        """
        Get XBRL data for a filing.

        Args:
            cik: Central Index Key
            accession_number: Accession number with dashes

        Returns:
            Parsed XBRL data
        """
        accession = accession_number.replace("-", "")
        url = f"{self.base_url}/Archives/edgar/data/{cik}/{accession}/Financial_Report.xlsx"

        try:
            # Try to get the structured XBRL data in JSON format
            json_url = f"{self.base_url}/Archives/edgar/data/{cik}/{accession}/xbrl.json"

            data = await self._make_request(json_url)

            return self._parse_xbrl_json(data)

        except Exception as e:
            logger.warning(f"Could not fetch XBRL JSON, trying XML: {e}")

            # Fallback to XML parsing
            try:
                xml_url = f"{self.base_url}/Archives/edgar/data/{cik}/{accession}"
                # Find the instance document (usually ends with .xml)
                # This is simplified - in production, you'd parse the filing to find the correct file
                return await self._parse_xbrl_xml(xml_url)

            except Exception as e2:
                logger.error(f"Error fetching XBRL data: {e2}")
                raise

    def _parse_xbrl_json(self, xbrl_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse XBRL JSON data into structured format.

        Args:
            xbrl_data: Raw XBRL JSON data from SEC

        Returns:
            Parsed financial data
        """
        result = {
            "facts": {},
            "statements": {},
            "contexts": {},
        }

        # Parse facts
        if "facts" in xbrl_data:
            us_gaap = xbrl_data["facts"].get("us-gaap", {})

            for concept, data in us_gaap.items():
                if "units" in data:
                    for unit, values in data["units"].items():
                        if isinstance(values, list):
                            result["facts"][concept] = values

        # Parse document information
        if "documentInfo" in xbrl_data:
            result["document_info"] = xbrl_data["documentInfo"]

        return result

    async def _parse_xbrl_xml(self, xml_url: str) -> Dict[str, Any]:
        """
        Parse XBRL XML data.

        This is a simplified parser - production implementation would use
        a proper XBRL library like python-xbrl or arelle.
        """
        # This would require more sophisticated parsing
        # For now, return empty structure
        logger.warning("XML XBRL parsing not fully implemented")
        return {"facts": {}, "statements": {}}

    async def extract_financial_statements(
        self,
        cik: str,
        accession_number: str,
        filing_html: str
    ) -> Dict[str, Any]:
        """
        Extract financial statements from filing HTML.

        Args:
            cik: Central Index Key
            accession_number: Accession number
            filing_html: Filing HTML content

        Returns:
            Dictionary of financial statements
        """
        soup = BeautifulSoup(filing_html, "html.parser")

        statements = {
            "balance_sheet": None,
            "income_statement": None,
            "cash_flow": None,
            "retained_earnings": None,
        }

        # Try to find financial statement tables
        # This is simplified - production would use more sophisticated parsing

        # Find all tables
        tables = soup.find_all("table")

        for table in tables:
            # Look for balance sheet indicators
            text = table.get_text().lower()

            if "balance sheet" in text or "financial position" in text:
                statements["balance_sheet"] = self._parse_financial_table(table)

            elif ("income" in text or "operations" in text or "earnings" in text) and "comprehensive" not in text:
                statements["income_statement"] = self._parse_financial_table(table)

            elif "cash flow" in text:
                statements["cash_flow"] = self._parse_financial_table(table)

            elif "stockholders" in text and "equity" in text:
                statements["retained_earnings"] = self._parse_financial_table(table)

        return statements

    def _parse_financial_table(self, table) -> Dict[str, Any]:
        """
        Parse HTML table into structured data.

        Args:
            table: BeautifulSoup table element

        Returns:
            Parsed table data
        """
        data = {
            "headers": [],
            "rows": [],
        }

        # Extract headers
        headers = table.find_all("th")
        data["headers"] = [h.get_text().strip() for h in headers]

        # Extract rows
        rows = table.find_all("tr")
        for row in rows:
            cells = row.find_all(["td", "th"])
            if cells:
                row_data = []
                for cell in cells:
                    text = cell.get_text().strip()
                    # Try to parse as number
                    cleaned = text.replace(",", "").replace("$", "").replace("(", "-").replace(")", "")
                    try:
                        value = float(cleaned)
                        row_data.append(value)
                    except ValueError:
                        row_data.append(text)

                if row_data:
                    data["rows"].append(row_data)

        return data

    async def get_company_facts(self, cik: str) -> Dict[str, Any]:
        """
        Get all company facts (financial data) in structured format.

        Args:
            cik: Central Index Key

        Returns:
            Company facts data
        """
        cik_padded = cik.zfill(10)
        url = f"{self.base_url}/api/xbrl/companyfacts/CIK{cik_padded}.json"

        try:
            data = await self._make_request(url)
            return data

        except Exception as e:
            logger.error(f"Error fetching company facts for CIK {cik}: {e}")
            raise

    async def get_company_concept(
        self,
        cik: str,
        taxonomy: str,
        concept: str
    ) -> Dict[str, Any]:
        """
        Get specific financial concept for company.

        Args:
            cik: Central Index Key
            taxonomy: Taxonomy (e.g., "us-gaap")
            concept: Concept name (e.g., "AccountsPayableCurrent")

        Returns:
            Concept data across all filings
        """
        cik_padded = cik.zfill(10)
        url = f"{self.base_url}/api/xbrl/companyconcept/CIK{cik_padded}/{taxonomy}/{concept}.json"

        try:
            data = await self._make_request(url)
            return data

        except Exception as e:
            logger.error(f"Error fetching concept {concept} for CIK {cik}: {e}")
            raise


# Singleton instance
edgar_service = EDGARService()
