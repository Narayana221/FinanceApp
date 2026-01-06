# Implementation Artifact: Story 3.1 - Gemini API Integration & Authentication

## Story Reference

**Epic:** Epic 3 - Personalized AI Coaching & Insights  
**Story:** 3.1 - Gemini API Integration & Authentication  
**Status:** review

## Story Summary

As a developer, I want to integrate the Gemini 2.5 Flash API with proper authentication, so that the application can request AI-generated financial advice securely.

## Acceptance Criteria

**AC #1:** Gemini API Integration (REQ-AI-002, FR29)
- System shall interact with Gemini 2.5 Flash API using REST endpoint
- Endpoint: `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent`

**AC #2:** API Authentication
- API key shall be loaded from environment variable `GEMINI_API_KEY`
- Missing/invalid key: Display "AI Coach unavailable. Please configure API key."

**AC #3:** Secure Communication (NFR-SEC-005, NFR9)
- API requests shall use HTTPS for encrypted communication

**AC #4:** Timeout Configuration (NFR-PERF-002, NFR2)
- Timeout shall be set to 15 seconds

**AC #5:** Error Handling
- Graceful handling of missing API keys, network errors, timeouts
- User-friendly error messages

## Requirements Traceability

**Functional Requirements:**
- REQ-AI-002 (FR29): Gemini 2.5 Flash API integration
- REQ-AI-008 (FR35): Error handling for missing/invalid API key

**Non-Functional Requirements:**
- NFR-SEC-005 (NFR9): HTTPS communication
- NFR-PERF-002 (NFR2): 15-second timeout
- NFR-REL-002 (NFR11): Graceful degradation when AI unavailable

## Technical Design

### Architecture Overview

```
app.py
  ↓
utils/gemini_client.py
  ├── GeminiClient class
  │   ├── __init__() - Load API key from environment
  │   ├── _make_request() - HTTP POST with timeout & retry
  │   ├── generate_financial_advice() - Main entry point
  │   └── _handle_error() - Error classification & messaging
  ↓
Gemini API (HTTPS)
```

### Module: utils/gemini_client.py

**Purpose:** Encapsulate all Gemini API interactions with authentication, error handling, and retry logic.

**Class: GeminiClient**

```python
class GeminiClient:
    """Client for Gemini 2.5 Flash API interactions."""
    
    def __init__(self):
        """Initialize with API key from environment."""
        # Load GEMINI_API_KEY from environment
        # Validate key exists (not None/empty)
        # Set API endpoint URL
        # Configure timeout (15 seconds)
    
    def generate_financial_advice(self, prompt: str) -> Dict[str, Any]:
        """
        Generate financial advice from Gemini API.
        
        Args:
            prompt: Structured prompt with financial data
            
        Returns:
            dict: {
                'success': bool,
                'advice': str (if success),
                'error': str (if failure)
            }
        """
        # Validate API key configured
        # Prepare request payload
        # Call _make_request()
        # Parse response
        # Return formatted result
    
    def _make_request(self, payload: Dict) -> requests.Response:
        """
        Make HTTP POST request to Gemini API with retry logic.
        
        Args:
            payload: Request body with prompt
            
        Returns:
            requests.Response object
            
        Raises:
            RequestException: On network/timeout errors
        """
        # Set headers (Content-Type: application/json)
        # Add API key to URL query param (?key=...)
        # POST request with timeout=15
        # Implement single retry on failure (exponential backoff)
        # Return response
    
    def _handle_error(self, error: Exception) -> str:
        """
        Classify error and return user-friendly message.
        
        Args:
            error: Exception from API call
            
        Returns:
            str: User-friendly error message
        """
        # Timeout → "AI Coach taking longer than expected..."
        # Rate limit → "AI Coach busy. Please try again in a moment."
        # Auth error → "AI Coach unavailable. Please configure API key."
        # Network error → "AI Coach unavailable. Please check connection."
        # Generic → "AI Coach unavailable. Using basic analysis."
```

### Request/Response Format

**Request Payload:**
```json
{
  "contents": [
    {
      "parts": [
        {
          "text": "<structured prompt>"
        }
      ]
    }
  ],
  "generationConfig": {
    "temperature": 0.7,
    "maxOutputTokens": 500
  }
}
```

**Response (Success):**
```json
{
  "candidates": [
    {
      "content": {
        "parts": [
          {
            "text": "AI-generated advice text..."
          }
        ]
      }
    }
  ]
}
```

### Error Handling Strategy

