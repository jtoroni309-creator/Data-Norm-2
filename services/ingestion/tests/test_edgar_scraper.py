"""
Tests for EDGAR Scraper
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import date

from app.edgar import EdgarClient
from app.scraper import EdgarScraper
from app.models import Filing, Fact


class TestEdgarClient:
    """Test EDGAR API client"""

    @pytest.fixture
    def client(self):
        """Create EDGAR client"""
        return EdgarClient(
            base_url="https://data.sec.gov",
            user_agent="Test Scraper test@example.com"
        )

    @pytest.mark.asyncio
    async def test_normalize_company_facts(self, client):
        """Test fact normalization"""
        company_data = {
            "cik": 320193,
            "entityName": "Apple Inc.",
            "facts": {
                "us-gaap": {
                    "Assets": {
                        "label": "Assets",
                        "description": "Total Assets",
                        "units": {
                            "USD": [
                                {
                                    "end": "2023-09-30",
                                    "val": 352755000000,
                                    "accn": "0000320193-23-000106",
                                    "fy": 2023,
                                    "fp": "FY",
                                    "form": "10-K",
                                    "filed": "2023-11-03"
                                }
                            ]
                        }
                    }
                }
            }
        }

        facts = client.normalize_company_facts(company_data)

        assert len(facts) == 1
        assert facts[0]["concept"] == "us-gaap:Assets"
        assert facts[0]["taxonomy"] == "us-gaap"
        assert facts[0]["label"] == "Assets"
        assert float(facts[0]["value"]) == 352755000000
        assert facts[0]["unit"] == "USD"
        assert facts[0]["end_date"] == date(2023, 9, 30)

    @pytest.mark.asyncio
    async def test_normalize_with_filter(self, client):
        """Test fact normalization with concept filter"""
        company_data = {
            "cik": 320193,
            "entityName": "Apple Inc.",
            "facts": {
                "us-gaap": {
                    "Assets": {
                        "label": "Assets",
                        "units": {
                            "USD": [{"end": "2023-09-30", "val": 352755000000, "form": "10-K"}]
                        }
                    },
                    "Revenues": {
                        "label": "Revenues",
                        "units": {
                            "USD": [{"end": "2023-09-30", "val": 383285000000, "form": "10-K"}]
                        }
                    }
                }
            }
        }

        # Filter by concept
        facts = client.normalize_company_facts(
            company_data,
            concepts=["us-gaap:Assets"]
        )

        assert len(facts) == 1
        assert facts[0]["concept"] == "us-gaap:Assets"

    @pytest.mark.asyncio
    async def test_normalize_with_form_filter(self, client):
        """Test fact normalization with form filter"""
        company_data = {
            "cik": 320193,
            "entityName": "Apple Inc.",
            "facts": {
                "us-gaap": {
                    "Assets": {
                        "label": "Assets",
                        "units": {
                            "USD": [
                                {"end": "2023-09-30", "val": 352755000000, "form": "10-K"},
                                {"end": "2023-06-30", "val": 340000000000, "form": "10-Q"}
                            ]
                        }
                    }
                }
            }
        }

        # Filter by form
        facts = client.normalize_company_facts(company_data, form="10-K")

        assert len(facts) == 1
        assert facts[0]["metadata"]["form"] == "10-K"


class TestEdgarScraper:
    """Test EDGAR scraper pipeline"""

    @pytest.fixture
    async def db_session(self):
        """Mock database session"""
        session = AsyncMock()
        session.add = Mock()
        session.commit = AsyncMock()
        session.flush = AsyncMock()
        session.refresh = AsyncMock()
        session.execute = AsyncMock()
        return session

    @pytest.fixture
    def scraper(self, db_session):
        """Create scraper instance"""
        return EdgarScraper(db_session)

    @pytest.mark.asyncio
    async def test_store_filing(self, scraper, db_session):
        """Test filing storage"""
        filing = await scraper._store_filing(
            cik="0000320193",
            company_name="Apple Inc.",
            ticker="AAPL",
            form="10-K",
            raw_data_uri="s3://bucket/key"
        )

        # Verify database operations
        assert db_session.add.called
        assert db_session.commit.called

    @pytest.mark.asyncio
    async def test_store_facts(self, scraper, db_session):
        """Test fact storage"""
        from uuid import uuid4

        filing_id = uuid4()
        normalized_facts = [
            {
                "concept": "us-gaap:Assets",
                "taxonomy": "us-gaap",
                "label": "Assets",
                "value": 352755000000,
                "unit": "USD",
                "end_date": date(2023, 9, 30),
                "metadata": {"form": "10-K"}
            }
        ]

        count = await scraper._store_facts(filing_id, normalized_facts)

        assert count == 1
        assert db_session.add.called
        assert db_session.commit.called

    @pytest.mark.asyncio
    @patch('app.scraper.EdgarClient')
    async def test_scrape_company_by_ticker(self, mock_edgar_client, scraper, db_session):
        """Test full scrape by ticker"""
        # Mock EDGAR client responses
        mock_client = AsyncMock()
        mock_client.get_company_facts_by_ticker.return_value = {
            "cik": 320193,
            "entityName": "Apple Inc.",
            "facts": {}
        }
        mock_client.normalize_company_facts.return_value = []

        mock_edgar_client.return_value = mock_client
        scraper.edgar_client = mock_client

        # Mock storage
        with patch('app.scraper.get_storage_client') as mock_storage:
            mock_storage.return_value.upload_json.return_value = "s3://bucket/key"

            # Mock query result
            mock_result = AsyncMock()
            mock_result.scalar_one_or_none.return_value = None
            db_session.execute.return_value = mock_result

            # Execute scrape
            await scraper.scrape_company_by_ticker("AAPL")

            # Verify EDGAR API was called
            mock_client.get_company_facts_by_ticker.assert_called_once_with("AAPL")


class TestStorageClient:
    """Test S3/MinIO storage client"""

    @pytest.fixture
    def storage_client(self):
        """Create storage client with mock boto3"""
        from app.storage import StorageClient

        with patch('app.storage.boto3') as mock_boto3:
            mock_s3 = Mock()
            mock_boto3.client.return_value = mock_s3

            # Mock bucket exists
            mock_s3.head_bucket.return_value = {}

            client = StorageClient()
            client.client = mock_s3
            return client

    def test_upload_file(self, storage_client):
        """Test file upload"""
        content = b"test content"
        key = "test/file.txt"

        s3_uri = storage_client.upload_file(
            content,
            key,
            content_type="text/plain",
            metadata={"test": "value"}
        )

        assert s3_uri == f"s3://{storage_client.bucket}/{key}"
        assert storage_client.client.upload_fileobj.called

    def test_upload_json(self, storage_client):
        """Test JSON upload"""
        data = {"key": "value", "number": 123}
        key = "test/data.json"

        s3_uri = storage_client.upload_json(data, key)

        assert s3_uri == f"s3://{storage_client.bucket}/{key}"
        assert storage_client.client.upload_fileobj.called

    def test_file_exists(self, storage_client):
        """Test file existence check"""
        # File exists
        storage_client.client.head_object.return_value = {}
        assert storage_client.file_exists("test/file.txt") is True

        # File doesn't exist
        from botocore.exceptions import ClientError
        error = ClientError({"Error": {"Code": "404"}}, "head_object")
        storage_client.client.head_object.side_effect = error
        assert storage_client.file_exists("test/missing.txt") is False


# Run tests with: pytest tests/test_edgar_scraper.py -v
