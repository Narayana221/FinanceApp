# Implementation Artifact: Story 4.2 - Export AI-Generated Monthly Plan

## Story Reference

**Epic:** Epic 4 - Data Export & Management  
**Story:** 4.2 - Export AI-Generated Monthly Plan  
**Status:** complete

## Story Summary

As a user, I want to download the AI-generated "Monthly Plan" as a text or Markdown file, so that I can easily review and act on the personalized advice offline or integrate it into my notes.

## Acceptance Criteria

**AC #1:** Text Format Export (REQ-UI-005, FR5, REQ-FO-002, FR39)
- Application provides option to save AI plan in text format
- Export button visible when AI advice is available

**AC #2:** Markdown Format Export (REQ-UI-005, FR5, REQ-FO-002, FR39)
- Application provides option to save AI plan in Markdown format
- Export button visible when AI advice is available

**AC #3:** Complete AI Plan Content (REQ-FO-002, FR39)
- Generated file contains complete AI-generated "Monthly Plan"
- Includes recommendations (3-5 items)
- Includes money habit suggestion (1 item)
- Includes spending leak analysis (1-2 items)
- Formatting preserved

## Requirements Traceability

**Functional Requirements:**
- REQ-UI-005 (FR5): Export AI coaching advice
- REQ-FO-002 (FR39): Text and Markdown export formats

**Non-Functional Requirements:**
- NFR-USABILITY-001 (NFR3): Intuitive export interface

## Technical Design

### Data Flow

```
┌─────────────────────────────────────────┐
│  AI Coach Generates Advice              │
│  (Gemini 2.5 Flash API)                 │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│  Store in Variable: ai_advice_text      │
│  (Markdown formatted text)              │
└────────────────┬────────────────────────┘
                 │
                 ├──────► Display in UI (st.markdown)
                 │
                 ▼
┌─────────────────────────────────────────┐
│  Export Buttons (if advice available)   │
│  TXT  │  MD                             │
└────────┬──────┬─────────────────────────┘
         │      │
         ▼      ▼
    TXT File  MD File
    (Download) (Download)
```

### Implementation in app.py

**Location:** In AI Coach section, after displaying advice

**Code Structure:**
```python
# Initialize AI client
client = GeminiClient()

# Store AI advice in session state for export
ai_advice_text = None

if client.is_configured():
    with st.spinner("💭 Analyzing..."):
        result = client.generate_financial_advice(prompt)
    
    if result['success']:
        ai_advice_text = result['advice']
        
        # Display advice
        st.markdown(ai_advice_text)
        
        # --- Export AI Plan (Story 4.2) ---
        st.markdown("")  # Spacing
        col1, col2 = st.columns(2)
        
        with col1:
            # Export as TXT
            st.download_button(
                label="📝 Download as Text",
                data=ai_advice_text,
                file_name="financeapp_monthly_plan.txt",
                mime="text/plain",
                help="Download AI coaching advice as plain text"
            )
        
        with col2:
            # Export as Markdown
            st.download_button(
                label="📄 Download as Markdown",
                data=ai_advice_text,
                file_name="financeapp_monthly_plan.md",
                mime="text/markdown",
                help="Download AI coaching advice as Markdown"
            )
```

### Export Formats

**Text Format (.txt):**
- Plain text file with markdown syntax preserved
- MIME type: `text/plain`
- Filename: `financeapp_monthly_plan.txt`
- Use case: Quick reference, email, plain text editors

**Sample TXT:**
```
## RECOMMENDATIONS

**Cut Subscriptions** - Save £50/month
You're spending £89 on subscriptions. Review which ones you actually use this month and cancel at least 2-3 that you rarely open. Many people pay for services they forget about, and this is a quick win that doesn't require changing your daily habits. Start with the ones you haven't used in the past 30 days.

**Reduce Eating Out** - Save £100/month
Your eating out spending is £245 this month. Try meal prepping on Sundays...

## MONEY HABIT

Pack lunch 3 days a week instead of buying it. This simple habit could save you around £60 per month...

## SPENDING LEAKS

**Subscriptions (£89/month)** - You have multiple recurring charges...
```

**Markdown Format (.md):**
- Markdown formatted text (same content as TXT)
- MIME type: `text/markdown`
- Filename: `financeapp_monthly_plan.md`
- Use case: Notion, Obsidian, GitHub, rich text editors

**Sample MD:**
(Identical to TXT - AI generates markdown by default)

**Why Both Formats?**
- Different users prefer different tools
- .txt opens in any text editor (universal)
- .md recognized by note-taking apps (richer rendering)
- Same content, different use cases

### Content Structure

**AI Advice Structure (from Story 3.2):**
```markdown
## RECOMMENDATIONS

**Title** - Save £X/month
Full paragraph explaining recommendation (40+ words)...

**Title** - Save £X/month
Full paragraph explaining recommendation (40+ words)...

[3-5 total recommendations]

## MONEY HABIT

Full paragraph explaining simple habit (30+ words)...

## SPENDING LEAKS

**Category (£X/month)** - Explanation (40+ words)...
**Category (£X/month)** - Explanation (40+ words)...
```

All sections preserved in export with formatting intact.

## UI Design

**Placement:** In AI Coach section, immediately after AI advice display

**Conditional Display:**
- Only shown when `result['success'] == True`
- Hidden when API error or no API key
- Hidden when AI unavailable

**Layout:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🤖 AI Cashflow Coach
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## RECOMMENDATIONS
[AI-generated content...]

## MONEY HABIT
[AI-generated content...]

## SPENDING LEAKS
[AI-generated content...]

