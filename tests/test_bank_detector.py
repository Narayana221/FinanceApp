"""
Unit tests for bank format detection and column mapping.

Tests cover:
- Monzo format detection
- Revolut format detection
- Barclays format detection
- Fallback detection for unknown formats
- Error handling for undetectable formats
- Case-insensitive matching
"""

import pytest
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.bank_detector import (
    detect_bank_format,
    normalize_columns,
    fallback_detect,
    detect_and_normalize,
    is_date_column,
    is_amount_column
)


class TestBankFormatDetection:
    """Test suite for bank format detection."""
    
    def test_detect_monzo_format(self):
        """Test detection of Monzo CSV format."""
        # Arrange
        df = pd.DataFrame({
            'Date': ['01/01/2025'],
            'Name': ['Tesco'],
            'Amount': [-45.30],
            'Category': ['Groceries']
        })
        
        # Act
        result = detect_bank_format(df)
        
        # Assert
        assert result == 'monzo'
    
    def test_detect_monzo_format_case_insensitive(self):
        """Test Monzo detection with different case."""
        # Arrange
        df = pd.DataFrame({
            'DATE': ['01/01/2025'],
            'name': ['Tesco'],
            'AMOUNT': [-45.30],
            'category': ['Groceries']
        })
        
        # Act
        result = detect_bank_format(df)
        
        # Assert
        assert result == 'monzo'
    
    def test_detect_revolut_format(self):
        """Test detection of Revolut CSV format."""
        # Arrange
        df = pd.DataFrame({
            'Started Date': ['01/01/2025 10:30:00'],
            'Description': ['Tesco Superstore'],
            'Amount': [-45.30],
            'Category': ['Groceries']
        })
        
        # Act
        result = detect_bank_format(df)
        
        # Assert
        assert result == 'revolut'
    
    def test_detect_barclays_format(self):
        """Test detection of Barclays CSV format."""
        # Arrange
        df = pd.DataFrame({
            'Number': ['001'],
            'Date': ['01/01/2025'],
            'Account': ['Current'],
            'Amount': [-45.30],
            'Subcategory': ['Shopping'],
            'Memo': ['Tesco Superstore']
        })
        
        # Act
        result = detect_bank_format(df)
        
        # Assert
        assert result == 'barclays'
    
    def test_detect_unknown_format(self):
        """Test that unknown format returns None."""
        # Arrange
        df = pd.DataFrame({
            'Transaction Date': ['01/01/2025'],
            'Merchant': ['Tesco'],
            'Value': [-45.30]
        })
        
        # Act
        result = detect_bank_format(df)
        
        # Assert
        assert result is None


class TestColumnNormalization:
    """Test suite for column normalization."""
    
    def test_normalize_monzo_columns(self):
        """Test normalization of Monzo columns."""
        # Arrange
        df = pd.DataFrame({
            'Date': ['01/01/2025', '02/01/2025'],
            'Name': ['Tesco', 'Sainsburys'],
            'Amount': [-45.30, -32.15],
            'Category': ['Groceries', 'Groceries']
        })
        
        # Act
        result = normalize_columns(df, 'monzo')
        
        # Assert
        assert 'Date' in result.columns
        assert 'Description' in result.columns
        assert 'Amount' in result.columns
        assert 'Category' in result.columns
        assert result['Description'].tolist() == ['Tesco', 'Sainsburys']
    
    def test_normalize_revolut_columns(self):
        """Test normalization of Revolut columns."""
        # Arrange
        df = pd.DataFrame({
            'Started Date': ['01/01/2025 10:30:00'],
            'Description': ['Tesco Superstore'],
            'Amount': [-45.30],
            'Category': ['Groceries']
        })
        
        # Act
        result = normalize_columns(df, 'revolut')
        
        # Assert
        assert 'Date' in result.columns
        assert 'Description' in result.columns
        assert 'Amount' in result.columns
        assert result['Date'].iloc[0] == '01/01/2025 10:30:00'
    
    def test_normalize_barclays_columns(self):
        """Test normalization of Barclays columns."""
        # Arrange
        df = pd.DataFrame({
            'Date': ['01/01/2025'],
            'Memo': ['Tesco Superstore'],
            'Amount': [-45.30],
            'Number': ['001']
        })
        
        # Act
        result = normalize_columns(df, 'barclays')
        
        # Assert
        assert 'Date' in result.columns
        assert 'Description' in result.columns
        assert 'Amount' in result.columns
        assert result['Description'].iloc[0] == 'Tesco Superstore'
        # Barclays doesn't have Category, so it shouldn't be in result
        assert 'Category' not in result.columns
    
    def test_normalize_invalid_format_raises_error(self):
        """Test that invalid format name raises ValueError."""
        # Arrange
        df = pd.DataFrame({'Date': ['01/01/2025']})
        
        # Act & Assert
        with pytest.raises(ValueError, match="Unknown format"):
            normalize_columns(df, 'invalid_bank')


