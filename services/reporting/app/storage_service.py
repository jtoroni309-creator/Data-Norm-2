"""Storage service for S3/Azure Blob Storage"""
import logging
import io
from typing import Optional, BinaryIO
from datetime import datetime, timedelta
import boto3
from botocore.client import Config
from botocore.exceptions import ClientError

from .config import settings

logger = logging.getLogger(__name__)


class StorageService:
    """Service for storing and retrieving reports from cloud storage"""

    def __init__(self):
        self.backend = settings.STORAGE_BACKEND
        self._s3_client = None
        self._azure_client = None

    def _get_s3_client(self):
        """Get S3 client (works with AWS S3 and MinIO)"""
        if self._s3_client is None:
            self._s3_client = boto3.client(
                's3',
                endpoint_url=settings.S3_ENDPOINT,
                aws_access_key_id=settings.S3_ACCESS_KEY,
                aws_secret_access_key=settings.S3_SECRET_KEY,
                region_name=settings.S3_REGION,
                config=Config(signature_version='s3v4')
            )
        return self._s3_client

    def _get_azure_client(self):
        """Get Azure Blob Storage client"""
        if self._azure_client is None:
            from azure.storage.blob import BlobServiceClient

            if settings.AZURE_STORAGE_CONNECTION_STRING:
                self._azure_client = BlobServiceClient.from_connection_string(
                    settings.AZURE_STORAGE_CONNECTION_STRING
                )
            else:
                raise ValueError("Azure Storage connection string not configured")

        return self._azure_client

    async def upload_report(
        self,
        file_content: bytes,
        file_name: str,
        content_type: str = "application/pdf",
        metadata: Optional[dict] = None
    ) -> str:
        """
        Upload report to storage

        Args:
            file_content: File content as bytes
            file_name: Name of the file
            content_type: MIME type
            metadata: Optional metadata

        Returns:
            Storage path/URL
        """
        if self.backend == "azure":
            return await self._upload_to_azure(file_content, file_name, content_type, metadata)
        else:
            return await self._upload_to_s3(file_content, file_name, content_type, metadata)

    async def _upload_to_s3(
        self,
        file_content: bytes,
        file_name: str,
        content_type: str,
        metadata: Optional[dict]
    ) -> str:
        """Upload to S3/MinIO"""
        try:
            s3_client = self._get_s3_client()

            # Generate object key (path)
            object_key = f"reports/{datetime.now().strftime('%Y/%m/%d')}/{file_name}"

            # Prepare metadata
            s3_metadata = metadata or {}
            s3_metadata['uploaded_at'] = datetime.now().isoformat()

            # Upload
            s3_client.put_object(
                Bucket=settings.S3_BUCKET,
                Key=object_key,
                Body=file_content,
                ContentType=content_type,
                Metadata={k: str(v) for k, v in s3_metadata.items()},
                ServerSideEncryption='AES256'
            )

            logger.info(f"Uploaded to S3: {object_key}")

            return f"s3://{settings.S3_BUCKET}/{object_key}"

        except ClientError as e:
            logger.error(f"S3 upload failed: {e}")
            raise

    async def _upload_to_azure(
        self,
        file_content: bytes,
        file_name: str,
        content_type: str,
        metadata: Optional[dict]
    ) -> str:
        """Upload to Azure Blob Storage"""
        try:
            blob_service_client = self._get_azure_client()
            container_client = blob_service_client.get_container_client(
                settings.AZURE_STORAGE_CONTAINER
            )

            # Generate blob name (path)
            blob_name = f"reports/{datetime.now().strftime('%Y/%m/%d')}/{file_name}"

            # Prepare metadata
            azure_metadata = metadata or {}
            azure_metadata['uploaded_at'] = datetime.now().isoformat()

            # Upload
            blob_client = container_client.get_blob_client(blob_name)
            blob_client.upload_blob(
                file_content,
                overwrite=True,
                content_settings={'content_type': content_type},
                metadata={k: str(v) for k, v in azure_metadata.items()}
            )

            logger.info(f"Uploaded to Azure: {blob_name}")

            return f"azure://{settings.AZURE_STORAGE_CONTAINER}/{blob_name}"

        except Exception as e:
            logger.error(f"Azure upload failed: {e}")
            raise

    async def upload_to_worm(
        self,
        file_content: bytes,
        file_name: str,
        metadata: Optional[dict] = None
    ) -> str:
        """
        Upload to WORM (Write-Once-Read-Many) storage

        This is for final, immutable reports that meet audit compliance.

        Args:
            file_content: File content as bytes
            file_name: Name of the file
            metadata: Optional metadata

        Returns:
            WORM storage path
        """
        if self.backend == "azure":
            return await self._upload_to_azure_worm(file_content, file_name, metadata)
        else:
            return await self._upload_to_s3_worm(file_content, file_name, metadata)

    async def _upload_to_s3_worm(
        self,
        file_content: bytes,
        file_name: str,
        metadata: Optional[dict]
    ) -> str:
        """Upload to S3 with Object Lock (WORM)"""
        try:
            s3_client = self._get_s3_client()

            # Generate object key
            object_key = f"worm/{datetime.now().strftime('%Y/%m/%d')}/{file_name}"

            # Prepare metadata
            s3_metadata = metadata or {}
            s3_metadata['uploaded_at'] = datetime.now().isoformat()
            s3_metadata['retention_years'] = '7'

            # Calculate retention until date (7 years for audit compliance)
            retention_until = datetime.now() + timedelta(days=2555)

            # Upload with Object Lock
            s3_client.put_object(
                Bucket=settings.S3_WORM_BUCKET,
                Key=object_key,
                Body=file_content,
                ContentType='application/pdf',
                Metadata={k: str(v) for k, v in s3_metadata.items()},
                ServerSideEncryption='AES256',
                ObjectLockMode='COMPLIANCE',  # Compliance mode cannot be overridden
                ObjectLockRetainUntilDate=retention_until
            )

            logger.info(f"Uploaded to WORM storage: {object_key}")

            return f"s3://{settings.S3_WORM_BUCKET}/{object_key}"

        except ClientError as e:
            logger.error(f"WORM upload failed: {e}")
            raise

    async def _upload_to_azure_worm(
        self,
        file_content: bytes,
        file_name: str,
        metadata: Optional[dict]
    ) -> str:
        """Upload to Azure with immutability policy"""
        try:
            blob_service_client = self._get_azure_client()
            container_client = blob_service_client.get_container_client(
                settings.AZURE_WORM_CONTAINER
            )

            # Generate blob name
            blob_name = f"worm/{datetime.now().strftime('%Y/%m/%d')}/{file_name}"

            # Prepare metadata
            azure_metadata = metadata or {}
            azure_metadata['uploaded_at'] = datetime.now().isoformat()
            azure_metadata['retention_years'] = '7'

            # Upload
            blob_client = container_client.get_blob_client(blob_name)
            blob_client.upload_blob(
                file_content,
                overwrite=False,  # Cannot overwrite in WORM container
                content_settings={'content_type': 'application/pdf'},
                metadata={k: str(v) for k, v in azure_metadata.items()}
            )

            # Set immutability policy (managed by container policy)

            logger.info(f"Uploaded to Azure WORM storage: {blob_name}")

            return f"azure://{settings.AZURE_WORM_CONTAINER}/{blob_name}"

        except Exception as e:
            logger.error(f"Azure WORM upload failed: {e}")
            raise

    async def download_report(self, storage_path: str) -> bytes:
        """
        Download report from storage

        Args:
            storage_path: Storage path (s3:// or azure://)

        Returns:
            File content as bytes
        """
        if storage_path.startswith("azure://"):
            return await self._download_from_azure(storage_path)
        elif storage_path.startswith("s3://"):
            return await self._download_from_s3(storage_path)
        else:
            raise ValueError(f"Invalid storage path: {storage_path}")

    async def _download_from_s3(self, storage_path: str) -> bytes:
        """Download from S3"""
        try:
            # Parse path: s3://bucket/key
            parts = storage_path.replace("s3://", "").split("/", 1)
            bucket = parts[0]
            key = parts[1]

            s3_client = self._get_s3_client()

            response = s3_client.get_object(Bucket=bucket, Key=key)
            content = response['Body'].read()

            logger.info(f"Downloaded from S3: {storage_path}")

            return content

        except ClientError as e:
            logger.error(f"S3 download failed: {e}")
            raise

    async def _download_from_azure(self, storage_path: str) -> bytes:
        """Download from Azure"""
        try:
            # Parse path: azure://container/blob
            parts = storage_path.replace("azure://", "").split("/", 1)
            container = parts[0]
            blob_name = parts[1]

            blob_service_client = self._get_azure_client()
            container_client = blob_service_client.get_container_client(container)
            blob_client = container_client.get_blob_client(blob_name)

            downloader = blob_client.download_blob()
            content = downloader.readall()

            logger.info(f"Downloaded from Azure: {storage_path}")

            return content

        except Exception as e:
            logger.error(f"Azure download failed: {e}")
            raise

    async def generate_presigned_url(
        self,
        storage_path: str,
        expiration: int = 3600
    ) -> str:
        """
        Generate presigned URL for temporary access

        Args:
            storage_path: Storage path
            expiration: URL expiration in seconds

        Returns:
            Presigned URL
        """
        if storage_path.startswith("s3://"):
            return self._generate_s3_presigned_url(storage_path, expiration)
        elif storage_path.startswith("azure://"):
            return self._generate_azure_presigned_url(storage_path, expiration)
        else:
            raise ValueError(f"Invalid storage path: {storage_path}")

    def _generate_s3_presigned_url(self, storage_path: str, expiration: int) -> str:
        """Generate S3 presigned URL"""
        try:
            parts = storage_path.replace("s3://", "").split("/", 1)
            bucket = parts[0]
            key = parts[1]

            s3_client = self._get_s3_client()

            url = s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': bucket, 'Key': key},
                ExpiresIn=expiration
            )

            return url

        except ClientError as e:
            logger.error(f"Failed to generate presigned URL: {e}")
            raise

    def _generate_azure_presigned_url(self, storage_path: str, expiration: int) -> str:
        """Generate Azure SAS URL"""
        try:
            from azure.storage.blob import generate_blob_sas, BlobSasPermissions

            parts = storage_path.replace("azure://", "").split("/", 1)
            container = parts[0]
            blob_name = parts[1]

            blob_service_client = self._get_azure_client()

            sas_token = generate_blob_sas(
                account_name=blob_service_client.account_name,
                container_name=container,
                blob_name=blob_name,
                account_key=blob_service_client.credential.account_key,
                permission=BlobSasPermissions(read=True),
                expiry=datetime.utcnow() + timedelta(seconds=expiration)
            )

            url = f"{blob_service_client.url}/{container}/{blob_name}?{sas_token}"

            return url

        except Exception as e:
            logger.error(f"Failed to generate SAS URL: {e}")
            raise

    async def delete_report(self, storage_path: str) -> bool:
        """
        Delete report from storage (only works for non-WORM storage)

        Args:
            storage_path: Storage path

        Returns:
            True if successful
        """
        # Prevent deletion from WORM storage
        if 'worm' in storage_path.lower():
            raise ValueError("Cannot delete from WORM storage")

        if storage_path.startswith("s3://"):
            return await self._delete_from_s3(storage_path)
        elif storage_path.startswith("azure://"):
            return await self._delete_from_azure(storage_path)
        else:
            raise ValueError(f"Invalid storage path: {storage_path}")

    async def _delete_from_s3(self, storage_path: str) -> bool:
        """Delete from S3"""
        try:
            parts = storage_path.replace("s3://", "").split("/", 1)
            bucket = parts[0]
            key = parts[1]

            s3_client = self._get_s3_client()
            s3_client.delete_object(Bucket=bucket, Key=key)

            logger.info(f"Deleted from S3: {storage_path}")

            return True

        except ClientError as e:
            logger.error(f"S3 delete failed: {e}")
            raise

    async def _delete_from_azure(self, storage_path: str) -> bool:
        """Delete from Azure"""
        try:
            parts = storage_path.replace("azure://", "").split("/", 1)
            container = parts[0]
            blob_name = parts[1]

            blob_service_client = self._get_azure_client()
            container_client = blob_service_client.get_container_client(container)
            blob_client = container_client.get_blob_client(blob_name)

            blob_client.delete_blob()

            logger.info(f"Deleted from Azure: {storage_path}")

            return True

        except Exception as e:
            logger.error(f"Azure delete failed: {e}")
            raise


# Global storage service instance
storage_service = StorageService()
