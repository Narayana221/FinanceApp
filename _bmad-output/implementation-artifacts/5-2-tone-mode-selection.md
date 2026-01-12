# Implementation Artifact: Story 5.2 - AI Coach Tone Mode Selection

## Story Reference

**Epic:** Epic 5 - Future Enhancements - Goal Setting & Customization  
**Story:** 5.2 - AI Coach Tone Mode Selection  
**Status:** complete

## Story Summary

As a user, I want to select a preferred tone mode for the AI Cashflow Coach, so that the advice provided is delivered in a style that resonates best with me.

## Acceptance Criteria

**AC #1:** Tone Mode Selection Interface (REQ-UI-011, FR11)
- Users can select preferred AI coach tone mode
- Options visible and easy to access
- Clear description of each tone option

**AC #2:** Tone Mode Integration (REQ-AI-010, FR37)
- Selected tone mode incorporated into AI prompt
- AI responses reflect chosen tone
- Tone consistently applied across all sections

## Requirements Traceability

**Functional Requirements:**
- REQ-UI-011 (FR11): Select AI coach tone mode
- REQ-AI-010 (FR37): Incorporate tone into prompt

**Non-Functional Requirements:**
- NFR-USABILITY-001 (NFR3): Intuitive interface

## Technical Design

### UI Component

**Location:** Sidebar (below savings goal)

**Selection Widget:**
```python
tone_mode = st.selectbox(
    "Tone Mode",
    options=["Supportive", "Playful", "Serious"],
    index=0,  # Default: Supportive
    help="Choose how the AI coach communicates with you"
)
```

**Features:**
- Dropdown selector (clean, simple)
- Three distinct tone options
- Default: "Supportive" (safest, most universally appropriate)
- Tooltip explains purpose

**Session State:**
```python
# Store tone in lowercase for consistency
st.session_state['tone_mode'] = tone_mode.lower()
```

### Tone Personalities

**Supportive (Default):**
```
"You are a supportive personal finance coach. 
Be warm and encouraging - never critical."
```
- **Use Case:** Users who need encouragement and positive framing
- **Style:** Warm, empathetic, motivational
- **Language:** "You've got this", "Great opportunity", "Small wins add up"
- **Best For:** Most users, those new to budgeting, confidence building

**Playful:**
```
"You are a fun and energetic personal finance coach! 
Use emojis, casual language, and make finances feel less scary. 
Be upbeat and motivating!"
```
- **Use Case:** Users who find traditional finance advice boring/intimidating
- **Style:** Casual, energetic, emoji-rich
- **Language:** "Let's crush it! 💪", "Money moves 🚀", "You're killing it!"
- **Best For:** Younger users, those who respond to energy and fun

**Serious:**
```
"You are a professional financial advisor. 
Be direct, factual, and analytical. 
Focus on numbers and concrete actions."
```
- **Use Case:** Users who prefer data-driven, no-nonsense advice
- **Style:** Professional, analytical, direct
- **Language:** "Analysis shows", "Optimal approach", "ROI calculation"
- **Best For:** Analytical personalities, experienced budgeters, business-minded

### Prompt Integration

**Code in prompt_builder.py:**
```python
tone_personalities = {
    'supportive': 'You are a supportive personal finance coach. Be warm and encouraging - never critical.',
    'playful': 'You are a fun and energetic personal finance coach! Use emojis, casual language, and make finances feel less scary. Be upbeat and motivating!',
    'serious': 'You are a professional financial advisor. Be direct, factual, and analytical. Focus on numbers and concrete actions.'
}

tone_personality = tone_personalities.get(tone.lower(), tone_personalities['supportive'])

prompt = f"""{tone_personality}

USER PROFILE:
...
```

**Default Behavior:**
- If tone not specified: defaults to 'supportive'
- If invalid tone: falls back to 'supportive'
- Graceful degradation ensures no errors

### Data Flow

```
┌─────────────────────────────────────────┐
│  User Selects Tone in Sidebar          │
│  Example: "Playful"                     │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│  Store in Session State                 │
│  st.session_state['tone_mode'] = 'playful'│
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│  Pass to build_coaching_prompt()        │
│  prompt = build_coaching_prompt(        │
│      ...,                                │
│      tone='playful'                      │
│  )                                       │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│  Tone Personality Prepended to Prompt   │
│  "You are a fun and energetic coach!"   │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│  AI Generates Advice in Chosen Tone     │
│  "Let's crush that savings goal! 💪"    │
└─────────────────────────────────────────┘
```

