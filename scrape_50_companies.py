#!/usr/bin/env python3
"""
Script to scrape 50 S&P 500 companies from EDGAR
Runs inside the ingestion pod
"""

# Top 50 S&P 500 companies by market cap (excluding already scraped)
COMPANIES = [
    {'ticker': 'NVDA'},   # NVIDIA
    {'ticker': 'TSLA'},   # Tesla
    {'ticker': 'META'},   # Meta
    {'ticker': 'BRK.B'},  # Berkshire Hathaway
    {'ticker': 'V'},      # Visa
    {'ticker': 'JPM'},    # JPMorgan
    {'ticker': 'WMT'},    # Walmart
    {'ticker': 'UNH'},    # UnitedHealth
    {'ticker': 'MA'},     # Mastercard
    {'ticker': 'PG'},     # Procter & Gamble
    {'ticker': 'JNJ'},    # Johnson & Johnson
    {'ticker': 'HD'},     # Home Depot
    {'ticker': 'COST'},   # Costco
    {'ticker': 'NFLX'},   # Netflix
    {'ticker': 'ABBV'},   # AbbVie
    {'ticker': 'BAC'},    # Bank of America
    {'ticker': 'KO'},     # Coca-Cola
    {'ticker': 'AVGO'},   # Broadcom
    {'ticker': 'CRM'},    # Salesforce
    {'ticker': 'PEP'},    # PepsiCo
    {'ticker': 'TMO'},    # Thermo Fisher
    {'ticker': 'MRK'},    # Merck
    {'ticker': 'ORCL'},   # Oracle
    {'ticker': 'CVX'},    # Chevron
    {'ticker': 'AMD'},    # AMD
    {'ticker': 'ACN'},    # Accenture
    {'ticker': 'CSCO'},   # Cisco
    {'ticker': 'LIN'},    # Linde
    {'ticker': 'ABT'},    # Abbott
    {'ticker': 'MCD'},    # McDonald's
    {'ticker': 'DIS'},    # Disney
    {'ticker': 'WFC'},    # Wells Fargo
    {'ticker': 'ADBE'},   # Adobe
    {'ticker': 'INTC'},   # Intel
    {'ticker': 'VZ'},     # Verizon
    {'ticker': 'PM'},     # Philip Morris
    {'ticker': 'CMCSA'},  # Comcast
    {'ticker': 'NKE'},    # Nike
    {'ticker': 'TXN'},    # Texas Instruments
    {'ticker': 'COP'},    # ConocoPhillips
    {'ticker': 'UNP'},    # Union Pacific
    {'ticker': 'NEE'},    # NextEra Energy
    {'ticker': 'UPS'},    # UPS
    {'ticker': 'RTX'},    # Raytheon
    {'ticker': 'BMY'},    # Bristol Myers
    {'ticker': 'T'},      # AT&T
    {'ticker': 'QCOM'},   # Qualcomm
    {'ticker': 'HON'},    # Honeywell
    {'ticker': 'LMT'},    # Lockheed Martin
    {'ticker': 'LOW'},    # Lowe's
]

if __name__ == "__main__":
    import asyncio
    import sys
    import os

    # Add app directory to path
    sys.path.insert(0, '/app')

    from app.scraper import EdgarScraper
    from app.database import AsyncSessionLocal

    async def main():
        print(f"Starting scrape of {len(COMPANIES)} companies...")

        async with AsyncSessionLocal() as db:
            scraper = EdgarScraper(db)

            results = await scraper.scrape_multiple_companies(
                identifiers=COMPANIES,
                forms=['10-K', '10-Q'],  # Annual and quarterly reports
                upload_raw=True
            )

            print(f"\\nScraping complete!")
            print(f"Successfully scraped: {len(results)} companies")
            print(f"Failed: {len(COMPANIES) - len(results)} companies")

    asyncio.run(main())
