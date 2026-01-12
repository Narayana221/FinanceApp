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
    savings_goal: Optional[float] = None,
    tone: str = 'supportive'
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
        tone: Tone mode for AI coach ('supportive', 'playful', 'serious')
        
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
        >>> prompt = build_coaching_prompt(financial, categories, 1000.00, 'playful')
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
    
    # Define tone personality (Story 5.2)
    tone_personalities = {
        'supportive': 'You are a supportive personal finance coach. Be warm and encouraging - never critical.',
        'playful': 'You are a fun and energetic personal finance coach! Use emojis, casual language, and make finances feel less scary. Be upbeat and motivating!',
        'serious': 'You are a professional financial advisor. Be direct, factual, and analytical. Focus on numbers and concrete actions.'
    }
    
    tone_personality = tone_personalities.get(tone.lower(), tone_personalities['supportive'])
    
    # Construct the full prompt
    prompt = f"""{tone_personality}

USER PROFILE:
- Monthly Income: £{total_income:,.2f}
- Monthly Expenses: £{total_expenses:,.2f}
- Net Savings: £{net_savings:,.2f}
- Savings Rate: {savings_rate:.1f}%
{savings_goal_section}

SPENDING BREAKDOWN:
{category_breakdown}

Provide advice in this EXACT format:

## RECOMMENDATIONS

**1. [Title with £X/month saving target]**
[2-3 sentences: explain the opportunity positively and give practical steps. 40+ words.]

**2. [Title with £X/month saving target]**
[2-3 sentences with positive framing. 40+ words.]

**3. [Title with £X/month saving target]**
[2-3 sentences with positive framing. 40+ words.]

## MONEY HABIT
[One simple daily/weekly habit in 2-3 sentences. Be encouraging. 30+ words.]

## SPENDING LEAKS
**[Category] – £[Amount]/month ([%]% of expenses)**
[2-3 sentences: frame as opportunity, suggest realistic reduction. 40+ words.]

RULES:
- Use encouraging language ("opportunity", "you could") not critical language
- Never suggest reducing discretionary spending to £0
- Each paragraph must be 40+ words
- No intro text - start with ## RECOMMENDATIONS"""
    
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
