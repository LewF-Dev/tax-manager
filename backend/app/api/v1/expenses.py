"""Expense tracking endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.database import get_db
from app.models.user import User
from app.models.expense import Expense
from app.schemas.expense import ExpenseCreate, ExpenseUpdate, ExpenseResponse, EXPENSE_CATEGORIES
from app.core.security import get_current_active_subscriber
from app.core.dates import get_tax_year

router = APIRouter(prefix="/expenses", tags=["expenses"])


@router.get("/categories", response_model=List[str])
async def get_expense_categories():
    """Get list of available expense categories."""
    return EXPENSE_CATEGORIES


@router.post("/", response_model=ExpenseResponse, status_code=status.HTTP_201_CREATED)
async def create_expense(
    expense_data: ExpenseCreate,
    current_user: User = Depends(get_current_active_subscriber),
    db: Session = Depends(get_db),
):
    """Create a new expense transaction."""
    tax_year = get_tax_year(expense_data.date_paid)
    
    expense = Expense(
        user_id=current_user.id,
        date_paid=expense_data.date_paid,
        amount=expense_data.amount,
        category=expense_data.category,
        description=expense_data.description,
        tax_year=tax_year,
    )
    
    db.add(expense)
    db.commit()
    db.refresh(expense)
    
    return expense


@router.get("/", response_model=List[ExpenseResponse])
async def list_expenses(
    current_user: User = Depends(get_current_active_subscriber),
    db: Session = Depends(get_db),
    tax_year: str = None,
):
    """List all expense transactions for current user."""
    query = db.query(Expense).filter(Expense.user_id == current_user.id)
    
    if tax_year:
        query = query.filter(Expense.tax_year == tax_year)
    
    expenses = query.order_by(Expense.date_paid.desc()).all()
    return expenses


@router.get("/{expense_id}", response_model=ExpenseResponse)
async def get_expense(
    expense_id: UUID,
    current_user: User = Depends(get_current_active_subscriber),
    db: Session = Depends(get_db),
):
    """Get a specific expense transaction."""
    expense = db.query(Expense).filter(
        Expense.id == expense_id,
        Expense.user_id == current_user.id,
    ).first()
    
    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense transaction not found",
        )
    
    return expense


@router.patch("/{expense_id}", response_model=ExpenseResponse)
async def update_expense(
    expense_id: UUID,
    expense_update: ExpenseUpdate,
    current_user: User = Depends(get_current_active_subscriber),
    db: Session = Depends(get_db),
):
    """Update an expense transaction."""
    expense = db.query(Expense).filter(
        Expense.id == expense_id,
        Expense.user_id == current_user.id,
    ).first()
    
    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense transaction not found",
        )
    
    update_data = expense_update.model_dump(exclude_unset=True)
    
    # If date changed, recalculate tax year
    if "date_paid" in update_data:
        update_data["tax_year"] = get_tax_year(update_data["date_paid"])
    
    for field, value in update_data.items():
        setattr(expense, field, value)
    
    db.commit()
    db.refresh(expense)
    
    return expense


@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_expense(
    expense_id: UUID,
    current_user: User = Depends(get_current_active_subscriber),
    db: Session = Depends(get_db),
):
    """Delete an expense transaction."""
    expense = db.query(Expense).filter(
        Expense.id == expense_id,
        Expense.user_id == current_user.id,
    ).first()
    
    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense transaction not found",
        )
    
    db.delete(expense)
    db.commit()
    
    return None
