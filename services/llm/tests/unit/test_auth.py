"""Unit tests for JWT authentication in LLM Service"""
import pytest
from datetime import datetime, timedelta
from uuid import uuid4, UUID
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from jose import jwt

from app.main import get_current_user_id
from app.config import settings


class TestJWTValidation:
    """Test JWT token validation"""

    def create_test_token(self, user_id: UUID, expires_delta: timedelta = None) -> str:
        """Helper to create test JWT tokens"""
        to_encode = {
            "sub": str(user_id),
            "email": "test@example.com",
            "role": "partner",
        }

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(hours=settings.JWT_EXPIRY_HOURS)

        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access"
        })

        token = jwt.encode(
            to_encode,
            settings.JWT_SECRET,
            algorithm=settings.JWT_ALGORITHM
        )

        return token

    @pytest.mark.asyncio
    async def test_valid_token(self):
        """Test that valid JWT token is accepted and user ID is extracted"""
        user_id = uuid4()
        token = self.create_test_token(user_id)

        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=token
        )

        extracted_user_id = await get_current_user_id(credentials)

        assert extracted_user_id == user_id
        assert isinstance(extracted_user_id, UUID)

    @pytest.mark.asyncio
    async def test_expired_token(self):
        """Test that expired JWT token is rejected"""
        user_id = uuid4()
        # Create token that expired 1 hour ago
        token = self.create_test_token(user_id, expires_delta=timedelta(hours=-1))

        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=token
        )

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user_id(credentials)

        assert exc_info.value.status_code == 401
        assert "Could not validate credentials" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_invalid_signature(self):
        """Test that token with invalid signature is rejected"""
        user_id = uuid4()
        # Create token with different secret
        to_encode = {
            "sub": str(user_id),
            "email": "test@example.com",
            "exp": datetime.utcnow() + timedelta(hours=1),
        }

        token = jwt.encode(
            to_encode,
            "wrong-secret-key",
            algorithm=settings.JWT_ALGORITHM
        )

        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=token
        )

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user_id(credentials)

        assert exc_info.value.status_code == 401
        assert "Could not validate credentials" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_missing_sub_claim(self):
        """Test that token without 'sub' claim is rejected"""
        # Create token without 'sub' claim
        to_encode = {
            "email": "test@example.com",
            "role": "partner",
            "exp": datetime.utcnow() + timedelta(hours=1),
        }

        token = jwt.encode(
            to_encode,
            settings.JWT_SECRET,
            algorithm=settings.JWT_ALGORITHM
        )

        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=token
        )

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user_id(credentials)

        assert exc_info.value.status_code == 401
        assert "Could not validate credentials" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_invalid_uuid_format(self):
        """Test that token with invalid UUID format in 'sub' is rejected"""
        # Create token with invalid UUID
        to_encode = {
            "sub": "not-a-valid-uuid",
            "email": "test@example.com",
            "exp": datetime.utcnow() + timedelta(hours=1),
        }

        token = jwt.encode(
            to_encode,
            settings.JWT_SECRET,
            algorithm=settings.JWT_ALGORITHM
        )

        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=token
        )

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user_id(credentials)

        assert exc_info.value.status_code == 401
        assert "Could not validate credentials" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_malformed_token(self):
        """Test that malformed token is rejected"""
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="malformed.token.here"
        )

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user_id(credentials)

        assert exc_info.value.status_code == 401
        assert "Could not validate credentials" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_token_with_correct_algorithm(self):
        """Test that token with correct algorithm (HS256) is accepted"""
        user_id = uuid4()

        to_encode = {
            "sub": str(user_id),
            "email": "test@example.com",
            "exp": datetime.utcnow() + timedelta(hours=1),
        }

        token = jwt.encode(
            to_encode,
            settings.JWT_SECRET,
            algorithm="HS256"  # Explicitly use HS256
        )

        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=token
        )

        extracted_user_id = await get_current_user_id(credentials)
        assert extracted_user_id == user_id
