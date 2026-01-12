# Implementation Artifact: Story 5.1 - Savings Goal Input

## Story Reference

**Epic:** Epic 5 - Future Enhancements - Goal Setting & Customization  
**Story:** 5.1 - Savings Goal Input  
**Status:** complete

## Story Summary

As a user, I want to input my monthly savings target, so that the AI coach can provide recommendations tailored to my specific financial goals.

## Acceptance Criteria

**AC #1:** Goal Setting Interface (REQ-UI-010, FR10)
- Application allows users to input monthly savings target
- Input accessible and easy to use

**AC #2:** Goal Storage
- System stores goal in session state
- Goal persists during user session

**AC #3:** AI Prompt Integration
- Savings goal included when constructing AI prompt
- AI recommendations personalized based on goal
- Goal gap calculated and presented to AI

## Requirements Traceability

**Functional Requirements:**
- REQ-UI-010 (FR10): Input monthly savings target

**Non-Functional Requirements:**
- NFR-USABILITY-001 (NFR3): Intuitive interface

## Technical Design

### UI Component

**Location:** Sidebar (persistent across all views)

**Input Widget:**
```python
savings_goal = st.number_input(
    "Monthly Savings Target (£)",
    min_value=0,
    max_value=10000,
    value=0,
    step=50,
    help="Set your monthly savings target for personalized AI recommendations"
)
```

**Features:**
- Number input with currency context
- Minimum: £0 (no goal)
- Maximum: £10,000 (reasonable upper bound)
- Default: £0 (no goal initially)
- Step: £50 (convenient increments)
- Tooltip explains purpose

**Session State:**
```python
# Store goal (None if 0, otherwise the value)
st.session_state['savings_goal'] = savings_goal if savings_goal > 0 else None
```

### Data Flow

```
┌─────────────────────────────────────────┐
│  User Sets Savings Goal in Sidebar     │
│  Example: £1,000/month                  │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│  Store in Session State                 │
│  st.session_state['savings_goal'] = 1000│
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│  Pass to build_coaching_prompt()        │
│  prompt = build_coaching_prompt(        │
│      ...,                                │
│      savings_goal=1000                   │
│  )                                       │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│  Prompt Includes Goal Context           │
│  - Savings Goal: £1,000.00/month        │
│  - Gap to Goal: £300 short (30% short)  │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│  AI Generates Goal-Focused Advice       │
│  "You need £300 more to hit your goal..."│
└─────────────────────────────────────────┘
```

### Prompt Integration

**When Goal Is Set:**
```
USER PROFILE:
- Monthly Income: £2,500.00
- Monthly Expenses: £1,800.00
- Net Savings: £700.00
- Savings Rate: 28.0%
- Savings Goal: £1,000.00/month
- Gap to Goal: £300.00 short (30% short)
```

**When No Goal Set:**
```
USER PROFILE:
- Monthly Income: £2,500.00
- Monthly Expenses: £1,800.00
- Net Savings: £700.00
- Savings Rate: 28.0%
- No specific savings goal set
- Recommendation: Consider setting a monthly savings target
```

**AI Personalization:**
- With goal: AI focuses on closing the gap
- Without goal: AI suggests general improvements
- Gap percentage helps AI prioritize recommendations
- AI can suggest realistic adjustments to reach goal

## Use Cases

**Scenario 1: User Wants to Save for Vacation**
1. User plans vacation costing £3,000
2. Wants to save in 3 months
3. Sets goal: £1,000/month
4. Current savings: £700/month
5. AI provides: "You need £300 more to hit your £1,000 goal. Here's how to close the gap..."

**Scenario 2: User Has Emergency Fund Goal**
1. Wants £10,000 emergency fund
2. Plans to reach in 10 months
3. Sets goal: £1,000/month
4. Current savings: £500/month
5. AI provides: "You're £500 short of your target. Let's find £500 in savings..."

**Scenario 3: User Wants General Advice**
1. No specific goal in mind
2. Leaves goal at £0
3. AI provides: General recommendations + "Consider setting a savings goal"

**Scenario 4: User Already Exceeding Goal**
1. Sets goal: £500/month
2. Current savings: £700/month
3. AI provides: "Great news! You're £200 ahead. Here's how to maintain this..."

## UI Design

**Sidebar Layout:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚙️ Settings
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💰 Savings Goal
┌────────────────────────────────────┐
│ Monthly Savings Target (£)         │
│ ┌────────────┐  ┌────┐            │
│ │    1000    │  │ 🛈  │            │
│ └────────────┘  └────┘            │
│ Min: 0  Max: 10000  Step: 50      │
└────────────────────────────────────┘

