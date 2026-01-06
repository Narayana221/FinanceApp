# Implementation Artifact: Story 3.2 - Prompt Engineering & JSON Summary Preparation

## Story Reference

**Epic:** Epic 3 - Personalized AI Coaching & Insights  
**Story:** 3.2 - Prompt Engineering & JSON Summary Preparation  
**Status:** ready-for-dev

## Story Summary

As a user, I want my spending data intelligently summarized and sent to the AI coach, so that I receive relevant, personalized recommendations.

## Acceptance Criteria

**AC #1:** JSON Summary Preparation (REQ-AI-001, FR28)
- System shall prepare JSON summary of spending data
- Include: income, expenses, top categories, user's savings goal

**AC #2:** Structured Prompt Construction (REQ-AI-003, FR30)
- Construct structured prompts with spending summary, category breakdown, user context
- Follow structure from Architecture Decision 4.4

**AC #3:** Request Personalized Recommendations (REQ-AI-004, FR31)
- Request 3-5 personalized, specific recommendations
- Include concrete savings amounts

**AC #4:** Request Money Habit (REQ-AI-005, FR32)
- Request one simple "money habit" suggestion

**AC #5:** Request Spending Leaks (REQ-AI-006, FR33)
- Request explanation of biggest spending leaks

## Requirements Traceability

**Functional Requirements:**
- REQ-AI-001 (FR28): JSON summary of spending data
- REQ-AI-003 (FR30): Structured prompts with spending summary
- REQ-AI-004 (FR31): 3-5 personalized recommendations
- REQ-AI-005 (FR32): One money habit suggestion
- REQ-AI-006 (FR33): Explanation of spending leaks

**Non-Functional Requirements:**
- NFR-MAINT-004 (NFR17): Modular architecture
- NFR-USABILITY-002 (NFR4): Clear and easy to interpret

## Technical Design

### Architecture Overview

```
app.py
  ↓
utils/prompt_builder.py
  ├── prepare_financial_summary() - Create JSON summary
  ├── build_coaching_prompt() - Construct structured prompt
  └── _format_category_breakdown() - Helper for category data
  ↓
utils/gemini_client.py
  └── generate_financial_advice(prompt)
```

### Module: utils/prompt_builder.py

**Purpose:** Prepare financial data summaries and construct structured prompts for Gemini API.

**Functions:**

```python
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
        {
            'income': 2500.00,
            'expenses': 1800.00,
            'net_savings': 700.00,
            'savings_rate': 28.00,
            'savings_goal': 1000.00,
            'top_categories': [
                {'category': 'Groceries', 'amount': 450.00},
                {'category': 'Bills', 'amount': 400.00},
                ...
            ]
        }
    """
    pass


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
        financial_summary: Dict with income, expenses, savings, rate
        category_summary: Dict with category spending amounts
        savings_goal: Optional monthly savings goal
        
    Returns:
        str: Structured prompt ready for Gemini API
    """
    pass


def _format_category_breakdown(category_summary: Dict[str, float]) -> str:
    """
    Format category spending data for prompt inclusion.
    
    Args:
        category_summary: Dict with category names and amounts
        
    Returns:
        str: Formatted string listing categories and amounts
        
    Example:
        "- Groceries: £450.00
         - Bills: £400.00
         - Transport: £120.00"
    """
    pass
```

### JSON Summary Structure

```json
{
  "income": 2500.00,
  "expenses": 1800.00,
  "net_savings": 700.00,
  "savings_rate": 28.00,
  "savings_goal": 1000.00,
  "goal_gap": 300.00,
  "top_categories": [
    {"category": "Groceries", "amount": 450.00, "percentage": 25.0},
    {"category": "Bills", "amount": 400.00, "percentage": 22.2},
    {"category": "Transport", "amount": 120.00, "percentage": 6.7},
    {"category": "Eating Out", "amount": 180.00, "percentage": 10.0}
  ],
  "total_categories": 8
}
```

### Prompt Template Structure

```
You are a personal finance AI coach helping users improve their financial health.

USER PROFILE:
- Monthly Income: £{income}
- Monthly Expenses: £{expenses}
- Net Savings: £{net_savings}
- Current Savings Rate: {savings_rate}%
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

Format your response clearly with these three sections labeled.
```

### Savings Goal Handling

