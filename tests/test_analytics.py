"""
Test suite for financial analytics utilities.

Tests income/expense calculation, net savings, savings rate,
extreme value flagging, and edge cases.
"""

import pytest
import pandas as pd
import numpy as np
from utils.analytics import (
    calculate_income_expenses,
    calculate_net_savings,
    calculate_savings_rate,
    get_financial_summary,
    flag_extreme_values
)


class TestCalculateIncomeExpenses:
    """Test income and expense calculation functionality."""
    
    def test_basic_income_and_expenses(self):
        """Test basic income and expense calculation."""
        df = pd.DataFrame({
            'Amount': [2500.00, -45.30, -100.00],
            'Category': ['Income', 'Groceries', 'Transport']
        })
        
        result = calculate_income_expenses(df)
        
        assert result['income'] == 2500.00
        assert result['expenses'] == 145.30
    
    def test_multiple_income_transactions(self):
        """Test with multiple income transactions."""
        df = pd.DataFrame({
            'Amount': [2500.00, 150.00, -200.00],
            'Category': ['Income', 'Income', 'Shopping']
        })
        
        result = calculate_income_expenses(df)
        
        assert result['income'] == 2650.00
        assert result['expenses'] == 200.00
    
    def test_multiple_expense_categories(self):
        """Test with expenses across multiple categories."""
        df = pd.DataFrame({
            'Amount': [2500.00, -45.30, -100.00, -25.50, -200.00],
            'Category': ['Income', 'Groceries', 'Transport', 'Eating Out', 'Shopping']
        })
        
        result = calculate_income_expenses(df)
        
        assert result['income'] == 2500.00
        assert result['expenses'] == 370.80
    
    def test_only_income(self):
        """Test with only income transactions."""
        df = pd.DataFrame({
            'Amount': [2500.00, 150.00],
            'Category': ['Income', 'Income']
        })
        
        result = calculate_income_expenses(df)
        
        assert result['income'] == 2650.00
        assert result['expenses'] == 0.00
    
    def test_only_expenses(self):
        """Test with only expense transactions."""
        df = pd.DataFrame({
            'Amount': [-45.30, -100.00, -25.50],
            'Category': ['Groceries', 'Transport', 'Eating Out']
        })
        
        result = calculate_income_expenses(df)
        
        assert result['income'] == 0.00
        assert result['expenses'] == 170.80
    
    def test_empty_dataframe(self):
        """Test with empty DataFrame."""
        df = pd.DataFrame(columns=['Amount', 'Category'])
        
        result = calculate_income_expenses(df)
        
        assert result['income'] == 0.00
        assert result['expenses'] == 0.00
    
    def test_none_dataframe(self):
        """Test with None input."""
        result = calculate_income_expenses(None)
        
        assert result['income'] == 0.00
        assert result['expenses'] == 0.00
    
    def test_missing_amount_column(self):
        """Test with missing Amount column."""
        df = pd.DataFrame({
            'Category': ['Income', 'Groceries']
        })
        
        result = calculate_income_expenses(df)
        
        assert result['income'] == 0.00
        assert result['expenses'] == 0.00
    
    def test_missing_category_column(self):
        """Test with missing Category column."""
        df = pd.DataFrame({
            'Amount': [2500.00, -45.30]
        })
        
        result = calculate_income_expenses(df)
        
        assert result['income'] == 0.00
        assert result['expenses'] == 0.00
    
    def test_negative_income_amount(self):
        """Test income with negative amount (edge case)."""
        df = pd.DataFrame({
            'Amount': [-2500.00, -100.00],
            'Category': ['Income', 'Transport']
        })
        
        result = calculate_income_expenses(df)
        
        # Income should still be converted to positive
        assert result['income'] == 2500.00
        assert result['expenses'] == 100.00
    
    def test_positive_expense_amount(self):
        """Test expense with positive amount (should not count as expense)."""
        df = pd.DataFrame({
            'Amount': [2500.00, 100.00],  # Second is positive but not Income
            'Category': ['Income', 'Transport']
        })
        
        result = calculate_income_expenses(df)
        
        assert result['income'] == 2500.00
        assert result['expenses'] == 0.00  # Positive non-Income not counted
    
    def test_uncategorized_transaction(self):
        """Test with uncategorized transactions."""
        df = pd.DataFrame({
            'Amount': [2500.00, -50.00, -100.00],
            'Category': ['Income', 'Uncategorized', 'Transport']
        })
        
        result = calculate_income_expenses(df)
        
        assert result['income'] == 2500.00
        assert result['expenses'] == 150.00
    
    def test_decimal_precision(self):
        """Test decimal precision and rounding."""
        df = pd.DataFrame({
            'Amount': [2500.555, -45.334, -100.125],
            'Category': ['Income', 'Groceries', 'Transport']
        })
        
        result = calculate_income_expenses(df)
        
        # Sum first, then abs(), then round - so 2500.555 becomes 2500.56
        assert result['income'] == 2500.55  # Rounded to 2 decimals
        assert result['expenses'] == 145.46


