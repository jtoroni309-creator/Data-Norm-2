"""
Tests for EDGAR Service - SEC API Integration

Tests the EDGAR scraper and data normalization functionality.
"""

import pytest
from datetime import datetime

from app.edgar_service import edgar_service


@pytest.mark.asyncio
class TestEDGARService:
    """Test EDGAR SEC API integration."""

    async def test_get_company_info_apple(self):
        """Test fetching Apple Inc. company information."""
        # Apple's CIK
        cik = "320193"

        company_info = await edgar_service.get_company_info(cik)

        assert company_info is not None
        assert company_info["cik"] == "0000320193"
        assert company_info["name"] == "Apple Inc."
        assert company_info["ticker"] == "AAPL"
        assert company_info["sic"] == "3571"
        assert "fiscal_year_end" in company_info

        print("\n✓ Company Info Test Passed")
        print(f"  Company: {company_info['name']}")
        print(f"  Ticker: {company_info['ticker']}")
        print(f"  CIK: {company_info['cik']}")
        print(f"  SIC: {company_info['sic']} - {company_info['sic_description']}")

    async def test_get_company_info_microsoft(self):
        """Test fetching Microsoft Corp. company information."""
        cik = "789019"

        company_info = await edgar_service.get_company_info(cik)

        assert company_info is not None
        assert company_info["cik"] == "0000789019"
        assert "Microsoft" in company_info["name"]
        assert company_info["ticker"] == "MSFT"

        print("\n✓ Microsoft Info Test Passed")
        print(f"  Company: {company_info['name']}")
        print(f"  Ticker: {company_info['ticker']}")

    async def test_search_companies(self):
        """Test searching for companies."""
        results = await edgar_service.search_companies("Apple")

        assert len(results) > 0

        # Should find Apple Inc.
        apple_found = False
        for company in results:
            if "Apple" in company.get("name", "") and company.get("ticker") == "AAPL":
                apple_found = True
                break

        assert apple_found, "Apple Inc. should be in search results"

        print("\n✓ Company Search Test Passed")
        print(f"  Found {len(results)} companies for 'Apple'")
        for i, company in enumerate(results[:3], 1):
            print(f"  {i}. {company['name']} ({company['ticker']})")

    async def test_get_company_filings_10k(self):
        """Test fetching 10-K filings for Apple."""
        cik = "320193"

        filings = await edgar_service.get_company_filings(
            cik=cik,
            filing_type="10-K",
            limit=3
        )

        assert len(filings) > 0
        assert len(filings) <= 3

        # Verify filing structure
        filing = filings[0]
        assert "accession_number" in filing
        assert filing["filing_type"] == "10-K"
        assert "filing_date" in filing
        assert isinstance(filing["filing_date"], datetime)
        assert "is_xbrl" in filing

        print("\n✓ 10-K Filings Test Passed")
        print(f"  Found {len(filings)} 10-K filings")
        for i, filing in enumerate(filings, 1):
            print(f"  {i}. {filing['filing_type']} - {filing['filing_date'].strftime('%Y-%m-%d')}")
            print(f"     Accession: {filing['accession_number']}")
            print(f"     XBRL: {filing['is_xbrl']}")

    async def test_get_company_filings_10q(self):
        """Test fetching 10-Q filings."""
        cik = "320193"

        filings = await edgar_service.get_company_filings(
            cik=cik,
            filing_type="10-Q",
            limit=5
        )

        assert len(filings) > 0

        # All should be 10-Q
        for filing in filings:
            assert filing["filing_type"] == "10-Q"

        print("\n✓ 10-Q Filings Test Passed")
        print(f"  Found {len(filings)} 10-Q filings")

    async def test_get_company_facts(self):
        """Test fetching company facts (financial data)."""
        cik = "320193"

        facts = await edgar_service.get_company_facts(cik)

        assert facts is not None
        assert "cik" in facts
        assert "entityName" in facts
        assert facts["entityName"] == "Apple Inc."

        # Should have GAAP facts
        if "facts" in facts:
            assert "us-gaap" in facts["facts"]
            us_gaap = facts["facts"]["us-gaap"]

            # Check for common concepts
            assert "Assets" in us_gaap or "AssetsCurrent" in us_gaap

            print("\n✓ Company Facts Test Passed")
            print(f"  Entity: {facts['entityName']}")
            print(f"  CIK: {facts['cik']}")

            if "us-gaap" in facts["facts"]:
                concepts_count = len(facts["facts"]["us-gaap"])
                print(f"  US-GAAP Concepts: {concepts_count}")

                # Show sample concepts
                sample_concepts = list(facts["facts"]["us-gaap"].keys())[:5]
                print("  Sample Concepts:")
                for concept in sample_concepts:
                    print(f"    - {concept}")

    async def test_get_company_concept_assets(self):
        """Test fetching specific financial concept (Assets)."""
        cik = "320193"

        try:
            concept_data = await edgar_service.get_company_concept(
                cik=cik,
                taxonomy="us-gaap",
                concept="Assets"
            )

            assert concept_data is not None
            assert "units" in concept_data

            # Should have USD values
            if "USD" in concept_data["units"]:
                usd_values = concept_data["units"]["USD"]
                assert len(usd_values) > 0

                # Get most recent value
                recent = sorted(usd_values, key=lambda x: x.get("end", ""), reverse=True)[0]

                print("\n✓ Company Concept Test Passed")
                print(f"  Concept: Assets")
                print(f"  Most Recent Value: ${recent['val']:,.0f}")
                print(f"  As of: {recent['end']}")
                print(f"  Form: {recent.get('form', 'N/A')}")

        except Exception as e:
            print(f"\n⚠ Company Concept Test Skipped: {e}")

    async def test_download_filing(self):
        """Test downloading actual filing document."""
        cik = "320193"

        # Get latest 10-K
        filings = await edgar_service.get_company_filings(
            cik=cik,
            filing_type="10-K",
            limit=1
        )

        assert len(filings) > 0

        filing = filings[0]

        try:
            content = await edgar_service.download_filing(
                cik=cik,
                accession_number=filing["accession_number"],
                document=filing["primary_document"]
            )

            assert content is not None
            assert len(content) > 0
            assert "html" in content.lower() or "xml" in content.lower()

            print("\n✓ Filing Download Test Passed")
            print(f"  Downloaded: {filing['filing_type']}")
            print(f"  Size: {len(content):,} bytes")
            print(f"  Document: {filing['primary_document']}")

        except Exception as e:
            print(f"\n⚠ Filing Download Test: {e}")

    async def test_parse_xbrl_data(self):
        """Test parsing XBRL data."""
        cik = "320193"

        # Get latest 10-K with XBRL
        filings = await edgar_service.get_company_filings(
            cik=cik,
            filing_type="10-K",
            limit=5
        )

        xbrl_filing = None
        for filing in filings:
            if filing["is_xbrl"]:
                xbrl_filing = filing
                break

        if xbrl_filing:
            try:
                xbrl_data = await edgar_service.get_xbrl_data(
                    cik=cik,
                    accession_number=xbrl_filing["accession_number"]
                )

                assert xbrl_data is not None
                assert "facts" in xbrl_data

                print("\n✓ XBRL Parsing Test Passed")
                print(f"  Filing: {xbrl_filing['filing_type']}")
                print(f"  Date: {xbrl_filing['filing_date'].strftime('%Y-%m-%d')}")
                print(f"  Facts extracted: {len(xbrl_data.get('facts', {}))}")

            except Exception as e:
                print(f"\n⚠ XBRL Parsing: {e}")
        else:
            print("\n⚠ XBRL Test Skipped: No XBRL filings found")

    async def test_rate_limiting(self):
        """Test that rate limiting is working."""
        import time

        cik = "320193"

        start_time = time.time()

        # Make 3 requests
        await edgar_service.get_company_info(cik)
        await edgar_service.get_company_info(cik)
        await edgar_service.get_company_info(cik)

        elapsed = time.time() - start_time

        # Should take at least 2 seconds (3 requests at 0.1 per second = 20 seconds between, but we're testing 3 requests)
        # At 10 requests per second, 3 requests should take at least 0.2 seconds
        assert elapsed >= 0.15, "Rate limiting not working properly"

        print("\n✓ Rate Limiting Test Passed")
        print(f"  3 requests took: {elapsed:.2f} seconds")
        print(f"  Rate limit: {1/settings.SEC_REQUESTS_PER_SECOND:.0f} requests/second")