**If savings_goal provided:**
```
- Savings Goal: £{savings_goal}/month
- Gap to Goal: £{goal_gap} ({percentage}% short/ahead)
```

**If no savings_goal:**
```
- No specific savings goal set
- Recommendation: Consider setting a monthly savings target
```

### Category Breakdown Formatting

**Format:**
```
Top Spending Categories:
1. Groceries: £450.00 (25.0% of expenses)
2. Bills: £400.00 (22.2% of expenses)
3. Transport: £120.00 (6.7% of expenses)
4. Eating Out: £180.00 (10.0% of expenses)
5. Shopping: £100.00 (5.6% of expenses)

Total categories tracked: 8
```

**Sorting:** Categories sorted by amount (highest to lowest)  
**Limit:** Top 5 categories shown in detail

### Edge Cases Handling

| Scenario | Handling |
|----------|----------|
| No income | Income: £0.00, Note: "No income detected" |
| No expenses | Expenses: £0.00, Note: "No expenses recorded" |
| Zero savings rate | Savings Rate: 0.0%, Highlight in goal gap |
| Negative savings (deficit) | Net Savings: -£200.00, Flag as urgent issue |
| Empty category_summary | Show "No category data available" |
| Single category | Show single category, note limited data |
| Very high savings rate (>50%) | Include congratulatory note |

### Testing Strategy

**Unit Tests (tests/test_prompt_builder.py):**

1. **Test JSON Summary Preparation:**
   - Standard financial data → Complete summary
   - With savings goal → Include goal and gap
   - Without savings goal → Exclude goal fields
   - Negative savings → Correct gap calculation
   - Empty categories → Empty top_categories list
   - Category percentages calculated correctly

2. **Test Prompt Construction:**
   - Standard data → Well-formed prompt with all sections
   - With savings goal → Goal section included
   - Without savings goal → Generic goal recommendation
   - Verify all 3 task sections present (recommendations, habit, leaks)
   - Verify category breakdown formatted correctly
   - Verify amounts formatted with £ symbol

3. **Test Category Formatting:**
   - Multiple categories → Top 5 shown
   - Sorted by amount descending
   - Percentages calculated correctly
   - Empty dict → Appropriate message

4. **Test Edge Cases:**
   - Zero income → Handled gracefully
   - Zero expenses → Handled gracefully
   - Deficit (negative savings) → Highlighted
   - Very high savings rate → Noted
   - Single category → Works correctly

### Integration Points

**Input Sources:**
- `get_financial_summary()` from `utils/analytics.py`
- `get_category_summary()` from `utils/categorizer.py`
- User-provided savings_goal (optional, future enhancement)

**Output Consumers:**
- `GeminiClient.generate_financial_advice()` from `utils/gemini_client.py`

**Integration Flow:**
```python
# In app.py (Story 3.3 or 3.4)
from utils.analytics import get_financial_summary
from utils.categorizer import get_category_summary
from utils.prompt_builder import build_coaching_prompt
from utils.gemini_client import GeminiClient

# Get analytics
financial_summary = get_financial_summary(categorized_data)
category_summary = get_category_summary(categorized_data)

# Build prompt
prompt = build_coaching_prompt(
    financial_summary,
    category_summary,
    savings_goal=1000.00  # Optional
)

# Get AI advice
client = GeminiClient()
result = client.generate_financial_advice(prompt)

if result['success']:
    display_advice(result['advice'])
```

## Files to Create/Modify

### Create:
- `utils/prompt_builder.py` - Prompt engineering module (~150 lines)
- `tests/test_prompt_builder.py` - Comprehensive test suite (~20 tests)

### Modify:
- `utils/__init__.py` - Export prompt_builder functions

## Dependencies

**Existing Dependencies:**
- `utils/analytics.py` - Provides get_financial_summary()
- `utils/categorizer.py` - Provides get_category_summary()
- `utils/gemini_client.py` - Will consume prompts (Story 3.1)

**New Dependencies:**
- None (uses standard library only)

## Implementation Notes

1. **JSON Summary:**
   - Use standard Python dict (JSON-serializable)
   - Round all monetary values to 2 decimal places
   - Calculate percentages to 1 decimal place

2. **Prompt Construction:**
   - Use f-strings for template formatting
   - Ensure proper line breaks and spacing
   - Keep prompt concise but informative (<500 words)