class TestCalculateNetSavings:
    """Test net savings calculation functionality."""
    
    def test_positive_savings(self):
        """Test calculation with positive savings."""
        result = calculate_net_savings(2500.00, 1500.00)
        assert result == 1000.00
    
    def test_negative_savings_deficit(self):
        """Test calculation with deficit (expenses > income)."""
        result = calculate_net_savings(1000.00, 1200.00)
        assert result == -200.00
    
    def test_zero_savings(self):
        """Test calculation with zero savings (income = expenses)."""
        result = calculate_net_savings(1500.00, 1500.00)
        assert result == 0.00
    
    def test_zero_income_and_expenses(self):
        """Test with zero income and expenses."""
        result = calculate_net_savings(0.00, 0.00)
        assert result == 0.00
    
    def test_decimal_precision(self):
        """Test decimal precision and rounding."""
        result = calculate_net_savings(2500.555, 1500.334)
        assert result == 1000.22


class TestCalculateSavingsRate:
    """Test savings rate calculation functionality."""
    
    def test_positive_savings_rate(self):
        """Test savings rate with positive savings."""
        result = calculate_savings_rate(2500.00, 1000.00)
        assert result == 40.00
    
    def test_negative_savings_rate(self):
        """Test savings rate with deficit."""
        result = calculate_savings_rate(2000.00, -200.00)
        assert result == -10.00
    
    def test_zero_savings_rate(self):
        """Test savings rate with zero savings."""
        result = calculate_savings_rate(2000.00, 0.00)
        assert result == 0.00
    
    def test_zero_income(self):
        """Test savings rate with zero income (division by zero)."""
        result = calculate_savings_rate(0.00, 0.00)
        assert result == 0.00
    
    def test_100_percent_savings_rate(self):
        """Test 100% savings rate (no expenses)."""
        result = calculate_savings_rate(2500.00, 2500.00)
        assert result == 100.00
    
    def test_over_100_percent_savings_rate(self):
        """Test > 100% savings rate (edge case with income from assets)."""
        result = calculate_savings_rate(1000.00, 1500.00)
        assert result == 150.00
    
    def test_decimal_precision(self):
        """Test decimal precision and rounding."""
        result = calculate_savings_rate(2500.00, 833.33)
        assert result == 33.33


