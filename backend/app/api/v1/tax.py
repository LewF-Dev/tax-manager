"""Tax calculation and summary endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List
from datetime import date
from decimal import Decimal

from app.database import get_db
from app.models.user import User
from app.models.income import Income
from app.models.expense import Expense
from app.models.tax_snapshot import TaxSnapshot
from app.schemas.tax import TaxSummary, TaxSnapshotResponse
from app.core.security import get_current_active_subscriber
from app.core.dates import get_current_tax_year, get_tax_year_dates, get_hmrc_registration_deadline
from app.core.tax_calc import calculate_total_tax, calculate_tax_to_set_aside
from app.core.tax_rulesets import get_ruleset_by_tax_year

router = APIRouter(prefix="/tax", tags=["tax"])


@router.get("/summary", response_model=TaxSummary)
async def get_tax_summary(
    current_user: User = Depends(get_current_active_subscriber),
    db: Session = Depends(get_db),
    tax_year: str = None,
):
    """
    Get tax summary for current or specified tax year.
    
    Calculates in real-time based on transactions.
    """
    if not tax_year:
        tax_year = get_current_tax_year()
    
    tax_year_start, tax_year_end = get_tax_year_dates(tax_year)
    
    # Get all income for this tax year
    incomes = db.query(Income).filter(
        and_(
            Income.user_id == current_user.id,
            Income.tax_year == tax_year,
        )
    ).all()
    
    # Get all expenses for this tax year
    expenses = db.query(Expense).filter(
        and_(
            Expense.user_id == current_user.id,
            Expense.tax_year == tax_year,
        )
    ).all()
    
    total_income = sum((i.amount for i in incomes), Decimal("0.00"))
    total_expenses = sum((e.amount for e in expenses), Decimal("0.00"))
    net_profit = total_income - total_expenses
    
    # Calculate actual tax saved
    actual_tax_saved = sum((i.tax_saved for i in incomes if i.tax_saved), Decimal("0.00"))
    
    # Calculate tax using first transaction date or tax year start
    calc_date = incomes[0].date_received if incomes else tax_year_start
    tax_breakdown = calculate_total_tax(net_profit, calc_date)
    
    # Calculate tax to set aside based on user's percentage (recommended)
    tax_to_set_aside = calculate_tax_to_set_aside(
        total_income,
        current_user.tax_set_aside_percentage,
    )
    
    # Calculate HMRC registration deadline
    hmrc_deadline = date(2099, 12, 31)  # Default far future
    if current_user.trading_start_date:
        hmrc_deadline = get_hmrc_registration_deadline(current_user.trading_start_date)
    
    # Calculate VAT threshold proximity
    ruleset = get_ruleset_by_tax_year(tax_year)
    vat_threshold = Decimal(str(ruleset["vat_threshold"]))
    vat_proximity = (total_income / vat_threshold * 100) if vat_threshold > 0 else Decimal("0.00")
    
    return TaxSummary(
        tax_year=tax_year,
        tax_year_start=tax_year_start,
        tax_year_end=tax_year_end,
        total_income=total_income,
        total_expenses=total_expenses,
        net_profit=net_profit,
        income_tax=Decimal(str(tax_breakdown["income_tax"])),
        ni_class2=Decimal(str(tax_breakdown["ni_class2"])),
        ni_class4=Decimal(str(tax_breakdown["ni_class4"])),
        total_tax=Decimal(str(tax_breakdown["total_tax"])),
        tax_to_set_aside=tax_to_set_aside,
        actual_tax_saved=actual_tax_saved,
        hmrc_registration_deadline=hmrc_deadline,
        vat_threshold_proximity=vat_proximity,
    )


@router.post("/snapshots", response_model=TaxSnapshotResponse, status_code=status.HTTP_201_CREATED)
async def create_tax_snapshot(
    tax_year: str,
    current_user: User = Depends(get_current_active_subscriber),
    db: Session = Depends(get_db),
):
    """
    Create a tax snapshot for a specific tax year.
    
    Stores a point-in-time calculation for audit trail.
    """
    tax_year_start, tax_year_end = get_tax_year_dates(tax_year)
    
    # Check if snapshot already exists
    existing = db.query(TaxSnapshot).filter(
        and_(
            TaxSnapshot.user_id == current_user.id,
            TaxSnapshot.tax_year == tax_year,
        )
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Snapshot already exists for this tax year",
        )
    
    # Get transactions
    incomes = db.query(Income).filter(
        and_(
            Income.user_id == current_user.id,
            Income.tax_year == tax_year,
        )
    ).all()
    
    expenses = db.query(Expense).filter(
        and_(
            Expense.user_id == current_user.id,
            Expense.tax_year == tax_year,
        )
    ).all()
    
    total_income = sum((i.amount for i in incomes), Decimal("0.00"))
    total_expenses = sum((e.amount for e in expenses), Decimal("0.00"))
    net_profit = total_income - total_expenses
    
    # Calculate tax
    calc_date = incomes[0].date_received if incomes else tax_year_start
    tax_breakdown = calculate_total_tax(net_profit, calc_date)
    
    # Get ruleset
    ruleset = get_ruleset_by_tax_year(tax_year)
    
    # Create snapshot
    snapshot = TaxSnapshot(
        user_id=current_user.id,
        tax_year=tax_year,
        tax_year_start=tax_year_start,
        tax_year_end=tax_year_end,
        total_income=total_income,
        total_expenses=total_expenses,
        net_profit=net_profit,
        income_tax=Decimal(str(tax_breakdown["income_tax"])),
        ni_class2=Decimal(str(tax_breakdown["ni_class2"])),
        ni_class4=Decimal(str(tax_breakdown["ni_class4"])),
        total_tax=Decimal(str(tax_breakdown["total_tax"])),
        tax_ruleset_version=ruleset["version"],
        ruleset_data=ruleset,
    )
    
    db.add(snapshot)
    db.commit()
    db.refresh(snapshot)
    
    return snapshot


@router.get("/snapshots", response_model=List[TaxSnapshotResponse])
async def list_tax_snapshots(
    current_user: User = Depends(get_current_active_subscriber),
    db: Session = Depends(get_db),
):
    """List all tax snapshots for current user."""
    snapshots = db.query(TaxSnapshot).filter(
        TaxSnapshot.user_id == current_user.id
    ).order_by(TaxSnapshot.tax_year.desc()).all()
    
    return snapshots
