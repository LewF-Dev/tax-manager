"""Data export service for CSV and GDPR compliance."""
import csv
import io
import json
from typing import List
from datetime import datetime

from app.models.user import User
from app.models.income import Income
from app.models.expense import Expense
from app.models.uc_report import UCReport
from app.models.tax_snapshot import TaxSnapshot


def generate_transactions_csv(incomes: List[Income], expenses: List[Expense]) -> str:
    """
    Generate CSV export of all transactions.
    
    Args:
        incomes: List of income transactions
        expenses: List of expense transactions
        
    Returns:
        CSV string
    """
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow([
        "Type",
        "Date",
        "Amount",
        "Description",
        "Category",
        "Tax Year",
        "Created At",
    ])
    
    # Income rows
    for income in incomes:
        writer.writerow([
            "Income",
            income.date_received.isoformat(),
            f"{income.amount:.2f}",
            income.description,
            "",
            income.tax_year,
            income.created_at.isoformat(),
        ])
    
    # Expense rows
    for expense in expenses:
        writer.writerow([
            "Expense",
            expense.date_paid.isoformat(),
            f"{expense.amount:.2f}",
            expense.description,
            expense.category,
            expense.tax_year,
            expense.created_at.isoformat(),
        ])
    
    return output.getvalue()


def generate_full_export(
    user: User,
    incomes: List[Income],
    expenses: List[Expense],
    uc_reports: List[UCReport],
    tax_snapshots: List[TaxSnapshot],
) -> dict:
    """
    Generate complete data export for GDPR compliance.
    
    Args:
        user: User account
        incomes: All income transactions
        expenses: All expense transactions
        uc_reports: All UC reports
        tax_snapshots: All tax snapshots
        
    Returns:
        Dictionary with all user data
    """
    return {
        "export_date": datetime.utcnow().isoformat(),
        "user": {
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "trading_start_date": user.trading_start_date.isoformat() if user.trading_start_date else None,
            "uc_enabled": user.uc_enabled,
            "uc_assessment_day": user.uc_assessment_day,
            "tax_set_aside_percentage": float(user.tax_set_aside_percentage),
            "subscription_status": user.subscription_status,
            "created_at": user.created_at.isoformat(),
        },
        "incomes": [
            {
                "id": str(i.id),
                "date_received": i.date_received.isoformat(),
                "amount": float(i.amount),
                "description": i.description,
                "tax_year": i.tax_year,
                "tax_ruleset_version": i.tax_ruleset_version,
                "created_at": i.created_at.isoformat(),
            }
            for i in incomes
        ],
        "expenses": [
            {
                "id": str(e.id),
                "date_paid": e.date_paid.isoformat(),
                "amount": float(e.amount),
                "category": e.category,
                "description": e.description,
                "tax_year": e.tax_year,
                "created_at": e.created_at.isoformat(),
            }
            for e in expenses
        ],
        "uc_reports": [
            {
                "id": str(r.id),
                "period_start": r.period_start.isoformat(),
                "period_end": r.period_end.isoformat(),
                "total_income": float(r.total_income),
                "total_expenses": float(r.total_expenses),
                "net_profit": float(r.net_profit),
                "reported_at": r.reported_at.isoformat() if r.reported_at else None,
                "notes": r.notes,
                "created_at": r.created_at.isoformat(),
            }
            for r in uc_reports
        ],
        "tax_snapshots": [
            {
                "id": str(s.id),
                "tax_year": s.tax_year,
                "tax_year_start": s.tax_year_start.isoformat(),
                "tax_year_end": s.tax_year_end.isoformat(),
                "total_income": float(s.total_income),
                "total_expenses": float(s.total_expenses),
                "net_profit": float(s.net_profit),
                "income_tax": float(s.income_tax),
                "ni_class2": float(s.ni_class2),
                "ni_class4": float(s.ni_class4),
                "total_tax": float(s.total_tax),
                "tax_ruleset_version": s.tax_ruleset_version,
                "created_at": s.created_at.isoformat(),
            }
            for s in tax_snapshots
        ],
    }
