# Architecture Overview: FinanceApp

## 1. System Context

The FinanceApp is a web-based application designed to help students and young professionals manage their finances. It allows users to upload bank transaction data (CSV), provides basic analytics on spending, and offers personalized financial coaching through an AI assistant. The core interaction is via a Streamlit user interface.

## 2. High-Level Components

The system comprises the following major components:

*   **User Interface (UI):** A Streamlit application handling user interaction, file uploads, data display, and presenting AI-generated insights.
*   **Data Ingestion & Processing:** A Python backend responsible for receiving CSV uploads, parsing and normalizing transactional data, and performing initial data aggregation.
*   **Analytics Engine:** A Python module that calculates key financial metrics (total income, expenses, net savings, savings rate) and categorizes spending.
*   **AI Cashflow Coach (Gemini Integration):** Interacts with the Gemini 2.5 Flash API to generate personalized financial recommendations and habits based on summarized spending data and user goals.
*   **File Storage:** For saving processed data summaries and monthly action plans.

## 3. Data Flow Overview

1.  **User Uploads CSV:** Through the Streamlit UI, a user uploads a bank statement CSV file.
2.  **Data Ingestion:** The Streamlit app passes the CSV data to the Python backend for processing.
3.  **Parsing & Normalization:** The Python backend (using pandas) reads the CSV, normalizes column names, and cleans the transaction data.
4.  **Analytics Generation:** The processed data is fed into the Analytics Engine to compute spending by category, monthly trends, income, expenses, and savings metrics.
5.  **Summary for AI Coach:** A JSON summary of the analyzed spending data, along with the user's savings goal, is prepared.
6.  **AI Coaching:** This JSON summary is sent to the Gemini 2.5 Flash API.
7.  **AI Response:** Gemini returns personalized recommendations and a money habit.
8.  **UI Display:** The analytics results (charts) and the AI coach's summary are displayed in the Streamlit UI.
9.  **File Export:** Users can choose to save the processed summary (CSV/JSON) or the AI-generated monthly plan (text/Markdown) to local files.

## 4. Key Architectural Decisions

### 4.1. CSV Format Handling & Normalization

**Decision:** Multi-bank CSV format support with intelligent column detection

**Approach:**
*   **Column Mapping Strategy:** Maintain a dictionary of known bank formats (Monzo, Revolut, Barclays) with their specific column names
*   **Fallback Detection:** If bank format is unknown, attempt to detect columns by:
    *   Date columns: Look for date-like values or headers containing "date", "time", "when"
    *   Amount columns: Numeric values with headers containing "amount", "value", "debit", "credit"
    *   Description: Text columns with headers like "description", "merchant", "details", "narrative"
    *   Category: Optional columns containing "category", "type", "tag"
*   **Date Format Handling:** Support both DD/MM/YYYY and MM/DD/YYYY using pandas' date parsing with `dayfirst=True` (UK default)
*   **Currency:** Assume single currency (GBP) for MVP; amounts stored as float
*   **Normalization Output:** Standardize to columns: `Date`, `Description`, `Amount`, `Category`

### 4.2. Transaction Categorization Strategy

**Decision:** Rule-based categorization with manual override capability

**Approach:**
*   **Primary:** Use existing category from CSV if available
*   **Fallback:** Keyword-based categorization using merchant/description text:
    *   "Groceries": Tesco, Sainsbury's, Asda, Waitrose, Aldi, Lidl
    *   "Eating Out": Restaurant, cafe, McDonald's, Deliveroo, Uber Eats, Just Eat
    *   "Transport": TfL, Uber, train, bus, fuel, petrol
    *   "Subscriptions": Netflix, Spotify, Amazon Prime, gym
    *   "Shopping": Amazon, eBay, clothing retailers
    *   "Bills": Utilities, phone, internet, council tax
    *   "Uncategorized": Default for unmatched transactions
*   **Income Detection:** Positive amounts or keywords: "salary", "transfer in", "payment received"
*   **Extensibility:** Category rules stored in configurable dictionary for easy expansion

### 4.3. Error Handling Strategy

**Decision:** Graceful degradation with informative user feedback

**Error Scenarios & Handling:**

