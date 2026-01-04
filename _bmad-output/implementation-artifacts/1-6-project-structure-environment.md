# Story 1.6: Setup Project Structure & Environment Configuration

Status: review

## Story

As a developer,
I want the project properly configured with necessary dependencies and environment variables,
So that the application can run securely and reliably.

## Acceptance Criteria

1. **Given** the project is initialized, **When** setting up dependencies, **Then** the system shall use Streamlit, Pandas, requests (or google-generativeai), and python-dotenv libraries (Architecture sections 4.4 and 5).

2. **Given** the project requires API credentials, **When** configuring the environment, **Then** Gemini API keys must be stored in environment variables using `python-dotenv` and never committed to version control (NFR-SEC-001, NFR5).

3. **Given** the project is shared or deployed, **When** reviewing the repository, **Then** the application shall include a `.env.example` file showing required environment variables (GEMINI_API_KEY) without actual secrets (NFR-SEC-002, NFR6).

4. **Given** the codebase is structured, **When** organizing modules, **Then** the system shall use modular architecture with separate modules for data processing, analytics, and AI integration (NFR-MAINT-004, NFR17).

## Tasks / Subtasks

- [x] Create environment configuration (AC: #2, #3)
  - [x] Create .env.example file with GEMINI_API_KEY placeholder
  - [x] Add .env to .gitignore (if not already present)
  - [x] Document environment setup in README

- [x] Document dependencies (AC: #1)
  - [x] Create requirements.txt with all dependencies
  - [x] Include version numbers for reproducibility
  - [x] List: streamlit, pandas, pytest, python-dotenv, requests

- [x] Create project documentation (AC: #1, #4)
  - [x] Create README.md with project overview
  - [x] Document installation instructions
  - [x] Document project structure (MVC architecture)
  - [x] Add usage instructions
  - [x] Include testing instructions

- [x] Verify modular architecture (AC: #4)
  - [x] Confirm models/ directory structure
  - [x] Confirm controllers/ directory structure
  - [x] Confirm views/ directory structure
  - [x] Confirm utils/ directory structure
  - [x] Confirm tests/ directory structure

## Dev Notes

### Critical Architecture Patterns

**Modular Architecture (NFR-MAINT-004, NFR17):**
Current project structure already follows MVC pattern:
```
FinanceApp/
├── models/          # Data layer
│   └── csv_model.py
├── controllers/     # Business logic
│   └── csv_controller.py
├── views/           # UI components (Streamlit)
│   └── (to be created in Epic 2+)
├── utils/           # Shared utilities
│   ├── bank_detector.py
│   └── data_validator.py
├── tests/           # Test suite
│   ├── test_csv_model.py
│   ├── test_csv_controller.py
│   ├── test_bank_detector.py
│   └── test_data_validator.py
└── app.py           # Main Streamlit application (to be created)
```

**Environment Security (NFR-SEC-001, NFR-SEC-002):**
- Sensitive data: Store in `.env` file (never committed)
- Template: Provide `.env.example` for documentation
- Loading: Use `python-dotenv` to load environment variables
- Access: `os.getenv('GEMINI_API_KEY')`

### Technical Requirements

**.env.example Template:**
```bash
# Gemini API Configuration
# Get your API key from: https://makersuite.google.com/app/apikey
GEMINI_API_KEY=your_api_key_here

# Optional: Application Configuration
# APP_ENV=development
# LOG_LEVEL=INFO
```

**requirements.txt Content:**
```
streamlit>=1.28.0
pandas>=2.0.0
pytest>=7.4.0
pytest-cov>=4.1.0
python-dotenv>=1.0.0
requests>=2.31.0
```

**README.md Structure:**
```markdown
# FinanceApp - Personal Finance Analytics with AI Coach

AI-powered financial insights for students and young professionals.

## Features
- CSV upload for bank statements (Monzo, Revolut, Barclays)
- Automatic transaction categorization
- Spending analytics and visualizations
- AI-powered financial coaching with Gemini 2.5 Flash

## Installation

### Prerequisites
- Python 3.9 or higher
- Gemini API key

### Setup
1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Configure environment variables (see Configuration)
4. Run the application: `streamlit run app.py`

## Configuration

Create a `.env` file in the project root:
```bash
GEMINI_API_KEY=your_actual_api_key_here
```

See `.env.example` for all configuration options.

## Project Structure

- `models/` - Data models (MVC pattern)
- `controllers/` - Business logic
- `views/` - UI components
- `utils/` - Shared utilities
- `tests/` - Test suite

## Testing

Run tests:
```bash
pytest tests/ -v
```

Run with coverage:
```bash
pytest tests/ --cov=. --cov-report=html
```

## Architecture

FinanceApp follows MVC (Model-View-Controller) architecture:
- **Models**: CSV data handling, validation
- **Controllers**: Upload processing, analytics coordination
- **Views**: Streamlit UI components
- **Utils**: Bank detection, data validation, categorization

## Requirements

See `requirements.txt` for full dependency list.

## License

[To be determined]

## Contributing

[To be determined]
```

### Code Standards

**Documentation Requirements:**
- Clear installation instructions
- Configuration examples (without secrets)
- Architecture overview
- Testing instructions
- Contribution guidelines (future)

**Security Best Practices:**
- Never commit `.env` file
- Provide `.env.example` as template
- Document where to obtain API keys
- Use environment variables for all secrets

### Implementation Guidance

**Minimal Changes Approach:**
This story is primarily about documentation and configuration:
1. Create `.env.example` (new file)
2. Create `requirements.txt` (new file)
3. Create `README.md` (new file)
4. Verify `.gitignore` includes `.env`

**Existing Files Check:**
```bash
# Check if .gitignore exists and includes .env
grep -q "^\.env$" .gitignore || echo ".env" >> .gitignore
```

**Dependencies to Document:**
Based on existing code:
- streamlit (main framework - to be used in Epic 2+)
- pandas (CSV processing, data manipulation)
- pytest (testing framework)
- pytest-cov (coverage reporting)
- python-dotenv (environment variables)
- requests (Gemini API calls - to be used in Epic 3)

### Usability Requirements

**Developer Experience:**
- One-command installation: `pip install -r requirements.txt`
- Clear setup instructions in README
- Example configuration provided
- Architecture diagram or description

### References

- [Architecture: Section 4.4 - Libraries & Dependencies](_bmad-output/planning-artifacts/architecture-overview-FinanceApp-2025-12-26.md#44-libraries--dependencies)
- [Architecture: Section 5 - Deployment Architecture](_bmad-output/planning-artifacts/architecture-overview-FinanceApp-2025-12-26.md#5-deployment-architecture)
- [PRD: Section 6.1 - NFR-SEC-001, NFR-SEC-002](_bmad-output/planning-artifacts/prd-FinanceApp-2025-12-26.md#61-security--privacy)
- [PRD: Section 6.4 - NFR-MAINT-004](_bmad-output/planning-artifacts/prd-FinanceApp-2025-12-26.md#64-maintainability)
- [Epic File: Story 1.6](_bmad-output/planning-artifacts/epics.md#story-16-setup-project-structure--environment-configuration)

## Dev Agent Record

### Agent Model Used

Claude Sonnet 4.5

### Debug Log References

None required - documentation and configuration task completed successfully.

### Completion Notes List

**Implementation Summary:**
- Enhanced `.env.example` with comprehensive documentation and setup instructions
- Updated `requirements.txt` to include `requests>=2.31.0` for Gemini API integration
- Updated `README.md` to reflect Epic 1 completion (Stories 1.1-1.6)
- Verified `.gitignore` already includes `.env` protection
- Confirmed modular MVC architecture in place
- All 96 tests passing, demonstrating project maturity

**Environment Configuration:**
- `.env.example` now includes:
  - Clear instructions to copy to `.env`
  - Link to Gemini API key acquisition
  - Optional configuration variables (APP_ENV, LOG_LEVEL)
  - Security reminder about never committing `.env`

**Dependencies Documented:**
```
streamlit>=1.28.0       # Web framework for UI
pandas>=2.0.0           # Data processing and analysis
python-dotenv>=1.0.0    # Environment variable management
requests>=2.31.0        # HTTP library for Gemini API (added)
pytest>=7.4.0           # Testing framework
pytest-cov>=4.1.0       # Coverage reporting
```

**README.md Updates:**
- Updated features section to show Epic 1 completion (Stories 1.1-1.6)
- Added 96 tests and 70%+ coverage metrics
- Enhanced installation instructions with git clone and .env setup
- Updated project structure to show all utility modules
- Reflected all implementation artifacts in BMad output structure
- Updated next stories to show Epic 2 (Analytics) is next
- Enhanced security section with .env.example mention

**Project Structure Verification:**
```
✅ models/           - CSVDataModel with encoding detection
✅ controllers/      - CSV upload handling
✅ views/            - Streamlit UI (placeholder for Epic 2+)
✅ utils/            - bank_detector.py, data_validator.py
✅ tests/            - 96 comprehensive tests
✅ _bmad-output/     - All 6 Epic 1 story artifacts
```

**Acceptance Criteria Verification:**
- ✅ AC #1: Dependencies documented (streamlit, pandas, requests, python-dotenv)
- ✅ AC #2: Gemini API key in environment variables via python-dotenv
- ✅ AC #3: `.env.example` file provided with clear documentation
- ✅ AC #4: Modular MVC architecture confirmed and documented

**Requirements Traceability:**
- NFR-SEC-001 (API keys in environment): ✅ python-dotenv configured
- NFR-SEC-002 (.env.example template): ✅ Enhanced with documentation
- NFR-MAINT-004 (Modular architecture): ✅ MVC pattern verified
- NFR17 (Separate modules): ✅ models/, controllers/, views/, utils/
- Architecture 4.4 (Libraries): ✅ All required dependencies listed
- Architecture 5 (Deployment): ✅ Environment configuration ready

**Epic 1 Status:**
All 6 stories complete:
- Story 1.1: CSV File Upload ✅
- Story 1.2: Multi-Bank Format Detection ✅
- Story 1.3: Data Validation & Reporting ✅
- Story 1.4: Multi-Format Date Support ✅
- Story 1.5: Multi-Encoding CSV Support ✅
- Story 1.6: Project Structure & Environment ✅

Ready for Epic 2: Core Financial Analytics & Visualization

### File List

**Modified Files:**
- `.env.example` (enhanced with comprehensive documentation and setup guide)
- `requirements.txt` (added requests>=2.31.0 for Gemini API support)
- `README.md` (updated to reflect Epic 1 completion, 96 tests, enhanced features)
- `_bmad-output/implementation-artifacts/1-6-project-structure-environment.md` (this file - status updated to review)

**Verified Existing Files:**
- `.gitignore` (confirmed .env is excluded from version control)
- Project structure (confirmed MVC architecture with models/, controllers/, views/, utils/, tests/)

