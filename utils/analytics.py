"""
Financial analytics utilities.

This module provides calculations for income, expenses, savings,
and other financial metrics based on categorized transaction data.
"""

from typing import Dict, List
import pandas as pd


def calculate_income_expenses(df: pd.DataFrame) -> Dict[str, float]:
    """
    Calculate total income and total expenses from categorized transactions.
    
    Income is identified by the 'Income' category (from categorizer.py).
    Expenses are all non-Income categories with negative amounts.
    
    Args:
        df: Categorized DataFrame with Amount and Category columns
        
    Returns:
        dict: {'income': float, 'expenses': float}
        Both values are positive numbers rounded to 2 decimal places.
        
    Examples:
        >>> df = pd.DataFrame({
        ...     'Amount': [2500.00, -45.30, -100.00],
        ...     'Category': ['Income', 'Groceries', 'Transport']
        ... })
        >>> result = calculate_income_expenses(df)
        >>> result['income']
        2500.0
        >>> result['expenses']
        145.3
    """
    if df is None or df.empty:
        return {'income': 0.0, 'expenses': 0.0}
    
    # Validate required columns exist
    if 'Amount' not in df.columns or 'Category' not in df.columns:
        return {'income': 0.0, 'expenses': 0.0}
    
    # Income: transactions categorized as 'Income'
    income_df = df[df['Category'] == 'Income']
    total_income = income_df['Amount'].sum() if not income_df.empty else 0.0
    total_income = abs(total_income)  # Ensure positive
    
    # Expenses: negative amounts from non-Income categories
    expense_df = df[df['Category'] != 'Income']
    total_expenses = expense_df[expense_df['Amount'] < 0]['Amount'].sum()
    total_expenses = abs(total_expenses)  # Convert to positive value
    
    return {
        'income': round(total_income, 2),
        'expenses': round(total_expenses, 2)
    }


def calculate_net_savings(income: float, expenses: float) -> float:
    """
    Calculate net savings using formula: Income - Expenses.
    
    Args:
        income: Total income (positive value)
        expenses: Total expenses (positive value)
        
    Returns:
        float: Net savings rounded to 2 decimal places
        Positive value indicates savings, negative indicates deficit
        
    Examples:
        >>> calculate_net_savings(2500.00, 1500.00)
        1000.0
        >>> calculate_net_savings(1000.00, 1200.00)
        -200.0
    """
    net_savings = income - expenses
    return round(net_savings, 2)


def calculate_savings_rate(income: float, net_savings: float) -> float:
    """
    Calculate savings rate as percentage of income.
    
    Formula: (Net Savings / Income) * 100
    
    Args:
        income: Total income
        net_savings: Net savings amount (can be negative)
        
    Returns:
        float: Savings rate as percentage (0-100+) rounded to 2 decimal places
        Returns 0.0 if income is zero to avoid division by zero
        
    Examples:
        >>> calculate_savings_rate(2500.00, 1000.00)
        40.0
        >>> calculate_savings_rate(2000.00, -200.00)
        -10.0
        >>> calculate_savings_rate(0.00, 0.00)
        0.0
    """
    if income == 0:
        return 0.0
    
    rate = (net_savings / income) * 100
    return round(rate, 2)


def get_financial_summary(df: pd.DataFrame) -> Dict[str, float]:
    """
    Calculate complete financial summary with all key metrics.
    
    This is the primary function for getting all financial analytics
    from a categorized transaction DataFrame.
    
    Args:
        df: Categorized DataFrame with Amount and Category columns
        
    Returns:
        dict: Complete financial metrics including:
            - total_income: Sum of all income transactions
            - total_expenses: Sum of all expense transactions
            - net_savings: Income minus expenses
            - savings_rate: Percentage of income saved
            
    Examples:
        >>> df = pd.DataFrame({
        ...     'Amount': [2500.00, -1200.00, -300.00],
        ...     'Category': ['Income', 'Bills', 'Groceries']
        ... })
        >>> summary = get_financial_summary(df)
        >>> summary['total_income']
        2500.0
        >>> summary['total_expenses']
        1500.0
        >>> summary['net_savings']
        1000.0
        >>> summary['savings_rate']
        40.0
    """
    ie = calculate_income_expenses(df)
    income = ie['income']
    expenses = ie['expenses']
    net_savings = calculate_net_savings(income, expenses)
    savings_rate = calculate_savings_rate(income, net_savings)
    
    return {
        'total_income': income,
        'total_expenses': expenses,
        'net_savings': net_savings,
        'savings_rate': savings_rate
    }


