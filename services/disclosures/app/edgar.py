"""
EDGAR (SEC) API Client for fetching company filings and facts
"""
import httpx
from typing import Optional, Dict, Any, List
from pydantic import BaseModel


class EdgarClient:
    """Client for interacting with SEC EDGAR API"""

    DEFAULT_BASE_URL = "https://data.sec.gov"

    def __init__(self, base_url: str = None, user_agent: str = None):
        self.base_url = base_url or self.DEFAULT_BASE_URL
        self.headers = {
            "User-Agent": user_agent or "AuraAuditAI/1.0 (support@auraai.com)",
            "Accept": "application/json"
        }

    async def get_company_facts(self, cik: str) -> Dict[str, Any]:
        """
        Get company facts from EDGAR

        Args:
            cik: Central Index Key (10-digit padded)

        Returns:
            Company facts data
        """
        cik = cik.zfill(10)
        url = f"{self.base_url}/api/xbrl/companyfacts/CIK{cik}.json"

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=self.headers, timeout=30.0)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError:
                return {}

    async def get_submissions(self, cik: str) -> Dict[str, Any]:
        """
        Get company submissions (filings) from EDGAR

        Args:
            cik: Central Index Key (10-digit padded)

        Returns:
            Submissions data
        """
        cik = cik.zfill(10)
        url = f"{self.base_url}/cgi-bin/browse-edgar?action=getcompany&CIK={cik}&type=10-K&dateb=&owner=include&count=10&output=json"

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=self.headers, timeout=30.0)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError:
                return {}

    async def search_filings(
        self,
        cik: Optional[str] = None,
        filing_type: str = "10-K",
        date_from: Optional[str] = None,
        date_to: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for company filings

        Args:
            cik: Company CIK
            filing_type: Type of filing (10-K, 10-Q, 8-K, etc.)
            date_from: Start date (YYYY-MM-DD)
            date_to: End date (YYYY-MM-DD)

        Returns:
            List of matching filings
        """
        filings = []

        if cik:
            submissions = await self.get_submissions(cik)
            if submissions:
                filings = submissions.get("filings", {}).get("recent", [])

        return filings
