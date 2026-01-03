# Technical Specification: FinanceApp

## 1. Introduction

This document outlines the technical design and implementation details for the FinanceApp, a Streamlit-based application that processes bank CSV data to provide financial analytics and AI-powered coaching. It builds upon the previously defined Product Brief and Architecture Overview.

## 2. Core Components and Technologies

### 2.1. User Interface (Streamlit)

*   **Framework:** Streamlit (Python)
*   **Components:**
    *   `st.file_uploader`: For CSV file upload.
    *   `st.dataframe`/`st.table`: To display raw or normalized transaction data (optional, for debugging/transparency).
    *   `st.bar_chart`/`st.line_chart`: For visualizing spending by category and monthly trends. Potentially using libraries like Altair or Plotly via Streamlit.
    *   `st.text_area`: To display the Gemini "Cashflow Coach" summary.
    *   `st.download_button`: To export processed data or monthly plans.
    *   `st.number_input`/`st.text_input`: For optional goal setting and user prompt input.

### 2.2. Data Ingestion and Processing

*   **Library:** Pandas (Python)
*   **Functions/Modules:**
    *   `read_csv(file_stream)`: Reads the uploaded CSV file into a pandas DataFrame.
    *   `normalize_columns(df)`: Standardizes column names (e.g., 'Date', 'Description', 'Amount', 'Category') irrespective of input variations. Handles potential missing columns.
    *   `clean_data(df)`: Handles missing values, converts data types (e.g., 'Amount' to numeric, 'Date' to datetime objects), and basic error checking.
    *   `categorize_transactions(df)`: (MVP) Simple keyword-based categorization or placeholder for future ML-based categorization. For MVP, assume categories are either in the CSV or derived simply. (Nice-to-have: more sophisticated categorization).

### 2.3. Analytics Engine

*   **Library:** Pandas (Python), potentially NumPy
*   **Functions/Modules:**
    *   `calculate_income_expenses(df)`: Determines total income (positive amounts) and total expenses (negative amounts or specific transaction types).
    *   `calculate_net_savings(income, expenses)`: Computes net savings.
    *   `calculate_monthly_savings_rate(net_savings, income)`: Calculates the savings rate.
    *   `aggregate_by_category(df)`: Groups transactions by category and sums amounts.
    *   `aggregate_by_month(df)`: Groups transactions by month and sums/averages relevant metrics.

### 2.4. AI Cashflow Coach (Gemini Integration)

*   **API:** Google Gemini API (specifically Gemini 2.5 Flash for speed and cost-efficiency).
*   **Python Library:** `google-generativeai` (or similar HTTP client like `requests`).
*   **Process:**
    1.  **Prepare Prompt:** Construct a detailed prompt including:
        *   Role instruction for the AI coach.
        *   User's specific savings goal.
        *   JSON representation of aggregated spending data (e.g., top categories, monthly summary, income/expenses).
        *   Clear request for 3-5 personalized recommendations and one money habit.
        *   (Optional) Request for biggest leaks.
    2.  **API Call:** Send the prompt to the Gemini API.
    3.  **Parse Response:** Extract recommendations and money habits from the AI's text response.

### 2.5. File Operations

*   **Python Libraries:** `pandas` (for CSV/JSON export), `io` (for in-memory file handling before saving).
*   **Functions:**
    *   `export_summary_data(df, format='csv')`: Saves processed data to CSV or JSON.
    *   `export_monthly_plan(text_content, format='md')`: Saves the AI coach's advice to a text/Markdown file.

## 3. Data Structures (Pandas DataFrames)

*   **Raw Transactions:** `DataFrame` with original CSV columns.
*   **Normalized Transactions:** `DataFrame` with `['Date', 'Description', 'Amount', 'Category']`.
*   **Aggregated Category Spend:** `DataFrame` with `['Category', 'Total Spend']`.
*   **Monthly Summary:** `DataFrame` with `['Month', 'Income', 'Expenses', 'Net Savings', 'Savings Rate']`.

## 4. API Keys and Security

*   **Gemini API Key:** Must be stored securely, ideally as an environment variable (e.g., `GEMINI_API_KEY`) and loaded at runtime. *Never hardcode API keys.*

## 5. Testing Strategy

*   **Unit Tests:** For individual functions within data processing, analytics, and file operations (e.g., `normalize_columns`, `calculate_net_savings`). Use `pytest`.
*   **Integration Tests:** To verify the flow from CSV upload through analytics to AI prompt generation. Mock the Gemini API response for predictable testing.
*   **UI Tests:** (Lower priority for MVP) Basic tests to ensure Streamlit components render correctly and interact as expected. Manual testing will suffice for MVP.
*   **Data Validation:** Ensure robust handling of malformed CSVs and edge cases in transaction data.

## 6. Deployment Considerations (Future)

*   The Streamlit application can be deployed on platforms that support Python applications, such as Streamlit Cloud, Heroku, or a custom server with Gunicorn/Uvicorn.
*   Environment variables for API keys are crucial for secure deployment.

## 7. Nice-to-Have Technical Details

*   **Goal Setting:** Add `st.session_state` to manage user-defined savings goals.
*   **Subscription Detection:** Implement regex or string matching on transaction descriptions combined with amount consistency checks.
*   **Tone Modes:** Include a parameter in the Gemini API prompt to specify the desired tone.
