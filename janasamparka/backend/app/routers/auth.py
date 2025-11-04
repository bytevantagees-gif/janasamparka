"""
Authentication router - OTP and JWT based authentication
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional
import os
import shutil
from pathlib import Path
from uuid import uuid4
from app.core.database import get_db
from app.core.auth import require_auth
from app.core.security import create_access_token, create_refresh_token, generate_otp, verify_token  # type: ignore
from app.core.config import settings
from app.models.user import User, UserRole
from app.schemas.user import OTPRequest, OTPVerify, TokenResponse, UserResponse, UserUpdate

router = APIRouter()

# In-memory OTP storage for development (use Redis in production)
otp_storage: Dict[str, Dict[str, Any]] = {}


@router.post("/request-otp", summary="Request OTP for phone number")
async def request_otp(request: OTPRequest, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Request OTP for phone number
    In development: Returns OTP in response
    In production: Send OTP via SMS gateway
    """
    phone = request.phone
    
    # Generate OTP
    otp = generate_otp(settings.OTP_LENGTH)
    
    # Store OTP with expiry
    otp_storage[phone] = {
        "otp": otp,
        "expires_at": datetime.now(timezone.utc) + timedelta(minutes=settings.OTP_EXPIRY_MINUTES),
        "attempts": 0
    }
    
    # In development, return OTP in response
    # In production, send via SMS and return success message only
    if settings.DEBUG:
        return {
            "message": "OTP sent successfully",
            "phone": phone,
            "otp": otp,  # Only in development!
            "expires_in_minutes": settings.OTP_EXPIRY_MINUTES
        }
    else:
        # TODO: Integrate SMS gateway here
        return {
            "message": "OTP sent successfully",
            "phone": phone,
            "expires_in_minutes": settings.OTP_EXPIRY_MINUTES
        }


@router.post("/verify-otp", response_model=TokenResponse, summary="Verify OTP and get access token")
async def verify_otp(request: OTPVerify, db: Session = Depends(get_db)):
    """
    Verify OTP and return JWT tokens
    Creates new user if doesn't exist
    """
    phone = request.phone
    otp = request.otp
    
    # Check if OTP exists
    if phone not in otp_storage:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OTP not found. Please request a new OTP."
        )
    
    stored_otp_data: Dict[str, Any] = otp_storage[phone]
    
    # Check if OTP expired
    if datetime.now(timezone.utc) > stored_otp_data["expires_at"]:
        del otp_storage[phone]
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OTP has expired. Please request a new OTP."
        )
    
    # Check attempts
    if stored_otp_data["attempts"] >= 3:
        del otp_storage[phone]
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many failed attempts. Please request a new OTP."
        )
    
    # Verify OTP
    if stored_otp_data["otp"] != otp:
        stored_otp_data["attempts"] += 1
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid OTP. {3 - stored_otp_data['attempts']} attempts remaining."
        )
    
    # OTP verified - remove from storage
    del otp_storage[phone]
    
    # Get or create user
    user = db.query(User).filter(User.phone == phone).first()
    
    if not user:
        # Create new user
        user = User(
            name=f"User {phone[-4:]}",  # Default name, user can update later
            phone=phone,
            role=UserRole.CITIZEN,
            locale_pref="kn"
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    
    # Generate tokens
    access_token = create_access_token(data={"sub": str(user.id), "role": user.role.value})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserResponse.model_validate(user)
    )


@router.get("/me", response_model=UserResponse, summary="Get current user")
async def get_me(
    current_user: User = Depends(require_auth),
):
    """Get current authenticated user"""
    return UserResponse.model_validate(current_user)


