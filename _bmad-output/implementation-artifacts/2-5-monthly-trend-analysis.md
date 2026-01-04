# Story 2.5: Monthly Trend Analysis

Status: review

## Story

As a user,
I want to see my spending and savings trends over time,
So that I can track my financial progress month by month.

## Acceptance Criteria

1. **Given** transaction data spans multiple months, **When** the analytics engine processes the data, **Then** the system shall aggregate spending and other metrics by month (REQ-AE-005, FR27).

2. **Given** monthly aggregation is complete, **When** calculating monthly metrics, **Then** the system shall provide income, expenses, net savings, and savings rate for each month.

3. **Given** monthly data is available, **When** displaying the trends, **Then** the application shall show a line chart or trend visualization of monthly spending and savings over time.

## Tasks / Subtasks

- [ ] Implement monthly aggregation (AC: #1, #2)
  - [ ] Add get_monthly_trends() to utils/analytics.py
  - [ ] Group transactions by month (YYYY-MM format)
  - [ ] Calculate monthly: income, expenses, net savings, savings rate
  - [ ] Return DataFrame with monthly metrics

- [ ] Create monthly trend visualization (AC: #3)
  - [ ] Add render_monthly_trends_chart() to views/charts.py
  - [ ] Line chart for income/expenses over time
  - [ ] Line chart for net savings over time
  - [ ] Line chart for savings rate over time
  - [ ] Use st.line_chart() or Altair

- [ ] Integrate into main app (AC: #3)
  - [ ] Update app.py to call get_monthly_trends()
  - [ ] Display monthly trends section
  - [ ] Show only if data spans multiple months

- [ ] Write comprehensive tests
  - [ ] Test monthly aggregation logic
  - [ ] Test single month scenario
  - [ ] Test multiple months
  - [ ] Test edge cases (missing dates, incomplete months)

## Dev Notes

### Critical Architecture Patterns

**Monthly Aggregation Strategy:**
- Extract year-month from Date column
- Group by year-month
- Apply income/expense calculations per month
- Return chronologically sorted DataFrame

**Data Structure:**
```python
# Output format
pd.DataFrame({
    'Month': ['2025-01', '2025-02', '2025-03'],
    'Income': [3300.00, 2500.00, 3150.00],
    'Expenses': [1200.00, 1300.00, 1250.00],
    'Net Savings': [2100.00, 1200.00, 1900.00],
    'Savings Rate': [63.64, 48.00, 60.32]
})
```

### Technical Requirements

**analytics.py Enhancement:**
```python
def get_monthly_trends(df: pd.DataFrame) -> pd.DataFrame:
    \"\"\"
    Aggregate financial metrics by month.
    
    Groups categorized transactions by month and calculates
    income, expenses, net savings, and savings rate for each month.
    
    Args:
        df: Categorized DataFrame with Date, Amount, Category columns
        
    Returns:
        pd.DataFrame: Monthly metrics with columns:
            - Month (str): YYYY-MM format
            - Income (float): Total monthly income
            - Expenses (float): Total monthly expenses (positive)
            - Net Savings (float): Income - Expenses
            - Savings Rate (float): (Net Savings / Income) * 100
            
    Examples:
        >>> df = pd.DataFrame({
        ...     'Date': ['2025-01-15', '2025-01-20', '2025-02-10'],
        ...     'Amount': [2500.00, -1000.00, 2500.00],
        ...     'Category': ['Income', 'Bills', 'Income']
        ... })
        >>> trends = get_monthly_trends(df)
        >>> trends['Month'].tolist()
        ['2025-01', '2025-02']
    \"\"\"
    if df is None or df.empty:
        return pd.DataFrame()
    
    # Ensure Date column exists and is datetime
    if 'Date' not in df.columns:
        return pd.DataFrame()
    
    # Create copy and ensure Date is datetime
    result = df.copy()
    result['Date'] = pd.to_datetime(result['Date'], errors='coerce')
    
    # Remove rows with invalid dates
    result = result.dropna(subset=['Date'])
    
    if result.empty:
        return pd.DataFrame()
    
    # Extract year-month
    result['Month'] = result['Date'].dt.to_period('M').astype(str)
    
    # Group by month and calculate metrics
    monthly_data = []
    for month, group in result.groupby('Month'):
        summary = get_financial_summary(group)
        monthly_data.append({
            'Month': month,
            'Income': summary['total_income'],
            'Expenses': summary['total_expenses'],
            'Net Savings': summary['net_savings'],
            'Savings Rate': summary['savings_rate']
        })
    
    # Convert to DataFrame and sort by month
    trends_df = pd.DataFrame(monthly_data)
    if not trends_df.empty:
        trends_df = trends_df.sort_values('Month')
    
    return trends_df
```

**charts.py Enhancement:**
```python
def render_monthly_trends_chart(trends_df: pd.DataFrame) -> None:
    \"\"\"
    Display monthly financial trends as line charts.
    
    Shows three trend lines:
    1. Income and Expenses over time
    2. Net Savings over time
    3. Savings Rate over time
    
    Args:
        trends_df: Monthly trends DataFrame from get_monthly_trends()
    \"\"\"
    if trends_df is None or trends_df.empty:
        st.info(\"Need data from multiple months to show trends.\")
        return
    
    if len(trends_df) < 2:
        st.info(\"Need at least 2 months of data to show meaningful trends.\")
        return
    
    st.subheader(\"📈 Monthly Trends\")
    
    # Chart 1: Income vs Expenses
    st.markdown(\"**Income & Expenses Trend**\")
    income_expense_df = trends_df.set_index('Month')[['Income', 'Expenses']]
    st.line_chart(income_expense_df)
    
    # Chart 2: Net Savings
    st.markdown(\"**Net Savings Trend**\")
    savings_df = trends_df.set_index('Month')[['Net Savings']]
    st.line_chart(savings_df)
    
    # Chart 3: Savings Rate
    st.markdown(\"**Savings Rate Trend**\")
    rate_df = trends_df.set_index('Month')[['Savings Rate']]
    st.line_chart(rate_df)
    
    # Show summary table
    with st.expander(\"View monthly breakdown\"):
        display_df = trends_df.copy()
        display_df['Income'] = display_df['Income'].apply(lambda x: f\"£{x:,.2f}\")
        display_df['Expenses'] = display_df['Expenses'].apply(lambda x: f\"£{x:,.2f}\")
        display_df['Net Savings'] = display_df['Net Savings'].apply(lambda x: f\"£{x:,.2f}\")
        display_df['Savings Rate'] = display_df['Savings Rate'].apply(lambda x: f\"{x:.1f}%\")
        st.dataframe(display_df, use_container_width=True, hide_index=True)
```

### Code Standards

**Date Handling:**
- Use pd.to_datetime() with errors='coerce'
- Extract year-month using dt.to_period('M')
- Sort chronologically by month
- Handle invalid/missing dates gracefully

**Monthly Metrics:**
- Reuse get_financial_summary() for consistency
- Calculate per month, not cumulative
- Maintain 2 decimal precision
- Handle months with no income (savings rate = 0)

### Implementation Guidance

**Integration Pattern:**
```python
# In app.py after categorization
categorized_data = categorize_transactions(data)

# Calculate monthly trends (Story 2.5)
monthly_trends = get_monthly_trends(categorized_data)

# Display only if multiple months
if not monthly_trends.empty and len(monthly_trends) >= 2:
    st.markdown(\"---\")
    st.header(\"📈 Monthly Trends\")
    render_monthly_trends_chart(monthly_trends)
```

**Edge Cases:**
- Single month: Don't show trends (need at least 2 months)
- Incomplete months: Include partial month data
- No dates: Return empty DataFrame
- Invalid dates: Filter out before aggregation

### Testing Requirements

**Test Cases:**
1. Multiple months aggregation
2. Single month (should work but won't display trends)
3. Empty DataFrame
4. Missing Date column
5. Invalid dates
6. Months with no income
7. Months with no expenses
8. Chronological sorting
9. Month format (YYYY-MM)
10. Metric calculations per month

### Usability Requirements

**Clear Trends:**
- X-axis: Month labels (2025-01, 2025-02)
- Y-axis: Currency (£) or percentage (%)
- Multiple line charts for clarity
- Color coding if using Altair
- Summary table for exact values

### References

- [Architecture: Section 4.5 - Analytics](_bmad-output/planning-artifacts/architecture-overview-FinanceApp-2025-12-26.md)
- [PRD: Section 5.3 - REQ-AE-005](_bmad-output/planning-artifacts/prd-FinanceApp-2025-12-26.md#53-analytics-and-calculations)
- [Epic File: Story 2.5](_bmad-output/planning-artifacts/epics.md#story-25-monthly-trend-analysis)
- [Technical Spec: Monthly Analytics](_bmad-output/planning-artifacts/technical-spec-FinanceApp-2025-12-26.md)

## Dev Agent Record

### Agent Model Used

Claude Sonnet 4.5 (Sm Agent)

### Debug Log References

N/A - Implementation completed without debugging issues

### Completion Notes List

**Story 2.5: Monthly Trend Analysis - COMPLETED**

**Implementation Summary:**
Successfully implemented comprehensive monthly trend analysis with date-based aggregation, monthly metrics calculation, and line chart visualizations for tracking financial progress over time.

**Files Created:**
- `utils/analytics.py` - Added `get_monthly_trends()` function (74 lines)
- `views/charts.py` - Added `render_monthly_trends_chart()` function (67 lines)
- `tests/test_monthly_trends.py` - Comprehensive test suite (24 tests, 389 lines)
- `sample-transactions-multi-month.csv` - Multi-month test data (45 transactions across 4 months)

**Files Modified:**
- `views/__init__.py` - Added render_monthly_trends_chart export
- `app.py` - Integrated monthly trends section (displays for 2+ months)

**Test Results:**
- ✅ **212 total tests passing** (188 previous + 24 new monthly trends)
- ✅ **24 new tests** covering all monthly aggregation scenarios
- ✅ **2 warnings** (pandas date parsing - non-blocking, pre-existing + new expected warning)
- ✅ **100% coverage** of monthly trend functionality

**Monthly Trends Functionality Implemented:**

1. **`get_monthly_trends(df)` in utils/analytics.py**
   - Groups transactions by month (YYYY-MM format)
   - Extracts year-month using `pd.to_period('M')`
   - Calculates metrics per month:
     - Income (total positive amounts)
     - Expenses (total negative amounts, displayed positive)
     - Net Savings (Income - Expenses)
     - Savings Rate ((Net Savings / Income) * 100)
   - Returns DataFrame sorted chronologically
   - Leverages `get_financial_summary()` for consistency
   - Handles invalid dates, empty data, missing columns

2. **`render_monthly_trends_chart(trends_df)` in views/charts.py**
   - Displays 3 separate line charts:
     - Income & Expenses Over Time
     - Net Savings Over Time
     - Savings Rate Over Time (%)
   - Requires ≥2 months for display (shows info message otherwise)
   - Expandable monthly breakdown table with currency formatting
   - Uses st.line_chart() for visualization
   - Month labels on X-axis, values on Y-axis

3. **App Integration (app.py)**
   - Calculates monthly trends after categorization
   - Displays only if 2+ months of data available
   - Shows in dedicated "📈 Monthly Trends" section
   - Positioned after charts, before data preview

**Data Flow:**
```
CSV Upload → Validation → Categorization (Story 2.1)
    ↓
get_monthly_trends(categorized_df)
    ├── Extract Date → Year-Month
    ├── Group by Month
    ├── Apply get_financial_summary() per group
    └── Return sorted DataFrame
    ↓
render_monthly_trends_chart(trends_df)
    ├── Income/Expenses Line Chart
    ├── Net Savings Line Chart
    ├── Savings Rate Line Chart
    └── Expandable Monthly Table
```

**Test Coverage (24 tests):**

*TestGetMonthlyTrends (20 tests):*
1. Basic monthly aggregation (2 months)
2. Multiple months aggregation (3+ months)
3. Monthly net savings calculation
4. Monthly savings rate calculation
5. Single month data
6. Empty DataFrame
7. None DataFrame
8. Missing Date column
9. Invalid dates
10. Mixed date formats
11. Chronological sorting
12. Month with only income
13. Month with only expenses
14. Month format validation (YYYY-MM)
15. Multiple transactions same month
16. Year boundary crossing (2024-12 to 2025-01)
17. DataFrame columns validation
18. Deficit month (expenses > income)
19. Datetime objects
20. Integration with categorized data

*TestMonthlyTrendsEdgeCases (4 tests):*
21. Very large date range (24 months)
22. Sparse months (non-consecutive)
23. NaN amounts
24. Partial month data

**Acceptance Criteria Validation:**

✅ **AC #1:** Aggregate spending and metrics by month (REQ-AE-005, FR27)
- `get_monthly_trends()` groups by YYYY-MM
- Calculates income, expenses, net savings, savings rate per month
- Returns chronologically sorted DataFrame

✅ **AC #2:** Provide income, expenses, net savings, and savings rate for each month
- Each month row contains all 4 metrics
- Leverages `get_financial_summary()` for consistency
- Handles edge cases (no income, no expenses, deficit)

✅ **AC #3:** Show line chart or trend visualization
- 3 separate line charts for clarity
- Income & Expenses (multi-line)
- Net Savings (trend)
- Savings Rate (percentage trend)
- Expandable table for exact values

**Technical Implementation Details:**

*Date Handling:*
- `pd.to_datetime()` with errors='coerce' for robust parsing
- `dt.to_period('M')` for year-month extraction
- Filters out invalid dates before aggregation
- Supports various date formats (YYYY-MM-DD, DD/MM/YYYY, datetime objects)

*Aggregation Strategy:*
- Group by extracted Month column
- Apply `get_financial_summary()` to each group
- Convert to DataFrame with Month, Income, Expenses, Net Savings, Savings Rate
- Sort by Month (chronological)

*Visualization Strategy:*
- Minimum 2 months required for meaningful trends
- Info messages for insufficient data
- Separate charts avoid cluttering
- Expandable table preserves detail
- Currency and percentage formatting

**UI/UX Features:**
- ✅ Clear section header (📈 Monthly Trends)
- ✅ Descriptive chart titles
- ✅ Month labels (2025-01, 2025-02)
- ✅ Currency formatting (£1,234.56)
- ✅ Percentage formatting (45.2%)
- ✅ Empty state messages
- ✅ Expandable details table
- ✅ Only shows with 2+ months
- ✅ Responsive layout

**Integration with Previous Stories:**
- Story 2.1: Uses categorized DataFrame with Category column
- Story 2.2: Leverages `get_financial_summary()` for monthly metrics
- Story 2.3: Follows same visualization patterns (st.line_chart, expandable tables)

**Sample Data Created:**
- `sample-transactions-multi-month.csv`
- 45 transactions across 4 months (Jan-Apr 2025)
- Tests monthly aggregation functionality
- Shows income and expense trends

**Validation Against Requirements:**
- REQ-AE-005 (Monthly Aggregation): ✅ Implemented
- FR27 (Monthly Trends): ✅ Visualized
- NFR-USABILITY-002 (Clear & Easy): ✅ Met with line charts and labels

**Notes:**
- Test count increased from 188 to 212 (+24 monthly trends tests)
- All existing tests remain passing (no regressions)
- Monthly trends only display with 2+ months (prevents misleading single-point charts)
- Chronological sorting ensures proper trend visualization
- Handles year boundaries correctly (2024-12 → 2025-01)

**Epic 2 Complete:**
✅ Story 2.1: Transaction Categorization Engine
✅ Story 2.2: Income & Expense Calculations
✅ Story 2.3: Display Financial Insights with Charts
✅ Story 2.4: Spending Aggregation by Category
✅ Story 2.5: Monthly Trend Analysis

**All 5 Epic 2 stories complete!** Ready for Epic 3: Personalized AI Coaching & Insights.

### File List

**Created:**
- `utils/analytics.py` - Added get_monthly_trends() function
- `views/charts.py` - Added render_monthly_trends_chart() function
- `tests/test_monthly_trends.py` - Monthly trends test suite (24 tests)
- `sample-transactions-multi-month.csv` - Multi-month test data

**Modified:**
- `views/__init__.py` - Added render_monthly_trends_chart export
- `app.py` - Integrated monthly trends section (conditional display for 2+ months)
- `_bmad-output/implementation-artifacts/2-5-monthly-trend-analysis.md` - Status updated to review