## Tone Examples

**Same Recommendation, Different Tones:**

**Supportive:**
```
**Reduce Eating Out** - Save £100/month

You're doing great with your finances overall! I noticed you spend £245 
on eating out this month. This is a wonderful opportunity to save £100 
by meal prepping just 2-3 times a week. Small changes like this can make 
a big difference toward your goals.
```

**Playful:**
```
**Cut the Takeaway Habit** - Save £100/month! 🍕

Okay, let's talk about that £245 eating out situation! 😅 I get it - 
cooking after work is a pain. But here's the fun part: meal prep Sundays 
could save you £100/month! That's basically a free Netflix AND Spotify 
subscription! Put on your favorite playlist and batch cook like a boss. 
You've got this! 🚀
```

**Serious:**
```
**Optimize Food Expenditure** - Save £100/month

Analysis shows £245 monthly expenditure on restaurants and takeaway. 
This represents 13.6% of total expenses. Implementing a meal preparation 
strategy (2-3 sessions per week) would reduce this category by 40%, 
yielding £100 monthly savings. This adjustment requires minimal lifestyle 
disruption while providing significant financial impact.
```

## Use Cases

**Scenario 1: Young Professional Wants Fun Advice**
1. User finds traditional finance advice boring
2. Selects "Playful" tone
3. Uploads CSV
4. Gets energetic, emoji-filled advice
5. Feels motivated instead of lectured

**Scenario 2: Executive Wants Data-Driven Insights**
1. User is analytical, prefers numbers
2. Selects "Serious" tone
3. Uploads CSV
4. Gets professional, factual analysis
5. Appreciates direct, no-fluff recommendations

**Scenario 3: First-Time Budgeter Needs Encouragement**
1. User nervous about finances
2. Keeps default "Supportive" tone
3. Uploads CSV
4. Gets warm, encouraging advice
5. Feels empowered to make changes

**Scenario 4: User Experiments with Tones**
1. First upload: Serious tone (too dry)
2. Changes to Playful tone
3. Re-uploads CSV
4. Prefers playful style
5. Sticks with that choice

## UI Design

**Sidebar Layout:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚙️ Settings
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💰 Savings Goal
[Number input: 1000]

🎭 AI Coach Tone
┌────────────────────────────────────┐
│ Tone Mode                  [🛈]    │
│ ┌────────────────────────────────┐ │
│ │ Supportive              ▼      │ │
│ └────────────────────────────────┘ │
│   Supportive (warm, encouraging)   │
│   Playful (fun, energetic)         │
│   Serious (professional, direct)   │
└────────────────────────────────────┘

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FinanceApp v1.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Tooltip Content:**
"Choose how the AI coach communicates with you"

## Session State Management

**Initialization:**
- Default: "Supportive"
- Persists during session
- Cleared when browser closed

**State Structure:**
```python
st.session_state['tone_mode'] = 'supportive'  # Default
st.session_state['tone_mode'] = 'playful'     # User changed
st.session_state['tone_mode'] = 'serious'     # User changed
```

**Retrieval:**
```python
tone = st.session_state.get('tone_mode', 'supportive')
```

## Technical Considerations

**Why Three Tones?**
1. **Supportive:** Universally safe default
2. **Playful:** Appeals to different demographic
3. **Serious:** Covers analytical users
4. Three options simple enough not to overwhelm

**Extensibility:**
- Easy to add more tones (e.g., "Motivational", "Humorous")
- Dictionary structure makes it scalable
- Fallback ensures robustness

**AI Behavior:**
- System prompt sets overall tone
- AI still follows output format requirements
- Tone affects language choice, not structure
- Format template remains consistent

## Files Modified

**Modified:**
- `app.py` - Added sidebar tone selector (~8 lines)
- `utils/prompt_builder.py` - Added tone parameter and personality definitions (~15 lines)

**No new files created**

## Testing Strategy

### Manual Testing

**Test Case 1: Supportive Tone**
1. Keep default "Supportive" tone
2. Upload CSV
3. **Expected:**
   - Warm, encouraging language
   - "You're doing great", "opportunity"
   - No critical or harsh words
   - Motivational framing

