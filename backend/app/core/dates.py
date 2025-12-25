"""UK tax year and date handling utilities."""
from datetime import date, timedelta
from typing import Tuple


def get_tax_year(transaction_date: date) -> str:
    """
    Returns the UK tax year string for a given date.
    
    UK tax year runs from 6 April to 5 April.
    
    Args:
        transaction_date: The date to determine tax year for
        
    Returns:
        Tax year string in format "YYYY-YY" (e.g., "2024-25")
    """
    if transaction_date.month < 4 or (transaction_date.month == 4 and transaction_date.day < 6):
        # Before April 6: use previous year as start
        start_year = transaction_date.year - 1
    else:
        # April 6 onwards: current year is start
        start_year = transaction_date.year
    
    end_year = start_year + 1
    return f"{start_year}-{str(end_year)[2:]}"


def get_tax_year_dates(tax_year: str) -> Tuple[date, date]:
    """
    Returns start and end dates for a UK tax year.
    
    Args:
        tax_year: Tax year string (e.g., "2024-25")
        
    Returns:
        Tuple of (start_date, end_date)
    """
    start_year = int(tax_year.split("-")[0])
    start_date = date(start_year, 4, 6)
    end_date = date(start_year + 1, 4, 5)
    return start_date, end_date


def get_current_tax_year() -> str:
    """Returns the current UK tax year string."""
    return get_tax_year(date.today())


def get_hmrc_registration_deadline(trading_start_date: date) -> date:
    """
    Calculate HMRC Self Assessment registration deadline.
    
    Must register by 5 October following the end of the tax year
    in which trading started.
    
    Args:
        trading_start_date: Date trading began
        
    Returns:
        Registration deadline date
    """
    tax_year = get_tax_year(trading_start_date)
    _, tax_year_end = get_tax_year_dates(tax_year)
    
    # Deadline is 5 October following tax year end
    deadline_year = tax_year_end.year
    if tax_year_end.month > 10 or (tax_year_end.month == 10 and tax_year_end.day > 5):
        deadline_year += 1
    
    return date(deadline_year, 10, 5)


def get_uc_assessment_period(reference_date: date, assessment_day: int) -> Tuple[date, date]:
    """
    Calculate UC assessment period containing the reference date.
    
    UC assessment periods run monthly from a fixed day (e.g., 15th to 14th).
    
    Args:
        reference_date: Date within the assessment period
        assessment_day: Day of month the period starts (1-28)
        
    Returns:
        Tuple of (period_start, period_end)
    """
    if not 1 <= assessment_day <= 28:
        raise ValueError("Assessment day must be between 1 and 28")
    
    # Determine which period the reference date falls in
    if reference_date.day >= assessment_day:
        # Period starts this month
        period_start = date(reference_date.year, reference_date.month, assessment_day)
    else:
        # Period started last month
        if reference_date.month == 1:
            period_start = date(reference_date.year - 1, 12, assessment_day)
        else:
            period_start = date(reference_date.year, reference_date.month - 1, assessment_day)
    
    # Period ends day before next period starts
    if period_start.month == 12:
        next_period_start = date(period_start.year + 1, 1, assessment_day)
    else:
        next_period_start = date(period_start.year, period_start.month + 1, assessment_day)
    
    period_end = next_period_start - timedelta(days=1)
    
    return period_start, period_end


def get_next_uc_assessment_period(current_period_start: date, assessment_day: int) -> Tuple[date, date]:
    """
    Get the next UC assessment period after the given period start.
    
    Args:
        current_period_start: Start date of current period
        assessment_day: Day of month periods start
        
    Returns:
        Tuple of (next_period_start, next_period_end)
    """
    if current_period_start.month == 12:
        next_start = date(current_period_start.year + 1, 1, assessment_day)
    else:
        next_start = date(current_period_start.year, current_period_start.month + 1, assessment_day)
    
    return get_uc_assessment_period(next_start, assessment_day)
