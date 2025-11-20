#!/usr/bin/env python3
"""
EDGAR Scraper - Top 50 Companies for LLM Training
Scrapes financial data from SEC EDGAR for the 50 largest US public companies

Execution:
    python scripts/scrape_50_companies.py

Environment Variables:
    DATABASE_URL - PostgreSQL connection string
    AZURE_STORAGE_CONNECTION_STRING - Azure Blob Storage connection
"""
import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.ingestion.app.database import AsyncSessionLocal
from services.ingestion.app.scraper import EdgarScraper


# Top 50 US Public Companies by Market Cap (November 2024)
TOP_50_COMPANIES = [
    # Big Tech
    {"ticker": "AAPL", "name": "Apple Inc.", "cik": "320193"},
    {"ticker": "MSFT", "name": "Microsoft Corporation", "cik": "789019"},
    {"ticker": "GOOGL", "name": "Alphabet Inc.", "cik": "1652044"},
    {"ticker": "AMZN", "name": "Amazon.com Inc.", "cik": "1018724"},
    {"ticker": "NVDA", "name": "NVIDIA Corporation", "cik": "1045810"},
    {"ticker": "META", "name": "Meta Platforms Inc.", "cik": "1326801"},
    {"ticker": "TSLA", "name": "Tesla Inc.", "cik": "1318605"},

    # Finance
    {"ticker": "BRK.B", "name": "Berkshire Hathaway Inc.", "cik": "1067983"},
    {"ticker": "JPM", "name": "JPMorgan Chase & Co.", "cik": "19617"},
    {"ticker": "V", "name": "Visa Inc.", "cik": "1403161"},
    {"ticker": "MA", "name": "Mastercard Inc.", "cik": "1141391"},
    {"ticker": "BAC", "name": "Bank of America Corp", "cik": "70858"},
    {"ticker": "WFC", "name": "Wells Fargo & Company", "cik": "72971"},
    {"ticker": "GS", "name": "Goldman Sachs Group Inc.", "cik": "886982"},
    {"ticker": "MS", "name": "Morgan Stanley", "cik": "895421"},

    # Healthcare & Pharma
    {"ticker": "UNH", "name": "UnitedHealth Group Inc.", "cik": "731766"},
    {"ticker": "JNJ", "name": "Johnson & Johnson", "cik": "200406"},
    {"ticker": "LLY", "name": "Eli Lilly and Company", "cik": "59478"},
    {"ticker": "PFE", "name": "Pfizer Inc.", "cik": "78003"},
    {"ticker": "ABBV", "name": "AbbVie Inc.", "cik": "1551152"},
    {"ticker": "MRK", "name": "Merck & Co. Inc.", "cik": "310158"},

    # Consumer & Retail
    {"ticker": "WMT", "name": "Walmart Inc.", "cik": "104169"},
    {"ticker": "PG", "name": "Procter & Gamble Co.", "cik": "80424"},
    {"ticker": "HD", "name": "Home Depot Inc.", "cik": "354950"},
    {"ticker": "COST", "name": "Costco Wholesale Corp.", "cik": "909832"},
    {"ticker": "KO", "name": "Coca-Cola Company", "cik": "21344"},
    {"ticker": "PEP", "name": "PepsiCo Inc.", "cik": "77476"},
    {"ticker": "MCD", "name": "McDonald's Corp.", "cik": "63908"},
    {"ticker": "NKE", "name": "Nike Inc.", "cik": "320187"},

    # Industrial & Energy
    {"ticker": "XOM", "name": "Exxon Mobil Corp.", "cik": "34088"},
    {"ticker": "CVX", "name": "Chevron Corporation", "cik": "93410"},
    {"ticker": "BA", "name": "Boeing Company", "cik": "12927"},
    {"ticker": "CAT", "name": "Caterpillar Inc.", "cik": "18230"},

    # Telecom & Media
    {"ticker": "NFLX", "name": "Netflix Inc.", "cik": "1065280"},
    {"ticker": "DIS", "name": "Walt Disney Company", "cik": "1744489"},
    {"ticker": "CMCSA", "name": "Comcast Corp.", "cik": "1166691"},
    {"ticker": "T", "name": "AT&T Inc.", "cik": "732717"},
    {"ticker": "VZ", "name": "Verizon Communications", "cik": "732712"},

    # Technology Hardware & Software
    {"ticker": "ORCL", "name": "Oracle Corporation", "cik": "1341439"},
    {"ticker": "CSCO", "name": "Cisco Systems Inc.", "cik": "858877"},
    {"ticker": "INTC", "name": "Intel Corporation", "cik": "50863"},
    {"ticker": "AMD", "name": "Advanced Micro Devices", "cik": "2488"},
    {"ticker": "CRM", "name": "Salesforce Inc.", "cik": "1108524"},
    {"ticker": "ADBE", "name": "Adobe Inc.", "cik": "796343"},

    # Other Key Industries
    {"ticker": "UPS", "name": "United Parcel Service", "cik": "1090727"},
    {"ticker": "PM", "name": "Philip Morris International", "cik": "1413329"},
    {"ticker": "TMO", "name": "Thermo Fisher Scientific", "cik": "97745"},
    {"ticker": "ABT", "name": "Abbott Laboratories", "cik": "1800"},
    {"ticker": "DHR", "name": "Danaher Corporation", "cik": "313616"},
    {"ticker": "TXN", "name": "Texas Instruments Inc.", "cik": "97476"},
]