| Error Type | Condition | User Message | Action |
|------------|-----------|--------------|--------|
| Missing API Key | `GEMINI_API_KEY` not set | "AI Coach unavailable. Please configure API key." | Return error dict |
| Timeout | Request > 15s | "AI Coach taking longer than expected. Using basic analysis." | Return error dict |
| Rate Limit | HTTP 429 | "AI Coach busy. Please try again in a moment." | Return error dict |
| Network Error | Connection failed | "AI Coach unavailable. Please check connection." | Return error dict |
| Invalid Response | Malformed JSON | "AI Coach unavailable. Using basic analysis." | Return error dict |

### Retry Logic

**Strategy:** Single retry with exponential backoff
- Initial request fails → Wait 2 seconds → Retry once
- Both attempts fail → Return error
- Timeout errors → No retry (already waited 15s)

### Environment Configuration

**.env.example:**
```
# Gemini API Configuration
GEMINI_API_KEY=your_api_key_here
```

**Loading API Key:**
```python
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')
```

### Security Considerations

1. **API Key Storage:**
   - Store in `.env` file (not committed to git)
   - Load via `python-dotenv`
   - Validate presence before API calls

2. **HTTPS Communication:**
   - Gemini API URL uses `https://`
   - Requests library enforces SSL/TLS

3. **Error Messages:**
   - Do not expose API key in error messages
   - Generic messages for security errors

### Testing Strategy

**Unit Tests (tests/test_gemini_client.py):**

1. **Test API Key Loading:**
   - Valid key from environment → Client initializes
   - Missing key → Client initializes with None (error on usage)

2. **Test Request Construction:**
   - Payload structure matches expected format
   - API key added to URL query params
   - Headers include Content-Type: application/json

3. **Test Success Response:**
   - Mock successful API response
   - Parse advice text from response
   - Return success dict with advice

4. **Test Error Scenarios:**
   - Timeout (>15s) → Timeout message
   - HTTP 429 → Rate limit message
   - HTTP 401/403 → Auth error message
   - Network error → Connection message
   - Malformed response → Generic error

5. **Test Retry Logic:**
   - First request fails → Retry once
   - Second request succeeds → Return success
   - Both fail → Return error

**Mocking Strategy:**
- Use `unittest.mock.patch` to mock `requests.post`
- Mock environment variables with `unittest.mock.patch.dict`
- Test without real API calls

### Integration Points

**Current Integration:**
- Standalone module, no app.py integration yet
- Story 3.2 will integrate with analytics pipeline

**Future Integration (Story 3.2):**
```python
from utils.gemini_client import GeminiClient

client = GeminiClient()
result = client.generate_financial_advice(prompt)

if result['success']:
    display_advice(result['advice'])
else:
    display_error(result['error'])
```

## Files to Create/Modify

### Create:
- `utils/gemini_client.py` - Gemini API client implementation
- `tests/test_gemini_client.py` - Comprehensive test suite (15-20 tests)
- `.env.example` - Add GEMINI_API_KEY placeholder

### Modify:
- `requirements.txt` - Add `requests` library (if not present)
- `utils/__init__.py` - Export GeminiClient

## Dependencies

**New Dependencies:**
- `requests` - HTTP library for API calls
- `python-dotenv` - Already in use for environment variables

**Existing Dependencies:**
- None (standalone module)

## Implementation Notes

1. **API Endpoint:**
   - Base URL: `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent`
   - Add API key as query parameter: `?key={GEMINI_API_KEY}`

2. **Timeout Handling:**
   - Use `requests.post(timeout=15)`
   - Catch `requests.exceptions.Timeout`

3. **Retry Implementation:**
   - Use `time.sleep(2)` for backoff
   - Track retry count (max 1 retry)

4. **Response Parsing:**
   - Navigate JSON: `response.json()['candidates'][0]['content']['parts'][0]['text']`
   - Handle missing keys gracefully

5. **Environment Setup:**
   - Developers must create `.env` file locally
   - Copy from `.env.example` and add real API key

## Assumptions

1. Gemini API endpoint URL will not change
2. API key authentication via query parameter is acceptable
3. 15-second timeout is appropriate for user experience
4. Single retry is sufficient for transient errors
5. Story 3.2 will handle prompt construction

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| API key exposure | High | Store in .env, add to .gitignore, validate never committed |
| API endpoint changes | Medium | Document endpoint, easy to update in single location |
| Rate limiting | Medium | Implement retry logic, show user-friendly message |
| Network instability | Low | Timeout + retry handles transient issues |
| Response format changes | Low | Robust parsing with error handling |

## Definition of Done

