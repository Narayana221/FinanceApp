---
stepsCompleted: []
inputDocuments:
  - _bmad-output/planning-artifacts/prd-FinanceApp-2025-12-26.md
  - _bmad-output/planning-artifacts/architecture-overview-FinanceApp-2025-12-26.md
  - _bmad-output/planning-artifacts/product-brief-FinanceApp-2025-12-26.md
  - _bmad-output/planning-artifacts/technical-spec-FinanceApp-2025-12-26.md
---

# FinanceApp - Epic Breakdown

## Overview

This document provides the complete epic and story breakdown for FinanceApp, decomposing the requirements from the PRD, UX Design if it exists, and Architecture requirements into implementable stories.

## Requirements Inventory

### Functional Requirements

FR1: The application shall provide a file uploader component for CSV files.
FR2: The application shall display key financial insights using charts (e.g., bar chart by category, monthly trend).
FR3: The application shall display the "Cashflow Coach" summary in a designated text area.
FR4: The application shall allow users to download processed data summaries.
FR5: The application shall allow users to export a "Monthly Plan" as a text or Markdown file.
FR6: The application shall display informative error messages for invalid or unreadable CSV files.
FR7: The application shall show processing status and the count of successfully processed vs skipped transactions.
FR8: The application shall display warnings when insufficient data is available (<10 transactions).
FR9: The application shall gracefully handle AI coach unavailability and allow users to view analytics without AI insights.
FR10: The application shall allow users to input a monthly savings target.
FR11: The application shall provide options to select a "Tone Mode" for the coach.
FR12: The system shall accept CSV files with columns for date, description, amount, and optionally category.
FR13: The system shall parse uploaded CSV files using Pandas.
FR14: The system shall detect and map common bank CSV formats (Monzo, Revolut, Barclays) to standard column names.
FR15: The system shall normalize input columns to a standard format (`Date`, `Description`, `Amount`, `Category`).
FR16: The system shall support both DD/MM/YYYY and MM/DD/YYYY date formats with UK format as default.
FR17: The system shall handle multiple text encodings (UTF-8, Latin-1, CP1252) for CSV files.
FR18: The system shall clean and validate transaction data (e.g., data types, missing values).
FR19: The system shall skip invalid rows and report the count of skipped transactions to the user.
FR20: The system shall categorize transactions using keyword-based rules for common merchants and spending categories.
FR21: The system shall detect income transactions based on positive amounts or income-related keywords.
FR22: The system shall assign "Uncategorized" to transactions that don't match any category rules.
FR23: The system shall compute total income and total expenses.
FR24: The system shall compute net savings (Income - Expenses).
FR25: The system shall compute the average monthly savings rate.
FR26: The system shall aggregate spending by category.
FR27: The system shall aggregate spending and other metrics by month.
FR28: The system shall prepare a JSON summary of spending data including income, expenses, top categories, and user's savings goal.
FR29: The system shall interact with the Gemini 2.5 Flash API using the REST endpoint.
FR30: The system shall construct structured prompts containing spending summary, category breakdown, and user context.
FR31: The system shall request and receive 3-5 personalized, specific recommendations with concrete savings amounts from the AI.
FR32: The system shall request and receive one simple "money habit" suggestion from the AI.
FR33: The system shall request and receive an explanation of the biggest spending leaks (MVP feature).
FR34: The system shall implement retry logic for API failures (single retry with exponential backoff).
FR35: The system shall handle API timeouts gracefully and inform users if AI coach is unavailable.
FR36: The system shall parse AI responses and display them in a user-friendly format.
FR37: The system shall incorporate user-selected tone modes into the AI prompt.
FR38: The system shall allow users to save the processed summary in CSV or JSON format.
FR39: The system shall allow users to export the "Monthly Plan" as a text or Markdown file.

### NonFunctional Requirements

