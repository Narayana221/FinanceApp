"""
Unit tests for transaction categorization.

Tests cover keyword matching, priority rules, and batch processing.
"""

import pytest
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.categorizer import (
    categorize_transaction,
    categorize_transactions,
    get_category_summary,
    CATEGORY_RULES
)


class TestCategorizeTransaction:
    """Test suite for single transaction categorization."""
    
    def test_existing_category_priority(self):
        """Test that existing category takes priority."""
        result = categorize_transaction("Tesco", "My Custom Category", -45.30)
        assert result == "My Custom Category"
    
    def test_existing_category_empty_string_ignored(self):
        """Test that empty existing category is ignored."""
        result = categorize_transaction("Tesco", "", -45.30)
        assert result == "Groceries"
    
    def test_existing_category_none_ignored(self):
        """Test that None existing category is ignored."""
        result = categorize_transaction("Tesco", None, -45.30)
        assert result == "Groceries"
    
    def test_groceries_tesco(self):
        """Test Tesco categorized as Groceries."""
        result = categorize_transaction("Tesco Superstore", None, -45.30)
        assert result == "Groceries"
    
    def test_groceries_sainsburys(self):
        """Test Sainsbury's categorized as Groceries."""
        result = categorize_transaction("Sainsburys Local", None, -23.45)
        assert result == "Groceries"
    
    def test_groceries_asda(self):
        """Test ASDA categorized as Groceries."""
        result = categorize_transaction("ASDA STORES", None, -67.89)
        assert result == "Groceries"
    
    def test_eating_out_starbucks(self):
        """Test Starbucks categorized as Eating Out."""
        result = categorize_transaction("Starbucks Coffee", None, -4.50)
        assert result == "Eating Out"
    
    def test_eating_out_restaurant(self):
        """Test restaurant categorized as Eating Out."""
        result = categorize_transaction("Italian Restaurant", None, -35.00)
        assert result == "Eating Out"
    
    def test_eating_out_deliveroo(self):
        """Test Deliveroo categorized as Eating Out."""
        result = categorize_transaction("Deliveroo Order", None, -15.99)
        assert result == "Eating Out"
    
    def test_transport_uber(self):
        """Test Uber categorized as Transport."""
        result = categorize_transaction("Uber Trip", None, -12.50)
        assert result == "Transport"
    
    def test_transport_tfl(self):
        """Test TfL categorized as Transport."""
        result = categorize_transaction("TFL TRAVEL CHARGE", None, -25.00)
        assert result == "Transport"
    
    def test_transport_petrol(self):
        """Test petrol categorized as Transport."""
        result = categorize_transaction("Shell Petrol Station", None, -50.00)
        assert result == "Transport"
    
    def test_subscriptions_netflix(self):
        """Test Netflix categorized as Subscriptions."""
        result = categorize_transaction("Netflix Monthly", None, -9.99)
        assert result == "Subscriptions"
    
    def test_subscriptions_spotify(self):
        """Test Spotify categorized as Subscriptions."""
        result = categorize_transaction("Spotify Premium", None, -9.99)
        assert result == "Subscriptions"
    
    def test_subscriptions_gym(self):
        """Test gym categorized as Subscriptions."""
        result = categorize_transaction("PureGym Membership", None, -25.00)
        assert result == "Subscriptions"
    
    def test_shopping_amazon(self):
        """Test Amazon categorized as Shopping."""
        result = categorize_transaction("Amazon Purchase", None, -34.99)
        assert result == "Shopping"
    
    def test_shopping_zara(self):
        """Test Zara categorized as Shopping."""
        result = categorize_transaction("ZARA STORE", None, -65.00)
        assert result == "Shopping"
    
    def test_bills_electric(self):
        """Test electricity categorized as Bills."""
        result = categorize_transaction("British Gas Electric", None, -85.00)
        assert result == "Bills"
    
    def test_bills_rent(self):
        """Test rent categorized as Bills."""
        result = categorize_transaction("Rent Payment", None, -800.00)
        assert result == "Bills"
    
    def test_bills_internet(self):
        """Test internet categorized as Bills."""
        result = categorize_transaction("Virgin Media Broadband", None, -35.00)
        assert result == "Bills"
    
    def test_income_keyword_salary(self):
        """Test salary keyword categorized as Income."""
        result = categorize_transaction("Monthly Salary", None, 2500.00)
        assert result == "Income"
    
    def test_income_keyword_wage(self):
        """Test wage keyword categorized as Income."""
        result = categorize_transaction("Weekly Wage", None, 500.00)
        assert result == "Income"
    
    def test_income_keyword_refund(self):
        """Test refund keyword categorized as Income."""
        result = categorize_transaction("Tax Refund", None, 150.00)
        assert result == "Income"
    
    def test_income_positive_amount(self):
        """Test positive amount without keyword categorized as Income."""
        result = categorize_transaction("Unknown Payment", None, 100.00)
        assert result == "Income"
    
    def test_uncategorized_unknown_merchant(self):
        """Test unknown merchant categorized as Uncategorized."""
        result = categorize_transaction("Random Store XYZ", None, -15.00)
        assert result == "Uncategorized"
    
    def test_case_insensitive_matching(self):
        """Test that keyword matching is case-insensitive."""
        result = categorize_transaction("TESCO SUPERSTORE", None, -45.30)
        assert result == "Groceries"
        
        result = categorize_transaction("starbucks coffee", None, -4.50)
        assert result == "Eating Out"
    
    def test_none_description(self):
        """Test handling of None description."""
        result = categorize_transaction(None, None, -10.00)
        assert result == "Uncategorized"
    
    def test_empty_description(self):
        """Test handling of empty description."""
        result = categorize_transaction("", None, -10.00)
        assert result == "Uncategorized"


