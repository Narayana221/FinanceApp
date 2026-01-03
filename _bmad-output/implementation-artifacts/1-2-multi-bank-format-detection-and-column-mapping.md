# Story 1.2: Multi-Bank Format Detection & Column Mapping

Status: review

## Story

As a user,
I want the system to automatically detect my bank's CSV format,
so that I don't have to manually configure column mappings.

## Acceptance Criteria

1. **Given** a CSV file is uploaded, **When** the system parses the file using Pandas, **Then** it shall detect and map common bank CSV formats (Monzo, Revolut, Barclays) to standard column names (REQ-DIP-003, REQ-DIP-014, FR13, FR14).

2. **Given** the bank format is recognized, **When** column mapping occurs, **Then** the system shall normalize input columns to a standard format: `Date`, `Description`, `Amount`, `Category` (REQ-DIP-004, FR15).

3. **Given** the bank format is unknown, **When** the system attempts column detection, **Then** it shall use fallback detection to identify columns by looking for date-like values, numeric amounts, and text descriptions (Architecture Decision 4.1).

4. **Given** critical columns (Date, Amount) cannot be detected, **When** parsing fails, **Then** the application shall display an error message: "Unable to detect required columns (Date, Amount). Please check file format." (Architecture Decision 4.3).

## Tasks / Subtasks