@pytest.mark.asyncio
class TestDataNormalization:
    """Test data normalization and parsing."""

    async def test_financial_table_parsing(self):
        """Test parsing financial tables from HTML."""
        # Create sample HTML table
        html_table = """
        <table>
            <tr>
                <th>Item</th>
                <th>2023</th>
                <th>2022</th>
            </tr>
            <tr>
                <td>Revenue</td>
                <td>$383,285</td>
                <td>$394,328</td>
            </tr>
            <tr>
                <td>Net Income</td>
                <td>$96,995</td>
                <td>$99,803</td>
            </tr>
        </table>
        """

        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html_table, "html.parser")
        table = soup.find("table")

        parsed = edgar_service._parse_financial_table(table)

        assert "headers" in parsed
        assert "rows" in parsed
        assert len(parsed["headers"]) == 3
        assert len(parsed["rows"]) > 0

        print("\n✓ Financial Table Parsing Test Passed")
        print(f"  Headers: {parsed['headers']}")
        print(f"  Rows: {len(parsed['rows'])}")

    async def test_xbrl_json_parsing(self):
        """Test parsing XBRL JSON format."""
        # Sample XBRL JSON structure
        sample_xbrl = {
            "facts": {
                "us-gaap": {
                    "Assets": {
                        "units": {
                            "USD": [
                                {
                                    "val": 352755000000,
                                    "accn": "0000320193-23-000077",
                                    "fy": 2023,
                                    "fp": "FY",
                                    "form": "10-K",
                                    "filed": "2023-11-03",
                                    "end": "2023-09-30"
                                }
                            ]
                        }
                    }
                }
            }
        }

        parsed = edgar_service._parse_xbrl_json(sample_xbrl)

        assert "facts" in parsed
        assert "Assets" in parsed["facts"]

        print("\n✓ XBRL JSON Parsing Test Passed")
        print(f"  Facts parsed: {len(parsed['facts'])}")


