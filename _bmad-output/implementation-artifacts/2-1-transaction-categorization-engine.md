# Story 2.1: Transaction Categorization Engine

Status: review

## Story

As a user,
I want my transactions automatically categorized by spending type,
So that I can understand where my money goes without manual categorization.

## Acceptance Criteria

1. **Given** normalized transaction data is available, **When** the system categorizes transactions, **Then** it shall use keyword-based rules for common merchants and spending categories (REQ-DIP-009, FR20).

2. **Given** a transaction has an existing category from the CSV, **When** categorization runs, **Then** the system shall use the existing category as primary (Architecture Decision 4.2).

3. **Given** a transaction has no existing category, **When** the fallback categorization runs, **Then** the system shall match merchant/description keywords against categories: Groceries, Eating Out, Transport, Subscriptions, Shopping, Bills (Architecture Decision 4.2).

4. **Given** a transaction matches no category rules, **When** categorization completes, **Then** the system shall assign "Uncategorized" to transactions that don't match any category rules (REQ-DIP-011, FR22).

5. **Given** category rules need updates, **When** reviewing the configuration, **Then** category rules shall be stored in configurable dictionaries for easy updates (NFR-MAINT-003, NFR16).

## Tasks / Subtasks

- [ ] Create categorization module (AC: #1, #2, #3, #4, #5)
  - [ ] Create utils/categorizer.py module
  - [ ] Define CATEGORY_RULES dictionary with keywords
  - [ ] Implement categorize_transaction() function
  - [ ] Implement categorize_transactions() for batch processing
  - [ ] Respect existing categories from CSV

- [ ] Define category rules (AC: #3, #5)
  - [ ] Groceries: tesco, sainsbury, asda, morrisons, waitrose, lidl, aldi
  - [ ] Eating Out: restaurant, cafe, coffee, starbucks, costa, nando, mcdonald
  - [ ] Transport: uber, train, bus, tube, oyster, tfl, petrol, fuel
  - [ ] Subscriptions: netflix, spotify, amazon prime, gym
  - [ ] Shopping: amazon, ebay, asos, zara, next, primark
  - [ ] Bills: electric, gas, water, council tax, rent, mortgage, internet

- [ ] Implement income detection (related to Story 2.2)
  - [ ] Detect positive amounts
  - [ ] Detect income keywords: salary, wage, payment received, transfer in

- [ ] Write comprehensive tests (NFR-MAINT-002)
  - [ ] Test categorization with existing categories
  - [ ] Test keyword matching for each category
  - [ ] Test case-insensitive matching
  - [ ] Test "Uncategorized" assignment
  - [ ] Test income detection
  - [ ] Test batch processing

## Dev Notes

### Critical Architecture Patterns

**Categorization Strategy (Architecture 4.2 - Transaction Categorization):**
1. **Primary**: Use existing `Category` column from CSV if present
2. **Fallback**: Match description keywords against category rules
3. **Default**: Assign "Uncategorized" if no match

**Income Detection:**
- Positive amounts (`Amount > 0`)
- Keywords: "salary", "wage", "payment received", "transfer in", "refund"

**Extensibility (NFR-MAINT-003, NFR16):**
- Category rules in configurable dictionary
- Easy to add new categories or keywords
- No code changes needed to update rules

### Technical Requirements

**categorizer.py Module Structure:**
```python
"""
Transaction categorization utilities.

This module provides keyword-based categorization for transactions.
"""

from typing import Dict, List, Optional
import pandas as pd

# Category rules dictionary - easily configurable
CATEGORY_RULES = {
    'Groceries': [
        'tesco', 'sainsbury', 'sainsburys', 'asda', 'morrisons',
        'waitrose', 'lidl', 'aldi', 'co-op', 'coop', 'marks & spencer',
        'm&s', 'iceland', 'ocado', 'supermarket', 'groceries'
    ],
    'Eating Out': [
        'restaurant', 'cafe', 'coffee', 'starbucks', 'costa', 'nero',
        'nando', 'nandos', 'mcdonald', 'mcdonalds', 'kfc', 'burger king',
        'pizza', 'domino', 'subway', 'greggs', 'pret', 'takeaway',
        'deliveroo', 'uber eats', 'just eat'
    ],
    'Transport': [
        'uber', 'train', 'bus', 'tube', 'metro', 'tram',
        'oyster', 'tfl', 'transport for london', 'national rail',
        'petrol', 'fuel', 'shell', 'bp', 'esso', 'parking',
        'taxi', 'car park'
    ],
    'Subscriptions': [
        'netflix', 'spotify', 'amazon prime', 'prime video',
        'apple music', 'youtube premium', 'disney', 'gym',
        'fitness', 'puregym', 'virgin active', 'membership'
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

# Income keywords
INCOME_KEYWORDS = [
    'salary', 'wage', 'wages', 'payment received', 'transfer in',
    'refund', 'cashback', 'interest', 'dividend', 'bonus'
]


def categorize_transaction(description: str, 
                          existing_category: Optional[str] = None,
                          amount: Optional[float] = None) -> str:
    """
    Categorize a single transaction based on description and amount.
    
    Priority:
    1. Use existing category if provided
    2. Detect income based on keywords or positive amount
    3. Match description against category rules
    4. Default to "Uncategorized"
    
    Args:
        description: Transaction description
        existing_category: Existing category from CSV (optional)
        amount: Transaction amount (optional, for income detection)
        
    Returns:
        str: Category name
    """
    # Priority 1: Use existing category
    if existing_category and pd.notna(existing_category) and str(existing_category).strip():
        return str(existing_category).strip()
    
    # Priority 2: Detect income
    if amount is not None and amount > 0:
        desc_lower = description.lower() if description else ''
        for keyword in INCOME_KEYWORDS:
            if keyword in desc_lower:
                return 'Income'
        # Positive amount without income keyword - likely a refund or credit
        # Check if it matches expense categories, otherwise treat as income
        
    # Priority 3: Match against category rules
    if description:
        desc_lower = description.lower()
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
    
    Expects columns: Description, Amount, Category (optional)
    Adds/updates Category column.
    
    Args:
        df: DataFrame with transactions
        
    Returns:
        pd.DataFrame: DataFrame with categorized transactions
    """
    if df is None or df.empty:
        return df
    
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
    Get spending summary by category.
    
    Args:
        df: Categorized DataFrame
        
    Returns:
        dict: Category totals (excluding Income)
    """
    if df is None or df.empty or 'Category' not in df.columns:
        return {}
    
    # Filter out income transactions
    expenses = df[df['Amount'] < 0].copy()
    
    # Group by category and sum amounts (convert to positive)
    if not expenses.empty:
        summary = expenses.groupby('Category')['Amount'].sum().abs().to_dict()
        return dict(sorted(summary.items(), key=lambda x: x[1], reverse=True))
    
    return {}
```

### Code Standards

**Configurability (NFR-MAINT-003):**
- CATEGORY_RULES as module-level constant
- Easy to add new categories or keywords
- No function changes needed for rule updates

**Testing Requirements (NFR-MAINT-002):**
- Test all category matching scenarios
- Test case-insensitive matching
- Test priority order (existing > keywords > uncategorized)
- Test income detection
- Maintain 70%+ code coverage

**Data Processing Best Practices:**
- Case-insensitive keyword matching
- Handle None/NaN values gracefully
- Return copy of DataFrame (don't modify original)
- Use pandas vectorization where possible

### Implementation Guidance

**Integration Points:**
- `models/csv_model.py`: Add categorization after validation
- New module: `utils/categorizer.py`
- Tests: `tests/test_categorizer.py`

**Example Usage:**
```python
from utils.categorizer import categorize_transactions

# In CSVDataModel after validation
self.categorized_data = categorize_transactions(self.validated_data)
```

### Usability Requirements

**Category Coverage:**
- Common UK spending categories
- Recognizable merchant names
- Transport includes TfL, Oyster (London-specific)
- Bills include utilities, rent, insurance

**Future Enhancements:**
- User-defined categories
- Machine learning categorization
- Category editing UI
- Transaction history learning

### References

- [Architecture: Section 4.2 - Transaction Categorization](_bmad-output/planning-artifacts/architecture-overview-FinanceApp-2025-12-26.md#42-transaction-categorization)
- [PRD: Section 5.2 - REQ-DIP-009, REQ-DIP-010, REQ-DIP-011](_bmad-output/planning-artifacts/prd-FinanceApp-2025-12-26.md#52-data-ingestion-and-processing)
- [Epic File: Story 2.1](_bmad-output/planning-artifacts/epics.md#story-21-transaction-categorization-engine)
- [Technical Spec: Analytics Functions](_bmad-output/planning-artifacts/technical-spec-FinanceApp-2025-12-26.md)

## Dev Agent Record

### Agent Model Used

_To be filled by Dev agent_

### Debug Log References

_To be filled by Dev agent during implementation_

### Completion Notes List

_To be filled by Dev agent upon completion_

### File List

_To be filled by Dev agent with created/modified files_
