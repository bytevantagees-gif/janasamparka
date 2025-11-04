"""
Unit tests for authentication functionality
"""
import pytest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException
from jose import JWTError
from uuid import uuid4

from app.core.auth import get_current_user, require_auth, require_role, get_user_constituency_id
from app.models.user import User, UserRole


class TestAuthentication:
    """Test authentication utilities"""
    
    def test_get_current_user_valid_token(self, test_db, test_admin_user):
        """Test getting current user with valid token"""
        # Mock JWT decode
        with patch('app.core.auth.jwt.decode') as mock_decode:
            mock_decode.return_value = {"sub": str(test_admin_user.id)}
            
            # Mock HTTPBearer credentials
            mock_credentials = MagicMock()
            mock_credentials.credentials = "valid_token"
            
            # Mock get_db dependency
            with patch('app.core.auth.get_db') as mock_get_db:
                mock_get_db.return_value = test_db
                
                user = get_current_user(mock_credentials, test_db)
                assert user is not None
                assert user.id == test_admin_user.id
    
    def test_get_current_user_invalid_token(self, test_db):
        """Test getting current user with invalid token"""
        # Mock JWT decode to raise error
        with patch('app.core.auth.jwt.decode', side_effect=JWTError("Invalid token")):
            # Mock HTTPBearer credentials
            mock_credentials = MagicMock()
            mock_credentials.credentials = "invalid_token"
            
            user = get_current_user(mock_credentials, test_db)
            assert user is None
    
    def test_get_current_user_no_credentials(self, test_db):
        """Test getting current user with no credentials"""
        user = get_current_user(None, test_db)
        assert user is None
    
    def test_require_auth_valid_user(self, test_admin_user):
        """Test require_auth with valid user"""
        with patch('app.core.auth.get_current_user', return_value=test_admin_user):
            user = require_auth()
            assert user == test_admin_user
    
    def test_require_auth_no_user(self):
        """Test require_auth with no user raises exception"""
        with patch('app.core.auth.get_current_user', return_value=None):
            with pytest.raises(HTTPException) as exc_info:
                require_auth()
            assert exc_info.value.status_code == 401
            assert exc_info.value.detail == "Not authenticated"
    
    def test_require_role_valid(self, test_admin_user):
        """Test require_role with valid role"""
        with patch('app.core.auth.require_auth', return_value=test_admin_user):
            role_checker = require_role(UserRole.ADMIN, UserRole.MLA)
            user = role_checker()
            assert user == test_admin_user
    
    def test_require_role_invalid(self, test_citizen_user):
        """Test require_role with invalid role"""
        with patch('app.core.auth.require_auth', return_value=test_citizen_user):
            role_checker = require_role(UserRole.ADMIN)
            with pytest.raises(HTTPException) as exc_info:
                role_checker()
            assert exc_info.value.status_code == 403
            assert "Access denied" in exc_info.value.detail
    
    def test_get_user_constituency_id_admin(self, test_admin_user):
        """Test constituency ID for admin (should be None)"""
        with patch('app.core.auth.get_current_user', return_value=test_admin_user):
            constituency_id = get_user_constituency_id()
            assert constituency_id is None
    
    def test_get_user_constituency_id_mla(self, test_mla_user):
        """Test constituency ID for MLA (should be their constituency)"""
        with patch('app.core.auth.get_current_user', return_value=test_mla_user):
            constituency_id = get_user_constituency_id()
            assert constituency_id == test_mla_user.constituency_id
    
    def test_get_user_constituency_id_no_auth(self):
        """Test constituency ID with no authentication"""
        with patch('app.core.auth.get_current_user', return_value=None):
            constituency_id = get_user_constituency_id()
            assert constituency_id is None


