"""
S3/MinIO Storage Client
Handles file uploads to object storage for PBC documents and raw EDGAR data
"""
import io
import logging
from typing import Optional, BinaryIO
from datetime import datetime, timedelta

import boto3
from botocore.exceptions import ClientError
from botocore.client import Config

from .config import settings

logger = logging.getLogger(__name__)


class StorageClient:
    """S3-compatible storage client for MinIO or AWS S3"""

    def __init__(self):
        """Initialize S3/MinIO client"""
        self.client = boto3.client(
            's3',
            endpoint_url=settings.S3_ENDPOINT if not settings.S3_USE_SSL else None,
            aws_access_key_id=settings.S3_ACCESS_KEY,
            aws_secret_access_key=settings.S3_SECRET_KEY,
            region_name=settings.S3_REGION,
            config=Config(signature_version='s3v4')
        )
        self.bucket = settings.S3_BUCKET

        # Ensure bucket exists
        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self):
        """Create bucket if it doesn't exist"""
        try:
            self.client.head_bucket(Bucket=self.bucket)
            logger.info(f"Bucket '{self.bucket}' exists")
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                logger.info(f"Creating bucket '{self.bucket}'")
                try:
                    self.client.create_bucket(Bucket=self.bucket)
                except ClientError as create_error:
                    logger.error(f"Failed to create bucket: {create_error}")
                    raise
            else:
                logger.error(f"Error checking bucket: {e}")
                raise

    def upload_file(
        self,
        file_content: bytes,
        key: str,
        content_type: Optional[str] = None,
        metadata: Optional[dict] = None
    ) -> str:
        """
        Upload file to S3/MinIO

        Args:
            file_content: File content as bytes
            key: S3 object key (path)
            content_type: MIME type of file
            metadata: Additional metadata to attach

        Returns:
            S3 URI (s3://bucket/key)
        """
        try:
            extra_args = {}

            if content_type:
                extra_args['ContentType'] = content_type

            if metadata:
                extra_args['Metadata'] = {k: str(v) for k, v in metadata.items()}

            # Upload file
            file_obj = io.BytesIO(file_content)
            self.client.upload_fileobj(
                file_obj,
                self.bucket,
                key,
                ExtraArgs=extra_args
            )

            s3_uri = f"s3://{self.bucket}/{key}"
            logger.info(f"Uploaded file to {s3_uri}")
            return s3_uri

        except ClientError as e:
            logger.error(f"Failed to upload file: {e}")
            raise

    def upload_fileobj(
        self,
        file_obj: BinaryIO,
        key: str,
        content_type: Optional[str] = None,
        metadata: Optional[dict] = None
    ) -> str:
        """
        Upload file object to S3/MinIO

        Args:
            file_obj: File-like object
            key: S3 object key (path)
            content_type: MIME type of file
            metadata: Additional metadata to attach

        Returns:
            S3 URI (s3://bucket/key)
        """
        try:
            extra_args = {}

            if content_type:
                extra_args['ContentType'] = content_type

            if metadata:
                extra_args['Metadata'] = {k: str(v) for k, v in metadata.items()}

            # Upload file object
            self.client.upload_fileobj(
                file_obj,
                self.bucket,
                key,
                ExtraArgs=extra_args
            )

            s3_uri = f"s3://{self.bucket}/{key}"
            logger.info(f"Uploaded file to {s3_uri}")
            return s3_uri

        except ClientError as e:
            logger.error(f"Failed to upload file: {e}")
            raise

    def upload_json(
        self,
        data: dict,
        key: str,
        metadata: Optional[dict] = None
    ) -> str:
        """
        Upload JSON data to S3/MinIO

        Args:
            data: Dictionary to upload as JSON
            key: S3 object key (path)
            metadata: Additional metadata to attach

        Returns:
            S3 URI (s3://bucket/key)
        """
        import json
        json_bytes = json.dumps(data, indent=2).encode('utf-8')
        return self.upload_file(
            json_bytes,
            key,
            content_type='application/json',
            metadata=metadata
        )

    def download_file(self, key: str) -> bytes:
        """
        Download file from S3/MinIO

        Args:
            key: S3 object key (path)

        Returns:
            File content as bytes
        """
        try:
            response = self.client.get_object(Bucket=self.bucket, Key=key)
            content = response['Body'].read()
            logger.info(f"Downloaded file from s3://{self.bucket}/{key}")
            return content

        except ClientError as e:
            logger.error(f"Failed to download file: {e}")
            raise

    def get_presigned_url(
        self,
        key: str,
        expiration: int = 3600,
        http_method: str = 'GET'
    ) -> str:
        """
        Generate presigned URL for file access

        Args:
            key: S3 object key (path)
            expiration: URL expiration in seconds (default 1 hour)
            http_method: HTTP method (GET, PUT, etc.)

        Returns:
            Presigned URL
        """
        try:
            method_map = {
                'GET': 'get_object',
                'PUT': 'put_object'
            }

            url = self.client.generate_presigned_url(
                method_map[http_method],
                Params={'Bucket': self.bucket, 'Key': key},
                ExpiresIn=expiration
            )

            logger.info(f"Generated presigned URL for {key}")
            return url

        except ClientError as e:
            logger.error(f"Failed to generate presigned URL: {e}")
            raise

    def delete_file(self, key: str):
        """
        Delete file from S3/MinIO

        Args:
            key: S3 object key (path)
        """
        try:
            self.client.delete_object(Bucket=self.bucket, Key=key)
            logger.info(f"Deleted file s3://{self.bucket}/{key}")

        except ClientError as e:
            logger.error(f"Failed to delete file: {e}")
            raise

    def list_files(self, prefix: str = '', max_keys: int = 1000) -> list[dict]:
        """
        List files in bucket with optional prefix

        Args:
            prefix: Key prefix to filter by
            max_keys: Maximum number of keys to return

        Returns:
            List of file metadata dictionaries
        """
        try:
            response = self.client.list_objects_v2(
                Bucket=self.bucket,
                Prefix=prefix,
                MaxKeys=max_keys
            )

            files = []
            for obj in response.get('Contents', []):
                files.append({
                    'key': obj['Key'],
                    'size': obj['Size'],
                    'last_modified': obj['LastModified'],
                    'etag': obj['ETag']
                })

            logger.info(f"Listed {len(files)} files with prefix '{prefix}'")
            return files

        except ClientError as e:
            logger.error(f"Failed to list files: {e}")
            raise

    def file_exists(self, key: str) -> bool:
        """
        Check if file exists in bucket

        Args:
            key: S3 object key (path)

        Returns:
            True if file exists, False otherwise
        """
        try:
            self.client.head_object(Bucket=self.bucket, Key=key)
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False
            raise


# Singleton instance
_storage_client: Optional[StorageClient] = None


def get_storage_client() -> StorageClient:
    """Get singleton storage client instance"""
    global _storage_client
    if _storage_client is None:
        _storage_client = StorageClient()
    return _storage_client