NFR1: CSV upload and initial processing should complete within 30 seconds for typical file sizes (up to 10MB).
NFR2: AI coach response time should ideally be under 15 seconds.
NFR3: The interface shall be intuitive and easy to navigate for users with intermediate technical skills.
NFR4: Visualizations should be clear and easy to interpret.
NFR5: Gemini API keys must be stored in environment variables using `python-dotenv` and never committed to version control.
NFR6: The application shall include a `.env.example` file showing required environment variables without actual secrets.
NFR7: User data should be handled with care; for MVP, data is processed in-memory only with no server-side persistence.
NFR8: Uploaded CSV files shall not be saved to disk; all processing occurs in-memory within the Streamlit session.
NFR9: API requests to Gemini shall use HTTPS for encrypted communication.
NFR10: The system shall gracefully handle malformed CSV files without crashing.
NFR11: The system shall continue to provide analytics functionality even if AI coach API is unavailable.
NFR12: The system shall validate all user inputs and provide clear error messages for invalid data.
NFR13: The system shall handle edge cases including empty files, single transactions, and extreme values.
NFR14: Code shall follow Python best practices (PEP 8) and be well-commented where necessary.
NFR15: Unit and integration tests shall be implemented using `pytest` with minimum 70% code coverage.
NFR16: Category rules and bank format mappings shall be stored in configurable dictionaries for easy updates.
NFR17: The system shall use modular architecture with separate modules for data processing, analytics, and AI integration.

### Additional Requirements

- **From Architecture Overview:**
    - **Column Mapping Strategy:** Maintain a dictionary of known bank formats with specific column names.
    - **Fallback Detection:** If bank format is unknown, attempt to detect columns by date, amount, description, and category.
    - **Date Format Handling:** Support both DD/MM/YYYY and MM/DD/YYYY using pandas with `dayfirst=True` (UK default).
    - **Currency:** Assume single currency (GBP) for MVP; amounts stored as float.
    - **Normalization Output:** Standardize to columns: `Date`, `Description`, `Amount`, `Category`.
    - **Rule-based Categorization:** Use existing category from CSV if available, fallback to keyword-based categorization for common merchants/spending categories.
    - **Income Detection:** Positive amounts or keywords: "salary", "transfer in", "payment received".
    - **Extensibility:** Category rules stored in configurable dictionary for easy expansion.
    - **Error Handling - CSV Upload:** Display specific messages for empty file, invalid format, missing critical columns.
    - **Error Handling - Data Parsing:** Skip invalid rows, log warnings, try multiple encodings (utf-8, latin-1, cp1252).
    - **Error Handling - Gemini API:** Display specific messages for missing/invalid API key, rate limit, timeout, network errors. Allow analytics-only view.
    - **Error Handling - Processing Errors:** Warnings for insufficient data, no expenses, flag extreme values.
    - **Gemini API Endpoint:** `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent`.
    - **Gemini Authentication:** API key stored in environment variable `GEMINI_API_KEY`.
    - **Gemini Timeout:** 15 seconds.
    - **Gemini Retry Policy:** Single retry on network errors, exponential backoff.
    - **Gemini Prompt Structure:** Detailed structure defined for AI coach interaction.
    - **State Management:** Use `st.session_state` to store data (uploaded CSV, processed data, analytics, AI response) during browser session; no server-side storage.

- **From Technical Specification:**
    - **Streamlit Components:** Specific components to be used (file_uploader, dataframe, bar_chart/line_chart, text_area, download_button, number_input/text_input).
    - **Pandas Functions:** Specific functions for data processing (`read_csv`, `normalize_columns`, `clean_data`, `categorize_transactions`).
    - **Analytics Functions:** Specific functions for calculations (`calculate_income_expenses`, `calculate_net_savings`, `calculate_monthly_savings_rate`, `aggregate_by_category`, `aggregate_by_month`).
    - **AI Integration Process:** Prepare prompt, API call, parse response using `google-generativeai` or `requests`.
    - **File Operations Functions:** `export_summary_data`, `export_monthly_plan`.
    - **Data Structures:** Specific Pandas DataFrames for raw, normalized, aggregated data.
    - **Testing Strategy:** Unit tests with `pytest`, integration tests (mocking Gemini API), basic UI tests, robust data validation.

- **From Project Brief:**
    - **Primary Goal:** To help users understand spending patterns and achieve savings goals through personalized insights and actionable plans.
    - **Secondary Goals:** User-friendly interface, AI-driven advice, easy data import/export.
    - **Target Audience:** Students and young professionals exporting bank statements as CSVs (Monzo, Revolut, Barclays), desiring clear spending understanding, and seeking tailored monthly action plans.
    - **MVP Scope:** CSV Upload and Processing, Basic Analytics, Gemini "Cashflow Coach" Integration, Streamlit UI, File Operations.

## Potential Risks

