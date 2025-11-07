# EDGAR Data Scraper - Complete Guide

## Overview

The EDGAR scraper provides a complete pipeline for fetching SEC filing data, normalizing it, and storing it in the database with raw data archived to S3/MinIO.

## Features

- ✅ Fetch company facts from SEC EDGAR API
- ✅ Normalize XBRL data to flat structure
- ✅ Store filings and facts in PostgreSQL
- ✅ Upload raw JSON data to S3/MinIO
- ✅ Support for CIK and ticker lookup
- ✅ Batch scraping capabilities
- ✅ CLI tool and API endpoints
- ✅ Filter by form types (10-K, 10-Q, etc.)
- ✅ Filter by XBRL concepts

## Architecture

```
┌─────────────┐      ┌──────────────┐      ┌────────────┐
│ EDGAR API   │─────▶│   Scraper    │─────▶│ PostgreSQL │
│ (SEC.gov)   │      │   Pipeline   │      │ Database   │
└─────────────┘      └──────────────┘      └────────────┘
                            │
                            ▼
                     ┌──────────────┐
                     │  S3/MinIO    │
                     │  (Raw Data)  │
                     └──────────────┘
```

## Database Schema

The scraper uses the following tables (created by migration `002_ingestion_and_mapping_tables.sql`):

- **filings** - EDGAR filing metadata (CIK, ticker, form, dates)
- **facts** - Individual XBRL facts (financial data points)
- **chart_of_accounts** - Standard GAAP chart with XBRL mappings
- **trial_balances** - Trial balance imports
- **trial_balance_lines** - TB line items
- **mapping_suggestions** - ML-generated account mappings

## Quick Start

### 1. Run Database Migration

```bash
# Apply the migration
psql -U atlas -d atlas -f database/migrations/002_ingestion_and_mapping_tables.sql
```

### 2. Start Services

```bash
# Start PostgreSQL, Redis, MinIO
docker-compose up -d db redis minio

# Start ingestion service
cd services/ingestion
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

### 3. Scrape Your First Company

```bash
# Using CLI
cd services/ingestion
python scrape_edgar.py --ticker AAPL

# Using API
curl "http://localhost:8001/edgar/company-facts?ticker=AAPL"
```

## CLI Usage

### Basic Commands

```bash
# Scrape by ticker
python scrape_edgar.py --ticker AAPL

# Scrape by CIK
python scrape_edgar.py --cik 0000320193

# Scrape multiple companies
python scrape_edgar.py --tickers AAPL,MSFT,GOOGL

# Batch scrape from JSON file
python scrape_edgar.py --batch examples/companies_batch.json
```

### Filtering Options

```bash
# Filter by form type
python scrape_edgar.py --ticker AAPL --forms 10-K,10-Q

# Filter by XBRL concepts
python scrape_edgar.py --ticker AAPL --concepts us-gaap:Assets,us-gaap:Revenues

# Combined filters
python scrape_edgar.py --ticker AAPL --forms 10-K --concepts us-gaap:Assets
```

### Search Existing Filings

```bash
# Search by ticker
python scrape_edgar.py --search --ticker AAPL

# Search by CIK
python scrape_edgar.py --search --cik 0000320193

# Limit results
python scrape_edgar.py --search --ticker AAPL --limit 5
```

## API Endpoints

### GET /edgar/company-facts

Fetch and store company facts from EDGAR.

**Parameters:**
- `cik` (string, optional) - Company CIK
- `ticker` (string, optional) - Stock ticker
- `form` (string, optional) - Form type (10-K, 10-Q, etc.)
- `concepts` (array, optional) - XBRL concepts to filter
- `upload_raw` (boolean, optional) - Upload raw JSON to S3 (default: true)

**Example:**
```bash
curl "http://localhost:8001/edgar/company-facts?ticker=AAPL&form=10-K"
```

**Response:**
```json
{
  "filing": {
    "cik": "0000320193",
    "ticker": "AAPL",
    "company_name": "Apple Inc.",
    "form": "10-K",
    "filing_date": "2024-01-01",
    "source_uri": "https://data.sec.gov/..."
  },
  "facts": [
    {
      "concept": "us-gaap:Assets",
      "taxonomy": "us-gaap",
      "label": "Assets",
      "value": 352755000000,
      "unit": "USD",
      "end_date": "2023-09-30",
      "metadata": {...}
    }
  ]
}
```

### POST /pbc/upload

Upload PBC (Provided By Client) documents to S3.

**Parameters:**
- `engagement_id` (UUID, required) - Engagement ID
- `file` (file, required) - Document file
- `description` (string, optional) - Description

**Example:**
```bash
curl -X POST "http://localhost:8001/pbc/upload?engagement_id=<uuid>" \
  -F "file=@trial_balance.xlsx" \
  -F "description=Q3 Trial Balance"
```

### POST /trial-balance/import

Import trial balance from Excel/CSV.

**Parameters:**
- `engagement_id` (UUID, required) - Engagement ID
- `file` (file, required) - Trial balance file
- `period_end_date` (date, optional) - Period end date

## Python API Usage

```python
from app.database import AsyncSessionLocal
from app.scraper import EdgarScraper

