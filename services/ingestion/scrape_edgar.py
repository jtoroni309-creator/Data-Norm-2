#!/usr/bin/env python3
"""
EDGAR Scraper CLI Tool
Command-line interface for scraping SEC EDGAR data

Usage:
    # Scrape by CIK
    python scrape_edgar.py --cik 0000320193

    # Scrape by ticker
    python scrape_edgar.py --ticker AAPL

    # Scrape multiple companies
    python scrape_edgar.py --tickers AAPL,MSFT,GOOGL

    # Filter by form type
    python scrape_edgar.py --ticker AAPL --forms 10-K,10-Q

    # Filter by specific concepts
    python scrape_edgar.py --ticker AAPL --concepts us-gaap:Assets,us-gaap:Revenues

    # Batch scrape from file
    python scrape_edgar.py --batch companies.json
"""
import asyncio
import argparse
import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.database import AsyncSessionLocal
from app.scraper import EdgarScraper


async def scrape_by_cik(cik: str, forms: list[str] = None, concepts: list[str] = None):
    """Scrape company by CIK"""
    async with AsyncSessionLocal() as db:
        scraper = EdgarScraper(db)
        try:
            filing = await scraper.scrape_company_by_cik(
                cik=cik,
                forms=forms,
                concepts=concepts,
                upload_raw=True
            )
            print(f"\n✓ Successfully scraped CIK {cik}")
            print(f"  Company: {filing.company_name}")
            print(f"  Filing ID: {filing.id}")
            print(f"  Form: {filing.form}")
            print(f"  Filing Date: {filing.filing_date}")
            if filing.raw_data_s3_uri:
                print(f"  Raw Data: {filing.raw_data_s3_uri}")

            # Get fact count
            facts = await scraper.get_facts_by_filing(filing.id)
            print(f"  Facts Stored: {len(facts)}")

        except Exception as e:
            print(f"\n✗ Error scraping CIK {cik}: {e}", file=sys.stderr)
            raise
        finally:
            await scraper.close()


async def scrape_by_ticker(ticker: str, forms: list[str] = None, concepts: list[str] = None):
    """Scrape company by ticker"""
    async with AsyncSessionLocal() as db:
        scraper = EdgarScraper(db)
        try:
            filing = await scraper.scrape_company_by_ticker(
                ticker=ticker,
                forms=forms,
                concepts=concepts,
                upload_raw=True
            )
            print(f"\n✓ Successfully scraped {ticker}")
            print(f"  Company: {filing.company_name}")
            print(f"  CIK: {filing.cik}")
            print(f"  Filing ID: {filing.id}")
            print(f"  Form: {filing.form}")
            print(f"  Filing Date: {filing.filing_date}")
            if filing.raw_data_s3_uri:
                print(f"  Raw Data: {filing.raw_data_s3_uri}")

            # Get fact count
            facts = await scraper.get_facts_by_filing(filing.id)
            print(f"  Facts Stored: {len(facts)}")

        except Exception as e:
            print(f"\n✗ Error scraping {ticker}: {e}", file=sys.stderr)
            raise
        finally:
            await scraper.close()


async def scrape_multiple_tickers(tickers: list[str], forms: list[str] = None, concepts: list[str] = None):
    """Scrape multiple companies by ticker"""
    identifiers = [{'ticker': ticker} for ticker in tickers]

    async with AsyncSessionLocal() as db:
        scraper = EdgarScraper(db)
        try:
            print(f"\nScraping {len(tickers)} companies...")

            filings = await scraper.scrape_multiple_companies(
                identifiers=identifiers,
                forms=forms,
                concepts=concepts,
                upload_raw=True
            )

            print(f"\n✓ Successfully scraped {len(filings)} / {len(tickers)} companies")

            for filing in filings:
                print(f"\n  {filing.ticker or filing.cik}: {filing.company_name}")
                print(f"    Filing ID: {filing.id}")
                facts = await scraper.get_facts_by_filing(filing.id)
                print(f"    Facts: {len(facts)}")

        except Exception as e:
            print(f"\n✗ Batch scrape error: {e}", file=sys.stderr)
            raise
        finally:
            await scraper.close()