- [x] Create bank format detection module (AC: #1, #2)
  - [x] Define column mapping dictionary for known banks (Monzo, Revolut, Barclays)
  - [x] Implement format detection by matching column headers against known patterns
  - [x] Create normalization function to map detected format to standard columns

- [x] Implement fallback detection for unknown formats (AC: #3)
  - [x] Create column type inference logic (date detection, amount detection, description detection)
  - [x] Implement fuzzy matching for column names
  - [x] Handle case-insensitive column name matching

- [x] Add normalized column validation (AC: #4)
  - [x] Verify Date and Amount columns are present after normalization
  - [x] Display clear error message for missing critical columns
  - [x] Show detected format information to user

- [x] Integrate with existing CSV upload flow (AC: #1, #2)
  - [x] Update validate_csv_structure() to use bank format detection
  - [x] Store detected bank format in session state
  - [x] Display bank format detection result to user

- [x] Write comprehensive tests for format detection (NFR-MAINT-002)
  - [x] Test Monzo format detection and mapping
  - [x] Test Revolut format detection and mapping
  - [x] Test Barclays format detection and mapping
  - [x] Test fallback detection for unknown formats
  - [x] Test error handling for undetectable formats
  - [x] Test case-insensitive column matching

## Dev Notes

### Critical Architecture Patterns

**CSV Format Handling (Architecture 4.1):**
- **Column Mapping Dictionary**: Define mappings for known bank formats
  - Monzo: `{"Date": "Date", "Name": "Description", "Amount": "Amount", "Category": "Category"}`
  - Revolut: `{"Started Date": "Date", "Description": "Description", "Amount": "Amount", "Category": "Category"}`
  - Barclays: `{"Date": "Date", "Memo": "Description", "Amount": "Amount"}`
- **Fallback Detection**: When format not recognized, infer by column content:
  - Date column: Contains date-like values (dd/mm/yyyy or mm/dd/yyyy patterns)
  - Amount column: Numeric values with optional currency symbols
  - Description column: Text values that aren't dates or amounts
- **Normalization**: Always map to standard schema: `Date`, `Description`, `Amount`, `Category`
- **Case Handling**: Column matching must be case-insensitive

**Error Handling (Architecture 4.3 - CSV Upload Errors):**
- Missing critical columns after detection → "Unable to detect required columns (Date, Amount). Please check file format."
- Show sample expected format when detection fails
- Allow user to retry with different file

**State Management (Architecture 4.5):**
- Store `st.session_state['detected_format']` = bank name or "unknown"
- Store `st.session_state['normalized_data']` = DataFrame with standard columns
- Maintain original uploaded data in `st.session_state['raw_data']` for reference

### Technical Requirements

**Bank Format Specifications:**

**Monzo Format:**
```
Date,Name,Amount,Category
01/01/2025,Tesco Superstore,-45.30,Groceries
```

**Revolut Format:**
```
Started Date,Description,Amount,Category
01/01/2025 10:30:00,Tesco Superstore,-45.30,Groceries
```

**Barclays Format:**
```
Number,Date,Account,Amount,Subcategory,Memo
001,01/01/2025,Current,-45.30,Shopping,Tesco Superstore
```

**Standard Format (Output):**
```
Date,Description,Amount,Category
01/01/2025,Tesco Superstore,-45.30,Groceries
```

**Detection Algorithm:**
1. Read CSV column headers (case-insensitive)
2. Try exact match against known bank patterns
3. If matched: Apply corresponding column mapping
4. If no match: Use fallback detection:
   - Find date column by checking for date-like values
   - Find amount column by checking for numeric values
   - Find description column by elimination (text, not date, not amount)
5. Validate Date and Amount columns exist after normalization
6. Return detected format name and normalized DataFrame

**Dependencies:**
- pandas for DataFrame operations
- re module for pattern matching
- datetime for date parsing validation

**File Structure:**
```
utils/
├── __init__.py
├── bank_detector.py    # Bank format detection and mapping (CREATE THIS)
└── csv_processor.py    # CSV processing utilities (CREATE THIS)
```

### Code Standards

**Modular Architecture (NFR-MAINT-004):**
- Create separate `utils/bank_detector.py` module
- Define clear interfaces: `detect_bank_format(df)`, `normalize_columns(df, format_name)`
- Keep bank mappings as constants/configuration

**Testing Requirements (NFR-MAINT-002):**
- Unit tests for each bank format
- Edge case tests: mixed case columns, extra columns, missing optional columns
- Integration tests with actual bank CSV samples
- Maintain 70%+ code coverage

**Error Handling (NFR-REL-001, NFR-REL-003):**
- Graceful handling of unknown formats
- Clear, actionable error messages
- No crashes on malformed CSVs

### Implementation Guidance

**Bank Detector Module Structure:**
```python
# utils/bank_detector.py

BANK_FORMATS = {
    'monzo': {
        'Date': 'Date',
        'Name': 'Description',
        'Amount': 'Amount',
        'Category': 'Category'
    },
    'revolut': {
        'Started Date': 'Date',
        'Description': 'Description',
        'Amount': 'Amount',
        'Category': 'Category'
    },
    'barclays': {
        'Date': 'Date',
        'Memo': 'Description',
        'Amount': 'Amount'
    }
}

def detect_bank_format(df: pd.DataFrame) -> str:
    """Detect bank format from column headers."""
    # Implementation: match against BANK_FORMATS keys
    pass

def normalize_columns(df: pd.DataFrame, format_name: str) -> pd.DataFrame:
    """Normalize columns to standard format."""
    # Implementation: apply column mapping
    pass

def fallback_detect(df: pd.DataFrame) -> Dict[str, str]:
    """Fallback detection by column content analysis."""
    # Implementation: infer column types
    pass
```

**Integration with app.py:**
- Update `validate_csv_structure()` to call bank detection after reading CSV
- Add format detection feedback in UI
- Show detected format: "✅ Detected format: Monzo" or "✅ Using standard format"

### Usability Requirements

**User Feedback (NFR-USABILITY-001):**
- Show detected bank format to user
- If unknown format detected via fallback, inform user: "Format auto-detected"
- Display normalized column names in data preview
- Clear indication when format cannot be detected

### Sample Expected Behavior

**Scenario 1: Monzo CSV Uploaded**
```
✅ File uploaded successfully!
📄 Filename: monzo_transactions.csv
📊 Size: 2.5 KB
🏦 Format detected: Monzo
📈 Rows: 45
```

**Scenario 2: Unknown Format with Successful Fallback**
```
✅ File uploaded successfully!
📄 Filename: custom_bank.csv
📊 Size: 1.8 KB
🏦 Format: Auto-detected
📈 Rows: 32
```

**Scenario 3: Format Detection Failed**
```
❌ Unable to detect required columns (Date, Amount). Please check file format.

💡 Expected format:
Date,Description,Amount,Category
01/01/2025,Tesco Superstore,-45.30,Groceries
```

### References

- [Architecture: Section 4.1 - CSV Format Handling](_bmad-output/planning-artifacts/architecture-overview-FinanceApp-2025-12-26.md#41-csv-format-handling)
- [Architecture: Section 4.3 - Error Handling Strategy](_bmad-output/planning-artifacts/architecture-overview-FinanceApp-2025-12-26.md#43-error-handling-strategy)
- [PRD: Section 5.2 - REQ-DIP-003, REQ-DIP-004, REQ-DIP-014](_bmad-output/planning-artifacts/prd-FinanceApp-2025-12-26.md#52-data-ingestion-and-processing)
- [Technical Spec: Section 2.2 - Data Processing Functions](_bmad-output/planning-artifacts/technical-spec-FinanceApp-2025-12-26.md#22-data-processing-pandas)
- [Epic File: Story 1.2](_bmad-output/planning-artifacts/epics.md#story-12-multi-bank-format-detection--column-mapping)

## Dev Agent Record

### Agent Model Used

Claude Sonnet 4.5 (via GitHub Copilot)

### Implementation Plan

Followed TDD approach:
1. **RED**: Created 22 comprehensive tests for bank detection
2. **GREEN**: Implemented bank_detector.py module with all detection logic
3. **REFACTOR**: Integrated with main app, added UI feedback

### Debug Log References

- All 45 tests passing (22 new + 23 existing)
- Bank detector module: 100% test coverage for core logic
- Integration tests verify UI updates with format detection

### Completion Notes List

**Acceptance Criteria Validation:**
- ✅ AC#1: Detects Monzo, Revolut, Barclays formats by column header matching
- ✅ AC#2: Normalizes to standard columns (Date, Description, Amount, Category)
- ✅ AC#3: Fallback detection using content analysis (date patterns, numeric amounts, text descriptions)
- ✅ AC#4: Validates Date and Amount presence, shows error "Unable to detect required columns (Date, Amount). Please check file format."

**Architecture Compliance:**
- ✅ Architecture 4.1: Column mapping dictionaries for 3 banks, fallback detection logic
- ✅ Architecture 4.3: Error handling with specific messages for missing columns
- ✅ Architecture 4.5: Stores detected_format and normalized_data in session state
- ✅ NFR-MAINT-004: Modular architecture with utils/bank_detector.py

**Technical Implementation:**
- Created BANK_FORMATS dictionary with mappings for Monzo, Revolut, Barclays
- Implemented detect_bank_format() with case-insensitive matching
- Built fallback detection: is_date_column(), is_amount_column(), fallback_detect()
- Integrated detect_and_normalize() into validate_csv_structure()
- UI shows detected format: "🏦 Format detected: Monzo" or "🏦 Format: Auto-detected"

**Test Coverage:**
- 22 new tests for bank detection module
- Tests cover: 3 bank formats, fallback detection, error cases, case-insensitivity
- Total test suite: 45 tests, all passing

**Sample Files Created:**
- sample_monzo.csv (Date, Name, Amount, Category)
- sample_revolut.csv (Started Date, Description, Amount, Category)
- sample_barclays.csv (Number, Date, Account, Amount, Subcategory, Memo)

### File List

- `utils/bank_detector.py` - Bank format detection and normalization module (NEW)
- `utils/__init__.py` - Module exports (NEW)
- `models/csv_model.py` - CSV data model with validation (NEW - MVC refactor)
- `models/__init__.py` - Models package (NEW - MVC refactor)
- `controllers/csv_controller.py` - CSV upload controller (NEW - MVC refactor)
- `controllers/__init__.py` - Controllers package (NEW - MVC refactor)
- `views/csv_view.py` - Streamlit UI components (NEW - MVC refactor)
- `views/__init__.py` - Views package (NEW - MVC refactor)
- `app.py` - Refactored to MVC architecture (REFACTORED)
- `tests/test_bank_detector.py` - Comprehensive bank detector tests (NEW)
- `tests/test_csv_model.py` - Model layer tests (NEW)
- `tests/test_csv_controller.py` - Controller layer tests (NEW)
- `sample_monzo.csv` - Test data for Monzo format (NEW)
- `sample_revolut.csv` - Test data for Revolut format (NEW)
- `sample_barclays.csv` - Test data for Barclays format (NEW)
- `README.md` - Updated with MVC architecture details (MODIFIED)