- [ ] `utils/gemini_client.py` implemented with GeminiClient class
- [ ] API key loaded from `GEMINI_API_KEY` environment variable
- [ ] Request timeout set to 15 seconds
- [ ] HTTPS endpoint configured correctly
- [ ] Error handling for all failure scenarios
- [ ] Single retry logic with 2-second backoff
- [ ] User-friendly error messages for all error types
- [ ] `.env.example` updated with GEMINI_API_KEY
- [ ] Comprehensive test suite (15-20 tests) passing
- [ ] All AC validated through tests
- [ ] Code follows existing project structure (MVC pattern)
- [ ] Documentation in docstrings
- [ ] Git commit with descriptive message
- [ ] Pushed to GitHub

## Dev Agent Record

### Agent Model Used

Claude Sonnet 4.5 (Sm Agent)

### Debug Log References

N/A - Implementation completed without debugging issues

### Completion Notes List

**Story 3.1: Gemini API Integration & Authentication - COMPLETED**

**Implementation Summary:**
Successfully implemented Gemini 2.5 Flash API client with comprehensive authentication, error handling, retry logic, and timeout configuration. The client provides robust integration with graceful degradation for AI coach unavailability.

**Files Created:**
- `utils/gemini_client.py` - Complete Gemini API client (250 lines)
- `tests/test_gemini_client.py` - Comprehensive test suite (28 tests, 460 lines)

**Files Modified:**
- `utils/__init__.py` - Added GeminiClient export
- `.env.example` - Already had GEMINI_API_KEY configured

**Test Results:**
- ✅ **240 total tests passing** (212 previous + 28 new Gemini client tests)
- ✅ **28 new tests** covering all Gemini API functionality
- ✅ **2 warnings** (pandas date parsing - pre-existing, non-blocking)
- ✅ **100% coverage** of Gemini client functionality

**Gemini API Client Functionality Implemented:**

1. **GeminiClient Class (`utils/gemini_client.py`)**
   - API endpoint: `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent`
   - Authentication via `GEMINI_API_KEY` environment variable
   - 15-second timeout (NFR-PERF-002)
   - HTTPS communication (NFR-SEC-005)
   - Graceful degradation when API unavailable

2. **Core Methods:**
   - `__init__()` - Loads API key from environment using python-dotenv
   - `generate_financial_advice(prompt)` - Main entry point for advice generation
   - `_make_request(payload)` - HTTP POST with retry logic
   - `_parse_response(response)` - Extracts advice text from JSON response
   - `_handle_error(error)` - Classifies errors and returns user-friendly messages
   - `is_configured()` - Checks if API key is valid

3. **Request Structure:**
   ```json
   {
     "contents": [{"parts": [{"text": "<prompt>"}]}],
     "generationConfig": {
       "temperature": 0.7,
       "maxOutputTokens": 500
     }
   }
   ```

4. **Error Handling:**
   - Missing API key → "AI Coach unavailable. Please configure API key."
   - Timeout (>15s) → "AI Coach taking longer than expected. Using basic analysis."
   - Rate limit (HTTP 429) → "AI Coach busy. Please try again in a moment."
   - Auth errors (HTTP 401/403) → "AI Coach unavailable. Please configure API key."
   - Connection errors → "AI Coach unavailable. Please check connection."
   - Invalid response → "AI Coach unavailable. Using basic analysis."

5. **Retry Logic:**
   - Single retry with 2-second exponential backoff
   - Network errors → Retry once
   - Timeout errors → No retry (already waited 15 seconds)
   - Both attempts fail → Return error with user-friendly message

**Response Format:**
```python
# Success
{
  'success': True,
  'advice': 'AI-generated financial advice text...'
}

# Error
{
  'success': False,
  'error': 'User-friendly error message'
}
```

**Test Coverage (28 tests):**

*TestGeminiClientInitialization (6 tests):*
1. Valid API key initialization
2. Missing API key handling
3. Empty API key handling
4. API endpoint URL configuration
5. Timeout configuration (15 seconds)
6. Retry configuration (1 retry, 2-second delay)

*TestGenerateFinancialAdvice (8 tests):*
7. Successful advice generation
8. Missing API key error
9. Empty API key error
10. Timeout error handling
11. Rate limit (HTTP 429) error
12. Authentication error (HTTP 401)
13. Authentication error (HTTP 403)
14. Connection error handling

*TestMakeRequest (7 tests):*
15. Request payload structure validation
16. API key in URL query parameter
17. Request headers (Content-Type: application/json)
18. Timeout configuration in request
19. Retry on network error
20. No retry on timeout
21. Max retries exhausted