class TestGetFinancialSummary:
    """Test complete financial summary functionality."""
    
    def test_complete_summary(self):
        """Test complete financial summary calculation."""
        df = pd.DataFrame({
            'Amount': [2500.00, -1200.00, -300.00],
            'Category': ['Income', 'Bills', 'Groceries']
        })
        
        summary = get_financial_summary(df)
        
        assert summary['total_income'] == 2500.00
        assert summary['total_expenses'] == 1500.00
        assert summary['net_savings'] == 1000.00
        assert summary['savings_rate'] == 40.00
    
    def test_summary_with_deficit(self):
        """Test summary with spending deficit."""
        df = pd.DataFrame({
            'Amount': [1000.00, -800.00, -400.00],
            'Category': ['Income', 'Shopping', 'Eating Out']
        })
        
        summary = get_financial_summary(df)
        
        assert summary['total_income'] == 1000.00
        assert summary['total_expenses'] == 1200.00
        assert summary['net_savings'] == -200.00
        assert summary['savings_rate'] == -20.00
    
    def test_summary_only_income(self):
        """Test summary with only income."""
        df = pd.DataFrame({
            'Amount': [2500.00, 150.00],
            'Category': ['Income', 'Income']
        })
        
        summary = get_financial_summary(df)
        
        assert summary['total_income'] == 2650.00
        assert summary['total_expenses'] == 0.00
        assert summary['net_savings'] == 2650.00
        assert summary['savings_rate'] == 100.00
    
    def test_summary_only_expenses(self):
        """Test summary with only expenses."""
        df = pd.DataFrame({
            'Amount': [-500.00, -300.00],
            'Category': ['Bills', 'Groceries']
        })
        
        summary = get_financial_summary(df)
        
        assert summary['total_income'] == 0.00
        assert summary['total_expenses'] == 800.00
        assert summary['net_savings'] == -800.00
        assert summary['savings_rate'] == 0.00  # Division by zero handled
    
    def test_summary_empty_dataframe(self):
        """Test summary with empty DataFrame."""
        df = pd.DataFrame(columns=['Amount', 'Category'])
        
        summary = get_financial_summary(df)
        
        assert summary['total_income'] == 0.00
        assert summary['total_expenses'] == 0.00
        assert summary['net_savings'] == 0.00
        assert summary['savings_rate'] == 0.00
    
    def test_summary_with_real_world_data(self):
        """Test summary with realistic transaction data."""
        df = pd.DataFrame({
            'Amount': [2500.00, -45.30, -12.50, -25.00, -100.00, -500.00, -15.99],
            'Category': ['Income', 'Groceries', 'Transport', 'Eating Out', 
                        'Shopping', 'Bills', 'Subscriptions']
        })
        
        summary = get_financial_summary(df)
        
        assert summary['total_income'] == 2500.00
        assert summary['total_expenses'] == 698.79
        assert summary['net_savings'] == 1801.21
        assert summary['savings_rate'] == 72.05


