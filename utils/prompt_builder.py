"""
Prompt Builder Module

This module prepares financial data summaries and constructs structured prompts
for the Gemini AI Financial Coach.

Functions:
    prepare_financial_summary: Create JSON summary of financial data
    build_coaching_prompt: Construct structured prompt for AI coaching
    _format_category_breakdown: Format category spending data
"""

from typing import Dict, Any, Optional, List


def prepare_financial_summary(
    financial_summary: Dict[str, float],
    category_summary: Dict[str, float],
    savings_goal: Optional[float] = None
) -> Dict[str, Any]:
    """
    Prepare JSON summary of financial data for AI coaching.
    
    Args:
        financial_summary: Dict with total_income, total_expenses, 
                          net_savings, savings_rate
        category_summary: Dict with category names and spending amounts
        savings_goal: Optional monthly savings goal (default: None)
        
    Returns:
        dict: JSON-serializable summary with all key metrics
        
    Example:
        >>> financial = {
        ...     'total_income': 2500.00,
        ...     'total_expenses': 1800.00,
        ...     'net_savings': 700.00,
        ...     'savings_rate': 28.00
        ... }
        >>> categories = {'Groceries': 450.00, 'Bills': 400.00}
        >>> summary = prepare_financial_summary(financial, categories, 1000.00)
        >>> summary['income']
        2500.0
        >>> summary['savings_goal']
        1000.0
    """
    # Extract financial metrics
    total_income = financial_summary.get('total_income', 0.0)
    total_expenses = financial_summary.get('total_expenses', 0.0)
    net_savings = financial_summary.get('net_savings', 0.0)
    savings_rate = financial_summary.get('savings_rate', 0.0)
    
    # Prepare base summary
    summary = {
        'income': round(total_income, 2),
        'expenses': round(total_expenses, 2),
        'net_savings': round(net_savings, 2),
        'savings_rate': round(savings_rate, 1)
    }
    
    # Add savings goal if provided
    if savings_goal is not None:
        summary['savings_goal'] = round(savings_goal, 2)
        goal_gap = savings_goal - net_savings
        summary['goal_gap'] = round(goal_gap, 2)
    
    # Prepare top categories list
    top_categories = []
    if category_summary:
        # Sort categories by amount (descending)
        sorted_categories = sorted(
            category_summary.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        # Take top 5 categories
        for category, amount in sorted_categories[:5]:
            # Calculate percentage of total expenses
            percentage = (amount / total_expenses * 100) if total_expenses > 0 else 0.0
            
            top_categories.append({
                'category': category,
                'amount': round(amount, 2),
                'percentage': round(percentage, 1)
            })
    
    summary['top_categories'] = top_categories
    summary['total_categories'] = len(category_summary)
    
    return summary


def build_coaching_prompt(
    financial_summary: Dict[str, float],
    category_summary: Dict[str, float],
    savings_goal: Optional[float] = None
) -> str:
    """
    Construct structured prompt for AI financial coaching.
    
    Follows Architecture Decision 4.4 structure:
    - User profile and context
    - Spending summary with key metrics
    - Top spending categories breakdown
    - Request for specific outputs (recommendations, habit, leaks)
    
    Args:
        financial_summary: Dict with total_income, total_expenses, 
                          net_savings, savings_rate
        category_summary: Dict with category spending amounts
        savings_goal: Optional monthly savings goal
        
    Returns:
        str: Structured prompt ready for Gemini API
        
    Example:
        >>> financial = {
        ...     'total_income': 2500.00,
        ...     'total_expenses': 1800.00,
        ...     'net_savings': 700.00,
        ...     'savings_rate': 28.00
        ... }
        >>> categories = {'Groceries': 450.00, 'Bills': 400.00}
        >>> prompt = build_coaching_prompt(financial, categories, 1000.00)
        >>> 'Monthly Income: £2,500.00' in prompt
        True
    """
    # Extract financial metrics
    total_income = financial_summary.get('total_income', 0.0)
    total_expenses = financial_summary.get('total_expenses', 0.0)
    net_savings = financial_summary.get('net_savings', 0.0)
    savings_rate = financial_summary.get('savings_rate', 0.0)
    
    # Build savings goal section
    if savings_goal is not None:
        goal_gap = savings_goal - net_savings
        if goal_gap > 0:
            gap_status = f"£{goal_gap:,.2f} short ({abs(goal_gap / savings_goal * 100):.0f}% short)"
        elif goal_gap < 0:
            gap_status = f"£{abs(goal_gap):,.2f} ahead ({abs(goal_gap / savings_goal * 100):.0f}% ahead)"
        else:
            gap_status = "On target"
        
        savings_goal_section = f"""- Savings Goal: £{savings_goal:,.2f}/month
- Gap to Goal: {gap_status}"""
    else:
        savings_goal_section = """- No specific savings goal set
- Recommendation: Consider setting a monthly savings target"""
    
    # Build category breakdown
    category_breakdown = _format_category_breakdown(category_summary, total_expenses)
    
    # Construct the full prompt
    prompt = f"""You are a personal finance AI coach helping users improve their financial health.

USER PROFILE:
- Monthly Income: £{total_income:,.2f}
- Monthly Expenses: £{total_expenses:,.2f}
- Net Savings: £{net_savings:,.2f}
- Current Savings Rate: {savings_rate:.1f}%
{savings_goal_section}

SPENDING BREAKDOWN:
{category_breakdown}

YOUR TASK:
Analyze this financial data and provide:

1. RECOMMENDATIONS (3-5 specific, actionable items):
   - Each recommendation should include a concrete savings amount
   - Be specific about which spending category to target
   - Provide practical steps the user can take immediately
   
2. MONEY HABIT (1 simple habit):
   - Suggest one easy-to-adopt daily or weekly habit
   - Make it specific and actionable
   
3. SPENDING LEAKS (explain the biggest issues):
   - Identify the 1-2 categories where the user is overspending most
   - Explain why these are problematic
   - Provide context based on typical budgeting guidelines

Format your response clearly with these three sections labeled."""
    
    return prompt


def _format_category_breakdown(
    category_summary: Dict[str, float],
    total_expenses: float
) -> str:
    """
    Format category spending data for prompt inclusion.
    
    Args:
        category_summary: Dict with category names and amounts
        total_expenses: Total expenses for percentage calculation
        
    Returns:
        str: Formatted string listing categories and amounts
        
    Example:
        >>> categories = {'Groceries': 450.00, 'Bills': 400.00}
        >>> breakdown = _format_category_breakdown(categories, 1800.00)
        >>> 'Groceries: £450.00' in breakdown
        True
    """
    if not category_summary:
        return "No category data available."
    
    # Sort categories by amount (descending)
    sorted_categories = sorted(
        category_summary.items(),
        key=lambda x: x[1],
        reverse=True
    )
    
    # Build formatted string
    lines = ["Top Spending Categories:"]
    
    # Show top 5 categories
    for i, (category, amount) in enumerate(sorted_categories[:5], 1):
        percentage = (amount / total_expenses * 100) if total_expenses > 0 else 0.0
        lines.append(f"{i}. {category}: £{amount:,.2f} ({percentage:.1f}% of expenses)")
    
    # Add total count
    total_count = len(category_summary)
    lines.append(f"\nTotal categories tracked: {total_count}")
    
    return "\n".join(lines)