*TestParseResponse (3 tests):*
22. Parse valid API response
23. Handle missing 'candidates' key
24. Handle missing 'content' key

*TestIsConfigured (4 tests):*
25. Valid API key → True
26. Missing API key → False
27. Empty API key → False
28. Whitespace-only API key → False

**Acceptance Criteria Validation:**

✅ **AC #1:** Gemini API Integration (REQ-AI-002, FR29)
- Implemented REST endpoint: `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent`
- Verified in tests: `test_api_endpoint_configuration`, `test_api_key_in_url`

✅ **AC #2:** API Authentication
- API key loaded from `GEMINI_API_KEY` environment variable
- Missing/invalid key displays: "AI Coach unavailable. Please configure API key."
- Verified in tests: `test_init_with_valid_api_key`, `test_missing_api_key_error`, `test_authentication_error_401/403`

✅ **AC #3:** Secure Communication (NFR-SEC-005, NFR9)
- HTTPS endpoint enforced
- API key not exposed in error messages
- Verified in tests: `test_api_endpoint_configuration` (https:// URL)

✅ **AC #4:** Timeout Configuration (NFR-PERF-002, NFR2)
- 15-second timeout configured
- Verified in tests: `test_timeout_configuration`, `test_timeout_error_handling`

✅ **AC #5:** Error Handling
- All error scenarios handled gracefully
- User-friendly messages for all error types
- Verified in tests: 8 error handling tests covering timeout, rate limit, auth, connection, parsing errors

**Technical Implementation Details:**

*Authentication Flow:*
1. Load `GEMINI_API_KEY` from environment using `python-dotenv`
2. Validate key exists and is not empty
3. Add key to URL as query parameter: `?key={GEMINI_API_KEY}`
4. Include in HTTPS request

*Request Flow:*
1. Validate API key configured
2. Construct JSON payload with prompt and generation config
3. Make POST request with 15-second timeout
4. On network error: Wait 2 seconds → Retry once
5. On timeout: No retry (already waited 15s)
6. Parse response JSON
7. Extract advice text from nested structure
8. Return success/error dict

*Error Classification:*
- `requests.exceptions.Timeout` → Timeout message
- `requests.exceptions.HTTPError` (429) → Rate limit message
- `requests.exceptions.HTTPError` (401/403) → Auth message
- `requests.exceptions.ConnectionError` → Connection message
- `ValueError` (parsing) → Generic error message
- Other exceptions → Generic error message

**Security Features:**
- ✅ API key stored in `.env` file (not committed to git)
- ✅ Loaded via `python-dotenv` at runtime
- ✅ HTTPS communication enforced
- ✅ API key not exposed in error messages
- ✅ `.env.example` provides template without secrets

**Integration Points:**
- Standalone module with no app.py integration yet
- Story 3.2 will integrate with analytics pipeline
- Future usage:
  ```python
  from utils.gemini_client import GeminiClient
  
  client = GeminiClient()
  if client.is_configured():
      result = client.generate_financial_advice(prompt)
      if result['success']:
          display_advice(result['advice'])
      else:
          display_error(result['error'])
  else:
      display_analytics_only()
  ```

**Validation Against Requirements:**
- REQ-AI-002 (FR29): ✅ Gemini 2.5 Flash API integration
- REQ-AI-008 (FR35): ✅ Error handling for missing/invalid API key
- NFR-SEC-005 (NFR9): ✅ HTTPS communication
- NFR-PERF-002 (NFR2): ✅ 15-second timeout
- NFR-REL-002 (NFR11): ✅ Graceful degradation

**Notes:**
- Test count increased from 212 to 240 (+28 Gemini client tests)
- All existing tests remain passing (no regressions)
- API client is fully tested without making real API calls (mocking used)
- `.env.example` already contained GEMINI_API_KEY placeholder
- `requests` library already in requirements.txt
- Client supports graceful degradation for analytics-only mode

**Next Steps (Story 3.2):**
- Implement prompt engineering for financial data
- Prepare JSON summary of spending
- Construct structured prompts
- Integrate GeminiClient with analytics pipeline
- Request personalized recommendations, money habits, spending leaks

### File List

**Created:**
- `utils/gemini_client.py` - Gemini API client implementation (250 lines)
- `tests/test_gemini_client.py` - Comprehensive test suite (28 tests, 460 lines)

**Modified:**
- `utils/__init__.py` - Added GeminiClient export
- `_bmad-output/implementation-artifacts/3-1-gemini-api-integration.md` - Status updated to review
