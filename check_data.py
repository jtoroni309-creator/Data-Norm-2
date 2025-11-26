#!/usr/bin/env python3
"""
Quick script to check existing scraped data in the database
"""
import asyncio
import sys
sys.path.insert(0, '/app')

from app.database import AsyncSessionLocal
from sqlalchemy import text

async def main():
    async with AsyncSessionLocal() as db:
        # Check filings
        result = await db.execute(text("""
            SELECT
                COUNT(*) as total_filings,
                COUNT(DISTINCT cik) as unique_companies
            FROM atlas.filings
        """))
        row = result.fetchone()

        print(f"\n=== DATABASE STATUS ===")
        print(f"Total SEC Filings: {row[0]}")
        print(f"Unique Companies (CIK): {row[1]}")

        # Check recent filings
        result2 = await db.execute(text("""
            SELECT cik, company_name, form_type, filing_date
            FROM atlas.filings
            ORDER BY filing_date DESC
            LIMIT 5
        """))

        print(f"\n=== RECENT FILINGS ===")
        for row in result2.fetchall():
            print(f"CIK {row[0]}: {row[1]} - {row[2]} ({row[3]})")

asyncio.run(main())