### Epic 1: Secure Data Ingestion & Basic Setup
*   **Risk 1 (Technical):** CSV parsing and normalization across various bank formats (Monzo, Revolut, Barclays) proves more complex or error-prone than anticipated, leading to data quality issues and user frustration.
*   **Risk 2 (Technical):** Handling diverse date formats and text encodings in CSVs leads to unexpected parsing failures for certain user files.
*   **Risk 3 (User Adoption):** Users are hesitant or unable to export their bank statements in a compatible CSV format, hindering initial onboarding.
*   **Risk 4 (Security):** Despite in-memory processing, users may have privacy concerns about uploading sensitive financial data, impacting trust.

### Epic 2: Core Financial Analytics & Visualization
*   **Risk 1 (Technical):** Performance issues arise when processing large CSV files for analytics, causing delays in chart generation and a poor user experience.
*   **Risk 2 (User Adoption):** Default categorization rules are insufficient or inaccurate for a significant portion of user transactions, requiring extensive manual correction or leading to misleading insights.
*   **Risk 3 (UX):** Visualizations are not clear or intuitive enough for the target audience (students/young professionals), leading to misinterpretation or lack of engagement.

### Epic 3: Personalized AI Coaching & Insights
*   **Risk 1 (Technical):** Gemini API integration has unforeseen latency issues or frequent outages, impacting the real-time availability and responsiveness of the AI coach.
*   **Risk 2 (Technical):** Prompt engineering for Gemini 2.5 Flash does not consistently yield highly personalized, actionable, and accurate recommendations, leading to generic or unhelpful advice.
*   **Risk 3 (User Adoption):** Users find the AI's tone or advice unhelpful, intrusive, or generic, leading to disengagement from the coaching feature.
*   **Risk 4 (Ethical/Legal):** AI recommendations could inadvertently lead to negative financial outcomes for users if not carefully crafted or if based on incomplete data, creating liability concerns, **especially if the advice does not strictly comply with UK financial regulations and legal standards.**

### Epic 4: Data Export & Management
*   **Risk 1 (Technical):** Exported CSV/JSON formats are not universally compatible with other tools users might want to use, limiting interoperability.
*   **Risk 2 (UX):** The process of saving and exporting data or plans is not straightforward, causing user confusion or abandonment.

### Epic 5: Future Enhancements - Goal Setting & Customization
*   **Risk 1 (Scope Creep):** Introducing goal setting and tone modes too early distracts from perfecting the core MVP, leading to delays.
*   **Risk 2 (Technical):** Integrating dynamic tone modes into the AI prompt significantly increases complexity or reduces the quality/consistency of AI responses.

### FR Coverage Map

FR1: Epic 1 - Secure Data Ingestion & Basic Setup
FR2: Epic 2 - Core Financial Analytics & Visualization
FR3: Epic 3 - Personalized AI Coaching & Insights
FR4: Epic 4 - Data Export & Management
FR5: Epic 4 - Data Export & Management
FR6: Epic 1 - Secure Data Ingestion & Basic Setup
FR7: Epic 1 - Secure Data Ingestion & Basic Setup
FR8: Epic 1 - Secure Data Ingestion & Basic Setup
FR9: Epic 3 - Personalized AI Coaching & Insights
FR10: Epic 5 - Future Enhancements - Goal Setting & Customization
FR11: Epic 5 - Future Enhancements - Goal Setting & Customization
FR12: Epic 1 - Secure Data Ingestion & Basic Setup
FR13: Epic 1 - Secure Data Ingestion & Basic Setup
FR14: Epic 1 - Secure Data Ingestion & Basic Setup
FR15: Epic 1 - Secure Data Ingestion & Basic Setup
FR16: Epic 1 - Secure Data Ingestion & Basic Setup
FR17: Epic 1 - Secure Data Ingestion & Basic Setup
FR18: Epic 1 - Secure Data Ingestion & Basic Setup
FR19: Epic 1 - Secure Data Ingestion & Basic Setup
FR20: Epic 2 - Core Financial Analytics & Visualization
FR21: Epic 2 - Core Financial Analytics & Visualization
FR22: Epic 2 - Core Financial Analytics & Visualization
FR23: Epic 2 - Core Financial Analytics & Visualization
FR24: Epic 2 - Core Financial Analytics & Visualization
FR25: Epic 2 - Core Financial Analytics & Visualization
FR26: Epic 2 - Core Financial Analytics & Visualization
FR27: Epic 2 - Core Financial Analytics & Visualization
FR28: Epic 3 - Personalized AI Coaching & Insights
FR29: Epic 3 - Personalized AI Coaching & Insights
FR30: Epic 3 - Personalized AI Coaching & Insights
FR31: Epic 3 - Personalized AI Coaching & Insights
FR32: Epic 3 - Personalized AI Coaching & Insights
FR33: Epic 3 - Personalized AI Coaching & Insights
FR34: Epic 3 - Personalized AI Coaching & Insights
FR35: Epic 3 - Personalized AI Coaching & Insights
FR36: Epic 3 - Personalized AI Coaching & Insights
FR37: Epic 5 - Future Enhancements - Goal Setting & Customization
FR38: Epic 4 - Data Export & Management
FR39: Epic 4 - Data Export & Management

