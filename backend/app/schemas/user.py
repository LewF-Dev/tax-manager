"""User schemas for validation."""
from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import date
from decimal import Decimal
from typing import Optional
from uuid import UUID


class UserCreate(BaseModel):
    """Schema for creating a new user."""
    email: EmailStr
    full_name: Optional[str] = None
    supabase_id: str


class UserUpdate(BaseModel):
    """Schema for updating user profile."""
    full_name: Optional[str] = None
    trading_start_date: Optional[date] = None
    uc_enabled: Optional[bool] = None
    uc_assessment_day: Optional[int] = Field(None, ge=1, le=28)
    tax_set_aside_percentage: Optional[Decimal] = Field(None, ge=0, le=100)
    
    @field_validator("uc_assessment_day")
    @classmethod
    def validate_uc_assessment_day(cls, v: Optional[int], info) -> Optional[int]:
        """Validate UC assessment day is only set when UC is enabled."""
        if v is not None and not (1 <= v <= 28):
            raise ValueError("UC assessment day must be between 1 and 28")
        return v


class UserProfile(BaseModel):
    """User profile for settings page."""
    id: UUID
    email: str
    full_name: Optional[str]
    trading_start_date: Optional[date]
    uc_enabled: bool
    uc_assessment_day: Optional[int]
    tax_set_aside_percentage: Decimal
    subscription_status: str
    
    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    """Full user response with subscription info."""
    id: UUID
    email: str
    full_name: Optional[str]
    trading_start_date: Optional[date]
    uc_enabled: bool
    uc_assessment_day: Optional[int]
    tax_set_aside_percentage: Decimal
    subscription_status: str
    stripe_customer_id: Optional[str]
    
    class Config:
        from_attributes = True