async def scrape_example():
    async with AsyncSessionLocal() as db:
        scraper = EdgarScraper(db)

        try:
            # Scrape Apple
            filing = await scraper.scrape_company_by_ticker(
                ticker='AAPL',
                forms=['10-K'],
                concepts=['us-gaap:Assets', 'us-gaap:Revenues'],
                upload_raw=True
            )

            print(f"Filing ID: {filing.id}")
            print(f"Company: {filing.company_name}")

            # Get facts
            facts = await scraper.get_facts_by_filing(filing.id)
            print(f"Facts stored: {len(facts)}")

            # Search filings
            filings = await scraper.search_filings(
                ticker='AAPL',
                form='10-K',
                limit=10
            )

        finally:
            await scraper.close()

# Run
import asyncio
asyncio.run(scrape_example())
```

## Batch File Format

Create a JSON file with company identifiers:

```json
{
  "description": "My companies to scrape",
  "companies": [
    {"cik": "0000320193", "note": "Apple Inc."},
    {"ticker": "MSFT", "note": "Microsoft"},
    {"ticker": "GOOGL", "note": "Alphabet"}
  ]
}
```

Then scrape:
```bash
python scrape_edgar.py --batch my_companies.json
```

## Common XBRL Concepts

Here are common XBRL concepts you can filter by:

**Balance Sheet:**
- `us-gaap:Assets` - Total Assets
- `us-gaap:AssetsCurrent` - Current Assets
- `us-gaap:Liabilities` - Total Liabilities
- `us-gaap:StockholdersEquity` - Total Equity
- `us-gaap:Cash` - Cash
- `us-gaap:AccountsReceivableNet` - Accounts Receivable

**Income Statement:**
- `us-gaap:Revenues` - Total Revenue
- `us-gaap:CostOfRevenue` - Cost of Revenue
- `us-gaap:GrossProfit` - Gross Profit
- `us-gaap:OperatingExpenses` - Operating Expenses
- `us-gaap:NetIncomeLoss` - Net Income

**Cash Flow:**
- `us-gaap:NetCashProvidedByUsedInOperatingActivities`
- `us-gaap:NetCashProvidedByUsedInInvestingActivities`
- `us-gaap:NetCashProvidedByUsedInFinancingActivities`

## Data Storage

### PostgreSQL Tables

**Filings:**
```sql
SELECT * FROM atlas.filings WHERE ticker = 'AAPL' LIMIT 5;
```

**Facts:**
```sql
SELECT concept, value, unit, end_date
FROM atlas.facts
WHERE filing_id = '<uuid>'
ORDER BY concept;
```

**Chart of Accounts:**
```sql
SELECT account_code, account_name, xbrl_concept
FROM atlas.chart_of_accounts
WHERE account_type = 'asset';
```

### S3/MinIO Structure

```
atlas-binders/
├── edgar/
│   └── raw/
│       ├── AAPL/
│       │   └── 20240101_120000.json
│       ├── MSFT/
│       │   └── 20240101_120030.json
│       └── <CIK>/
│           └── <timestamp>.json
└── pbc/
    └── <engagement_id>/
        └── <filename>
```

## Troubleshooting

### Error: "Bucket not found"

Make sure MinIO is running:
```bash
docker-compose up -d minio
```

Check MinIO console at http://localhost:9001 (user: minio, pass: minio123)

### Error: "Table 'filings' does not exist"

Run the database migration:
```bash
psql -U atlas -d atlas -f database/migrations/002_ingestion_and_mapping_tables.sql
```

### Error: "SEC API rate limit exceeded"

SEC limits requests to 10 per second. The scraper includes delays, but for large batches:
- Spread scrapes over time
- Use batch mode with smaller groups
- Contact SEC for increased limits

### Error: "Ticker not found"

Some tickers may not be in SEC's database:
- Verify ticker on SEC website
- Try using CIK instead
- Check if company files with SEC (foreign companies may use different forms)

## Performance Tips

1. **Batch Processing**: Use batch mode for multiple companies
2. **Filter Concepts**: Only request needed XBRL concepts
3. **Raw Upload**: Set `upload_raw=False` if you don't need archival
4. **Database Indexes**: Ensure indexes exist (created by migration)
5. **Connection Pooling**: Reuse database sessions

## SEC EDGAR Resources

- [EDGAR API Documentation](https://www.sec.gov/edgar/sec-api-documentation)
- [Company Search](https://www.sec.gov/cgi-bin/browse-edgar)
- [XBRL Taxonomy](https://www.sec.gov/info/edgar/edgartaxonomies.shtml)
- [Filing Types](https://www.sec.gov/forms)

## Next Steps

1. **Trial Balance Mapping**: Use the normalize service to map TB accounts
2. **Analytics**: Run analytics on stored facts
3. **Automation**: Set up scheduled scraping with cron/Airflow
4. **Monitoring**: Add alerts for failed scrapes

## Support

For issues or questions:
- Check logs: `docker-compose logs ingestion`
- Review API docs: http://localhost:8001/docs
- Check database: `psql -U atlas -d atlas`
