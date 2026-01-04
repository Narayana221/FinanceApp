"""
Financial data visualization components.

This module provides Streamlit chart components for displaying
financial insights and analytics.
"""

import streamlit as st
import pandas as pd
from typing import Dict, List


def render_financial_summary_metrics(summary: Dict[str, float]) -> None:
    """
    Display financial summary metrics in card format using st.metric.
    
    Shows four key financial indicators:
    - Total Income (green)
    - Total Expenses (red/inverse)
    - Net Savings (green if positive, red if negative)
    - Savings Rate (green if positive, red if negative)
    
    Args:
        summary: Financial summary dict from get_financial_summary()
                 Must contain: total_income, total_expenses, net_savings, savings_rate
                 
    Examples:
        >>> summary = {
        ...     'total_income': 2500.00,
        ...     'total_expenses': 1500.00,
        ...     'net_savings': 1000.00,
        ...     'savings_rate': 40.00
        ... }
        >>> render_financial_summary_metrics(summary)
        # Displays 4 metric cards in Streamlit
    """
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="💰 Total Income",
            value=f"£{summary['total_income']:,.2f}",
            delta=None
        )
    
    with col2:
        st.metric(
            label="💸 Total Expenses",
            value=f"£{summary['total_expenses']:,.2f}",
            delta=None
        )
    
    with col3:
        savings_value = summary['net_savings']
        savings_label = "💵 Net Savings" if savings_value >= 0 else "⚠️ Deficit"
        st.metric(
            label=savings_label,
            value=f"£{savings_value:,.2f}",
            delta=None
        )
    
    with col4:
        rate_value = summary['savings_rate']
        rate_label = "📈 Savings Rate"
        st.metric(
            label=rate_label,
            value=f"{rate_value:.1f}%",
            delta=None
        )


def render_spending_by_category_chart(category_summary: Dict[str, float]) -> None:
    """
    Display spending breakdown by category as a horizontal bar chart.
    
    Categories are already sorted by amount (descending) from
    get_category_summary(). Shows only expense categories (no Income).
    
    Args:
        category_summary: Category spending dict from get_category_summary()
                         Maps category names to total amounts
                         
    Examples:
        >>> category_summary = {
        ...     'Groceries': 45.30,
        ...     'Transport': 12.50,
        ...     'Eating Out': 25.00
        ... }
        >>> render_spending_by_category_chart(category_summary)
        # Displays bar chart in Streamlit
    """
    if not category_summary:
        st.info("No expense data available to display.")
        return
    
    st.subheader("💳 Spending by Category")
    
    # Convert to DataFrame for Streamlit charting
    df = pd.DataFrame(
        list(category_summary.items()),
        columns=['Category', 'Amount (£)']
    )
    
    # Display as bar chart (already sorted from get_category_summary)
    st.bar_chart(df.set_index('Category'))
    
    # Also show as table for exact values
    with st.expander("View detailed breakdown"):
        df['Amount (£)'] = df['Amount (£)'].apply(lambda x: f"£{x:,.2f}")
        st.dataframe(df, use_container_width=True, hide_index=True)


def render_income_vs_expenses_chart(summary: Dict[str, float]) -> None:
    """
    Display income vs expenses comparison as a bar chart.
    
    Provides quick visual comparison of total income against
    total expenses to understand cash flow.
    
    Args:
        summary: Financial summary dict from get_financial_summary()
                 Must contain: total_income, total_expenses
                 
    Examples:
        >>> summary = {
        ...     'total_income': 2500.00,
        ...     'total_expenses': 1500.00,
        ...     'net_savings': 1000.00,
        ...     'savings_rate': 40.00
        ... }
        >>> render_income_vs_expenses_chart(summary)
        # Displays comparison bar chart in Streamlit
    """
    st.subheader("📊 Income vs Expenses")
    
    # Create comparison DataFrame
    df = pd.DataFrame({
        'Amount (£)': [summary['total_income'], summary['total_expenses']]
    }, index=['Income', 'Expenses'])
    
    st.bar_chart(df)
    
    # Show exact values
    income_text = f"Income: **£{summary['total_income']:,.2f}**"
    expenses_text = f"Expenses: **£{summary['total_expenses']:,.2f}**"
    difference = summary['total_income'] - summary['total_expenses']
    
    if difference >= 0:
        diff_text = f"✅ Surplus: **£{difference:,.2f}**"
    else:
        diff_text = f"⚠️ Deficit: **£{abs(difference):,.2f}**"
    
    st.markdown(f"{income_text} | {expenses_text} | {diff_text}")