@router.put("/me", response_model=UserResponse, summary="Update current user profile")
async def update_me(
    user_update: UserUpdate,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Update current user profile"""
    if user_update.name is not None:
        current_user.name = user_update.name
    if user_update.locale_pref is not None:
        current_user.locale_pref = user_update.locale_pref
    if user_update.profile_photo is not None:
        current_user.profile_photo = user_update.profile_photo
    
    current_user.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(current_user)
    
    return UserResponse.model_validate(current_user)


@router.post("/me/profile-photo", response_model=UserResponse, summary="Upload profile photo")
async def upload_profile_photo(
    file: UploadFile = File(...),
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Upload profile photo for current user"""
    # Validate file type
    allowed_types = ["image/jpeg", "image/jpg", "image/png", "image/gif", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed types: {', '.join(allowed_types)}"
        )
    
    # Validate file size (max 5MB)
    file_size = 0
    max_size = 5 * 1024 * 1024  # 5MB
    
    # Check file size
    if file.file:
        file.file.seek(0, 2)  # Seek to end
        file_size = file.file.tell()
        file.file.seek(0)  # Seek back to start
        
        if file_size > max_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File size too large. Maximum 5MB allowed."
            )
    
    # Create upload directory if it doesn't exist
    upload_dir = Path(settings.UPLOAD_DIR) / "profile_photos"
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate unique filename
    file_extension = Path(file.filename or "image.jpg").suffix
    unique_filename = f"{uuid4()}{file_extension}"
    file_path = upload_dir / unique_filename
    
    # Save file
    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload file: {str(e)}"
        )
    
    # Update user profile photo URL
    photo_url = f"/uploads/profile_photos/{unique_filename}"
    
    # Delete old profile photo if exists
    old_photo = current_user.profile_photo
    if old_photo and old_photo != photo_url:
        old_file_path = Path(settings.UPLOAD_DIR) / old_photo.lstrip("/uploads/")
        if old_file_path.exists():
            try:
                os.remove(old_file_path)
            except Exception:
                pass  # Ignore if file doesn't exist
    
    current_user.profile_photo = photo_url
    current_user.updated_at = datetime.now(timezone.utc)
    
    db.commit()
    db.refresh(current_user)
    
    return UserResponse.model_validate(current_user)


@router.post("/refresh", response_model=TokenResponse, summary="Refresh access token")
async def refresh_access_token(
    refresh_token: str,
    db: Session = Depends(get_db)
):
    """
    Refresh access token using refresh token
    """
    # Verify refresh token
    payload: Optional[Dict[str, Any]] = verify_token(refresh_token)
    
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    user_id: Optional[str] = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    # Get user
    from uuid import UUID
    user = db.query(User).filter(User.id == UUID(str(user_id))).first()
    
    if not user or user.is_active != "true":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    # Generate new tokens
    new_access_token = create_access_token(data={"sub": str(user.id), "role": user.role.value})
    new_refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    return TokenResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        user=UserResponse.model_validate(user)
    )


@router.post("/admin/reset-user-access", summary="Generate temporary access code for user (Admin only)")
async def reset_user_access(
    user_id: str,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Admin endpoint to generate temporary access code for users who lost their phone.
    Code is valid for 24 hours and single-use.
    """
    # Only admins can generate codes
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can generate temporary access codes"
        )
    
    from uuid import UUID
    from app.models.temporary_access import TemporaryAccess
    
    # Get target user
    user_uuid = UUID(user_id)
    target_user = db.query(User).filter(User.id == user_uuid).first()
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Generate temporary access code
    access = TemporaryAccess.create_for_user(user_uuid, db)
    
    # TODO: If user has email, send code via email
    email_sent = False
    if target_user.email:
        # Email sending logic would go here
        # email_sent = send_temporary_code_email(target_user.email, access.access_code)
        pass
    
    return {
        "user_id": user_id,
        "user_name": target_user.name,
        "user_phone": target_user.phone,
        "user_email": target_user.email,
        "access_code": access.access_code,
        "expires_at": access.expires_at.isoformat(),
        "email_sent": email_sent,
        "message": "Temporary access code generated successfully. Code is valid for 24 hours."
    }


@router.post("/login-with-code", response_model=TokenResponse, summary="Login with temporary access code")
async def login_with_code(
    access_code: str,
    db: Session = Depends(get_db)
):
    """
    Login using temporary access code (for users who lost their phone).
    Code is single-use and expires after 24 hours.
    """
    from app.models.temporary_access import TemporaryAccess
    
    # Find access code
    access = db.query(TemporaryAccess).filter(
        TemporaryAccess.access_code == access_code
    ).first()
    
    if not access:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access code"
        )
    
    # Check if code is still valid
    if not access.is_valid():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access code has expired or already been used"
        )
    
    # Get user
    user = db.query(User).filter(User.id == access.user_id).first()
    if not user or user.is_active != "true":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    # Mark code as used
    access.mark_as_used(db)
    
    # Generate tokens
    access_token = create_access_token(data={"sub": str(user.id), "role": user.role.value})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserResponse.model_validate(user)
    )
