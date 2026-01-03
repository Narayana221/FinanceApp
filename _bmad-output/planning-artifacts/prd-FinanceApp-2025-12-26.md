# Product Requirements Document (PRD): FinanceApp

**Version:** 1.0
**Date:** 2025-12-26

## 1. Introduction

This Product Requirements Document (PRD) details the functional and non-functional requirements for the FinanceApp. The FinanceApp aims to empower students and young professionals by providing them with clarity on their spending habits and personalized coaching to achieve their savings goals. It leverages CSV bank statement uploads and an AI assistant for tailored financial guidance.

## 2. Goals

*   **Primary Goal:** To help users understand their spending patterns and achieve their savings goals through personalized insights and actionable plans.
*   **Secondary Goals:**
    *   Provide a user-friendly interface for financial data analysis.
    *   Offer AI-driven, context-aware financial advice.
    *   Facilitate easy data import and export.

## 3. Target Audience

Students and young professionals who: 
*   Export bank statements as CSV files from institutions like Monzo, Revolut, or Barclays.
*   Desire a clear understanding of where their money goes.
*   Seek simple, tailored monthly action plans for savings, rather than generic budgeting advice.

## 4. Scope

### 4.1. Minimum Viable Product (MVP)

The MVP will focus on core functionality essential for demonstrating the app's value proposition:

*   **CSV Upload and Processing:** Users can upload bank statement CSVs. The system will parse and normalize columns using Python and Pandas.
*   **Basic Analytics:** Compute total income, total expenses, net savings, average monthly savings rate, and aggregate spend by category and month.
*   **Gemini "Cashflow Coach" Integration:** Utilize Gemini 2.5 Flash to provide 3-5 personalized recommendations and one simple money habit based on spending summary and user goals.
*   **Streamlit UI:** A functional interface for file upload, displaying charts (category, monthly trends), and presenting the AI coach's summary.
*   **File Operations:** Ability to save processed summaries (CSV/JSON) and export the AI-generated monthly plan (text/Markdown).

### 4.2. Future Enhancements (Nice-to-Have)

*   **Simple Goal Setting:** Users can set monthly savings targets, and the coach can provide feedback and adjustments.
*   **Subscription Detection:** Automatic flagging and summarization of recurring expenses for AI analysis.
*   **Tone Modes:** User-selectable tones (e.g., playful, serious) for the AI coach.

## 5. Functional Requirements

### 5.1. User Interface (Streamlit)

*   **REQ-UI-001:** The application shall provide a file uploader component for CSV files.
*   **REQ-UI-002:** The application shall display key financial insights using charts (e.g., bar chart by category, monthly trend).
*   **REQ-UI-003:** The application shall display the "Cashflow Coach" summary in a designated text area.
*   **REQ-UI-004:** The application shall allow users to download processed data summaries.
*   **REQ-UI-005:** The application shall allow users to export a "Monthly Plan" as a text or Markdown file.
*   **REQ-UI-006:** The application shall display informative error messages for invalid or unreadable CSV files.
*   **REQ-UI-007:** The application shall show processing status and the count of successfully processed vs skipped transactions.
*   **REQ-UI-008:** The application shall display warnings when insufficient data is available (<10 transactions).
*   **REQ-UI-009:** The application shall gracefully handle AI coach unavailability and allow users to view analytics without AI insights.
*   **REQ-UI-010 (Future):** The application shall allow users to input a monthly savings target.
*   **REQ-UI-011 (Future):** The application shall provide options to select a "Tone Mode" for the coach.

### 5.2. Data Ingestion and Processing

*   **REQ-DIP-001:** The system shall accept CSV files with columns for date, description, amount, and optionally category.
*   **REQ-DIP-002:** The system shall parse uploaded CSV files using Pandas.
*   **REQ-DIP-003:** The system shall detect and map common bank CSV formats (Monzo, Revolut, Barclays) to standard column names.
*   **REQ-DIP-004:** The system shall normalize input columns to a standard format (`Date`, `Description`, `Amount`, `Category`).
*   **REQ-DIP-005:** The system shall support both DD/MM/YYYY and MM/DD/YYYY date formats with UK format as default.
*   **REQ-DIP-006:** The system shall handle multiple text encodings (UTF-8, Latin-1, CP1252) for CSV files.
*   **REQ-DIP-007:** The system shall clean and validate transaction data (e.g., data types, missing values).
*   **REQ-DIP-008:** The system shall skip invalid rows and report the count of skipped transactions to the user.
*   **REQ-DIP-009:** The system shall categorize transactions using keyword-based rules for common merchants and spending categories.
*   **REQ-DIP-010:** The system shall detect income transactions based on positive amounts or income-related keywords.
*   **REQ-DIP-011:** The system shall assign "Uncategorized" to transactions that don't match any category rules.