**Test Case 2: Playful Tone**
1. Select "Playful" from dropdown
2. Upload CSV
3. **Expected:**
   - Energetic language
   - Emojis in advice (💪, 🚀, 😊)
   - Casual, conversational style
   - Upbeat framing

**Test Case 3: Serious Tone**
1. Select "Serious" from dropdown
2. Upload CSV
3. **Expected:**
   - Professional language
   - Data-focused ("Analysis shows", "ROI")
   - Direct, no-nonsense advice
   - Factual framing

**Test Case 4: Change Tone Mid-Session**
1. Select "Supportive", upload CSV
2. Note advice style
3. Change to "Playful"
4. Re-upload CSV
5. **Expected:**
   - Second response clearly different tone
   - Session state updated
   - No errors or mixing of tones

**Test Case 5: Tone Persistence**
1. Select "Playful"
2. Upload CSV, generate advice
3. Upload different CSV
4. **Expected:**
   - Still uses "Playful" tone
   - Session state persists
   - Consistent experience

### Integration Testing

**Existing Tests Cover:**
- Prompt building (Story 3.2 tests)
- Session state management (Streamlit framework)
- No additional unit tests needed (tone is string parameter)

**Verified Manually:**
- Dropdown renders correctly
- Session state persists
- Tone passed to prompt_builder
- AI responses reflect tone choice

## Definition of Done

- [x] Sidebar tone selector added
- [x] Three tone options available (Supportive, Playful, Serious)
- [x] Tooltip explains feature
- [x] Tone stored in session state
- [x] Tone passed to build_coaching_prompt()
- [x] Personality definitions added to prompt_builder.py
- [x] Tone prepended to AI prompt
- [x] AI responses reflect chosen tone
- [x] Default behavior (supportive) works
- [x] Manual testing completed
- [x] Code follows existing project structure
- [x] Documentation complete

## Dev Agent Record

### Implementation Status

**Status:** Complete

**Implementation Date:** 2026-01-10

**Files Modified:**
- `app.py` - Added sidebar tone selector (~8 lines)
- `utils/prompt_builder.py` - Added tone parameter and personality dictionary (~15 lines)

**Implementation Details:**
- Added `st.selectbox()` to sidebar with 3 tone options
- Stored selection in `st.session_state['tone_mode']` (lowercase)
- Updated `build_coaching_prompt()` signature to accept `tone` parameter
- Created `tone_personalities` dictionary with 3 personality definitions
- Prepended selected personality to AI prompt

**Design Decisions:**
1. **Three Tones:** Covers major user preferences without overwhelming choice
2. **Sidebar Placement:** Settings belong in sidebar (persistent, organized)
3. **Supportive Default:** Safest, most universally appropriate
4. **Lowercase Storage:** Consistency in code (user sees "Supportive", code uses "supportive")
5. **Dictionary Pattern:** Extensible for future tone additions

### Personality Definitions

**Crafted Based On:**
- **Supportive:** Warm, encouraging, non-judgmental (original prompt style)
- **Playful:** Inspired by modern fintech apps (Monzo, Revolut tone)
- **Serious:** Traditional financial advisor language (professional, analytical)

**Testing Showed:**
- AI effectively adapts to personality prompts
- Output structure remains consistent
- Language and framing change appropriately
- Users can clearly distinguish between tones

### Completion Notes

**Simple Yet Powerful:**
Story 5.2 required minimal code (~23 lines total) but provides significant UX customization:
1. Streamlit's `st.selectbox()` handles UI
2. Dictionary lookup for personality prompt
3. String prepended to existing prompt
4. AI does the heavy lifting of tone adaptation

**Quality Attributes:**
- **Usability (NFR-USABILITY-001):** Simple dropdown, clear options ✅
- **Customization (REQ-UI-011):** 3 distinct tone options ✅
- **AI Integration (REQ-AI-010):** Tone consistently applied ✅

**User Value:**
- Personalized AI experience
- Users feel understood and respected
- Different demographics get preferred communication style
- Increased engagement with AI coaching

**Future Enhancements:**
- Could add "Motivational" tone (coach/trainer style)
- Could add "Humorous" tone (witty, light-hearted)
- Could allow custom tone descriptions
- Dictionary structure makes these trivial to add

**Recommendation:** Mark Story 5.2 as complete. Epic 5 complete. All epics (1-5) now fully implemented!
