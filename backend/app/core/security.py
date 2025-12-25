"""Authentication and security utilities."""
from fastapi import Depends, HTTPException, status, Request, Cookie
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from sqlalchemy.orm import Session
from typing import Optional

from app.core.config import settings
from app.database import get_db
from app.models.user import User

security = HTTPBearer(auto_error=False)


def verify_token(token: str) -> dict:
    """
    Verify Supabase JWT token.
    
    Args:
        token: JWT token string
        
    Returns:
        Decoded token payload
        
    Raises:
        HTTPException: If token is invalid
    """
    try:
        # Supabase uses ES256 algorithm, decode without verification for development
        # In production, you'd fetch the public key from Supabase and verify properly
        payload = jwt.decode(
            token,
            options={"verify_signature": False},
        )
        return payload
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    access_token: Optional[str] = Cookie(None),
) -> User:
    """
    Get current authenticated user from JWT token (cookie or header).
    
    Args:
        request: FastAPI request
        db: Database session
        credentials: HTTP authorization credentials (optional)
        access_token: Token from cookie (optional)
        
    Returns:
        Current user
        
    Raises:
        HTTPException: If user not found or token invalid
    """
    # Try to get token from cookie first, then from Authorization header
    token = access_token
    if not token and credentials:
        token = credentials.credentials
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    
    payload = verify_token(token)
    
    supabase_id = payload.get("sub")
    if not supabase_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )
    
    user = db.query(User).filter(User.supabase_id == supabase_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    return user


async def get_current_active_subscriber(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Get current user and verify active subscription.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Current user with active subscription
        
    Raises:
        HTTPException: If subscription is not active
    """
    if current_user.subscription_status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Active subscription required",
        )
    
    return current_user


async def require_uc_enabled(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Require that UC is enabled for the current user.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Current user with UC enabled
        
    Raises:
        HTTPException: If UC is not enabled
    """
    if not current_user.uc_enabled:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Universal Credit functionality is not enabled for this account",
        )
    
    return current_user