async def scrape_company_data(scraper: EdgarScraper, company: dict, progress: int, total: int):
    """Scrape a single company's data"""
    ticker = company["ticker"]
    name = company["name"]
    cik = company["cik"]

    print(f"\n{'='*80}")
    print(f"[{progress}/{total}] Scraping {ticker} - {name}")
    print(f"CIK: {cik}")
    print(f"{'='*80}")

    try:
        # Scrape by CIK (more reliable than ticker)
        filing = await scraper.scrape_company_by_cik(
            cik=cik,
            forms=["10-K", "10-Q"],  # Annual and Quarterly reports
            concepts=None,  # Get all concepts
            upload_raw=True  # Upload to Azure Blob Storage
        )

        if filing:
            print(f"✅ SUCCESS: {ticker}")
            print(f"   Company: {filing.company_name}")
            print(f"   Filing ID: {filing.id}")
            print(f"   Form: {filing.form}")
            print(f"   Filing Date: {filing.filing_date}")
            if filing.raw_data_s3_uri:
                print(f"   Raw Data: {filing.raw_data_s3_uri}")

            # Get fact count
            facts = await scraper.get_facts_by_filing(filing.id)
            print(f"   Facts Stored: {len(facts)}")

            return {
                "ticker": ticker,
                "name": name,
                "cik": cik,
                "status": "success",
                "filing_id": str(filing.id),
                "facts_count": len(facts),
            }
        else:
            print(f"⚠️  WARNING: No filings found for {ticker}")
            return {
                "ticker": ticker,
                "name": name,
                "cik": cik,
                "status": "no_filings",
            }

    except Exception as e:
        print(f"❌ ERROR scraping {ticker}: {e}")
        return {
            "ticker": ticker,
            "name": name,
            "cik": cik,
            "status": "error",
            "error": str(e),
        }


async def main():
    """Main execution function"""
    print("\n" + "="*80)
    print("EDGAR SCRAPER - TOP 50 COMPANIES FOR LLM TRAINING")
    print("="*80)
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Companies to Scrape: {len(TOP_50_COMPANIES)}")
    print(f"Database: {os.getenv('DATABASE_URL', 'Not configured')[:50]}...")
    print(f"Azure Storage: {'Configured' if os.getenv('AZURE_STORAGE_CONNECTION_STRING') else 'Not configured'}")
    print("="*80 + "\n")

    results = []
    success_count = 0
    error_count = 0
    no_filing_count = 0

    async with AsyncSessionLocal() as db:
        scraper = EdgarScraper(db)

        try:
            for i, company in enumerate(TOP_50_COMPANIES, 1):
                result = await scrape_company_data(scraper, company, i, len(TOP_50_COMPANIES))
                results.append(result)

                if result["status"] == "success":
                    success_count += 1
                elif result["status"] == "error":
                    error_count += 1
                else:
                    no_filing_count += 1

                # Progress update
                print(f"\nProgress: {i}/{len(TOP_50_COMPANIES)} companies processed")
                print(f"Success: {success_count} | Errors: {error_count} | No Filings: {no_filing_count}")

                # Rate limiting - SEC allows 10 requests per second
                await asyncio.sleep(0.2)

        finally:
            await scraper.close()

    # Final Report
    print("\n" + "="*80)
    print("SCRAPING COMPLETE - FINAL REPORT")
    print("="*80)
    print(f"End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\nResults:")
    print(f"  ✅ Successful: {success_count}/{len(TOP_50_COMPANIES)} ({success_count/len(TOP_50_COMPANIES)*100:.1f}%)")
    print(f"  ⚠️  No Filings: {no_filing_count}/{len(TOP_50_COMPANIES)}")
    print(f"  ❌ Errors: {error_count}/{len(TOP_50_COMPANIES)}")

    if error_count > 0:
        print(f"\nFailed Companies:")
        for result in results:
            if result["status"] == "error":
                print(f"  - {result['ticker']}: {result.get('error', 'Unknown error')}")

    # Calculate total facts
    total_facts = sum(r.get("facts_count", 0) for r in results if r["status"] == "success")
    print(f"\nTotal Financial Facts Collected: {total_facts:,}")
    print(f"Average Facts per Company: {total_facts/success_count if success_count > 0 else 0:,.0f}")

    print("\n" + "="*80)
    print("✅ Data ready for LLM training pipeline")
    print("="*80 + "\n")

    return results


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Scraping interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