## Epic List

### Epic 1: Secure Data Ingestion & Basic Setup
Users can securely upload their bank CSV files, and the system can reliably process and normalize this data, providing immediate feedback on the upload status.
**FRs covered:** FR1, FR6, FR7, FR8, FR12, FR13, FR14, FR15, FR16, FR17, FR18, FR19

### Epic 2: Core Financial Analytics & Visualization
Users can view a clear, intuitive breakdown of their spending and earnings, understanding their cash flow through categorized data and trend visualizations.
**FRs covered:** FR2, FR20, FR21, FR22, FR23, FR24, FR25, FR26, FR27

### Epic 3: Personalized AI Coaching & Insights
Users receive actionable, personalized financial recommendations and money habits from the AI coach, helping them identify spending leaks and work towards savings goals.
**FRs covered:** FR3, FR9, FR28, FR29, FR30, FR31, FR32, FR33, FR34, FR35, FR36

### Epic 4: Data Export & Management
Users can easily save their processed financial summaries and the AI-generated monthly plans for their records or further analysis.
**FRs covered:** FR4, FR5, FR38, FR39

### Epic 5: Future Enhancements - Goal Setting & Customization
Users can set personal savings targets and customize their interaction with the AI coach, making the guidance even more tailored to their preferences.
**FRs covered:** FR10, FR11, FR37

---

## Epic 1: Secure Data Ingestion & Basic Setup

Users can securely upload their bank CSV files, and the system can reliably process and normalize this data, providing immediate feedback on the upload status.

### Story 1.1: CSV File Upload Component

As a user,
I want to upload my bank CSV file through a simple interface,
So that I can analyze my spending without manual data entry.

**Acceptance Criteria:**

**Given** I am on the FinanceApp homepage,
**When** I access the application,
**Then** the application shall provide a file uploader component for CSV files (referencing REQ-UI-001, FR1).

**Given** the file uploader is displayed,
**When** I select a CSV file from my computer,
**Then** the system shall accept CSV files with columns for date, description, amount, and optionally category (referencing REQ-DIP-001, FR12).

**Given** a CSV file is selected,
**When** the upload completes,
**Then** I shall see a confirmation message showing the filename and file size.

**Given** an invalid file type is selected,
**When** I attempt to upload,
**Then** the application shall display an informative error message indicating only CSV files are accepted (referencing REQ-UI-006, FR6).

### Story 1.2: Multi-Bank Format Detection & Column Mapping

As a user,
I want the system to automatically detect my bank's CSV format,
So that I don't have to manually configure column mappings.

**Acceptance Criteria:**

**Given** a CSV file is uploaded,
**When** the system parses the file using Pandas,
**Then** it shall detect and map common bank CSV formats (Monzo, Revolut, Barclays) to standard column names (referencing REQ-DIP-003, REQ-DIP-014, FR13, FR14).

**Given** the bank format is recognized,
**When** column mapping occurs,
**Then** the system shall normalize input columns to a standard format: `Date`, `Description`, `Amount`, `Category` (referencing REQ-DIP-004, FR15).

**Given** the bank format is unknown,
**When** the system attempts column detection,
**Then** it shall use fallback detection to identify columns by looking for date-like values, numeric amounts, and text descriptions (per Architecture Decision 4.1).

**Given** critical columns (Date, Amount) cannot be detected,
**When** parsing fails,
**Then** the application shall display an error message: "Unable to detect required columns (Date, Amount). Please check file format." (per Architecture Decision 4.3).

### Story 1.3: Clean, Validate, and Report Transaction Data