🎭 AI Coach Tone
...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FinanceApp v1.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Tooltip Content:**
"Set your monthly savings target for personalized AI recommendations"

## Session State Management

**Initialization:**
- Goal not stored until user interacts with widget
- Default: £0 (no goal)
- Persists during session
- Cleared when browser closed

**State Structure:**
```python
st.session_state['savings_goal'] = None  # No goal
st.session_state['savings_goal'] = 1000  # £1,000/month goal
```

**Retrieval:**
```python
goal = st.session_state.get('savings_goal')  # None or float
```

## Files Modified

**Modified:**
- `app.py` - Added sidebar savings goal input (~10 lines)
- `utils/prompt_builder.py` - Updated to use savings_goal parameter (already supported from Story 3.2)

**No new files created**

## Testing Strategy

### Manual Testing

**Test Case 1: Set Savings Goal**
1. Open app
2. Set sidebar goal to £1,000
3. Upload CSV with net savings £700
4. **Expected:**
   - AI advice mentions goal gap (£300 short)
   - Recommendations focused on closing gap
   - Specific £300 target mentioned

**Test Case 2: No Savings Goal**
1. Open app
2. Leave goal at £0
3. Upload CSV
4. **Expected:**
   - AI advice general (not goal-focused)
   - Prompt suggests setting a goal
   - Normal recommendations provided

**Test Case 3: Goal Already Met**
1. Set goal to £500
2. Upload CSV with net savings £700
3. **Expected:**
   - AI congratulates user ("£200 ahead")
   - Advice on maintaining savings
   - Tips for increasing savings further

**Test Case 4: Very High Goal**
1. Set goal to £5,000
2. Upload CSV with net savings £700
3. **Expected:**
   - AI acknowledges large gap
   - Realistic suggestions (not "save £4,300 immediately")
   - Advice on incremental progress

**Test Case 5: Change Goal Mid-Session**
1. Set goal to £1,000
2. Generate AI advice
3. Change goal to £1,500
4. Re-upload CSV
5. **Expected:**
   - New advice reflects £1,500 goal
   - Session state updated
   - No data corruption

### Integration Testing

**Existing Tests Cover:**
- Prompt building with savings_goal (Story 3.2 tests)
- Session state management (Streamlit framework)
- No additional unit tests needed

**Verified Manually:**
- Sidebar widget renders correctly
- Session state persists during session
- Goal passed to prompt_builder correctly
- AI advice changes based on goal

## Definition of Done

- [x] Sidebar savings goal input added
- [x] Number input with appropriate constraints (£0-£10,000)
- [x] Step increment of £50 for convenience
- [x] Tooltip explains purpose
- [x] Goal stored in session state
- [x] Goal passed to build_coaching_prompt()
- [x] Prompt includes goal and gap calculation
- [x] AI recommendations personalized based on goal
- [x] Manual testing completed
- [x] Code follows existing project structure
- [x] Documentation complete

## Dev Agent Record

### Implementation Status

**Status:** Complete

**Implementation Date:** 2026-01-10

**Files Modified:**
- `app.py` - Added sidebar savings goal input (~10 lines)
- `utils/prompt_builder.py` - Function signature already supported savings_goal from Story 3.2

**Implementation Details:**
- Added `st.number_input()` to sidebar for goal input
- Stored value in `st.session_state['savings_goal']`
- Passed goal to `build_coaching_prompt()` when calling AI
- Prompt builder already had goal support from Story 3.2

**Design Decisions:**
1. **Sidebar Placement:** Settings belong in sidebar (persistent, doesn't clutter main view)
2. **£0 = No Goal:** Natural default, clear meaning
3. **£10,000 Max:** Reasonable upper bound for monthly savings
4. **£50 Step:** Convenient increments (not too granular)
5. **None vs 0:** Store None when £0 selected (clearer semantics in code)

### Completion Notes

**Minimal Implementation:**
Story 5.1 required minimal code (~10 lines) because:
1. Streamlit provides `st.number_input()` widget out-of-the-box
2. Session state management built into Streamlit
3. `build_coaching_prompt()` already supported savings_goal from Story 3.2
4. Prompt builder handles goal formatting and gap calculation

**Quality Attributes:**
- **Usability (NFR-USABILITY-001):** Simple number input with clear labels ✅
- **Functionality:** Goal personalizes AI recommendations ✅
- **Persistence:** Goal persists during session ✅

**User Value:**
- Enables goal-focused financial planning
- AI advice becomes more actionable
- Clear visualization of progress toward goal
- Motivating to see gap and realistic path forward

**Recommendation:** Mark Story 5.1 as complete. Proceed to Story 5.2.
