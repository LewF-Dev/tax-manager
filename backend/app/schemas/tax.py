"""Tax calculation schemas."""
from pydantic import BaseModel
from datetime import date
from decimal import Decimal
from typing import Dict, Any
from uuid import UUID


class TaxSummary(BaseModel):
    """Tax summary for current tax year."""
    tax_year: str
    tax_year_start: date
    tax_year_end: date
    total_income: Decimal
    total_expenses: Decimal
    net_profit: Decimal
    income_tax: Decimal
    ni_class2: Decimal
    ni_class4: Decimal
    total_tax: Decimal
    tax_to_set_aside: Decimal  # Recommended amount based on percentage
    actual_tax_saved: Decimal  # Actual amount user has saved
    hmrc_registration_deadline: date
    vat_threshold_proximity: Decimal  # Percentage towards VAT threshold


class TaxSnapshotResponse(BaseModel):
    """Tax snapshot response."""
    id: UUID
    user_id: UUID
    tax_year: str
    tax_year_start: date
    tax_year_end: date
    total_income: Decimal
    total_expenses: Decimal
    net_profit: Decimal
    income_tax: Decimal
    ni_class2: Decimal
    ni_class4: Decimal
    total_tax: Decimal
    tax_ruleset_version: str
    ruleset_data: Dict[str, Any]
    created_at: date
    
    class Config:
        from_attributes = True
