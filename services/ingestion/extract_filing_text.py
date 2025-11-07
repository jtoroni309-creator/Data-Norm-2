#!/usr/bin/env python3
"""
Extract full text content from SEC filings
Pulls notes, disclosures, MD&A, risk factors, and other narrative content for AI training

Usage:
    # Extract text from existing filing
    python extract_filing_text.py --filing-id <uuid>

    # Extract text for all filings from a ticker
    python extract_filing_text.py --ticker AAPL

    # Scrape and extract text in one step
    python extract_filing_text.py --ticker AAPL --scrape-first
"""
import asyncio
import argparse
import sys
from pathlib import Path
from uuid import UUID

sys.path.insert(0, str(Path(__file__).parent))

from app.database import AsyncSessionLocal
from app.scraper import EdgarScraper


async def extract_text_from_filing(filing_id: str):
    """Extract text from a specific filing"""
    async with AsyncSessionLocal() as db:
        scraper = EdgarScraper(db)
        try:
            # Get filing
            filing = await scraper.get_filing_by_id(UUID(filing_id))

            if not filing:
                print(f"✗ Filing {filing_id} not found", file=sys.stderr)
                return

            print(f"\n🔍 Extracting text from {filing.company_name} - {filing.form}")
            print(f"   CIK: {filing.cik}, Date: {filing.filing_date}")

            # Extract text
            counts = await scraper.extract_filing_text(filing, upload_to_s3=True)

            print(f"\n✓ Text extraction complete!")
            print(f"   Sections: {counts['sections']}")
            print(f"   Notes: {counts['notes']}")
            print(f"   Risk Factors: {counts['risks']}")
            print(f"   Policies: {counts['policies']}")

        except Exception as e:
            print(f"\n✗ Error: {e}", file=sys.stderr)
            raise
        finally:
            await scraper.close()


async def extract_text_from_ticker(ticker: str, scrape_first: bool = False):
    """Extract text from all filings for a ticker"""
    async with AsyncSessionLocal() as db:
        scraper = EdgarScraper(db)
        try:
            # Optionally scrape first
            if scrape_first:
                print(f"\n📥 Scraping {ticker} first...")
                filing = await scraper.scrape_company_by_ticker(
                    ticker=ticker,
                    forms=['10-K', '10-Q'],
                    upload_raw=True
                )
                filings = [filing]
                print(f"✓ Scraped filing: {filing.id}")
            else:
                # Get existing filings
                filings = await scraper.search_filings(ticker=ticker, limit=10)

                if not filings:
                    print(f"✗ No filings found for {ticker}", file=sys.stderr)
                    print(f"   Try running with --scrape-first")
                    return

            print(f"\n🔍 Found {len(filings)} filings for {ticker}")

            # Extract text from each
            for i, filing in enumerate(filings, 1):
                if filing.text_extracted:
                    print(f"\n[{i}/{len(filings)}] {filing.form} - Already extracted")
                    continue

                print(f"\n[{i}/{len(filings)}] Extracting from {filing.form} ({filing.filing_date})")

                try:
                    counts = await scraper.extract_filing_text(filing, upload_to_s3=True)

                    print(f"   ✓ Sections: {counts['sections']}, Notes: {counts['notes']}, "
                          f"Risks: {counts['risks']}, Policies: {counts['policies']}")

                except Exception as e:
                    print(f"   ✗ Failed: {e}", file=sys.stderr)
                    continue

            print(f"\n✓ Complete! Processed {len(filings)} filings")

        except Exception as e:
            print(f"\n✗ Error: {e}", file=sys.stderr)
            raise
        finally:
            await scraper.close()


async def show_training_data_stats():
    """Show statistics on available training data"""
    from sqlalchemy import text

    async with AsyncSessionLocal() as db:
        # Count sections
        result = await db.execute(text("""
            SELECT section_type, COUNT(*), SUM(word_count)
            FROM atlas.filing_sections
            GROUP BY section_type
            ORDER BY COUNT(*) DESC
        """))
        sections = result.fetchall()

        # Count notes
        result = await db.execute(text("""
            SELECT COUNT(*), SUM(word_count)
            FROM atlas.filing_notes
        """))
        notes = result.fetchone()

        # Count risks
        result = await db.execute(text("""
            SELECT COUNT(*)
            FROM atlas.filing_risk_factors
        """))
        risks = result.fetchone()

        print("\n📊 AI Training Data Statistics\n")
        print("=" * 60)

        print(f"\nFinancial Statement Notes:")
        print(f"  Total: {notes[0]:,} notes")
        print(f"  Words: {notes[1]:,}")

        print(f"\nRisk Factors:")
        print(f"  Total: {risks[0]:,} risk factors")

        print(f"\nFiling Sections:")
        for section_type, count, words in sections:
            print(f"  {section_type:30} {count:5,} sections  {words:10,} words")

        print("\n" + "=" * 60)


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Extract full text content from SEC filings for AI training',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('--filing-id', help='Filing UUID to extract text from')
    parser.add_argument('--ticker', help='Extract text from all filings for ticker')
    parser.add_argument('--scrape-first', action='store_true', help='Scrape filing before extracting text')
    parser.add_argument('--stats', action='store_true', help='Show training data statistics')

    args = parser.parse_args()

    try:
        if args.stats:
            asyncio.run(show_training_data_stats())
        elif args.filing_id:
            asyncio.run(extract_text_from_filing(args.filing_id))
        elif args.ticker:
            asyncio.run(extract_text_from_ticker(args.ticker, args.scrape_first))
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
