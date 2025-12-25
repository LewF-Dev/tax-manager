"""Web UI routes."""
from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from datetime import date, timedelta
from decimal import Decimal

from app.database import get_db
from app.models.user import User
from app.models.income import Income
from app.models.expense import Expense
from app.models.uc_report import UCReport
from app.core.security import get_current_user, get_current_active_subscriber
from app.core.dates import get_tax_year, get_uc_assessment_period, get_hmrc_registration_deadline
from app.core.tax_calc import calculate_total_tax, calculate_tax_to_set_aside
from app.schemas.expense import EXPENSE_CATEGORIES
from app.api.v1.tax import get_tax_summary as get_tax_summary_data
from app.api.v1.uc import get_current_uc_period as get_uc_period_data

router = APIRouter(tags=["web"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def root():
    """Redirect to login page."""
    return RedirectResponse(url="/login")


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    current_user: User = Depends(get_current_active_subscriber),
    db: Session = Depends(get_db),
):
    """Dashboard view."""
    # Get tax summary
    tax_summary = await get_tax_summary_data(current_user, db)
    
    # Get UC period if enabled
    uc_period = None
    if current_user.uc_enabled and current_user.uc_assessment_day:
        try:
            uc_period = await get_uc_period_data(current_user, db)
        except:
            pass
    
    # Calculate days until HMRC deadline
    days_until_hmrc_deadline = None
    if current_user.trading_start_date:
        deadline = get_hmrc_registration_deadline(current_user.trading_start_date)
        days_until_hmrc_deadline = (deadline - date.today()).days
    
    # Count recent income
    recent_income_count = db.query(Income).filter(
        and_(
            Income.user_id == current_user.id,
            Income.date_received >= date.today().replace(day=1)
        )
    ).count()
    
    # Calculate recommended tax percentage
    from app.core.tax_calc import recommend_tax_set_aside_percentage
    recommendation = recommend_tax_set_aside_percentage(
        Decimal(str(tax_summary.net_profit)),
        date.today()
    )
    
    # Check if any next actions exist
    next_actions_exist = (
        not current_user.trading_start_date or
        (current_user.uc_enabled and uc_period and not uc_period.reported_at) or
        (days_until_hmrc_deadline and days_until_hmrc_deadline < 90) or
        (tax_summary.vat_threshold_proximity > 80) or
        recent_income_count == 0 or
        (recommendation["recommended_percentage"] > current_user.tax_set_aside_percentage)
    )
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user": current_user,
        "active_page": "dashboard",
        "tax_summary": tax_summary,
        "uc_period": uc_period,
        "days_until_hmrc_deadline": days_until_hmrc_deadline,
        "recent_income_count": recent_income_count,
        "recommended_percentage": recommendation["recommended_percentage"],
        "recommendation_reason": recommendation["reason"],
        "next_actions_exist": next_actions_exist,
    })


@router.get("/income", response_class=HTMLResponse)
async def income_page(
    request: Request,
    added_amount: float = None,
    save_amount: float = None,
    current_user: User = Depends(get_current_active_subscriber),
    db: Session = Depends(get_db),
):
    """Income tracking page."""
    incomes = db.query(Income).filter(
        Income.user_id == current_user.id
    ).order_by(Income.date_received.desc()).all()
    
    total_income = sum((i.amount for i in incomes), Decimal("0.00"))
    last_income_amount = incomes[0].amount if incomes else None
    
    # Calculate recommended tax percentage based on current year's profit
    from app.core.tax_calc import recommend_tax_set_aside_percentage
    total_expenses = db.query(func.sum(Expense.amount)).filter(
        Expense.user_id == current_user.id
    ).scalar() or Decimal("0.00")
    
    projected_profit = total_income - total_expenses
    recommendation = recommend_tax_set_aside_percentage(
        projected_profit,
        date.today()
    )
    
    return templates.TemplateResponse("income.html", {
        "request": request,
        "user": current_user,
        "active_page": "income",
        "incomes": incomes,
        "total_income": total_income,
        "last_income_amount": last_income_amount,
        "today": date.today().isoformat(),
        "added_amount": added_amount,
        "save_amount": save_amount,
        "recommended_percentage": recommendation["recommended_percentage"],
        "recommendation_reason": recommendation["reason"],
    })