As a user,
I want the system to clean and validate my transaction data, skip invalid rows, and report on the processing status,
So that I have confidence in the accuracy of the data used for analysis and understand any data quality issues encountered.

**Acceptance Criteria:**

**Given** normalized transaction data,
**When** the system cleans and validates data (e.g., ensuring correct data types for Amount, Date),
**Then** it shall handle missing values appropriately and correct data types (referencing REQ-DIP-007, FR18).

**Given** the system is processing transactions,
**When** it encounters invalid rows (e.g., malformed dates, non-numeric amounts),
**Then** it shall skip these rows and not include them in further processing (referencing REQ-DIP-008, FR19).

**Given** invalid rows have been skipped,
**When** the processing is complete,
**Then** the application shall display the total count of successfully processed transactions and the count of skipped transactions to the user (referencing REQ-UI-007, FR7).

**Given** the system encounters critical errors during file processing (e.g., unreadable file format),
**When** the error occurs,
**Then** it shall display informative, user-friendly error messages (referencing REQ-UI-006, FR6).

**Given** the total number of valid transactions is less than 10 after processing,
**When** the summary is presented,
**Then** the application shall display a warning indicating insufficient data for robust analysis (referencing REQ-UI-008, FR8).

### Story 1.4: Multi-Format Date Support

As a user,
I want the system to handle different date formats from various banks,
So that my CSV data is parsed correctly regardless of regional formatting.

**Acceptance Criteria:**

**Given** a CSV file contains dates,
**When** the system parses date columns,
**Then** it shall support both DD/MM/YYYY and MM/DD/YYYY date formats with UK format (DD/MM/YYYY) as default (referencing REQ-DIP-005, FR16).

**Given** date parsing is configured,
**When** using Pandas date parsing,
**Then** the system shall use `dayfirst=True` as the default setting (per Architecture Decision 4.1).

**Given** ambiguous dates are encountered (e.g., 01/02/2025),
**When** parsing with UK default,
**Then** the system shall interpret this as 1st February 2025 (day-first).

**Given** invalid dates are encountered,
**When** the system attempts to parse them,
**Then** it shall skip those rows and include them in the skipped transaction count (referencing REQ-DIP-008, FR19).

### Story 1.5: Multi-Encoding CSV Support

As a user,
I want the system to handle CSV files with different text encodings,
So that international characters and various bank exports are processed correctly.

**Acceptance Criteria:**

**Given** a CSV file is uploaded,
**When** the system reads the file,
**Then** it shall handle multiple text encodings (UTF-8, Latin-1, CP1252) for CSV files (referencing REQ-DIP-006, FR17).

**Given** the primary encoding (UTF-8) fails,
**When** a reading error occurs,
**Then** the system shall automatically retry with alternative encodings (Latin-1, then CP1252) (per Architecture Decision 4.3).

**Given** all encoding attempts fail,
**When** the file cannot be read,
**Then** the application shall display an error message: "File encoding not recognized. Please ensure the file is a valid CSV." (per Architecture Decision 4.3).

### Story 1.6: Setup Project Structure & Environment Configuration

As a developer,
I want the project properly configured with necessary dependencies and environment variables,
So that the application can run securely and reliably.

**Acceptance Criteria:**

**Given** the project is initialized,
**When** setting up dependencies,
**Then** the system shall use Streamlit, Pandas, requests (or google-generativeai), and python-dotenv libraries (per Architecture sections 4.4 and 5).

**Given** the project requires API credentials,
**When** configuring the environment,
**Then** Gemini API keys must be stored in environment variables using `python-dotenv` and never committed to version control (referencing NFR-SEC-001, NFR5).

**Given** the project is shared or deployed,
**When** reviewing the repository,
**Then** the application shall include a `.env.example` file showing required environment variables (GEMINI_API_KEY) without actual secrets (referencing NFR-SEC-002, NFR6).

**Given** the codebase is structured,
**When** organizing modules,
**Then** the system shall use modular architecture with separate modules for data processing, analytics, and AI integration (referencing NFR-MAINT-004, NFR17).

---

## Epic 2: Core Financial Analytics & Visualization

Users can view a clear, intuitive breakdown of their spending and earnings, understanding their cash flow through categorized data and trend visualizations.

### Story 2.1: Transaction Categorization Engine

As a user,
I want my transactions automatically categorized by spending type,
So that I can understand where my money goes without manual categorization.

**Acceptance Criteria:**