class TestCategorizeTransactions:
    """Test suite for batch transaction categorization."""
    
    def test_categorize_multiple_transactions(self):
        """Test categorizing multiple transactions."""
        df = pd.DataFrame({
            'Description': ['Tesco', 'Starbucks', 'Uber', 'Netflix', 'Salary'],
            'Amount': [-45.30, -4.50, -12.50, -9.99, 2500.00]
        })
        
        result = categorize_transactions(df)
        
        assert result['Category'].tolist() == [
            'Groceries', 'Eating Out', 'Transport', 'Subscriptions', 'Income'
        ]
    
    def test_preserve_existing_categories(self):
        """Test that existing categories are preserved."""
        df = pd.DataFrame({
            'Description': ['Tesco', 'Unknown Store'],
            'Amount': [-45.30, -15.00],
            'Category': [None, 'Work Expenses']
        })
        
        result = categorize_transactions(df)
        
        assert result.loc[0, 'Category'] == 'Groceries'
        assert result.loc[1, 'Category'] == 'Work Expenses'
    
    def test_add_category_column_if_missing(self):
        """Test that Category column is added if it doesn't exist."""
        df = pd.DataFrame({
            'Description': ['Tesco'],
            'Amount': [-45.30]
        })
        
        result = categorize_transactions(df)
        
        assert 'Category' in result.columns
        assert result['Category'][0] == 'Groceries'
    
    def test_empty_dataframe(self):
        """Test handling of empty DataFrame."""
        df = pd.DataFrame(columns=['Description', 'Amount'])
        result = categorize_transactions(df)
        
        assert result.empty
    
    def test_none_dataframe(self):
        """Test handling of None DataFrame."""
        result = categorize_transactions(None)
        assert result is None
    
    def test_missing_description_column_raises_error(self):
        """Test that missing Description column raises ValueError."""
        df = pd.DataFrame({'Amount': [-45.30]})
        
        with pytest.raises(ValueError, match="Description"):
            categorize_transactions(df)
    
    def test_missing_amount_column_raises_error(self):
        """Test that missing Amount column raises ValueError."""
        df = pd.DataFrame({'Description': ['Tesco']})
        
        with pytest.raises(ValueError, match="Amount"):
            categorize_transactions(df)
    
    def test_does_not_modify_original_dataframe(self):
        """Test that original DataFrame is not modified."""
        df = pd.DataFrame({
            'Description': ['Tesco'],
            'Amount': [-45.30]
        })
        
        original_columns = list(df.columns)
        categorize_transactions(df)
        
        assert list(df.columns) == original_columns