@router.post("/income/add")
async def add_income(
    date_received: date = Form(...),
    amount: Decimal = Form(...),
    description: str = Form(...),
    tax_saved: Decimal = Form(None),
    current_user: User = Depends(get_current_active_subscriber),
    db: Session = Depends(get_db),
):
    """Add income transaction."""
    from app.core.tax_rulesets import get_ruleset_for_date
    
    tax_year = get_tax_year(date_received)
    ruleset = get_ruleset_for_date(date_received)
    
    income = Income(
        user_id=current_user.id,
        date_received=date_received,
        amount=amount,
        description=description,
        tax_saved=tax_saved if tax_saved and tax_saved > 0 else None,
        tax_year=tax_year,
        tax_ruleset_version=ruleset["version"],
    )
    
    db.add(income)
    db.commit()
    
    # Calculate amount to save for this payment
    amount_to_save = calculate_tax_to_set_aside(
        amount,
        Decimal(str(current_user.tax_set_aside_percentage))
    )
    
    return RedirectResponse(
        url=f"/income?added_amount={float(amount)}&save_amount={float(amount_to_save)}",
        status_code=303
    )


@router.post("/income/update-savings/{income_id}")
async def update_income_savings(
    income_id: str,
    tax_saved: Decimal = Form(...),
    current_user: User = Depends(get_current_active_subscriber),
    db: Session = Depends(get_db),
):
    """Update tax saved amount for an income transaction."""
    income = db.query(Income).filter(
        Income.id == income_id,
        Income.user_id == current_user.id,
    ).first()
    
    if income:
        income.tax_saved = tax_saved if tax_saved > 0 else None
        db.commit()
    
    return RedirectResponse(url="/income", status_code=303)


@router.post("/income/delete/{income_id}")
async def delete_income(
    income_id: str,
    current_user: User = Depends(get_current_active_subscriber),
    db: Session = Depends(get_db),
):
    """Delete income transaction."""
    income = db.query(Income).filter(
        Income.id == income_id,
        Income.user_id == current_user.id,
    ).first()
    
    if income:
        db.delete(income)
        db.commit()
    
    return RedirectResponse(url="/income", status_code=303)


@router.get("/expenses", response_class=HTMLResponse)
async def expenses_page(
    request: Request,
    current_user: User = Depends(get_current_active_subscriber),
    db: Session = Depends(get_db),
):
    """Expenses tracking page."""
    expenses = db.query(Expense).filter(
        Expense.user_id == current_user.id
    ).order_by(Expense.date_paid.desc()).all()
    
    total_expenses = sum((e.amount for e in expenses), Decimal("0.00"))
    
    return templates.TemplateResponse("expenses.html", {
        "request": request,
        "user": current_user,
        "active_page": "expenses",
        "expenses": expenses,
        "total_expenses": total_expenses,
        "categories": EXPENSE_CATEGORIES,
        "today": date.today().isoformat(),
    })


@router.post("/expenses/add")
async def add_expense(
    date_paid: date = Form(...),
    amount: Decimal = Form(...),
    category: str = Form(...),
    description: str = Form(...),
    current_user: User = Depends(get_current_active_subscriber),
    db: Session = Depends(get_db),
):
    """Add expense transaction."""
    tax_year = get_tax_year(date_paid)
    
    expense = Expense(
        user_id=current_user.id,
        date_paid=date_paid,
        amount=amount,
        category=category,
        description=description,
        tax_year=tax_year,
    )
    
    db.add(expense)
    db.commit()
    
    return RedirectResponse(url="/expenses", status_code=303)


@router.post("/expenses/delete/{expense_id}")
async def delete_expense(
    expense_id: str,
    current_user: User = Depends(get_current_active_subscriber),
    db: Session = Depends(get_db),
):
    """Delete expense transaction."""
    expense = db.query(Expense).filter(
        Expense.id == expense_id,
        Expense.user_id == current_user.id,
    ).first()
    
    if expense:
        db.delete(expense)
        db.commit()
    
    return RedirectResponse(url="/expenses", status_code=303)


@router.get("/tax", response_class=HTMLResponse)
async def tax_page(
    request: Request,
    current_user: User = Depends(get_current_active_subscriber),
    db: Session = Depends(get_db),
):
    """Tax summary page."""
    tax_summary = await get_tax_summary_data(current_user, db)
    
    days_until_hmrc_deadline = None
    if current_user.trading_start_date:
        deadline = get_hmrc_registration_deadline(current_user.trading_start_date)
        days_until_hmrc_deadline = (deadline - date.today()).days
    
    return templates.TemplateResponse("tax.html", {
        "request": request,
        "user": current_user,
        "active_page": "tax",
        "tax_summary": tax_summary,
        "days_until_hmrc_deadline": days_until_hmrc_deadline,
    })