3. **Category Breakdown:**
   - Limit to top 5 categories for brevity
   - Calculate percentages relative to total expenses
   - Format amounts with £ symbol for clarity

4. **Savings Goal:**
   - Default to None if not provided
   - Calculate gap: savings_goal - net_savings
   - Show percentage: (gap / savings_goal) * 100

5. **Prompt Optimization:**
   - Clear section headers (CAPITALS)
   - Numbered lists for structure
   - Specific instructions for AI output format

## Assumptions

1. `financial_summary` dict contains keys: total_income, total_expenses, net_savings, savings_rate
2. `category_summary` dict maps category names to amounts
3. Savings goal is a monthly target (not annual)
4. Currency is GBP (£)
5. AI will follow prompt structure in response

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Prompt too long | API limits/cost | Keep concise, limit categories to top 5 |
| Missing data fields | Incomplete summary | Validate inputs, provide defaults |
| AI misinterprets prompt | Poor recommendations | Clear structure, specific instructions |
| Category data empty | Generic advice | Handle gracefully, note in prompt |
| Negative savings | Confusing output | Clearly flag deficit situations |

## Definition of Done

- [ ] `utils/prompt_builder.py` implemented with all functions
- [ ] `prepare_financial_summary()` creates complete JSON summary
- [ ] `build_coaching_prompt()` constructs well-formed prompts
- [ ] `_format_category_breakdown()` formats categories correctly
- [ ] Savings goal included when provided
- [ ] All 3 task sections in prompt (recommendations, habit, leaks)
- [ ] Top 5 categories shown with percentages
- [ ] Edge cases handled (zero values, deficit, empty data)
- [ ] Comprehensive test suite (~20 tests) passing
- [ ] All AC validated through tests
- [ ] Code follows existing project structure
- [ ] Documentation in docstrings
- [ ] Git commit with descriptive message
- [ ] Pushed to GitHub

## Dev Agent Record

### Agent Model Used

Claude Sonnet 4.5 via GitHub Copilot

### Debug Log References

No debugging required - implementation proceeded smoothly.

### Completion Notes List

1. **Implementation Complete (2025-01-XX)**
   - Created `utils/prompt_builder.py` with all three functions
   - Implemented `prepare_financial_summary()` to create JSON summaries
   - Implemented `build_coaching_prompt()` to construct structured prompts
   - Implemented `_format_category_breakdown()` helper function
   - All functions handle edge cases (zero values, empty data, deficit, etc.)

2. **Testing Complete**
   - Created comprehensive test suite `tests/test_prompt_builder.py`
   - 28 tests covering all functionality:
     * 9 tests for `prepare_financial_summary()`
     * 9 tests for `build_coaching_prompt()`
     * 6 tests for `_format_category_breakdown()`
     * 4 tests for edge cases
   - All 268 tests passing (240 existing + 28 new)
   - No regressions introduced

3. **Module Features**
   - JSON summary includes: income, expenses, net_savings, savings_rate, top_categories
   - Optional savings_goal with calculated goal_gap
   - Top 5 categories sorted by amount with percentages
   - Structured prompt follows Architecture Decision 4.4
   - Requests 3-5 recommendations, money habit, spending leaks analysis
   - Handles all edge cases gracefully

4. **Integration Points**
   - Exported functions via `utils/__init__.py`
   - Ready for integration with `GeminiClient` (Story 3.1)
   - Consumes output from `analytics.py` and `categorizer.py`
   - Will be used in Story 3.3 (Display AI Coach Summary)

5. **Acceptance Criteria Validation**
   - ✅ AC #1: JSON summary preparation (REQ-AI-001)
   - ✅ AC #2: Structured prompt construction (REQ-AI-003)
   - ✅ AC #3: Request personalized recommendations (REQ-AI-004)
   - ✅ AC #4: Request money habit (REQ-AI-005)
   - ✅ AC #5: Request spending leaks (REQ-AI-006)

### File List

**Created:**
- `utils/prompt_builder.py` (205 lines)
- `tests/test_prompt_builder.py` (495 lines)

**Modified:**
- `utils/__init__.py` - Added prompt_builder exports
- `_bmad-output/implementation-artifacts/3-2-prompt-engineering.md` - Updated with completion notes