async def scrape_from_batch_file(filepath: str, forms: list[str] = None, concepts: list[str] = None):
    """Scrape from batch file"""
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)

        identifiers = data.get('companies', [])
        if not identifiers:
            print(f"✗ No companies found in {filepath}", file=sys.stderr)
            return

        print(f"\nLoaded {len(identifiers)} companies from {filepath}")

        async with AsyncSessionLocal() as db:
            scraper = EdgarScraper(db)
            try:
                filings = await scraper.scrape_multiple_companies(
                    identifiers=identifiers,
                    forms=forms,
                    concepts=concepts,
                    upload_raw=True
                )

                print(f"\n✓ Successfully scraped {len(filings)} / {len(identifiers)} companies")

                for filing in filings:
                    print(f"\n  {filing.ticker or filing.cik}: {filing.company_name}")
                    print(f"    Filing ID: {filing.id}")
                    facts = await scraper.get_facts_by_filing(filing.id)
                    print(f"    Facts: {len(facts)}")

            except Exception as e:
                print(f"\n✗ Batch scrape error: {e}", file=sys.stderr)
                raise
            finally:
                await scraper.close()

    except FileNotFoundError:
        print(f"✗ File not found: {filepath}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"✗ Invalid JSON in {filepath}: {e}", file=sys.stderr)
        sys.exit(1)


async def search_filings(
    cik: str = None,
    ticker: str = None,
    form: str = None,
    limit: int = 10
):
    """Search existing filings"""
    async with AsyncSessionLocal() as db:
        scraper = EdgarScraper(db)
        try:
            filings = await scraper.search_filings(
                cik=cik,
                ticker=ticker,
                form=form,
                limit=limit
            )

            if not filings:
                print("\nNo filings found")
                return

            print(f"\nFound {len(filings)} filings:")
            for filing in filings:
                print(f"\n  {filing.ticker or filing.cik}: {filing.company_name}")
                print(f"    Filing ID: {filing.id}")
                print(f"    Form: {filing.form}")
                print(f"    Date: {filing.filing_date}")
                print(f"    Accession: {filing.accession_number}")

        except Exception as e:
            print(f"\n✗ Search error: {e}", file=sys.stderr)
            raise
        finally:
            await scraper.close()


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='EDGAR Data Scraper - Fetch and store SEC filing data',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scrape Apple by CIK
  %(prog)s --cik 0000320193

  # Scrape Microsoft by ticker
  %(prog)s --ticker MSFT

  # Scrape multiple companies
  %(prog)s --tickers AAPL,MSFT,GOOGL

  # Filter by form types
  %(prog)s --ticker AAPL --forms 10-K,10-Q

  # Scrape specific concepts
  %(prog)s --ticker AAPL --concepts us-gaap:Assets,us-gaap:Revenues

  # Batch scrape from JSON file
  %(prog)s --batch companies.json

  # Search existing filings
  %(prog)s --search --ticker AAPL
        """
    )

    # Scraping options
    parser.add_argument('--cik', help='Company CIK to scrape')
    parser.add_argument('--ticker', help='Company ticker to scrape')
    parser.add_argument('--tickers', help='Comma-separated list of tickers')
    parser.add_argument('--batch', help='JSON file with companies to scrape')

    # Filtering options
    parser.add_argument('--forms', help='Comma-separated list of form types (e.g., 10-K,10-Q)')
    parser.add_argument('--concepts', help='Comma-separated list of XBRL concepts')

    # Text extraction
    parser.add_argument('--extract-text', action='store_true', help='Extract full text content (notes, disclosures, etc.)')

    # Search options
    parser.add_argument('--search', action='store_true', help='Search existing filings')
    parser.add_argument('--limit', type=int, default=10, help='Search result limit')

    args = parser.parse_args()

    # Parse forms and concepts
    forms = args.forms.split(',') if args.forms else None
    concepts = args.concepts.split(',') if args.concepts else None

    # Execute command
    try:
        if args.search:
            asyncio.run(search_filings(
                cik=args.cik,
                ticker=args.ticker,
                form=forms[0] if forms else None,
                limit=args.limit
            ))
        elif args.cik:
            asyncio.run(scrape_by_cik(args.cik, forms, concepts))
        elif args.ticker:
            asyncio.run(scrape_by_ticker(args.ticker, forms, concepts))
        elif args.tickers:
            tickers = [t.strip() for t in args.tickers.split(',')]
            asyncio.run(scrape_multiple_tickers(tickers, forms, concepts))
        elif args.batch:
            asyncio.run(scrape_from_batch_file(args.batch, forms, concepts))
        else:
            parser.print_help()
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n\nInterrupted by user", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"\n✗ Fatal error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