@router.get("/uc", response_class=HTMLResponse)
async def uc_page(
    request: Request,
    current_user: User = Depends(get_current_active_subscriber),
    db: Session = Depends(get_db),
):
    """Universal Credit page."""
    if not current_user.uc_enabled:
        return RedirectResponse(url="/dashboard")
    
    # Get current period
    current_period = await get_uc_period_data(current_user, db)
    
    # Get previous periods
    previous_periods = db.query(UCReport).filter(
        UCReport.user_id == current_user.id
    ).order_by(UCReport.period_start.desc()).limit(12).all()
    
    return templates.TemplateResponse("uc.html", {
        "request": request,
        "user": current_user,
        "active_page": "uc",
        "current_period": current_period,
        "previous_periods": previous_periods,
        "today": date.today().isoformat(),
    })


@router.post("/uc/mark-reported")
async def mark_uc_reported(
    period_start: date = Form(...),
    reported_at: date = Form(...),
    current_user: User = Depends(get_current_active_subscriber),
    db: Session = Depends(get_db),
):
    """Mark UC period as reported."""
    # Find or create report
    period_end = get_uc_assessment_period(period_start, current_user.uc_assessment_day)[1]
    
    report = db.query(UCReport).filter(
        and_(
            UCReport.user_id == current_user.id,
            UCReport.period_start == period_start,
        )
    ).first()
    
    if not report:
        # Create report
        incomes = db.query(Income).filter(
            and_(
                Income.user_id == current_user.id,
                Income.date_received >= period_start,
                Income.date_received <= period_end,
            )
        ).all()
        
        expenses = db.query(Expense).filter(
            and_(
                Expense.user_id == current_user.id,
                Expense.date_paid >= period_start,
                Expense.date_paid <= period_end,
            )
        ).all()
        
        total_income = sum((i.amount for i in incomes), Decimal("0.00"))
        total_expenses = sum((e.amount for e in expenses), Decimal("0.00"))
        
        report = UCReport(
            user_id=current_user.id,
            period_start=period_start,
            period_end=period_end,
            total_income=total_income,
            total_expenses=total_expenses,
            net_profit=total_income - total_expenses,
        )
        db.add(report)
    
    report.reported_at = reported_at
    db.commit()
    
    return RedirectResponse(url="/uc", status_code=303)


@router.get("/settings", response_class=HTMLResponse)
async def settings_page(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Settings page."""
    # Calculate recommended tax percentage
    from app.core.tax_calc import recommend_tax_set_aside_percentage
    
    total_income = db.query(func.sum(Income.amount)).filter(
        Income.user_id == current_user.id
    ).scalar() or Decimal("0.00")
    
    total_expenses = db.query(func.sum(Expense.amount)).filter(
        Expense.user_id == current_user.id
    ).scalar() or Decimal("0.00")
    
    projected_profit = total_income - total_expenses
    recommendation = recommend_tax_set_aside_percentage(
        projected_profit,
        date.today()
    )
    
    return templates.TemplateResponse("settings.html", {
        "request": request,
        "user": current_user,
        "active_page": "settings",
        "recommended_percentage": recommendation["recommended_percentage"],
        "recommendation_reason": recommendation["reason"],
    })


@router.get("/exports", response_class=HTMLResponse)
async def exports_page(
    request: Request,
    current_user: User = Depends(get_current_active_subscriber),
):
    """Exports page."""
    return templates.TemplateResponse("exports.html", {
        "request": request,
        "user": current_user,
        "active_page": "exports",
    })


@router.post("/settings/profile")
async def update_profile(
    full_name: str = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update user profile."""
    if full_name:
        current_user.full_name = full_name
    
    db.commit()
    return RedirectResponse(url="/settings", status_code=303)


@router.post("/settings/trading")
async def update_trading(
    trading_start_date: date = Form(...),
    tax_set_aside_percentage: Decimal = Form(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update trading settings."""
    current_user.trading_start_date = trading_start_date
    current_user.tax_set_aside_percentage = tax_set_aside_percentage
    
    db.commit()
    return RedirectResponse(url="/settings", status_code=303)


@router.post("/settings/uc")
async def update_uc(
    uc_enabled: bool = Form(False),
    uc_assessment_day: int = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update UC settings."""
    current_user.uc_enabled = uc_enabled
    if uc_enabled and uc_assessment_day:
        current_user.uc_assessment_day = uc_assessment_day
    
    db.commit()
    return RedirectResponse(url="/settings", status_code=303)


@router.post("/settings/delete-account")
async def delete_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete user account."""
    db.delete(current_user)
    db.commit()
    
    return RedirectResponse(url="/login", status_code=303)
