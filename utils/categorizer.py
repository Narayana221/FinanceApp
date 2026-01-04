"""
Transaction categorization utilities.

This module provides keyword-based categorization for transactions,
supporting automatic category assignment based on merchant names and
transaction descriptions.
"""

from typing import Dict, Optional
import pandas as pd


# Category rules dictionary - easily configurable (NFR-MAINT-003)
# Order matters: checked sequentially, first match wins
CATEGORY_RULES = {
    'Groceries': [
        'tesco', 'sainsbury', 'sainsburys', 'asda', 'morrisons',
        'waitrose', 'lidl', 'aldi', 'co-op', 'coop', 'marks & spencer',
        'm&s', 'iceland', 'ocado', 'supermarket', 'groceries'
    ],
    'Subscriptions': [
        'netflix', 'spotify', 'amazon prime', 'prime video',
        'apple music', 'youtube premium', 'disney', 'gym',
        'fitness', 'puregym', 'virgin active', 'membership'
    ],
    'Eating Out': [
        'restaurant', 'cafe', 'coffee', 'starbucks', 'costa', 'nero',
        'nando', 'nandos', 'mcdonald', 'mcdonalds', 'kfc', 'burger king',
        'pizza', 'domino', 'subway', 'greggs', 'pret', 'takeaway',
        'deliveroo', 'uber eats', 'just eat'
    ],
    'Transport': [
        'uber', 'train', 'bus', 'tube', 'tram',
        'oyster', 'tfl', 'transport for london', 'national rail',
        'petrol', 'fuel', 'shell', 'bp', 'esso', 'parking',
        'taxi', 'car park'
    ],
    'Shopping': [
        'amazon', 'ebay', 'asos', 'zara', 'h&m', 'next',
        'primark', 'argos', 'john lewis', 'boots', 'superdrug',
        'clothes', 'clothing', 'fashion'
    ],
    'Bills': [
        'electric', 'electricity', 'gas', 'water', 'council tax',
        'rent', 'mortgage', 'internet', 'broadband', 'virgin media',
        'bt', 'sky', 'vodafone', 'ee', 'o2', 'three', 'phone bill',
        'utilities', 'insurance'
    ]
}

# Income keywords for detection
INCOME_KEYWORDS = [
    'salary', 'wage', 'wages', 'payment received', 'transfer in',
    'refund', 'cashback', 'interest', 'dividend', 'bonus'
]


def categorize_transaction(description: str, 
                          existing_category: Optional[str] = None,
                          amount: Optional[float] = None) -> str:
    """
    Categorize a single transaction based on description and amount.
    
    Priority order:
    1. Use existing category if provided and not empty
    2. Detect income based on keywords or positive amount
    3. Match description against category rules
    4. Default to "Uncategorized"
    
    Args:
        description: Transaction description (merchant name, etc.)
        existing_category: Existing category from CSV (optional)
        amount: Transaction amount (optional, for income detection)
        
    Returns:
        str: Category name
        
    Examples:
        >>> categorize_transaction("Tesco", None, -45.30)
        'Groceries'
        
        >>> categorize_transaction("Salary", None, 2500.00)
        'Income'
        
        >>> categorize_transaction("Unknown", "Custom Category", -10.00)
        'Custom Category'
    """
    # Priority 1: Use existing category if provided
    if existing_category and pd.notna(existing_category) and str(existing_category).strip():
        return str(existing_category).strip()
    
    # Ensure description is string
    if description is None or pd.isna(description):
        description = ''
    desc_lower = str(description).lower()
    
    # Priority 2: Detect income based on keywords
    if desc_lower:
        for keyword in INCOME_KEYWORDS:
            if keyword.lower() in desc_lower:
                return 'Income'
    
    # Priority 3: Match against category rules
    for category, keywords in CATEGORY_RULES.items():
        for keyword in keywords:
            if keyword.lower() in desc_lower:
                return category
    
    # Priority 4: Check if it's income based on positive amount
    if amount is not None and amount > 0:
        return 'Income'
    
    # Default: Uncategorized
    return 'Uncategorized'


def categorize_transactions(df: pd.DataFrame) -> pd.DataFrame:
    """
    Categorize all transactions in a DataFrame.
    
    Expects columns: Description, Amount
    Optional columns: Category (existing categories preserved)
    Adds/updates Category column based on categorization rules.
    
    Args:
        df: DataFrame with transactions (must have Description and Amount columns)
        
    Returns:
        pd.DataFrame: DataFrame with categorized transactions
        
    Raises:
        ValueError: If required columns (Description, Amount) are missing
        
    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame({
        ...     'Description': ['Tesco', 'Salary'],
        ...     'Amount': [-45.30, 2500.00]
        ... })
        >>> result = categorize_transactions(df)
        >>> result['Category'].tolist()
        ['Groceries', 'Income']
    """
    if df is None or df.empty:
        return df
    
    # Validate required columns
    if 'Description' not in df.columns:
        raise ValueError("DataFrame must have 'Description' column")
    if 'Amount' not in df.columns:
        raise ValueError("DataFrame must have 'Amount' column")
    
    # Create copy to avoid modifying original
    result = df.copy()
    
    # Ensure Category column exists
    if 'Category' not in result.columns:
        result['Category'] = None
    
    # Categorize each transaction
    for idx, row in result.iterrows():
        description = row.get('Description', '')
        existing_category = row.get('Category', None)
        amount = row.get('Amount', None)
        
        result.at[idx, 'Category'] = categorize_transaction(
            description, existing_category, amount
        )
    
    return result


def get_category_summary(df: pd.DataFrame) -> Dict[str, float]:
    """
    Get spending summary by category (expenses only, excluding income).
    
    Returns categories sorted by total spending (highest first).
    
    Args:
        df: Categorized DataFrame with Amount and Category columns
        
    Returns:
        dict: Category names mapped to total spending (positive values)
        
    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame({
        ...     'Amount': [-45.30, -10.00, 2500.00],
        ...     'Category': ['Groceries', 'Transport', 'Income']
        ... })
        >>> summary = get_category_summary(df)
        >>> summary['Groceries']
        45.3
    """
    if df is None or df.empty or 'Category' not in df.columns or 'Amount' not in df.columns:
        return {}
    
    # Filter out income transactions (only show expenses)
    expenses = df[df['Amount'] < 0].copy()
    
    # Group by category and sum amounts (convert to positive)
    if not expenses.empty:
        summary = expenses.groupby('Category')['Amount'].sum().abs().to_dict()
        # Sort by spending amount (highest first)
        return dict(sorted(summary.items(), key=lambda x: x[1], reverse=True))
    
    return {}
