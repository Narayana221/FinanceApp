# FinanceApp - Personal Cashflow Coach 💰

A Streamlit-based financial analysis tool that helps students and young professionals understand their spending patterns through AI-powered coaching.

## Features (Stories 1.1 & 1.2 - MVP)

- 📁 **CSV File Upload**: Simple interface to upload bank transaction CSV files
- 🏦 **Multi-Bank Support**: Automatically detects and normalizes Monzo, Revolut, and Barclays formats
- 🔍 **Smart Detection**: Fallback detection for unknown CSV formats
- ✅ **Intelligent Validation**: Automatically detects required columns (Date, Description, Amount)
- 📊 **Data Preview**: View your normalized transactions immediately after upload
- 🔒 **Privacy First**: All processing happens in-memory, no data saved to disk

## Quick Start

### Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

### Running the App

```bash
# Start Streamlit app
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=term-missing
```

## CSV Format

Your CSV file should include these columns (case-insensitive):

- **Date**: Transaction date (e.g., 01/01/2025)
- **Description**: Transaction description
- **Amount**: Transaction amount (negative for expenses, positive for income)
- **Category** (optional): Transaction category

### Example CSV

```csv
Date,Description,Amount,Category
01/01/2025,Tesco Superstore,-45.30,Groceries
02/01/2025,Salary Payment,2500.00,Income
03/01/2025,Coffee Shop,-3.50,Dining
```

## Supported Banks

The app automatically detects and normalizes CSV files from:

**Known Formats:**
- **Monzo**: Columns - Date, Name, Amount, Category
- **Revolut**: Columns - Started Date, Description, Amount, Category  
- **Barclays**: Columns - Number, Date, Account, Amount, Subcategory, Memo

**Unknown Formats:**
- Automatic fallback detection analyzes column content
- Identifies Date (date patterns), Amount (numeric), Description (text) columns
- Works with any CSV containing Date, Description, and Amount data

All formats are normalized to: `Date`, `Description`, `Amount`, `Category`

## Project Structure

```
FinanceApp/
├── app.py                 # Main Streamlit application (MVC orchestration)
├── requirements.txt       # Python dependencies
├── .env.example          # Environment template
├── .gitignore            # Git exclusions
│
├── models/               # Data layer (MVC)
│   ├── __init__.py
│   └── csv_model.py      # CSV data model with validation logic
│
├── views/                # Presentation layer (MVC)
│   ├── __init__.py
│   └── csv_view.py       # Streamlit UI components
│
├── controllers/          # Business logic layer (MVC)
│   ├── __init__.py
│   └── csv_controller.py # CSV upload request handling
│
├── utils/                # Utility modules
│   ├── __init__.py
│   └── bank_detector.py  # Bank format detection & normalization
│
├── tests/                # Test suite
│   ├── test_csv_model.py       # Model layer tests
│   ├── test_csv_controller.py  # Controller layer tests
│   └── test_bank_detector.py   # Bank detection tests
│
└── _bmad-output/         # BMad Method artifacts
    └── implementation-artifacts/
        ├── 1-1-csv-file-upload-component.md
        ├── 1-2-multi-bank-format-detection-and-column-mapping.md
        └── sprint-status.yaml
```

### Architecture

**MVC Pattern:**
- **Models** (`models/`): Data models, validation, and business rules
- **Views** (`views/`): Streamlit UI components, rendering logic
- **Controllers** (`controllers/`): Request handling, orchestration between models and views
- **Utils** (`utils/`): Shared utilities and helper functions

## Development

Built using the BMad Method v6 (alpha.21) for structured agile development.

### Tech Stack

- **Frontend/Backend**: Streamlit 1.28+ (Python web framework)
- **Architecture**: MVC (Model-View-Controller) pattern
- **Data Processing**: Pandas 2.0+
- **Testing**: pytest 7.4+ with 39 tests
- **Python**: 3.10+

### Next Stories

- Story 1.3: Data Cleaning & Validation
- Story 1.4: Multi-Format Date Support  
- Story 1.5: Multi-Encoding CSV Support
- Story 2.1: Transaction Categorization Engine

## Security

- ✅ All data processed in-memory (no disk storage)
- ✅ Environment variables for API keys (.env file, not committed)
- ✅ No server-side persistence

## License

Personal project for educational purposes.