class TestTokenGeneration:
    """Test JWT token generation and validation"""
    
    def test_token_creation(self):
        """Test JWT token creation"""
        from app.core.auth import jwt, settings
        from datetime import datetime, timedelta
        
        user_id = str(uuid4())
        expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        expire = datetime.utcnow() + expires_delta
        
        payload = {
            "sub": user_id,
            "exp": expire,
            "iat": datetime.utcnow()
        }
        
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        assert token is not None
        assert isinstance(token, str)
    
    def test_token_validation(self):
        """Test JWT token validation"""
        from app.core.auth import jwt, settings
        from datetime import datetime, timedelta
        
        user_id = str(uuid4())
        expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        expire = datetime.utcnow() + expires_delta
        
        payload = {
            "sub": user_id,
            "exp": expire,
            "iat": datetime.utcnow()
        }
        
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        
        assert decoded["sub"] == user_id
        assert "exp" in decoded
    
    def test_token_expiry(self):
        """Test expired token validation"""
        from app.core.auth import jwt, settings
        from datetime import datetime, timedelta
        
        user_id = str(uuid4())
        # Create expired token
        expire = datetime.utcnow() - timedelta(minutes=1)
        
        payload = {
            "sub": user_id,
            "exp": expire,
            "iat": datetime.utcnow() - timedelta(minutes=2)
        }
        
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        
        with pytest.raises(JWTError):
            jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])


class TestOTPGeneration:
    """Test OTP generation and validation"""
    
    def test_otp_generation_length(self):
        """Test OTP generation with correct length"""
        from app.routers.auth import generate_otp
        
        otp = generate_otp()
        assert len(otp) == 6
        assert otp.isdigit()
    
    def test_otp_uniqueness(self):
        """Test OTP generation produces unique values"""
        from app.routers.auth import generate_otp
        
        otps = [generate_otp() for _ in range(100)]
        unique_otps = set(otps)
        
        # Should have high uniqueness (allowing some collisions)
        assert len(unique_otps) > 90
    
    def test_otp_validation_valid(self):
        """Test OTP validation with correct OTP"""
        from app.routers.auth import validate_otp
        
        # Mock OTP storage
        mock_otp_storage = {"+919876543210": "123456"}
        
        with patch('app.routers.auth.otp_storage', mock_otp_storage):
            result = validate_otp("+919876543210", "123456")
            assert result is True
    
    def test_otp_validation_invalid(self):
        """Test OTP validation with incorrect OTP"""
        from app.routers.auth import validate_otp
        
        # Mock OTP storage
        mock_otp_storage = {"+919876543210": "123456"}
        
        with patch('app.routers.auth.otp_storage', mock_otp_storage):
            result = validate_otp("+919876543210", "654321")
            assert result is False
    
    def test_otp_validation_expired(self):
        """Test OTP validation with expired OTP"""
        from app.routers.auth import validate_otp
        from datetime import datetime, timedelta
        
        # Mock expired OTP storage
        expired_time = datetime.utcnow() - timedelta(minutes=10)
        mock_otp_storage = {
            "+919876543210": {
                "otp": "123456",
                "timestamp": expired_time.isoformat()
            }
        }
        
        with patch('app.routers.auth.otp_storage', mock_otp_storage):
            result = validate_otp("+919876543210", "123456")
            assert result is False


class TestPasswordHashing:
    """Test password hashing and verification"""
    
    def test_password_hashing(self):
        """Test password hashing creates different hashes"""
        from app.core.security import get_password_hash, verify_password
        
        password = "test_password_123"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        
        assert hash1 != hash2  # Should be different due to salt
        assert verify_password(password, hash1)
        assert verify_password(password, hash2)
    
    def test_password_verification_invalid(self):
        """Test password verification with wrong password"""
        from app.core.security import get_password_hash, verify_password
        
        password = "test_password_123"
        wrong_password = "wrong_password"
        hashed = get_password_hash(password)
        
        assert not verify_password(wrong_password, hashed)
    
    def test_password_hashing_strength(self):
        """Test password hashing uses bcrypt"""
        from app.core.security import get_password_hash
        
        password = "test_password_123"
        hashed = get_password_hash(password)
        
        # Bcrypt hashes start with $2b$
        assert hashed.startswith("$2b$")
        assert len(hashed) == 60  # Standard bcrypt hash length
