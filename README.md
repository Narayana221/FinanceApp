# FinanceApp - Personal Cashflow Coach 💰

A Streamlit-based financial analysis tool that helps students and young professionals understand their spending patterns through AI-powered coaching.

## Features (All 5 Epics Complete - 20 Stories)

### 📁 Epic 1: Secure Data Ingestion
- **CSV File Upload**: Simple interface to upload bank transaction CSV files
- **Multi-Bank Support**: Automatically detects and normalizes Monzo, Revolut, and Barclays formats
- **Smart Detection**: Fallback detection for unknown CSV formats
- **Data Validation**: Comprehensive validation with error reporting and skipped row tracking
- **Multi-Format Date Support**: Handles DD/MM/YYYY, MM/DD/YYYY, and ISO formats
- **Multi-Encoding Support**: UTF-8, Latin-1, CP1252 with automatic fallback
- **Privacy First**: All processing happens in-memory, no data saved to disk

### 📊 Epic 2: Core Financial Analytics
- **Income/Expense Analysis**: Automatic categorization and breakdown of transactions
- **Category Summary**: Visual breakdown by category with totals and percentages
- **Monthly Trends**: Line chart showing income vs expenses over time
- **Financial Health Score**: Calculated savings rate and financial health assessment
- **Summary Dashboard**: Key metrics including total income, expenses, and net savings

### 🤖 Epic 3: Personalized AI Coaching
- **Gemini AI Integration**: Powered by Google's Gemini 2.0 Flash model
- **Personalized Advice**: Context-aware financial coaching based on your data
- **Smart Prompts**: Structured prompts analyzing spending patterns and opportunities
- **Button-Triggered Generation**: User controls when AI generates recommendations
- **Session Caching**: Results cached for better performance

### 📥 Epic 4: Data Export & Management
- **Text Export**: Download AI coaching advice as plain text (.txt)
- **Markdown Export**: Download formatted advice as Markdown (.md)
- **CSV Export**: Export processed transaction data

### 🎯 Epic 5: Goal Setting & Customization
- **Savings Goal Input**: Set monthly savings targets (£0-£10,000)
- **Tone Customization**: Choose AI personality (Supportive, Playful, or Serious)
- **Persistent Settings**: Settings saved in session state

### 🧪 Quality Assurance
- **268 Comprehensive Tests**: Full test coverage across all features
- **90%+ Code Coverage**: Rigorous testing of models, controllers, and utilities

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/Narayana221/FinanceApp.git
cd FinanceApp

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env and add your Gemini API key
# Get your free API key from: https://aistudio.google.com/app/apikey
```

**Important:** The `.env` file should contain:
```
GEMINI_API_KEY=your_actual_api_key_here
```

### Running the App

```bash
# Start Streamlit app
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

### Running Tests

```bash
# Run all tests (268 tests)
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=. --cov-report=term-missing

# Quick test run
pytest tests/ -q
```

## How It Works

1. **Upload CSV**: Upload your bank transaction CSV file
2. **Auto-Detection**: App automatically detects your bank format (Monzo, Revolut, Barclays, or generic)
3. **Validation**: Data is validated and cleaned
4. **Analytics**: View financial summary, category breakdown, and monthly trends
5. **Set Goals**: Configure your savings goal and preferred AI tone in the sidebar
6. **AI Coaching**: Click "🎯 Generate AI Recommendations" for personalized advice
7. **Export**: Download your AI plan as text or markdown

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
│   ├── bank_detector.py    # Bank format detection & normalization
│   ├── data_validator.py   # Data validation and cleaning
│   ├── financial_analyzer.py  # Financial analytics and health scoring
│   ├── gemini_client.py    # Gemini AI API integration
│   └── prompt_builder.py   # AI prompt construction with tone modes
│
├── tests/                # Test suite (268 tests)
│   ├── test_csv_model.py         # Model layer tests
│   ├── test_csv_controller.py    # Controller layer tests
│   ├── test_bank_detector.py     # Bank detection tests
│   ├── test_data_validator.py    # Validation tests
│   ├── test_financial_analyzer.py # Analytics tests
│   ├── test_gemini_client.py     # AI client tests
│   └── test_prompt_builder.py    # Prompt builder tests
│
└── _bmad-output/         # BMad Method artifacts
    └── implementation-artifacts/
        ├── 1-*.md        # Epic 1: Secure Data Ingestion (6 stories)
        ├── 2-*.md        # Epic 2: Core Financial Analytics (5 stories)
        ├── 3-*.md        # Epic 3: Personalized AI Coaching (5 stories)
        ├── 4-*.md        # Epic 4: Data Export & Management (2 stories)
        ├── 5-*.md        # Epic 5: Goal Setting & Customization (2 stories)
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
- **AI Model**: Google Gemini 2.0 Flash (via REST API)
- **Architecture**: MVC (Model-View-Controller) pattern
- **Data Processing**: Pandas 2.0+ with multi-format date and encoding support
- **Visualization**: Plotly for interactive charts
- **Testing**: pytest 7.4+ with 268 tests and 90%+ code coverage
- **Environment**: python-dotenv for configuration management
- **Python**: 3.9+

## Deployment

### Streamlit Cloud

1. Push your code to GitHub
2. Go to [Streamlit Cloud](https://share.streamlit.io/)
3. Connect your repository
4. In **App Settings** → **Secrets**, add:
   ```toml
   GEMINI_API_KEY = "your_api_key_here"
   ```
5. Deploy!

**Note:** If deploying publicly, consider adding a user API key input option to avoid consuming your personal API quota.

## Security & Privacy

- ✅ All data processed in-memory (no disk storage)
- ✅ Environment variables for API keys (.env file, never committed)
- ✅ No server-side persistence
- ✅ `.gitignore` configured to protect sensitive data
- ✅ `.env.example` template provided for safe configuration sharing

## License

MIT License - See LICENSE file for details