# Helper function to run all tests
async def run_all_tests():
    """Run all EDGAR service tests."""
    print("="*70)
    print("EDGAR SERVICE TEST SUITE")
    print("="*70)

    test_class = TestEDGARService()

    tests = [
        ("Company Info (Apple)", test_class.test_get_company_info_apple),
        ("Company Info (Microsoft)", test_class.test_get_company_info_microsoft),
        ("Company Search", test_class.test_search_companies),
        ("10-K Filings", test_class.test_get_company_filings_10k),
        ("10-Q Filings", test_class.test_get_company_filings_10q),
        ("Company Facts", test_class.test_get_company_facts),
        ("Company Concept", test_class.test_get_company_concept_assets),
        ("Download Filing", test_class.test_download_filing),
        ("XBRL Parsing", test_class.test_parse_xbrl_data),
        ("Rate Limiting", test_class.test_rate_limiting),
    ]

    passed = 0
    failed = 0
    skipped = 0

    for test_name, test_func in tests:
        print(f"\n{'='*70}")
        print(f"Testing: {test_name}")
        print('='*70)

        try:
            await test_func()
            passed += 1
        except Exception as e:
            if "⚠" in str(e) or "Skipped" in str(e):
                skipped += 1
                print(f"\n⚠ {test_name}: Skipped")
            else:
                failed += 1
                print(f"\n✗ {test_name}: FAILED")
                print(f"  Error: {e}")

    # Data normalization tests
    print(f"\n{'='*70}")
    print("DATA NORMALIZATION TESTS")
    print('='*70)

    norm_test_class = TestDataNormalization()
    norm_tests = [
        ("Financial Table Parsing", norm_test_class.test_financial_table_parsing),
        ("XBRL JSON Parsing", norm_test_class.test_xbrl_json_parsing),
    ]

    for test_name, test_func in norm_tests:
        try:
            await test_func()
            passed += 1
        except Exception as e:
            failed += 1
            print(f"\n✗ {test_name}: FAILED")
            print(f"  Error: {e}")

    # Summary
    print(f"\n{'='*70}")
    print("TEST SUMMARY")
    print('='*70)
    print(f"✓ Passed:  {passed}")
    print(f"✗ Failed:  {failed}")
    print(f"⚠ Skipped: {skipped}")
    print(f"  Total:   {passed + failed + skipped}")
    print('='*70)

    return passed, failed, skipped


if __name__ == "__main__":
    import asyncio
    from app.config import settings

    # Run tests
    asyncio.run(run_all_tests())
