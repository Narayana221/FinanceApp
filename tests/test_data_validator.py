"""
Tests for data validation module.

Tests cover data cleaning, validation, error handling, and reporting.
"""

import pytest
import pandas as pd
from datetime import datetime
from utils.data_validator import (
    clean_amount,
    parse_date,
    validate_row,
    validate_dataframe
)


class TestCleanAmount:
    """Tests for clean_amount function."""
    
    def test_clean_valid_numeric(self):
        """Test cleaning valid numeric amounts."""
        assert clean_amount(100.50) == 100.50
        assert clean_amount(100) == 100.0
        assert clean_amount(-50.25) == -50.25
    
    def test_clean_string_amount(self):
        """Test cleaning string amounts."""
        assert clean_amount("100.50") == 100.50
        assert clean_amount("-45.30") == -45.30
        assert clean_amount("2500.00") == 2500.0
    
    def test_clean_amount_with_currency(self):
        """Test cleaning amounts with currency symbols."""
        assert clean_amount("£45.30") == 45.30
        assert clean_amount("$100.00") == 100.0
        assert clean_amount("€75.50") == 75.50
    
    def test_clean_amount_with_commas(self):
        """Test cleaning amounts with thousand separators."""
        assert clean_amount("1,234.56") == 1234.56
        assert clean_amount("10,000.00") == 10000.0
    
    def test_clean_amount_with_parentheses(self):
        """Test cleaning amounts in accounting format (parentheses for negative)."""
        assert clean_amount("(45.30)") == -45.30
        assert clean_amount("(100.00)") == -100.0
    
    def test_clean_amount_whitespace(self):
        """Test cleaning amounts with whitespace."""
        assert clean_amount("  100.50  ") == 100.50
        assert clean_amount("£ 45.30") == 45.30
    
    def test_clean_amount_missing(self):
        """Test handling missing amounts."""
        with pytest.raises(ValueError, match="Amount is missing"):
            clean_amount(pd.NA)
        with pytest.raises(ValueError, match="Amount is missing"):
            clean_amount(None)
    
    def test_clean_amount_empty(self):
        """Test handling empty string amounts."""
        with pytest.raises(ValueError, match="Amount is empty"):
            clean_amount("")
        with pytest.raises(ValueError, match="Amount is empty"):
            clean_amount("   ")
    
    def test_clean_amount_invalid(self):
        """Test handling invalid amounts."""
        with pytest.raises(ValueError, match="Cannot convert"):
            clean_amount("abc")
        with pytest.raises(ValueError, match="Cannot convert"):
            clean_amount("N/A")


class TestParseDate:
    """Tests for parse_date function."""
    
    def test_parse_datetime_object(self):
        """Test parsing datetime objects."""
        dt = datetime(2025, 1, 1)
        result = parse_date(dt)
        assert result.year == 2025
        assert result.month == 1
        assert result.day == 1
    
    def test_parse_timestamp_object(self):
        """Test parsing pandas Timestamp objects."""
        ts = pd.Timestamp('2025-01-01')
        result = parse_date(ts)
        assert result.year == 2025
        assert result.month == 1
        assert result.day == 1
    
    def test_parse_date_string_ddmmyyyy(self):
        """Test parsing DD/MM/YYYY format."""
        result = parse_date("01/01/2025", dayfirst=True)
        assert result.year == 2025
        assert result.month == 1
        assert result.day == 1
    
    def test_parse_date_string_mmddyyyy(self):
        """Test parsing MM/DD/YYYY format."""
        result = parse_date("01/15/2025", dayfirst=False)
        assert result.year == 2025
        assert result.month == 1
        assert result.day == 15
    
    def test_parse_date_iso_format(self):
        """Test parsing ISO format (YYYY-MM-DD)."""
        result = parse_date("2025-01-01")
        assert result.year == 2025
        assert result.month == 1
        assert result.day == 1
    
    def test_parse_date_missing(self):
        """Test handling missing dates."""
        with pytest.raises(ValueError, match="Date is missing"):
            parse_date(pd.NA)
        with pytest.raises(ValueError, match="Date is missing"):
            parse_date(None)
    
    def test_parse_date_empty(self):
        """Test handling empty string dates."""
        with pytest.raises(ValueError, match="Date is empty"):
            parse_date("")
        with pytest.raises(ValueError, match="Date is empty"):
            parse_date("   ")
    
    def test_parse_date_invalid(self):
        """Test handling invalid dates."""
        with pytest.raises(ValueError, match="Cannot parse"):
            parse_date("not a date")
        with pytest.raises(ValueError, match="Cannot parse"):
            parse_date("32/01/2025")  # Invalid day
        with pytest.raises(ValueError, match="Cannot parse"):
            parse_date("99/99/9999")  # Invalid everything


