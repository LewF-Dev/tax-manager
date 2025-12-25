"""Tests for tax calculation engine."""
import pytest
from decimal import Decimal
from datetime import date

from app.core.tax_calc import (
    calculate_income_tax,
    calculate_ni_class2,
    calculate_ni_class4,
    calculate_total_tax,
)
from app.core.tax_rulesets import get_ruleset_for_date


class TestTaxCalculations:
    """Test tax calculation functions."""
    
    def test_income_tax_below_personal_allowance(self):
        """Test income tax when profit is below personal allowance."""
        ruleset = get_ruleset_for_date(date(2024, 6, 1))
        profit = Decimal("10000.00")
        
        tax = calculate_income_tax(profit, ruleset)
        
        assert tax == Decimal("0.00")
    
    def test_income_tax_basic_rate(self):
        """Test income tax in basic rate band."""
        ruleset = get_ruleset_for_date(date(2024, 6, 1))
        profit = Decimal("30000.00")
        
        tax = calculate_income_tax(profit, ruleset)
        
        # £30,000 - £12,570 = £17,430 taxable
        # £17,430 * 20% = £3,486
        assert tax == Decimal("3486.00")
    
    def test_ni_class2_below_threshold(self):
        """Test NI Class 2 below small profits threshold."""
        ruleset = get_ruleset_for_date(date(2024, 6, 1))
        profit = Decimal("6000.00")
        
        ni = calculate_ni_class2(profit, ruleset)
        
        assert ni == Decimal("0.00")
    
    def test_ni_class2_above_threshold(self):
        """Test NI Class 2 above small profits threshold."""
        ruleset = get_ruleset_for_date(date(2024, 6, 1))
        profit = Decimal("10000.00")
        
        ni = calculate_ni_class2(profit, ruleset)
        
        # £3.45 * 52 weeks = £179.40
        assert ni == Decimal("179.40")
    
    def test_ni_class4_below_threshold(self):
        """Test NI Class 4 below lower threshold."""
        ruleset = get_ruleset_for_date(date(2024, 6, 1))
        profit = Decimal("10000.00")
        
        ni = calculate_ni_class4(profit, ruleset)
        
        assert ni == Decimal("0.00")
    
    def test_ni_class4_main_rate(self):
        """Test NI Class 4 in main rate band."""
        ruleset = get_ruleset_for_date(date(2024, 6, 1))
        profit = Decimal("30000.00")
        
        ni = calculate_ni_class4(profit, ruleset)
        
        # £30,000 - £12,570 = £17,430
        # £17,430 * 9% = £1,568.70
        assert ni == Decimal("1568.70")
    
    def test_total_tax_calculation(self):
        """Test complete tax calculation."""
        profit = Decimal("30000.00")
        transaction_date = date(2024, 6, 1)
        
        result = calculate_total_tax(profit, transaction_date)
        
        assert "income_tax" in result
        assert "ni_class2" in result
        assert "ni_class4" in result
        assert "total_tax" in result
        assert "tax_year" in result
        assert "ruleset_version" in result
        
        # Verify total is sum of components
        total = (
            Decimal(str(result["income_tax"])) +
            Decimal(str(result["ni_class2"])) +
            Decimal(str(result["ni_class4"]))
        )
        assert Decimal(str(result["total_tax"])) == total
    
    def test_tax_calculation_uses_correct_ruleset(self):
        """Test that tax calculation uses correct ruleset for date."""
        profit = Decimal("30000.00")
        
        # Test 2023-24 tax year
        result_2023 = calculate_total_tax(profit, date(2023, 6, 1))
        assert result_2023["tax_year"] == "2023-24"
        
        # Test 2024-25 tax year
        result_2024 = calculate_total_tax(profit, date(2024, 6, 1))
        assert result_2024["tax_year"] == "2024-25"
