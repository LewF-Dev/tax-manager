"""Tax calculation engine with ruleset versioning."""
from decimal import Decimal
from typing import Dict, Any
from datetime import date

from .tax_rulesets import get_ruleset_for_date


def calculate_income_tax(profit: Decimal, ruleset: Dict[str, Any]) -> Decimal:
    """
    Calculate income tax on self-employment profit.
    
    Args:
        profit: Net profit for the tax year
        ruleset: Tax ruleset to use
        
    Returns:
        Income tax amount
    """
    if profit <= 0:
        return Decimal("0.00")
    
    profit = Decimal(str(profit))
    personal_allowance = Decimal(str(ruleset["personal_allowance"]))
    basic_rate_threshold = Decimal(str(ruleset["basic_rate_threshold"]))
    higher_rate_threshold = Decimal(str(ruleset["higher_rate_threshold"]))
    
    # Taxable income after personal allowance
    taxable = max(Decimal("0"), profit - personal_allowance)
    
    if taxable == 0:
        return Decimal("0.00")
    
    tax = Decimal("0.00")
    
    # Basic rate band
    basic_band_limit = basic_rate_threshold - personal_allowance
    basic_taxable = min(taxable, basic_band_limit)
    tax += basic_taxable * Decimal(str(ruleset["basic_rate"]))
    
    # Higher rate band
    if taxable > basic_band_limit:
        higher_band_limit = higher_rate_threshold - basic_rate_threshold
        higher_taxable = min(taxable - basic_band_limit, higher_band_limit)
        tax += higher_taxable * Decimal(str(ruleset["higher_rate"]))
        
        # Additional rate band
        if taxable > (higher_rate_threshold - personal_allowance):
            additional_taxable = taxable - (higher_rate_threshold - personal_allowance)
            tax += additional_taxable * Decimal(str(ruleset["additional_rate"]))
    
    return tax.quantize(Decimal("0.01"))


def calculate_ni_class2(profit: Decimal, ruleset: Dict[str, Any]) -> Decimal:
    """
    Calculate National Insurance Class 2 (flat weekly rate for self-employed).
    
    Only payable if profits exceed small profits threshold.
    
    Args:
        profit: Net profit for the tax year
        ruleset: Tax ruleset to use
        
    Returns:
        NI Class 2 amount (52 weeks)
    """
    if profit <= 0:
        return Decimal("0.00")
    
    profit = Decimal(str(profit))
    threshold = Decimal(str(ruleset["ni_class2_threshold"]))
    
    if profit < threshold:
        return Decimal("0.00")
    
    weekly_rate = Decimal(str(ruleset["ni_class2_weekly"]))
    annual = weekly_rate * 52
    
    return annual.quantize(Decimal("0.01"))


def calculate_ni_class4(profit: Decimal, ruleset: Dict[str, Any]) -> Decimal:
    """
    Calculate National Insurance Class 4 (on profits).
    
    Args:
        profit: Net profit for the tax year
        ruleset: Tax ruleset to use
        
    Returns:
        NI Class 4 amount
    """
    if profit <= 0:
        return Decimal("0.00")
    
    profit = Decimal(str(profit))
    lower_threshold = Decimal(str(ruleset["ni_class4_lower_threshold"]))
    upper_threshold = Decimal(str(ruleset["ni_class4_upper_threshold"]))
    
    # No NI Class 4 below lower threshold
    if profit <= lower_threshold:
        return Decimal("0.00")
    
    ni = Decimal("0.00")
    
    # Main rate (between lower and upper threshold)
    main_rate_profit = min(profit, upper_threshold) - lower_threshold
    ni += main_rate_profit * Decimal(str(ruleset["ni_class4_rate"]))
    
    # Higher rate (above upper threshold)
    if profit > upper_threshold:
        higher_rate_profit = profit - upper_threshold
        ni += higher_rate_profit * Decimal(str(ruleset["ni_class4_higher_rate"]))
    
    return ni.quantize(Decimal("0.01"))


def calculate_total_tax(profit: Decimal, transaction_date: date) -> Dict[str, Any]:
    """
    Calculate all tax obligations for a given profit and date.
    
    Uses the correct ruleset based on transaction date.
    
    Args:
        profit: Net profit
        transaction_date: Date to determine tax year/ruleset
        
    Returns:
        Dictionary with breakdown of all taxes
    """
    ruleset = get_ruleset_for_date(transaction_date)
    
    income_tax = calculate_income_tax(profit, ruleset)
    ni_class2 = calculate_ni_class2(profit, ruleset)
    ni_class4 = calculate_ni_class4(profit, ruleset)
    total = income_tax + ni_class2 + ni_class4
    
    return {
        "income_tax": float(income_tax),
        "ni_class2": float(ni_class2),
        "ni_class4": float(ni_class4),
        "total_tax": float(total),
        "tax_year": ruleset["version"].split("-v")[0],
        "ruleset_version": ruleset["version"],
    }


def calculate_tax_to_set_aside(
    amount: Decimal,
    set_aside_percentage: Decimal
) -> Decimal:
    """
    Calculate amount to set aside for tax from a payment.
    
    This is a simple percentage-based calculation for immediate discipline,
    not a precise tax calculation.
    
    Args:
        amount: Payment amount received
        set_aside_percentage: Percentage to set aside (e.g., 20.00 for 20%)
        
    Returns:
        Amount to set aside
    """
    if amount <= 0 or set_aside_percentage <= 0:
        return Decimal("0.00")
    
    amount = Decimal(str(amount))
    percentage = Decimal(str(set_aside_percentage)) / 100
    
    return (amount * percentage).quantize(Decimal("0.01"))