**Given** normalized transaction data is available,
**When** the system categorizes transactions,
**Then** it shall use keyword-based rules for common merchants and spending categories (referencing REQ-DIP-009, FR20).

**Given** a transaction has an existing category from the CSV,
**When** categorization runs,
**Then** the system shall use the existing category as primary (per Architecture Decision 4.2).

**Given** a transaction has no existing category,
**When** the fallback categorization runs,
**Then** the system shall match merchant/description keywords against categories: Groceries, Eating Out, Transport, Subscriptions, Shopping, Bills (per Architecture Decision 4.2).

**Given** a transaction matches no category rules,
**When** categorization completes,
**Then** the system shall assign "Uncategorized" to transactions that don't match any category rules (referencing REQ-DIP-011, FR22).

**Given** category rules need updates,
**When** reviewing the configuration,
**Then** category rules and bank format mappings shall be stored in configurable dictionaries for easy updates (referencing NFR-MAINT-003, NFR16).

### Story 2.2: Income & Expense Calculations

As a user,
I want to see my total income, expenses, and net savings,
So that I understand my overall financial health.

**Acceptance Criteria:**

**Given** categorized transaction data is available,
**When** the system analyzes transactions,
**Then** it shall detect income transactions based on positive amounts or income-related keywords (referencing REQ-DIP-010, FR21).

**Given** transactions are categorized as income or expenses,
**When** calculating totals,
**Then** the system shall compute total income and total expenses (referencing REQ-AE-001, FR23).

**Given** total income and expenses are calculated,
**When** computing savings,
**Then** the system shall compute net savings using the formula: Income - Expenses (referencing REQ-AE-002, FR24).

**Given** net savings is calculated,
**When** computing the savings rate,
**Then** the system shall compute the average monthly savings rate (referencing REQ-AE-003, FR25).

**Given** extreme transaction values (> £1000) are detected,
**When** processing completes,
**Then** the system shall flag these transactions for user review (per Architecture Decision 4.3).

### Story 2.3: Display Financial Insights with Charts

As a user,
I want to see my financial insights presented visually through charts,
So that I can quickly and easily understand my spending patterns and overall financial health.

**Acceptance Criteria:**

**Given** core financial metrics (income, expenses, net savings, savings rate) and aggregated spending data are available,
**When** the application displays the financial insights,
**Then** it shall use charts (e.g., bar chart by category, monthly trend) to visualize key financial insights (referencing REQ-UI-002, FR2).

**Given** the financial charts are displayed,
**When** a user views the visualizations,
**Then** the charts shall be clear and easy to interpret (referencing NFR-USABILITY-002, NFR4).

**Given** the application displays data,
**When** rendering charts,
**Then** it shall use Streamlit's native charting components (st.bar_chart, st.line_chart) with Altair for advanced visualizations (per Architecture section 5).

### Story 2.4: Spending Aggregation by Category

As a user,
I want to see my spending broken down by category,
So that I can identify which spending types consume most of my budget.

**Acceptance Criteria:**

**Given** categorized transaction data is available,
**When** the analytics engine processes the data,
**Then** the system shall aggregate spending by category (referencing REQ-AE-004, FR26).

**Given** spending is aggregated by category,
**When** displaying the results,
**Then** the application shall show total amounts for each category (Groceries, Eating Out, Transport, Subscriptions, Shopping, Bills, Uncategorized).

**Given** category aggregation is complete,
**When** preparing visualizations,
**Then** the data shall be formatted for bar chart display showing category names and amounts.

### Story 2.5: Monthly Trend Analysis

As a user,
I want to see my spending and savings trends over time,
So that I can track my financial progress month by month.

**Acceptance Criteria:**

**Given** transaction data spans multiple months,
**When** the analytics engine processes the data,
**Then** the system shall aggregate spending and other metrics by month (referencing REQ-AE-005, FR27).

**Given** monthly aggregation is complete,
**When** calculating monthly metrics,
**Then** the system shall provide income, expenses, net savings, and savings rate for each month.

**Given** monthly data is available,
**When** displaying the trends,
**Then** the application shall show a line chart or trend visualization of monthly spending and savings over time.

---

## Epic 3: Personalized AI Coaching & Insights

Users receive actionable, personalized financial recommendations and money habits from the AI coach, helping them identify spending leaks and work towards savings goals.

### Story 3.1: Gemini API Integration & Authentication

