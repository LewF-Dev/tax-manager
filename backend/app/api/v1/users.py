"""User management endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserResponse, UserProfile
from app.core.security import get_current_user, get_current_active_subscriber

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
):
    """
    Create a new user account.
    
    Called after Supabase authentication.
    """
    # Check if user already exists
    existing = db.query(User).filter(User.supabase_id == user_data.supabase_id).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists",
        )
    
    # Create user
    user = User(
        supabase_id=user_data.supabase_id,
        email=user_data.email,
        full_name=user_data.full_name,
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user


@router.get("/me", response_model=UserProfile)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user),
):
    """Get current user profile."""
    return current_user


@router.patch("/me", response_model=UserProfile)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update current user profile."""
    update_data = user_update.model_dump(exclude_unset=True)
    
    # Validate UC configuration
    if "uc_enabled" in update_data:
        if update_data["uc_enabled"] and not current_user.uc_assessment_day:
            if "uc_assessment_day" not in update_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="uc_assessment_day required when enabling UC",
                )
    
    # Apply updates
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    db.commit()
    db.refresh(current_user)
    
    return current_user


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_current_user(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Delete current user account and all associated data.
    
    GDPR compliance: complete data deletion.
    """
    db.delete(current_user)
    db.commit()
    
    return None