### 5.3. Analytics Engine

*   **REQ-AE-001:** The system shall compute total income and total expenses.
*   **REQ-AE-002:** The system shall compute net savings (Income - Expenses).
*   **REQ-AE-003:** The system shall compute the average monthly savings rate.
*   **REQ-AE-004:** The system shall aggregate spending by category.
*   **REQ-AE-005:** The system shall aggregate spending and other metrics by month.

### 5.4. AI Cashflow Coach Integration

*   **REQ-AI-001:** The system shall prepare a JSON summary of spending data including income, expenses, top categories, and user's savings goal.
*   **REQ-AI-002:** The system shall interact with the Gemini 2.5 Flash API using the REST endpoint.
*   **REQ-AI-003:** The system shall construct structured prompts containing spending summary, category breakdown, and user context.
*   **REQ-AI-004:** The system shall request and receive 3-5 personalized, specific recommendations with concrete savings amounts from the AI.
*   **REQ-AI-005:** The system shall request and receive one simple "money habit" suggestion from the AI.
*   **REQ-AI-006:** The system shall request and receive an explanation of the biggest spending leaks (MVP feature).
*   **REQ-AI-007:** The system shall implement retry logic for API failures (single retry with exponential backoff).
*   **REQ-AI-008:** The system shall handle API timeouts gracefully and inform users if AI coach is unavailable.
*   **REQ-AI-009:** The system shall parse AI responses and display them in a user-friendly format.
*   **REQ-AI-010 (Future):** The system shall incorporate user-selected tone modes into the AI prompt.

### 5.5. File Operations

*   **REQ-FO-001:** The system shall allow users to save the processed summary in CSV or JSON format.
*   **REQ-FO-002:** The system shall allow users to export the "Monthly Plan" as a text or Markdown file.

## 6. Non-Functional Requirements

### 6.1. Performance

*   **NFR-PERF-001:** CSV upload and initial processing should complete within 30 seconds for typical file sizes (up to 10MB).
*   **NFR-PERF-002:** AI coach response time should ideally be under 15 seconds.

### 6.2. Usability

*   **NFR-USABILITY-001:** The interface shall be intuitive and easy to navigate for users with intermediate technical skills.
*   **NFR-USABILITY-002:** Visualizations should be clear and easy to interpret.

### 6.3. Security

*   **NFR-SEC-001:** Gemini API keys must be stored in environment variables using `python-dotenv` and never committed to version control.
*   **NFR-SEC-002:** The application shall include a `.env.example` file showing required environment variables without actual secrets.
*   **NFR-SEC-003:** User data should be handled with care; for MVP, data is processed in-memory only with no server-side persistence.
*   **NFR-SEC-004:** Uploaded CSV files shall not be saved to disk; all processing occurs in-memory within the Streamlit session.
*   **NFR-SEC-005:** API requests to Gemini shall use HTTPS for encrypted communication.

### 6.4. Reliability

*   **NFR-REL-001:** The system shall gracefully handle malformed CSV files without crashing.
*   **NFR-REL-002:** The system shall continue to provide analytics functionality even if AI coach API is unavailable.
*   **NFR-REL-003:** The system shall validate all user inputs and provide clear error messages for invalid data.
*   **NFR-REL-004:** The system shall handle edge cases including empty files, single transactions, and extreme values.

### 6.5. Maintainability

*   **NFR-MAINT-001:** Code shall follow Python best practices (PEP 8) and be well-commented where necessary.
*   **NFR-MAINT-002:** Unit and integration tests shall be implemented using `pytest` with minimum 70% code coverage.
*   **NFR-MAINT-003:** Category rules and bank format mappings shall be stored in configurable dictionaries for easy updates.
*   **NFR-MAINT-004:** The system shall use modular architecture with separate modules for data processing, analytics, and AI integration.

## 7. Future Considerations

*   **Data Persistence:** Implementation of a database for user accounts, goals, and historical transaction storage.
*   **Advanced Categorization:** Machine learning for more intelligent transaction categorization.
*   **Error Handling:** Robust error handling for API calls, file parsing, and data inconsistencies.