def render_extreme_values_table(extreme_values: List[Dict]) -> None:
    """
    Display flagged extreme value transactions in a warning table.
    
    Shows transactions that exceed the threshold (default £1000)
    for user review. Helps identify unusual spending or income.
    
    Args:
        extreme_values: List of flagged transaction dicts from flag_extreme_values()
                       Each dict contains: date, description, amount, category, flag_reason
                       
    Examples:
        >>> extreme_values = [
        ...     {
        ...         'date': '2024-01-15',
        ...         'description': 'Salary',
        ...         'amount': 2500.00,
        ...         'category': 'Income',
        ...         'flag_reason': 'Extreme value: £2500.00 exceeds threshold'
        ...     }
        ... ]
        >>> render_extreme_values_table(extreme_values)
        # Displays warning with transaction table
    """
    if not extreme_values:
        return
    
    st.warning(f"⚠️ **{len(extreme_values)} large transaction(s) flagged for review**")
    
    # Convert to DataFrame
    df = pd.DataFrame(extreme_values)
    
    # Format amount column with currency and ensure positive display
    if 'amount' in df.columns:
        df['Amount'] = df['amount'].apply(lambda x: f"£{abs(x):,.2f}")
        df['Type'] = df['amount'].apply(lambda x: 'Income' if x > 0 else 'Expense')
    
    # Rename columns for display
    display_df = df.rename(columns={
        'date': 'Date',
        'description': 'Description',
        'category': 'Category',
        'flag_reason': 'Reason'
    })
    
    # Select and order columns
    columns_to_show = ['Date', 'Description', 'Amount', 'Type', 'Category', 'Reason']
    display_df = display_df[[col for col in columns_to_show if col in display_df.columns]]
    
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )


def render_monthly_trends_chart(trends_df: pd.DataFrame) -> None:
    """
    Display monthly financial trends as line charts.
    
    Shows three separate trend visualizations:
    1. Income and Expenses over time (line chart)
    2. Net Savings over time (line chart)
    3. Savings Rate over time (line chart)
    
    Requires at least 2 months of data to show meaningful trends.
    
    Args:
        trends_df: Monthly trends DataFrame from get_monthly_trends()
                  Must contain columns: Month, Income, Expenses, Net Savings, Savings Rate
                  
    Examples:
        >>> trends_df = pd.DataFrame({
        ...     'Month': ['2025-01', '2025-02', '2025-03'],
        ...     'Income': [2500.00, 2600.00, 2550.00],
        ...     'Expenses': [1500.00, 1400.00, 1450.00],
        ...     'Net Savings': [1000.00, 1200.00, 1100.00],
        ...     'Savings Rate': [40.00, 46.15, 43.14]
        ... })
        >>> render_monthly_trends_chart(trends_df)
        # Displays 3 line charts in Streamlit
    """
    if trends_df is None or trends_df.empty:
        st.info("📅 Need data from multiple months to show trends.")
        return
    
    if len(trends_df) < 2:
        st.info("📅 Need at least 2 months of data to show meaningful trends.")
        return
    
    st.subheader("📈 Monthly Trends")
    
    # Chart 1: Income vs Expenses Trend
    st.markdown("**Income & Expenses Over Time**")
    income_expense_df = trends_df.set_index('Month')[['Income', 'Expenses']]
    st.line_chart(income_expense_df)
    
    st.markdown("")  # Spacing
    
    # Chart 2: Net Savings Trend
    st.markdown("**Net Savings Over Time**")
    savings_df = trends_df.set_index('Month')[['Net Savings']]
    st.line_chart(savings_df)
    
    st.markdown("")  # Spacing
    
    # Chart 3: Savings Rate Trend
    st.markdown("**Savings Rate Over Time (%)**")
    rate_df = trends_df.set_index('Month')[['Savings Rate']]
    st.line_chart(rate_df)
    
    # Show detailed monthly breakdown table
    with st.expander("📊 View monthly breakdown"):
        display_df = trends_df.copy()
        display_df['Income'] = display_df['Income'].apply(lambda x: f"£{x:,.2f}")
        display_df['Expenses'] = display_df['Expenses'].apply(lambda x: f"£{x:,.2f}")
        display_df['Net Savings'] = display_df['Net Savings'].apply(lambda x: f"£{x:,.2f}")
        display_df['Savings Rate'] = display_df['Savings Rate'].apply(lambda x: f"{x:.1f}%")
        st.dataframe(display_df, use_container_width=True, hide_index=True)

