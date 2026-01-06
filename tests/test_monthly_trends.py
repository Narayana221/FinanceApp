"""
Test suite for monthly trend analysis functionality.

Tests monthly aggregation, trend calculations, and edge cases.
"""

import pandas as pd
import numpy as np
from datetime import datetime
from utils.analytics import get_monthly_trends


class TestGetMonthlyTrends:
    """Test monthly trend aggregation functionality."""
    
    def test_basic_monthly_aggregation(self):
        """Test basic monthly trend aggregation with multiple months."""
        df = pd.DataFrame({
            'Date': ['2025-01-15', '2025-01-20', '2025-02-10', '2025-02-15'],
            'Amount': [2500.00, -1000.00, 2500.00, -800.00],
            'Category': ['Income', 'Bills', 'Income', 'Groceries']
        })
        
        trends = get_monthly_trends(df)
        
        assert len(trends) == 2
        assert trends['Month'].tolist() == ['2025-01', '2025-02']
        assert trends['Income'].tolist() == [2500.00, 2500.00]
        assert trends['Expenses'].tolist() == [1000.00, 800.00]
    
    def test_monthly_aggregation_multiple_months(self):
        """Test aggregation across multiple months with varied transactions."""
        df = pd.DataFrame({
            'Date': ['2025-01-10', '2025-01-15', '2025-02-05', '2025-02-20', '2025-03-10'],
            'Amount': [2500.00, -1200.00, 2600.00, -1300.00, 2550.00],
            'Category': ['Income', 'Bills', 'Income', 'Shopping', 'Income']
        })
        
        trends = get_monthly_trends(df)
        
        assert len(trends) == 3
        assert trends['Month'].tolist() == ['2025-01', '2025-02', '2025-03']
        assert trends['Income'].tolist() == [2500.00, 2600.00, 2550.00]
        assert trends['Expenses'].tolist() == [1200.00, 1300.00, 0.00]
    
    def test_monthly_net_savings_calculation(self):
        """Test net savings calculation per month."""
        df = pd.DataFrame({
            'Date': ['2025-01-10', '2025-01-20', '2025-02-10'],
            'Amount': [3000.00, -1500.00, 2500.00],
            'Category': ['Income', 'Bills', 'Income']
        })
        
        trends = get_monthly_trends(df)
        
        assert trends.loc[0, 'Net Savings'] == 1500.00  # 3000 - 1500
        assert trends.loc[1, 'Net Savings'] == 2500.00  # 2500 - 0
    
    def test_monthly_savings_rate_calculation(self):
        """Test savings rate calculation per month."""
        df = pd.DataFrame({
            'Date': ['2025-01-10', '2025-01-20', '2025-02-10', '2025-02-15'],
            'Amount': [2500.00, -1500.00, 2500.00, -1000.00],
            'Category': ['Income', 'Bills', 'Income', 'Groceries']
        })
        
        trends = get_monthly_trends(df)
        
        # January: (1000 / 2500) * 100 = 40%
        assert trends.loc[0, 'Savings Rate'] == 40.00
        # February: (1500 / 2500) * 100 = 60%
        assert trends.loc[1, 'Savings Rate'] == 60.00
    
    def test_single_month_data(self):
        """Test with data from only one month."""
        df = pd.DataFrame({
            'Date': ['2025-01-10', '2025-01-15', '2025-01-20'],
            'Amount': [2500.00, -500.00, -300.00],
            'Category': ['Income', 'Groceries', 'Transport']
        })
        
        trends = get_monthly_trends(df)
        
        assert len(trends) == 1
        assert trends['Month'].tolist() == ['2025-01']
        assert trends['Income'].iloc[0] == 2500.00
        assert trends['Expenses'].iloc[0] == 800.00
    
    def test_empty_dataframe(self):
        """Test with empty DataFrame."""
        df = pd.DataFrame(columns=['Date', 'Amount', 'Category'])
        
        trends = get_monthly_trends(df)
        
        assert trends.empty
    
    def test_none_dataframe(self):
        """Test with None input."""
        trends = get_monthly_trends(None)
        
        assert trends.empty
    
    def test_missing_date_column(self):
        """Test with missing Date column."""
        df = pd.DataFrame({
            'Amount': [2500.00, -1000.00],
            'Category': ['Income', 'Bills']
        })
        
        trends = get_monthly_trends(df)
        
        assert trends.empty
    
    def test_invalid_dates(self):
        """Test with invalid date values."""
        df = pd.DataFrame({
            'Date': ['invalid', 'not a date', '2025-02-10'],
            'Amount': [2500.00, -500.00, 2600.00],
            'Category': ['Income', 'Bills', 'Income']
        })
        
        trends = get_monthly_trends(df)
        
        # Should only include the valid date row
        assert len(trends) == 1
        assert trends['Month'].iloc[0] == '2025-02'
    
    def test_mixed_date_formats(self):
        """Test with different date formats (pandas should handle)."""
        df = pd.DataFrame({
            'Date': ['2025-01-15', '01/20/2025', '2025-02-10'],
            'Amount': [2500.00, -1000.00, 2600.00],
            'Category': ['Income', 'Bills', 'Income']
        })
        
        trends = get_monthly_trends(df)
        
        assert len(trends) == 2
        assert '2025-01' in trends['Month'].tolist()
        assert '2025-02' in trends['Month'].tolist()
    
    def test_chronological_sorting(self):
        """Test that months are sorted chronologically."""
        df = pd.DataFrame({
            'Date': ['2025-03-10', '2025-01-10', '2025-02-10'],
            'Amount': [2550.00, 2500.00, 2600.00],
            'Category': ['Income', 'Income', 'Income']
        })
        
        trends = get_monthly_trends(df)
        
        assert trends['Month'].tolist() == ['2025-01', '2025-02', '2025-03']
    
    def test_month_with_only_income(self):
        """Test month with only income transactions."""
        df = pd.DataFrame({
            'Date': ['2025-01-10', '2025-01-15'],
            'Amount': [2500.00, 500.00],
            'Category': ['Income', 'Income']
        })
        
        trends = get_monthly_trends(df)
        
        assert trends['Income'].iloc[0] == 3000.00
        assert trends['Expenses'].iloc[0] == 0.00
        assert trends['Net Savings'].iloc[0] == 3000.00
        assert trends['Savings Rate'].iloc[0] == 100.00
    
    def test_month_with_only_expenses(self):
        """Test month with only expense transactions."""
        df = pd.DataFrame({
            'Date': ['2025-01-10', '2025-01-15'],
            'Amount': [-500.00, -300.00],
            'Category': ['Groceries', 'Transport']
        })
        
        trends = get_monthly_trends(df)
        
        assert trends['Income'].iloc[0] == 0.00
        assert trends['Expenses'].iloc[0] == 800.00
        assert trends['Net Savings'].iloc[0] == -800.00
        assert trends['Savings Rate'].iloc[0] == 0.00  # No income
    
    def test_month_format(self):
        """Test that month format is YYYY-MM."""
        df = pd.DataFrame({
            'Date': ['2025-01-15', '2025-12-20'],
            'Amount': [2500.00, 2600.00],
            'Category': ['Income', 'Income']
        })
        
        trends = get_monthly_trends(df)
        
        assert trends['Month'].tolist() == ['2025-01', '2025-12']
    
    def test_multiple_transactions_same_month(self):
        """Test aggregating multiple transactions within same month."""
        df = pd.DataFrame({
            'Date': ['2025-01-05', '2025-01-10', '2025-01-15', '2025-01-20', '2025-01-25'],
            'Amount': [2500.00, -200.00, -300.00, -100.00, -150.00],
            'Category': ['Income', 'Groceries', 'Transport', 'Eating Out', 'Shopping']
        })
        
        trends = get_monthly_trends(df)
        
        assert len(trends) == 1
        assert trends['Income'].iloc[0] == 2500.00
        assert trends['Expenses'].iloc[0] == 750.00  # 200 + 300 + 100 + 150
        assert trends['Net Savings'].iloc[0] == 1750.00
    
    def test_year_boundary(self):
        """Test monthly aggregation across year boundary."""
        df = pd.DataFrame({
            'Date': ['2024-12-20', '2025-01-10', '2025-02-05'],
            'Amount': [2400.00, 2500.00, 2600.00],
            'Category': ['Income', 'Income', 'Income']
        })
        
        trends = get_monthly_trends(df)
        
        assert len(trends) == 3
        assert trends['Month'].tolist() == ['2024-12', '2025-01', '2025-02']
    
    def test_dataframe_columns(self):
        """Test that output DataFrame has all required columns."""
        df = pd.DataFrame({
            'Date': ['2025-01-10', '2025-02-10'],
            'Amount': [2500.00, 2600.00],
            'Category': ['Income', 'Income']
        })
        
        trends = get_monthly_trends(df)
        
        expected_columns = ['Month', 'Income', 'Expenses', 'Net Savings', 'Savings Rate']
        assert all(col in trends.columns for col in expected_columns)
    
    def test_deficit_month(self):
        """Test month with spending deficit (expenses > income)."""
        df = pd.DataFrame({
            'Date': ['2025-01-10', '2025-01-15'],
            'Amount': [1000.00, -1500.00],
            'Category': ['Income', 'Bills']
        })
        
        trends = get_monthly_trends(df)
        
        assert trends['Net Savings'].iloc[0] == -500.00
        assert trends['Savings Rate'].iloc[0] == -50.00
    
    def test_datetime_objects(self):
        """Test with datetime objects instead of strings."""
        df = pd.DataFrame({
            'Date': [datetime(2025, 1, 15), datetime(2025, 2, 10)],
            'Amount': [2500.00, 2600.00],
            'Category': ['Income', 'Income']
        })
        
        trends = get_monthly_trends(df)
        
        assert len(trends) == 2
        assert trends['Month'].tolist() == ['2025-01', '2025-02']
    
    def test_integration_with_categorized_data(self):
        """Test with realistic categorized transaction data."""
        df = pd.DataFrame({
            'Date': ['2025-01-05', '2025-01-10', '2025-01-15', '2025-02-05', '2025-02-20'],
            'Description': ['Salary', 'Tesco', 'TfL', 'Salary', 'Nando\'s'],
            'Amount': [2500.00, -45.30, -25.00, 2500.00, -32.00],
            'Category': ['Income', 'Groceries', 'Transport', 'Income', 'Eating Out']
        })
        
        trends = get_monthly_trends(df)
        
        assert len(trends) == 2
        assert trends.loc[0, 'Income'] == 2500.00
        assert trends.loc[0, 'Expenses'] == 70.30  # 45.30 + 25.00
        assert trends.loc[1, 'Income'] == 2500.00
        assert trends.loc[1, 'Expenses'] == 32.00


