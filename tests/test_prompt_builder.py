"""
Tests for Prompt Builder Module

This test suite verifies the prompt engineering functionality for the AI Financial Coach.
Tests cover JSON summary preparation, prompt construction, and edge case handling.
"""

import pytest
from utils.prompt_builder import (
    prepare_financial_summary,
    build_coaching_prompt,
    _format_category_breakdown
)


class TestPrepareFinancialSummary:
    """Test JSON summary preparation functionality."""
    
    def test_basic_summary_without_goal(self):
        """Test creating summary with standard financial data, no savings goal."""
        financial = {
            'total_income': 2500.00,
            'total_expenses': 1800.00,
            'net_savings': 700.00,
            'savings_rate': 28.00
        }
        categories = {
            'Groceries': 450.00,
            'Bills': 400.00,
            'Transport': 120.00
        }
        
        summary = prepare_financial_summary(financial, categories)
        
        assert summary['income'] == 2500.00
        assert summary['expenses'] == 1800.00
        assert summary['net_savings'] == 700.00
        assert summary['savings_rate'] == 28.0
        assert 'savings_goal' not in summary
        assert 'goal_gap' not in summary
        assert len(summary['top_categories']) == 3
        assert summary['total_categories'] == 3
    
    def test_summary_with_savings_goal(self):
        """Test creating summary with savings goal included."""
        financial = {
            'total_income': 2500.00,
            'total_expenses': 1800.00,
            'net_savings': 700.00,
            'savings_rate': 28.00
        }
        categories = {'Groceries': 450.00}
        
        summary = prepare_financial_summary(financial, categories, savings_goal=1000.00)
        
        assert summary['savings_goal'] == 1000.00
        assert summary['goal_gap'] == 300.00  # 1000 - 700
    
    def test_goal_gap_when_ahead(self):
        """Test goal gap calculation when savings exceed goal."""
        financial = {
            'total_income': 3000.00,
            'total_expenses': 1500.00,
            'net_savings': 1500.00,
            'savings_rate': 50.00
        }
        categories = {'Bills': 500.00}
        
        summary = prepare_financial_summary(financial, categories, savings_goal=1000.00)
        
        assert summary['goal_gap'] == -500.00  # 1000 - 1500 (negative = ahead)
    
    def test_top_categories_sorted_by_amount(self):
        """Test that categories are sorted by amount (highest first)."""
        financial = {
            'total_income': 2000.00,
            'total_expenses': 1000.00,
            'net_savings': 1000.00,
            'savings_rate': 50.00
        }
        categories = {
            'Transport': 100.00,
            'Groceries': 400.00,
            'Bills': 300.00,
            'Shopping': 150.00,
            'Eating Out': 50.00
        }
        
        summary = prepare_financial_summary(financial, categories)
        
        top_cats = summary['top_categories']
        assert top_cats[0]['category'] == 'Groceries'
        assert top_cats[1]['category'] == 'Bills'
        assert top_cats[2]['category'] == 'Shopping'
        assert top_cats[3]['category'] == 'Transport'
        assert top_cats[4]['category'] == 'Eating Out'
    
    def test_top_categories_limited_to_five(self):
        """Test that only top 5 categories are included."""
        financial = {
            'total_income': 3000.00,
            'total_expenses': 2000.00,
            'net_savings': 1000.00,
            'savings_rate': 33.33
        }
        categories = {
            'Cat1': 500.00,
            'Cat2': 400.00,
            'Cat3': 300.00,
            'Cat4': 200.00,
            'Cat5': 150.00,
            'Cat6': 100.00,
            'Cat7': 50.00,
            'Cat8': 300.00
        }
        
        summary = prepare_financial_summary(financial, categories)
        
        assert len(summary['top_categories']) == 5
        assert summary['total_categories'] == 8
        # Check top 5 are correct
        assert summary['top_categories'][0]['category'] == 'Cat1'
        assert summary['top_categories'][1]['category'] == 'Cat2'
    
    def test_category_percentages_calculated_correctly(self):
        """Test that category percentages relative to total expenses are correct."""
        financial = {
            'total_income': 2000.00,
            'total_expenses': 1000.00,
            'net_savings': 1000.00,
            'savings_rate': 50.00
        }
        categories = {
            'Groceries': 250.00,  # 25%
            'Bills': 400.00,      # 40%
            'Transport': 100.00    # 10%
        }
        
        summary = prepare_financial_summary(financial, categories)
        
        groceries = next(c for c in summary['top_categories'] if c['category'] == 'Groceries')
        bills = next(c for c in summary['top_categories'] if c['category'] == 'Bills')
        transport = next(c for c in summary['top_categories'] if c['category'] == 'Transport')
        
        assert groceries['percentage'] == 25.0
        assert bills['percentage'] == 40.0
        assert transport['percentage'] == 10.0
    
    def test_empty_category_summary(self):
        """Test handling of empty category data."""
        financial = {
            'total_income': 2000.00,
            'total_expenses': 0.00,
            'net_savings': 2000.00,
            'savings_rate': 100.00
        }
        categories = {}
        
        summary = prepare_financial_summary(financial, categories)
        
        assert summary['top_categories'] == []
        assert summary['total_categories'] == 0
    
    def test_zero_expenses_percentage_handling(self):
        """Test that percentage calculation handles zero expenses gracefully."""
        financial = {
            'total_income': 1000.00,
            'total_expenses': 0.00,
            'net_savings': 1000.00,
            'savings_rate': 100.00
        }
        categories = {'Misc': 50.00}  # This shouldn't happen but test edge case
        
        summary = prepare_financial_summary(financial, categories)
        
        assert summary['top_categories'][0]['percentage'] == 0.0
    
    def test_negative_savings(self):
        """Test handling of deficit (negative savings)."""
        financial = {
            'total_income': 1000.00,
            'total_expenses': 1200.00,
            'net_savings': -200.00,
            'savings_rate': -20.00
        }
        categories = {'Bills': 600.00, 'Shopping': 600.00}
        
        summary = prepare_financial_summary(financial, categories)
        
        assert summary['net_savings'] == -200.00
        assert summary['savings_rate'] == -20.0