As a developer,
I want to integrate the Gemini 2.5 Flash API with proper authentication,
So that the application can request AI-generated financial advice securely.

**Acceptance Criteria:**

**Given** the Gemini API integration is configured,
**When** making API calls,
**Then** the system shall interact with the Gemini 2.5 Flash API using the REST endpoint: `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent` (referencing REQ-AI-002, FR29, per Architecture Decision 4.4).

**Given** API authentication is required,
**When** the system initializes,
**Then** the API key shall be loaded from the environment variable `GEMINI_API_KEY` (per Architecture Decision 4.4).

**Given** the API key is missing or invalid,
**When** attempting to call the API,
**Then** the application shall display: "AI Coach unavailable. Please configure API key." (per Architecture Decision 4.3, referencing REQ-AI-008, FR35).

**Given** API requests are made,
**When** communicating with Gemini,
**Then** API requests shall use HTTPS for encrypted communication (referencing NFR-SEC-005, NFR9).

**Given** the API client is configured,
**When** making requests,
**Then** the timeout shall be set to 15 seconds (referencing NFR-PERF-002, NFR2, per Architecture Decision 4.4).

### Story 3.2: Prompt Engineering & JSON Summary Preparation

As a user,
I want my spending data intelligently summarized and sent to the AI coach,
So that I receive relevant, personalized recommendations.

**Acceptance Criteria:**

**Given** analytics are complete,
**When** preparing data for the AI coach,
**Then** the system shall prepare a JSON summary of spending data including income, expenses, top categories, and user's savings goal (referencing REQ-AI-001, FR28).

**Given** the JSON summary is prepared,
**When** constructing the AI prompt,
**Then** the system shall construct structured prompts containing spending summary, category breakdown, and user context (referencing REQ-AI-003, FR30).

**Given** the prompt is being built,
**When** formatting the request,
**Then** it shall follow the structure defined in Architecture Decision 4.4 (user profile, spending summary, top categories, request for recommendations/habit/spending leaks).

**Given** the prompt is complete,
**When** sending to the API,
**Then** the system shall request 3-5 personalized, specific recommendations with concrete savings amounts (referencing REQ-AI-004, FR31).

**Given** the prompt includes all required elements,
**When** making the API call,
**Then** the system shall also request one simple "money habit" suggestion (referencing REQ-AI-005, FR32) and an explanation of biggest spending leaks (referencing REQ-AI-006, FR33).

### Story 3.3: Display AI Cashflow Coach Summary

As a user,
I want to see the personalized financial recommendations and money habit suggestions from the AI Cashflow Coach,
So that I can easily understand and act upon the advice provided.

**Acceptance Criteria:**

**Given** the AI's response has been successfully parsed,
**When** the application displays the AI coaching summary,
**Then** it shall present the 3-5 personalized recommendations, one money habit suggestion, and the explanation of biggest spending leaks in a designated, user-friendly text area (referencing REQ-UI-003, FR3, REQ-AI-009, FR36).

**Given** the AI coach summary is displayed,
**When** a user reads the recommendations,
**Then** the interface shall be intuitive and easy to navigate for users with intermediate technical skills (referencing NFR-USABILITY-001, NFR3).

### Story 3.4: API Error Handling & Retry Logic

As a user,
I want the application to handle AI service issues gracefully,
So that I can still use the app even when the AI coach is temporarily unavailable.

**Acceptance Criteria:**

**Given** the Gemini API call fails due to network errors,
**When** the error occurs,
**Then** the system shall implement retry logic for API failures (single retry with exponential backoff) (referencing REQ-AI-007, FR34, per Architecture Decision 4.4).

**Given** the API rate limit is exceeded,
**When** receiving a rate limit response,
**Then** the application shall display: "AI Coach busy. Please try again in a moment." (per Architecture Decision 4.3).

**Given** the API request times out (>15 seconds),
**When** the timeout occurs,
**Then** the application shall display: "AI Coach taking longer than expected. Using basic analysis." and allow the user to view analytics without AI insights (per Architecture Decision 4.3, referencing REQ-UI-009, FR9).

**Given** all retry attempts fail,
**When** the API is unavailable,
**Then** the system shall continue to provide analytics functionality even if AI coach API is unavailable (referencing NFR-REL-002, NFR11).

### Story 3.5: Graceful Degradation - Analytics-Only Mode

As a user,
I want to access my financial analytics even when AI coaching is unavailable,
So that I'm not completely blocked from using the app.

