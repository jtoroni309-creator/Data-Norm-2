"""Unit tests for authentication logic"""
import pytest
from datetime import datetime, timedelta
from jose import jwt

from app.main import hash_password, verify_password, create_access_token
from app.config import settings
from app.schemas import RoleEnum


class TestPasswordHashing:
    """Test password hashing and verification"""

    def test_hash_password(self):
        """Test password is hashed correctly"""
        password = "TestPassword123!"
        hashed = hash_password(password)

        assert hashed != password
        assert hashed.startswith("$2b$")  # bcrypt prefix
        assert len(hashed) == 60  # bcrypt hash length

    def test_verify_password_correct(self):
        """Test password verification with correct password"""
        password = "TestPassword123!"
        hashed = hash_password(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password"""
        password = "TestPassword123!"
        hashed = hash_password(password)

        assert verify_password("WrongPassword456!", hashed) is False

    def test_same_password_different_hashes(self):
        """Test same password produces different hashes (salt)"""
        password = "TestPassword123!"
        hash1 = hash_password(password)
        hash2 = hash_password(password)

        assert hash1 != hash2
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True


class TestJWTTokens:
    """Test JWT token creation and validation"""

    def test_create_access_token(self):
        """Test JWT token creation"""
        data = {
            "sub": "user-123",
            "email": "test@example.com",
            "role": RoleEnum.PARTNER.value
        }

        token = create_access_token(data)

        assert isinstance(token, str)
        assert len(token) > 0

    def test_token_contains_correct_claims(self):
        """Test JWT token contains correct claims"""
        data = {
            "sub": "user-123",
            "email": "test@example.com",
            "role": RoleEnum.PARTNER.value
        }

        token = create_access_token(data)
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])

        assert payload["sub"] == "user-123"
        assert payload["email"] == "test@example.com"
        assert payload["role"] == "partner"
        assert payload["type"] == "access"
        assert "exp" in payload
        assert "iat" in payload

    def test_token_expiry(self):
        """Test JWT token has correct expiration"""
        data = {"sub": "user-123"}

        token = create_access_token(data, expires_delta=timedelta(minutes=30))
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])

        exp_time = datetime.fromtimestamp(payload["exp"])
        iat_time = datetime.fromtimestamp(payload["iat"])

        # Should expire in approximately 30 minutes
        delta = exp_time - iat_time
        assert 29 <= delta.total_seconds() / 60 <= 31

    def test_token_signature_verification_fails_with_wrong_secret(self):
        """Test JWT token verification fails with wrong secret"""
        data = {"sub": "user-123"}
        token = create_access_token(data)

        with pytest.raises(Exception):
            jwt.decode(token, "wrong-secret", algorithms=[settings.JWT_ALGORITHM])


class TestPasswordValidation:
    """Test password complexity validation"""

    def test_password_too_short(self):
        """Test password validation rejects short passwords"""
        from app.schemas import UserCreate
        from pydantic import ValidationError

        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                email="test@example.com",
                full_name="Test User",
                password="Short1!",  # Only 7 characters
                role=RoleEnum.STAFF
            )

        errors = exc_info.value.errors()
        assert any("at least 8 characters" in str(err) for err in errors)

    def test_password_no_uppercase(self):
        """Test password validation rejects passwords without uppercase"""
        from app.schemas import UserCreate
        from pydantic import ValidationError

        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                email="test@example.com",
                full_name="Test User",
                password="password123!",  # No uppercase
                role=RoleEnum.STAFF
            )

        errors = exc_info.value.errors()
        assert any("uppercase" in str(err) for err in errors)

    def test_password_no_lowercase(self):
        """Test password validation rejects passwords without lowercase"""
        from app.schemas import UserCreate
        from pydantic import ValidationError

        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                email="test@example.com",
                full_name="Test User",
                password="PASSWORD123!",  # No lowercase
                role=RoleEnum.STAFF
            )

        errors = exc_info.value.errors()
        assert any("lowercase" in str(err) for err in errors)

    def test_password_no_digit(self):
        """Test password validation rejects passwords without digits"""
        from app.schemas import UserCreate
        from pydantic import ValidationError

        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                email="test@example.com",
                full_name="Test User",
                password="Password!!!",  # No digit
                role=RoleEnum.STAFF
            )

        errors = exc_info.value.errors()
        assert any("digit" in str(err) for err in errors)

    def test_password_valid(self):
        """Test password validation accepts valid password"""
        from app.schemas import UserCreate

        user = UserCreate(
            email="test@example.com",
            full_name="Test User",
            password="ValidPass123!",
            role=RoleEnum.STAFF
        )

        assert user.password == "ValidPass123!"