class TestBuildCoachingPrompt:
    """Test prompt construction functionality."""
    
    def test_basic_prompt_structure(self):
        """Test that prompt contains all required sections."""
        financial = {
            'total_income': 2500.00,
            'total_expenses': 1800.00,
            'net_savings': 700.00,
            'savings_rate': 28.00
        }
        categories = {'Groceries': 450.00, 'Bills': 400.00}
        
        prompt = build_coaching_prompt(financial, categories)
        
        # Check all major sections exist
        assert "USER PROFILE:" in prompt
        assert "SPENDING BREAKDOWN:" in prompt
        assert "YOUR TASK:" in prompt
        assert "RECOMMENDATIONS" in prompt
        assert "MONEY HABIT" in prompt
        assert "SPENDING LEAKS" in prompt
    
    def test_prompt_includes_financial_metrics(self):
        """Test that prompt includes all financial metrics correctly formatted."""
        financial = {
            'total_income': 2500.00,
            'total_expenses': 1800.00,
            'net_savings': 700.00,
            'savings_rate': 28.00
        }
        categories = {}
        
        prompt = build_coaching_prompt(financial, categories)
        
        assert "Monthly Income: £2,500.00" in prompt
        assert "Monthly Expenses: £1,800.00" in prompt
        assert "Net Savings: £700.00" in prompt
        assert "Current Savings Rate: 28.0%" in prompt
    
    def test_prompt_with_savings_goal_short(self):
        """Test prompt includes savings goal when user is short of target."""
        financial = {
            'total_income': 2500.00,
            'total_expenses': 1800.00,
            'net_savings': 700.00,
            'savings_rate': 28.00
        }
        categories = {'Groceries': 450.00}
        
        prompt = build_coaching_prompt(financial, categories, savings_goal=1000.00)
        
        assert "Savings Goal: £1,000.00/month" in prompt
        assert "£300.00 short" in prompt
        assert "30% short" in prompt
    
    def test_prompt_with_savings_goal_ahead(self):
        """Test prompt includes goal when user exceeds target."""
        financial = {
            'total_income': 3000.00,
            'total_expenses': 1500.00,
            'net_savings': 1500.00,
            'savings_rate': 50.00
        }
        categories = {'Bills': 500.00}
        
        prompt = build_coaching_prompt(financial, categories, savings_goal=1000.00)
        
        assert "Savings Goal: £1,000.00/month" in prompt
        assert "£500.00 ahead" in prompt
        assert "50% ahead" in prompt
    
    def test_prompt_with_savings_goal_on_target(self):
        """Test prompt when user exactly meets savings goal."""
        financial = {
            'total_income': 2500.00,
            'total_expenses': 1500.00,
            'net_savings': 1000.00,
            'savings_rate': 40.00
        }
        categories = {'Bills': 500.00}
        
        prompt = build_coaching_prompt(financial, categories, savings_goal=1000.00)
        
        assert "Savings Goal: £1,000.00/month" in prompt
        assert "On target" in prompt
    
    def test_prompt_without_savings_goal(self):
        """Test prompt suggests setting goal when none provided."""
        financial = {
            'total_income': 2000.00,
            'total_expenses': 1500.00,
            'net_savings': 500.00,
            'savings_rate': 25.00
        }
        categories = {'Groceries': 400.00}
        
        prompt = build_coaching_prompt(financial, categories)
        
        assert "No specific savings goal set" in prompt
        assert "Consider setting a monthly savings target" in prompt
    
    def test_prompt_includes_category_breakdown(self):
        """Test that prompt includes formatted category breakdown."""
        financial = {
            'total_income': 2000.00,
            'total_expenses': 1000.00,
            'net_savings': 1000.00,
            'savings_rate': 50.00
        }
        categories = {
            'Groceries': 400.00,
            'Bills': 300.00,
            'Transport': 100.00
        }
        
        prompt = build_coaching_prompt(financial, categories)
        
        assert "Top Spending Categories:" in prompt
        assert "Groceries: £400.00" in prompt
        assert "Bills: £300.00" in prompt
        assert "Transport: £100.00" in prompt
        assert "Total categories tracked: 3" in prompt
    
    def test_prompt_with_empty_categories(self):
        """Test prompt handles empty category data gracefully."""
        financial = {
            'total_income': 2000.00,
            'total_expenses': 0.00,
            'net_savings': 2000.00,
            'savings_rate': 100.00
        }
        categories = {}
        
        prompt = build_coaching_prompt(financial, categories)
        
        assert "No category data available" in prompt
    
    def test_prompt_requests_specific_outputs(self):
        """Test that prompt clearly requests all required AI outputs."""
        financial = {
            'total_income': 2000.00,
            'total_expenses': 1500.00,
            'net_savings': 500.00,
            'savings_rate': 25.00
        }
        categories = {'Bills': 500.00}
        
        prompt = build_coaching_prompt(financial, categories)
        
        # Check specific instructions are present
        assert "3-5 specific, actionable items" in prompt
        assert "concrete savings amount" in prompt
        assert "one easy-to-adopt daily or weekly habit" in prompt
        assert "1-2 categories where the user is overspending most" in prompt
        assert "typical budgeting guidelines" in prompt


