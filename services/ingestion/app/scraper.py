"""
EDGAR Data Scraper & Ingestion Pipeline
Complete workflow for fetching, normalizing, and storing SEC EDGAR data
"""
import logging
from datetime import date, datetime
from typing import Optional, List, Dict, Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .edgar import EdgarClient
from .models import Filing, Fact, TrialBalance, TrialBalanceLine
from .storage import get_storage_client
from .config import settings

logger = logging.getLogger(__name__)


class EdgarScraper:
    """Complete EDGAR scraping and normalization pipeline"""

    def __init__(self, db: AsyncSession):
        """
        Initialize scraper with database session

        Args:
            db: SQLAlchemy async database session
        """
        self.db = db
        self.edgar_client = EdgarClient(
            base_url=settings.EDGAR_BASE_URL,
            user_agent=settings.EDGAR_USER_AGENT
        )
        self.storage = get_storage_client()

    async def scrape_company_by_cik(
        self,
        cik: str,
        forms: Optional[List[str]] = None,
        concepts: Optional[List[str]] = None,
        upload_raw: bool = True,
        user_id: Optional[UUID] = None
    ) -> Filing:
        """
        Scrape company data from EDGAR by CIK

        Args:
            cik: Company CIK (Central Index Key)
            forms: List of form types to filter (e.g., ['10-K', '10-Q'])
            concepts: List of XBRL concepts to extract
            upload_raw: Whether to upload raw JSON to S3
            user_id: User ID performing the scrape

        Returns:
            Filing record with associated facts
        """
        logger.info(f"Starting EDGAR scrape for CIK {cik}")

        try:
            # Step 1: Fetch company facts from EDGAR
            company_data = await self.edgar_client.get_company_facts(cik)

            # Extract company info
            entity_name = company_data.get("entityName", "")
            cik_value = company_data.get("cik", cik)

            logger.info(f"Fetched data for {entity_name} (CIK: {cik_value})")

            # Step 2: Upload raw data to S3 (optional)
            raw_data_uri = None
            if upload_raw:
                s3_key = f"edgar/raw/{cik}/{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                raw_data_uri = self.storage.upload_json(
                    company_data,
                    s3_key,
                    metadata={
                        'cik': str(cik_value),
                        'company_name': entity_name,
                        'scraped_at': datetime.now().isoformat()
                    }
                )
                logger.info(f"Uploaded raw data to {raw_data_uri}")

            # Step 3: Normalize facts
            normalized_facts = self.edgar_client.normalize_company_facts(
                company_data,
                concepts=concepts,
                form=forms[0] if forms else None
            )

            logger.info(f"Normalized {len(normalized_facts)} facts")

            # Step 4: Store filing and facts in database
            filing = await self._store_filing(
                cik=str(cik_value),
                company_name=entity_name,
                form=forms[0] if forms else "10-K",
                raw_data_uri=raw_data_uri,
                user_id=user_id
            )

            # Step 5: Store facts
            facts_created = await self._store_facts(filing.id, normalized_facts)

            logger.info(
                f"Successfully scraped {entity_name}: "
                f"Filing ID {filing.id}, {facts_created} facts stored"
            )

            return filing

        except Exception as e:
            logger.error(f"Error scraping CIK {cik}: {e}")
            raise

    async def scrape_company_by_ticker(
        self,
        ticker: str,
        forms: Optional[List[str]] = None,
        concepts: Optional[List[str]] = None,
        upload_raw: bool = True,
        user_id: Optional[UUID] = None
    ) -> Filing:
        """
        Scrape company data from EDGAR by ticker symbol

        Args:
            ticker: Stock ticker symbol
            forms: List of form types to filter
            concepts: List of XBRL concepts to extract
            upload_raw: Whether to upload raw JSON to S3
            user_id: User ID performing the scrape

        Returns:
            Filing record with associated facts
        """
        logger.info(f"Starting EDGAR scrape for ticker {ticker}")

        try:
            # Fetch company data by ticker
            company_data = await self.edgar_client.get_company_facts_by_ticker(ticker)

            # Extract CIK and company name
            cik_value = company_data.get("cik", "")
            entity_name = company_data.get("entityName", "")

            logger.info(f"Resolved {ticker} to {entity_name} (CIK: {cik_value})")

            # Upload raw data to S3
            raw_data_uri = None
            if upload_raw:
                s3_key = f"edgar/raw/{ticker.upper()}/{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                raw_data_uri = self.storage.upload_json(
                    company_data,
                    s3_key,
                    metadata={
                        'ticker': ticker.upper(),
                        'cik': str(cik_value),
                        'company_name': entity_name,
                        'scraped_at': datetime.now().isoformat()
                    }
                )
                logger.info(f"Uploaded raw data to {raw_data_uri}")

            # Normalize facts
            normalized_facts = self.edgar_client.normalize_company_facts(
                company_data,
                concepts=concepts,
                form=forms[0] if forms else None
            )

            # Store filing and facts
            filing = await self._store_filing(
                cik=str(cik_value),
                company_name=entity_name,
                ticker=ticker.upper(),
                form=forms[0] if forms else "10-K",
                raw_data_uri=raw_data_uri,
                user_id=user_id
            )

            facts_created = await self._store_facts(filing.id, normalized_facts)

            logger.info(
                f"Successfully scraped {ticker}: "
                f"Filing ID {filing.id}, {facts_created} facts stored"
            )

            return filing

        except Exception as e:
            logger.error(f"Error scraping ticker {ticker}: {e}")
            raise

    async def scrape_multiple_companies(
        self,
        identifiers: List[Dict[str, str]],
        forms: Optional[List[str]] = None,
        concepts: Optional[List[str]] = None,
        upload_raw: bool = True,
        user_id: Optional[UUID] = None
    ) -> List[Filing]:
        """
        Scrape multiple companies in batch

        Args:
            identifiers: List of dicts with 'cik' or 'ticker' keys
            forms: List of form types to filter
            concepts: List of XBRL concepts to extract
            upload_raw: Whether to upload raw JSON to S3
            user_id: User ID performing the scrape

        Returns:
            List of Filing records

        Example:
            identifiers = [
                {'cik': '0000320193'},  # Apple
                {'ticker': 'MSFT'},     # Microsoft
                {'ticker': 'GOOGL'}     # Alphabet
            ]
        """
        filings = []

        for identifier in identifiers:
            try:
                if 'cik' in identifier:
                    filing = await self.scrape_company_by_cik(
                        identifier['cik'],
                        forms=forms,
                        concepts=concepts,
                        upload_raw=upload_raw,
                        user_id=user_id
                    )
                elif 'ticker' in identifier:
                    filing = await self.scrape_company_by_ticker(
                        identifier['ticker'],
                        forms=forms,
                        concepts=concepts,
                        upload_raw=upload_raw,
                        user_id=user_id
                    )
                else:
                    logger.warning(f"Invalid identifier: {identifier}")
                    continue

                filings.append(filing)

            except Exception as e:
                logger.error(f"Failed to scrape {identifier}: {e}")
                continue

        logger.info(f"Batch scrape complete: {len(filings)} companies processed")
        return filings

    async def _store_filing(
        self,
        cik: str,
        company_name: str,
        form: str,
        ticker: Optional[str] = None,
        raw_data_uri: Optional[str] = None,
        user_id: Optional[UUID] = None
    ) -> Filing:
        """
        Store filing metadata in database

        Args:
            cik: Company CIK
            company_name: Company name
            form: Filing form type
            ticker: Stock ticker (optional)
            raw_data_uri: S3 URI of raw data
            user_id: User ID

        Returns:
            Filing ORM object
        """
        # Check if filing already exists
        query = select(Filing).where(
            Filing.cik == cik,
            Filing.form == form
        ).order_by(Filing.filing_date.desc()).limit(1)

        result = await self.db.execute(query)
        existing_filing = result.scalar_one_or_none()

        # Use today's date as filing date (in production, extract from metadata)
        filing_date = date.today()

        # Generate accession number
        accession_number = f"CIK{int(cik):010d}-{filing_date.strftime('%Y%m%d')}-{form}"

        # Check for duplicate by accession number
        if existing_filing and existing_filing.accession_number == accession_number:
            logger.info(f"Filing {accession_number} already exists, updating")
            existing_filing.raw_data_s3_uri = raw_data_uri
            existing_filing.updated_at = datetime.now()
            await self.db.commit()
            await self.db.refresh(existing_filing)
            return existing_filing

        # Create new filing
        filing = Filing(
            cik=cik,
            ticker=ticker,
            company_name=company_name,
            form=form,
            filing_date=filing_date,
            accession_number=accession_number,
            source_uri=f"{settings.EDGAR_BASE_URL}/companyfacts/CIK{int(cik):010d}.json",
            raw_data_s3_uri=raw_data_uri,
            ingested_by=user_id
        )

        self.db.add(filing)
        await self.db.commit()
        await self.db.refresh(filing)

        logger.info(f"Created filing: {filing.id}")
        return filing

    async def _store_facts(
        self,
        filing_id: UUID,
        normalized_facts: List[Dict[str, Any]]
    ) -> int:
        """
        Store normalized facts in database

        Args:
            filing_id: Filing UUID
            normalized_facts: List of normalized fact dictionaries

        Returns:
            Number of facts created
        """
        facts_created = 0

        for fact_data in normalized_facts:
            fact = Fact(
                filing_id=filing_id,
                concept=fact_data.get("concept"),
                taxonomy=fact_data.get("taxonomy", "us-gaap"),
                label=fact_data.get("label"),
                value=fact_data.get("value"),
                unit=fact_data.get("unit"),
                start_date=fact_data.get("start_date"),
                end_date=fact_data.get("end_date"),
                instant_date=fact_data.get("instant_date"),
                metadata=fact_data.get("metadata", {})
            )

            self.db.add(fact)
            facts_created += 1

        await self.db.commit()

        logger.info(f"Stored {facts_created} facts for filing {filing_id}")
        return facts_created

    async def get_filing_by_id(self, filing_id: UUID) -> Optional[Filing]:
        """
        Retrieve filing by ID

        Args:
            filing_id: Filing UUID

        Returns:
            Filing object or None
        """
        query = select(Filing).where(Filing.id == filing_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_facts_by_filing(
        self,
        filing_id: UUID,
        concepts: Optional[List[str]] = None,
        limit: int = 1000
    ) -> List[Fact]:
        """
        Retrieve facts for a filing

        Args:
            filing_id: Filing UUID
            concepts: Filter by concept names (optional)
            limit: Maximum number of facts to return

        Returns:
            List of Fact objects
        """
        query = select(Fact).where(Fact.filing_id == filing_id)

        if concepts:
            query = query.where(Fact.concept.in_(concepts))

        query = query.limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def search_filings(
        self,
        cik: Optional[str] = None,
        ticker: Optional[str] = None,
        form: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = 100
    ) -> List[Filing]:
        """
        Search filings with filters

        Args:
            cik: Company CIK
            ticker: Stock ticker
            form: Filing form type
            start_date: Start date filter
            end_date: End date filter
            limit: Maximum results

        Returns:
            List of Filing objects
        """
        query = select(Filing)

        if cik:
            query = query.where(Filing.cik == cik)
        if ticker:
            query = query.where(Filing.ticker == ticker)
        if form:
            query = query.where(Filing.form == form)
        if start_date:
            query = query.where(Filing.filing_date >= start_date)
        if end_date:
            query = query.where(Filing.filing_date <= end_date)

        query = query.order_by(Filing.filing_date.desc()).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def close(self):
        """Close EDGAR client"""
        await self.edgar_client.close()
