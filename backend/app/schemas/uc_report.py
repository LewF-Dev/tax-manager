"""Universal Credit report schemas."""
from pydantic import BaseModel
from datetime import date
from decimal import Decimal
from typing import Optional
from uuid import UUID


class UCPeriodSummary(BaseModel):
    """Summary for a UC assessment period."""
    period_start: date
    period_end: date
    total_income: Decimal
    total_expenses: Decimal
    net_profit: Decimal
    reported_at: Optional[date] = None
    notes: Optional[str] = None


class UCReportResponse(BaseModel):
    """UC report response."""
    id: UUID
    user_id: UUID
    period_start: date
    period_end: date
    total_income: Decimal
    total_expenses: Decimal
    net_profit: Decimal
    reported_at: Optional[date]
    notes: Optional[str]
    created_at: date
    
    class Config:
        from_attributes = True


class UCReportMarkReported(BaseModel):
    """Schema for marking a UC report as reported."""
    reported_at: date
    notes: Optional[str] = None
