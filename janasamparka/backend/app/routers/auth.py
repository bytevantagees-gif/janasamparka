"""
Authentication router - OTP and JWT based authentication
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.core.database import get_db
from app.core.security import create_access_token, create_refresh_token, generate_otp, verify_token
from app.core.config import settings
from app.models.user import User, UserRole
from app.schemas.user import OTPRequest, OTPVerify, TokenResponse, UserResponse
from typing import Dict

router = APIRouter()

# In-memory OTP storage for development (use Redis in production)
otp_storage: Dict[str, Dict] = {}


@router.post("/request-otp", summary="Request OTP for phone number")
async def request_otp(request: OTPRequest, db: Session = Depends(get_db)):
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
        "expires_at": datetime.utcnow() + timedelta(minutes=settings.OTP_EXPIRY_MINUTES),
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
    
    stored_otp_data = otp_storage[phone]
    
    # Check if OTP expired
    if datetime.utcnow() > stored_otp_data["expires_at"]:
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
    access_token = create_access_token(data={"sub": str(user.id), "role": user.role})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserResponse.from_orm(user)
    )


@router.get("/me", response_model=UserResponse, summary="Get current user")
async def get_current_user(
    db: Session = Depends(get_db),
    # TODO: Add authentication dependency
):
    """Get current authenticated user"""
    # Placeholder - will add auth dependency
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Authentication dependency not yet implemented"
    )
