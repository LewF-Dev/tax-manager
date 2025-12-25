"""Universal Credit reporting endpoints."""
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
from app.models.uc_report import UCReport
from app.schemas.uc_report import UCPeriodSummary, UCReportResponse, UCReportMarkReported
from app.core.security import get_current_active_subscriber, require_uc_enabled
from app.core.dates import get_uc_assessment_period, get_next_uc_assessment_period

router = APIRouter(prefix="/uc", tags=["universal-credit"])


@router.get("/current-period", response_model=UCPeriodSummary)
async def get_current_uc_period(
    current_user: User = Depends(require_uc_enabled),
    db: Session = Depends(get_db),
):
    """Get current UC assessment period summary."""
    if not current_user.uc_assessment_day:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="UC assessment day not configured",
        )
    
    # Get current period dates
    period_start, period_end = get_uc_assessment_period(
        date.today(),
        current_user.uc_assessment_day,
    )
    
    # Calculate totals for this period
    total_income = db.query(Income).filter(
        and_(
            Income.user_id == current_user.id,
            Income.date_received >= period_start,
            Income.date_received <= period_end,
        )
    ).with_entities(Income.amount).all()
    
    total_expenses = db.query(Expense).filter(
        and_(
            Expense.user_id == current_user.id,
            Expense.date_paid >= period_start,
            Expense.date_paid <= period_end,
        )
    ).with_entities(Expense.amount).all()
    
    income_sum = sum((i[0] for i in total_income), Decimal("0.00"))
    expense_sum = sum((e[0] for e in total_expenses), Decimal("0.00"))
    net_profit = income_sum - expense_sum
    
    # Check if already reported
    existing_report = db.query(UCReport).filter(
        and_(
            UCReport.user_id == current_user.id,
            UCReport.period_start == period_start,
            UCReport.period_end == period_end,
        )
    ).first()
    
    return UCPeriodSummary(
        period_start=period_start,
        period_end=period_end,
        total_income=income_sum,
        total_expenses=expense_sum,
        net_profit=net_profit,
        reported_at=existing_report.reported_at if existing_report else None,
        notes=existing_report.notes if existing_report else None,
    )


@router.get("/periods", response_model=List[UCReportResponse])
async def list_uc_periods(
    current_user: User = Depends(require_uc_enabled),
    db: Session = Depends(get_db),
    limit: int = 12,
):
    """List recent UC assessment periods."""
    reports = db.query(UCReport).filter(
        UCReport.user_id == current_user.id
    ).order_by(UCReport.period_start.desc()).limit(limit).all()
    
    return reports


@router.post("/periods/generate", response_model=UCReportResponse, status_code=status.HTTP_201_CREATED)
async def generate_uc_report(
    period_start_date: date,
    current_user: User = Depends(require_uc_enabled),
    db: Session = Depends(get_db),
):
    """
    Generate a UC report for a specific period.
    
    Creates a snapshot of income/expenses for the assessment period.
    """
    if not current_user.uc_assessment_day:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="UC assessment day not configured",
        )
    
    # Get period dates
    period_start, period_end = get_uc_assessment_period(
        period_start_date,
        current_user.uc_assessment_day,
    )
    
    # Check if report already exists
    existing = db.query(UCReport).filter(
        and_(
            UCReport.user_id == current_user.id,
            UCReport.period_start == period_start,
        )
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Report already exists for this period",
        )
    
    # Calculate totals
    total_income = db.query(Income).filter(
        and_(
            Income.user_id == current_user.id,
            Income.date_received >= period_start,
            Income.date_received <= period_end,
        )
    ).with_entities(Income.amount).all()
    
    total_expenses = db.query(Expense).filter(
        and_(
            Expense.user_id == current_user.id,
            Expense.date_paid >= period_start,
            Expense.date_paid <= period_end,
        )
    ).with_entities(Expense.amount).all()
    
    income_sum = sum((i[0] for i in total_income), Decimal("0.00"))
    expense_sum = sum((e[0] for e in total_expenses), Decimal("0.00"))
    net_profit = income_sum - expense_sum
    
    # Create report
    report = UCReport(
        user_id=current_user.id,
        period_start=period_start,
        period_end=period_end,
        total_income=income_sum,
        total_expenses=expense_sum,
        net_profit=net_profit,
    )
    
    db.add(report)
    db.commit()
    db.refresh(report)
    
    return report


@router.patch("/periods/{period_start}/mark-reported", response_model=UCReportResponse)
async def mark_uc_period_reported(
    period_start: date,
    mark_data: UCReportMarkReported,
    current_user: User = Depends(require_uc_enabled),
    db: Session = Depends(get_db),
):
    """Mark a UC period as reported to Universal Credit."""
    report = db.query(UCReport).filter(
        and_(
            UCReport.user_id == current_user.id,
            UCReport.period_start == period_start,
        )
    ).first()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="UC report not found for this period",
        )
    
    report.reported_at = mark_data.reported_at
    report.notes = mark_data.notes
    
    db.commit()
    db.refresh(report)
    
    return report