**Acceptance Criteria:**

**Given** the AI coach is unavailable (API error, missing key, timeout),
**When** the application detects AI unavailability,
**Then** it shall gracefully handle AI coach unavailability and allow users to view analytics without AI insights (referencing REQ-UI-009, FR9).

**Given** the app is running in analytics-only mode,
**When** displaying the interface,
**Then** the application shall show all charts, calculations, and spending breakdowns without the AI coach summary section.

**Given** analytics-only mode is active,
**When** the user views the app,
**Then** a message shall be displayed: "AI Coach currently unavailable. Showing analytics only."

**Given** the system handles errors,
**When** validating inputs and processing,
**Then** it shall validate all user inputs and provide clear error messages for invalid data (referencing NFR-REL-003, NFR12).

---

## Epic 4: Data Export & Management

Users can easily save their processed financial summaries and the AI-generated monthly plans for their records or further analysis.

### Story 4.1: Export Processed Data Summary

As a user,
I want to download my processed spending data,
So that I can keep records or analyze it further in other tools.

**Acceptance Criteria:**

**Given** transaction processing is complete,
**When** the user requests to download processed data,
**Then** the application shall allow users to download processed data summaries (referencing REQ-UI-004, FR4).

**Given** the export option is selected,
**When** choosing the format,
**Then** the system shall allow users to save the processed summary in CSV format (referencing REQ-FO-001, FR38).

**Given** the export option is selected,
**When** choosing the format,
**Then** the system shall allow users to save the processed summary in JSON format (referencing REQ-FO-001, FR38).

**Given** the user selects an export format,
**When** the download is triggered,
**Then** the file shall contain all processed transaction data with normalized columns (Date, Description, Amount, Category) and calculated fields.

**Given** data is being exported,
**When** the file is generated,
**Then** uploaded CSV files shall not be saved to disk; all processing occurs in-memory within the Streamlit session (referencing NFR-SEC-004, NFR8).

### Story 4.2: Export AI-Generated Monthly Plan

As a user,
I want to download the AI-generated "Monthly Plan" as a text or Markdown file,
So that I can easily review and act on the personalized advice offline or integrate it into my notes.

**Acceptance Criteria:**

**Given** the AI-generated "Monthly Plan" is available in the application,
**When** the user selects to export the plan,
**Then** the application shall provide an option to save the plan in text format (referencing REQ-UI-005, FR5, REQ-FO-002, FR39).

**Given** the AI-generated "Monthly Plan" is available in the application,
**When** the user selects to export the plan,
**Then** the application shall provide an option to save the plan in Markdown format (referencing REQ-UI-005, FR5, REQ-FO-002, FR39).

**Given** the user selects an export format,
**When** the system generates the file,
**Then** the generated file shall contain the AI-generated "Monthly Plan" accurately including recommendations, money habit, and spending leak analysis (referencing REQ-FO-002, FR39).

---

## Epic 5: Future Enhancements - Goal Setting & Customization

Users can set personal savings targets and customize their interaction with the AI coach, making the guidance even more tailored to their preferences.

### Story 5.1: Savings Goal Input

As a user,
I want to input my monthly savings target,
So that the AI coach can provide recommendations tailored to my specific financial goals.

**Acceptance Criteria:**

**Given** the application is running,
**When** the user accesses goal setting features,
**Then** the application shall allow users to input a monthly savings target (referencing REQ-UI-010, FR10).

**Given** a savings goal is entered,
**When** the user submits the goal,
**Then** the system shall store the goal in session state and use it when preparing the JSON summary for the AI coach.

**Given** the savings goal is available,
**When** constructing the AI prompt,
**Then** the prompt shall include the user's specific savings goal (e.g., "save £300/month") for personalized recommendations.

### Story 5.2: Implement AI Coach Tone Mode Selection

As a user,
I want to select a preferred tone mode for the AI Cashflow Coach,
So that the advice provided is delivered in a style that resonates best with me.

**Acceptance Criteria:**

**Given** the application is running,
**When** a user navigates to the AI coach settings or preferences,
**Then** they should see options to select a "Tone Mode" for the coach (e.g., playful, serious) (referencing REQ-UI-011, FR11).

**Given** a user has selected a preferred "Tone Mode",
**When** the system constructs the AI prompt,
**Then** it shall incorporate the user-selected tone mode into the AI prompt (referencing REQ-AI-010, FR37).


