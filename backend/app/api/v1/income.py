"""Income tracking endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.database import get_db
from app.models.user import User
from app.models.income import Income
from app.schemas.income import IncomeCreate, IncomeUpdate, IncomeResponse
from app.core.security import get_current_active_subscriber
from app.core.dates import get_tax_year
from app.core.tax_rulesets import get_ruleset_for_date

router = APIRouter(prefix="/income", tags=["income"])


@router.post("/", response_model=IncomeResponse, status_code=status.HTTP_201_CREATED)
async def create_income(
    income_data: IncomeCreate,
    current_user: User = Depends(get_current_active_subscriber),
    db: Session = Depends(get_db),
):
    """Create a new income transaction."""
    # Determine tax year and ruleset
    tax_year = get_tax_year(income_data.date_received)
    ruleset = get_ruleset_for_date(income_data.date_received)
    
    income = Income(
        user_id=current_user.id,
        date_received=income_data.date_received,
        amount=income_data.amount,
        description=income_data.description,
        tax_year=tax_year,
        tax_ruleset_version=ruleset["version"],
    )
    
    db.add(income)
    db.commit()
    db.refresh(income)
    
    return income


@router.get("/", response_model=List[IncomeResponse])
async def list_income(
    current_user: User = Depends(get_current_active_subscriber),
    db: Session = Depends(get_db),
    tax_year: str = None,
):
    """List all income transactions for current user."""
    query = db.query(Income).filter(Income.user_id == current_user.id)
    
    if tax_year:
        query = query.filter(Income.tax_year == tax_year)
    
    incomes = query.order_by(Income.date_received.desc()).all()
    return incomes


@router.get("/{income_id}", response_model=IncomeResponse)
async def get_income(
    income_id: UUID,
    current_user: User = Depends(get_current_active_subscriber),
    db: Session = Depends(get_db),
):
    """Get a specific income transaction."""
    income = db.query(Income).filter(
        Income.id == income_id,
        Income.user_id == current_user.id,
    ).first()
    
    if not income:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Income transaction not found",
        )
    
    return income


@router.patch("/{income_id}", response_model=IncomeResponse)
async def update_income(
    income_id: UUID,
    income_update: IncomeUpdate,
    current_user: User = Depends(get_current_active_subscriber),
    db: Session = Depends(get_db),
):
    """Update an income transaction."""
    income = db.query(Income).filter(
        Income.id == income_id,
        Income.user_id == current_user.id,
    ).first()
    
    if not income:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Income transaction not found",
        )
    
    update_data = income_update.model_dump(exclude_unset=True)
    
    # If date changed, recalculate tax year and ruleset
    if "date_received" in update_data:
        new_date = update_data["date_received"]
        update_data["tax_year"] = get_tax_year(new_date)
        ruleset = get_ruleset_for_date(new_date)
        update_data["tax_ruleset_version"] = ruleset["version"]
    
    for field, value in update_data.items():
        setattr(income, field, value)
    
    db.commit()
    db.refresh(income)
    
    return income


@router.delete("/{income_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_income(
    income_id: UUID,
    current_user: User = Depends(get_current_active_subscriber),
    db: Session = Depends(get_db),
):
    """Delete an income transaction."""
    income = db.query(Income).filter(
        Income.id == income_id,
        Income.user_id == current_user.id,
    ).first()
    
    if not income:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Income transaction not found",
        )
    
    db.delete(income)
    db.commit()
    
    return None
