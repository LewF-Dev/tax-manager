"""Data export endpoints."""
from fastapi import APIRouter, Depends, Response
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import json

from app.database import get_db
from app.models.user import User
from app.models.income import Income
from app.models.expense import Expense
from app.models.uc_report import UCReport
from app.models.tax_snapshot import TaxSnapshot
from app.core.security import get_current_active_subscriber
from app.services.export import generate_transactions_csv, generate_full_export

router = APIRouter(prefix="/export", tags=["export"])


@router.get("/csv")
async def export_transactions_csv(
    current_user: User = Depends(get_current_active_subscriber),
    db: Session = Depends(get_db),
):
    """Export all transactions as CSV."""
    incomes = db.query(Income).filter(
        Income.user_id == current_user.id
    ).order_by(Income.date_received).all()
    
    expenses = db.query(Expense).filter(
        Expense.user_id == current_user.id
    ).order_by(Expense.date_paid).all()
    
    csv_content = generate_transactions_csv(incomes, expenses)
    
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=transactions.csv"
        },
    )


@router.get("/full")
async def export_full_data(
    current_user: User = Depends(get_current_active_subscriber),
    db: Session = Depends(get_db),
):
    """
    Export complete user data (GDPR compliance).
    
    Returns all user data in JSON format.
    """
    incomes = db.query(Income).filter(
        Income.user_id == current_user.id
    ).all()
    
    expenses = db.query(Expense).filter(
        Expense.user_id == current_user.id
    ).all()
    
    uc_reports = db.query(UCReport).filter(
        UCReport.user_id == current_user.id
    ).all()
    
    tax_snapshots = db.query(TaxSnapshot).filter(
        TaxSnapshot.user_id == current_user.id
    ).all()
    
    export_data = generate_full_export(
        current_user,
        incomes,
        expenses,
        uc_reports,
        tax_snapshots,
    )
    
    return JSONResponse(
        content=export_data,
        headers={
            "Content-Disposition": "attachment; filename=full_export.json"
        },
    )
