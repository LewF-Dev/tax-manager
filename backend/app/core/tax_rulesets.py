"""UK tax rulesets versioned by tax year."""
from datetime import date
from typing import Dict, Any
from .dates import get_tax_year


# Tax rulesets by UK tax year
# All monetary values in GBP
TAX_RULESETS: Dict[str, Dict[str, Any]] = {
    "2023-24": {
        "version": "2023-24-v1",
        "personal_allowance": 12570,
        "basic_rate": 0.20,
        "basic_rate_threshold": 50270,
        "higher_rate": 0.40,
        "higher_rate_threshold": 125140,
        "additional_rate": 0.45,
        # National Insurance Class 2 (self-employed, flat weekly rate)
        "ni_class2_threshold": 6725,  # Annual small profits threshold
        "ni_class2_weekly": 3.45,
        # National Insurance Class 4 (self-employed, on profits)
        "ni_class4_lower_threshold": 12570,
        "ni_class4_upper_threshold": 50270,
        "ni_class4_rate": 0.09,
        "ni_class4_higher_rate": 0.02,
        # VAT
        "vat_threshold": 85000,
        "vat_registration_threshold": 90000,  # Must register by this point
    },
    "2024-25": {
        "version": "2024-25-v1",
        "personal_allowance": 12570,
        "basic_rate": 0.20,
        "basic_rate_threshold": 50270,
        "higher_rate": 0.40,
        "higher_rate_threshold": 125140,
        "additional_rate": 0.45,
        # National Insurance Class 2
        "ni_class2_threshold": 6725,
        "ni_class2_weekly": 3.45,
        # National Insurance Class 4
        "ni_class4_lower_threshold": 12570,
        "ni_class4_upper_threshold": 50270,
        "ni_class4_rate": 0.09,
        "ni_class4_higher_rate": 0.02,
        # VAT
        "vat_threshold": 85000,
        "vat_registration_threshold": 90000,
    },
    "2025-26": {
        "version": "2025-26-v1",
        # Placeholder - update when HMRC announces rates
        "personal_allowance": 12570,
        "basic_rate": 0.20,
        "basic_rate_threshold": 50270,
        "higher_rate": 0.40,
        "higher_rate_threshold": 125140,
        "additional_rate": 0.45,
        "ni_class2_threshold": 6725,
        "ni_class2_weekly": 3.45,
        "ni_class4_lower_threshold": 12570,
        "ni_class4_upper_threshold": 50270,
        "ni_class4_rate": 0.09,
        "ni_class4_higher_rate": 0.02,
        "vat_threshold": 85000,
        "vat_registration_threshold": 90000,
    },
}


def get_ruleset_for_date(transaction_date: date) -> Dict[str, Any]:
    """
    Get the tax ruleset for a specific transaction date.
    
    Args:
        transaction_date: Date of the transaction
        
    Returns:
        Tax ruleset dictionary for that tax year
        
    Raises:
        ValueError: If no ruleset exists for that tax year
    """
    tax_year = get_tax_year(transaction_date)
    
    if tax_year not in TAX_RULESETS:
        raise ValueError(
            f"No tax ruleset available for tax year {tax_year}. "
            f"Available years: {', '.join(TAX_RULESETS.keys())}"
        )
    
    return TAX_RULESETS[tax_year]


def get_ruleset_by_tax_year(tax_year: str) -> Dict[str, Any]:
    """
    Get the tax ruleset for a specific tax year string.
    
    Args:
        tax_year: Tax year string (e.g., "2024-25")
        
    Returns:
        Tax ruleset dictionary
        
    Raises:
        ValueError: If no ruleset exists for that tax year
    """
    if tax_year not in TAX_RULESETS:
        raise ValueError(
            f"No tax ruleset available for tax year {tax_year}. "
            f"Available years: {', '.join(TAX_RULESETS.keys())}"
        )
    
    return TAX_RULESETS[tax_year]


def get_available_tax_years() -> list[str]:
    """Returns list of tax years with available rulesets."""
    return sorted(TAX_RULESETS.keys())
