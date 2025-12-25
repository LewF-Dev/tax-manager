"""Tests for UK tax year and date utilities."""
import pytest
from datetime import date

from app.core.dates import (
    get_tax_year,
    get_tax_year_dates,
    get_hmrc_registration_deadline,
    get_uc_assessment_period,
)


class TestTaxYearCalculations:
    """Test UK tax year calculations."""
    
    def test_get_tax_year_before_april_6(self):
        """Test tax year for date before April 6."""
        # March 15, 2024 is in 2023-24 tax year
        tax_year = get_tax_year(date(2024, 3, 15))
        assert tax_year == "2023-24"
    
    def test_get_tax_year_on_april_6(self):
        """Test tax year for April 6 (start of new tax year)."""
        # April 6, 2024 is start of 2024-25 tax year
        tax_year = get_tax_year(date(2024, 4, 6))
        assert tax_year == "2024-25"
    
    def test_get_tax_year_after_april_6(self):
        """Test tax year for date after April 6."""
        # June 1, 2024 is in 2024-25 tax year
        tax_year = get_tax_year(date(2024, 6, 1))
        assert tax_year == "2024-25"
    
    def test_get_tax_year_dates(self):
        """Test getting start and end dates for tax year."""
        start, end = get_tax_year_dates("2024-25")
        
        assert start == date(2024, 4, 6)
        assert end == date(2025, 4, 5)
    
    def test_hmrc_registration_deadline(self):
        """Test HMRC registration deadline calculation."""
        # Started trading June 1, 2024 (in 2024-25 tax year)
        # Tax year ends April 5, 2025
        # Deadline is October 5, 2025
        deadline = get_hmrc_registration_deadline(date(2024, 6, 1))
        assert deadline == date(2025, 10, 5)
    
    def test_hmrc_registration_deadline_early_in_tax_year(self):
        """Test deadline for trading start early in tax year."""
        # Started April 10, 2024 (in 2024-25 tax year)
        # Deadline is October 5, 2025
        deadline = get_hmrc_registration_deadline(date(2024, 4, 10))
        assert deadline == date(2025, 10, 5)


class TestUCAssessmentPeriods:
    """Test Universal Credit assessment period calculations."""
    
    def test_uc_period_mid_month(self):
        """Test UC period calculation for mid-month assessment day."""
        # Assessment day is 15th
        # Reference date is June 20, 2024
        # Period should be June 15 - July 14
        period_start, period_end = get_uc_assessment_period(
            date(2024, 6, 20),
            15
        )
        
        assert period_start == date(2024, 6, 15)
        assert period_end == date(2024, 7, 14)
    
    def test_uc_period_before_assessment_day(self):
        """Test UC period when reference date is before assessment day."""
        # Assessment day is 15th
        # Reference date is June 10, 2024
        # Period should be May 15 - June 14
        period_start, period_end = get_uc_assessment_period(
            date(2024, 6, 10),
            15
        )
        
        assert period_start == date(2024, 5, 15)
        assert period_end == date(2024, 6, 14)
    
    def test_uc_period_on_assessment_day(self):
        """Test UC period when reference date is the assessment day."""
        # Assessment day is 15th
        # Reference date is June 15, 2024
        # Period should be June 15 - July 14
        period_start, period_end = get_uc_assessment_period(
            date(2024, 6, 15),
            15
        )
        
        assert period_start == date(2024, 6, 15)
        assert period_end == date(2024, 7, 14)
    
    def test_uc_period_year_boundary(self):
        """Test UC period spanning year boundary."""
        # Assessment day is 20th
        # Reference date is December 25, 2024
        # Period should be December 20, 2024 - January 19, 2025
        period_start, period_end = get_uc_assessment_period(
            date(2024, 12, 25),
            20
        )
        
        assert period_start == date(2024, 12, 20)
        assert period_end == date(2025, 1, 19)
    
    def test_uc_period_invalid_assessment_day(self):
        """Test that invalid assessment day raises error."""
        with pytest.raises(ValueError):
            get_uc_assessment_period(date(2024, 6, 15), 0)
        
        with pytest.raises(ValueError):
            get_uc_assessment_period(date(2024, 6, 15), 29)
