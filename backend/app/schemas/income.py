"""Income schemas for validation."""
from pydantic import BaseModel, Field
from datetime import date
from decimal import Decimal
from typing import Optional
from uuid import UUID


class IncomeCreate(BaseModel):
    """Schema for creating income transaction."""
    date_received: date
    amount: Decimal = Field(gt=0)
    description: str = Field(min_length=1, max_length=500)


class IncomeUpdate(BaseModel):
    """Schema for updating income transaction."""
    date_received: Optional[date] = None
    amount: Optional[Decimal] = Field(None, gt=0)
    description: Optional[str] = Field(None, min_length=1, max_length=500)


class IncomeResponse(BaseModel):
    """Income transaction response."""
    id: UUID
    user_id: UUID
    date_received: date
    amount: Decimal
    description: str
    tax_year: str
    tax_ruleset_version: str
    created_at: date
    
    class Config:
        from_attributes = True