1.  **CSV Upload Errors:**
    *   Empty file → Display: "File is empty. Please upload a valid CSV."
    *   Invalid format (not CSV) → Display: "File format not recognized. Please upload a CSV file."
    *   Missing critical columns → Display: "Unable to detect required columns (Date, Amount). Please check file format."
    *   Action: Show sample expected format; allow re-upload

2.  **Data Parsing Errors:**
    *   Invalid dates → Skip row, log warning, show count of skipped rows
    *   Non-numeric amounts → Skip row, log warning
    *   Encoding issues → Try multiple encodings (utf-8, latin-1, cp1252)
    *   Action: Display summary: "Processed X transactions, skipped Y due to errors"

3.  **Gemini API Errors:**
    *   API key missing/invalid → Display: "AI Coach unavailable. Please configure API key."
    *   Rate limit exceeded → Display: "AI Coach busy. Please try again in a moment."
    *   Timeout (>30s) → Display: "AI Coach taking longer than expected. Using basic analysis."
    *   Network errors → Retry once, then fail gracefully with cached/default advice
    *   Action: Allow user to continue with analytics-only view

4.  **Processing Errors:**
    *   Insufficient data (<10 transactions) → Warning: "Limited data may affect insights quality"
    *   No expenses detected → Warning: "No expenses found. Check if amounts are correctly formatted."
    *   Extreme values → Flag transactions >£1000 for user review

### 4.4. Gemini API Integration Details

**Decision:** Use Gemini 2.5 Flash via REST API with structured prompts

**Configuration:**
*   **API Endpoint:** `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent`
*   **Authentication:** API key stored in environment variable `GEMINI_API_KEY`
*   **Timeout:** 15 seconds (as per NFR-PERF-002)
*   **Retry Policy:** Single retry on network errors, exponential backoff
*   **Response Format:** JSON with structured fields

**Prompt Structure:**
```
You are a friendly financial coach helping a user manage their spending.

User Profile:
- Monthly Income: £{income}
- Savings Goal: £{goal}/month

Spending Summary (Last 3 months):
{json_summary}

Top Categories:
{category_breakdown}

Provide:
1. 3-5 specific, actionable recommendations
2. One simple money habit to start next month
3. Identify biggest spending leaks

Be concise, encouraging, and specific with numbers.
```

**Expected Response Structure:**
```json
{
  "recommendations": [
    "Reduce eating out from £280 to £200/month (save £80)",
    "Cancel unused subscriptions: Netflix + Spotify (save £25)"
  ],
  "money_habit": "Pack lunch 3 days/week instead of buying",
  "spending_leaks": "Food delivery (£140/month) and impulse shopping (£95/month)"
}
```

### 4.5. State Management (Streamlit)

**Decision:** Session-based state with no persistence

**Approach:**
*   Use `st.session_state` to store:
    *   Uploaded CSV data (raw DataFrame)
    *   Processed/normalized data
    *   Analytics results (categories, trends, metrics)
    *   AI coach response
*   **Data Lifecycle:** Data exists only during browser session; cleared on refresh/close
*   **Security:** No server-side storage; all processing in-memory
*   **File Export:** User explicitly downloads processed data if needed

## 5. Technologies Used (High-Level)

*   **Frontend/Backend Framework:** Streamlit (Python 3.10+)
*   **Data Processing:** Pandas (Python)
*   **AI Integration:** Google Gemini API 2.5 Flash via REST
*   **API Client:** `requests` library for HTTP calls
*   **Charting:** Streamlit's native charting (`st.bar_chart`, `st.line_chart`) with Altair for advanced visualizations
*   **File Handling:** Standard Python I/O operations
*   **Environment Management:** `python-dotenv` for API key management
*   **Testing:** `pytest` for unit and integration tests

## 6. Future Considerations

*   **Database:** For persistent storage of user data, goals, and historical transactions beyond single-session CSV processing.
*   **Authentication/Authorization:** For multi-user environments.
*   **Deployment:** Containerization (e.g., Docker) for easier deployment to cloud platforms.
*   **Advanced Categorization:** Machine learning model for intelligent transaction categorization based on merchant names and spending patterns.
*   **Multi-currency Support:** Handle international students with transactions in multiple currencies.
*   **Subscription Detection:** Pattern recognition for recurring transactions (same merchant, similar amounts, regular intervals).