┌──────────────┐  ┌──────────────┐
│ 📝 Download  │  │ 📄 Download  │
│   as Text    │  │ as Markdown  │
└──────────────┘  └──────────────┘

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**When AI Unavailable:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🤖 AI Cashflow Coach
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ AI Coach currently unavailable. Configure GEMINI_API_KEY...

[No export buttons shown]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Use Cases

**Scenario 1: Notion Integration**
1. User gets AI coaching advice
2. Downloads as Markdown (.md)
3. Pastes into Notion page
4. Markdown headers and formatting render correctly
5. User adds personal notes and tracks progress

**Scenario 2: Email to Accountability Partner**
1. User gets AI coaching advice
2. Downloads as Text (.txt)
3. Opens in email client
4. Copies content to email body
5. Shares financial goals with partner

**Scenario 3: Offline Reference**
1. User gets AI coaching advice
2. Downloads both TXT and MD
3. Saves to Dropbox/Google Drive
4. Reviews advice throughout month without re-running app

**Scenario 4: Monthly Archive**
1. User runs app monthly
2. Downloads Markdown each time
3. Saves with date: `2025-01-monthly-plan.md`
4. Tracks progress over time by comparing monthly files

## Error Handling

**No Export When:**
- AI key not configured → No buttons shown
- API error → No buttons shown
- API timeout → No buttons shown
- Response truncated → Buttons shown (user can export partial response with warning)

**User Experience:**
- Export only available when advice successfully generated
- If AI fails, user can still export processed data (Story 4.1)
- Clear messaging when AI unavailable

## Files Modified

**Modified:**
- `app.py` - Added export buttons in AI Coach section (~20 lines)

**No new files created** - Leverages existing Streamlit components

## Testing Strategy

### Manual Testing

**Test Case 1: Text Export**
1. Upload valid CSV with API key configured
2. Wait for AI advice to generate
3. Click "Download as Text" button
4. **Expected:**
   - Browser downloads `financeapp_monthly_plan.txt`
   - File contains complete AI advice
   - Opens in any text editor
   - Markdown syntax visible (##, **)

**Test Case 2: Markdown Export**
1. Upload valid CSV with API key configured
2. Wait for AI advice to generate
3. Click "Download as Markdown" button
4. **Expected:**
   - Browser downloads `financeapp_monthly_plan.md`
   - File contains complete AI advice
   - Opens in Markdown editor with proper rendering
   - Headers, bold text formatted correctly

**Test Case 3: Content Completeness**
1. Generate AI advice
2. Export as both TXT and MD
3. **Expected:**
   - Both files identical
   - All sections present (Recommendations, Money Habit, Spending Leaks)
   - All recommendations included (3-5 items)
   - Formatting preserved

**Test Case 4: No API Key**
1. Remove API key from .env
2. Upload CSV
3. **Expected:**
   - AI Coach shows warning
   - No export buttons visible
   - Data export (Story 4.1) still works

**Test Case 5: API Error**
1. Set invalid API key
2. Upload CSV
3. **Expected:**
   - AI Coach shows error message
   - No export buttons visible
   - App continues to work

**Test Case 6: Truncated Response**
1. Generate advice that triggers truncation warning
2. Export as TXT
3. **Expected:**
   - File contains partial advice
   - Truncation warning included in export
   - User aware response is incomplete

### Integration Testing

**Existing Tests Cover:**
- AI advice generation (Story 3.1 tests)
- Prompt building (Story 3.2 tests)
- Display logic (Story 3.3 integration)
- Export uses ai_advice_text variable
- No additional unit tests needed (Streamlit download_button is framework code)

## Definition of Done

- [x] Export buttons added to AI Coach section
- [x] Text download button implemented
- [x] Markdown download button implemented
- [x] Export only shown when AI advice available
- [x] Both exports contain complete AI plan
- [x] Filenames are descriptive and consistent
- [x] MIME types correctly set
- [x] Tooltips provide helpful information
- [x] Two-column layout for side-by-side buttons
- [x] Conditional display logic works correctly
- [x] Manual testing completed
- [x] Code follows existing project structure
- [x] Documentation complete

## Dev Agent Record

### Implementation Status

**Status:** Complete

**Implementation Date:** 2026-01-10

**Files Modified:**
- `app.py` - Added export buttons in AI Coach section (~20 lines)

**Implementation Details:**
- Added `ai_advice_text` variable to capture AI response
- Used Streamlit's `st.download_button()` for TXT and MD exports
- Export buttons placed after `st.markdown(ai_advice_text)`
- Two-column layout for side-by-side buttons
- Conditional display: only shown when `result['success'] == True`
- Descriptive filenames and tooltips

**Design Decisions:**
1. **Both TXT and MD export same content:** AI generates markdown by default, users choose format based on their preferred tools
2. **Placement after advice:** Keeps export buttons close to content they export
3. **Conditional display:** Prevents confusion when AI unavailable
4. **No session state:** Uses local variable to avoid state management complexity

### Completion Notes

**Simple Implementation:**
Story 4.2 required minimal code (~20 lines) because:
1. AI advice already generated as markdown text
2. Streamlit's `st.download_button()` handles file download UX
3. No data transformation needed (export raw markdown)
4. Conditional logic straightforward (`if result['success']`)

**Quality Attributes:**
- **Usability (NFR-USABILITY-001):** Intuitive export buttons ✅
- **Functionality:** Complete AI plan exported ✅
- **Conditional UX:** Only shown when relevant ✅

**User Value:**
- Enables offline review of AI advice
- Supports various note-taking workflows (Notion, Obsidian, etc.)
- Allows monthly progress tracking
- Facilitates sharing with accountability partners

**Recommendation:** Mark Story 4.2 as complete. Epic 4 complete. Proceed to Epic 5 or wrap up.