class TestFlagExtremeValues:
    """Test extreme value flagging functionality."""
    
    def test_flag_large_income(self):
        """Test flagging large income transaction."""
        df = pd.DataFrame({
            'Date': ['2024-01-15'],
            'Description': ['Salary'],
            'Amount': [2500.00],
            'Category': ['Income']
        })
        
        flagged = flag_extreme_values(df, threshold=1000.0)
        
        assert len(flagged) == 1
        assert flagged[0]['amount'] == 2500.00
        assert flagged[0]['description'] == 'Salary'
        assert 'Extreme value' in flagged[0]['flag_reason']
    
    def test_flag_large_expense(self):
        """Test flagging large expense transaction."""
        df = pd.DataFrame({
            'Date': ['2024-01-16'],
            'Description': ['Laptop'],
            'Amount': [-1200.00],
            'Category': ['Shopping']
        })
        
        flagged = flag_extreme_values(df, threshold=1000.0)
        
        assert len(flagged) == 1
        assert flagged[0]['amount'] == -1200.00
        assert flagged[0]['description'] == 'Laptop'
        assert '£1200.00' in flagged[0]['flag_reason']
    
    def test_flag_multiple_extreme_values(self):
        """Test flagging multiple extreme transactions."""
        df = pd.DataFrame({
            'Date': ['2024-01-15', '2024-01-16', '2024-01-17'],
            'Description': ['Salary', 'Laptop', 'Coffee'],
            'Amount': [2500.00, -1200.00, -3.50],
            'Category': ['Income', 'Shopping', 'Eating Out']
        })
        
        flagged = flag_extreme_values(df, threshold=1000.0)
        
        assert len(flagged) == 2
        assert any(f['amount'] == 2500.00 for f in flagged)
        assert any(f['amount'] == -1200.00 for f in flagged)
    
    def test_no_extreme_values(self):
        """Test with no extreme values."""
        df = pd.DataFrame({
            'Date': ['2024-01-15', '2024-01-16'],
            'Description': ['Coffee', 'Lunch'],
            'Amount': [-3.50, -8.99],
            'Category': ['Eating Out', 'Eating Out']
        })
        
        flagged = flag_extreme_values(df, threshold=1000.0)
        
        assert len(flagged) == 0
    
    def test_custom_threshold(self):
        """Test with custom threshold value."""
        df = pd.DataFrame({
            'Date': ['2024-01-15', '2024-01-16'],
            'Description': ['Grocery Shop', 'Coffee'],
            'Amount': [-150.00, -3.50],
            'Category': ['Groceries', 'Eating Out']
        })
        
        flagged = flag_extreme_values(df, threshold=100.0)
        
        assert len(flagged) == 1
        assert flagged[0]['amount'] == -150.00
    
    def test_empty_dataframe(self):
        """Test with empty DataFrame."""
        df = pd.DataFrame(columns=['Date', 'Description', 'Amount', 'Category'])
        
        flagged = flag_extreme_values(df, threshold=1000.0)
        
        assert len(flagged) == 0
    
    def test_none_dataframe(self):
        """Test with None input."""
        flagged = flag_extreme_values(None, threshold=1000.0)
        
        assert len(flagged) == 0
    
    def test_exact_threshold_not_flagged(self):
        """Test that exact threshold value is not flagged."""
        df = pd.DataFrame({
            'Date': ['2024-01-15'],
            'Description': ['Payment'],
            'Amount': [1000.00],
            'Category': ['Income']
        })
        
        flagged = flag_extreme_values(df, threshold=1000.0)
        
        assert len(flagged) == 0
    
    def test_slightly_above_threshold_flagged(self):
        """Test that value slightly above threshold is flagged."""
        df = pd.DataFrame({
            'Date': ['2024-01-15'],
            'Description': ['Payment'],
            'Amount': [1000.01],
            'Category': ['Income']
        })
        
        flagged = flag_extreme_values(df, threshold=1000.0)
        
        assert len(flagged) == 1
    
    def test_flagged_contains_all_fields(self):
        """Test that flagged transactions contain all required fields."""
        df = pd.DataFrame({
            'Date': ['2024-01-15'],
            'Description': ['Salary'],
            'Amount': [2500.00],
            'Category': ['Income']
        })
        
        flagged = flag_extreme_values(df, threshold=1000.0)
        
        assert 'date' in flagged[0]
        assert 'description' in flagged[0]
        assert 'amount' in flagged[0]
        assert 'category' in flagged[0]
        assert 'flag_reason' in flagged[0]


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_very_large_numbers(self):
        """Test with very large transaction amounts."""
        df = pd.DataFrame({
            'Amount': [1000000.00, -500000.00],
            'Category': ['Income', 'Shopping']
        })
        
        result = calculate_income_expenses(df)
        
        assert result['income'] == 1000000.00
        assert result['expenses'] == 500000.00
    
    def test_very_small_numbers(self):
        """Test with very small transaction amounts."""
        df = pd.DataFrame({
            'Amount': [0.01, -0.01],
            'Category': ['Income', 'Shopping']
        })
        
        result = calculate_income_expenses(df)
        
        assert result['income'] == 0.01
        assert result['expenses'] == 0.01
    
    def test_mixed_data_types_in_amount(self):
        """Test handling of mixed numeric types."""
        df = pd.DataFrame({
            'Amount': [2500, -45.30, np.float64(-100.00)],
            'Category': ['Income', 'Groceries', 'Transport']
        })
        
        result = calculate_income_expenses(df)
        
        assert result['income'] == 2500.00
        assert result['expenses'] == 145.30
    
    def test_integration_with_categorizer_output(self):
        """Test that analytics works with categorizer output format."""
        # Simulating output from categorizer.categorize_transactions()
        df = pd.DataFrame({
            'Date': ['2024-01-15', '2024-01-16', '2024-01-17'],
            'Description': ['Salary', 'Tesco', 'TfL'],
            'Amount': [2500.00, -45.30, -12.50],
            'Category': ['Income', 'Groceries', 'Transport']
        })
        
        summary = get_financial_summary(df)
        
        assert summary['total_income'] == 2500.00
        assert summary['total_expenses'] == 57.80
        assert summary['net_savings'] == 2442.20
        assert summary['savings_rate'] == 97.69
