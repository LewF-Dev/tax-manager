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


def recommend_tax_set_aside_percentage(
    projected_annual_profit: Decimal,
    transaction_date: date
) -> Dict[str, Any]:
    """
    Recommend a tax set-aside percentage based on projected annual profit.
    
    Calculates the effective tax rate and adds a buffer for safety.
    
    Args:
        projected_annual_profit: Estimated annual profit
        transaction_date: Date to determine tax year/ruleset
        
    Returns:
        Dictionary with recommended percentage and reasoning
    """
    if projected_annual_profit <= 0:
        return {
            "recommended_percentage": 20,
            "reason": "Default recommendation",
            "is_sufficient": True
        }
    
    # Calculate actual tax on projected profit
    tax_breakdown = calculate_total_tax(projected_annual_profit, transaction_date)
    total_tax = Decimal(str(tax_breakdown["total_tax"]))
    
    # Calculate effective tax rate
    effective_rate = (total_tax / projected_annual_profit * 100) if projected_annual_profit > 0 else Decimal("0")
    
    # Add 5% buffer for safety and round up to nearest 5%
    recommended = int((effective_rate + 5).quantize(Decimal("1")))
    recommended = ((recommended + 4) // 5) * 5  # Round up to nearest 5
    
    # Minimum 15%, maximum 50%
    recommended = max(15, min(50, recommended))
    
    # Determine reason based on profit thresholds
    profit_float = float(projected_annual_profit)
    
    if profit_float < 12570:
        reason = "Below Personal Allowance - minimal tax expected"
    elif profit_float < 25000:
        reason = "Basic rate taxpayer - 20% Income Tax + NI"
    elif profit_float < 50270:
        reason = "Higher basic rate income - increased NI contributions"
    elif profit_float < 100000:
        reason = "Higher rate taxpayer - 40% Income Tax on earnings over £50,270"
    else:
        reason = "High earner - 40%+ tax rates apply"
    
    return {
        "recommended_percentage": recommended,
        "effective_tax_rate": float(effective_rate.quantize(Decimal("0.1"))),
        "reason": reason,
        "is_sufficient": True
    }