class TestFormatCategoryBreakdown:
    """Test category formatting helper function."""
    
    def test_format_multiple_categories(self):
        """Test formatting of multiple categories."""
        categories = {
            'Groceries': 450.00,
            'Bills': 400.00,
            'Transport': 120.00
        }
        total_expenses = 1000.00
        
        breakdown = _format_category_breakdown(categories, total_expenses)
        
        assert "Top Spending Categories:" in breakdown
        assert "1. Groceries: £450.00 (45.0% of expenses)" in breakdown
        assert "2. Bills: £400.00 (40.0% of expenses)" in breakdown
        assert "3. Transport: £120.00 (12.0% of expenses)" in breakdown
        assert "Total categories tracked: 3" in breakdown
    
    def test_format_sorts_by_amount(self):
        """Test that categories are sorted by amount descending."""
        categories = {
            'Small': 50.00,
            'Large': 500.00,
            'Medium': 200.00
        }
        total_expenses = 750.00
        
        breakdown = _format_category_breakdown(categories, total_expenses)
        
        lines = breakdown.split('\n')
        assert "Large" in lines[1]  # First category after header
        assert "Medium" in lines[2]
        assert "Small" in lines[3]
    
    def test_format_limits_to_top_five(self):
        """Test that only top 5 categories are shown."""
        categories = {
            f'Category{i}': 100.00 - (i * 10) for i in range(10)
        }
        total_expenses = sum(categories.values())
        
        breakdown = _format_category_breakdown(categories, total_expenses)
        
        lines = breakdown.split('\n')
        # Header + 5 categories + blank + total = 8 lines
        category_lines = [l for l in lines if l.startswith(('1.', '2.', '3.', '4.', '5.'))]
        assert len(category_lines) == 5
    
    def test_format_empty_categories(self):
        """Test handling of empty category dict."""
        categories = {}
        total_expenses = 0.00
        
        breakdown = _format_category_breakdown(categories, total_expenses)
        
        assert breakdown == "No category data available."
    
    def test_format_single_category(self):
        """Test formatting with only one category."""
        categories = {'Bills': 500.00}
        total_expenses = 500.00
        
        breakdown = _format_category_breakdown(categories, total_expenses)
        
        assert "1. Bills: £500.00 (100.0% of expenses)" in breakdown
        assert "Total categories tracked: 1" in breakdown
    
    def test_format_with_zero_expenses(self):
        """Test percentage calculation with zero total expenses."""
        categories = {'Misc': 100.00}
        total_expenses = 0.00
        
        breakdown = _format_category_breakdown(categories, total_expenses)
        
        assert "0.0% of expenses" in breakdown


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_zero_income(self):
        """Test handling of zero income."""
        financial = {
            'total_income': 0.00,
            'total_expenses': 500.00,
            'net_savings': -500.00,
            'savings_rate': -100.00
        }
        categories = {'Bills': 500.00}
        
        summary = prepare_financial_summary(financial, categories)
        prompt = build_coaching_prompt(financial, categories)
        
        assert summary['income'] == 0.00
        assert "Monthly Income: £0.00" in prompt
    
    def test_very_high_savings_rate(self):
        """Test handling of very high savings rate (>50%)."""
        financial = {
            'total_income': 3000.00,
            'total_expenses': 900.00,
            'net_savings': 2100.00,
            'savings_rate': 70.00
        }
        categories = {'Groceries': 300.00}
        
        summary = prepare_financial_summary(financial, categories)
        
        assert summary['savings_rate'] == 70.0
    
    def test_missing_financial_keys(self):
        """Test handling of missing financial summary keys."""
        financial = {}  # Missing all keys
        categories = {'Bills': 100.00}
        
        summary = prepare_financial_summary(financial, categories)
        
        assert summary['income'] == 0.00
        assert summary['expenses'] == 0.00
        assert summary['net_savings'] == 0.00
        assert summary['savings_rate'] == 0.0
    
    def test_rounding_precision(self):
        """Test that monetary values are rounded to 2 decimal places."""
        financial = {
            'total_income': 2500.556,
            'total_expenses': 1800.996,
            'net_savings': 699.556,
            'savings_rate': 27.982
        }
        categories = {'Groceries': 450.126}
        
        summary = prepare_financial_summary(financial, categories, savings_goal=1000.786)
        
        assert summary['income'] == 2500.56
        assert summary['expenses'] == 1801.00
        assert summary['net_savings'] == 699.56
        assert summary['savings_rate'] == 28.0
        assert summary['savings_goal'] == 1000.79
        assert summary['top_categories'][0]['amount'] == 450.13
