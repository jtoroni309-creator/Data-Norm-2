"""
EDGAR API Client
Fetches company facts, filings, and XBRL data from SEC EDGAR database

Reference: https://www.sec.gov/edgar/sec-api-documentation
"""
import asyncio
import logging
from datetime import date, datetime
from typing import Optional, List, Dict, Any
from decimal import Decimal

import httpx

logger = logging.getLogger(__name__)


class EdgarClient:
    """Client for SEC EDGAR API"""

    def __init__(self, base_url: str, user_agent: str):
        """
        Initialize EDGAR client

        Args:
            base_url: EDGAR API base URL (e.g., https://data.sec.gov)
            user_agent: User agent string (required by SEC)
        """
        self.base_url = base_url.rstrip("/")
        self.user_agent = user_agent
        self.client = httpx.AsyncClient(
            headers={"User-Agent": user_agent},
            timeout=30.0,
            follow_redirects=True
        )

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

    async def get_company_facts(self, cik: str) -> Dict[str, Any]:
        """
        Fetch all company facts for a given CIK

        Args:
            cik: Company CIK (Central Index Key)

        Returns:
            Company facts JSON

        Example:
            https://data.sec.gov/api/xbrl/companyfacts/CIK0000320193.json
        """
        # Pad CIK to 10 digits
        cik_padded = f"CIK{int(cik):010d}"
        url = f"{self.base_url}/api/xbrl/companyfacts/{cik_padded}.json"

        logger.info(f"Fetching company facts from EDGAR: {url}")

        try:
            response = await self.client.get(url)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"EDGAR API error: {e.response.status_code} - {e.response.text}")
            raise
        except httpx.RequestError as e:
            logger.error(f"EDGAR request error: {e}")
            raise

    async def get_company_facts_by_ticker(self, ticker: str) -> Dict[str, Any]:
        """
        Fetch company facts by ticker symbol

        Note: Requires a ticker->CIK mapping. For production, maintain a local
        ticker-CIK lookup table or use SEC's ticker.txt file.

        Args:
            ticker: Stock ticker symbol

        Returns:
            Company facts JSON
        """
        # For demonstration, we'll fetch the ticker-CIK mapping from SEC
        # In production, cache this mapping locally
        url = f"{self.base_url}/files/company_tickers.json"

        try:
            response = await self.client.get(url)
            response.raise_for_status()
            tickers_data = response.json()

            # Find matching ticker
            ticker_upper = ticker.upper()
            for key, company in tickers_data.items():
                if company.get("ticker") == ticker_upper:
                    cik = str(company["cik_str"])
                    return await self.get_company_facts(cik)

            raise ValueError(f"Ticker '{ticker}' not found in EDGAR database")

        except httpx.HTTPError as e:
            logger.error(f"Error fetching ticker mapping: {e}")
            raise

    def normalize_company_facts(
        self,
        company_data: Dict[str, Any],
        concepts: Optional[List[str]] = None,
        form: Optional[str] = None,
        filing_date: Optional[date] = None
    ) -> List[Dict[str, Any]]:
        """
        Normalize company facts JSON into a flat list of facts

        Args:
            company_data: Raw company facts from EDGAR
            concepts: Filter by specific XBRL concepts (e.g., ['us-gaap:Assets'])
            form: Filter by form type (e.g., '10-K')
            filing_date: Filter by specific filing date

        Returns:
            List of normalized fact dictionaries
        """
        normalized_facts = []

        # company_data structure:
        # {
        #   "cik": 320193,
        #   "entityName": "Apple Inc.",
        #   "facts": {
        #     "us-gaap": {
        #       "AccountsPayableCurrent": {
        #         "label": "Accounts Payable, Current",
        #         "description": "...",
        #         "units": {
        #           "USD": [
        #             {
        #               "end": "2023-09-30",
        #               "val": 62611000000,
        #               "accn": "0000320193-23-000106",
        #               "fy": 2023,
        #               "fp": "FY",
        #               "form": "10-K",
        #               "filed": "2023-11-03",
        #               ...
        #             },
        #             ...
        #           ]
        #         }
        #       },
        #       ...
        #     }
        #   }
        # }

        facts_data = company_data.get("facts", {})

        for taxonomy, concepts_dict in facts_data.items():
            for concept_name, concept_data in concepts_dict.items():
                full_concept = f"{taxonomy}:{concept_name}"

                # Filter by concept if specified
                if concepts and full_concept not in concepts:
                    continue

                label = concept_data.get("label", concept_name)
                description = concept_data.get("description", "")

                # Process units (USD, shares, etc.)
                units = concept_data.get("units", {})
                for unit, values in units.items():
                    for value_item in values:
                        # Filter by form if specified
                        if form and value_item.get("form") != form:
                            continue

                        # Filter by filing date if specified
                        if filing_date:
                            filed_date_str = value_item.get("filed")
                            if filed_date_str:
                                filed_date = datetime.strptime(filed_date_str, "%Y-%m-%d").date()
                                if filed_date != filing_date:
                                    continue

                        # Extract date fields
                        end_date = value_item.get("end")
                        start_date = value_item.get("start")

                        normalized_fact = {
                            "concept": full_concept,
                            "taxonomy": taxonomy,
                            "label": label,
                            "description": description,
                            "value": Decimal(str(value_item.get("val"))) if value_item.get("val") is not None else None,
                            "unit": unit,
                            "start_date": datetime.strptime(start_date, "%Y-%m-%d").date() if start_date else None,
                            "end_date": datetime.strptime(end_date, "%Y-%m-%d").date() if end_date else None,
                            "instant_date": datetime.strptime(end_date, "%Y-%m-%d").date() if end_date and not start_date else None,
                            "metadata": {
                                "accession_number": value_item.get("accn"),
                                "fiscal_year": value_item.get("fy"),
                                "fiscal_period": value_item.get("fp"),
                                "form": value_item.get("form"),
                                "filed_date": value_item.get("filed"),
                                "frame": value_item.get("frame"),
                            }
                        }

                        normalized_facts.append(normalized_fact)

        logger.info(f"Normalized {len(normalized_facts)} facts from EDGAR data")
        return normalized_facts

    async def get_submission_history(self, cik: str) -> Dict[str, Any]:
        """
        Fetch submission history for a company

        Args:
            cik: Company CIK

        Returns:
            Submissions JSON with all filings

        Example:
            https://data.sec.gov/submissions/CIK0000320193.json
        """
        cik_padded = f"CIK{int(cik):010d}"
        url = f"{self.base_url}/submissions/{cik_padded}.json"

        logger.info(f"Fetching submission history from EDGAR: {url}")

        try:
            response = await self.client.get(url)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Error fetching submission history: {e}")
            raise

    async def get_company_concept(self, cik: str, taxonomy: str, concept: str) -> Dict[str, Any]:
        """
        Fetch a specific company concept

        Args:
            cik: Company CIK
            taxonomy: Taxonomy (e.g., 'us-gaap')
            concept: Concept name (e.g., 'AccountsPayableCurrent')

        Returns:
            Company concept JSON

        Example:
            https://data.sec.gov/api/xbrl/companyconcept/CIK0000320193/us-gaap/AccountsPayableCurrent.json
        """
        cik_padded = f"CIK{int(cik):010d}"
        url = f"{self.base_url}/api/xbrl/companyconcept/{cik_padded}/{taxonomy}/{concept}.json"

        logger.info(f"Fetching company concept from EDGAR: {url}")

        try:
            response = await self.client.get(url)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Error fetching company concept: {e}")
            raise


# Example usage
async def example_usage():
    """Example of using EdgarClient"""
    client = EdgarClient(
        base_url="https://data.sec.gov",
        user_agent="Aura Audit AI contact@example.com"
    )

    try:
        # Fetch Apple's company facts (CIK: 0000320193)
        company_data = await client.get_company_facts("320193")

        # Normalize and filter for 10-K filings
        facts = client.normalize_company_facts(
            company_data,
            concepts=["us-gaap:Assets", "us-gaap:Revenues"],
            form="10-K"
        )

        print(f"Found {len(facts)} facts")
        for fact in facts[:5]:  # Print first 5
            print(f"  {fact['concept']}: {fact['value']} {fact['unit']} (as of {fact['end_date']})")

    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(example_usage())