class TestValidateRow:
    """Tests for validate_row function."""
    
    def test_validate_valid_row(self):
        """Test validating a valid row."""
        row = pd.Series({
            'Date': '01/01/2025',
            'Amount': '100.50',
            'Description': 'Test',
            'Category': 'Food'
        })
        is_valid, error = validate_row(row, 1)
        assert is_valid is True
        assert error == ""
    
    def test_validate_missing_amount(self):
        """Test validating row with missing amount."""
        row = pd.Series({
            'Date': '01/01/2025',
            'Amount': pd.NA,
            'Description': 'Test'
        })
        is_valid, error = validate_row(row, 1)
        assert is_valid is False
        assert "Invalid amount" in error
    
    def test_validate_missing_date(self):
        """Test validating row with missing date."""
        row = pd.Series({
            'Date': pd.NA,
            'Amount': '100.50',
            'Description': 'Test'
        })
        is_valid, error = validate_row(row, 1)
        assert is_valid is False
        assert "Invalid date" in error
    
    def test_validate_invalid_amount(self):
        """Test validating row with invalid amount."""
        row = pd.Series({
            'Date': '01/01/2025',
            'Amount': 'abc',
            'Description': 'Test'
        })
        is_valid, error = validate_row(row, 5)
        assert is_valid is False
        assert "Row 5" in error
        assert "Invalid amount" in error
    
    def test_validate_invalid_date(self):
        """Test validating row with invalid date."""
        row = pd.Series({
            'Date': '32/13/2025',
            'Amount': '100.50',
            'Description': 'Test'
        })
        is_valid, error = validate_row(row, 10)
        assert is_valid is False
        assert "Row 10" in error
        assert "Invalid date" in error
    
    def test_validate_missing_columns(self):
        """Test validating row with missing required columns."""
        row = pd.Series({
            'Description': 'Test'
        })
        is_valid, error = validate_row(row, 1)
        assert is_valid is False
        assert "Missing required columns" in error