class TestGetCategorySummary:
    """Test suite for category spending summary."""
    
    def test_category_summary_basic(self):
        """Test basic category summary calculation."""
        df = pd.DataFrame({
            'Amount': [-45.30, -23.45, -12.50],
            'Category': ['Groceries', 'Groceries', 'Transport']
        })
        
        summary = get_category_summary(df)
        
        assert summary['Groceries'] == pytest.approx(68.75, 0.01)
        assert summary['Transport'] == pytest.approx(12.50, 0.01)
    
    def test_category_summary_excludes_income(self):
        """Test that income is excluded from summary."""
        df = pd.DataFrame({
            'Amount': [-45.30, 2500.00, -12.50],
            'Category': ['Groceries', 'Income', 'Transport']
        })
        
        summary = get_category_summary(df)
        
        assert 'Income' not in summary
        assert 'Groceries' in summary
        assert 'Transport' in summary
    
    def test_category_summary_sorted_by_amount(self):
        """Test that summary is sorted by amount (highest first)."""
        df = pd.DataFrame({
            'Amount': [-10.00, -50.00, -25.00],
            'Category': ['Transport', 'Groceries', 'Eating Out']
        })
        
        summary = get_category_summary(df)
        keys = list(summary.keys())
        
        assert keys[0] == 'Groceries'  # Highest
        assert keys[1] == 'Eating Out'
        assert keys[2] == 'Transport'  # Lowest
    
    def test_category_summary_empty_dataframe(self):
        """Test category summary with empty DataFrame."""
        df = pd.DataFrame(columns=['Amount', 'Category'])
        summary = get_category_summary(df)
        
        assert summary == {}
    
    def test_category_summary_none_dataframe(self):
        """Test category summary with None DataFrame."""
        summary = get_category_summary(None)
        assert summary == {}
    
    def test_category_summary_missing_columns(self):
        """Test category summary with missing columns."""
        df = pd.DataFrame({'Amount': [-45.30]})
        summary = get_category_summary(df)
        
        assert summary == {}
    
    def test_category_summary_only_income(self):
        """Test category summary with only income transactions."""
        df = pd.DataFrame({
            'Amount': [2500.00, 500.00],
            'Category': ['Income', 'Income']
        })
        
        summary = get_category_summary(df)
        assert summary == {}


class TestCategoryRulesConfiguration:
    """Test suite for category rules configuration."""
    
    def test_category_rules_exist(self):
        """Test that category rules are defined."""
        assert CATEGORY_RULES is not None
        assert len(CATEGORY_RULES) > 0
    
    def test_required_categories_present(self):
        """Test that all required categories are present."""
        required = ['Groceries', 'Eating Out', 'Transport', 'Subscriptions', 'Shopping', 'Bills']
        
        for category in required:
            assert category in CATEGORY_RULES
    
    def test_all_categories_have_keywords(self):
        """Test that all categories have at least one keyword."""
        for category, keywords in CATEGORY_RULES.items():
            assert len(keywords) > 0, f"{category} has no keywords"
    
    def test_keywords_are_lowercase_for_matching(self):
        """Test that keyword matching works with any case."""
        # Test with uppercase description
        result = categorize_transaction("TESCO", None, -45.30)
        assert result == "Groceries"
        
        # Test with lowercase description
        result = categorize_transaction("tesco", None, -45.30)
        assert result == "Groceries"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
