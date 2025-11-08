"""Database models for Accounting Integrations Service"""

from datetime import datetime, timedelta
from enum import Enum
from uuid import uuid4

from sqlalchemy import Column, String, DateTime, Text, JSON, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from cryptography.fernet import Fernet

from .database import Base
from .config import get_settings

settings = get_settings()

# Encryption for sensitive data (tokens)
cipher_suite = Fernet(settings.ENCRYPTION_KEY.encode()) if settings.ENCRYPTION_KEY else None


class ConnectionStatus(str, Enum):
    """Connection status"""
    ACTIVE = "active"
    EXPIRED = "expired"
    ERROR = "error"
    DISCONNECTED = "disconnected"


class Connection(Base):
    """
    OAuth connection to an accounting system.

    Stores encrypted access tokens and refresh tokens.
    """
    __tablename__ = "accounting_connections"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    organization_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Provider info
    provider = Column(String(50), nullable=False)  # quickbooks, xero, netsuite, sage
    provider_company_id = Column(String(255), nullable=False)  # realm_id, tenant_id, etc.

    # OAuth tokens (encrypted)
    access_token = Column(Text, nullable=False)
    refresh_token = Column(Text, nullable=True)
    token_expires_at = Column(DateTime, nullable=True)

    # Connection status
    status = Column(SQLEnum(ConnectionStatus), default=ConnectionStatus.ACTIVE)
    last_sync_at = Column(DateTime, nullable=True)
    last_error = Column(Text, nullable=True)

    # Provider-specific settings
    settings = Column(JSON, default={})

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, **kwargs):
        # Encrypt tokens before storing
        if "access_token" in kwargs and cipher_suite:
            kwargs["access_token"] = cipher_suite.encrypt(
                kwargs["access_token"].encode()
            ).decode()

        if "refresh_token" in kwargs and kwargs["refresh_token"] and cipher_suite:
            kwargs["refresh_token"] = cipher_suite.encrypt(
                kwargs["refresh_token"].encode()
            ).decode()

        super().__init__(**kwargs)

    @property
    def access_token(self) -> str:
        """Decrypt access token on read"""
        encrypted = self.__dict__.get("access_token")
        if encrypted and cipher_suite:
            return cipher_suite.decrypt(encrypted.encode()).decode()
        return encrypted

    @access_token.setter
    def access_token(self, value: str):
        """Encrypt access token on write"""
        if value and cipher_suite:
            self.__dict__["access_token"] = cipher_suite.encrypt(value.encode()).decode()
        else:
            self.__dict__["access_token"] = value

    @property
    def refresh_token(self) -> str:
        """Decrypt refresh token on read"""
        encrypted = self.__dict__.get("refresh_token")
        if encrypted and cipher_suite:
            return cipher_suite.decrypt(encrypted.encode()).decode()
        return encrypted

    @refresh_token.setter
    def refresh_token(self, value: str):
        """Encrypt refresh token on write"""
        if value and cipher_suite:
            self.__dict__["refresh_token"] = cipher_suite.encrypt(value.encode()).decode()
        else:
            self.__dict__["refresh_token"] = value

    def is_token_expired(self) -> bool:
        """Check if access token is expired"""
        if not self.token_expires_at:
            return False

        # Consider expired if within 5 minutes of expiry
        return datetime.utcnow() >= (self.token_expires_at - timedelta(minutes=5))