class TestMonthlyTrendsEdgeCases:
    """Test edge cases for monthly trend analysis."""
    
    def test_very_large_date_range(self):
        """Test with data spanning many months."""
        dates = pd.date_range(start='2024-01-01', end='2025-12-31', freq='MS')
        df = pd.DataFrame({
            'Date': dates,
            'Amount': [2500.00] * len(dates),
            'Category': ['Income'] * len(dates)
        })
        
        trends = get_monthly_trends(df)
        
        assert len(trends) == 24  # 2 years = 24 months
    
    def test_sparse_months(self):
        """Test with transactions only in some months."""
        df = pd.DataFrame({
            'Date': ['2025-01-10', '2025-03-10', '2025-06-10'],
            'Amount': [2500.00, 2600.00, 2700.00],
            'Category': ['Income', 'Income', 'Income']
        })
        
        trends = get_monthly_trends(df)
        
        # Should only have the 3 months with data
        assert len(trends) == 3
        assert trends['Month'].tolist() == ['2025-01', '2025-03', '2025-06']
    
    def test_nan_amounts(self):
        """Test handling of NaN amounts."""
        df = pd.DataFrame({
            'Date': ['2025-01-10', '2025-01-15', '2025-02-10'],
            'Amount': [2500.00, np.nan, 2600.00],
            'Category': ['Income', 'Bills', 'Income']
        })
        
        trends = get_monthly_trends(df)
        
        # Should process valid rows
        assert len(trends) >= 1
    
    def test_partial_month_data(self):
        """Test with incomplete month data (only first few days)."""
        df = pd.DataFrame({
            'Date': ['2025-01-01', '2025-01-02', '2025-01-03'],
            'Amount': [2500.00, -100.00, -50.00],
            'Category': ['Income', 'Groceries', 'Transport']
        })
        
        trends = get_monthly_trends(df)
        
        # Should still calculate for the partial month
        assert len(trends) == 1
        assert trends['Month'].iloc[0] == '2025-01'
        assert trends['Expenses'].iloc[0] == 150.00
