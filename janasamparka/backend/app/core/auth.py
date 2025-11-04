"""
Authentication and authorization utilities
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID

from app.core.config import settings
from app.core.database import get_db
from app.models.user import User, UserRole

security = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Get current user from JWT token.
    Returns None if no token or invalid token (for optional authentication).
    """
    if not credentials:
        return None
    
    try:
        token = credentials.credentials
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
    except JWTError:
        return None
    
    user = db.query(User).filter(User.id == UUID(user_id)).first()
    return user


def require_auth(
    current_user: Optional[User] = Depends(get_current_user)
) -> User:
    """
    Require authentication. Raises 401 if not authenticated.
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return current_user


def require_role(*allowed_roles: UserRole):
    """
    Require specific role(s). Returns a dependency function.
    """
    def role_checker(current_user: User = Depends(require_auth)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {', '.join([r.value for r in allowed_roles])}"
            )
        return current_user
    return role_checker


def get_user_constituency_id(
    current_user: Optional[User] = Depends(get_current_user)
) -> Optional[UUID]:
    """
    Get the constituency_id for filtering based on user role.
    - Admin: Returns None (can see all constituencies)
    - Other roles: Returns user's constituency_id
    - No auth: Returns None (for development/testing)
    """
    if not current_user:
        # No authentication - return None (allow all for development)
        return None
    
    # Admin can see all constituencies
    if current_user.role == UserRole.ADMIN:
        return None
    
    # All other roles are scoped to their constituency
    return current_user.constituency_id