class TestValidateDataFrame:
    """Tests for validate_dataframe function."""
    
    def test_validate_all_valid_rows(self):
        """Test validating DataFrame with all valid rows."""
        df = pd.DataFrame({
            'Date': ['01/01/2025', '02/01/2025', '03/01/2025'],
            'Amount': ['100.50', '-45.30', '2500.00'],
            'Description': ['Salary', 'Tesco', 'Rent'],
            'Category': ['Income', 'Groceries', 'Housing']
        })
        
        cleaned_df, report = validate_dataframe(df)
        
        assert len(cleaned_df) == 3
        assert report['total_rows'] == 3
        assert report['valid_rows'] == 3
        assert report['skipped_rows'] == 0
        assert len(report['errors']) == 0
        assert len(report['warnings']) == 1  # Warning for < 10 transactions
    
    def test_validate_some_invalid_rows(self):
        """Test validating DataFrame with some invalid rows."""
        df = pd.DataFrame({
            'Date': ['01/01/2025', 'invalid', '03/01/2025', '04/01/2025'],
            'Amount': ['100.50', '-45.30', 'abc', '50.00'],
            'Description': ['Test1', 'Test2', 'Test3', 'Test4'],
            'Category': ['Cat1', 'Cat2', 'Cat3', 'Cat4']
        })
        
        cleaned_df, report = validate_dataframe(df)
        
        assert len(cleaned_df) == 2  # Only valid rows
        assert report['total_rows'] == 4
        assert report['valid_rows'] == 2
        assert report['skipped_rows'] == 2
        assert len(report['errors']) == 2
    
    def test_validate_empty_dataframe(self):
        """Test validating empty DataFrame."""
        df = pd.DataFrame()
        
        cleaned_df, report = validate_dataframe(df)
        
        assert len(cleaned_df) == 0
        assert report['total_rows'] == 0
        assert report['valid_rows'] == 0
        assert report['skipped_rows'] == 0
        assert 'No data to validate' in report['warnings']
    
    def test_validate_none_dataframe(self):
        """Test validating None DataFrame."""
        cleaned_df, report = validate_dataframe(None)
        
        assert len(cleaned_df) == 0
        assert report['total_rows'] == 0
        assert 'No data to validate' in report['warnings']
    
    def test_validate_sufficient_data_no_warning(self):
        """Test no warning for >= 10 valid transactions."""
        df = pd.DataFrame({
            'Date': ['01/01/2025', '02/01/2025', '03/01/2025', '04/01/2025', '05/01/2025',
                     '06/01/2025', '07/01/2025', '08/01/2025', '09/01/2025', '10/01/2025', '11/01/2025'],
            'Amount': ['100.50'] * 11,
            'Description': ['Test'] * 11,
            'Category': ['Cat'] * 11
        })
        
        cleaned_df, report = validate_dataframe(df)
        
        assert report['valid_rows'] == 11
        # Should not have insufficient data warning
        insufficient_warnings = [w for w in report['warnings'] if 'Only' in w and 'valid transaction' in w]
        assert len(insufficient_warnings) == 0
    
    def test_validate_insufficient_data_warning(self):
        """Test warning for < 10 valid transactions."""
        df = pd.DataFrame({
            'Date': ['01/01/2025', '02/01/2025'],
            'Amount': ['100.50', '-45.30'],
            'Description': ['Test1', 'Test2'],
            'Category': ['Cat1', 'Cat2']
        })
        
        cleaned_df, report = validate_dataframe(df)
        
        assert report['valid_rows'] == 2
        # Should have insufficient data warning
        insufficient_warnings = [w for w in report['warnings'] if 'Only' in w and 'valid transaction' in w]
        assert len(insufficient_warnings) == 1
        assert '2 valid transaction' in insufficient_warnings[0]
    
    def test_validate_all_rows_skipped_warning(self):
        """Test warning when all rows are skipped."""
        df = pd.DataFrame({
            'Date': ['invalid', 'bad date'],
            'Amount': ['abc', 'xyz'],
            'Description': ['Test1', 'Test2'],
            'Category': ['Cat1', 'Cat2']
        })
        
        cleaned_df, report = validate_dataframe(df)
        
        assert report['valid_rows'] == 0
        assert report['skipped_rows'] == 2
        # Should have warning about all rows skipped
        all_skipped_warnings = [w for w in report['warnings'] if 'All rows were skipped' in w]
        assert len(all_skipped_warnings) == 1
    
    def test_validate_high_skip_rate_warning(self):
        """Test warning when > 50% of rows are skipped."""
        df = pd.DataFrame({
            'Date': ['01/01/2025', 'invalid', 'bad', 'wrong', '05/01/2025'],
            'Amount': ['100.50', 'abc', 'xyz', 'def', '50.00'],
            'Description': ['Test'] * 5,
            'Category': ['Cat'] * 5
        })
        
        cleaned_df, report = validate_dataframe(df)
        
        assert report['valid_rows'] == 2
        assert report['skipped_rows'] == 3
        # Should have warning about high skip rate
        high_skip_warnings = [w for w in report['warnings'] if 'More than half' in w]
        assert len(high_skip_warnings) == 1
    
    def test_validate_cleaned_data_types(self):
        """Test that cleaned DataFrame has correct data types."""
        df = pd.DataFrame({
            'Date': ['01/01/2025', '02/01/2025'],
            'Amount': ['100.50', '-45.30'],
            'Description': ['Test1', 'Test2'],
            'Category': ['Cat1', 'Cat2']
        })
        
        cleaned_df, report = validate_dataframe(df)
        
        # Check data types
        assert cleaned_df['Amount'].dtype == float
        assert pd.api.types.is_datetime64_any_dtype(cleaned_df['Date'])
    
    def test_validate_error_details(self):
        """Test that error details include row numbers and reasons."""
        df = pd.DataFrame({
            'Date': ['01/01/2025', 'invalid', '03/01/2025'],
            'Amount': ['100.50', '-45.30', 'abc'],
            'Description': ['Test1', 'Test2', 'Test3'],
            'Category': ['Cat1', 'Cat2', 'Cat3']
        })
        
        cleaned_df, report = validate_dataframe(df)
        
        assert len(report['errors']) == 2
        
        # Check error structure
        for error in report['errors']:
            assert 'row' in error
            assert 'reason' in error
            assert isinstance(error['row'], int)
            assert isinstance(error['reason'], str)