def flag_extreme_values(df: pd.DataFrame, threshold: float = 1000.0) -> List[Dict]:
    """
    Flag transactions with extreme values (> threshold) for user review.
    
    Large transactions may require special attention or verification.
    This function identifies both large income and large expenses.
    
    Args:
        df: Transaction DataFrame with Date, Description, Amount, Category
        threshold: Amount threshold in currency units (default £1000)
        
    Returns:
        list: List of flagged transaction dictionaries, each containing:
            - date: Transaction date
            - description: Transaction description
            - amount: Transaction amount
            - category: Transaction category
            - flag_reason: Explanation of why transaction was flagged
            
    Examples:
        >>> df = pd.DataFrame({
        ...     'Date': ['2024-01-15', '2024-01-16'],
        ...     'Description': ['Salary', 'Laptop'],
        ...     'Amount': [2500.00, -1200.00],
        ...     'Category': ['Income', 'Shopping']
        ... })
        >>> flagged = flag_extreme_values(df, threshold=1000.0)
        >>> len(flagged)
        2
        >>> flagged[0]['flag_reason']
        'Extreme value: £2500.00 exceeds threshold'
    """
    if df is None or df.empty:
        return []
    
    # Flag transactions where absolute amount > threshold
    extreme = df[abs(df['Amount']) > threshold].copy()
    
    if extreme.empty:
        return []
    
    # Convert to list of dictionaries for easy consumption
    flagged = []
    for _, row in extreme.iterrows():
        amount = row.get('Amount', 0.0)
        flagged.append({
            'date': row.get('Date'),
            'description': row.get('Description'),
            'amount': amount,
            'category': row.get('Category'),
            'flag_reason': f'Extreme value: £{abs(amount):.2f} exceeds threshold'
        })
    
    return flagged


def get_monthly_trends(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate financial metrics by month for trend analysis.
    
    Groups categorized transactions by month (YYYY-MM format) and calculates
    income, expenses, net savings, and savings rate for each month.
    Useful for tracking financial progress over time.
    
    Args:
        df: Categorized DataFrame with Date, Amount, Category columns
        
    Returns:
        pd.DataFrame: Monthly metrics with columns:
            - Month (str): YYYY-MM format
            - Income (float): Total monthly income
            - Expenses (float): Total monthly expenses (positive values)
            - Net Savings (float): Income - Expenses
            - Savings Rate (float): (Net Savings / Income) * 100
        Empty DataFrame if insufficient data or errors
            
    Examples:
        >>> df = pd.DataFrame({
        ...     'Date': ['2025-01-15', '2025-01-20', '2025-02-10'],
        ...     'Amount': [2500.00, -1000.00, 2500.00],
        ...     'Category': ['Income', 'Bills', 'Income']
        ... })
        >>> trends = get_monthly_trends(df)
        >>> trends['Month'].tolist()
        ['2025-01', '2025-02']
        >>> trends['Income'].tolist()
        [2500.0, 2500.0]
    """
    if df is None or df.empty:
        return pd.DataFrame()
    
    # Ensure Date column exists
    if 'Date' not in df.columns:
        return pd.DataFrame()
    
    # Create copy and ensure Date is datetime
    result = df.copy()
    result['Date'] = pd.to_datetime(result['Date'], errors='coerce')
    
    # Remove rows with invalid dates
    result = result.dropna(subset=['Date'])
    
    if result.empty:
        return pd.DataFrame()
    
    # Extract year-month (YYYY-MM format)
    result['Month'] = result['Date'].dt.to_period('M').astype(str)
    
    # Group by month and calculate metrics
    monthly_data = []
    for month, group in result.groupby('Month'):
        # Use existing get_financial_summary for consistency
        summary = get_financial_summary(group)
        monthly_data.append({
            'Month': month,
            'Income': summary['total_income'],
            'Expenses': summary['total_expenses'],
            'Net Savings': summary['net_savings'],
            'Savings Rate': summary['savings_rate']
        })
    
    # Convert to DataFrame and sort chronologically by month
    trends_df = pd.DataFrame(monthly_data)
    if not trends_df.empty:
        trends_df = trends_df.sort_values('Month').reset_index(drop=True)
    
    return trends_df

