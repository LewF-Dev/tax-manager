"""Expense schemas for validation."""
from pydantic import BaseModel, Field
from datetime import date
from decimal import Decimal
from typing import Optional
from uuid import UUID


# Common expense categories
EXPENSE_CATEGORIES = [
    "Equipment",
    "Software",
    "Travel",
    "Office Supplies",
    "Professional Fees",
    "Marketing",
    "Training",
    "Insurance",
    "Other",
]


class ExpenseCreate(BaseModel):
    """Schema for creating expense transaction."""
    date_paid: date
    amount: Decimal = Field(gt=0)
    category: str = Field(min_length=1, max_length=100)
    description: str = Field(min_length=1, max_length=500)


class ExpenseUpdate(BaseModel):
    """Schema for updating expense transaction."""
    date_paid: Optional[date] = None
    amount: Optional[Decimal] = Field(None, gt=0)
    category: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, min_length=1, max_length=500)


class ExpenseResponse(BaseModel):
    """Expense transaction response."""
    id: UUID
    user_id: UUID
    date_paid: date
    amount: Decimal
    category: str
    description: str
    tax_year: str
    created_at: date
    
    class Config:
        from_attributes = True