class TestFallbackDetection:
    """Test suite for fallback detection."""
    
    def test_is_date_column_dd_mm_yyyy(self):
        """Test date column detection for dd/mm/yyyy format."""
        # Arrange
        series = pd.Series(['01/01/2025', '02/01/2025', '03/01/2025'])
        
        # Act
        result = is_date_column(series)
        
        # Assert
        assert result is True
    
    def test_is_date_column_yyyy_mm_dd(self):
        """Test date column detection for yyyy-mm-dd format."""
        # Arrange
        series = pd.Series(['2025-01-01', '2025-01-02', '2025-01-03'])
        
        # Act
        result = is_date_column(series)
        
        # Assert
        assert result is True
    
    def test_is_date_column_not_dates(self):
        """Test that non-date column returns False."""
        # Arrange
        series = pd.Series(['Tesco', 'Sainsburys', 'Asda'])
        
        # Act
        result = is_date_column(series)
        
        # Assert
        assert result is False
    
    def test_is_amount_column_numeric(self):
        """Test amount column detection for numeric data."""
        # Arrange
        series = pd.Series([-45.30, -32.15, 2500.00])
        
        # Act
        result = is_amount_column(series)
        
        # Assert
        assert result is True
    
    def test_is_amount_column_string_numbers(self):
        """Test amount column detection for string numbers."""
        # Arrange
        series = pd.Series(['-45.30', '-32.15', '2500.00'])
        
        # Act
        result = is_amount_column(series)
        
        # Assert
        assert result is True
    
    def test_is_amount_column_with_currency(self):
        """Test amount column detection with currency symbols."""
        # Arrange
        series = pd.Series(['£45.30', '£32.15', '£2500.00'])
        
        # Act
        result = is_amount_column(series)
        
        # Assert
        assert result is True
    
    def test_is_amount_column_not_amounts(self):
        """Test that non-amount column returns False."""
        # Arrange
        series = pd.Series(['Tesco', 'Sainsburys', 'Asda'])
        
        # Act
        result = is_amount_column(series)
        
        # Assert
        assert result is False
    
    def test_fallback_detect_custom_format(self):
        """Test fallback detection for custom format."""
        # Arrange
        df = pd.DataFrame({
            'Transaction Date': ['01/01/2025', '02/01/2025'],
            'Merchant': ['Tesco', 'Sainsburys'],
            'Value': [-45.30, -32.15]
        })
        
        # Act
        mapping = fallback_detect(df)
        
        # Assert
        assert 'Date' in mapping
        assert 'Amount' in mapping
        assert 'Description' in mapping
        assert mapping['Date'] == 'Transaction Date'
        assert mapping['Amount'] == 'Value'
        assert mapping['Description'] == 'Merchant'


class TestDetectAndNormalize:
    """Test suite for combined detect and normalize operation."""
    
    def test_detect_and_normalize_monzo(self):
        """Test end-to-end detection and normalization for Monzo."""
        # Arrange
        df = pd.DataFrame({
            'Date': ['01/01/2025', '02/01/2025'],
            'Name': ['Tesco', 'Sainsburys'],
            'Amount': [-45.30, -32.15],
            'Category': ['Groceries', 'Groceries']
        })
        
        # Act
        normalized_df, format_name = detect_and_normalize(df)
        
        # Assert
        assert format_name == 'monzo'
        assert 'Date' in normalized_df.columns
        assert 'Description' in normalized_df.columns
        assert 'Amount' in normalized_df.columns
        assert len(normalized_df) == 2
    
    def test_detect_and_normalize_revolut(self):
        """Test end-to-end detection and normalization for Revolut."""
        # Arrange
        df = pd.DataFrame({
            'Started Date': ['01/01/2025 10:30:00'],
            'Description': ['Tesco Superstore'],
            'Amount': [-45.30],
            'Category': ['Groceries']
        })
        
        # Act
        normalized_df, format_name = detect_and_normalize(df)
        
        # Assert
        assert format_name == 'revolut'
        assert 'Description' in normalized_df.columns
    
    def test_detect_and_normalize_fallback(self):
        """Test end-to-end with fallback detection."""
        # Arrange
        df = pd.DataFrame({
            'Transaction Date': ['01/01/2025', '02/01/2025'],
            'Merchant': ['Tesco', 'Sainsburys'],
            'Value': [-45.30, -32.15]
        })
        
        # Act
        normalized_df, format_name = detect_and_normalize(df)
        
        # Assert
        assert format_name == 'auto-detected'
        assert 'Date' in normalized_df.columns
        assert 'Description' in normalized_df.columns
        assert 'Amount' in normalized_df.columns
    
    def test_detect_and_normalize_missing_critical_columns(self):
        """Test that missing critical columns raises ValueError."""
        # Arrange
        df = pd.DataFrame({
            'Random Column': ['A', 'B'],
            'Another Column': ['C', 'D']
        })
        
        # Act & Assert
        with pytest.raises(ValueError, match="Unable to detect required columns"):
            detect_and_normalize(df)
    
    def test_detect_and_normalize_missing_amount_only(self):
        """Test error when only Date is detected."""
        # Arrange
        df = pd.DataFrame({
            'Date': ['01/01/2025', '02/01/2025'],
            'Text': ['Some text', 'More text']
        })
        
        # Act & Assert
        with pytest.raises(ValueError, match="Unable to detect required columns"):
            detect_and_normalize(df)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
